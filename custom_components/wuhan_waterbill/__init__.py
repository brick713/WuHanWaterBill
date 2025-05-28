from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN, LOGGER, SCAN_INTERVAL
from .sensor import async_update_data

async def async_setup(hass: HomeAssistant, config: dict):
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    coordinator = DataUpdateCoordinator(
        hass,
        LOGGER,
        name=DOMAIN,
        update_method=async_update_data,
        update_interval=SCAN_INTERVAL,
        update_interval_supported=True,
    )
    
    await coordinator.async_config_entry_first_refresh()
    
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator
    
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "sensor")
    )
    
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    await hass.config_entries.async_forward_entry_unload(entry, "sensor")
    hass.data[DOMAIN].pop(entry.entry_id)
    return True
