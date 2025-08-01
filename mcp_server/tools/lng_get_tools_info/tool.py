import mcp.types as types
import mcp_server.tools.tool_registry as tools

async def tool_info() -> dict:
    """Returns information about the lng_save_prompt_template tool."""
    return {
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
        
        return [types.TextContent(type="text", text=markdown_content)]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Error retrieving tools information: {str(e)}")]