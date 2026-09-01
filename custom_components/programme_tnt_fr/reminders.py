"""Scheduled 'notify me before it starts' reminders for Programme TNT FR."""
from __future__ import annotations

import hashlib
import logging
from datetime import timedelta

import voluptuous as vol

from homeassistant.core import HomeAssistant, ServiceCall, ServiceResponse, SupportsResponse
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.event import async_track_point_in_time
from homeassistant.helpers.storage import Store
from homeassistant.util import dt as dt_util

from .const import (
    CONF_MEDIA_PLAYER_TARGETS,
    CONF_NOTIFY_TARGET,
    CONF_REMINDER_PROFILES,
    CONF_TTS_ENGINE,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

STORAGE_VERSION = 1
STORAGE_KEY = f"{DOMAIN}_reminders"
SERVICE_SCHEDULE_REMINDER = "schedule_reminder"
SERVICE_CANCEL_REMINDER = "cancel_reminder"
SERVICE_GET_STATUS = "get_reminder_status"

_REMINDERS_SETUP_KEY = f"{DOMAIN}_reminders_setup"
_UNSUB_KEY = f"{DOMAIN}_reminder_unsubs"

_REMINDER_FIELDS = {
    vol.Required("channel_name"): cv.string,
    vol.Required("program_title"): cv.string,
    vol.Required("start_time"): cv.string,
    vol.Required("minutes_before"): vol.In([5, 10, 15]),
}

# Optional on every service call: which named reminder profile (person -> their
# own notify_target/media_player_targets/tts_engine, configured in the
# integration's options) this reminder is for. Omitted or unknown -> falls
# back to the integration-wide defaults, exactly as before this field existed.
_PROFILE_FIELD = {vol.Optional("profile_name"): cv.string}

SCHEDULE_SCHEMA = vol.Schema({**_REMINDER_FIELDS, **_PROFILE_FIELD})
CANCEL_SCHEMA = vol.Schema({**_REMINDER_FIELDS, **_PROFILE_FIELD})
STATUS_SCHEMA = vol.Schema(
    {
        vol.Required("channel_name"): cv.string,
        vol.Required("program_title"): cv.string,
        vol.Required("start_time"): cv.string,
        **_PROFILE_FIELD,
    }
)

def _reminder_id(
    channel_name: str,
    program_title: str,
    start_time: str,
    minutes_before: int,
    profile_name: str | None = None,
) -> str:
    """Deterministic id derived from the identifying fields.

    Lets the card cancel a reminder using the same data it scheduled it
    with, without needing the server to hand back a generated id. The
    profile name is part of the id so that two profiles (e.g. two people
    in two rooms) scheduling a reminder for the very same program and
    delay don't collide into a single stored reminder.
    """
    raw = f"{channel_name}|{program_title}|{start_time}|{minutes_before}|{profile_name or ''}"
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()

async def async_setup_reminders(hass: HomeAssistant) -> None:
    """Register the reminder services and restore pending reminders.

    Safe to call multiple times (e.g. multiple config entry reloads) - only
    does real work once per HA run. Never raises: a failure here must not
    block the rest of the integration's setup.
    """
    if hass.data.get(_REMINDERS_SETUP_KEY):
        return
    hass.data[_REMINDERS_SETUP_KEY] = True
    hass.data.setdefault(_UNSUB_KEY, {})

    store: Store = Store(hass, STORAGE_VERSION, STORAGE_KEY)
    manager = _ReminderManager(hass, store)

    hass.services.async_register(
        DOMAIN, SERVICE_SCHEDULE_REMINDER, manager.async_handle_schedule, schema=SCHEDULE_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, SERVICE_CANCEL_REMINDER, manager.async_handle_cancel, schema=CANCEL_SCHEMA
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_GET_STATUS,
        manager.async_handle_status,
        schema=STATUS_SCHEMA,
        supports_response=SupportsResponse.ONLY,
    )

    try:
        await manager.async_restore_pending()
    except Exception:  # noqa: BLE001
        _LOGGER.exception(
            "Impossible de recharger les rappels programme_tnt_fr en attente "
            "(les rappels deja programmes avant ce redemarrage sont perdus, "
            "le reste de l'integration n'est pas affecte)"
        )

class _ReminderManager:
    def __init__(self, hass: HomeAssistant, store: Store) -> None:
        self._hass = hass
        self._store = store

    def _resolve_notify_targets(self) -> list[str]:
        """Notify service slugs (e.g. "mobile_app_iphone_fred") to call directly.

        This install's notify integrations register one legacy
        notify.<slug> service per device, not entities - so targets are
        called as hass.services.async_call("notify", slug, ...), never via
        notify.send_message with an entity target.
        """
        for entry in self._hass.config_entries.async_entries(DOMAIN):
            targets = entry.options.get(CONF_NOTIFY_TARGET, entry.data.get(CONF_NOTIFY_TARGET))
            if targets:
                raw = list(targets) if isinstance(targets, list) else [targets]
                return [
                    slug[len("notify.") :] if slug.startswith("notify.") else slug
                    for slug in raw
                ]
        return []

    def _resolve_media_player_targets(self) -> list[str]:
        """media_player entity_ids to announce the reminder on via TTS."""
        for entry in self._hass.config_entries.async_entries(DOMAIN):
            targets = entry.options.get(
                CONF_MEDIA_PLAYER_TARGETS, entry.data.get(CONF_MEDIA_PLAYER_TARGETS)
            )
            if targets:
                return list(targets) if isinstance(targets, list) else [targets]
        return []

    def _resolve_tts_engine(self) -> str | None:
        """tts.* entity_id to use for spoken reminders on media_player targets."""
        for entry in self._hass.config_entries.async_entries(DOMAIN):
            engine = entry.options.get(CONF_TTS_ENGINE, entry.data.get(CONF_TTS_ENGINE))
            if engine:
                return engine
        return None

    def _find_profile(self, profile_name: str | None) -> dict | None:
        """Named reminder profile matching profile_name, if configured and found."""
        if not profile_name:
            return None
        for entry in self._hass.config_entries.async_entries(DOMAIN):
            profiles = entry.options.get(CONF_REMINDER_PROFILES, [])
            for profile in profiles:
                if profile.get("name") == profile_name:
                    return profile
        return None

    def _resolve_targets(self, profile_name: str | None) -> tuple[list[str], list[str], str | None]:
        """(notify targets, media_player targets, tts engine) for this reminder.

        Uses the named profile's own devices when profile_name matches a
        configured profile; otherwise falls back to the integration-wide
        defaults, exactly like before profiles existed.
        """
        profile = self._find_profile(profile_name)
        if profile is not None:
            raw_targets = profile.get(CONF_NOTIFY_TARGET) or []
            raw_targets = raw_targets if isinstance(raw_targets, list) else [raw_targets]
            targets = [
                slug[len("notify.") :] if slug.startswith("notify.") else slug
                for slug in raw_targets
            ]
            media_targets = profile.get(CONF_MEDIA_PLAYER_TARGETS) or []
            media_targets = media_targets if isinstance(media_targets, list) else [media_targets]
            return targets, media_targets, profile.get(CONF_TTS_ENGINE)
        return (
            self._resolve_notify_targets(),
            self._resolve_media_player_targets(),
            self._resolve_tts_engine(),
        )

    async def async_handle_schedule(self, call: ServiceCall) -> None:
        channel_name = call.data["channel_name"]
        program_title = call.data["program_title"]
        start_time_raw = call.data["start_time"]
        minutes_before = call.data["minutes_before"]
        profile_name = call.data.get("profile_name")

        targets, media_player_targets, tts_engine = self._resolve_targets(profile_name)
        if not media_player_targets or not tts_engine:
            media_player_targets = []
        if not targets and not media_player_targets:
            raise ServiceValidationError(
                "Aucun appareil de notification configure - configure-le dans "
                "les options de l'integration Programme TNT FR."
            )

        start_time = dt_util.parse_datetime(start_time_raw)
        if start_time is None:
            raise ServiceValidationError("Heure de debut de programme invalide.")

        fire_time = start_time - timedelta(minutes=minutes_before)
        if fire_time <= dt_util.now():
            raise ServiceValidationError(
                "Trop tard pour programmer ce rappel : il ne reste plus assez "
                "de temps avant le debut du programme."
            )

        reminder_id = _reminder_id(
            channel_name, program_title, start_time_raw, minutes_before, profile_name
        )
        reminder = {
            "id": reminder_id,
            "channel_name": channel_name,
            "program_title": program_title,
            "minutes_before": minutes_before,
            "profile_name": profile_name,
            "fire_time": fire_time.isoformat(),
            "targets": targets,
            "media_player_targets": media_player_targets,
            "tts_engine": tts_engine,
        }
        await self._async_save(reminder)
        self._schedule(reminder)

    async def async_handle_cancel(self, call: ServiceCall) -> None:
        reminder_id = _reminder_id(
            call.data["channel_name"],
            call.data["program_title"],
            call.data["start_time"],
            call.data["minutes_before"],
            call.data.get("profile_name"),
        )
        unsub_map = self._hass.data.setdefault(_UNSUB_KEY, {})
        unsub = unsub_map.pop(reminder_id, None)
        if unsub:
            unsub()
        await self._async_remove(reminder_id)

    async def async_handle_status(self, call: ServiceCall) -> ServiceResponse:
        channel_name = call.data["channel_name"]
        program_title = call.data["program_title"]
        start_time = call.data["start_time"]
        profile_name = call.data.get("profile_name")
        data = await self._store.async_load() or {"reminders": []}
        existing_ids = {r["id"] for r in data.get("reminders", [])}
        scheduled = [
            minutes
            for minutes in (5, 10, 15)
            if _reminder_id(channel_name, program_title, start_time, minutes, profile_name)
            in existing_ids
        ]
        return {"scheduled_minutes": scheduled}

    async def async_restore_pending(self) -> None:
        data = await self._store.async_load()
        if not data:
            return
        now = dt_util.now()
        kept = []
        for reminder in data.get("reminders", []):
            fire_time = dt_util.parse_datetime(reminder.get("fire_time", ""))
            if fire_time is None or fire_time <= now:
                continue
            kept.append(reminder)
            self._schedule(reminder)
        if len(kept) != len(data.get("reminders", [])):
            await self._store.async_save({"reminders": kept})

    def _schedule(self, reminder: dict) -> None:
        fire_time = dt_util.parse_datetime(reminder["fire_time"])

        async def _fire(_now) -> None:
            self._hass.data.setdefault(_UNSUB_KEY, {}).pop(reminder["id"], None)
            await self._async_remove(reminder["id"])
            await self._async_notify(reminder)

        unsub = async_track_point_in_time(self._hass, _fire, fire_time)
        self._hass.data.setdefault(_UNSUB_KEY, {})[reminder["id"]] = unsub

    def _alexa_notify_slug(self, entity_id: str) -> str | None:
        """notify.alexa_media_<slug> service name for this entity, if any.

        Alexa Media Player registers both a media_player entity and a
        notify.alexa_media_<slug> service using the same device slug. So
        if someone picks their Echo from the "media player" field (the
        obvious, expected place - it IS a media player after all), we
        still route it through Alexa's own voice via the notify service
        instead of tts.speak, which needs a publicly reachable URL for a
        generated audio file - something most home installs (Tailscale-
        only external_url, no Nabu Casa Cloud) can't offer Amazon's
        servers. This makes the intuitive choice work, instead of only
        the "appareil a notifier" field.
        """
        registry = er.async_get(self._hass)
        entry = registry.async_get(entity_id)
        if entry is None or entry.platform != "alexa_media":
            return None
        slug = "alexa_media_" + entity_id.split(".", 1)[1]
        if self._hass.services.has_service("notify", slug):
            return slug
        return None

    async def _async_notify(self, reminder: dict) -> None:
        targets = reminder.get("targets") or self._resolve_notify_targets()
        media_player_targets_early = reminder.get("media_player_targets") or []
        if not targets and not media_player_targets_early:
            _LOGGER.warning(
                "Rappel pour %s ignore : aucun appareil de notification "
                "configure dans les options de l'integration Programme TNT FR",
                reminder["program_title"],
            )
            return
        message = (
            f"{reminder['program_title']} commence dans "
            f"{reminder['minutes_before']} min sur {reminder['channel_name']}"
        )
        for slug in targets:
            try:
                service_data = {"title": "Programme TNT FR", "message": message}
                if slug.startswith("alexa_media"):
                    # Ask Alexa to speak the message in its own voice
                    # instead of posting a silent notification to the
                    # Alexa app - avoids needing a publicly reachable
                    # URL for a generated audio file (see _notify_options
                    # docstring in config_flow.py for the full reasoning).
                    service_data["data"] = {"type": "tts"}
                await self._hass.services.async_call(
                    "notify",
                    slug,
                    service_data,
                )
            except Exception:  # noqa: BLE001
                _LOGGER.exception(
                    "Echec de l'envoi du rappel pour %s via notify.%s",
                    reminder["program_title"],
                    slug,
                )

        media_player_targets = reminder.get("media_player_targets") or []
        tts_engine = reminder.get("tts_engine") or self._resolve_tts_engine()
        for player in media_player_targets:
            alexa_slug = self._alexa_notify_slug(player)
            if alexa_slug:
                try:
                    await self._hass.services.async_call(
                        "notify",
                        alexa_slug,
                        {
                            "title": "Programme TNT FR",
                            "message": message,
                            "data": {"type": "tts"},
                        },
                    )
                except Exception:  # noqa: BLE001
                    _LOGGER.exception(
                        "Echec de l'annonce vocale Alexa du rappel pour %s sur %s",
                        reminder["program_title"],
                        player,
                    )
                continue
            if not tts_engine:
                _LOGGER.warning(
                    "Pas de moteur TTS configure pour annoncer le rappel de %s sur %s",
                    reminder["program_title"],
                    player,
                )
                continue
            try:
                await self._hass.services.async_call(
                    "tts",
                    "speak",
                    {"media_player_entity_id": player, "message": message},
                    target={"entity_id": tts_engine},
                )
            except Exception:  # noqa: BLE001
                _LOGGER.exception(
                    "Echec de l'annonce vocale du rappel pour %s sur %s",
                    reminder["program_title"],
                    player,
                )

    async def _async_save(self, reminder: dict) -> None:
        data = await self._store.async_load() or {"reminders": []}
        reminders = [r for r in data.get("reminders", []) if r["id"] != reminder["id"]]
        reminders.append(reminder)
        data["reminders"] = reminders
        await self._store.async_save(data)

    async def _async_remove(self, reminder_id: str) -> None:
        data = await self._store.async_load() or {"reminders": []}
        data["reminders"] = [r for r in data.get("reminders", []) if r["id"] != reminder_id]
        await self._store.async_save(data)
