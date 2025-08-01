"""TypeScript execution engine for Universal Controller."""
from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)


class TypeScriptExecutionEngine:
    """Engine for executing TypeScript/JavaScript code safely."""

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize the execution engine."""
        self.hass = hass
        self._timeout = 10  # seconds
        self._context = None

    async def execute(self, code: str) -> Any:
        """Execute TypeScript/JavaScript code and return the result."""
        if not code.strip():
            return None

        try:
            # Try to use py-mini-racer for real JavaScript execution
            result = await self._execute_with_v8(code)
            return result
        except ImportError:
            _LOGGER.warning("py-mini-racer not available, falling back to Python simulation")
            return await self._execute_with_python_fallback(code)
        except Exception as err:
            _LOGGER.error("JavaScript execution error: %s", err)
            raise RuntimeError(f"JavaScript execution failed: {err}")

    async def _execute_with_v8(self, code: str) -> Any:
        """Execute code using V8 JavaScript engine via py-mini-racer."""
        try:
            from py_mini_racer import MiniRacer
        except ImportError:
            raise ImportError("py-mini-racer not available")

        # Create V8 context
        ctx = MiniRacer()
        
        # Set up Home Assistant API in JavaScript context
        hass_api = self._create_hass_api()
        
        # Inject the API into JavaScript
        ctx.eval(f"""
            const hass = {json.dumps(hass_api, default=str)};
            const states = hass.states;
            const console = {{
                log: function(...args) {{ 
                    return '_LOG_:' + args.join(' '); 
                }},
                error: function(...args) {{ 
                    return '_ERROR_:' + args.join(' '); 
                }},
                warn: function(...args) {{ 
                    return '_WARN_:' + args.join(' '); 
                }}
            }};
        """)
        
        # Wrap user code in a function
        wrapped_code = f"""
        (function() {{
            try {{
                {code}
            }} catch (error) {{
                throw new Error('User code error: ' + error.message);
            }}
        }})();
        """
        
        # Execute with timeout
        result = await asyncio.wait_for(
            asyncio.get_event_loop().run_in_executor(
                None, lambda: ctx.eval(wrapped_code)
            ),
            timeout=self._timeout
        )
        
        return result

    async def _execute_with_python_fallback(self, code: str) -> Any:
        """Fallback Python execution for basic JavaScript-like code."""
        try:
            # Create execution context with Home Assistant access
            context = self._create_execution_context()
            
            # Simple JavaScript to Python conversions
            python_code = self._convert_basic_js_to_python(code)
            
            # Execute in restricted environment
            result = await asyncio.wait_for(
                asyncio.get_event_loop().run_in_executor(
                    None, lambda: eval(python_code, {"__builtins__": {}}, context)
                ),
                timeout=self._timeout
            )
            
            # Handle async results
            if asyncio.iscoroutine(result):
                result = await result
                
            return result
            
        except Exception as err:
            raise RuntimeError(f"Python fallback execution error: {err}")

    def _create_hass_api(self) -> dict[str, Any]:
        """Create Home Assistant API for JavaScript context."""
        # Convert states to simple dict format for JSON serialization
        states_dict = {}
        for entity_id, state in self.hass.states.async_all():
            states_dict[entity_id] = {
                "state": state.state,
                "attributes": dict(state.attributes),
                "entity_id": entity_id,
                "last_changed": state.last_changed.isoformat(),
                "last_updated": state.last_updated.isoformat(),
            }
        
        return {
            "states": states_dict,
            "config": {
                "latitude": self.hass.config.latitude,
                "longitude": self.hass.config.longitude,
                "elevation": self.hass.config.elevation,
                "unit_system": self.hass.config.units.name,
                "time_zone": str(self.hass.config.time_zone),
            }
        }

    def _create_execution_context(self) -> dict[str, Any]:
        """Create the execution context with Home Assistant APIs."""
        return {
            "hass": self.hass,
            "states": self.hass.states,
            "services": self._create_services_api(),
            "console": self._create_console_api(),
            "JSON": json,
            "Date": self._create_date_api(),
        }

    def _create_services_api(self) -> dict[str, Any]:
        """Create a services API for the execution context."""
        async def call_service(domain: str, service: str, service_data: dict | None = None):
            """Call a Home Assistant service."""
            return await self.hass.services.async_call(
                domain, service, service_data or {}
            )
        
        return {
            "call": call_service,
        }

    def _create_console_api(self) -> dict[str, Any]:
        """Create a console API for logging."""
        return {
            "log": lambda *args: _LOGGER.info("User code: %s", " ".join(str(arg) for arg in args)),
            "error": lambda *args: _LOGGER.error("User code: %s", " ".join(str(arg) for arg in args)),
            "warn": lambda *args: _LOGGER.warning("User code: %s", " ".join(str(arg) for arg in args)),
        }

    def _create_date_api(self) -> dict[str, Any]:
        """Create a Date API."""
        from datetime import datetime
        return {
            "now": lambda: datetime.now().isoformat(),
            "utcnow": lambda: datetime.utcnow().isoformat(),
        }

    def _convert_basic_js_to_python(self, js_code: str) -> str:
        """Convert basic JavaScript syntax to Python (simplified)."""
        python_code = js_code
        
        # Basic conversions for common JavaScript patterns
        replacements = [
            ("new Date()", "Date['now']()"),
            ("console.log", "console['log']"),
            ("console.error", "console['error']"),
            ("console.warn", "console['warn']"),
            ("const ", ""),
            ("let ", ""),
            ("var ", ""),
            ("===", "=="),
            ("!==", "!="),
            ("true", "True"),
            ("false", "False"),
            ("null", "None"),
        ]
        
        for js_pattern, py_pattern in replacements:
            python_code = python_code.replace(js_pattern, py_pattern)
        
        # Handle return statements in simple cases
        if "return " in python_code and not python_code.strip().startswith("def "):
            lines = python_code.split("\n")
            for i, line in enumerate(lines):
                if "return " in line and not line.strip().startswith("#"):
                    return_value = line.split("return ")[1].strip()
                    return return_value.rstrip(";")
        
        return python_code
