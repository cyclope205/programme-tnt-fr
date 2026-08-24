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
    DEFAULT_TMDB_API_KEY,
    FETCH_MIN_INTERVAL_MINUTES,
    LATE_NIGHT_START,
    PRIME_TIME_START,
    TMDB_IMAGE_BASE_URL,
    TMDB_SEARCH_MOVIE_URL,
    TMDB_SEARCH_TV_URL,
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

    def as_dict(self, poster: str | None = None) -> dict:
        return {
            "title": self.title,
            "subtitle": self.subtitle,
            "description": self.desc,
            "category": self.category,
            "icon": self.icon,
            "poster": poster,
            "rating": self.rating,
            "start": self.start.isoformat() if self.start else None,
            "stop": self.stop.isoformat() if self.stop else None,
        }


class ProgrammeTntFrCoordinator(DataUpdateCoordinator):
    """Fetches the XMLTV feed and derives now / prime-time / late-night slots."""

    def __init__(
        self, hass: HomeAssistant, channels: list[str], tmdb_api_key: str | None = None
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name="programme_tnt_fr",
            update_interval=timedelta(minutes=UPDATE_INTERVAL_MINUTES),
        )
        self._channels = channels
        self._tmdb_api_key = tmdb_api_key or DEFAULT_TMDB_API_KEY
        self._session = async_get_clientsession(hass)
        self._programmes_by_channel: dict[str, list[Programme]] = {}
        self._channels_meta: dict[str, dict] = {}
        self._last_fetch = None
        # Cache titre -> URL d'affiche TMDB (ou None si aucune correspondance
        # trouvee), pour eviter de re-interroger TMDB a chaque rafraichissement
        # (toutes les 5 min) pour un programme deja resolu.
        self._tmdb_poster_cache: dict[str, str | None] = {}

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

        picks = {
            channel_id: self._pick_slots(channel_id, now)
            for channel_id in self._channels
        }

        if self._tmdb_api_key:
            title_categories: dict[str, str | None] = {}
            for slots in picks.values():
                for programme in slots:
                    if (
                        programme is not None
                        and programme.title
                        and programme.title not in self._tmdb_poster_cache
                        and programme.title not in title_categories
                    ):
                        title_categories[programme.title] = programme.category
            if title_categories:
                await self._resolve_tmdb_posters(title_categories)

        result: dict[str, dict] = {}
        for channel_id, (current, prime_time, second_part) in picks.items():
            meta = self._channels_meta.get(channel_id, {})
            result[channel_id] = {
                "channel_id": channel_id,
                "channel_name": meta.get("name", channel_id),
                "channel_icon": meta.get("icon"),
                "current": self._programme_dict(current),
                "prime_time": self._programme_dict(prime_time),
                "second_part": self._programme_dict(second_part),
            }
        return result

    def _programme_dict(self, programme: Programme | None) -> dict | None:
        if programme is None:
            return None
        poster = self._tmdb_poster_cache.get(programme.title) if self._tmdb_api_key else None
        return programme.as_dict(poster=poster)

    async def _resolve_tmdb_posters(self, title_categories: dict[str, str | None]) -> None:
        """Look up a poster on TMDB (film ou serie selon la categorie) pour chaque nouveau titre."""
        for title, category in title_categories.items():
            try:
                self._tmdb_poster_cache[title] = await self._lookup_tmdb_poster(title, category)
            except Exception as err:  # noqa: BLE001
                _LOGGER.debug("Echec de la recherche TMDB pour %s: %s", title, err)
                self._tmdb_poster_cache[title] = None

    async def _lookup_tmdb_poster(self, title: str, category: str | None = None) -> str | None:
        if self._is_movie_category(category):
            search_order = (TMDB_SEARCH_MOVIE_URL, TMDB_SEARCH_TV_URL)
        else:
            search_order = (TMDB_SEARCH_TV_URL, TMDB_SEARCH_MOVIE_URL)
        poster_path = await self._tmdb_search(search_order[0], title)
        if not poster_path:
            poster_path = await self._tmdb_search(search_order[1], title)
        if not poster_path:
            return None
        return TMDB_IMAGE_BASE_URL + poster_path

    @staticmethod
    def _is_movie_category(category: str | None) -> bool:
        """Return True if the XMLTV category explicitly indicates a movie.

        Le flux XMLTV tague systematiquement les films avec "Film" (ou
        variantes), alors que les series n'ont pas toujours de categorie
        "Serie" explicite (parfois seulement un genre comme "Action"). On ne
        bascule donc en recherche film que si la categorie le confirme
        explicitement ; sinon on cherche d'abord cote serie, avec repli
        automatique sur film si la recherche serie ne trouve rien.
        """
        if not category:
            return False
        normalized = category.strip().lower()
        movie_keywords = (
            "film",
            "long m\u00e9trage",
            "long metrage",
            "cin\u00e9ma",
            "cinema",
        )
        return any(keyword in normalized for keyword in movie_keywords)

    async def _tmdb_search(self, url: str, title: str) -> str | None:
        params = {
            "api_key": self._tmdb_api_key,
            "query": title,
            "language": "fr-FR",
            "include_adult": "false",
        }
        resp = await self._session.get(url, params=params, timeout=10)
        if resp.status != 200:
            return None
        data = await resp.json()
        results = data.get("results") or []
        if not results:
            return None
        return results[0].get("poster_path")

    async def _fetch_and_parse(self) -> None:
        resp = await self._session.get(XMLTV_URL, timeout=30)
        resp.raise_for_status()
        text = await resp.text()

        # Le flux complet (xmltv_fr.xml) pese plusieurs dizaines de Mo : on
        # deporte le parsing XML (CPU-bound) dans un thread pour ne pas
        # bloquer la boucle evenementielle de Home Assistant.
        channels_meta, programmes = await self.hass.async_add_executor_job(
            self._parse_xmltv, text, set(self._channels)
        )

        self._programmes_by_channel = programmes
        self._channels_meta = channels_meta

    @staticmethod
    def _parse_xmltv(
        text: str, wanted: set[str]
    ) -> tuple[dict[str, dict], dict[str, list[Programme]]]:
        """Parse le flux XMLTV (CPU-bound, execute dans un executor thread)."""
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

        return channels_meta, programmes

    def _pick_slots(
        self, channel_id: str, now
    ) -> tuple[Programme | None, Programme | None, Programme | None]:
        progs = self._programmes_by_channel.get(channel_id, [])

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

        return current, prime_time, second_part
