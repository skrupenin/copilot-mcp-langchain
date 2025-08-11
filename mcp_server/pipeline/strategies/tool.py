"""
Tool execution strategy.

This strategy handles basic tool execution with parameter substitution
and result storage. It's the fundamental building block of the pipeline system.
"""

import asyncio
import logging
from typing import Any, Dict, Callable

from .base import ExecutionStrategy
from ..models import PipelineResult, ExecutionContext
from ..expressions import substitute_expressions

logger = logging.getLogger('mcp_server.pipeline.strategies.tool')


class ToolStrategy(ExecutionStrategy):
    """Strategy for executing tool calls - the basic pipeline functionality."""
    
    def __init__(self, tool_runner: Callable[[str, Dict[str, Any]], Any]):
        self.tool_runner = tool_runner
    
    def can_handle(self, step: Dict[str, Any]) -> bool:
        """Handle steps that have a 'tool' field."""
        return "tool" in step and step.get("type", "tool") == "tool"
    
    async def execute(self, step: Dict[str, Any], context: ExecutionContext, executor) -> PipelineResult:
        """Execute a tool call with parameter substitution."""
        try:
            tool_name = step["tool"]
            params = step.get("params", {})
            output_var = step.get("output")
            
            logger.info(f"Step {context.step_number}: Executing tool '{tool_name}'")
            
            # Determine tool type for smart parameter conversion
            tool_type = self._detect_tool_type(tool_name)
            logger.debug(f"Detected tool type: {tool_type} for tool: {tool_name}")
            
            # Substitute variables in parameters based on tool type
            if tool_type == "python_json":
                # Special handling for Python tools that work with JSON data
                substituted_params = self._substitute_for_python_json(params, context.variables)
                logger.debug(f"Python-JSON parameters after substitution: {substituted_params}")
            else:
                substituted_params = self._substitute_recursive(params, context.variables)
                logger.debug(f"Standard parameters after substitution: {substituted_params}")
            
            logger.debug(f"Tool parameters after substitution: {substituted_params}")
            
            # Execute the tool
            if asyncio.iscoroutinefunction(self.tool_runner):
                tool_result = await self.tool_runner(tool_name, substituted_params)
            else:
                tool_result = self.tool_runner(tool_name, substituted_params)
            
            # Parse and store result - extract and parse JSON from TextContent
            if isinstance(tool_result, list) and len(tool_result) > 0:
                first_result = tool_result[0]
                # If it's a TextContent object, extract the text
                if hasattr(first_result, 'text'):
                    text_content = first_result.text
                    # Try to parse as JSON, but if it fails, keep as text
                    try:
                        import json
                        parsed_result = json.loads(text_content)
                        logger.debug(f"Successfully parsed tool result as JSON")
                    except (json.JSONDecodeError, AttributeError):
                        # Not JSON - keep as plain text (useful for CSV, HTML, etc.)
                        parsed_result = text_content
                        logger.debug(f"Tool result kept as plain text (not JSON)")
                else:
                    parsed_result = first_result
            else:
                parsed_result = tool_result
            
            # Ensure result is JSON-compatible before storing
            json_compatible_result = self._ensure_json_compatible(parsed_result)
            
            if output_var:
                context.variables[output_var] = json_compatible_result
                logger.debug(f"Stored JSON-compatible result in variable '{output_var}': {type(json_compatible_result).__name__}")
            
            return PipelineResult(success=True, context=context.variables)
            
        except Exception as e:
            error_msg = f"Step {context.step_number} tool '{tool_name}' failed: {str(e)}"
            logger.error(error_msg)
            return PipelineResult(
                success=False,
                error=error_msg,
                step=context.step_number,
                tool=tool_name,
                context=context.variables
            )
    
    @property
    def strategy_name(self) -> str:
        return "Tool"
    
    def _substitute_recursive(self, obj: Any, variables: Dict[str, Any]) -> Any:
        """Recursively substitute expressions in an object."""
        if isinstance(obj, dict):
            return {k: self._substitute_recursive(v, variables) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._substitute_recursive(item, variables) for item in obj]
        elif isinstance(obj, str):
            if "${" in obj or "$[" in obj:
                return substitute_expressions(obj, variables, expected_result_type="python")
            return obj
        else:
            return obj
    
    def _ensure_json_compatible(self, obj: Any) -> Any:
        """Ensure object is JSON-serializable."""
        import json
        from datetime import datetime
        from decimal import Decimal
        
        try:
            # Test if object is already JSON-serializable
            json.dumps(obj)
            return obj
        except (TypeError, ValueError):
            pass
        
        # Convert problematic types
        if isinstance(obj, tuple):
            return [self._ensure_json_compatible(item) for item in obj]
        elif isinstance(obj, set):
            return [self._ensure_json_compatible(item) for item in obj]
        elif isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, Decimal):
            return float(obj)
        elif hasattr(obj, '__dict__'):
            return {k: self._ensure_json_compatible(v) for k, v in obj.__dict__.items()}
        elif isinstance(obj, dict):
            return {k: self._ensure_json_compatible(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._ensure_json_compatible(item) for item in obj]
        else:
            return str(obj)
    
    def _detect_tool_type(self, tool_name: str) -> str:
        """Detect tool type based on tool name."""
        if "json" in tool_name.lower():
            # Tools that work with JSON data need special object handling
            return "python_json"
        elif tool_name.startswith("lng_"):
            return "python"
        else:
            return "other"
    
    def _substitute_for_python_json(self, obj: Any, variables: Dict[str, Any]) -> Any:
        """Substitute expressions for Python tools that expect JSON objects - keep objects as objects."""
        import json
        import re
        
        if isinstance(obj, dict):
            result = {}
            for k, v in obj.items():
                result[k] = self._substitute_for_python_json(v, variables)
            return result
            
        elif isinstance(obj, list):
            return [self._substitute_for_python_json(item, variables) for item in obj]
        elif isinstance(obj, str):
            if "${" in obj or "$[" in obj:
                # Handle each expression separately
                def replace_expression(match):
                    expr = match.group(0)
                    try:
                        # For simple variable substitution like ${variable_name}, get directly from context
                        if expr.startswith('${') and expr.endswith('}'):
                            var_name = expr[2:-1].strip()
                            if var_name in variables:
                                result = variables[var_name]
                                logger.debug(f"Expression '{expr}' evaluated to: {result} (type: {type(result)})")
                                
                                # For Python JSON tools, keep objects as objects (don't convert to strings)
                                if isinstance(result, (dict, list, int, float, bool, type(None))):
                                    logger.debug(f"Keeping object as-is for Python JSON tool: {type(result)}")
                                    return result  # Return the actual object, not string
                                else:
                                    return str(result)
                        
                        # For complex expressions, use substitute_expressions
                        result = substitute_expressions(expr, variables, expected_result_type="python")
                        logger.debug(f"Complex expression '{expr}' evaluated to: {result} (type: {type(result)})")
                        return result
                            
                    except Exception as e:
                        logger.warning(f"Failed to evaluate expression '{expr}': {e}")
                        return expr  # Return original expression on error
                
                # Check if this is a simple single expression that should return the object directly
                pattern = r'\$\{[^}]+\}|\$\[[^\]]+\]'
                matches = re.findall(pattern, obj)
                
                if len(matches) == 1 and matches[0] == obj.strip():
                    # This is a single expression - return the object directly
                    return replace_expression(re.match(pattern, obj.strip()))
                else:
                    # This is a complex string with multiple expressions - do string substitution
                    result = re.sub(pattern, lambda m: str(replace_expression(m)), obj)
                    return result
            return obj
        else:
            return obj
