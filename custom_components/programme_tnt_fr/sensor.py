"""Sensor platform for Programme TNT FR."""
from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, TNT_CHANNELS
from .coordinator import ProgrammeTntFrCoordinator


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the Programme TNT FR sensors for one config entry."""
    coordinator: ProgrammeTntFrCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        ProgrammeTntFrSensor(coordinator, entry, channel_id)
        for channel_id in coordinator.data
    )


class ProgrammeTntFrSensor(CoordinatorEntity[ProgrammeTntFrCoordinator], SensorEntity):
    """Exposes the current / prime-time / late-night programmes of one TNT channel."""

    _attr_icon = "mdi:television-classic"

    def __init__(
        self,
        coordinator: ProgrammeTntFrCoordinator,
        entry: ConfigEntry,
        channel_id: str,
    ) -> None:
        super().__init__(coordinator)
        self._channel_id = channel_id
        self._attr_unique_id = f"{entry.entry_id}_{channel_id}"
        self._attr_name = TNT_CHANNELS.get(channel_id, channel_id)
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, "programme_tnt_fr")},
            name="Programme TNT FR",
            manufacturer="xmltvfr.fr",
            entry_type="service",
        )

    @property
    def _data(self) -> dict:
        return self.coordinator.data.get(self._channel_id, {})

    @property
    def native_value(self) -> str | None:
        current = self._data.get("current")
        return current.get("title") if current else None

    @property
    def entity_picture(self) -> str | None:
        return self._data.get("channel_icon")

    @property
    def extra_state_attributes(self) -> dict:
        data = self._data
        return {
            "channel_id": self._channel_id,
            "channel_name": data.get("channel_name"),
            "channel_icon": data.get("channel_icon"),
            "current": data.get("current"),
            "prime_time": data.get("prime_time"),
            "second_part": data.get("second_part"),
        }
