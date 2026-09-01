"""Config flow for Programme TNT FR."""
from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import selector

from .const import (
    ALL_CHANNELS,
    CONF_CHANNELS,
    CONF_MEDIA_PLAYER_TARGETS,
    CONF_NOTIFY_TARGET,
    CONF_REMINDER_PROFILES,
    CONF_TMDB_API_KEY,
    CONF_TTS_ENGINE,
    DEFAULT_CHANNELS,
    DOMAIN,
    TNT_CHANNELS,
)


def _notify_options(hass: HomeAssistant) -> list[selector.SelectOptionDict]:
    """Notify services actually registered on this HA instance.

    Built dynamically (not a hardcoded list) since available targets
    (mobile_app_*, alexa_media_*, ...) differ per install. Excluded:
    "send_message" (needs an entity-based notify target, which this
    install's notify integrations - legacy service-per-device style -
    do not register); "notify" and "persistent_notification" (generic,
    not tied to a specific person's device).

    "alexa_media_*" slugs are kept: the reminder-firing code calls them
    with data={"type": "tts"} so Alexa speaks the message itself, in its
    own voice, with no audio file to fetch. That matters because the
    other option (media_player_targets + tts_engine, using tts.speak)
    needs Amazon's servers to download a generated audio file from this
    HA instance's external URL - which fails for any install that isn't
    reachable from the public internet (e.g. Tailscale-only external_url,
    no Nabu Casa Cloud), producing a "can't access..." error spoken by
    the Echo instead of the reminder.
    """
    services = hass.services.async_services().get("notify", {})
    return [
        selector.SelectOptionDict(value=slug, label=slug)
        for slug in sorted(services)
        if slug not in {"send_message", "notify", "persistent_notification"}
    ]


def _schema(
    hass: HomeAssistant,
    channels_default: list[str],
    tmdb_api_key_default: str | None = None,
) -> vol.Schema:
    options = [
        selector.SelectOptionDict(value=channel_id, label=name)
        for channel_id, name in ALL_CHANNELS.items()
    ]
    fields: dict = {}

    tmdb_selector = selector.selector({"text": {}})
    if tmdb_api_key_default:
        fields[vol.Optional(CONF_TMDB_API_KEY, default=tmdb_api_key_default)] = tmdb_selector
    else:
        fields[vol.Optional(CONF_TMDB_API_KEY)] = tmdb_selector

    fields[vol.Required(CONF_CHANNELS, default=channels_default)] = selector.selector(
        {
            "select": {
                "options": options,
                "multiple": True,
                "mode": "list",
            }
        }
    )
    return vol.Schema(fields)


def _profile_schema(
    hass: HomeAssistant,
    name_default: str | None = None,
    notify_default: list[str] | None = None,
    media_player_default: list[str] | None = None,
    tts_default: str | None = None,
) -> vol.Schema:
    """Form to create or edit one named reminder profile (a person -> their devices).

    Mirrors the notify/media_player/tts fields of the general settings
    form, but scoped to a single named profile instead of the whole
    integration - so two people who each want reminders on their own
    phone/speaker don't have to share one global target list. Passing
    the *_default arguments pre-fills the form for editing an existing
    profile instead of creating a new one.
    """
    notify_selector = selector.selector(
        {
            "select": {
                "options": _notify_options(hass),
                "multiple": True,
                "mode": "dropdown",
            }
        }
    )
    media_player_selector = selector.selector(
        {"entity": {"domain": "media_player", "multiple": True}}
    )
    tts_selector = selector.selector({"entity": {"domain": "tts", "multiple": False}})
    fields: dict = {}
    if name_default is not None:
        fields[vol.Required("name", default=name_default)] = selector.selector({"text": {}})
    else:
        fields[vol.Required("name")] = selector.selector({"text": {}})
    if notify_default:
        fields[vol.Optional(CONF_NOTIFY_TARGET, default=notify_default)] = notify_selector
    else:
        fields[vol.Optional(CONF_NOTIFY_TARGET)] = notify_selector
    if media_player_default:
        fields[
            vol.Optional(CONF_MEDIA_PLAYER_TARGETS, default=media_player_default)
        ] = media_player_selector
    else:
        fields[vol.Optional(CONF_MEDIA_PLAYER_TARGETS)] = media_player_selector
    if tts_default:
        fields[vol.Optional(CONF_TTS_ENGINE, default=tts_default)] = tts_selector
    else:
        fields[vol.Optional(CONF_TTS_ENGINE)] = tts_selector
    return vol.Schema(fields)


class ProgrammeTntFrConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Programme TNT FR."""

    VERSION = 1

    async def async_step_user(self, user_input: dict | None = None):
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        errors: dict[str, str] = {}
        if user_input is not None:
            channels = user_input.get(CONF_CHANNELS) or []
            if not channels:
                errors["base"] = "no_channels"
            else:
                data: dict = {CONF_CHANNELS: channels}
                if user_input.get(CONF_TMDB_API_KEY):
                    data[CONF_TMDB_API_KEY] = user_input[CONF_TMDB_API_KEY]
                return self.async_create_entry(title="Programme TNT FR", data=data)

        return self.async_show_form(
            step_id="user",
            data_schema=_schema(self.hass, DEFAULT_CHANNELS),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry):
        return ProgrammeTntFrOptionsFlow(config_entry)


class ProgrammeTntFrOptionsFlow(config_entries.OptionsFlow):
    """Let the user change the followed channels, and manage reminder profiles."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self._config_entry = config_entry
        self._profiles: list[dict] = [
            dict(p) for p in config_entry.options.get(CONF_REMINDER_PROFILES, [])
        ]
        self._editing_profile: str | None = None

    async def async_step_init(self, user_input: dict | None = None):
        return self.async_show_menu(
            step_id="init",
            menu_options=["general", "profiles"],
        )

    async def async_step_general(self, user_input: dict | None = None):
        errors: dict[str, str] = {}
        current_channels = self._config_entry.options.get(
            CONF_CHANNELS,
            self._config_entry.data.get(CONF_CHANNELS, DEFAULT_CHANNELS),
        )
        current_tmdb_api_key = self._config_entry.options.get(
            CONF_TMDB_API_KEY,
            self._config_entry.data.get(CONF_TMDB_API_KEY),
        )

        if user_input is not None:
            channels = user_input.get(CONF_CHANNELS) or []
            if not channels:
                errors["base"] = "no_channels"
            else:
                data: dict = {
                    CONF_CHANNELS: channels,
                    CONF_REMINDER_PROFILES: self._profiles,
                }
                if user_input.get(CONF_TMDB_API_KEY):
                    data[CONF_TMDB_API_KEY] = user_input[CONF_TMDB_API_KEY]
                return self.async_create_entry(title="", data=data)

        return self.async_show_form(
            step_id="general",
            data_schema=_schema(
                self.hass,
                current_channels,
                current_tmdb_api_key,
            ),
            errors=errors,
        )

    async def async_step_profiles(self, user_input: dict | None = None):
        actions = [
            selector.SelectOptionDict(value="add", label="Ajouter un profil"),
        ]
        for profile in self._profiles:
            actions.append(
                selector.SelectOptionDict(
                    value=f"edit:{profile['name']}",
                    label=f"Modifier {profile['name']}",
                )
            )
            actions.append(
                selector.SelectOptionDict(
                    value=f"remove:{profile['name']}",
                    label=f"Supprimer {profile['name']}",
                )
            )
        actions.append(selector.SelectOptionDict(value="done", label="Terminer"))

        if user_input is not None:
            action = user_input.get("action")
            if action == "add":
                self._editing_profile = None
                return await self.async_step_add_profile()
            if action and action.startswith("edit:"):
                self._editing_profile = action[len("edit:") :]
                return await self.async_step_add_profile()
            if action and action.startswith("remove:"):
                name = action[len("remove:") :]
                self._profiles = [p for p in self._profiles if p["name"] != name]
                return await self.async_step_profiles()
            return self._save_profiles()

        names = ", ".join(p["name"] for p in self._profiles) or "aucun profil configure"
        return self.async_show_form(
            step_id="profiles",
            data_schema=vol.Schema(
                {
                    vol.Required("action", default="done"): selector.selector(
                        {"select": {"options": actions, "mode": "list"}}
                    )
                }
            ),
            description_placeholders={"profiles": names},
        )

    async def async_step_add_profile(self, user_input: dict | None = None):
        errors: dict[str, str] = {}
        editing_name = self._editing_profile
        if user_input is not None:
            name = (user_input.get("name") or "").strip()
            if not name:
                errors["base"] = "no_name"
            elif any(
                p["name"] == name
                for p in self._profiles
                if editing_name is None or p["name"] != editing_name
            ):
                errors["base"] = "duplicate_name"
            else:
                profile: dict = {"name": name}
                if user_input.get(CONF_NOTIFY_TARGET):
                    profile[CONF_NOTIFY_TARGET] = user_input[CONF_NOTIFY_TARGET]
                if user_input.get(CONF_MEDIA_PLAYER_TARGETS):
                    profile[CONF_MEDIA_PLAYER_TARGETS] = user_input[CONF_MEDIA_PLAYER_TARGETS]
                if user_input.get(CONF_TTS_ENGINE):
                    profile[CONF_TTS_ENGINE] = user_input[CONF_TTS_ENGINE]
                if editing_name is not None:
                    self._profiles = [
                        profile if p["name"] == editing_name else p
                        for p in self._profiles
                    ]
                else:
                    self._profiles.append(profile)
                self._editing_profile = None
                return await self.async_step_profiles()

        existing = None
        if editing_name is not None:
            existing = next(
                (p for p in self._profiles if p["name"] == editing_name), None
            )

        if errors and user_input is not None:
            name_default = user_input.get("name")
            notify_default = user_input.get(CONF_NOTIFY_TARGET)
            media_player_default = user_input.get(CONF_MEDIA_PLAYER_TARGETS)
            tts_default = user_input.get(CONF_TTS_ENGINE)
        else:
            name_default = existing["name"] if existing else None
            notify_default = existing.get(CONF_NOTIFY_TARGET) if existing else None
            media_player_default = (
                existing.get(CONF_MEDIA_PLAYER_TARGETS) if existing else None
            )
            tts_default = existing.get(CONF_TTS_ENGINE) if existing else None

        return self.async_show_form(
            step_id="add_profile",
            data_schema=_profile_schema(
                self.hass,
                name_default=name_default,
                notify_default=notify_default,
                media_player_default=media_player_default,
                tts_default=tts_default,
            ),
            errors=errors,
        )

    def _save_profiles(self):
        data = dict(self._config_entry.options)
        data[CONF_REMINDER_PROFILES] = self._profiles
        return self.async_create_entry(title="", data=data)
