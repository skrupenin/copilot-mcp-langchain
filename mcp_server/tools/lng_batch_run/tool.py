import mcp.types as types
import json
import re
import logging
from typing import Any, Dict, List
from mcp_server.tools.tool_registry import run_tool as execute_tool

logger = logging.getLogger('mcp_server.tools.lng_batch_run')

async def tool_info() -> dict:
    return {
        "description": """Executes a batch pipeline of tool calls with variable substitution using JavaScript expressions.

**Pipeline Structure:**
```json
{
  "pipeline": [
    {
      "tool": "tool_name",
      "params": {
        "param1": "${variable_name}",
        "param2": "${variable_name.property || 'default'}"
      },
      "output": "variable_name"
    }
  ],
  "final_result": "${last_variable || 'ok'}"
}
```

**Features:**
• Sequential tool execution with variable passing
• JavaScript expressions inside ${} for data manipulation
• JSON parsing for structured responses, fallback to string
• Error handling with context preservation
• Flexible final result calculation

**Variable Substitution:**
• `${variable}` - Direct variable value
• `${variable.property}` - Object property access
• `${variable || 'default'}` - Fallback values
• `${variable ? value1 : value2}` - Conditional expressions
• `${JSON.stringify(variable)}` - JSON serialization

**Example Usage:**
1. Get clipboard → Process with LLM → Set clipboard back
2. Chain multiple data transformations
3. Conditional logic based on previous results

**Error Handling:**
Returns error details with failed tool name and variable context when any step fails.""",
        "schema": {
            "type": "object",
            "properties": {
                "pipeline": {
                    "type": "array",
                    "description": "Array of pipeline steps with tools, parameters, and variable mappings",
                    "items": {
                        "type": "object",
                        "properties": {
                            "tool": {
                                "type": "string",
                                "description": "Name of the tool to execute"
                            },
                            "params": {
                                "type": "object",
                                "description": "Parameters to pass to the tool"
                            },
                            "output": {
                                "type": "string",
                                "description": "Variable name to store the tool result"
                            }
                        },
                        "required": ["tool", "params"]
                    }
                },
                "final_result": {
                    "type": "string",
                    "description": "Expression or value for the final result (default: 'ok')"
                }
            },
            "required": ["pipeline"]
        }
    }

def evaluate_js_expression(expression: str, variables: Dict[str, Any]) -> Any:
    """
    Evaluate a JavaScript-like expression using Python eval with available variables.
    
    Args:
        expression: JavaScript expression to evaluate
        variables: Dictionary of available variables
        
    Returns:
        Evaluated result
    """
    try:
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
            # Add more JavaScript-like functions as needed
        }
        
        # Simple replacements for JavaScript syntax
        py_expression = expression
        
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

def substitute_variables(text: str, variables: Dict[str, Any]) -> str:
    """
    Replace ${expression} patterns in text with evaluated JavaScript expressions.
    
    Args:
        text: Text containing ${} patterns
        variables: Dictionary of available variables
        
    Returns:
        Text with substituted values
    """
    def replace_expression(match):
        expression = match.group(1)
        try:
            result = evaluate_js_expression(expression, variables)
            return str(result) if result is not None else ""
        except Exception as e:
            logger.error(f"Error substituting expression '${{{expression}}}': {e}")
            raise
    
    # Find and replace all ${expression} patterns
    pattern = r'\$\{([^}]+)\}'
    return re.sub(pattern, replace_expression, text)

def parse_tool_response(response: List[types.Content]) -> Any:
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

async def run_tool(name: str, arguments: dict) -> list[types.Content]:
    """Execute a batch pipeline of tool calls with variable substitution."""
    
    try:
        # Get pipeline configuration directly as object
        pipeline_steps = arguments.get("pipeline", [])
        final_result_expr = arguments.get("final_result", "ok")
        
        if not pipeline_steps:
            return [types.TextContent(
                type="text", 
                text=json.dumps({
                    "success": False,
                    "error": "Pipeline must contain at least one step",
                    "context": {}
                }, ensure_ascii=False, indent=2)
            )]
        
        if not isinstance(pipeline_steps, list):
            return [types.TextContent(
                type="text", 
                text=json.dumps({
                    "success": False,
                    "error": "Pipeline must be an array of steps",
                    "context": {}
                }, ensure_ascii=False, indent=2)
            )]
        
        # Execute pipeline steps
        variables = {}
        current_step = 0
        
        for step_index, step in enumerate(pipeline_steps):
            current_step = step_index + 1
            
            # Get step configuration
            tool_name = step.get("tool", "")
            tool_params = step.get("params", {})
            output_var = step.get("output")
            
            if not tool_name:
                return [types.TextContent(
                    type="text", 
                    text=json.dumps({
                        "success": False,
                        "error": f"Step {current_step}: tool name is required",
                        "step": current_step,
                        "tool": tool_name,
                        "context": variables
                    }, ensure_ascii=False, indent=2)
                )]
            
            logger.info(f"Executing step {current_step}: {tool_name}")
            
            try:
                # Substitute variables in parameters
                substituted_params = {}
                for param_name, param_value in tool_params.items():
                    if isinstance(param_value, str):
                        substituted_params[param_name] = substitute_variables(param_value, variables)
                    else:
                        substituted_params[param_name] = param_value
                
                logger.info(f"Step {current_step} params after substitution: {substituted_params}")
                
                # Execute tool
                tool_response = await execute_tool(tool_name, substituted_params)
                
                logger.info(f"Step {current_step} ({tool_name}) raw response: {tool_response}")
                
                # Parse response
                parsed_response = parse_tool_response(tool_response)
                
                logger.info(f"Step {current_step} ({tool_name}) parsed response: {parsed_response}")
                
                # Store result in variable if output is specified
                if output_var:
                    variables[output_var] = parsed_response
                    logger.info(f"Step {current_step} stored result in variable '{output_var}': {type(parsed_response).__name__}")
                
            except Exception as e:
                logger.error(f"Error executing step {current_step} ({tool_name}): {e}")
                return [types.TextContent(
                    type="text", 
                    text=json.dumps({
                        "success": False,
                        "error": f"Step {current_step} failed: {str(e)}",
                        "step": current_step,
                        "tool": tool_name,
                        "context": variables
                    }, ensure_ascii=False, indent=2)
                )]
        
        # Calculate final result
        try:
            if isinstance(final_result_expr, str) and "${" in final_result_expr:
                final_result = substitute_variables(final_result_expr, variables)
            else:
                final_result = final_result_expr
        except Exception as e:
            logger.error(f"Error calculating final result: {e}")
            return [types.TextContent(
                type="text", 
                text=json.dumps({
                    "success": False,
                    "error": f"Final result calculation failed: {str(e)}",
                    "context": variables
                }, ensure_ascii=False, indent=2)
            )]
        
        # Return success result
        return [types.TextContent(
            type="text", 
            text=json.dumps({
                "success": True,
                "result": final_result,
                "steps_executed": len(pipeline_steps),
                "context": variables
            }, ensure_ascii=False, indent=2)
        )]
        
    except Exception as e:
        logger.error(f"Unexpected error in lng_batch_run: {e}")
        return [types.TextContent(
            type="text", 
            text=json.dumps({
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "context": {}
            }, ensure_ascii=False, indent=2)
        )]
