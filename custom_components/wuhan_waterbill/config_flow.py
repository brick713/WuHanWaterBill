"""Config flow for Wuhan Water integration."""
from __future__ import annotations

import logging
from typing import Any

import requests
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .const import API_URL, CONF_USER_CODE, DOMAIN, LOGGER

DATA_SCHEMA = vol.Schema({vol.Required(CONF_USER_CODE): str})

async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input."""
    try:
        response = await hass.async_add_executor_job(
            requests.post,
            API_URL,
            {"userCode": data[CONF_USER_CODE], "source": "ONLINE"},
            {"timeout": 10}
        )
        result = response.json()
        
        if "restMoney" not in result:
            raise InvalidAccount
        
        return {
            "title": f"水费账户 {data[CONF_USER_CODE]}",
            "data": data
        }
    except requests.exceptions.RequestException as err:
        LOGGER.error("Error connecting to API: %s", err)
        raise CannotConnect from err

class WhWaterConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Wuhan Water."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
                return self.async_create_entry(title=info["title"], data=user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAccount:
                errors["base"] = "invalid_account"
            except Exception:  # pylint: disable=broad-except
                LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=DATA_SCHEMA,
            errors=errors,
        )

class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""

class InvalidAccount(HomeAssistantError):
    """Error to indicate there is an invalid account."""
