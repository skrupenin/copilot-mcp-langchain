# Langchain MCP Tools

This document describes the tools available in the Langchain Model Context Protocol (MCP) implementation.

## Available Tools

### 1. `lng_save_prompt_template`

Saves a prompt template for later use by the system.

**Parameters:**
- `template` (string, required): The prompt template to save with placeholders in {name} format

**Example Usage:**
- Create a template like "Tell me about {topic} in the style of {style}."
- The system saves this template for future use
- Placeholders like {topic} and {style} will be replaced with actual values when used

### 2. `lng_use_prompt_template`

Uses the previously saved prompt template with provided parameters.

**Parameters:**
- Any key-value pairs that match the placeholders in your template

**Example Usage:**
- If your saved template contains {topic} and {style} placeholders
- You would provide values like "topic: artificial intelligence" and "style: a pirate"
- The system will replace the placeholders with these values and process the completed prompt

### 3. `lng_get_tools_info`

Returns information about the available langchain tools in markdown format.

**Parameters:**
- None required

**Example Usage:**
- Simply request this tool without any parameters
- The system will return this documentation about available tools

## How MCP Tools Work Together

1. First, you save a template using the `lng_save_prompt_template` tool
2. The template contains placeholders in curly braces, like {name} or {topic}
3. Later, you use the `lng_use_prompt_template` tool with specific values for those placeholders
4. The system fills in the template with your values and processes the completed prompt
5. If you need information about available tools, you can use the `lng_get_tools_info` tool

This workflow allows for flexible prompt engineering while maintaining a clean separation between the prompt structure and the specific content.
