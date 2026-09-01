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
    CONF_TTS_ENGINE,
    DEFAULT_CHANNELS,
    DOMAIN,
    TNT_CHANNELS,
)


def _notify_options(hass: HomeAssistant) -> list[selector.SelectOptionDict]:
    """Notify services actually registered on this HA instance.

    Built dynamically (not a hardcoded list) since available targets
    (mobile_app_*, alexa_media_*, ...) differ per install. "send_message"
    is excluded: it needs an entity-based notify target, which this
    install's notify integrations (legacy service-per-device style) do
    not register - calling notify.<slug> directly is what actually works
    here.
    """
    services = hass.services.async_services().get("notify", {})
    return [
        selector.SelectOptionDict(value=slug, label=slug)
        for slug in sorted(services)
        if slug != "send_message"
    ]


def _schema(
    hass: HomeAssistant,
    channels_default: list[str],
    notify_targets_default: list[str] | None = None,
    media_player_defaults: list[str] | None = None,
    tts_engine_default: str | None = None,
) -> vol.Schema:
    options = [
        selector.SelectOptionDict(value=channel_id, label=name)
        for channel_id, name in ALL_CHANNELS.items()
    ]
    notify_selector = selector.selector(
        {
            "select": {
                "options": _notify_options(hass),
                "multiple": True,
                "mode": "dropdown",
            }
        }
    )
    fields: dict = {}
    if notify_targets_default:
        fields[vol.Optional(CONF_NOTIFY_TARGET, default=notify_targets_default)] = notify_selector
    else:
        fields[vol.Optional(CONF_NOTIFY_TARGET)] = notify_selector

    media_player_selector = selector.selector(
        {"entity": {"domain": "media_player", "multiple": True}}
    )
    if media_player_defaults:
        fields[
            vol.Optional(CONF_MEDIA_PLAYER_TARGETS, default=media_player_defaults)
        ] = media_player_selector
    else:
        fields[vol.Optional(CONF_MEDIA_PLAYER_TARGETS)] = media_player_selector

    tts_selector = selector.selector({"entity": {"domain": "tts", "multiple": False}})
    if tts_engine_default:
        fields[vol.Optional(CONF_TTS_ENGINE, default=tts_engine_default)] = tts_selector
    else:
        fields[vol.Optional(CONF_TTS_ENGINE)] = tts_selector

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
                if user_input.get(CONF_NOTIFY_TARGET):
                    data[CONF_NOTIFY_TARGET] = user_input[CONF_NOTIFY_TARGET]
                if user_input.get(CONF_MEDIA_PLAYER_TARGETS):
                    data[CONF_MEDIA_PLAYER_TARGETS] = user_input[CONF_MEDIA_PLAYER_TARGETS]
                if user_input.get(CONF_TTS_ENGINE):
                    data[CONF_TTS_ENGINE] = user_input[CONF_TTS_ENGINE]
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
    """Let the user change the followed channels later."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self._config_entry = config_entry

    async def async_step_init(self, user_input: dict | None = None):
        errors: dict[str, str] = {}
        current_channels = self._config_entry.options.get(
            CONF_CHANNELS,
            self._config_entry.data.get(CONF_CHANNELS, DEFAULT_CHANNELS),
        )
        current_notify_targets = self._config_entry.options.get(
            CONF_NOTIFY_TARGET,
            self._config_entry.data.get(CONF_NOTIFY_TARGET),
        )
        current_media_players = self._config_entry.options.get(
            CONF_MEDIA_PLAYER_TARGETS,
            self._config_entry.data.get(CONF_MEDIA_PLAYER_TARGETS),
        )
        current_tts_engine = self._config_entry.options.get(
            CONF_TTS_ENGINE,
            self._config_entry.data.get(CONF_TTS_ENGINE),
        )

        if user_input is not None:
            channels = user_input.get(CONF_CHANNELS) or []
            if not channels:
                errors["base"] = "no_channels"
            else:
                data: dict = {CONF_CHANNELS: channels}
                if user_input.get(CONF_NOTIFY_TARGET):
                    data[CONF_NOTIFY_TARGET] = user_input[CONF_NOTIFY_TARGET]
                if user_input.get(CONF_MEDIA_PLAYER_TARGETS):
                    data[CONF_MEDIA_PLAYER_TARGETS] = user_input[CONF_MEDIA_PLAYER_TARGETS]
                if user_input.get(CONF_TTS_ENGINE):
                    data[CONF_TTS_ENGINE] = user_input[CONF_TTS_ENGINE]
                return self.async_create_entry(title="", data=data)

        return self.async_show_form(
            step_id="init",
            data_schema=_schema(
                self.hass,
                current_channels,
                current_notify_targets,
                current_media_players,
                current_tts_engine,
            ),
            errors=errors,
        )
