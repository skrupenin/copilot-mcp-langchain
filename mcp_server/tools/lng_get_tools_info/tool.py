import mcp.types as types
import mcp_server.tools.tool_registry as tools

async def tool_info() -> dict:
    """Returns information about the lng_save_prompt_template tool."""
    return {
        "name": "lng_get_tools_info",
        "description": """Returns information about the available langchain tools.

**Parameters:**
- None required

**Example Usage:**
- Simply request this tool without any parameters
- The system will return documentation about all available tools

This tool helps you understand the capabilities of all available tools in the system.""",
        "schema": {
            "type": "object",
            "description": "No parameters required",
        }
    }

async def run_tool(name: str, parameters: dict) -> list[types.Content]:
    """Returns information about the available langchain tools."""
        
    try:
        # Format the tools information as markdown using the global tool_definitions
        markdown_content = "# Langchain MCP Tools\n\n"
        markdown_content += "This document describes the tools available in the Langchain Model Context Protocol (MCP) implementation.\n\n"
        markdown_content += "## Available Tools\n\n"
        
        # Add each tool's information
        tool_info_list = await tools.tools_info()
        for i, tool in enumerate(tool_info_list, 1):
            markdown_content += f"### {i}. `{tool['name']}`\n\n"
            markdown_content += f"{tool['description']}\n\n"
        
        # Add section about how tools work together
        markdown_content += "## How MCP Tools Work Together\n\n"
        markdown_content += "1. First, you save a template using the `lng_save_prompt_template` tool\n"
        markdown_content += "2. The template contains placeholders in curly braces, like {name} or {topic}\n"
        markdown_content += "3. Later, you use the `lng_use_prompt_template` tool with specific values for those placeholders\n"
        markdown_content += "4. The system fills in the template with your values and processes the completed prompt\n"
        markdown_content += "5. If you need information about available tools, you can use the `lng_get_tools_info` tool\n\n"
        markdown_content += "This workflow allows for flexible prompt engineering while maintaining a clean separation between the prompt structure and the specific content."
        
        return [types.TextContent(type="text", text=markdown_content)]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Error retrieving tools information: {str(e)}")]
