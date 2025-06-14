import sys
import os
print(f"Python executable: {sys.executable}")
print(f"Python version: {sys.version}")
print(f"Current directory: {os.getcwd()}")
import asyncio
from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

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
                
                # List available tools - just print raw list to avoid attribute errors
                print("Requesting tools list...")
                tools = await session.list_tools()
                print("Available tools:")
                print(tools)
                
                # Save a prompt template
                print("\nSaving a prompt template...")
                template = "Tell me about {topic} in the style of {style}."
                save_result = await session.call_tool("save_prompt", {"template": template})
                print("Prompt template saved:")
                print(save_result)
                
                # Use the saved prompt template
                print("\nUsing the saved prompt template...")
                parameters = {"topic": "artificial intelligence", "style": "a pirate"}
                use_result = await session.call_tool("use_prompt", parameters)
                print("Generated response:")
                print(use_result)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("Running main function...")
    asyncio.run(main())
    print("Main function completed.")
