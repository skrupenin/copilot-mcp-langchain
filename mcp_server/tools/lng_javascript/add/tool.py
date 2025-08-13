import mcp.types as types
import json
from mcp_server.file_state_manager import FileStateManager

# Create file state manager for JavaScript functions
javascript_manager = FileStateManager("mcp_server/config/javascript")

async def tool_info() -> dict:
    """Returns information about the lng_javascript_add tool."""
    return {
        "description": """Save JavaScript functions to filesystem for later execution.

**Parameters:**
- `function_name` (string, required): Name of the function (must match function declaration)
- `function_code` (string, required): JavaScript function code (must be declared function, not arrow function)

**Function Requirements:**
- Must be declared functions (not arrow functions)
- Function name must match the function_name parameter
- Functions can contain any JavaScript code including async/await
- Functions are stored in mcp_server/config/javascript/ directory with .js extension

**Example:**
```json
{
    "function_name": "calculateSum", 
    "function_code": "function calculateSum(params) { return params.a + params.b; }"
}
```

**Output:**
- Success: JSON object with save confirmation
- Error: JSON object with error message""",
        "schema": {
            "type": "object",
            "properties": {
                "function_name": {
                    "type": "string", 
                    "description": "Name of the JavaScript function"
                },
                "function_code": {
                    "type": "string",
                    "description": "JavaScript function code"
                }
            },
            "required": ["function_name", "function_code"]
        }
    }

async def run_tool(name: str, parameters: dict) -> list[types.Content]:
    """Save JavaScript function to filesystem."""
    try:
        function_name = parameters.get("function_name", "")
        function_code = parameters.get("function_code", "")
        
        if not function_name:
            return [types.TextContent(type="text", text=json.dumps({"error": "function_name is required"}))]
        
        if not function_code:
            return [types.TextContent(type="text", text=json.dumps({"error": "function_code is required"}))]
        
        # Validate that function_code contains a function declaration with the correct name
        if f"function {function_name}" not in function_code:
            return [types.TextContent(type="text", text=json.dumps({
                "error": f"Function code must contain a declared function named {function_name}. Arrow functions are not allowed."
            }))]
        
        # Save the function to the filesystem
        javascript_manager.set(function_name, function_code, extension=".js")
        
        result = {
            "message": f"Function '{function_name}' saved successfully",
            "function_name": function_name,
            "storage_path": f"mcp_server/config/javascript/{function_name}.js"
        }
        
        return [types.TextContent(type="text", text=json.dumps(result, indent=2, ensure_ascii=False))]
        
    except Exception as e:
        error_result = {"error": f"Error saving function: {str(e)}"}
        return [types.TextContent(type="text", text=json.dumps(error_result, ensure_ascii=False))]
