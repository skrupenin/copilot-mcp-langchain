python --version

# create virtual environment
pip install virtualenv
python -m virtualenv .virtualenv
. ./.virtualenv/Scripts/activate

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

# install FastAPI and Uvicorn for HTTP server
pip install fastapi uvicorn requests
pip install psutil