python --version

# create virtual environment
python -m venv langchain_env
. ./langchain_env/Scripts/activate

# install langchain libraries
pip install langchain openai
pip install langchain-openai
pip install langchain-community

# install additional libraries for agent demo
pip install langchain-experimental
pip install langchain-text-splitters

# install library to work with environment variables
pip install python-dotenv

# install RAG libraries
pip install faiss-cpu

# install MCP server and client
pip install "mcp[cli]"
pip show mcp

# to check connection to the OpenAI/Azure LLM provider
python simple_openai.py 
python simple_azure.py 
python simple_both.py 

# to test MCP server with MCP client 
python mcp_client.py

# to check one MCP tool without MCP 

# lng_get_tools_info
python -c "import asyncio
from mcp_server.tools.lng_get_tools_info.tool import run_tool
result = asyncio.run(run_tool('lng_get_tools_info', {}))
print(result)"

# lng_count_words
python -c "import asyncio
from mcp_server.tools.lng_count_words.tool import run_tool
result = asyncio.run(run_tool('lng_count_words', {'input_text': 'Hello pirate!'}))
print(result)"

# lng_run_chain
python -c "import asyncio
from mcp_server.tools.lng_run_chain.tool import run_tool
result = asyncio.run(run_tool('lng_run_chain', {'input_text': 'Hello pirate!'}))
print(result)"

# lng_agent_demo
python -c "import asyncio
from mcp_server.tools.lng_agent_demo.tool import run_tool
result = asyncio.run(run_tool('lng_agent_demo', {'input_text': 'Hello pirate!', 'task': 'Reverse this text and then capitalize it'}))
print(result)"

# lng_structured_output
# possible output formats: json, xml, csv, yaml, pydantic
python -c "import asyncio
from mcp_server.tools.lng_structured_output.tool import run_tool
result = asyncio.run(run_tool('lng_structured_output', {'question': 'Tell me more about Matrix', 'output_format': 'xml'}))
print(result)"

# to check several MCP tools without MCP

# lng_save_prompt_template and lng_use_prompt_template
python -c "import asyncio
from mcp_server.tools.lng_save_prompt_template.tool import run_tool as save_tool
from mcp_server.tools.lng_use_prompt_template.tool import run_tool as use_tool
async def test_tools():
    save_result = await save_tool('lng_save_prompt_template', {'template': 'Tell me about {topic} in the style of {style}.'})
    print('Save template result:', save_result)   
    use_result = await use_tool('lng_use_prompt_template', {'topic': 'artificial intelligence', 'style': 'a pirate'})
    print('Use template result:', use_result)
asyncio.run(test_tools())"

# lng_rag_add_data and lng_rag_search
python -c "import asyncio
from mcp_server.tools.lng_rag_add_data.tool import run_tool as add_data_tool
from mcp_server.tools.lng_rag_search.tool import run_tool as search_tool
async def test_rag_tools():
    add_result = await add_data_tool('lng_rag_add_data', {'input_text': 'Hello pirate!'})
    print('Add data result:', add_result)
    search_result = await search_tool('lng_rag_search', {'query': 'Pirate'})
    print('Search result:', search_result)
asyncio.run(test_rag_tools())"
