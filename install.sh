python --version

# create virtual environment
pip install virtualenv
python -m virtualenv .virtualenv
. ./.virtualenv/Scripts/activate

# install core MCP dependencies
pip install "mcp[cli]"
pip show mcp

# install python-dotenv
pip install python-dotenv

# install FastAPI and Uvicorn for HTTP server
pip install fastapi uvicorn requests

# Tool-specific dependencies are now managed via `settings.yaml` files.
# Run this to install dependencies for enabled tools:
python -m mcp_server.run install_dependencies