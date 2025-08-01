"""Frontend for Universal Controller integration."""
from __future__ import annotations

import logging
from pathlib import Path

from homeassistant.components import frontend
from homeassistant.components.http import StaticPathConfig
from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)

FRONTEND_URL_PATH = "/universal_controller_frontend"
FRONTEND_FILE_PATH = "universal-controller-card.js"
FRONTEND_EDITOR_PATH = "universal-controller-card-editor.js"
FRONTEND_MONACO_PATH = "universal-controller-monaco-editor.js"
FRONTEND_TYPES_PATH = "types/homeassistant.d.ts"


async def async_register_frontend(hass: HomeAssistant) -> None:
    """Register the frontend components."""
    try:
        _LOGGER.info("🚀 STARTING ENHANCED FRONTEND REGISTRATION")
        
        # Get the path to our www directory
        integration_dir = Path(__file__).parent
        www_dir = integration_dir / "www"
        
        _LOGGER.info(f"📁 Integration dir: {integration_dir}")
        _LOGGER.info(f"📁 WWW dir: {www_dir}")
        _LOGGER.info(f"📁 WWW dir exists: {www_dir.exists()}")
        
        if www_dir.exists():
            # Check for all frontend files
            card_file = www_dir / FRONTEND_FILE_PATH
            editor_file = www_dir / FRONTEND_EDITOR_PATH
            monaco_file = www_dir / FRONTEND_MONACO_PATH
            types_file = www_dir / FRONTEND_TYPES_PATH
            
            _LOGGER.info(f"📄 Card file: {card_file} (exists: {card_file.exists()})")
            _LOGGER.info(f"📄 Editor file: {editor_file} (exists: {editor_file.exists()})")
            _LOGGER.info(f"📄 Monaco file: {monaco_file} (exists: {monaco_file.exists()})")
            _LOGGER.info(f"📄 Types file: {types_file} (exists: {types_file.exists()})")
            
            if card_file.exists():
                # Register the static files using the correct async method
                _LOGGER.info("🔧 Registering static paths for Universal Controller frontend")
                try:
                    await hass.http.async_register_static_paths([
                        StaticPathConfig(
                            url_path=FRONTEND_URL_PATH,
                            path=str(www_dir),
                            cache_headers=False
                        )
                    ])
                    _LOGGER.info(f"📁 Static path registered: {FRONTEND_URL_PATH} -> {www_dir}")
                except Exception as static_error:
                    _LOGGER.error(f"❌ Static path registration failed: {static_error}")
                    raise
                
                # Add all JS files to frontend
                try:
                    # Main card
                    frontend_url = f"{FRONTEND_URL_PATH}/{FRONTEND_FILE_PATH}"
                    frontend.add_extra_js_url(hass, frontend_url)
                    _LOGGER.info(f"🔗 Main card JS URL added: {frontend_url}")
                    
                    # Simple editor (if exists)
                    if editor_file.exists():
                        editor_url = f"{FRONTEND_URL_PATH}/{FRONTEND_EDITOR_PATH}"
                        frontend.add_extra_js_url(hass, editor_url)
                        _LOGGER.info(f"🔗 Simple editor JS URL added: {editor_url}")
                    
                    # Monaco editor (if exists)
                    if monaco_file.exists():
                        monaco_url = f"{FRONTEND_URL_PATH}/{FRONTEND_MONACO_PATH}"
                        frontend.add_extra_js_url(hass, monaco_url)
                        _LOGGER.info(f"🔗 Monaco editor JS URL added: {monaco_url}")
                        
                except Exception as js_error:
                    _LOGGER.error(f"❌ JS URL registration failed: {js_error}")
                    raise
                
                _LOGGER.info(f"✅ ENHANCED FRONTEND REGISTRATION COMPLETE")
                _LOGGER.info(f"🎯 CARD TYPE: 'custom:universal-controller-card'")
                _LOGGER.info(f"🎯 MONACO EDITOR: 'universal-controller-monaco-editor'")
                _LOGGER.info(f"🎯 TYPESCRIPT TYPES: Available at {FRONTEND_URL_PATH}/types/homeassistant.d.ts")
                _LOGGER.info(f"🔍 CHECK BROWSER CONSOLE FOR CARD LOGS")
            else:
                _LOGGER.error(f"❌ Card file not found: {card_file}")
        else:
            _LOGGER.error(f"❌ WWW directory not found: {www_dir}")
        
    except Exception as e:
        _LOGGER.error(f"❌ FRONTEND REGISTRATION FAILED: {e}")
        _LOGGER.error(f"🔥 Exception type: {type(e).__name__}")
        import traceback
        _LOGGER.error(f"🔥 Traceback: {traceback.format_exc()}")
        raise
