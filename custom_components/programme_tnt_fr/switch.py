"""Switch platform: a simple on/off toggle for the Guide TV conditional
card."""
from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the Guide TV toggle switch."""
    async_add_entities([ProgrammeTntFrGuideToggle(entry)])


class ProgrammeTntFrGuideToggle(SwitchEntity, RestoreEntity):
    """Toggle used to show/hide the Guide TV conditional card.

    Pure UI convenience, no coordinator/network data involved: the
    carousel card header has a "Guide TV" link that flips this switch,
    and a Lovelace `type: conditional` card wrapping
    `custom:programme-tnt-fr-guide-card` watches its state (see README).
    """

    _attr_name = "Guide TV"
    _attr_icon = "mdi:television-guide"
    _attr_has_entity_name = False

    def __init__(self, entry: ConfigEntry) -> None:
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_guide_toggle"
        self._attr_is_on = False
        self._attr_extra_state_attributes = {"guide_toggle": True}

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        last_state = await self.async_get_last_state()
        if last_state is not None:
            self._attr_is_on = last_state.state == "on"

    async def async_turn_on(self, **kwargs) -> None:
        self._attr_is_on = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs) -> None:
        self._attr_is_on = False
        self.async_write_ha_state()
