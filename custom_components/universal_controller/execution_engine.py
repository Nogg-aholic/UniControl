"""JavaScript-like execution engine for Universal Controller using pure Python."""
from __future__ import annotations

import asyncio
import json
import logging
import re
from typing import Any

from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)


class TypeScriptExecutionEngine:
    """Engine for executing JavaScript-like code using pure Python."""

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize the execution engine."""
        self.hass = hass
        self._timeout = 10  # seconds

    async def execute(self, code: str) -> Any:
        """Execute JavaScript-like code and return the result."""
        if not code.strip():
            return None

        try:
            _LOGGER.debug("Executing JavaScript-like code with Python")
            return await self._execute_with_python_transpiler(code)
        except Exception as err:
            _LOGGER.error("Code execution error: %s", err)
            raise RuntimeError(f"Code execution failed: {err}")

    async def _execute_with_python_transpiler(self, code: str) -> Any:
        """Execute code by transpiling JavaScript-like syntax to Python."""
        
        # Create execution context with Home Assistant APIs
        context = self._create_execution_context()
        
        # Transpile JavaScript-like code to Python
        python_code = self._transpile_js_to_python(code)
        
        _LOGGER.debug(f"Transpiled code: {python_code}")
        
        # Execute in restricted environment
        try:
            result = await asyncio.wait_for(
                asyncio.get_event_loop().run_in_executor(
                    None, 
                    lambda: eval(python_code, {"__builtins__": {}}, context)
                ),
                timeout=self._timeout
            )
            
            # Handle async results
            if asyncio.iscoroutine(result):
                result = await result
                
            return result
            
        except Exception as err:
            raise RuntimeError(f"Execution error: {err}")

    def _transpile_js_to_python(self, js_code: str) -> str:
        """Convert JavaScript-like syntax to Python."""
        code = js_code.strip()
        
        # Handle common JavaScript patterns
        transformations = [
            # Variable declarations
            (r'\bconst\s+(\w+)', r'\1'),
            (r'\blet\s+(\w+)', r'\1'),
            (r'\bvar\s+(\w+)', r'\1'),
            
            # Boolean values
            (r'\btrue\b', 'True'),
            (r'\bfalse\b', 'False'),
            (r'\bnull\b', 'None'),
            (r'\bundefined\b', 'None'),
            
            # Comparison operators
            (r'===', '=='),
            (r'!==', '!='),
            
            # Arrow functions (simple cases)
            (r'(\w+)\s*=>\s*(\w+)', r'lambda \1: \2'),
            
            # Template literals (basic)
            (r'`([^`]*)`', r'f"\1"'),
            
            # Object property access (optional chaining)
            (r'(\w+)\?\.(\w+)', r'(\1.get("\2") if \1 else None)'),
            
            # Array methods
            (r'\.forEach\s*\(', '.for_each('),
            (r'\.map\s*\(', '.map('),
            (r'\.filter\s*\(', '.filter('),
            (r'\.find\s*\(', '.find('),
            
            # Console methods
            (r'console\.log\s*\(', 'console.log('),
            (r'console\.error\s*\(', 'console.error('),
            (r'console\.warn\s*\(', 'console.warn('),
        ]
        
        for pattern, replacement in transformations:
            code = re.sub(pattern, replacement, code)
        
        # Handle function calls and method chaining
        # Convert someObject.method() to someObject.method()
        
        # Handle return statements
        if not code.strip().startswith('return') and 'return' not in code:
            # If no explicit return, wrap in a lambda that returns the result
            lines = code.split('\n')
            if len(lines) == 1 and not any(keyword in code for keyword in ['if', 'for', 'while', 'def']):
                # Simple expression, just return it
                code = f'({code})'
        
        return code

    def _create_execution_context(self) -> dict[str, Any]:
        """Create the execution context with Home Assistant APIs."""
        
        # Get all states
        states = {}
        for entity_id, state in self.hass.states.async_all():
            states[entity_id] = {
                "state": state.state,
                "attributes": dict(state.attributes),
                "last_changed": state.last_changed.isoformat(),
                "last_updated": state.last_updated.isoformat(),
            }
        
        # Create service call handler
        service_calls = []
        
        async def call_service(domain: str, service: str, data: dict = None):
            """Call a Home Assistant service."""
            try:
                await self.hass.services.async_call(domain, service, data or {})
                _LOGGER.info(f"Executed service: {domain}.{service}")
                return f"service_call_{len(service_calls)}"
            except Exception as err:
                _LOGGER.error(f"Service call failed: {err}")
                raise
        
        # Create JavaScript-like APIs
        class JSObject:
            """JavaScript-like object with methods."""
            def __init__(self, data):
                self._data = data
                
            def __getitem__(self, key):
                return self._data.get(key)
                
            def get(self, key, default=None):
                return self._data.get(key, default)
                
            def __getattr__(self, name):
                return self._data.get(name)
        
        class JSArray(list):
            """JavaScript-like array with methods."""
            def for_each(self, func):
                for item in self:
                    func(item)
                    
            def map(self, func):
                return JSArray([func(item) for item in self])
                
            def filter(self, func):
                return JSArray([item for item in self if func(item)])
                
            def find(self, func):
                for item in self:
                    if func(item):
                        return item
                return None
        
        # HACS data
        hacs_data = self._get_hacs_data()
        
        # Services object
        services = JSObject({
            "call": call_service,
            "turnOn": lambda entity_id, data=None: call_service('homeassistant', 'turn_on', 
                                                               {'entity_id': entity_id, **(data or {})}),
            "turnOff": lambda entity_id, data=None: call_service('homeassistant', 'turn_off', 
                                                                {'entity_id': entity_id, **(data or {})}),
            "toggle": lambda entity_id, data=None: call_service('homeassistant', 'toggle', 
                                                               {'entity_id': entity_id, **(data or {})}),
            "notify": lambda message, title=None: call_service('notify', 'notify', 
                                                              {'message': message, 'title': title} if title else {'message': message}),
        })
        
        # Utils object
        utils = JSObject({
            "getEntity": lambda entity_id: JSObject(states.get(entity_id, {})),
            "getState": lambda entity_id: states.get(entity_id, {}).get('state'),
            "getAttribute": lambda entity_id, attr: states.get(entity_id, {}).get('attributes', {}).get(attr),
            "isOn": lambda entity_id: states.get(entity_id, {}).get('state') in ['on', 'open', 'active', 'playing'],
            "isOff": lambda entity_id: states.get(entity_id, {}).get('state') in ['off', 'closed', 'inactive', 'paused', 'stopped'],
            "filterByDomain": lambda domain: JSArray([eid for eid in states.keys() if eid.startswith(domain + '.')]),
            "now": lambda: __import__('datetime').datetime.now().isoformat(),
            "timestamp": lambda: int(__import__('time').time()),
        })
        
        # Console object
        console = JSObject({
            "log": lambda *args: _LOGGER.info("User code: %s", " ".join(str(arg) for arg in args)),
            "error": lambda *args: _LOGGER.error("User code: %s", " ".join(str(arg) for arg in args)),
            "warn": lambda *args: _LOGGER.warning("User code: %s", " ".join(str(arg) for arg in args)),
        })
        
        # HACS object
        HACS = JSObject(hacs_data)
        
        # Math utilities
        import math
        Math = JSObject({
            "min": min,
            "max": max,
            "round": round,
            "floor": math.floor,
            "ceil": math.ceil,
            "abs": abs,
            "random": __import__('random').random,
        })
        
        return {
            "states": JSObject(states),
            "services": services,
            "utils": utils,
            "console": console,
            "HACS": HACS,
            "Math": Math,
            "Date": JSObject({
                "now": lambda: int(__import__('time').time() * 1000),
            }),
            "JSON": JSObject({
                "stringify": json.dumps,
                "parse": json.loads,
            }),
            # Python built-ins we want to allow
            "len": len,
            "str": str,
            "int": int,
            "float": float,
            "bool": bool,
            "list": list,
            "dict": dict,
        }

    def _get_hacs_data(self) -> dict[str, Any]:
        """Get HACS data safely."""
        try:
            if 'hacs' in self.hass.data:
                hacs = self.hass.data['hacs']
                return {
                    "repositories": [
                        {
                            "name": getattr(repo.data, 'full_name', 'unknown'),
                            "installed": getattr(repo.data, 'installed', False),
                            "category": getattr(repo.data, 'category', 'unknown'),
                        }
                        for repo in getattr(hacs.repositories, 'list_all', [])
                        if hasattr(repo, 'data')
                    ]
                }
        except Exception:
            pass
        return {"repositories": []}
