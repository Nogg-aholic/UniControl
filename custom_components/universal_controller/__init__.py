"""Universal Controller integration setup."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN, PLATFORMS

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up Universal Controller integration."""
    _LOGGER.info("Setting up Universal Controller integration")
    
    # Register frontend resources will be handled by HACS automatically
    # for custom cards in the www/ directory
    
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Universal Controller from a config entry."""
    _LOGGER.info("Setting up Universal Controller entry: %s", entry.entry_id)
    
    # Initialize domain data
    hass.data.setdefault(DOMAIN, {"entities": []})
    
    # Register services
    await _async_setup_services(hass)
    
    # Forward setup to platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload Universal Controller config entry."""
    _LOGGER.info("Unloading Universal Controller entry: %s", entry.entry_id)
    
    # Unload platforms
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    
    return unload_ok


async def _async_setup_services(hass: HomeAssistant) -> None:
    """Set up Universal Controller services."""
    
    async def create_entity_service(call: ServiceCall) -> None:
        """Handle create_entity service call."""
        name = call.data.get("name")
        if not name:
            _LOGGER.error("name is required for create_entity service")
            return
            
        # Create a new config entry for the entity
        from homeassistant.config_entries import ConfigEntryState
        
        # Check if we already have this name
        existing_entries = [
            entry for entry in hass.config_entries.async_entries(DOMAIN)
            if entry.data.get("name") == name
        ]
        
        if existing_entries:
            _LOGGER.error("Entity with name %s already exists", name)
            return
            
        # Create the config entry
        config_data = {
            "name": name,
            "interval": call.data.get("interval", 30),
        }
        
        # If HTML/CSS/TypeScript provided, we'll store them via services after creation
        try:
            result = await hass.config_entries.flow.async_init(
                DOMAIN,
                context={"source": "service"},
                data=config_data
            )
            
            if result["type"] == "create_entry":
                entry_id = result["result"].entry_id
                _LOGGER.info("Created entity %s with entry_id %s", name, entry_id)
                
                # If initial configuration provided, update it
                if any(key in call.data for key in ["html_template", "css_styles", "typescript_code"]):
                    # Find the created entity and update it
                    await hass.async_create_task(_update_entity_after_creation(
                        hass, entry_id, call.data
                    ))
                    
        except Exception as err:
            _LOGGER.error("Failed to create entity %s: %s", name, err)
    
    async def _update_entity_after_creation(hass: HomeAssistant, entry_id: str, data: dict) -> None:
        """Update entity configuration after creation."""
        import asyncio
        # Wait a bit for entity to be fully set up
        await asyncio.sleep(1)
        
        # Find the entity and update it
        for entity_obj in hass.data[DOMAIN].get("entities", []):
            if entity_obj._unique_id == entry_id:
                await entity_obj.update_configuration(
                    html_template=data.get("html_template"),
                    css_styles=data.get("css_styles"),
                    typescript_code=data.get("typescript_code"),
                )
                break
    
    async def update_entity_service(call: ServiceCall) -> None:
        """Handle update_entity service call."""
        entity_id = call.data.get("entity_id")
        if not entity_id:
            _LOGGER.error("entity_id is required for update_entity service")
            return
            
        # Get the entity
        entity = hass.states.get(entity_id)
        if not entity:
            _LOGGER.error("Entity %s not found", entity_id)
            return
            
        # Find the actual entity object
        for entity_obj in hass.data[DOMAIN].get("entities", []):
            if entity_obj.entity_id == entity_id:
                await entity_obj.update_configuration(
                    html_template=call.data.get("html_template"),
                    css_styles=call.data.get("css_styles"),
                    typescript_code=call.data.get("typescript_code"),
                    interval=call.data.get("interval"),
                )
                break
        else:
            _LOGGER.error("Universal Controller entity %s not found", entity_id)
    
    async def execute_now_service(call: ServiceCall) -> None:
        """Handle execute_now service call."""
        entity_id = call.data.get("entity_id")
        if not entity_id:
            _LOGGER.error("entity_id is required for execute_now service")
            return
            
        # Find and execute the entity
        for entity_obj in hass.data[DOMAIN].get("entities", []):
            if entity_obj.entity_id == entity_id:
                await entity_obj._execute_typescript()
                break
        else:
            _LOGGER.error("Universal Controller entity %s not found", entity_id)
    
    # Register services
    hass.services.async_register(DOMAIN, "create_entity", create_entity_service)
    hass.services.async_register(DOMAIN, "update_entity", update_entity_service)
    hass.services.async_register(DOMAIN, "execute_now", execute_now_service)
