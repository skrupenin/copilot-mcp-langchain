import sys
import os
print(f"Python executable: {sys.executable}")
print(f"Python version: {sys.version}")
print(f"Current directory: {os.getcwd()}")
import anyio
import click
import mcp.types as types
from mcp.server.lowlevel import Server
from langchain_openai import OpenAI
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
import os.path

# Add the project root to the Python path to ensure imports work correctly
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Load environment variables
load_dotenv()

# Initialize OpenAI client
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if OPENAI_API_KEY is None:
    raise ValueError("OPENAI_API_KEY not found in .env")

# Store the saved prompt template
saved_prompt_template = None

async def lng_save_prompt_template(template_text: str) -> list[types.Content]:
    global saved_prompt_template
    try:
        saved_prompt_template = template_text
        return [types.TextContent(type="text", text="Prompt template saved successfully.")]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Error saving prompt template: {str(e)}")]

async def lng_get_tools_info() -> list[types.Content]:
    try:
        # Path to the markdown file relative to the server script
        md_file_path = os.path.join(project_root, "langchain_tools.md")
        
        # Read the markdown file
        with open(md_file_path, "r", encoding="utf-8") as file:
            content = file.read()
        
        return [types.TextContent(type="text", text=content)]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Error retrieving tools information: {str(e)}")]

async def lng_use_prompt_template(parameters: dict) -> list[types.Content]:
    global saved_prompt_template
    
    if saved_prompt_template is None:
        return [types.TextContent(type="text", text="No prompt template has been saved. Please save a template first.")]
    
    try:
        # Extract input variables from the parameters
        input_variables = list(parameters.keys())
        
        # Create prompt template with the input variables
        prompt_template = PromptTemplate(
            input_variables=input_variables,
            template=saved_prompt_template
        )
        
        # Format the prompt with the provided parameters
        prompt = prompt_template.format(**parameters)
        
        # Initialize LLM and get response
        llm = OpenAI(openai_api_key=OPENAI_API_KEY)
        response = llm.invoke(prompt)
        
        return [types.TextContent(type="text", text=response)]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Error using prompt template: {str(e)}")]


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
    async def fetch_tool(name: str, arguments: dict) -> list[types.Content]:
        if name == "lng_save_prompt_template":
            if "template" not in arguments:
                raise ValueError("Missing required argument 'template'")
            return await lng_save_prompt_template(arguments["template"])
        elif name == "lng_use_prompt_template":
            if not arguments:
                raise ValueError("No parameters provided for the prompt template")
            return await lng_use_prompt_template(arguments)
        elif name == "lng_get_tools_info":
            return await lng_get_tools_info()
        else:
            raise ValueError(f"Unknown tool: {name}")

    @app.list_tools()
    async def list_tools() -> list[types.Tool]:
        return [
            types.Tool(
                name="lng_save_prompt_template",
                description="Saves a prompt template for later use",
                inputSchema={
                    "type": "object",
                    "required": ["template"],
                    "properties": {
                        "template": {
                            "type": "string",
                            "description": "The prompt template to save (with placeholders in {name} format)",
                        }
                    },
                },
            ),
            types.Tool(
                name="lng_use_prompt_template",
                description="Uses the saved prompt template with provided parameters",
                inputSchema={
                    "type": "object",
                    "additionalProperties": {
                        "type": "string"
                    },
                    "description": "Key-value pairs to use as parameters in the prompt template",
                },
            ),
            types.Tool(
                name="lng_get_tools_info",
                description="Returns information about the available langchain tools",
                inputSchema={
                    "type": "object",
                    "description": "No parameters required",
                },
            )
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
