"""Config flow for Programme TNT FR."""
from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector

from .const import CONF_CHANNELS, DEFAULT_CHANNELS, DOMAIN, TNT_CHANNELS


def _channels_schema(default: list[str]) -> vol.Schema:
    options = [
        selector.SelectOptionDict(value=channel_id, label=name)
        for channel_id, name in TNT_CHANNELS.items()
    ]
    return vol.Schema(
        {
            vol.Required(CONF_CHANNELS, default=default): selector.selector(
                {
                    "select": {
                        "options": options,
                        "multiple": True,
                        "mode": "list",
                    }
                }
            )
        }
    )


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
                return self.async_create_entry(
                    title="Programme TNT FR", data={CONF_CHANNELS: channels}
                )

        return self.async_show_form(
            step_id="user",
            data_schema=_channels_schema(DEFAULT_CHANNELS),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry):
        return ProgrammeTntFrOptionsFlow(config_entry)


class ProgrammeTntFrOptionsFlow(config_entries.OptionsFlow):
    """Let the user change the list of followed channels later."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self._config_entry = config_entry

    async def async_step_init(self, user_input: dict | None = None):
        errors: dict[str, str] = {}
        current = self._config_entry.options.get(
            CONF_CHANNELS,
            self._config_entry.data.get(CONF_CHANNELS, DEFAULT_CHANNELS),
        )

        if user_input is not None:
            channels = user_input.get(CONF_CHANNELS) or []
            if not channels:
                errors["base"] = "no_channels"
            else:
                return self.async_create_entry(title="", data={CONF_CHANNELS: channels})

        return self.async_show_form(
            step_id="init",
            data_schema=_channels_schema(current),
            errors=errors,
        )
