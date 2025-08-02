"""
Utility classes for pipeline execution.

This module contains helper classes for expression evaluation,
variable substitution, response parsing, and other utilities.
"""

import json
import re
import logging
from typing import Any, Dict, List

import mcp.types as types

logger = logging.getLogger('mcp_server.pipeline.utils')


class ExpressionHandler:
    """
    Universal handler for working with ${} expressions.
    
    Provides methods to detect, extract, and evaluate expressions
    in a consistent way across the entire pipeline system.
    """
    
    EXPRESSION_PREFIX = "${"
    EXPRESSION_SUFFIX = "}"
    
    @classmethod
    def is_expression(cls, text: str) -> bool:
        """Check if text contains a ${} expression."""
        if not isinstance(text, str):
            return False
        return text.startswith(cls.EXPRESSION_PREFIX) and text.endswith(cls.EXPRESSION_SUFFIX)
    
    @classmethod
    def extract_expression(cls, text: str) -> str:
        """Extract the inner expression from ${expression} format."""
        if not cls.is_expression(text):
            return text
        return text[len(cls.EXPRESSION_PREFIX):-len(cls.EXPRESSION_SUFFIX)].strip()
    
    @classmethod
    def wrap_expression(cls, expression: str) -> str:
        """Wrap expression in ${} format."""
        if cls.is_expression(expression):
            return expression
        return f"{cls.EXPRESSION_PREFIX}{expression}{cls.EXPRESSION_SUFFIX}"
    
    @classmethod
    def evaluate_if_expression(cls, text: str, variables: Dict[str, Any], evaluator: 'ExpressionEvaluator' = None) -> Any:
        """
        Evaluate text if it's an expression, otherwise return as-is.
        
        Args:
            text: Text that may be an expression
            variables: Variables for evaluation
            evaluator: Optional custom evaluator, creates default if None
            
        Returns:
            Evaluated result if expression, original text otherwise
        """
        if not cls.is_expression(text):
            return text
        
        if evaluator is None:
            evaluator = ExpressionEvaluator()
        
        expression = cls.extract_expression(text)
        return evaluator.evaluate(expression, variables)
    
    @classmethod
    def contains_expressions(cls, text: str) -> bool:
        """Check if text contains any ${} expressions (not just pure expression)."""
        if not isinstance(text, str):
            return False
        return cls.EXPRESSION_PREFIX in text and cls.EXPRESSION_SUFFIX in text
    
    @classmethod
    def find_all_expressions(cls, text: str) -> List[str]:
        """Find all ${} expressions in text."""
        if not isinstance(text, str):
            return []
        
        pattern = re.escape(cls.EXPRESSION_PREFIX) + r'([^}]+)' + re.escape(cls.EXPRESSION_SUFFIX)
        matches = re.findall(pattern, text)
        return matches


class ExpressionEvaluator:
    """Evaluates JavaScript-like expressions in Python context."""
    
    def __init__(self):
        self.handler = ExpressionHandler()
    
    def evaluate(self, expression: str, variables: Dict[str, Any]) -> Any:
        """
        Evaluate a JavaScript-like expression using Python eval with available variables.
        
        Args:
            expression: JavaScript expression to evaluate (can include ${} wrapper)
            variables: Dictionary of available variables
            
        Returns:
            Evaluated result
        """
        try:
            # Extract expression from ${} if present
            clean_expression = self.handler.extract_expression(expression)
            
            # If expression is a simple string without operators/brackets, handle specially
            if not any(char in clean_expression for char in ['(', ')', '[', ']', '+', '-', '*', '/', '>', '<', '=', '!', '&', '|', '?', ':']):
                # Check if it's a variable reference
                if clean_expression in variables:
                    return variables[clean_expression]
                # Check if it's a property access
                if '.' in clean_expression:
                    parts = clean_expression.split('.')
                    if parts[0] in variables:
                        obj = variables[parts[0]]
                        for part in parts[1:]:
                            if isinstance(obj, dict):
                                obj = obj.get(part)
                            else:
                                obj = getattr(obj, part, None) if hasattr(obj, part) else None
                        return obj
                # Return as literal string if no variables match
                return clean_expression
            
            # Create a safe evaluation context with variables and common functions
            eval_context = {
                **variables,
                'JSON': {
                    'stringify': lambda obj: json.dumps(obj, ensure_ascii=False),
                    'parse': lambda s: json.loads(s)
                },
                'String': str,
                'Number': float,
                'Boolean': bool,
                'len': len,
                'str': str,
                'int': int,
                'float': float,
                'bool': bool,
            }
            
            # Simple replacements for JavaScript syntax
            py_expression = clean_expression
            
            # Replace JavaScript null/undefined with Python None
            py_expression = re.sub(r'\bundefined\b', 'None', py_expression)
            py_expression = re.sub(r'\bnull\b', 'None', py_expression)
            
            # Replace JavaScript boolean literals
            py_expression = re.sub(r'\btrue\b', 'True', py_expression)
            py_expression = re.sub(r'\bfalse\b', 'False', py_expression)
            
            # Replace JavaScript || operator with Python or
            py_expression = re.sub(r'\|\|', ' or ', py_expression)
            
            # Replace JavaScript && operator with Python and
            py_expression = re.sub(r'&&', ' and ', py_expression)
            
            # Handle JSON.stringify calls
            py_expression = re.sub(r'JSON\.stringify\(([^)]+)\)', r'JSON["stringify"](\1)', py_expression)
            py_expression = re.sub(r'JSON\.parse\(([^)]+)\)', r'JSON["parse"](\1)', py_expression)
            
            # Handle JavaScript ternary operator (condition ? value1 : value2)
            # Convert to Python conditional expression (value1 if condition else value2)
            ternary_pattern = r'([^?]+)\s*\?\s*([^:]+)\s*:\s*(.+)'
            def replace_ternary(match):
                condition = match.group(1).strip()
                value1 = match.group(2).strip()
                value2 = match.group(3).strip()
                return f'({value1} if {condition} else {value2})'
            
            py_expression = re.sub(ternary_pattern, replace_ternary, py_expression)
            
            # Replace JavaScript property access with Python dict access for known variables
            for var_name in variables.keys():
                # Replace var.property with var.get("property") if var is a dict
                var_value = variables[var_name]
                if isinstance(var_value, dict):
                    # Use regex to replace property access
                    pattern = rf'\b{re.escape(var_name)}\.(\w+)'
                    py_expression = re.sub(pattern, rf'{var_name}.get("\1")', py_expression)
            
            result = eval(py_expression, {"__builtins__": {}}, eval_context)
            return result
        except Exception as e:
            logger.error(f"Error evaluating JavaScript expression '{expression}': {e}")
            raise ValueError(f"JavaScript evaluation error: {str(e)}")
    
    def evaluate_if_expression(self, text: str, variables: Dict[str, Any]) -> Any:
        """Convenience method using ExpressionHandler."""
        return self.handler.evaluate_if_expression(text, variables, self)


class VariableSubstitutor:
    """Handles variable substitution in strings."""
    
    def __init__(self):
        self.handler = ExpressionHandler()
        self.evaluator = ExpressionEvaluator()
    
    def substitute(self, text: str, variables: Dict[str, Any]) -> str:
        """
        Replace ${expression} patterns in text with evaluated JavaScript expressions.
        
        Args:
            text: Text containing ${} patterns
            variables: Dictionary of available variables
            
        Returns:
            Text with substituted values
        """
        if not isinstance(text, str):
            return text
        
        if not self.handler.contains_expressions(text):
            return text
            
        def replace_expression(match):
            expression = match.group(1)
            try:
                result = self.evaluator.evaluate(expression, variables)
                return str(result) if result is not None else ""
            except Exception as e:
                logger.error(f"Error substituting expression '${{{expression}}}': {e}")
                raise
        
        # Find and replace all ${expression} patterns
        pattern = r'\$\{([^}]+)\}'
        return re.sub(pattern, replace_expression, text)
    
    def substitute_recursive(self, obj: Any, variables: Dict[str, Any]) -> Any:
        """Recursively substitute variables in nested structures."""
        if isinstance(obj, str):
            return self.substitute(obj, variables)
        elif isinstance(obj, dict):
            return {k: self.substitute_recursive(v, variables) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self.substitute_recursive(item, variables) for item in obj]
        else:
            return obj


class ResponseParser:
    """Parses tool responses and converts them to appropriate format."""
    
    @staticmethod
    def parse(response: List[types.Content]) -> Any:
        """
        Parse tool response and try to convert to JSON if possible.
        
        Args:
            response: Tool response content list
            
        Returns:
            Parsed JSON object or original string
        """
        if not response:
            return ""
        
        # Get the text content from the first response item
        text_content = ""
        for content in response:
            if isinstance(content, types.TextContent):
                text_content = content.text
                break
        
        if not text_content:
            return ""
        
        # Try to parse as JSON
        try:
            return json.loads(text_content)
        except (json.JSONDecodeError, TypeError):
            # If not valid JSON, return as string
            return text_content


# Export all utilities
__all__ = [
    'ExpressionHandler',
    'ExpressionEvaluator',
    'VariableSubstitutor',
    'ResponseParser'
]
