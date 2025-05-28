from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from .const import DOMAIN, ATTR_MAP, LOGGER, CONF_USER_CODE

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    user_code = entry.data[CONF_USER_CODE]
    
    entities = [
        BalanceSensor(coordinator, user_code),
        MonthlyUsageSensor(coordinator, user_code),
        YearlyUsageSensor(coordinator, user_code)
    ]
    async_add_entities(entities)

async def async_update_data(hass, user_code):
    headers = {  "Content-Type": "application/json;charset=UTF-8",
    "Accept": "*/*",
    "Accept-Language": "zh-CN,zh-Hans;q=0.9",
    "Accept-Encoding": "gzip, deflate",
    "Origin": "http://wsyy.whwater.com:8223",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.4 Safari/605.1.15",
    "Content-Length": "43",
    "Connection": "keep-alive",
    "X-Requested-With": "XMLHttpRequest",
    "Priority": "u=3, i"
  }
    
    session = async_get_clientsession(hass)
    try:
        async with session.post(
            API_URL,
            headers=headers,
            json={"userCode": user_code, "source": "ONLINE"},
            timeout=REQUEST_TIMEOUT
        ) as resp:
            resp.raise_for_status()
            return await resp.json()
    except Exception as e:
        LOGGER.error("Update failed: %s", e)
        return None

class WaterBaseSensor(CoordinatorEntity, SensorEntity):
    _attr_has_entity_name = True
    
    def __init__(self, coordinator, user_code):
        super().__init__(coordinator)
        self._user_code = user_code
        self._attr_device_info = {
            "identifiers": {(DOMAIN, user_code)},
            "name": f"水费账户 {user_code}",
            "manufacturer": "武汉水务"
        }

class BalanceSensor(WaterBaseSensor):
    _attr_name = "账户余额"
    _attr_unique_id = "balance"
    _attr_icon = "mdi:cash"
    _attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self):
        return self.coordinator.data.get("restMoney")

class MonthlyUsageSensor(WaterBaseSensor):
    _attr_name = "本月消耗"
    _attr_unique_id = "monthly_usage"
    _attr_icon = "mdi:water"
    _attr_state_class = SensorStateClass.TOTAL_INCREASING

    @property
    def native_value(self):
        records = self.coordinator.data.get("payMessageList", [])
        return records[0]["totalFee"] if records else 0

    @property
    def native_unit_of_measurement(self):
        return "元"

    @property
    def extra_state_attributes(self):
        if records := self.coordinator.data.get("payMessageList"):
            return {ATTR_MAP[k]: v for k, v in records[0].items() if k in ATTR_MAP}
        return {}

class YearlyUsageSensor(WaterBaseSensor):
    _attr_name = "年度消耗"
    _attr_unique_id = "yearly_usage"
    _attr_icon = "mdi:chart-bar"
    _attr_state_class = SensorStateClass.TOTAL

    @property
    def native_value(self):
        return sum(float(r["totalFee"]) for r in self.coordinator.data.get("payMessageList", []))

    @property
    def extra_state_attributes(self):
        return {
            "months": [
                {ATTR_MAP[k]: v for k, v in item.items() if k in ATTR_MAP}
                for item in self.coordinator.data.get("payMessageList", [])
            ]
        }
