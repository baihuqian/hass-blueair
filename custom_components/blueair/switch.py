from custom_components.blueair.device import BlueairDataUpdateCoordinator
from .const import DOMAIN
from .device import BlueairDataUpdateCoordinator
from .entity import BlueairEntity
from homeassistant.components.switch import SwitchEntity


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the Blueair switches from config entry."""
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
                    BlueAirChildLockSwitch(f"{device.device_name} Child Lock", device),
                    BlueAirNightModeSwitch(f"{device.device_name} Night Mode", device),
                    BlueAirAutoModeSwitch(f"{device.device_name} Auto Mode", device),
                    BlueAirPowerSwitch(f"{device.device_name} Power", device),
                ]
            )
            
    async_add_entities(entities)

class BlueAirChildLockSwitch(BlueairEntity, SwitchEntity):
    _attr_has_entity_name = True

    def __init__(self, name: str, device: BlueairDataUpdateCoordinator):
        super().__init__("child_lcok", name, device)

    @property
    def is_on(self):
        """If the switch is currently on or off."""
        return self._device.child_lock

    async def async_turn_on(self, **kwargs):
        """Turn the switch on."""
        await self._device.set_child_lock(True)

    async def async_turn_off(self, **kwargs):
        """Turn the switch off."""
        await self._device.set_child_lock(False)

class BlueAirNightModeSwitch(BlueairEntity, SwitchEntity):
    _attr_has_entity_name = True

    def __init__(self, name: str, device: BlueairDataUpdateCoordinator):
        super().__init__("night_mode", name, device)

    @property
    def is_on(self):
        """If the switch is currently on or off."""
        return self._device.night_mode

    async def async_turn_on(self, **kwargs):
        """Turn the switch on."""
        await self._device.set_night_mode(True)

    async def async_turn_off(self, **kwargs):
        """Turn the switch off."""
        await self._device.set_night_mode(False)

class BlueAirAutoModeSwitch(BlueairEntity, SwitchEntity):
    _attr_has_entity_name = True

    def __init__(self, name: str, device: BlueairDataUpdateCoordinator):
        super().__init__("auto_mode", name, device)

    @property
    def is_on(self):
        """If the switch is currently on or off."""
        return self._device.auto_mode

    async def async_turn_on(self, **kwargs):
        """Turn the switch on."""
        await self._device.set_auto_mode(True)

    async def async_turn_off(self, **kwargs):
        """Turn the switch off."""
        await self._device.set_auto_mode(False)

class BlueAirPowerSwitch(BlueairEntity, SwitchEntity):
    _attr_has_entity_name = True

    def __init__(self, name: str, device: BlueairDataUpdateCoordinator):
        super().__init__("power", name, device)

    @property
    def is_on(self):
        """If the switch is currently on or off."""
        return self._device.is_on

    async def async_turn_on(self, **kwargs):
        """Turn the switch on."""
        await self._device.set_on(True)

    async def async_turn_off(self, **kwargs):
        """Turn the switch off."""
        await self._device.set_on(False)
