from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import voluptuous as vol
import json

from .const import DOMAIN, API_URL, CONF_USER_CODE, REQUEST_TIMEOUT, LOGGER

class WhWaterConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input:
            valid = await self._test_connection(user_input[CONF_USER_CODE])
            if valid:
                return self.async_create_entry(
                    title=f"水费账户 {user_input[CONF_USER_CODE]}",
                    data=user_input
                )
            errors["base"] = "invalid_auth"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_USER_CODE): str
            }),
            errors=errors
        )

    async def _test_connection(self, user_code):
        try:
            session = async_get_clientsession(self.hass)
            async with session.post(
                API_URL,
                json={"userCode": user_code, "source": "ONLINE"},
                timeout=REQUEST_TIMEOUT
            ) as resp:
                if resp.status != 200:
                    return False
                data = await resp.json()
                return "restMoney" in data
        except Exception as e:
            LOGGER.error("Connection test failed: %s", e)
            return False
