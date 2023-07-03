"""Blueair device object."""
import asyncio
from datetime import datetime, timedelta
from typing import Any
from async_timeout import timeout


from . import blueair

API = blueair.BlueAirAws

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
import homeassistant.util.dt as dt_util

from .const import DOMAIN, LOGGER


class BlueairDataUpdateCoordinator(DataUpdateCoordinator):
    """Blueair device object."""

    def __init__(
        self, hass: HomeAssistant, api_client: API, uuid: str, device_name: str
    ) -> None:
        """Initialize the device."""
        self.hass: HomeAssistant = hass
        self.api_client: API = api_client
        self._uuid: str = uuid
        self._name: str = device_name
        self._manufacturer: str = "BlueAir"
        self._device_information: dict[str, Any] = {}
        self._datapoint: dict[str, Any] = {}
        self._attribute: dict[str, Any] = {}

        super().__init__(
            hass,
            LOGGER,
            name=f"{DOMAIN}-{device_name}",
            update_interval=timedelta(seconds=60),
        )

    async def _async_update_data(self):
        """Update data via library."""
        try:
            async with timeout(10):
                await asyncio.gather(*[self._update_device()])
        except Exception as error:
            raise UpdateFailed(error) from error

    @property
    def id(self) -> str:
        """Return Blueair device id."""
        return self._uuid

    @property
    def device_name(self) -> str:
        """Return device name."""
        return self._device_information.get("name", f"{self.name}")

    @property
    def manufacturer(self) -> str:
        """Return manufacturer for device."""
        return self._manufacturer

    @property
    def model(self) -> str:
        """Return model for device, or the UUID if it's not known."""
        if 'hw' in self._device_information:
            hw = self._device_information['hw']
            match hw:
                case "nb_m_1.0":
                    return "Blue Pure 311i Max"
                case _:
                    return "BlueAir Wi-Fi Enabled Purifier"
        else: 
            return self.id

    @property
    def pm25(self) -> float:
        """Return the current pm2.5."""
        if "pm2_5" not in self._datapoint:
            return None
        return self._datapoint["pm2_5"]
    
    @property
    def filter_usage(self) -> int:
        if "filterusage" not in self._attribute:
            return None
        return int(self._attribute["filterusage"])

    @property
    def brightness(self) -> int:
        if "brightness" not in self._attribute:
            return None
        return int(self._attribute["brightness"])
    
    @property
    def fan_speed(self) -> int:
        """Return the current fan speed."""
        if "fanspeed" not in self._attribute:
            return None
        return int(self._attribute["fanspeed"])

    @property
    def is_on(self) -> bool():
        """Return the current fan state."""
        if "standby" not in self._attribute:
            return None
        return not self._attribute["standby"]

    @property
    def night_mode(self) -> bool:
        """Return the current fan mode"""
        if "nightmode" not in self._attribute:
            return None
        return self._attribute["nightmode"]

    @property
    def child_lock(self) -> bool:
        """Return the current fan mode"""
        if "childlock" not in self._attribute:
            return None
        return self._attribute["childlock"]

    @property
    def auto_mode(self) -> bool:
        """Return the current fan mode"""
        if "automode" not in self._attribute:
            return None
        return self._attribute["automode"]

    async def set_fan_speed(self, new_speed) -> None:
        await self.hass.async_add_executor_job(
            lambda: self.api_client.send_command(self._uuid, 'fanspeed', new_speed)
        )
        self._attribute["fan_speed"] = new_speed
        await self.async_refresh()

    async def set_brightness(self, new_brightness) -> None:
        await self.hass.async_add_executor_job(
            lambda: self.api_client.send_command(self._uuid, 'brightness', new_brightness)
        )
        self._attribute["brightness"] = new_brightness
        await self.async_refresh()

    async def set_auto_mode(self, new_auto_mode: bool) -> None:
        await self.hass.async_add_executor_job(
            lambda: self.api_client.send_command(self._uuid, 'automode', new_auto_mode)
        )
        self._attribute["automode"] = new_auto_mode
        await self.async_refresh()

    async def set_night_mode(self, new_night_mode: bool) -> None:
        await self.hass.async_add_executor_job(
            lambda: self.api_client.send_command(self._uuid, 'nightmode', new_night_mode)
        )
        self._attribute["nightmode"] = new_night_mode
        await self.async_refresh()

    async def set_child_lock(self, new_child_lock: bool) -> None:
        await self.hass.async_add_executor_job(
            lambda: self.api_client.send_command(self._uuid, 'childlock', new_child_lock)
        )
        self._attribute["childlock"] = new_child_lock
        await self.async_refresh()
    
    async def set_on(self, on: bool) -> None:
        standby = not on
        await self.hass.async_add_executor_job(
            lambda: self.api_client.send_command(self._uuid, 'standby', standby)
        )
        self._attribute["standby"] = standby
        await self.async_refresh()

    async def _update_device(self, *_) -> None:
        """Update the device information from the API."""
        LOGGER.info(self._name)

        info = await self.hass.async_add_executor_job(
            lambda: self.api_client.get_info(self._name, self._uuid)
        )
        LOGGER.info(f"_device_info: {info}")

        self._device_information = info['configuration']['di']
        LOGGER.info(f"_device_information: {self._device_information}")
        
        self._datapoint = {sd['n']: sd['v'] for sd in info['sensorData']}
        LOGGER.info(f"_datapoint: {self._datapoint}")

        self._attribute = {state['n']: state['v'] for state in info['states']}
        LOGGER.info(f"_attribute: {self._attribute}")
