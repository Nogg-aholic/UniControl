"""Template rendering engine for Universal Controller."""
from __future__ import annotations

import json
import logging
import re
from datetime import datetime
from typing import Any, Dict

from homeassistant.core import HomeAssistant
from homeassistant.util import dt as dt_util

_LOGGER = logging.getLogger(__name__)


class TemplateRenderer:
    """Advanced template renderer for Universal Controller."""

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize the template renderer."""
        self.hass = hass

    def render_html(self, template: str, context: Dict[str, Any]) -> str:
        """Render HTML template with advanced features."""
        if not template.strip():
            return "<div>No template defined</div>"

        try:
            # Start with the template
            rendered = template
            
            # Apply simple variable substitutions first
            rendered = self._apply_variable_substitutions(rendered, context)
            
            # Apply conditional blocks
            rendered = self._apply_conditionals(rendered, context)
            
            # Apply loops
            rendered = self._apply_loops(rendered, context)
            
            # Apply function calls
            rendered = self._apply_functions(rendered, context)
            
            return rendered
            
        except Exception as err:
            _LOGGER.error("Template rendering error: %s", err)
            return f"<div class='error'>Template error: {err}</div>"

    def _apply_variable_substitutions(self, template: str, context: Dict[str, Any]) -> str:
        """Apply variable substitutions like {{variable}}."""
        # Find all variable patterns
        pattern = r'\{\{([^}]+)\}\}'
        
        def replace_var(match):
            var_path = match.group(1).strip()
            try:
                value = self._get_nested_value(context, var_path)
                return self._format_value(value)
            except (KeyError, AttributeError, TypeError):
                return f"{{{{ {var_path} }}}}"  # Keep original if not found
        
        return re.sub(pattern, replace_var, template)

    def _apply_conditionals(self, template: str, context: Dict[str, Any]) -> str:
        """Apply conditional blocks like {% if condition %}...{% endif %}."""
        # Pattern for if blocks
        if_pattern = r'\{%\s*if\s+([^%]+)\s*%\}(.*?)\{%\s*endif\s*%\}'
        
        def replace_if(match):
            condition = match.group(1).strip()
            content = match.group(2)
            
            try:
                if self._evaluate_condition(condition, context):
                    return content
                else:
                    return ""
            except Exception as err:
                _LOGGER.warning("Conditional evaluation error: %s", err)
                return ""
        
        return re.sub(if_pattern, replace_if, template, flags=re.DOTALL)

    def _apply_loops(self, template: str, context: Dict[str, Any]) -> str:
        """Apply loop blocks like {% for item in items %}...{% endfor %}."""
        # Pattern for for loops
        for_pattern = r'\{%\s*for\s+(\w+)\s+in\s+([^%]+)\s*%\}(.*?)\{%\s*endfor\s*%\}'
        
        def replace_for(match):
            var_name = match.group(1).strip()
            iterable_path = match.group(2).strip()
            content = match.group(3)
            
            try:
                iterable = self._get_nested_value(context, iterable_path)
                if not isinstance(iterable, (list, tuple, dict)):
                    return ""
                
                result = []
                for item in iterable:
                    # Create new context with loop variable
                    loop_context = context.copy()
                    loop_context[var_name] = item
                    
                    # Render content with loop context
                    rendered_content = self._apply_variable_substitutions(content, loop_context)
                    result.append(rendered_content)
                
                return "".join(result)
                
            except Exception as err:
                _LOGGER.warning("Loop evaluation error: %s", err)
                return ""
        
        return re.sub(for_pattern, replace_for, template, flags=re.DOTALL)

    def _apply_functions(self, template: str, context: Dict[str, Any]) -> str:
        """Apply function calls like {{ function(args) }}."""
        # Pattern for function calls
        func_pattern = r'\{\{\s*(\w+)\(([^)]*)\)\s*\}\}'
        
        def replace_func(match):
            func_name = match.group(1)
            args_str = match.group(2).strip()
            
            try:
                # Parse arguments
                args = self._parse_function_args(args_str, context)
                
                # Call function
                result = self._call_function(func_name, args, context)
                return self._format_value(result)
                
            except Exception as err:
                _LOGGER.warning("Function call error for %s: %s", func_name, err)
                return f"{{{{ {func_name}({args_str}) }}}}"
        
        return re.sub(func_pattern, replace_func, template)

    def _get_nested_value(self, obj: Any, path: str) -> Any:
        """Get nested value from object using dot notation."""
        keys = path.split('.')
        current = obj
        
        for key in keys:
            if isinstance(current, dict):
                current = current[key]
            elif hasattr(current, key):
                current = getattr(current, key)
            else:
                raise KeyError(f"Path '{path}' not found")
        
        return current

    def _evaluate_condition(self, condition: str, context: Dict[str, Any]) -> bool:
        """Evaluate a condition expression."""
        # Simple condition evaluation
        # Support for: variable, variable == value, variable != value, etc.
        
        # Replace variables in condition
        condition = self._apply_variable_substitutions(f"{{{{{condition}}}}}", context)[2:-2]
        
        # Basic operators
        if " == " in condition:
            left, right = condition.split(" == ", 1)
            return str(left).strip() == str(right).strip()
        elif " != " in condition:
            left, right = condition.split(" != ", 1)
            return str(left).strip() != str(right).strip()
        elif " > " in condition:
            left, right = condition.split(" > ", 1)
            try:
                return float(left) > float(right)
            except ValueError:
                return False
        elif " < " in condition:
            left, right = condition.split(" < ", 1)
            try:
                return float(left) < float(right)
            except ValueError:
                return False
        else:
            # Simple truthiness test
            try:
                value = self._get_nested_value(context, condition.strip())
                return bool(value)
            except (KeyError, AttributeError):
                return False

    def _parse_function_args(self, args_str: str, context: Dict[str, Any]) -> list[Any]:
        """Parse function arguments."""
        if not args_str.strip():
            return []
        
        args = []
        for arg in args_str.split(','):
            arg = arg.strip()
            
            # String literal
            if (arg.startswith('"') and arg.endswith('"')) or (arg.startswith("'") and arg.endswith("'")):
                args.append(arg[1:-1])
            # Number
            elif arg.replace('.', '').replace('-', '').isdigit():
                args.append(float(arg) if '.' in arg else int(arg))
            # Variable
            else:
                try:
                    value = self._get_nested_value(context, arg)
                    args.append(value)
                except (KeyError, AttributeError):
                    args.append(arg)  # Keep as string if variable not found
        
        return args

    def _call_function(self, func_name: str, args: list[Any], context: Dict[str, Any]) -> Any:
        """Call a template function."""
        functions = {
            'now': lambda: datetime.now().isoformat(),
            'format_date': lambda date_str, fmt='%Y-%m-%d %H:%M:%S': 
                datetime.fromisoformat(str(date_str)).strftime(fmt) if date_str else '',
            'upper': lambda text: str(text).upper(),
            'lower': lambda text: str(text).lower(),
            'length': lambda obj: len(obj) if obj else 0,
            'round': lambda num, digits=0: round(float(num), int(digits)),
            'json': lambda obj: json.dumps(obj, default=str),
            'default': lambda value, default_val: value if value is not None else default_val,
            'state': lambda entity_id: self.hass.states.get(entity_id).state if self.hass.states.get(entity_id) else None,
            'attr': lambda entity_id, attr_name: 
                getattr(self.hass.states.get(entity_id), 'attributes', {}).get(attr_name) 
                if self.hass.states.get(entity_id) else None,
        }
        
        if func_name in functions:
            return functions[func_name](*args)
        else:
            raise ValueError(f"Unknown function: {func_name}")

    def _format_value(self, value: Any) -> str:
        """Format a value for HTML output."""
        if value is None:
            return ""
        elif isinstance(value, bool):
            return str(value).lower()
        elif isinstance(value, (int, float)):
            return str(value)
        elif isinstance(value, datetime):
            return value.isoformat()
        elif isinstance(value, (dict, list)):
            return json.dumps(value, default=str)
        else:
            return str(value)

    def create_context(self, entity_state: Any, execution_result: Any = None) -> Dict[str, Any]:
        """Create template context from entity state and execution result."""
        context = {
            'state': entity_state.state,
            'entity_id': entity_state.entity_id,
            'friendly_name': entity_state.attributes.get('friendly_name', entity_state.entity_id),
            'attributes': dict(entity_state.attributes),
            'last_changed': entity_state.last_changed,
            'last_updated': entity_state.last_updated,
        }
        
        # Add execution result if available
        if execution_result is not None:
            context['result'] = execution_result
            
            # If result is a dict, add its keys to context
            if isinstance(execution_result, dict):
                context.update(execution_result)
        
        # Add Home Assistant states for template access
        context['states'] = {
            entity_id: {
                'state': state.state,
                'attributes': dict(state.attributes),
            }
            for entity_id, state in self.hass.states.async_all()
        }
        
        # Add current time
        context['now'] = datetime.now()
        context['utc_now'] = dt_util.utcnow()
        
        return context
