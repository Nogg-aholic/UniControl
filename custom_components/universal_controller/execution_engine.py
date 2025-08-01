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
            # Try V8 JavaScript engine first
            try:
                _LOGGER.debug("Attempting V8 JavaScript execution")
                return await self._execute_with_v8(code)
            except ImportError:
                _LOGGER.warning("py-mini-racer not available, falling back to Python")
                return await self._execute_with_python_fallback(code)
        except Exception as err:
            _LOGGER.error("Code execution error: %s", err)
            raise RuntimeError(f"Code execution failed: {err}")

    async def _execute_with_v8(self, code: str) -> Any:
        """Execute code using V8 JavaScript engine via py-mini-racer."""
        try:
            from py_mini_racer import MiniRacer
        except ImportError:
            raise ImportError("py-mini-racer not available")

        # Create V8 context
        ctx = MiniRacer()
        
        # Create service call handler
        service_calls = {}
        service_call_counter = 0
        
        def handle_service_call(domain: str, service: str, data: dict = None):
            """Handle service calls from JavaScript."""
            nonlocal service_call_counter
            call_id = f"service_call_{service_call_counter}"
            service_call_counter += 1
            service_calls[call_id] = {
                "domain": domain,
                "service": service,
                "data": data or {}
            }
            return f"SERVICE_CALL_QUEUED:{call_id}"
        
        # Set up comprehensive Home Assistant and HACS API in JavaScript context
        hass_api = self._create_comprehensive_hass_api()
        
        # Inject the APIs into JavaScript with TypeScript-compatible declarations
        ctx.eval(f"""
            // Service call queue for async operations
            const _serviceCalls = {{}};
            
            // Service call handler
            function callService(domain, service, data = {{}}) {{
                const callId = 'call_' + Math.random().toString(36).substr(2, 9);
                _serviceCalls[callId] = {{ domain, service, data }};
                return callId;
            }}
            
            // Home Assistant API
            const hass = {json.dumps(hass_api, default=str)};
            hass.callService = callService;
            const states = hass.states;
            
            // Enhanced Console API
            const console = {{
                log: function(...args) {{ 
                    return '_LOG_:' + args.map(a => typeof a === 'object' ? JSON.stringify(a) : String(a)).join(' '); 
                }},
                error: function(...args) {{ 
                    return '_ERROR_:' + args.map(a => typeof a === 'object' ? JSON.stringify(a) : String(a)).join(' '); 
                }},
                warn: function(...args) {{ 
                    return '_WARN_:' + args.map(a => typeof a === 'object' ? JSON.stringify(a) : String(a)).join(' '); 
                }},
                info: function(...args) {{ 
                    return '_INFO_:' + args.map(a => typeof a === 'object' ? JSON.stringify(a) : String(a)).join(' '); 
                }},
                debug: function(...args) {{ 
                    return '_DEBUG_:' + args.map(a => typeof a === 'object' ? JSON.stringify(a) : String(a)).join(' '); 
                }}
            }};
            
            // Date utilities (don't override global Date)
            const DateUtils = {{
                now: () => Date.now(),
                utc: () => new Date().toISOString(),
                local: () => new Date().toLocaleString(),
                parse: (str) => new Date(str),
                format: (date, format) => new Date(date).toLocaleString()
            }};
            
            // Math utilities (extend existing Math, don't replace)
            const MathUtils = Object.assign({{}}, Math, {{
                clamp: (num, min, max) => Math.min(Math.max(num, min), max),
                randomRange: (min, max) => Math.random() * (max - min) + min,
                roundTo: (num, decimals) => Math.round(num * Math.pow(10, decimals)) / Math.pow(10, decimals)
            }});
            
            // HACS Integration API
            const HACS = {{
                // Repository management
                getRepositories: () => hass.hacs_repositories || [],
                getRepository: (name) => (hass.hacs_repositories || []).find(r => r.name === name),
                isInstalled: (name) => (hass.hacs_repositories || []).some(r => r.name === name && r.installed),
                
                // Installation management (returns call IDs for async processing)
                install: (name) => hass.callService('hacs', 'install', {{ repository: name }}),
                uninstall: (name) => hass.callService('hacs', 'uninstall', {{ repository: name }}),
                update: (name) => hass.callService('hacs', 'update', {{ repository: name }}),
                
                // Information
                getInfo: () => hass.hacs_info || {{}},
                getStatus: () => hass.hacs_status || {{}}
            }};
            
            // Enhanced Services API
            const services = {{
                call: (domain, service, data = {{}}) => {{
                    console.log('Calling service:', domain + '.' + service, data);
                    return hass.callService(domain, service, data);
                }},
                
                // Convenience methods for common services
                turnOn: (entityId, data = {{}}) => services.call('homeassistant', 'turn_on', {{ entity_id: entityId, ...data }}),
                turnOff: (entityId, data = {{}}) => services.call('homeassistant', 'turn_off', {{ entity_id: entityId, ...data }}),
                toggle: (entityId, data = {{}}) => services.call('homeassistant', 'toggle', {{ entity_id: entityId, ...data }}),
                
                // Notification services
                notify: (message, title = null, data = {{}}) => {{
                    const payload = {{ message, ...data }};
                    if (title) payload.title = title;
                    return services.call('notify', 'notify', payload);
                }},
                
                // Script and automation
                runScript: (scriptId, data = {{}}) => services.call('script', scriptId, data),
                triggerAutomation: (automationId) => services.call('automation', 'trigger', {{ entity_id: automationId }})
            }};
            
            // Utility functions
            const utils = {{
                // Entity helpers
                getEntity: (entityId) => states[entityId],
                getEntityState: (entityId) => states[entityId]?.state,
                getEntityAttribute: (entityId, attr) => states[entityId]?.attributes[attr],
                
                // Filtering helpers
                filterEntities: (domain) => Object.keys(states).filter(id => id.startsWith(domain + '.')),
                getEntitiesByDomain: (domain) => Object.fromEntries(
                    Object.entries(states).filter(([id]) => id.startsWith(domain + '.'))
                ),
                
                // State helpers
                isOn: (entityId) => ['on', 'open', 'active', 'playing'].includes(states[entityId]?.state),
                isOff: (entityId) => ['off', 'closed', 'inactive', 'paused', 'stopped'].includes(states[entityId]?.state),
                
                // Time helpers
                now: () => new Date().toISOString(),
                timestamp: () => Math.floor(Date.now() / 1000),
                
                // Data processing
                parseNumber: (value) => parseFloat(value) || 0,
                parseBoolean: (value) => Boolean(value) && value !== 'false' && value !== 'off',
                
                // Array helpers
                sum: (arr) => arr.reduce((a, b) => a + b, 0),
                avg: (arr) => arr.length ? utils.sum(arr) / arr.length : 0,
                min: (arr) => Math.min(...arr),
                max: (arr) => Math.max(...arr)
            }};
        """)
        
        # Wrap user code in an async function for better error handling
        wrapped_code = f"""
        (function() {{
            try {{
                const result = (function() {{
                    {code}
                }})();
                
                // Return both the result and any queued service calls
                return {{
                    result: result,
                    serviceCalls: _serviceCalls
                }};
            }} catch (error) {{
                console.error('User code error:', error.message);
                throw new Error('User code error: ' + error.message);
            }}
        }})();
        """
        
        # Execute with timeout
        execution_result = await asyncio.wait_for(
            asyncio.get_event_loop().run_in_executor(
                None, lambda: ctx.eval(wrapped_code)
            ),
            timeout=self._timeout
        )
        
        # Process any service calls that were queued
        if isinstance(execution_result, dict) and "serviceCalls" in execution_result:
            service_calls = execution_result.get("serviceCalls", {})
            for call_id, call_data in service_calls.items():
                try:
                    await self.hass.services.async_call(
                        call_data["domain"],
                        call_data["service"],
                        call_data["data"]
                    )
                    _LOGGER.info(f"Executed service call {call_id}: {call_data['domain']}.{call_data['service']}")
                except Exception as err:
                    _LOGGER.error(f"Service call {call_id} failed: {err}")
            
            return execution_result.get("result")
        
        return execution_result

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

    def _create_comprehensive_hass_api(self) -> dict[str, Any]:
        """Create comprehensive Home Assistant and HACS API for JavaScript context."""
        # Convert states to simple dict format for JSON serialization
        states_dict = {}
        for entity_id, state in self.hass.states.async_all():
            states_dict[entity_id] = {
                "state": state.state,
                "attributes": dict(state.attributes),
                "entity_id": entity_id,
                "last_changed": state.last_changed.isoformat(),
                "last_updated": state.last_updated.isoformat(),
                "domain": state.domain,
                "object_id": state.object_id,
                "name": state.name,
            }
        
        # Get HACS data if available - with proper error handling
        hacs_repositories = []
        hacs_info = {}
        hacs_status = {}
        
        try:
            if hasattr(self.hass.data, 'get') and 'hacs' in self.hass.data:
                hacs_data = self.hass.data.get('hacs')
                if hacs_data:
                    # Extract HACS repositories safely
                    if hasattr(hacs_data, 'repositories'):
                        for repo in getattr(hacs_data.repositories, 'list_all', []):
                            try:
                                if hasattr(repo, 'data'):
                                    repo_info = {
                                        "name": getattr(repo.data, 'full_name', getattr(repo.data, 'name', 'unknown')),
                                        "description": getattr(repo.data, 'description', ''),
                                        "installed": getattr(repo.data, 'installed', False),
                                        "available_version": getattr(repo.data, 'available_version', None),
                                        "installed_version": getattr(repo.data, 'installed_version', None),
                                        "category": getattr(repo.data, 'category', 'unknown'),
                                        "stars": getattr(repo.data, 'stargazers_count', 0),
                                        "topics": getattr(repo.data, 'topics', []),
                                    }
                                    hacs_repositories.append(repo_info)
                            except Exception as repo_err:
                                _LOGGER.debug(f"Error processing HACS repository {repo}: {repo_err}")
                                continue
                    
                    # HACS info safely
                    if hasattr(hacs_data, 'configuration'):
                        hacs_info = {
                            "version": getattr(hacs_data.configuration, 'version', 'unknown'),
                            "dev": getattr(hacs_data.configuration, 'dev', False),
                            "debug": getattr(hacs_data.configuration, 'debug', False),
                        }
                    
                    # HACS status safely
                    if hasattr(hacs_data, 'status'):
                        hacs_status = {
                            "startup": getattr(hacs_data.status, 'startup', True),
                            "background_task": getattr(hacs_data.status, 'background_task', False),
                        }
                        
        except Exception as hacs_err:
            _LOGGER.warning(f"Could not access HACS data: {hacs_err}")
            # Provide safe defaults
            hacs_repositories = []
            hacs_info = {"version": "unavailable", "dev": False, "debug": False}
            hacs_status = {"startup": True, "background_task": False}
        
        return {
            "states": states_dict,
            "config": {
                "latitude": self.hass.config.latitude,
                "longitude": self.hass.config.longitude,
                "elevation": self.hass.config.elevation,
                "unit_system": self.hass.config.units.name,
                "time_zone": str(self.hass.config.time_zone),
                "version": self.hass.config.version,
                "config_dir": self.hass.config.config_dir,
            },
            "hacs_repositories": hacs_repositories,
            "hacs_info": hacs_info,
            "hacs_status": hacs_status,
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
