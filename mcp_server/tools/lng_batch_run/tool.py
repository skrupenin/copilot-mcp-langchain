import mcp.types as types
import json
import logging
from typing import Any, Dict, List
from mcp_server.tools.tool_registry import run_tool as execute_tool
from mcp_server.pipeline import execute_pipeline

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

async def run_tool(name: str, arguments: dict) -> list[types.Content]:
    """Execute a batch pipeline of tool calls with variable substitution."""
    
    try:
        # Execute pipeline using the new pipeline module
        result = await execute_pipeline(arguments, execute_tool)
        
        # Return result in the expected format
        return [types.TextContent(
            type="text", 
            text=json.dumps(result.to_dict(), ensure_ascii=False, indent=2)
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
