import mcp.types as types
import json
import re
import math
import operator

async def tool_info() -> dict:
    """Returns information about the lng_math_calculator tool."""
    return {
        "description": """Performs mathematical calculations and operations.

**Parameters:**
- `expression` (string, required): Mathematical expression for calculation.

**Supported operations:**
- Basic arithmetic operations: +, -, *, /
- Power: ** or ^
- Parentheses for grouping: ()
- Mathematical functions: sin, cos, tan, log, ln, sqrt, abs
- Constants: pi, e
- Integer division: //
- Modulo: %

**Usage examples:**
- "2 + 3 * 4" → 14
- "sqrt(16) + 2^3" → 12
- "sin(pi/2)" → 1
- "(10 + 5) * 2" → 30
- "log(100)" → 2

This tool is useful for performing complex mathematical calculations.""",
        "schema": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "Mathematical expression for calculation"
                }
            },
            "required": ["expression"]
        }
    }

async def run_tool(name: str, parameters: dict) -> list[types.Content]:
    """Performs mathematical calculations."""
    try:
        # Get the expression
        expression = parameters.get("expression", "")
        
        if not expression:
            return [types.TextContent(type="text", text='{"error": "No mathematical expression provided for calculation."}')]
        
        # Clean and prepare the expression
        cleaned_expression = clean_expression(expression)
        
        # Calculate the result
        result = safe_eval(cleaned_expression)
        
        # Create JSON result
        result_dict = {
            "originalExpression": expression,
            "cleanedExpression": cleaned_expression,
            "result": result,
            "resultType": type(result).__name__
        }
        
        # Convert to JSON string
        json_result = json.dumps(result_dict, indent=2, ensure_ascii=False)
        
        return [types.TextContent(type="text", text=json_result)]
        
    except Exception as e:
        error_result = {
            "error": f"Error during calculation: {str(e)}",
            "originalExpression": parameters.get("expression", "")
        }
        return [types.TextContent(type="text", text=json.dumps(error_result, ensure_ascii=False))]

def clean_expression(expr: str) -> str:
    """Cleans and prepares the mathematical expression."""
    # Remove extra spaces
    expr = expr.strip()
    
    # Replace ^ with **
    expr = expr.replace('^', '**')
    
    # Replace constants
    expr = expr.replace('pi', str(math.pi))
    expr = expr.replace('e', str(math.e))
    # Replace mathematical functions
    math_functions = {
        'sin': 'math.sin',
        'cos': 'math.cos',
        'tan': 'math.tan',
        'log': 'math.log10',
        'ln': 'math.log',
        'sqrt': 'math.sqrt',
        'abs': 'abs',
        'floor': 'math.floor',
        'ceil': 'math.ceil',
        'round': 'round'
    }
    
    for func, replacement in math_functions.items():
        # Use regular expressions for precise function replacement
        pattern = r'\b' + func + r'\b'
        expr = re.sub(pattern, replacement, expr)
    
    return expr

def safe_eval(expr: str):
    """Safely evaluates a mathematical expression."""
    # List of allowed names
    allowed_names = {
        '__builtins__': {},
        'math': math,
        'abs': abs,
        'round': round,
        'min': min,
        'max': max,
        'sum': sum,
        'pow': pow
    }
    # List of forbidden symbols/functions
    forbidden = ['import', '__', 'exec', 'eval', 'open', 'file', 'input', 'raw_input']
    
    # Check for forbidden elements
    for item in forbidden:
        if item in expr:
            raise ValueError(f"Forbidden element '{item}' in expression")
    
    try:
        # Safely evaluate the expression
        result = eval(expr, allowed_names, {})
        # Check result type
        if isinstance(result, (int, float, complex)):
            # Round float to reasonable number of decimal places
            if isinstance(result, float):
                return round(result, 10)
            return result
        else:
            raise ValueError(f"Unexpected result type: {type(result)}")
            
    except ZeroDivisionError:
        raise ValueError("Division by zero")    
    except OverflowError:
        raise ValueError("Result too large")
    except ValueError as e:
        raise ValueError(f"Value error: {str(e)}")
    except Exception as e:
        raise ValueError(f"Calculation error: {str(e)}")
