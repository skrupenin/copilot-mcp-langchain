# Todoist AI MCP Server Setup

This document explains how to set up and use the Todoist AI MCP server in this project.

## Prerequisites

- Node.js and npm installed
- Todoist account with API access

## Installation

The Todoist AI MCP server has been pre-configured in this project. The setup includes:

1. **Global Package Installation**: The `@doist/todoist-ai` npm package is installed globally
2. **MCP Configuration**: Added to `.cursor/mcp.json` file
3. **Environment Setup**: Template provided in `.env.example`

## Configuration

### Step 1: Get Your Todoist API Token

1. Go to [https://todoist.com/prefs/integrations](https://todoist.com/prefs/integrations)
2. Scroll down to the "API token" section
3. Copy your API token

### Step 2: Configure the Token

Edit the `.cursor/mcp.json` file and replace `"your-todoist-token-here"` with your actual Todoist API token:

```json
{
  "mcpServers": {
    "langchain-mcp": {
        "type": "stdio",
        "command": "{workspaceFolder}\\.virtualenv\\Scripts\\python.exe",
        "args": ["{workspaceFolder}\\mcp_server\\server.py"]
    },
    "todoist-ai": {
        "type": "stdio",
        "command": "npx",
        "args": ["@doist/todoist-ai"],
        "env": {
            "TODOIST_API_KEY": "your-actual-token-here"
        }
    }
  }
}
```

## Available Tools

The Todoist AI MCP server provides the following tools:

- **Task Management**: Create, update, and complete tasks
- **Project Organization**: Manage projects and task organization
- **Date and Time**: Handle due dates, reminders, and scheduling
- **Search and Filter**: Find tasks and projects based on criteria

## Usage Examples

Once configured, you can use the Todoist AI tools in your AI conversations:

1. **Create Tasks**: "Add a task to buy groceries due tomorrow"
2. **Project Management**: "Create a new project for my vacation planning"
3. **Task Updates**: "Mark the presentation task as completed"
4. **Search**: "Show me all tasks due this week"

## Troubleshooting

### Common Issues

1. **Authentication Error**: Verify your API token is correct
2. **Connection Failed**: Ensure Node.js and npm are properly installed
3. **Package Not Found**: Run `npm install -g @doist/todoist-ai` to reinstall

### Testing the Connection

You can test if the MCP server is working by:

1. Restarting your Cursor/Claude application
2. Asking the AI to create a simple task
3. Checking your Todoist account to see if the task appears

## Security Notes

- Never commit your actual API token to version control
- Keep your API token secure and private
- Consider using environment variables for additional security

## More Information

- [Todoist AI GitHub Repository](https://github.com/Doist/todoist-ai)
- [Todoist API Documentation](https://developer.todoist.com/)
- [MCP Server Documentation](https://github.com/Doist/todoist-ai/blob/main/docs/mcp-server.md)