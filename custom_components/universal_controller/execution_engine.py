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
            # Try Node.js execution first, then fallback to Python
            try:
                _LOGGER.debug("Attempting Node.js JavaScript execution")
                return await self._execute_with_nodejs(code)
            except (FileNotFoundError, RuntimeError) as nodejs_err:
                _LOGGER.warning(f"Node.js not available ({nodejs_err}), falling back to Python")
                return await self._execute_with_python_fallback(code)
        except Exception as err:
            _LOGGER.error("Code execution error: %s", err)
            raise RuntimeError(f"Code execution failed: {err}")

    async def _execute_with_nodejs(self, code: str) -> Any:
        """Execute code using Node.js JavaScript engine."""
        import tempfile
        import subprocess
        import os
        
        # Check if Node.js is available
        try:
            subprocess.run(["node", "--version"], capture_output=True, check=True)
        except (FileNotFoundError, subprocess.CalledProcessError):
            raise FileNotFoundError("Node.js not available")

        # Create comprehensive Home Assistant and HACS API
        hass_api = self._create_comprehensive_hass_api()
        
        # Create JavaScript wrapper with all APIs
        js_wrapper = f"""
const hass = {json.dumps(hass_api, default=str)};
const states = hass.states;

// Service call queue for async operations
const _serviceCalls = {{}};

// Service call handler
function callService(domain, service, data = {{}}) {{
    const callId = 'call_' + Math.random().toString(36).substr(2, 9);
    _serviceCalls[callId] = {{ domain, service, data }};
    return callId;
}}

hass.callService = callService;

// Enhanced Console API
const console = {{
    log: function(...args) {{ 
        process.stdout.write('_LOG_:' + args.map(a => typeof a === 'object' ? JSON.stringify(a) : String(a)).join(' ') + '\\n'); 
    }},
    error: function(...args) {{ 
        process.stderr.write('_ERROR_:' + args.map(a => typeof a === 'object' ? JSON.stringify(a) : String(a)).join(' ') + '\\n'); 
    }},
    warn: function(...args) {{ 
        process.stdout.write('_WARN_:' + args.map(a => typeof a === 'object' ? JSON.stringify(a) : String(a)).join(' ') + '\\n'); 
    }},
    info: function(...args) {{ 
        process.stdout.write('_INFO_:' + args.map(a => typeof a === 'object' ? JSON.stringify(a) : String(a)).join(' ') + '\\n'); 
    }},
    debug: function(...args) {{ 
        process.stdout.write('_DEBUG_:' + args.map(a => typeof a === 'object' ? JSON.stringify(a) : String(a)).join(' ') + '\\n'); 
    }}
}};

// Date utilities
const DateUtils = {{
    now: () => Date.now(),
    utc: () => new Date().toISOString(),
    local: () => new Date().toLocaleString(),
    parse: (str) => new Date(str),
    format: (date, format) => new Date(date).toLocaleString()
}};

// Math utilities
const MathUtils = Object.assign({{}}, Math, {{
    clamp: (num, min, max) => Math.min(Math.max(num, min), max),
    randomRange: (min, max) => Math.random() * (max - min) + min,
    roundTo: (num, decimals) => Math.round(num * Math.pow(10, decimals)) / Math.pow(10, decimals)
}});

// HACS Integration API
const HACS = {{
    getRepositories: () => hass.hacs_repositories || [],
    getRepository: (name) => (hass.hacs_repositories || []).find(r => r.name === name),
    isInstalled: (name) => (hass.hacs_repositories || []).some(r => r.name === name && r.installed),
    install: (name) => hass.callService('hacs', 'install', {{ repository: name }}),
    uninstall: (name) => hass.callService('hacs', 'uninstall', {{ repository: name }}),
    update: (name) => hass.callService('hacs', 'update', {{ repository: name }}),
    getInfo: () => hass.hacs_info || {{}},
    getStatus: () => hass.hacs_status || {{}}
}};

// Enhanced Services API
const services = {{
    call: (domain, service, data = {{}}) => {{
        console.log('Calling service:', domain + '.' + service, data);
        return hass.callService(domain, service, data);
    }},
    turnOn: (entityId, data = {{}}) => services.call('homeassistant', 'turn_on', {{ entity_id: entityId, ...data }}),
    turnOff: (entityId, data = {{}}) => services.call('homeassistant', 'turn_off', {{ entity_id: entityId, ...data }}),
    toggle: (entityId, data = {{}}) => services.call('homeassistant', 'toggle', {{ entity_id: entityId, ...data }}),
    notify: (message, title = null, data = {{}}) => {{
        const payload = {{ message, ...data }};
        if (title) payload.title = title;
        return services.call('notify', 'notify', payload);
    }},
    runScript: (scriptId, data = {{}}) => services.call('script', scriptId, data),
    triggerAutomation: (automationId) => services.call('automation', 'trigger', {{ entity_id: automationId }})
}};

// Utility functions
const utils = {{
    getEntity: (entityId) => states[entityId],
    getEntityState: (entityId) => states[entityId]?.state,
    getEntityAttribute: (entityId, attr) => states[entityId]?.attributes[attr],
    filterEntities: (domain) => Object.keys(states).filter(id => id.startsWith(domain + '.')),
    getEntitiesByDomain: (domain) => Object.fromEntries(
        Object.entries(states).filter(([id]) => id.startsWith(domain + '.'))
    ),
    isOn: (entityId) => ['on', 'open', 'active', 'playing'].includes(states[entityId]?.state),
    isOff: (entityId) => ['off', 'closed', 'inactive', 'paused', 'stopped'].includes(states[entityId]?.state),
    now: () => new Date().toISOString(),
    timestamp: () => Math.floor(Date.now() / 1000),
    parseNumber: (value) => parseFloat(value) || 0,
    parseBoolean: (value) => Boolean(value) && value !== 'false' && value !== 'off',
    sum: (arr) => arr.reduce((a, b) => a + b, 0),
    avg: (arr) => arr.length ? utils.sum(arr) / arr.length : 0,
    min: (arr) => Math.min(...arr),
    max: (arr) => Math.max(...arr)
}};

// User code execution
try {{
    const result = (function() {{
        {code}
    }})();
    
    // Output result and service calls
    console.log('_RESULT_:' + JSON.stringify({{
        result: result,
        serviceCalls: _serviceCalls
    }}));
}} catch (error) {{
    console.error('_USER_CODE_ERROR_:' + error.message);
    process.exit(1);
}}
"""

        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as temp_file:
            temp_file.write(js_wrapper)
            temp_file_path = temp_file.name

        try:
            # Execute with Node.js
            process = await asyncio.create_subprocess_exec(
                'node', temp_file_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=self._timeout
            )
            
            # Parse output
            stdout_text = stdout.decode() if stdout else ""
            stderr_text = stderr.decode() if stderr else ""
            
            # Process logs and find result
            result_data = None
            service_calls = {}
            
            for line in stdout_text.split('\\n'):
                if line.startswith('_RESULT_:'):
                    try:
                        result_json = json.loads(line[9:])
                        result_data = result_json.get('result')
                        service_calls = result_json.get('serviceCalls', {})
                    except json.JSONDecodeError:
                        pass
                elif line.startswith('_LOG_:'):
                    _LOGGER.info("User code: %s", line[5:])
                elif line.startswith('_ERROR_:'):
                    _LOGGER.error("User code: %s", line[7:])
                elif line.startswith('_WARN_:'):
                    _LOGGER.warning("User code: %s", line[6:])
            
            # Check for errors
            if process.returncode != 0:
                error_msg = stderr_text
                if '_USER_CODE_ERROR_:' in stderr_text:
                    error_msg = stderr_text.split('_USER_CODE_ERROR_:')[1].strip()
                raise RuntimeError(f"JavaScript execution error: {error_msg}")
            
            # Process service calls
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
            
            return result_data
            
        finally:
            # Clean up temp file
            try:
                os.unlink(temp_file_path)
            except OSError:
                pass

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
