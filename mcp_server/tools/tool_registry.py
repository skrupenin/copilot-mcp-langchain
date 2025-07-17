import os
import logging
import traceback
from importlib import import_module
from pathlib import Path

logger = logging.getLogger('mcp_server.tools')

tool_definitions = []

def register_tool(name: str, module_path: str):
    """Registers a tool with its name and module path."""
    tool_definitions.append({"name": name, "module_path": module_path})

async def get_tool_info(name: str):
    """Retrieves the tool information based on the tool name."""
    try:
        for tool in tool_definitions:
            if tool["name"] == name:
                logger.info(f"Getting info for tool: {name}, module path: {tool['module_path']}")
                try:
                    module = import_module(tool["module_path"])
                    logger.info(f"Successfully imported module for tool: {name}")
                    tool_info = await module.tool_info()
                    logger.info(f"Successfully retrieved info for tool: {name}")
                    return tool_info
                except Exception as e:
                    logger.error(f"Error getting info for tool {name}: {e}")
                    logger.error(traceback.format_exc())
                    # Return a minimal tool info to prevent breaking the entire list
                    return {
                        "name": name,
                        "description": f"Error loading tool: {str(e)}",
                        "schema": {"type": "object", "properties": {}}
                    }
        logger.warning(f"Tool '{name}' not found.")
        raise ValueError(f"Tool '{name}' not found.")
    except Exception as e:
        logger.error(f"Unexpected error in get_tool_info for {name}: {e}")
        logger.error(traceback.format_exc())
        # Return a minimal tool info to prevent breaking the entire list
        return {
            "name": name,
            "description": f"Error loading tool: {str(e)}",
            "schema": {"type": "object", "properties": {}}
        }

async def tools_info():
    """Returns information about all registered tools."""
    logger.info(f"Retrieving info for {len(tool_definitions)} registered tools")
    results = []
    for tool in tool_definitions:
        try:
            logger.info(f"Getting info for tool: {tool['name']}")
            info = await get_tool_info(tool["name"])
            results.append(info)
            logger.info(f"Successfully added info for tool: {tool['name']}")
        except Exception as e:
            logger.error(f"Error processing tool {tool['name']}: {e}")
            logger.error(traceback.format_exc())
            # Add minimal info to not break the entire list
            results.append({
                "name": tool["name"],
                "description": f"Error loading tool: {str(e)}",
                "schema": {"type": "object", "properties": {}}
            })
    logger.info(f"Returning info for {len(results)} tools")
    return results

def register_tools():
    """Registers all tools in the project by automatically scanning the tools directory."""
    logger.info("Starting to register tools")
    
    # Get the directory where this file is located
    current_dir = Path(os.path.dirname(os.path.abspath(__file__)))
    logger.info(f"Scanning tools directory: {current_dir}")
    
    tool_count = 0
    # Scan the directory for tool folders
    for item in current_dir.iterdir():
        # Check if the item is a directory and starts with 'lng_'
        if item.is_dir() and item.name.startswith('lng_'):
            logger.info(f"Found potential tool directory: {item.name}")
            # Check if there's a tool.py file in the directory
            tool_file = item / 'tool.py'
            if tool_file.exists():
                tool_name = item.name
                module_path = f"mcp_server.tools.{tool_name}.tool"
                register_tool(tool_name, module_path)
                logger.info(f"Registered tool: {tool_name}")
                # Using logger instead of print
                tool_count += 1
            else:
                logger.warning(f"Directory {item.name} does not contain tool.py file")
    
    logger.info(f"Registered a total of {tool_count} tools")
    
async def run_tool(name: str, arguments: dict) -> list:
    """Runs the specified tool with the provided arguments."""
    logger.info(f"Running tool: {name} with arguments: {arguments}")
    
    try:
        for tool in tool_definitions:
            if tool["name"] == name:
                logger.info(f"Found tool {name}, importing module {tool['module_path']}")
                try:
                    module = import_module(tool["module_path"])
                    logger.info(f"Successfully imported module for tool: {name}")
                    result = await module.run_tool(name, arguments)
                    logger.info(f"Tool {name} executed successfully")
                    return result
                except Exception as e:
                    logger.error(f"Error running tool {name}: {e}")
                    logger.error(traceback.format_exc())
                    raise
        
        logger.warning(f"Tool '{name}' not found.")
        raise ValueError(f"Tool '{name}' not found.")
    except Exception as e:
        logger.error(f"Unexpected error in run_tool for {name}: {e}")
        logger.error(traceback.format_exc())
        raise

register_tools()