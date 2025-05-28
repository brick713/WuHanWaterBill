from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from .const import DOMAIN, ATTR_MAP, LOGGER, API_URL, REQUEST_TIMEOUT
import aiohttp
import logging

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    """设置传感器实体"""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    user_code = entry.data["user_code"]
    
    # 创建三个传感器实体
    entities = [
        BalanceSensor(coordinator, user_code),
        MonthlyUsageSensor(coordinator, user_code),
        YearlyUsageSensor(coordinator, user_code)
    ]
    async_add_entities(entities)

async def async_update_data(hass, user_code):
    """获取并处理水费数据"""
    session = async_get_clientsession(hass)
    
    # 设置完整的请求头
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
    
    try:
        # 发送API请求
        async with session.post(
            API_URL,
            headers=headers,
            json={"userCode": user_code, "source": "ONLINE"},
            timeout=REQUEST_TIMEOUT
        ) as resp:
            # 处理403错误
            if resp.status == 403:
                _LOGGER.warning("API访问被拒绝，尝试添加安全令牌...")
                # 获取CSRF令牌
                token = await get_csrf_token(session)
                headers["X-CSRF-Token"] = token
                
                # 使用令牌重试
                async with session.post(
                    API_URL,
                    headers=headers,
                    json={"userCode": user_code, "source": "ONLINE"},
                    timeout=REQUEST_TIMEOUT
                ) as retry_resp:
                    retry_resp.raise_for_status()
                    return await retry_resp.json()
            
            # 处理其他状态码
            resp.raise_for_status()
            return await resp.json()
            
    except aiohttp.ClientError as e:
        _LOGGER.error("网络请求错误: %s", e)
        return None
    except Exception as e:
        _LOGGER.error("数据处理错误: %s", e)
        return None

async def get_csrf_token(session):
    """获取CSRF安全令牌"""
    token_url = "http://wsyy.whwater.com:8223/csrf-token"
    try:
        async with session.get(token_url) as resp:
            resp.raise_for_status()
            return (await resp.json()).get("token", "default-token")
    except Exception as e:
        _LOGGER.error("获取CSRF令牌失败: %s", e)
        return "fallback-token"

class WaterBaseSensor(CoordinatorEntity, SensorEntity):
    """所有水费传感器的基类"""
    
    def __init__(self, coordinator, user_code):
        super().__init__(coordinator)
        self._user_code = user_code
        self._attr_device_info = {
            "identifiers": {(DOMAIN, user_code)},
            "name": f"水费账户 {user_code}",
            "manufacturer": "武汉水务"
        }
        self._attr_has_entity_name = True

class BalanceSensor(WaterBaseSensor):
    """账户余额传感器"""
    
    _attr_name = "账户余额"
    _attr_unique_id = "balance"
    _attr_icon = "mdi:cash"
    _attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self):
        data = self.coordinator.data
        return float(data.get("restMoney", 0)) if data else 0

    @property
    def native_unit_of_measurement(self):
        return "元"

    @property
    def extra_state_attributes(self):
        data = self.coordinator.data
        if not data or "customer" not in data:
            return {}
        
        customer = data["customer"]
        return {
            "户名": customer.get("customerName", ""),
            "地址": customer.get("address", ""),
            "水表号": customer.get("waterMeterNO", ""),
            "缴费方式": customer.get("paymentMode", "")
        }

class MonthlyUsageSensor(WaterBaseSensor):
    """本月消耗传感器"""
    
    _attr_name = "本月消耗"
    _attr_unique_id = "monthly_usage"
    _attr_icon = "mdi:water"
    _attr_state_class = SensorStateClass.TOTAL_INCREASING

    @property
    def native_value(self):
        data = self.coordinator.data
        if not data or "payMessageList" not in data or not data["payMessageList"]:
            return 0
            
        records = data["payMessageList"]
        return float(records[0]["totalFee"]) if records else 0

    @property
    def native_unit_of_measurement(self):
        return "元"

    @property
    def extra_state_attributes(self):
        data = self.coordinator.data
        if not data or "payMessageList" not in data or not data["payMessageList"]:
            return {}
            
        record = data["payMessageList"][0]
        return {
            ATTR_MAP[k]: v for k, v in record.items() 
            if k in ATTR_MAP and v is not None
        }

class YearlyUsageSensor(WaterBaseSensor):
    """年度消耗传感器"""
    
    _attr_name = "年度消耗"
    _attr_unique_id = "yearly_usage"
    _attr_icon = "mdi:chart-bar"
    _attr_state_class = SensorStateClass.TOTAL

    @property
    def native_value(self):
        data = self.coordinator.data
        if not data or "payMessageList" not in data or not data["payMessageList"]:
            return 0
            
        try:
            return sum(float(r["totalFee"]) for r in data["payMessageList"])
        except (TypeError, ValueError):
            return 0

    @property
    def native_unit_of_measurement(self):
        return "元"

    @property
    def extra_state_attributes(self):
        data = self.coordinator.data
        if not data or "payMessageList" not in data:
            return {}
            
        return {
            "months": [
                {
                    "月份": item["payMonth"],
                    "用水量(吨)": item["useWater"],
                    "总费用(元)": item["totalFee"],
                    "基础水费(元)": item["waterFee"],
                    "排水费(元)": item["drainFee"]
                }
                for item in data["payMessageList"]
            ]
        }
