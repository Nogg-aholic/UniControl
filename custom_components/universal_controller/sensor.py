"""Universal Controller sensor platform."""
from __future__ import annotations

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import dt as dt_util

from .const import (
    DOMAIN,
    ATTR_HTML_TEMPLATE,
    ATTR_CSS_STYLES,
    ATTR_TYPESCRIPT_CODE,
    ATTR_INTERVAL,
    ATTR_LAST_EXECUTION,
    ATTR_EXECUTION_COUNT,
    ATTR_LAST_ERROR,
    DEFAULT_INTERVAL,
)
from .execution_engine import TypeScriptExecutionEngine
from .storage import UniversalControllerStorage
from .template_renderer import TemplateRenderer

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Universal Controller sensor."""
    # Get the ticker manager and storage from the domain data
    domain_data = hass.data.get(DOMAIN, {})
    entry_data = domain_data.get(config_entry.entry_id)
    
    if not entry_data:
        _LOGGER.error("No data found for entry %s", config_entry.entry_id)
        return
        
    ticker_manager = entry_data["ticker_manager"]
    storage = entry_data["storage"]
    
    name = config_entry.data.get("name", "Universal Controller")
    interval = config_entry.data.get("interval", DEFAULT_INTERVAL)
    
    entity = UniversalControllerEntity(
        hass=hass,
        name=name,
        interval=interval,
        unique_id=config_entry.entry_id,
        ticker_manager=ticker_manager,
        storage=storage,
    )
    
    # Store entity reference for services
    hass.data[DOMAIN].setdefault("entities", []).append(entity)
    
    async_add_entities([entity], True)


class UniversalControllerEntity(SensorEntity):
    """Universal Controller entity that executes TypeScript code."""

    def __init__(
        self,
        hass: HomeAssistant,
        name: str,
        interval: int,
        unique_id: str,
        ticker_manager,
        storage,
    ) -> None:
        """Initialize the Universal Controller entity."""
        self.hass = hass
        self._name = name
        self._interval = interval
        self._unique_id = unique_id
        self._ticker_manager = ticker_manager
        self._storage = storage
        
        # Code storage
        self._html_template = "<div>Hello from Universal Controller!</div>"
        self._css_styles = "div { padding: 16px; background: #f0f0f0; }"
        self._typescript_code = "return { message: 'Hello World', timestamp: new Date() };"
        
        # Execution tracking
        self._last_execution: datetime | None = None
        self._execution_count = 0
        self._last_error: str | None = None
        self._state = "idle"
        self._execution_result = None
        
        # Execution engine and template renderer
        self._execution_engine = TypeScriptExecutionEngine(hass)
        self._template_renderer = TemplateRenderer(hass)

    @property
    def name(self) -> str:
        """Return the name of the entity."""
        return self._name

    @property
    def unique_id(self) -> str:
        """Return the unique ID of the entity."""
        return self._unique_id

    @property
    def state(self) -> str:
        """Return the state of the entity."""
        return self._state

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return entity specific state attributes."""
        attrs = {
            ATTR_HTML_TEMPLATE: self._html_template,
            ATTR_CSS_STYLES: self._css_styles,
            ATTR_TYPESCRIPT_CODE: self._typescript_code,
            ATTR_INTERVAL: self._interval,
            ATTR_LAST_EXECUTION: self._last_execution.isoformat() if self._last_execution else None,
            ATTR_EXECUTION_COUNT: self._execution_count,
            ATTR_LAST_ERROR: self._last_error,
            "execution_result": self._execution_result,
        }
        
        # Add ticker information
        ticker_info = self._ticker_manager.get_ticker_info(self._unique_id)
        if ticker_info:
            attrs.update({
                "ticker_running": ticker_info["is_running"],
                "ticker_execution_count": ticker_info["execution_count"],
                "ticker_error_count": ticker_info["error_count"],
                "ticker_next_execution": ticker_info["next_execution"],
            })
        
        return attrs

    async def async_added_to_hass(self) -> None:
        """When entity is added to hass."""
        await super().async_added_to_hass()
        
        # Register with ticker manager
        self._ticker_manager.register_entity(self._unique_id, self)
        
        # Load saved configuration
        await self._load_configuration()
        
        # Start ticker if interval is set
        if self._interval > 0:
            self._ticker_manager.start_ticker(self._unique_id, self._interval)

    async def async_will_remove_from_hass(self) -> None:
        """When entity will be removed from hass."""
        # Unregister from ticker manager
        self._ticker_manager.unregister_entity(self._unique_id)
        
        await super().async_will_remove_from_hass()

    async def _execute_typescript(self) -> None:
        """Execute the TypeScript code."""
        if not self._typescript_code.strip():
            return

        try:
            self._state = "executing"
            self._last_execution = dt_util.utcnow()
            self._execution_count += 1
            self._last_error = None
            
            # Execute the code
            result = await self._execution_engine.execute(self._typescript_code)
            self._execution_result = result
            
            # Update state based on result
            if isinstance(result, dict):
                self._state = json.dumps(result, default=str)
            else:
                self._state = str(result)
                
        except Exception as err:
            _LOGGER.error("TypeScript execution error: %s", err)
            self._last_error = str(err)
            self._state = "error"
            self._execution_result = None
        
        # Schedule update
        self.async_write_ha_state()

    async def update_configuration(
        self,
        html_template: str | None = None,
        css_styles: str | None = None,
        typescript_code: str | None = None,
        interval: int | None = None,
    ) -> None:
        """Update the entity configuration."""
        updated = False
        
        if html_template is not None and html_template != self._html_template:
            self._html_template = html_template
            updated = True
        if css_styles is not None and css_styles != self._css_styles:
            self._css_styles = css_styles
            updated = True
        if typescript_code is not None and typescript_code != self._typescript_code:
            self._typescript_code = typescript_code
            updated = True
        if interval is not None and interval != self._interval:
            old_interval = self._interval
            self._interval = max(1, min(3600, interval))
            updated = True
            
            # Restart ticker with new interval
            if self._interval > 0:
                self._ticker_manager.restart_ticker(self._unique_id, self._interval)
            else:
                self._ticker_manager.stop_ticker(self._unique_id)
            
            _LOGGER.info(
                "Updated ticker interval for %s from %s to %s seconds",
                self._unique_id,
                old_interval,
                self._interval
            )
        
        if updated:
            self.async_write_ha_state()
            _LOGGER.info("Updated configuration for %s", self._name)
            
            # Save to persistent storage
            await self._save_configuration()

    async def _load_configuration(self) -> None:
        """Load configuration from storage."""
        try:
            config = await self._storage.async_load_entity_config(self.entity_id)
            if config:
                self._html_template = config.get("html_template", self._html_template)
                self._css_styles = config.get("css_styles", self._css_styles)
                self._typescript_code = config.get("typescript_code", self._typescript_code)
                self._interval = config.get("interval", self._interval)
                _LOGGER.info("Loaded configuration for %s", self._name)
        except Exception as err:
            _LOGGER.error("Failed to load configuration for %s: %s", self._name, err)

    async def _save_configuration(self) -> None:
        """Save configuration to storage."""
        try:
            await self._storage.async_save_entity_config(
                self.entity_id,
                self._html_template,
                self._css_styles,
                self._typescript_code,
                self._interval,
            )
        except Exception as err:
            _LOGGER.error("Failed to save configuration for %s: %s", self._name, err)

    def get_rendered_html(self) -> str:
        """Get rendered HTML using the template engine."""
        try:
            # Create context for template rendering
            entity_state = self.hass.states.get(self.entity_id)
            if not entity_state:
                return "<div>Entity state not available</div>"
            
            context = self._template_renderer.create_context(entity_state, self._execution_result)
            
            # Render the HTML template
            return self._template_renderer.render_html(self._html_template, context)
            
        except Exception as err:
            _LOGGER.error("Template rendering error: %s", err)
            return f"<div class='error'>Template error: {err}</div>"
