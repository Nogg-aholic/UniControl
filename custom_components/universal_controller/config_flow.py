"""Config flow for Universal Controller integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN, DEFAULT_NAME, DEFAULT_INTERVAL

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required("name", default=DEFAULT_NAME): str,
        vol.Optional("interval", default=DEFAULT_INTERVAL): vol.All(
            vol.Coerce(int), vol.Range(min=1, max=3600)
        ),
    }
)


class UniversalControllerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Universal Controller."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                # Simple unique check based on name
                name = user_input["name"]
                
                # Check if already configured by searching existing entries
                for entry in self._async_current_entries():
                    if entry.data.get("name") == name:
                        return self.async_abort(reason="already_configured")
                
                return self.async_create_entry(
                    title=name,
                    data=user_input,
                )
            except Exception as exception:
                _LOGGER.exception("Unexpected exception: %s", exception)
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )
