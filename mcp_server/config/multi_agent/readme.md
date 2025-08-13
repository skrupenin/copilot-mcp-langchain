# Multi-Agent System Configuration

This directory contains configuration files for the multi-agent system.

## Files

- `agents.json` - Active agents configuration and state

## Agent Configuration (`agents.json`)

Contains the configuration and state of all active sub-agents in the multi-agent system:

```json
{
  "agents": [
    {
      "agent_id": "uuid",
      "name": "Agent Name",
      "module_path": "/path/to/module",
      "available_tools": ["tool1", "tool2"],
      "description": "Agent purpose",
      "created_at": "2025-01-01T00:00:00",
      "last_active": "2025-01-01T00:00:00"
    }
  ]
}
```

## Configuration Management

### Clearing All Agents
To remove all agents, set the configuration to:
```json
{
  "agents": []
}
```
**Note**: Changes take effect only after MCP server restart.

### Agent Lifecycle
1. **Load**: Agents loaded from this file when MCP server starts
2. **Runtime**: Agents exist in server memory during session
3. **Save**: Configuration automatically updated when agents are created/modified/removed
4. **Memory**: Conversation history exists only in RAM (lost on restart)

## Important Notes

- This file is automatically managed by the `lng_multi_agent_manager` tool
- Do not edit manually - use the MCP tool operations instead
- Agents are automatically persisted when created, updated, or removed
- Each agent has a unique UUID and is associated with a specific module path
- Agent memory (conversation history) is not persisted to disk
