"""
Expression evaluation strategies for pipeline execution.

Provides unified expression evaluation with multiple backends:
- JavaScript expressions: ${expression}  
- Python expressions: $[expression]

Context always contains native Python objects (dict, list, str, int, bool, None).
Results can be returned as Python objects or JSON strings based on expected_result_type.
"""

import json
import re
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

logger = logging.getLogger('mcp_server.pipeline.expressions')

# Check for PyMiniRacer availability
try:
    import py_mini_racer
    JS_AVAILABLE = True
except ImportError:
    JS_AVAILABLE = False
    logger.warning("PyMiniRacer not available. JavaScript expressions will use fallback Python evaluation.")


class ExpressionEvaluationError(Exception):
    """Raised when expression evaluation fails."""
    
    def __init__(self, strategy_name: str, expression: str, step_info: Dict[str, Any], original_error: Exception):
        self.strategy_name = strategy_name
        self.expression = expression
        self.step_info = step_info
        self.original_error = original_error
        
        super().__init__(
            f"Expression evaluation failed in '{strategy_name}' at step '{step_info.get('step', 'unknown')}': "
            f"'{expression}' -> '{str(original_error)}'"
        )


class ExpressionStrategy(ABC):
    """Base class for expression evaluation strategies."""
    
    @abstractmethod
    def can_handle(self, expression: str) -> bool:
        """Check if this strategy can handle the given expression."""
        pass
    
    @abstractmethod
    def evaluate(self, expression: str, context: Dict[str, Any], expected_result_type: str, step_info: Dict[str, Any] = None) -> Any:
        """
        Evaluate expression with given context.
        
        Args:
            expression: Expression string (e.g., "${variable}" or "$[expression]")
            context: Dictionary of native Python objects
            expected_result_type: "python" or "json"
            step_info: Information about current pipeline step for error reporting
            
        Returns:
            Result in format specified by expected_result_type
        """
        pass
    
    def extract_expression(self, expression: str) -> str:
        """Extract clean expression content from wrapper syntax."""
        # Remove ${...} or $[...] wrapper
        if expression.startswith('${') and expression.endswith('}'):
            return expression[2:-1]
        elif expression.startswith('$[') and expression.endswith(']'):
            return expression[2:-1]
        return expression
    
    def format_result(self, result: Any, expected_result_type: str) -> Any:
        """Format result according to expected type."""
        if expected_result_type == "python":
            return result
        elif expected_result_type == "json":
            try:
                return json.dumps(result, ensure_ascii=False)
            except (TypeError, ValueError) as e:
                logger.warning(f"Failed to serialize result to JSON: {e}, returning string representation")
                return str(result)
        else:
            raise ValueError(f"Unknown expected_result_type: {expected_result_type}")


class JavaScriptExpressionStrategy(ExpressionStrategy):
    """Strategy for evaluating JavaScript expressions: ${expression}"""
    
    def __init__(self):
        self.js_context = None
        if JS_AVAILABLE:
            self.js_context = py_mini_racer.MiniRacer()
    
    def can_handle(self, expression: str) -> bool:
        """Check if expression uses JavaScript syntax: ${...}"""
        return expression.startswith('${') and expression.endswith('}')
    
    def evaluate(self, expression: str, context: Dict[str, Any], expected_result_type: str, step_info: Dict[str, Any] = None) -> Any:
        """Evaluate JavaScript expression."""
        step_info = step_info or {}
        
        try:
            if not JS_AVAILABLE:
                # Fallback to Python evaluation with JS syntax conversion
                return self._evaluate_fallback(expression, context, expected_result_type, step_info)
            
            clean_expression = self.extract_expression(expression)
            
            # Set context variables in JavaScript environment
            self._set_js_context(context)
            
            # Evaluate expression in JavaScript
            js_result = self.js_context.eval(clean_expression)
            
            # Convert JavaScript result back to Python
            python_result = self._convert_js_to_python(js_result, clean_expression)
            
            # Format according to expected type
            return self.format_result(python_result, expected_result_type)
            
        except Exception as e:
            raise ExpressionEvaluationError("JavaScriptStrategy", expression, step_info, e)
    
    def _set_js_context(self, context: Dict[str, Any]) -> None:
        """Set Python context variables in JavaScript environment."""
        for key, value in context.items():
            try:
                if isinstance(value, (dict, list)):
                    # Convert complex objects to JSON for JavaScript
                    js_value = json.dumps(value, ensure_ascii=False)
                    self.js_context.eval(f"var {key} = JSON.parse({json.dumps(js_value)});")
                elif isinstance(value, str):
                    self.js_context.eval(f"var {key} = {json.dumps(value)};")
                elif isinstance(value, (int, float, bool)) or value is None:
                    self.js_context.eval(f"var {key} = {json.dumps(value)};")
                else:
                    # Fallback: convert to JSON string
                    js_value = json.dumps(str(value))
                    self.js_context.eval(f"var {key} = {js_value};")
            except Exception as e:
                logger.warning(f"Failed to set JavaScript context variable '{key}': {e}")
    
    def _convert_js_to_python(self, js_result: Any, expression: str) -> Any:
        """Convert JavaScript result back to Python object."""
        try:
            # Try to serialize and deserialize to get clean Python objects
            json_str = self.js_context.eval(f"JSON.stringify(({expression}))")
            return json.loads(json_str)
        except:
            # Fallback: return as-is (PyMiniRacer should handle basic conversion)
            return js_result
    
    def _evaluate_fallback(self, expression: str, context: Dict[str, Any], expected_result_type: str, step_info: Dict[str, Any]) -> Any:
        """Fallback JavaScript evaluation using Python with JS syntax conversion."""
        clean_expression = self.extract_expression(expression)
        
        # Simple JavaScript to Python syntax conversion
        py_expression = clean_expression
        py_expression = re.sub(r'\bundefined\b', 'None', py_expression)
        py_expression = re.sub(r'\bnull\b', 'None', py_expression)
        py_expression = re.sub(r'\btrue\b', 'True', py_expression)
        py_expression = re.sub(r'\bfalse\b', 'False', py_expression)
        py_expression = re.sub(r'\|\|', ' or ', py_expression)
        py_expression = re.sub(r'&&', ' and ', py_expression)
        
        # Handle JSON methods
        eval_context = {
            **context,
            'JSON': {
                'stringify': lambda obj: json.dumps(obj, ensure_ascii=False),
                'parse': lambda s: json.loads(s)
            }
        }
        
        try:
            result = eval(py_expression, {"__builtins__": {}}, eval_context)
            return self.format_result(result, expected_result_type)
        except Exception as e:
            raise ExpressionEvaluationError("JavaScriptStrategy(Fallback)", expression, step_info, e)


class PythonExpressionStrategy(ExpressionStrategy):
    """Strategy for evaluating Python expressions: $[expression]"""
    
    def can_handle(self, expression: str) -> bool:
        """Check if expression uses Python syntax: $[...]"""
        return expression.startswith('$[') and expression.endswith(']')
    
    def evaluate(self, expression: str, context: Dict[str, Any], expected_result_type: str, step_info: Dict[str, Any] = None) -> Any:
        """Evaluate Python expression."""
        step_info = step_info or {}
        
        try:
            clean_expression = self.extract_expression(expression)
            
            # Create safe evaluation context
            eval_context = {
                **context,
                'json': json,
                'len': len,
                'str': str,
                'int': int,
                'float': float,
                'bool': bool,
                'list': list,
                'dict': dict,
                'sum': sum,
                'max': max,
                'min': min,
                'sorted': sorted,
                'reversed': reversed,
                'enumerate': enumerate,
                'zip': zip,
                'range': range,
            }
            
            # Evaluate Python expression
            result = eval(clean_expression, {"__builtins__": {}}, eval_context)
            
            # Format according to expected type
            return self.format_result(result, expected_result_type)
            
        except Exception as e:
            raise ExpressionEvaluationError("PythonStrategy", expression, step_info, e)


# Global registry of expression strategies
_strategies: List[ExpressionStrategy] = [
    JavaScriptExpressionStrategy(),
    PythonExpressionStrategy()
]


def evaluate_expression(expression: str, context: Dict[str, Any], expected_result_type: str = "python", step_info: Dict[str, Any] = None) -> Any:
    """
    Universal expression evaluation function.
    
    Args:
        expression: Expression to evaluate ("${js_expr}", "$[py_expr]", or plain text)
        context: Dictionary of native Python objects 
        expected_result_type: "python" (returns Python objects) or "json" (returns JSON strings)
        step_info: Pipeline step information for error reporting
        
    Returns:
        Evaluated result in specified format
        
    Raises:
        ExpressionEvaluationError: If evaluation fails
    """
    # Try each strategy
    for strategy in _strategies:
        if strategy.can_handle(expression):
            return strategy.evaluate(expression, context, expected_result_type, step_info)
    
    # Fallback for plain text
    if expected_result_type == "python":
        return None
    elif expected_result_type == "json":
        return "null"
    else:
        raise ValueError(f"Unknown expected_result_type: {expected_result_type}")


def contains_expressions(text: str) -> bool:
    """Check if text contains any evaluable expressions."""
    return bool(re.search(r'\$\{[^}]+\}|\$\[[^\]]+\]', text))


def substitute_expressions(text: str, context: Dict[str, Any], expected_result_type: str = "json", step_info: Dict[str, Any] = None) -> str:
    """
    Replace all expressions in text with their evaluated values.
    
    Args:
        text: Text containing expressions
        context: Evaluation context
        expected_result_type: Type for expression results  
        step_info: Step info for error reporting
        
    Returns:
        Text with expressions replaced by their string representations
    """
    if not isinstance(text, str) or not contains_expressions(text):
        return text
    
    def replace_expr(match):
        expr = match.group(0)
        try:
            result = evaluate_expression(expr, context, expected_result_type, step_info)
            # Use JSON representation for complex objects instead of str()
            if isinstance(result, (dict, list)):
                return json.dumps(result, ensure_ascii=False)
            return str(result) if result is not None else ""
        except Exception as e:
            logger.error(f"Failed to substitute expression '{expr}': {e}")
            raise
    
    # Replace both ${...} and $[...] patterns
    pattern = r'\$\{[^}]+\}|\$\[[^\]]+\]'
    return re.sub(pattern, replace_expr, text)
