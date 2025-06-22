# filepath: c:\Java\CopipotTraining\hello-langchain\mcp_server\server.py
import sys
import os
import logging
import traceback

# logging configuration
# Create a file logger instead of outputting to stdout, so as not to interfere with the MCP protocol
log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mcp_server.log')
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, mode='w', encoding='utf-8')
    ]
)
logger = logging.getLogger('mcp_server')

logger.info(f"Python executable: {sys.executable}")
logger.info(f"Python version: {sys.version}")
logger.info(f"Current directory: {os.getcwd()}")

# Add the project root to the Python path to ensure imports work correctly
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
logger.info(f"Added to sys.path: {project_root}")

try:
    import anyio
    import click
    import mcp.types as types
    from mcp.server.lowlevel import Server
    from dotenv import load_dotenv
    import os.path
    import mcp_server.tools.tool_registry as tools
    from mcp_server.state_manager import state_manager
    logger.info("All modules imported successfully")
except Exception as e:
    logger.error(f"Error importing modules: {e}")
    logger.error(traceback.format_exc())
    raise

# Importing problematic libraries early to catch any issues before starting the server
try:
    logger.info("Attempting to pre-import problematic libraries")
       
    logger.info("Importing FAISS")
    from mcp_server.tools.lng_rag_add_data.tool import problem_imports
    problem_imports()
    logger.info("Successfully imported FAISS")
    
    logger.info("Pre-imports completed successfully")
except Exception as e:
    logger.error(f"Error during pre-imports: {e}")
    logger.exception("Stack trace:")

# Initialize the shared state with default values if needed
# Example: state_manager.set("app_start_time", datetime.now().isoformat())

@click.command()
@click.option("--port", default=8000, help="Port to listen on for SSE")
@click.option(
    "--transport",
    type=click.Choice(["stdio", "sse"]),
    default="stdio",
    help="Transport type",
)
def main(port: int, transport: str) -> int:
    logger.info(f"Starting MCP server with transport: {transport}, port: {port}")
    app = Server("langchain-prompt-server")
    logger.info("Server instance created")

    @app.call_tool()
    async def process_tool(name: str, arguments: dict) -> list[types.Content]:
        logger.info(f"Calling tool: {name} with arguments: {arguments}")
        try:
            result = await tools.run_tool(name, arguments)
            logger.info(f"Tool {name} completed successfully")
            return result
        except Exception as e:
            logger.error(f"Error running tool {name}: {e}")
            logger.error(traceback.format_exc())
            raise
            
    @app.list_tools()
    async def list_tools() -> list[types.Tool]:
        logger.info("Listing available tools")
        try:
            tool_info_list = await tools.tools_info()
            logger.info(f"Found {len(tool_info_list)} tools")
            return [
                types.Tool(
                    name=tool["name"],
                    description=tool["description"],
                    inputSchema=tool["schema"]
                ) for tool in tool_info_list
            ]
        except Exception as e:
            logger.error(f"Error listing tools: {e}")
            logger.error(traceback.format_exc())
            raise

    if transport == "sse":
        logger.info("Using SSE transport")
        try:
            from mcp.server.sse import SseServerTransport
            from starlette.applications import Starlette
            from starlette.responses import Response
            from starlette.routing import Mount, Route

            sse = SseServerTransport("/messages/")
            logger.info("SSE transport created")

            async def handle_sse(request):
                logger.info("SSE connection received")
                try:
                    async with sse.connect_sse(
                        request.scope, request.receive, request._send
                    ) as streams:
                        logger.info("SSE streams created, running app")
                        await app.run(
                            streams[0], streams[1], app.create_initialization_options()
                        )
                    logger.info("App run completed for SSE connection")
                    return Response()
                except Exception as e:
                    logger.error(f"Error in SSE handler: {e}")
                    logger.error(traceback.format_exc())
                    raise

            starlette_app = Starlette(
                debug=True,
                routes=[
                    Route("/sse", endpoint=handle_sse, methods=["GET"]),
                    Mount("/messages/", app=sse.handle_post_message),
                ],
            )
            logger.info("Starlette app created with routes")

            import uvicorn
            logger.info(f"Starting Uvicorn server on 127.0.0.1:{port}")
            uvicorn.run(starlette_app, host="127.0.0.1", port=port)
        except Exception as e:
            logger.error(f"Error in SSE setup: {e}")
            logger.error(traceback.format_exc())
            raise
    else:
        logger.info("Using stdio transport")
        try:
            from mcp.server.stdio import stdio_server

            async def arun():
                logger.info("Setting up stdio streams")
                try:
                    async with stdio_server() as streams:
                        logger.info("Stdio streams created, running app")
                        await app.run(
                            streams[0], streams[1], app.create_initialization_options()
                        )
                        logger.info("App run completed for stdio connection")
                except Exception as e:
                    logger.error(f"Error in stdio handler: {e}")
                    logger.error(traceback.format_exc())
                    raise

            logger.info("Starting anyio run")
            anyio.run(arun)
            logger.info("Anyio run completed")
        except Exception as e:
            logger.error(f"Error in stdio setup: {e}")
            logger.error(traceback.format_exc())
            raise

    return 0


if __name__ == "__main__":
    try:
        logger.info("Starting main function")
        main()
    except Exception as e:
        logger.error(f"Unhandled exception in main: {e}")
        logger.error(traceback.format_exc())
        raise
