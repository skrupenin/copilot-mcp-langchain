import mcp.types as types
from mcp_server.state_manager import state_manager

async def tool_info() -> dict:
    """Returns information about the lng_save_prompt_template tool."""
    return {
        "name": "lng_save_prompt_template",
        "description": """Saves a prompt template for later use by the system.

**Parameters:**
- `template` (string, required): The prompt template to save with placeholders in {name} format

**Example Usage:**
- Create a template like "Tell me about {topic} in the style of {style}."
- The system saves this template for future use
- Placeholders like {topic} and {style} will be replaced with actual values when used

This tool is part of a workflow that allows for flexible prompt engineering while maintaining a clean separation between the prompt structure and the specific content.""",
        "schema": {
            "type": "object",
            "required": ["template"],
            "properties": {
                "template": {
                    "type": "string",
                    "description": "The prompt template to save (with placeholders in {name} format)",
                }
            },
        }
    }

async def run_tool(name: str, parameters: dict) -> list[types.Content]:
    """Saves a prompt template for later use."""
    template_text = parameters.get("template", None)
    if not template_text:
        return [types.TextContent(type="text", text="Error: 'template' parameter is required.")]
    
    try:
        state_manager.set("prompt_template", template_text)
        return [types.TextContent(type="text", text="Prompt template saved successfully.")]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Error saving prompt template: {str(e)}")]
