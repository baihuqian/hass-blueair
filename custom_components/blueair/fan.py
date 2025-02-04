"""Support for Blueair fans."""
from homeassistant.components.fan import (
    FanEntity,
    SUPPORT_SET_SPEED,
)

from typing import Any, Optional

from .const import DOMAIN
from .device import BlueairDataUpdateCoordinator
from .entity import BlueairEntity


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the Blueair fans from config entry."""
    devices: list[BlueairDataUpdateCoordinator] = hass.data[DOMAIN][
        config_entry.entry_id
    ]["devices"]
    entities = []
    for device in devices:
        if device.model != 'foobot':
            entities.extend(
                [
                    BlueairFan(f"{device.device_name} Fan", device),
                ]
            )
    async_add_entities(entities)


class BlueairFan(BlueairEntity, FanEntity):
    """Controls Fan."""

    def __init__(self, name: str, device: BlueairDataUpdateCoordinator):
        """Initialize the temperature sensor."""
        super().__init__("Fan", name, device)
        self._state: float = None

    @property
    def supported_features(self) -> int:
        # If the fan_mode property is supported, enable support for presets
        return SUPPORT_SET_SPEED

    @property
    def is_on(self) -> int:
        return self._device.is_on

    @property
    def percentage(self) -> Optional[int]:
        """Return the current speed percentage."""
        if self._device.fan_speed is not None:
            return int(self._device.fan_speed)
        else:
            return 0

    async def async_set_percentage(self, percentage: int) -> None:
        """Sets fan speed percentage."""
        await self._device.set_fan_speed(percentage)

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self._device.set_on(False)

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self._device.set_fan_speed(11)

    @property
    def speed_count(self) -> int:
        """Return the number of speeds the fan supports."""
        return 100
