"""Support for Blueair sensors."""
from homeassistant.components.sensor import SensorEntity
from homeassistant.const import DEVICE_CLASS_PM25

from .const import DOMAIN
from .device import BlueairDataUpdateCoordinator
from .entity import BlueairEntity


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the Blueair sensors from config entry."""
    devices: list[BlueairDataUpdateCoordinator] = hass.data[DOMAIN][
        config_entry.entry_id
    ]["devices"]
    entities = []
    for device in devices:
        # Don't add sensors to classic models
        if (
            device.model.startswith("classic") and not device.model.endswith("i")
        ) or device.model == "foobot":
            pass
        else:            
            entities.extend(
                [
                    BlueairPM25Sensor(f"{device.device_name}_pm25", device),
                    BlueairFilterUsageSensor(f"{device.device_name}_filter_usage", device),
                ]
            )
    async_add_entities(entities)

class BlueairPM25Sensor(BlueairEntity, SensorEntity):
    """Monitors the pm25"""

    _attr_device_class = DEVICE_CLASS_PM25
    _attr_native_unit_of_measurement = "µg/m³"

    def __init__(self, name, device):
        """Initialize the pm25 sensor."""
        super().__init__("pm25", name, device)
        self._state: float = None

    @property
    def native_value(self) -> float:
        """Return the current pm25."""
        if self._device.pm2_5 is None:
            return None
        return round(self._device.pm2_5, 0)

class BlueairFilterUsageSensor(BlueairEntity, SensorEntity):
    """Monitors the status of the Filter"""

    def __init__(self, name, device):
        """Initialize the filter_status sensor."""
        super().__init__("filter_usage", name, device)
        self._state: str = None
        self._attr_icon = "mdi:air-filter"

    @property
    def native_value(self) -> float:
        """Return the current filter_status."""
        if self._device.filter_usage is None:
            return None
        return str(self._device.filter_usage)
