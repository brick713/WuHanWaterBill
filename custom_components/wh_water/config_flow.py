from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import voluptuous as vol
import json
import logging

from .const import DOMAIN, API_URL, CONF_USER_CODE, REQUEST_TIMEOUT, LOGGER

class WhWaterConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL
    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            try:
                if await self._test_connection(user_input[CONF_USER_CODE]) == "success":
                    return self.async_create_entry(
                        title=f"水费账户 {user_input[CONF_USER_CODE]}",
                        data=user_input
                    )
                errors["base"] = "connection_failed"
            except Exception as e:
                LOGGER.error("配置流程错误: %s", str(e))
                errors["base"] = "unknown_error"
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_USER_CODE, description="水务账户编码"): str
            }),
            description_placeholders={"note": "在武汉水务账单上查找10位用户编码"},
            errors=errors
        )
    async def _test_connection(self, user_code):
        try:
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
            session = async_get_clientsession(self.hass)
            async with session.post(
                API_URL,
                headers=headers,
                json={"userCode": user_code, "source": "ONLINE"},
                timeout=REQUEST_TIMEOUT
            ) as resp:
                # 处理HTTP错误码
                if resp.status != 200:
                    body = await resp.text()
                    LOGGER.error(f"HTTP错误 {resp.status}: {body}")
                    return "http_error"

                data = await resp.json()
                
                # 检查关键字段
                if "restMoney" not in data:
                    LOGGER.error("响应缺少关键字段: %s", data)
                    return "invalid_response"
                    
                return "success"
                
        except aiohttp.ClientError as e:
            LOGGER.error("连接错误: %s", str(e))
            return "connection_failed"
