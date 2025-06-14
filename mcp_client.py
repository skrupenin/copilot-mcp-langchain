import sys
import os
import json  # Added json module for pretty printing
print(f"Python executable: {sys.executable}")
print(f"Python version: {sys.version}")
print(f"Current directory: {os.getcwd()}")
import asyncio
from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

# Helper function to safely convert objects to JSON-serializable dictionaries
def to_json_serializable(obj):
    """Convert an object to a JSON-serializable form without using deprecated methods."""
    if hasattr(obj, "model_dump"):
        # Preferred method for Pydantic v2+
        return obj.model_dump()
    else:
        # Try various fallback methods
        try:
            # For objects with __dict__ attribute
            return vars(obj)
        except (TypeError, AttributeError):
            # For basic JSON-serializable objects
            return obj

async def main():
    try:
        # Connect to the MCP server
        print("Attempting to connect to server...")
        async with stdio_client(
            StdioServerParameters(command="python", args=["-m", "mcp_server.server"])
        ) as (read, write):
            print("Connection established!")
            async with ClientSession(read, write) as session:
                print("Initializing session...")
                await session.initialize()
                print("Session initialized!")
                
                # List available tools
                print("Requesting tools list...")
                tools = await session.list_tools()
                print("Available tools:")
                tools_dict = to_json_serializable(tools)
                
                if tools_dict is not None:
                    print(json.dumps(tools_dict, indent=4))
                
                # Save a prompt template
                print("\nSaving a prompt template...")
                template = "Tell me about {topic} in the style of {style}."
                save_result = await session.call_tool("lng_save_prompt_template", {"template": template})
                print("Prompt template saved:")
                save_dict = to_json_serializable(save_result)
                print(json.dumps(save_dict, indent=4))
                
                # Use the saved prompt template
                print("\nUsing the saved prompt template...")
                parameters = {"topic": "artificial intelligence", "style": "a pirate"}
                use_result = await session.call_tool("lng_use_prompt_template", parameters)
                print("Generated response:")
                use_dict = to_json_serializable(use_result)
                print(json.dumps(use_dict, indent=4))
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("Running main function...")
    asyncio.run(main())
    print("Main function completed.")
