python --version

# create virtual environment
python -m venv langchain_env
. ./langchain_env/Scripts/activate

# install libraries
pip install langchain openai
pip install langchain-openai
pip install langchain-community

pip install python-dotenv
pip install faiss-cpu
pip install "mcp[cli]"
pip show mcp

# to check connection to the OpenAI/Azure LLM provider
python simple_openai.py 
python simple_azure.py 
python simple_both.py 

# to test MCP server with MCP client 
python mcp_client.py

# to check one MCP tool without MCP 
python -c "import asyncio
from mcp_server.tools.lng_count_words.tool import run_tool
result = asyncio.run(run_tool('f1e_lng_count_words', {'text': 'Мама мыла раму'}))
print(result)"

# to check several MCP tools without MCP
python -c "import asyncio
from mcp_server.tools.lng_save_prompt_template.tool import run_tool as save_tool
from mcp_server.tools.lng_use_prompt_template.tool import run_tool as use_tool
async def test_tools():
    save_result = await save_tool('f1e_lng_save_prompt_template', {'template': 'Расскажи о {topic} в стиле {style}.'})
    print('Save template result:', save_result)   
    use_result = await use_tool('f1e_lng_use_prompt_template', {'topic': 'искусственный интеллект', 'style': 'пирата'})
    print('Use template result:', use_result)
asyncio.run(test_tools())"