"""Storage management for Universal Controller."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store

from .const import DOMAIN, STORAGE_VERSION, STORAGE_KEY

_LOGGER = logging.getLogger(__name__)


class UniversalControllerStorage:
    """Handle storage for Universal Controller entities."""

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize storage."""
        self.hass = hass
        self._store = Store(hass, STORAGE_VERSION, STORAGE_KEY)
        self._data: dict[str, Any] = {}

    async def async_load(self) -> dict[str, Any]:
        """Load data from storage."""
        if not self._data:
            stored_data = await self._store.async_load()
            self._data = stored_data or {}
        return self._data

    async def async_save(self) -> None:
        """Save data to storage."""
        await self._store.async_save(self._data)

    async def async_save_entity_config(
        self,
        entity_id: str,
        html_template: str,
        css_styles: str,
        typescript_code: str,
        interval: int,
    ) -> None:
        """Save entity configuration."""
        await self.async_load()
        self._data[entity_id] = {
            "html_template": html_template,
            "css_styles": css_styles,
            "typescript_code": typescript_code,
            "interval": interval,
        }
        await self.async_save()
        _LOGGER.info("Saved configuration for entity %s", entity_id)

    async def async_load_entity_config(self, entity_id: str) -> dict[str, Any] | None:
        """Load entity configuration."""
        await self.async_load()
        return self._data.get(entity_id)

    async def async_remove_entity_config(self, entity_id: str) -> None:
        """Remove entity configuration."""
        await self.async_load()
        self._data.pop(entity_id, None)
        await self.async_save()
        _LOGGER.info("Removed configuration for entity %s", entity_id)
