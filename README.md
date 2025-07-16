# Extending GitHub Copilot with Python and Langchain via MCP

This project demonstrates how to extend `GitHub Copilot` capabilities using `Python`, `Langchain`, and the `Model Context Protocol (MCP)`, allowing for more deterministic and powerful interactions with the LLM.

## Project Overview

As a `GitHub Copilot` trainer, I've observed its impressive evolution. However, I've always wanted to access GitHub Copilot's internals to build more complex transformation chains. This project shows how to achieve that goal by leveraging MCP (Model Context Protocol) and Langchain.

While `GitHub Copilot` [repository custom instructions](https://docs.github.com/en/copilot/customizing-copilot/adding-repository-custom-instructions-for-github-copilot) feature improved customization options, the introduction of the [MCP protocol](https://docs.github.com/en/copilot/using-github-copilot/coding-agent/extending-copilot-coding-agent-with-mcp) opened new possibilities for extending Copilot's functionality through custom `MCP` servers.

## The Problem

Instruction files are not always deterministic - they need to be fine-tuned when new LLM versions are released to reduce hallucinations. LLMs often struggle with precise text manipulations, sometimes creatively reinterpreting tasks and adding unwanted artifacts. What we need is a way to inject deterministic logic into our instructions.

## The Solution

This project demonstrates a solution through:

1. `Python` scripts installed on the local machine
2. Custom `MCP` server configuration through `.vscode/mcp.json`
3. Custom tools defined in the `mcp_server/tools directory`

With this setup, `GitHub Copilot` gains access to new, well-documented tools that it can see as part of your project. When you ask Copilot to "create a tool that does X", it can generate a solution very close to what you need. You simply accept its changes and restart MCP to get a new deterministic tool for your specific logic.

## Key Components

- **Simple Examples**: Demonstrates integration with different LLM providers
  - `simple_openai.py` - OpenAI integration
  - `simple_azure.py` - Azure OpenAI integration
  - `simple_both.py` - Flexible approach to switch between providers

- **MCP Implementation**:
  - `mcp_client.py` - Client implementation
  - `mcp_server/` - Server with custom tools

- **Install file** `install.sh`: 
  - Setup virtal environment 
  - Setup libraties
  - Smoke tests

- **mcp.json**
  ```json
    {
      "servers": {
        "langchain-mcp":{
            "type": "stdio",
            "command": "${workspaceFolder}\\langchain_env\\Scripts\\python.exe",
            "args": ["${workspaceFolder}\\mcp_server\\server.py"]
        }
      }
    }
  ```

- **Custom Langchain Tools**:
  - `lng_cont_words` - word counting, demonstrates python function calling
  - `lng_get_tools_info` - tools information retrieval, collects all the information about tools in one place, that helps in `Github Copilot`.
  - `lng_rag_add_data` and `lng_rag_search` - demonstrates RAG (Retrieval Augmented Generation) functionality 
  - `lng_save_prompt_template` and `lng_use_prompt_template` - demonstrates Prompt template management
  - `lng_run_chain` - demostrates Chain execution 
  - `lng_agent_demo` - demonstrates Agent functionality
  - `lng_structured_output` - demonstrates Structured output
  - `lng_chain_of_thought` - demonstrates Chain of Thought reasoning approach with Memory usage
  - And more in `mcp_server/tools/`

## Debug 

To debug mcp protocol you can run server in terminal 
`.\langchain_env\Scripts\python.exe .\mcp_server\server.py`, 
then update `mcp.json` from `"args": ["${workspaceFolder}\\mcp_server\\server.py"]` to 
`"args": ["${workspaceFolder}\\mcp_server\\server_fake.py"]` and run fake server. 
After that copy request from `mcp_out.log`: 
```
2025-07-16 20:54:30,339 - mcp_fake_logger - INFO - [<] {"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-03-26","capabilities":{"roots":{"listChanged":true}},"clientInfo":{"name":"Visual Studio Code - Insiders","version":"1.100.0-insider"}}}
```
to the server console. Then copy output to the `mcp_in.log` and save. Then reiterate. 

## Use Cases

While LLMs can handle simple tasks, more complex operations like processing Excel files or extracting specific data benefit greatly from custom `MCP` tools. The LLM can still help generate the code for these tools, providing the best of both worlds.

## Getting Started

1. Clone this repository
2. Set up your environment variables in a `.env` file
3. Install `Python` dependencies as described in `install.sh`
4. Configure `.vscode/mcp.json` for your MCP server
5. Start using the enhanced `GitHub Copilot` capabilities

## API Keys

API keys and other credentials should be stored in a `.env` file (not included in the repository).

## Original Source

This project is based on concepts from the blog post: [Как расширить GithubCopilot с помощью Python и Langchain через MCP](http://www.apofig.com/2025/06/githubcopilot-python-langchain-mcp.html)

## Repository

The original repository is available at: [https://github.com/codenjoyme/copilot-mcp-langchain](https://github.com/codenjoyme/copilot-mcp-langchain)

## Alternative HTTP Proxy Setup (When MCP is Not Available)

If you're experiencing issues with MCP connectivity or want to test the system without full MCP integration, this project provides an alternative HTTP-based architecture that allows you to quickly test and interact with LangChain tools.

### Architecture Overview

The alternative setup consists of three components:

1. **Component 1**: `mcp_server/server.py` - The original MCP server with LangChain tools (will run automatically with Component 2)
2. **Component 2**: `mcp_proxy.py` - Full HTTP proxy server with complete MCP protocol implementation
3. **Component 3**: `mcp_execute.py` - Client for quick requests

### Quick Start

#### 1. Start the MCP HTTP Proxy Server

Open a terminal and run:
```bash
python mcp_proxy.py
```

The server will start on `http://127.0.0.1:8080` and provide:
- `GET /health` - Server health check with MCP connection status
- `GET /tools` - List all available LangChain tools
- `POST /execute` - Execute tools using full MCP protocol

#### 2. Test the System

Open another terminal and test the system:

**Check server health:**
```bash
python mcp_execute.py health
```

**List available tools:**
```bash
python mcp_execute.py list
```

**Execute tools:**
```bash
# Count words in text
python mcp_execute.py exec lng_count_words --params '{\"input_text\": \"Hello world this is a test\"}'

# Math calculations
python mcp_execute.py exec lng_math_calculator --params '{\"expression\": \"2 + 3 * 4\"}'

# Chain of thought reasoning
python mcp_execute.py exec lng_chain_of_thought --params '{\"question\": \"What is 15 * 24?\"}'

# RAG functionality
python mcp_execute.py exec lng_rag_add_data --params '{\"input_text\": \"Your document content\"}'
python mcp_execute.py exec lng_rag_search --params '{\"query\": \"search term\"}'
```

#### 3. View Available Examples

```bash
python mcp_execute.py examples
```

### Troubleshooting

If you encounter issues:

1. **Server not starting**: Check if port 8080 is available
2. **Connection refused**: Ensure the test server is running
3. **JSON parsing errors**: Use single quotes for PowerShell parameters
4. **Tool errors**: Check the server console for detailed error messages

### Browser Testing

You can also test the system directly in your browser:

- Health check: `http://127.0.0.1:8080/health`
- Use tools like Postman or curl for POST requests to `/execute`

This alternative setup provides a reliable fallback when MCP is not available while maintaining full access to your LangChain tools.