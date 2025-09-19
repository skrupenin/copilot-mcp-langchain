# Todoist AI MCP Server Integration

## Overview
The Todoist AI MCP server has been integrated into this project to provide task management capabilities through AI conversations.

## Setup Status
- ✅ Package installed globally via npm (`@doist/todoist-ai@4.4.0`)
- ✅ MCP configuration added to `.cursor/mcp.json`
- ✅ Documentation created in `docs/todoist-ai-mcp-setup.md`
- ⚠️ Requires user to configure `TODOIST_API_KEY` in MCP configuration

## Configuration Required
To activate the Todoist AI MCP server:

1. Obtain your Todoist API token from [https://todoist.com/prefs/integrations](https://todoist.com/prefs/integrations)
2. Edit `.cursor/mcp.json` and replace `"your-todoist-token-here"` with your actual token
3. Restart Cursor/Claude to reload the MCP configuration

## Available Capabilities
Once configured, the AI assistant can:
- Create, update, and complete Todoist tasks
- Manage projects and organize tasks
- Handle due dates, reminders, and scheduling
- Search and filter tasks based on various criteria

## Documentation
Complete setup instructions are available in: `docs/todoist-ai-mcp-setup.md`

## Security Notes
- Never commit the actual API token to version control
- Keep the API token secure and private
- The `.env.example` file provides a template for secure configuration