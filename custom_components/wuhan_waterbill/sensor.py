"""Sensor platform for Wuhan Water."""
from __future__ import annotations

from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CURRENCY_YUAN
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .const import (
    ATTR_DRAIN_FEE,
    ATTR_LATEST_MONTH,
    ATTR_REST_MONEY,
    ATTR_TOTAL_FEE,
    ATTR_USE_WATER,
    ATTR_WATER_FEE,
    DOMAIN,
    LOGGER,
)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities([
        WhWaterBalanceSensor(coordinator, entry),
        WhWaterUsageSensor(coordinator, entry)
    ])

class WhWaterSensor(CoordinatorEntity):
    """Representation of a Wuhan Water sensor."""

    def __init__(self, coordinator, config_entry):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._config_entry = config_entry
        self._attr_device_info = {
            "identifiers": {(DOMAIN, self._config_entry.entry_id)},
            "name": f"水费账户 {self._config_entry.data[CONF_USER_CODE]}",
            "manufacturer": "武汉市水务集团"
        }

class WhWaterBalanceSensor(WhWaterSensor, SensorEntity):
    """Representation of water balance."""

    _attr_name = "Water Balance"
    _attr_native_unit_of_measurement = CURRENCY_YUAN
    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:cash"

    @property
    def unique_id(self):
        """Return a unique ID."""
        return f"{self._config_entry.entry_id}_balance"

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self.coordinator.data.get("balance")

class WhWaterUsageSensor(WhWaterSensor, SensorEntity):
    """Representation of water usage."""

    _attr_name = "Water Usage"
    _attr_native_unit_of_measurement = CURRENCY_YUAN
    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_icon = "mdi:water"

    @property
    def unique_id(self):
        """Return a unique ID."""
        return f"{self._config_entry.entry_id}_usage"

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self.coordinator.data.get("usage")

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return self.coordinator.data.get("attributes")
