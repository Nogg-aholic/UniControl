"""Frontend for Universal Controller integration."""
from __future__ import annotations

import logging
from pathlib import Path

from homeassistant.components import frontend
from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)

FRONTEND_URL_PATH = "/universal_controller_frontend"
FRONTEND_FILE_PATH = "universal-controller-card.js"


async def async_register_frontend(hass: HomeAssistant) -> None:
    """Register the frontend components."""
    try:
        _LOGGER.info("🚀 STARTING FRONTEND REGISTRATION")
        
        # Get the path to our www directory
        integration_dir = Path(__file__).parent
        www_dir = integration_dir / "www"
        
        _LOGGER.info(f"📁 Integration dir: {integration_dir}")
        _LOGGER.info(f"📁 WWW dir: {www_dir}")
        _LOGGER.info(f"📁 WWW dir exists: {www_dir.exists()}")
        
        if www_dir.exists():
            card_file = www_dir / FRONTEND_FILE_PATH
            _LOGGER.info(f"📄 Card file: {card_file}")
            _LOGGER.info(f"📄 Card file exists: {card_file.exists()}")
            
            if card_file.exists():
                # Register the static files
                hass.http.register_static_path(
                    FRONTEND_URL_PATH, 
                    str(www_dir), 
                    cache_headers=False
                )
                _LOGGER.info(f"📁 Static path registered: {FRONTEND_URL_PATH} -> {www_dir}")
                
                # Add the JS file to frontend
                frontend_url = f"{FRONTEND_URL_PATH}/{FRONTEND_FILE_PATH}"
                frontend.add_extra_js_url(hass, frontend_url)
                _LOGGER.info(f"🔗 JS URL added to frontend: {frontend_url}")
                
                _LOGGER.info(f"✅ FRONTEND REGISTRATION COMPLETE")
                _LOGGER.info(f"🎯 CARD TYPE: 'custom:universal-controller-card'")
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
