python --version

python -m venv langchain_env
. ./langchain_env/Scripts/activate

pip install langchain openai
pip install langchain-openai
pip install langchain-community
pip install python-dotenv
pip install faiss-cpu
pip install "mcp[cli]"
pip show mcp

# to check connection to the OpenAI/Azure LLM provider
python main.py 

# to test MCP server with MCP client 
python mcp_client.py

# to run one MCP tool without MCP for debugging
python -m mcp_server.tools.lng_rag_add_data.tool
