# lng_batch_run

Executes a batch pipeline of tool calls with variable substitution using JavaScript expressions.

## Features

- **Sequential execution** - Tools run one after another
- **Variable passing** - Store results and use in subsequent steps
- **JavaScript expressions** - Use `${expression}` syntax for data manipulation
- **JSON parsing** - Automatic parsing of tool responses
- **Property access** - Access object properties with `obj.property` syntax
- **Error handling** - Detailed error reporting with execution context

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
    {"tool": "lng_winapi_clipboard_set", "params": {"text": "Words: ${count}"}}
  ],
  "final_result": "completed"
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
  "context": {"var1": "value1", "var2": "value2"}
}
```

## Integration

Designed for use with hotkey listener for automated workflows:
1. Register hotkey → batch tool
2. Define pipeline in tool parameters
3. Execute complex operations with single keypress
