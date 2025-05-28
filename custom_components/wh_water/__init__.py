from __future__ import annotations

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN, LOGGER, SCAN_INTERVAL, CONF_USER_CODE
from .sensor import async_update_data

async def async_setup(hass: HomeAssistant, config: dict):
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """设置配置条目"""
    user_code = entry.data[CONF_USER_CODE]
    
    # 创建协调器实例
    coordinator = DataUpdateCoordinator(
        hass,
        LOGGER,
        name=DOMAIN,
        update_method=lambda: async_update_data(hass, user_code),  # 修复：使用lambda传递参数
        update_interval=SCAN_INTERVAL,
    )
    
    # 首次刷新数据
    await coordinator.async_refresh()
    
    # 存储协调器实例
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator
    
    # 设置传感器平台
    await hass.config_entries.async_forward_entry_setup(entry, "sensor")
    
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """卸载配置条目"""
    await hass.config_entries.async_forward_entry_unload(entry, "sensor")
    hass.data[DOMAIN].pop(entry.entry_id)
    return True
