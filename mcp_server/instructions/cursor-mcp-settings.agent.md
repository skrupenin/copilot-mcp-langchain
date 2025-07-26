- Links contains `{workspaceFolder}` which should be replaced with absolute path to the project.
 - For example for Windows.
 ```json
 {
  "mcpServers": {
    "langchain-mcp":{
        "type": "stdio",
        "command": "C:\\Java\\CopipotTraining\\hello-langchain\\.virtualenv\\Scripts\\python.exe",
        "args": ["C:\\Java\\CopipotTraining\\hello-langchain\\mcp_server\\server.py"]
    }
  }
}
```
- For other OS links should be un Unix style: `/home/user/Java/CopipotTraining/hello-langchain/mcp_server/server.py`.