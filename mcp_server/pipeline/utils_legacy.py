"""
Legacy pipeline utilities - DEPRECATED

This module provides backward compatibility for existing code.
New code should use expressions.py directly.
"""

# Import new expression system for backward compatibility
from .expressions import (
    evaluate_expression, 
    substitute_expressions, 
    contains_expressions,
    ExpressionEvaluationError
)

import logging

logger = logging.getLogger('mcp_server.pipeline.utils_legacy')

# Legacy compatibility classes - these just wrap the new system
class ExpressionHandler:
    """DEPRECATED: Use expressions.evaluate_expression() instead."""
    
    @classmethod
    def contains_expressions(cls, text):
        return contains_expressions(text)
    
    def evaluate_if_expression(self, text, variables, evaluator=None):
        if contains_expressions(text):
            return evaluate_expression(text, variables, "python")
        return text


class ExpressionEvaluator:
    """DEPRECATED: Use expressions.evaluate_expression() instead."""
    
    def evaluate(self, expression, variables):
        return evaluate_expression(expression, variables, "python")
    
    def evaluate_if_expression(self, text, variables):
        handler = ExpressionHandler()
        return handler.evaluate_if_expression(text, variables, self)


class VariableSubstitutor:
    """DEPRECATED: Use expressions.substitute_expressions() instead."""
    
    def substitute(self, text, variables):
        return substitute_expressions(text, variables, "json")
    
    def substitute_recursive(self, obj, variables):
        if isinstance(obj, str):
            return self.substitute(obj, variables)
        elif isinstance(obj, dict):
            return {key: self.substitute_recursive(value, variables) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self.substitute_recursive(item, variables) for item in obj]
        else:
            return obj
