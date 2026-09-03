"""The Programme TNT FR integration."""
from __future__ import annotations

import logging
from pathlib import Path

from homeassistant.components.frontend import add_extra_js_url
from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback

from .const import CONF_CHANNELS, CONF_TMDB_API_KEY, DEFAULT_CHANNELS, DOMAIN
from .coordinator import ProgrammeTntFrCoordinator
from .reminders import async_setup_reminders
from .ws_api import async_register_websocket_api

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor"]

CARD_FILENAME = "programme-tnt-fr-card.js"
CARD_URL_PATH = f"/programme_tnt_fr/{CARD_FILENAME}"
CARD_VERSION = "2.2.3"
_CARD_REGISTERED_KEY = f"{DOMAIN}_card_registered"
_WS_API_REGISTERED_KEY = f"{DOMAIN}_ws_api_registered"


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Programme TNT FR from a config entry."""
    await _async_register_card(hass)
    _async_register_ws_api(hass)
    try:
        await async_setup_reminders(hass)
    except Exception:  # noqa: BLE001
        _LOGGER.exception(
            "Echec de l'initialisation des rappels programme_tnt_fr "
            "(fonctionnalite desactivee, le reste de l'integration n'est pas affecte)"
        )

    channels = entry.options.get(
        CONF_CHANNELS, entry.data.get(CONF_CHANNELS, DEFAULT_CHANNELS)
    )
    tmdb_api_key = entry.options.get(
        CONF_TMDB_API_KEY, entry.data.get(CONF_TMDB_API_KEY)
    )
    coordinator = ProgrammeTntFrCoordinator(hass, channels, tmdb_api_key)
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
    if not hass.data.get(_CARD_REGISTERED_KEY):
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

    await _async_sync_lovelace_resource(hass)


async def _async_sync_lovelace_resource(hass: HomeAssistant) -> None:
    """Additionally register the card as a real Lovelace resource.

    add_extra_js_url only injects a <script type="module"> tag into the
    frontend's index.html, which the browser only re-evaluates on a
    genuine full page reload. If the custom element registration loses
    the race against Lovelace's own view construction (more likely on
    slower devices or dashboards with many other custom resources), the
    browser is stuck showing "Custom element doesn't exist" until the
    user manually hard-refreshes - some users have reported needing to
    add the resource by hand for it to work at all.

    A real Lovelace resource (type: module) is loaded by the frontend's
    own resource loader every time a dashboard/view connects within the
    running session, giving it another chance to register without a
    full reload. This is purely additive on top of add_extra_js_url
    (kept for the very first load) and best-effort: any failure here is
    logged and does not affect the rest of setup, since it only touches
    storage-mode Lovelace resources (a fresh install with no dashboards
    configured yet, or YAML-mode resources, are silently skipped).
    """
    lovelace_data = hass.data.get("lovelace")
    resources = getattr(lovelace_data, "resources", None)
    if resources is None or not hasattr(resources, "async_create_item"):
        return

    target_url = f"{CARD_URL_PATH}?v={CARD_VERSION}"
    try:
        if not getattr(resources, "loaded", False):
            await resources.async_load()

        existing = next(
            (
                item
                for item in resources.async_items()
                if str(item.get("url", "")).split("?", 1)[0] == CARD_URL_PATH
            ),
            None,
        )
        if existing is None:
            await resources.async_create_item(
                {"res_type": "module", "url": target_url}
            )
        elif existing.get("url") != target_url:
            await resources.async_update_item(existing["id"], {"url": target_url})
    except Exception:  # noqa: BLE001
        _LOGGER.debug(
            "Could not auto-register the Lovelace resource for the card; "
            "add_extra_js_url is still active as a fallback.",
            exc_info=True,
        )


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
