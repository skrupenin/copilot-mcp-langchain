from importlib import import_module

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
    """Registers all tools in the project."""
    register_tool("lng_save_prompt_template", "mcp_server.tools.lng_save_prompt_template.tool")
    register_tool("lng_use_prompt_template", "mcp_server.tools.lng_use_prompt_template.tool")
    register_tool("lng_get_tools_info", "mcp_server.tools.lng_get_tools_info.tool")

async def run_tool(name: str, arguments: dict) -> list:
    """Runs the specified tool with the provided arguments."""
    for tool in tool_definitions:
        if tool["name"] == name:
            module = import_module(tool["module_path"])
            return await module.run_tool(name, arguments)
    raise ValueError(f"Tool '{name}' not found.")