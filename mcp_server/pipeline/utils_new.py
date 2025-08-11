"""
Pipeline utilities with expression evaluation support.

DEPRECATED: This module is being replaced by expressions.py with strategy-based architecture.
Some functions are kept for backward compatibility.
"""

import json
import re
import logging
from typing import Any, Dict, List

# Import new expression system
from .expressions import evaluate_expression, substitute_expressions, contains_expressions

logger = logging.getLogger('mcp_server.pipeline.utils')

# Check for PyMiniRacer availability (deprecated - moved to expressions.py)
try:
    import py_mini_racer
    JS_AVAILABLE = True
except ImportError:
    JS_AVAILABLE = False
    logger.warning("PyMiniRacer not available. Using new expression system fallback.")


class ExpressionHandler:
    """
    DEPRECATED: Use expressions.evaluate_expression() instead.
    
    Legacy expression handler for backward compatibility.
    """
    
    # Legacy constants
    EXPRESSION_PREFIX = "${"
    EXPRESSION_SUFFIX = "}"
    JS_PREFIX = "${"
    JS_SUFFIX = "}"  
    PY_PREFIX = "$["
    PY_SUFFIX = "]"
    
    @classmethod
    def contains_expressions(cls, text: str) -> bool:
        """DEPRECATED: Use expressions.contains_expressions() instead."""
        return contains_expressions(text)
    
    @classmethod
    def find_all_expressions(cls, text: str) -> List[str]:
        """Find all ${} and $[] expressions in text."""
        if not isinstance(text, str):
            return []
        pattern = r'\$\{[^}]+\}|\$\[[^\]]+\]'
        matches = re.findall(pattern, text)
        return matches
    
    @classmethod
    def extract_expression(cls, expression: str) -> str:
        """Extract clean expression content from wrapper."""
        if expression.startswith('${') and expression.endswith('}'):
            return expression[2:-1]
        elif expression.startswith('$[') and expression.endswith(']'):
            return expression[2:-1]
        return expression
    
    @classmethod 
    def is_js_expression(cls, expression: str) -> bool:
        """Check if expression uses JavaScript syntax."""
        return expression.startswith(cls.JS_PREFIX) and expression.endswith(cls.JS_SUFFIX)
    
    @classmethod
    def is_py_expression(cls, expression: str) -> bool:
        """Check if expression uses Python syntax."""
        return expression.startswith(cls.PY_PREFIX) and expression.endswith(cls.PY_SUFFIX)
    
    def evaluate_if_expression(self, text: str, variables: Dict[str, Any], evaluator=None) -> Any:
        """DEPRECATED: Use expressions.evaluate_expression() instead."""
        if self.contains_expressions(text):
            return evaluate_expression(text, variables, "python")
        return text


class ExpressionEvaluator:
    """
    DEPRECATED: Use expressions.evaluate_expression() instead.
    
    Legacy evaluator for backward compatibility.
    """
    
    def __init__(self):
        self.handler = ExpressionHandler()
        logger.warning("ExpressionEvaluator is deprecated. Use expressions.evaluate_expression() instead.")
    
    def evaluate(self, expression: str, variables: Dict[str, Any]) -> Any:
        """DEPRECATED: Use expressions.evaluate_expression() instead."""
        try:
            return evaluate_expression(expression, variables, "python")
        except Exception as e:
            logger.error(f"Legacy evaluation failed: {e}")
            # Fallback to old behavior
            return str(expression)
    
    def evaluate_if_expression(self, text: str, variables: Dict[str, Any]) -> Any:
        """DEPRECATED: Use expressions.evaluate_expression() instead."""
        return self.handler.evaluate_if_expression(text, variables, self)


class VariableSubstitutor:
    """
    DEPRECATED: Use expressions.substitute_expressions() instead.
    
    Legacy substitutor for backward compatibility.
    """
    
    def __init__(self):
        self.handler = ExpressionHandler()
        self.evaluator = ExpressionEvaluator()
        logger.warning("VariableSubstitutor is deprecated. Use expressions.substitute_expressions() instead.")
    
    def substitute(self, text: str, variables: Dict[str, Any]) -> str:
        """DEPRECATED: Use expressions.substitute_expressions() instead."""
        try:
            return substitute_expressions(text, variables, "json")
        except Exception as e:
            logger.error(f"Legacy substitution failed: {e}")
            return text
    
    def substitute_recursive(self, obj: Any, variables: Dict[str, Any]) -> Any:
        """
        DEPRECATED: Use expressions.substitute_expressions() instead.
        
        Recursively substitute expressions in nested data structures.
        """
        if isinstance(obj, str):
            return self.substitute(obj, variables)
        elif isinstance(obj, dict):
            return {key: self.substitute_recursive(value, variables) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self.substitute_recursive(item, variables) for item in obj]
        else:
            return obj
