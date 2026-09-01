"""WebSocket API for the Programme TNT FR Guide TV card."""
from __future__ import annotations

import voluptuous as vol

from homeassistant.components import websocket_api
from homeassistant.core import HomeAssistant, callback

from .const import CONF_REMINDER_PROFILES, DOMAIN


@callback
def async_register_websocket_api(hass: HomeAssistant) -> None:
    """Register the programme_tnt_fr websocket commands."""
    websocket_api.async_register_command(hass, websocket_get_programmes)
    websocket_api.async_register_command(hass, websocket_get_reminder_profiles)


@websocket_api.websocket_command(
    {
        vol.Required("type"): "programme_tnt_fr/programmes",
        vol.Required("channels"): [str],
        vol.Optional("date"): str,
    }
)
@callback
def websocket_get_programmes(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict
) -> None:
    """Retourne, pour les chaines demandees, tous les programmes en cache
    pour une journee de diffusion donnee. Alimente la carte "Guide TV"
    (custom:programme-tnt-fr-guide-card), qui a besoin de la liste complete
    des programmes d'une chaine (pas seulement en ce moment / 1re / 2e
    partie de soiree comme les sensors), sans polluer le recorder avec des
    attributs de sensor supplementaires.
    """
    channels = msg["channels"]
    date_str = msg.get("date")

    programmes: dict[str, list[dict]] = {}
    for coordinator in hass.data.get(DOMAIN, {}).values():
        for channel_id in channels:
            if channel_id in programmes:
                continue
            day_progs = coordinator.get_programmes_for_day(channel_id, date_str)
            if day_progs is not None:
                programmes[channel_id] = day_progs

    connection.send_result(msg["id"], {"programmes": programmes})


@websocket_api.websocket_command({vol.Required("type"): "programme_tnt_fr/reminder_profiles"})
@callback
def websocket_get_reminder_profiles(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict
) -> None:
    """Retourne les noms des profils de rappel configures (options de
    l'integration), pour que la carte propose un choix de profil au moment
    de programmer un rappel quand plusieurs personnes/appareils sont
    configures. Liste vide si aucun profil n'a ete cree : la carte se
    rabat alors sur les cibles globales, sans afficher de selecteur.
    """
    names: list[str] = []
    for entry in hass.config_entries.async_entries(DOMAIN):
        for profile in entry.options.get(CONF_REMINDER_PROFILES, []):
            name = profile.get("name")
            if name and name not in names:
                names.append(name)

    connection.send_result(msg["id"], {"profiles": names})
