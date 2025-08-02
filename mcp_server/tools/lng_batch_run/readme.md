# lng_batch_run

Executes a batch pipeline of tool calls with variable substitution using JavaScript expressions.

**⚡ Now powered by the new `mcp_server.pipeline` module for better extensibility and maintainability!**

## Features

- **Sequential execution** - Tools run one after another
- **Variable passing** - Store results and use in subsequent steps
- **JavaScript expressions** - Use `${expression}` syntax for data manipulation
- **JSON parsing** - Automatic parsing of tool responses
- **Property access** - Access object properties with `obj.property` syntax
- **Error handling** - Detailed error reporting with execution context
- **Modular architecture** - Built on `mcp_server.pipeline` for easy extension

## Usage

```bash
python -m mcp_server.run run lng_batch_run '{
  "pipeline": [
    {
      "tool": "tool_name",
      "params": {"param": "${variable}"},
      "output": "variable_name"
    }
  ],
  "final_result": "${result_expression}"
}'
```

### Three-step pipeline example

```bash
python -m mcp_server.run run lng_batch_run '{
  "pipeline": [
    {
      "tool": "lng_winapi_clipboard_get",
      "params": {},
      "output": "clipboard_content"
    },
    {
      "tool": "lng_count_words",
      "params": {"input_text": "${clipboard_content.content}"},
      "output": "word_stats"
    },
    {
      "tool": "lng_winapi_clipboard_set",
      "params": {"text": "Analysis: ${word_stats.wordCount} words, ${word_stats.charactersWithSpaces} chars"}
    }
  ],
  "final_result": "Text analysis completed with ${word_stats.wordCount} words"
}'
```

## Pipeline Structure

- **pipeline** - Array of steps to execute
- **tool** - Name of the MCP tool to call
- **params** - Parameters to pass (supports variable substitution)
- **output** - Variable name to store the result (optional)
- **final_result** - Expression for the final return value (optional, default: "ok")

## Variable Substitution

Variables are substituted using `${expression}` syntax:

- `${variable}` - Direct variable access
- `${variable.property}` - Object property access
- `${variable || 'default'}` - Fallback values
- `${variable ? 'yes' : 'no'}` - Conditional expressions
- `${JSON.stringify(variable)}` - JSON serialization

## Examples

### Simple clipboard operations
```json
{
  "pipeline": [
    {"tool": "lng_winapi_clipboard_get", "params": {}, "output": "clipboard_text"},
    {"tool": "lng_winapi_clipboard_set", "params": {"text": "${clipboard_text.content}"}}
  ],
  "final_result": "ok"
}
```

### Text processing chain
```json
{
  "pipeline": [
    {"tool": "lng_winapi_clipboard_get", "params": {}, "output": "text"},
    {"tool": "lng_count_words", "params": {"input_text": "${text.content}"}, "output": "count"},
    {"tool": "lng_winapi_clipboard_set", "params": {"text": "Words: ${count.wordCount}"}}
  ],
  "final_result": "completed"
}
```

## New Response Format

The pipeline now returns a structured response with more details:

```json
{
  "success": true,
  "result": "final_result_value",
  "error": null,
  "step": null,
  "tool": null,
  "context": {
    "variable1": "value1",
    "variable2": "value2"
  },
  "execution_time": 0.002
}
```

## Error Handling

If any step fails, execution stops and returns:
```json
{
  "success": false,
  "error": "Step 2 failed: error description",
  "step": 2,
  "tool": "tool_name",
  "context": {"var1": "value1", "var2": "value2"},
  "execution_time": 0.001
}
```

## Conditional Logic Support ✨

**NEW**: The pipeline now supports conditional logic with JavaScript-like expressions!

### Basic Conditional Syntax
```json
{
  "type": "condition",
  "condition": "${variable > 5}",
  "then": [
    {"tool": "tool_when_true", "params": {}, "output": "result"}
  ],
  "else": [
    {"tool": "tool_when_false", "params": {}, "output": "result"}
  ]
}
```

### Smart Clipboard Processing Example
```json
{
  "pipeline": [
    {"tool": "lng_winapi_clipboard_get", "params": {}, "output": "clipboard"},
    {"tool": "lng_count_words", "params": {"input_text": "${clipboard.content}"}, "output": "stats"},
    {
      "type": "condition",
      "condition": "${stats.wordCount > 10}",
      "then": [
        {"tool": "lng_winapi_clipboard_set", "params": {"text": "Too long: ${stats.wordCount} words"}}
      ],
      "else": [
        {"tool": "lng_winapi_clipboard_set", "params": {"text": "Word count: ${stats.wordCount}"}}
      ]
    }
  ]
}
```

**📖 See `conditional_examples.md` for comprehensive conditional logic documentation!**

## Future Extensions

The new architecture in `mcp_server.pipeline` supports future extensions:

- ✅ **Conditional logic** - `if/then/else` statements (IMPLEMENTED)
- **Loops** - `foreach` iterations
- **Parallel execution** - Running multiple tools simultaneously
- **Templates** - Reusable pipeline components
- **Advanced error handling** - Retry, fallback, continue strategies

## Integration

Designed for use with hotkey listener for automated workflows:
1. Register hotkey → batch tool
2. Define pipeline in tool parameters
3. Execute complex operations with single keypress
