import sys
import os
print(f"Python executable: {sys.executable}")
print(f"Python version: {sys.version}")
print(f"Current directory: {os.getcwd()}")

# Add the project root to the Python path to ensure imports work correctly
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import anyio
import click
import mcp.types as types
from mcp.server.lowlevel import Server
from dotenv import load_dotenv
import os.path
import mcp_server.tools.tool_registry as tools
from mcp_server.state_manager import state_manager

# Initialize the shared state with default values if needed
# Example: state_manager.set("app_start_time", datetime.now().isoformat())

tools.register_tools()

@click.command()
@click.option("--port", default=8000, help="Port to listen on for SSE")
@click.option(
    "--transport",
    type=click.Choice(["stdio", "sse"]),
    default="stdio",
    help="Transport type",
)
def main(port: int, transport: str) -> int:
    app = Server("langchain-prompt-server")

    @app.call_tool()
    async def process_tool(name: str, arguments: dict) -> list[types.Content]:
        return await tools.run_tool(name, arguments)        
            
    @app.list_tools()
    async def list_tools() -> list[types.Tool]:
        tool_info_list = await tools.tools_info()
        return [
            types.Tool(
                name=tool["name"],
                description=tool["description"],
                inputSchema=tool["schema"]
            ) for tool in tool_info_list
        ]

    if transport == "sse":
        from mcp.server.sse import SseServerTransport
        from starlette.applications import Starlette
        from starlette.responses import Response
        from starlette.routing import Mount, Route

        sse = SseServerTransport("/messages/")

        async def handle_sse(request):
            async with sse.connect_sse(
                request.scope, request.receive, request._send
            ) as streams:
                await app.run(
                    streams[0], streams[1], app.create_initialization_options()
                )
            return Response()

        starlette_app = Starlette(
            debug=True,
            routes=[
                Route("/sse", endpoint=handle_sse, methods=["GET"]),
                Mount("/messages/", app=sse.handle_post_message),
            ],
        )

        import uvicorn
        uvicorn.run(starlette_app, host="127.0.0.1", port=port)
    else:
        from mcp.server.stdio import stdio_server

        async def arun():
            async with stdio_server() as streams:
                await app.run(
                    streams[0], streams[1], app.create_initialization_options()
                )

        anyio.run(arun)

    return 0


if __name__ == "__main__":
    main()
