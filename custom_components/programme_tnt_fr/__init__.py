"""The Programme TNT FR integration."""
from __future__ import annotations

import logging
from pathlib import Path

from homeassistant.components.frontend import add_extra_js_url
from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback

from .const import CONF_CHANNELS, DEFAULT_CHANNELS, DOMAIN
from .coordinator import ProgrammeTntFrCoordinator
from .ws_api import async_register_websocket_api

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor"]

CARD_FILENAME = "programme-tnt-fr-card.js"
CARD_URL_PATH = f"/programme_tnt_fr/{CARD_FILENAME}"
CARD_VERSION = "2.1.12"
_CARD_REGISTERED_KEY = f"{DOMAIN}_card_registered"
_WS_API_REGISTERED_KEY = f"{DOMAIN}_ws_api_registered"


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Programme TNT FR from a config entry."""
    await _async_register_card(hass)
    _async_register_ws_api(hass)

    channels = entry.options.get(
        CONF_CHANNELS, entry.data.get(CONF_CHANNELS, DEFAULT_CHANNELS)
    )
    coordinator = ProgrammeTntFrCoordinator(hass, channels)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    return True

async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload the entry when its options change (e.g. channel selection)."""
    await hass.config_entries.async_reload(entry.entry_id)

async def _async_register_card(hass: HomeAssistant) -> None:
    """Serve the Lovelace card from this integration and auto-register it.

    This avoids asking the user to manually add a Lovelace resource: the
    card is served locally by Home Assistant and injected on every
    dashboard load, the same way built-in frontend assets are.
    """
    if hass.data.get(_CARD_REGISTERED_KEY):
        return

    www_dir = Path(__file__).parent / "www"
    await hass.http.async_register_static_paths(
        [
            StaticPathConfig(
                CARD_URL_PATH, str(www_dir / CARD_FILENAME), cache_headers=False
            )
        ]
    )
    add_extra_js_url(hass, f"{CARD_URL_PATH}?v={CARD_VERSION}")
    hass.data[_CARD_REGISTERED_KEY] = True

@callback
def _async_register_ws_api(hass: HomeAssistant) -> None:
    """Register the Guide TV card websocket API (once)."""
    if hass.data.get(_WS_API_REGISTERED_KEY):
        return
    async_register_websocket_api(hass)
    hass.data[_WS_API_REGISTERED_KEY] = True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok
