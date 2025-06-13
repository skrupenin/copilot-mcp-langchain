python --version

python -m venv langchain_env
. ./langchain_env/Scripts/activate

pip install langchain openai
pip install langchain-openai
pip install python-dotenv
pip install "mcp[cli]"
pip show mcp