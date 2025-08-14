import mcp.types as types
import mcp_server.tools.tool_registry as tools

async def tool_info() -> dict:
    """Returns information about the lng_get_tools_info tool."""
    return {
        "description": """Returns detailed information about specific tools.

**Parameters:**
- `tools` (string, optional): Comma-separated list of tool names to get info for. If not provided, returns info about all tools.

**Example Usage:**
- Get info for specific tools: `{"tools": "lng_file_list,lng_file_read"}`
- Get info for single tool: `{"tools": "lng_file_list"}`
- Get info for all tools: `{}` (no parameters)

This tool helps you understand the capabilities, parameters, and usage examples of specific tools in the system.""",
        "schema": {
            "type": "object",
            "properties": {
                "tools": {
                    "type": "string",
                    "description": "Comma-separated list of tool names to get information for"
                }
            }
        }
    }

async def run_tool(name: str, parameters: dict) -> list[types.Content]:
    """Returns information about the available langchain tools."""
    
    tools_arg = parameters.get("tools", None)
    
    try:
        # Get all tools information
        tool_info_list = await tools.tools_info()
        
        # If specific tools requested, filter the results
        if tools_arg:
            requested_tools = [tool.strip() for tool in tools_arg.split(',')]
            filtered_tools = []
            missing_tools = []
            
            for tool_name in requested_tools:
                found = False
                for tool in tool_info_list:
                    if tool['name'] == tool_name:
                        filtered_tools.append(tool)
                        found = True
                        break
                if not found:
                    missing_tools.append(tool_name)
            
            # Build markdown for filtered tools
            markdown_content = f"# Langchain MCP Tools (Filtered: {len(filtered_tools)} of {len(requested_tools)} requested)\n\n"
            
            if missing_tools:
                markdown_content += f"**⚠️ Missing tools:** {', '.join(missing_tools)}\n\n"
            
            markdown_content += "This document describes the requested tools available in the Langchain Model Context Protocol (MCP) implementation.\n\n"
            markdown_content += "## Requested Tools\n\n"
            
            # Add each filtered tool's information
            for i, tool in enumerate(filtered_tools, 1):
                markdown_content += f"### {i}. `{tool['name']}`\n\n"
                markdown_content += f"{tool['description']}\n\n"
                
        else:
            # Show all tools
            markdown_content = "# Langchain MCP Tools\n\n"
            markdown_content += "This document describes the tools available in the Langchain Model Context Protocol (MCP) implementation.\n\n"
            markdown_content += f"## Available Tools (Total: {len(tool_info_list)})\n\n"
            
            # Add each tool's information
            for i, tool in enumerate(tool_info_list, 1):
                markdown_content += f"### {i}. `{tool['name']}`\n\n"
                markdown_content += f"{tool['description']}\n\n"
        
        return [types.TextContent(type="text", text=markdown_content)]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Error retrieving tools information: {str(e)}")]