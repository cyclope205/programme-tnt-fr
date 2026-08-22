"""Data update coordinator for the Programme TNT FR integration."""
from __future__ import annotations

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
        resp = await self._session.get(XMLTV_URL, timeout=30)
        resp.raise_for_status()
        text = await resp.text()
        root = ET.fromstring(text)

        channels_meta: dict[str, dict] = {}
        for chan in root.findall("channel"):
            cid = chan.get("id")
            if not cid:
                continue
            name_el = chan.find("display-name")
            icon_el = chan.find("icon")
            channels_meta[cid] = {
                "name": name_el.text if name_el is not None else cid,
                "icon": icon_el.get("src") if icon_el is not None else None,
            }

        wanted = set(self._channels)
        programmes: dict[str, list[Programme]] = {}
        for prog in root.findall("programme"):
            channel_id = prog.get("channel")
            if channel_id not in wanted:
                continue
            start = _parse_xmltv_datetime(prog.get("start"))
            stop = _parse_xmltv_datetime(prog.get("stop"))
            if start is None or stop is None:
                continue
            title_el = prog.find("title")
            subtitle_el = prog.find("sub-title")
            desc_el = prog.find("desc")
            category_el = prog.find("category")
            icon_el = prog.find("icon")
            rating_el = prog.find("rating/value")
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

        def _first_after(threshold_time):
            threshold = datetime.combine(broadcast_day, threshold_time, tzinfo=now.tzinfo)
            for programme in progs:
                if programme.start >= threshold:
                    return programme
            return None

        prime_time = _first_after(PRIME_TIME_START)
        second_part = _first_after(LATE_NIGHT_START)
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
