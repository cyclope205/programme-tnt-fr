"""The Programme TNT FR integration."""
from __future__ import annotations

import logging
from pathlib import Path

import voluptuous as vol

from homeassistant.components import websocket_api
from homeassistant.components.frontend import add_extra_js_url
from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import (
    CoreState,
    EVENT_HOMEASSISTANT_STARTED,
    HomeAssistant,
    callback,
)
from homeassistant.helpers.event import async_call_later

from .const import (
    CARD_VERSION,
    CHANNEL_ORDER,
    CONF_CHANNELS,
    CONF_TMDB_API_KEY,
    DEFAULT_CHANNELS,
    DOMAIN,
)
from .coordinator import ProgrammeTntFrCoordinator
from .reminders import async_setup_reminders
from .ws_api import async_register_websocket_api

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor"]

CARD_FILENAME = "programme-tnt-fr-card.js"
CARD_URL_PATH = f"/programme_tnt_fr/{CARD_FILENAME}"
_CARD_REGISTERED_KEY = f"{DOMAIN}_card_registered"
_WS_API_REGISTERED_KEY = f"{DOMAIN}_ws_api_registered"


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Programme TNT FR from a config entry."""
    _async_register_ws_api(hass)

    async def _setup_frontend(_event=None) -> None:
        await _async_register_card(hass)

    if hass.state == CoreState.running:
        await _setup_frontend()
    else:
        hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STARTED, _setup_frontend)
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
    if CONF_TMDB_API_KEY in entry.options:
        tmdb_api_key = entry.options[CONF_TMDB_API_KEY] or None
    else:
        tmdb_api_key = entry.data.get(CONF_TMDB_API_KEY)
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
        # cache_headers=True: the URL already carries a cache-buster
        # (?v={CARD_VERSION}), so a version bump changes the URL and is
        # never served stale. Letting the browser cache the file makes
        # subsequent page loads near-instant, shrinking the window in
        # which the custom element registration can lose the race
        # against Lovelace's view/card-picker construction (see
        # _async_sync_lovelace_resource docstring below).
        await hass.http.async_register_static_paths(
            [
                StaticPathConfig(
                    CARD_URL_PATH, str(www_dir / CARD_FILENAME), cache_headers=True
                )
            ]
        )
        hass.data[_CARD_REGISTERED_KEY] = True

    await _async_sync_lovelace_resource(hass)


async def _async_sync_lovelace_resource(hass: HomeAssistant, _now=None) -> None:
    """Register the card as a real Lovelace resource (the normal way).

    This is deliberately the ONLY loading path used when it succeeds.
    Every other well-behaved custom card (installed via HACS) is loaded
    exactly this way: as a plain Lovelace resource that the frontend's
    dashboard bootstrap explicitly awaits before constructing any view.
    That await is what protects those cards from ever showing "Custom
    element doesn't exist".

    add_extra_js_url() instead injects a raw <script type="module"> tag
    into index.html, which is NOT part of that awaited resource list -
    the dashboard can start building cards before it resolves. Calling
    both for the same URL (as an earlier version of this integration
    did) let the browser register the module via this unawaited path,
    silently opting this card out of the same protection every other
    custom card gets - hence the seemingly random "Custom element
    doesn't exist" errors some users saw, even though the file itself
    loaded fine (no 404, no console error). add_extra_js_url is now
    used ONLY as a fallback below, when the proper resource can't be
    registered at all (YAML-mode dashboards).

    If Lovelace itself isn't ready yet (hass.data["lovelace"] not
    populated - a startup race), this retries every 5 seconds
    indefinitely, since Lovelace always eventually loads. YAML-mode
    dashboards (no `resources.async_create_item` ) are a permanent
    state, not a race, so that case falls back to add_extra_js_url
    once instead of retrying forever.
    """
    lovelace_data = hass.data.get("lovelace")
    resources = getattr(lovelace_data, "resources", None)
    if resources is None:
        _LOGGER.debug("Lovelace not ready yet, retrying resource sync in 5s")
        async_call_later(hass, 5, _async_sync_lovelace_resource)
        return
    if not hasattr(resources, "async_create_item"):
        _LOGGER.warning(
            "Lovelace resources are in YAML mode; the card cannot be "
            "auto-registered as a proper resource. Falling back to "
            "add_extra_js_url (works, but loses the load-order "
            "protection other custom cards get - consider adding the "
            "resource by hand in your YAML dashboard config instead)."
        )
        add_extra_js_url(hass, f"{CARD_URL_PATH}?v={CARD_VERSION}")
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
        _LOGGER.warning(
            "Could not auto-register the Lovelace resource for the card; "
            "falling back to add_extra_js_url (works, but loses the "
            "load-order protection other custom cards get).",
            exc_info=True,
        )
        add_extra_js_url(hass, f"{CARD_URL_PATH}?v={CARD_VERSION}")


@websocket_api.websocket_command({vol.Required("type"): "programme_tnt_fr/version"})
@callback
def _websocket_get_version(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict
) -> None:
    """Retourne la version courante de l'integration, pour que la carte
    puisse detecter un decalage avec sa propre version embarquee et
    proposer un rechargement (cache navigateur perime apres mise a jour).
    """
    connection.send_result(
        msg["id"], {"version": CARD_VERSION, "channel_order": CHANNEL_ORDER}
    )


@callback
def _async_register_ws_api(hass: HomeAssistant) -> None:
    """Register the Guide TV card websocket API (once)."""
    if hass.data.get(_WS_API_REGISTERED_KEY):
        return
    async_register_websocket_api(hass)
    websocket_api.async_register_command(hass, _websocket_get_version)
    hass.data[_WS_API_REGISTERED_KEY] = True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok
