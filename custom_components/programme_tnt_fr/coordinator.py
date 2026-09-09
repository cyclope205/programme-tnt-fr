"""Data update coordinator for the Programme TNT FR integration."""
from __future__ import annotations

import io
import logging
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from .const import (
    DAY_RESET,
    FETCH_MIN_INTERVAL_MINUTES,
    LATE_NIGHT_START,
    PRIME_TIME_START,
    UPDATE_INTERVAL_MINUTES,
    XMLTV_URL,
)

_LOGGER = logging.getLogger(__name__)


def _parse_xmltv_datetime(value: str | None):
    """Parse a XMLTV datetime such as '20260821000500 +0200'."""
    if not value:
        return None
    try:
        return datetime.strptime(value.strip(), "%Y%m%d%H%M%S %z")
    except ValueError:
        return None


class Programme:
    """A single TV programme entry."""

    def __init__(
        self,
        start,
        stop,
        title,
        subtitle,
        desc,
        category,
        icon,
        rating,
    ) -> None:
        self.start = start
        self.stop = stop
        self.title = title
        self.subtitle = subtitle
        self.desc = desc
        self.category = category
        self.icon = icon
        self.rating = rating

    def as_dict(self) -> dict:
        return {
            "title": self.title,
            "subtitle": self.subtitle,
            "description": self.desc,
            "category": self.category,
            "icon": self.icon,
            "rating": self.rating,
            "start": self.start.isoformat() if self.start else None,
            "stop": self.stop.isoformat() if self.stop else None,
        }


def _parse_xmltv_bytes(
    raw: bytes, wanted: set[str]
) -> tuple[dict[str, dict], dict[str, list[Programme]]]:
    """Stream-parse the XMLTV feed, keeping only the wanted channels.

    Runs in a worker thread (see _fetch_and_parse): this walks the whole
    document with ET.iterparse and discards each <channel>/<programme>
    element right after reading it (elem.clear() + detach from the root),
    instead of ET.fromstring() which would first build the *entire* tree
    in memory (every channel, every one of the ~113k programmes in the
    full feed) before any filtering happens. Peak memory here scales with
    the number of channels actually followed, not with the size of the
    whole feed.
    """
    channels_meta: dict[str, dict] = {}
    programmes: dict[str, list[Programme]] = {}

    context = ET.iterparse(io.BytesIO(raw), events=("start", "end"))
    _, root = next(context)  # first start event: the <tv> root element

    for event, elem in context:
        if event != "end":
            continue

        if elem.tag == "channel":
            cid = elem.get("id")
            if cid and cid in wanted:
                name_el = elem.find("display-name")
                icon_el = elem.find("icon")
                channels_meta[cid] = {
                    "name": name_el.text if name_el is not None else cid,
                    "icon": icon_el.get("src") if icon_el is not None else None,
                }
            elem.clear()
            root.remove(elem)

        elif elem.tag == "programme":
            channel_id = elem.get("channel")
            if channel_id in wanted:
                start = _parse_xmltv_datetime(elem.get("start"))
                stop = _parse_xmltv_datetime(elem.get("stop"))
                if start is not None and stop is not None:
                    title_el = elem.find("title")
                    subtitle_el = elem.find("sub-title")
                    desc_el = elem.find("desc")
                    category_el = elem.find("category")
                    icon_el = elem.find("icon")
                    rating_el = elem.find("rating/value")
                    item = Programme(
                        start=dt_util.as_local(start),
                        stop=dt_util.as_local(stop),
                        title=title_el.text if title_el is not None else "",
                        subtitle=subtitle_el.text if subtitle_el is not None else None,
                        desc=desc_el.text if desc_el is not None else None,
                        category=category_el.text if category_el is not None else None,
                        icon=icon_el.get("src") if icon_el is not None else None,
                        rating=rating_el.text if rating_el is not None else None,
                    )
                    programmes.setdefault(channel_id, []).append(item)
            elem.clear()
            root.remove(elem)

    return channels_meta, programmes


class ProgrammeTntFrCoordinator(DataUpdateCoordinator):
    """Fetches the XMLTV feed and derives now / prime-time / late-night slots."""

    def __init__(self, hass: HomeAssistant, channels: list[str]) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name="programme_tnt_fr",
            update_interval=timedelta(minutes=UPDATE_INTERVAL_MINUTES),
        )
        self._channels = channels
        self._session = async_get_clientsession(hass)
        self._programmes_by_channel: dict[str, list[Programme]] = {}
        self._channels_meta: dict[str, dict] = {}
        self._last_fetch = None
        self._etag: str | None = None
        self._last_modified: str | None = None

    async def _async_update_data(self) -> dict:
        now = dt_util.now()
        need_fetch = (
            self._last_fetch is None
            or (now - self._last_fetch) >= timedelta(minutes=FETCH_MIN_INTERVAL_MINUTES)
        )
        if need_fetch:
            try:
                await self._fetch_and_parse()
                self._last_fetch = now
            except Exception as err:  # noqa: BLE001
                if not self._programmes_by_channel:
                    raise UpdateFailed(
                        f"Impossible de recuperer le flux XMLTV: {err}"
                    ) from err
                _LOGGER.warning(
                    "Echec du rafraichissement du flux XMLTV, utilisation du cache: %s",
                    err,
                )

        return {
            channel_id: self._compute_slots(channel_id, now)
            for channel_id in self._channels
        }

    async def _fetch_and_parse(self) -> None:
        # Conditional request: if the feed hasn't changed since our last
        # successful fetch, the server answers 304 with an empty body
        # instead of resending the full ~80 Mo file - the feed itself only
        # changes every few days, this check still runs hourly but the
        # actual download (and the parsing work below) only happens when
        # there is really something new.
        headers = {}
        if self._etag:
            headers["If-None-Match"] = self._etag
        elif self._last_modified:
            headers["If-Modified-Since"] = self._last_modified

        resp = await self._session.get(XMLTV_URL, timeout=60, headers=headers)
        if resp.status == 304:
            _LOGGER.debug("Flux XMLTV inchange depuis le dernier telechargement")
            return
        resp.raise_for_status()
        self._etag = resp.headers.get("ETag")
        self._last_modified = resp.headers.get("Last-Modified")
        raw = await resp.read()

        wanted = set(self._channels)
        # The XML parsing itself is CPU-bound and, for the full feed, can
        # take a noticeable amount of time - run it in the executor so it
        # never blocks Home Assistant's event loop.
        channels_meta, programmes = await self.hass.async_add_executor_job(
            _parse_xmltv_bytes, raw, wanted
        )

        for progs in programmes.values():
            progs.sort(key=lambda p: p.start)

        self._programmes_by_channel = programmes
        self._channels_meta = channels_meta

    def _compute_slots(self, channel_id: str, now) -> dict:
        progs = self._programmes_by_channel.get(channel_id, [])
        meta = self._channels_meta.get(channel_id, {})

        current = None
        for programme in progs:
            if programme.start <= now < programme.stop:
                current = programme
                break

        if now.time() < DAY_RESET:
            broadcast_day = (now - timedelta(days=1)).date()
        else:
            broadcast_day = now.date()

        def _programme_at(reference_time):
            """Programme airing at reference_time, or the next one if none covers it."""
            threshold = datetime.combine(broadcast_day, reference_time, tzinfo=now.tzinfo)
            for programme in progs:
                if programme.start <= threshold < programme.stop:
                    return programme
            for programme in progs:
                if programme.start >= threshold:
                    return programme
            return None

        prime_time = _programme_at(PRIME_TIME_START)
        second_part = _programme_at(LATE_NIGHT_START)
        if second_part is not None and prime_time is not None and second_part is prime_time:
            second_part = None
            for programme in progs:
                if programme.start > prime_time.start:
                    second_part = programme
                    break

        return {
            "channel_id": channel_id,
            "channel_name": meta.get("name", channel_id),
            "channel_icon": meta.get("icon"),
            "current": current.as_dict() if current else None,
            "prime_time": prime_time.as_dict() if prime_time else None,
            "second_part": second_part.as_dict() if second_part else None,
        }
