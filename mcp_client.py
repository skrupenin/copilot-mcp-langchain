import asyncio
from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client


async def main():
    # Using pip instead of uv as per your requirements
    async with stdio_client(
        StdioServerParameters(command="python", args=["-m", "mcp_server.server"])
    ) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # List available tools
            tools = await session.list_tools()
            print("Available tools:")
            print(tools)

            # Call the fetch tool
            print("\nFetching website content...")
            url = "https://example.com"
            result = await session.call_tool("fetch", {"url": url})
            print(f"Content from {url}:")
            for content in result:
                if hasattr(content, 'text'):
                    print(content.text[:500] + "..." if len(content.text) > 500 else content.text)


if __name__ == "__main__":
    asyncio.run(main())
