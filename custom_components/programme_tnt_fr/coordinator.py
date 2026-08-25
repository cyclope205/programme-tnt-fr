"""Data update coordinator for the Programme TNT FR integration."""
from __future__ import annotations

import asyncio
import logging
import re
import unicodedata
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


# Bruit frequent dans les titres du flux XMLTV pour les series : sous-titre
# d'episode entre parentheses, numero de saison, position dans la saison
# (ex: "Candice Renoir (Faute avouee a demi-pardonnee) S5 (1/10)"), et
# marqueur d'annee pour distinguer un reboot (ex: "Magnum *2018" du Magnum
# original des annees 1980). Verifie sur le flux xmltvfr.fr reel : environ
# un quart des titres suivent ce format. On les retire avant d'interroger
# TMDB, car la requete brute (bruitee de mots sans rapport avec le vrai
# titre) degrade nettement la pertinence du moteur de recherche TMDB et
# peut faire disparaitre le bon resultat de la premiere page de reponses.
_EPISODE_SUFFIX_RE = re.compile(r"\s*\([^()]*\)\s*S\d{1,2}\s*\(\d+/\d+\)\s*$", re.IGNORECASE)
_SEASON_SUFFIX_RE = re.compile(r"\s*S\d{1,2}\s*\(\d+/\d+\)\s*$", re.IGNORECASE)
_YEAR_MARKER_RE = re.compile(r"\s*\*(\d{4})\b")


class _TmdbTransientError(Exception):
    """Raised for TMDB failures that should be retried, not cached as no-poster.

    Covers auth failures (revoked/invalid API key), rate limiting, and
    server errors - none of these mean "this title has no TMDB match", so
    they must not be cached as such in _tmdb_poster_cache.
    """


# "un"/"une" sont volontairement absents : ce sont des articles francais
# omnipresents (ex: "Un diner presque parfait"), pas seulement des nombres -
# les convertir en "1" corromprait la comparaison de la plupart des titres.
_FR_NUMBER_WORDS = {
    "zero": "0",
    "deux": "2",
    "trois": "3",
    "quatre": "4",
    "cinq": "5",
    "six": "6",
    "sept": "7",
    "huit": "8",
    "neuf": "9",
    "dix": "10",
    "onze": "11",
    "douze": "12",
    "treize": "13",
    "quatorze": "14",
    "quinze": "15",
    "seize": "16",
    "vingt": "20",
    "trente": "30",
    "quarante": "40",
    "cinquante": "50",
    "soixante": "60",
}


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
        # Evite de repeter le warning de cle TMDB invalide/revoquee a chaque
        # cycle de rafraichissement (toutes les 5 min) une fois qu'il a ete logue.
        self._tmdb_auth_warned = False

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
            for channel_id in self._channels:
                for programme in self._programmes_by_channel.get(channel_id, []):
                    if (
                        programme is not None
                        and programme.title
                        and programme.stop > now
                        and programme.title not in self._tmdb_poster_cache
                        and programme.title not in title_categories
                    ):
                        title_categories[programme.title] = programme.category
            if title_categories:
                self.hass.async_create_task(
                    self._background_resolve_tmdb_posters(title_categories)
                )

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

    async def _background_resolve_tmdb_posters(self, title_categories: dict[str, str | None]) -> None:
        """Resolve TMDB posters in the background, then push a refresh once done.

        Runs outside of _async_update_data's await chain so a large batch of
        new titles (e.g. a whole day's guide on first setup) can never delay
        or cancel config entry setup again.
        """
        await self._resolve_tmdb_posters(title_categories)
        await self.async_request_refresh()

    async def _resolve_tmdb_posters(self, title_categories: dict[str, str | None]) -> None:
        """Look up a poster on TMDB (film ou serie selon la categorie) pour chaque nouveau titre.

        Runs lookups concurrently (bounded) instead of one at a time, since
        this can now cover a full day's programmes instead of just 3 picks.
        """
        semaphore = asyncio.Semaphore(5)

        async def _resolve_one(title: str, category: str | None) -> None:
            async with semaphore:
                try:
                    poster = await self._lookup_tmdb_poster(title, category)
                except Exception as err:  # noqa: BLE001
                    # Erreur temporaire (reseau, cle invalide, rate limit...) :
                    # on ne met PAS en cache pour que ce titre soit retente au
                    # prochain cycle, plutot que fige a tort sur "aucune affiche".
                    _LOGGER.debug("Recherche TMDB reportee pour %s (erreur temporaire): %s", title, err)
                    return
                self._tmdb_poster_cache[title] = poster

        await asyncio.gather(
            *(_resolve_one(title, category) for title, category in title_categories.items())
        )

    async def _lookup_tmdb_poster(self, title: str, category: str | None = None) -> str | None:
        clean_title, year = self._clean_search_query(title)
        if self._is_movie_category(category):
            search_order = (TMDB_SEARCH_MOVIE_URL, TMDB_SEARCH_TV_URL)
        else:
            search_order = (TMDB_SEARCH_TV_URL, TMDB_SEARCH_MOVIE_URL)
        for url in search_order:
            poster_path = await self._tmdb_search(url, clean_title)
            if poster_path:
                return TMDB_IMAGE_BASE_URL + poster_path
        # Repli avec filtre par annee, uniquement si un marqueur "*AAAA" a ete
        # trouve et que rien n'a matche sans lui (ex: distinguer le Magnum de
        # 2018 de l'original) - tente en plus, ne remplace jamais les essais
        # ci-dessus, donc ne peut pas faire regresser un match qui marchait deja.
        if year:
            for url in search_order:
                poster_path = await self._tmdb_search(url, clean_title, year)
                if poster_path:
                    return TMDB_IMAGE_BASE_URL + poster_path
        return None

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

    async def _tmdb_search(self, url: str, title: str, year: str | None = None) -> str | None:
        params = {
            "api_key": self._tmdb_api_key,
            "query": title,
            "language": "fr-FR",
            "include_adult": "false",
        }
        if year:
            if url == TMDB_SEARCH_TV_URL:
                params["first_air_date_year"] = year
            elif url == TMDB_SEARCH_MOVIE_URL:
                params["primary_release_year"] = year
        resp = await self._session.get(url, params=params, timeout=10)
        if resp.status in (401, 403):
            if not self._tmdb_auth_warned:
                self._tmdb_auth_warned = True
                _LOGGER.warning(
                    "TMDB a rejete la requete (cle API invalide ou revoquee, code %s) : "
                    "les affiches TMDB resteront indisponibles tant que ce n'est pas "
                    "corrige. Vous pouvez renseigner votre propre cle TMDB dans les "
                    "options de l'integration.",
                    resp.status,
                )
            raise _TmdbTransientError(f"TMDB auth error {resp.status}")
        if resp.status == 429:
            raise _TmdbTransientError("TMDB rate limited (429)")
        if resp.status >= 500:
            raise _TmdbTransientError(f"TMDB server error {resp.status}")
        if resp.status != 200:
            return None
        data = await resp.json()
        results = data.get("results") or []
        if not results:
            return None
        query_norm = self._normalize_title(title)
        for result in results:
            candidate = result.get("title") or result.get("name") or ""
            candidate_norm = self._normalize_title(candidate)
            if candidate_norm and self._titles_match(query_norm, candidate_norm):
                return result.get("poster_path")
            # Repli sur le titre original (non localise) : le titre fr-FR peut
            # diverger du nom XMLTV alors que le titre original correspond.
            original = result.get("original_title") or result.get("original_name") or ""
            original_norm = self._normalize_title(original)
            if (
                original_norm
                and original_norm != candidate_norm
                and self._titles_match(query_norm, original_norm)
            ):
                return result.get("poster_path")
        return None

    @staticmethod
    def _clean_search_query(title: str) -> tuple[str, str | None]:
        """Retire le bruit episode/saison d'un titre XMLTV avant de le
        soumettre a TMDB (voir les regex ci-dessus pour des exemples reels).
        Retourne (titre_nettoye, annee) : annee (extraite d'un marqueur
        "*AAAA") aide a distinguer un reboot de l'original du meme nom.
        Si aucun motif ne correspond, retourne le titre original inchange -
        aucun effet de bord pour les titres deja propres (films, etc.).
        """
        working = title or ""
        year = None
        year_match = _YEAR_MARKER_RE.search(working)
        if year_match:
            year = year_match.group(1)
            working = _YEAR_MARKER_RE.sub("", working)
        before = working
        working = _EPISODE_SUFFIX_RE.sub("", working)
        if working == before:
            working = _SEASON_SUFFIX_RE.sub("", working)
        working = working.strip()
        return (working or title or "", year)

    @staticmethod
    def _titles_match(query_norm: str, candidate_norm: str) -> bool:
        """Return True if a normalized TMDB candidate matches a normalized query.

        A prefix match in either direction: handles XMLTV titles with episode
        suffixes (ex: "Koh-Lanta - S29E01" matching TMDB's "Koh-Lanta") while
        rejecting loose full-text matches where neither is a prefix of the
        other (ex: "Meteo" vs "Miss Meteo").
        """
        return query_norm.startswith(candidate_norm) or candidate_norm.startswith(query_norm)

    @staticmethod
    def _normalize_title(value: str) -> str:
        """Normalise un titre pour comparaison (minuscules, sans accents).

        Utilise pour verifier qu'un resultat TMDB correspond vraiment au
        titre recherche avant d'accepter son affiche, plutot que de
        prendre le premier resultat les yeux fermes : une recherche
        plein texte comme "Meteo" matchait a tort la serie "Miss Meteo"
        alors que le bulletin meteo generique n'a pas de fiche TMDB.
        """
        normalized = unicodedata.normalize("NFD", value or "")
        normalized = "".join(ch for ch in normalized if unicodedata.category(ch) != "Mn")
        normalized = normalized.lower().strip()
        normalized = (
            normalized.replace("dix-sept", "17")
            .replace("dix-huit", "18")
            .replace("dix-neuf", "19")
        )
        # XMLTV et TMDB ne separent pas titre/sous-titre avec la meme
        # ponctuation pour le meme programme (ex: XMLTV "Sisteron : citadelle
        # de tous les defis" vs TMDB "Sisteron, la citadelle de tous les
        # defis" ; "Irish Celtic : le chemin des legendes" vs TMDB "Irish
        # Celtic - Le Chemin des Legendes") : on normalise tous ces
        # separateurs en simple espace pour que la comparaison ne depende pas
        # du signe de ponctuation utilise par chaque source.
        for separator in ("-", ":", ",", ";", "!", "?"):
            normalized = normalized.replace(separator, " ")
        words = [_FR_NUMBER_WORDS.get(word, word) for word in normalized.split()]
        return " ".join(words)

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

    def get_programmes_for_day(
        self, channel_id: str, date_str: str | None = None
    ) -> list[dict] | None:
        """Retourne tous les programmes en cache pour channel_id sur une
        journee de diffusion (de DAY_RESET a DAY_RESET le lendemain), pour
        alimenter la carte "Guide TV". Utilise la meme frontiere que le
        calcul des creneaux pour que les programmes de nuit avant 05h00
        restent rattaches a la soiree precedente. date_str est une date ISO
        (AAAA-MM-JJ) ; si absente, utilise la journee de diffusion en cours.
        """
        if channel_id not in self._programmes_by_channel:
            return None

        tzinfo = dt_util.now().tzinfo
        if date_str:
            try:
                broadcast_day = datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                return None
        else:
            now = dt_util.now()
            broadcast_day = (
                (now - timedelta(days=1)).date()
                if now.time() < DAY_RESET
                else now.date()
            )

        day_start = datetime.combine(broadcast_day, DAY_RESET, tzinfo=tzinfo)
        day_end = day_start + timedelta(days=1)

        return [
            self._programme_dict(p)
            for p in self._programmes_by_channel[channel_id]
            if p.start < day_end and p.stop > day_start
        ]
