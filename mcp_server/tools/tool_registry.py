import os
from importlib import import_module
from pathlib import Path

tool_definitions = []

def register_tool(name: str, module_path: str):
    """Registers a tool with its name and module path."""
    tool_definitions.append({"name": name, "module_path": module_path})

async def get_tool_info(name: str):
    """Retrieves the tool information based on the tool name."""
    for tool in tool_definitions:
        if tool["name"] == name:
            module = import_module(tool["module_path"])
            return await module.tool_info() 
    raise ValueError(f"Tool '{name}' not found.")

async def tools_info():
    """Returns information about all registered tools."""
    results = []
    for tool in tool_definitions:
        info = await get_tool_info(tool["name"])
        results.append(info)
    return results

def register_tools():
    """Registers all tools in the project by automatically scanning the tools directory."""
    # Get the directory where this file is located
    current_dir = Path(os.path.dirname(os.path.abspath(__file__)))
    
    # Scan the directory for tool folders
    for item in current_dir.iterdir():
        # Check if the item is a directory and starts with 'lng_'
        if item.is_dir() and item.name.startswith('lng_'):
            # Check if there's a tool.py file in the directory
            tool_file = item / 'tool.py'
            if tool_file.exists():
                tool_name = item.name
                module_path = f"mcp_server.tools.{tool_name}.tool"
                register_tool(tool_name, module_path)
                print(f"Registered tool: {tool_name}")
    
async def run_tool(name: str, arguments: dict) -> list:
    """Runs the specified tool with the provided arguments."""
    for tool in tool_definitions:
        if tool["name"] == name:
            module = import_module(tool["module_path"])
            return await module.run_tool(name, arguments)
    raise ValueError(f"Tool '{name}' not found.")

register_tools()