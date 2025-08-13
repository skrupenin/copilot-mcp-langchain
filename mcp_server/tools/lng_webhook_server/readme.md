# 🌐 lng_webhook_server

Universal webhook server constructor with pipeline integration for MCP (Model Context Protocol).

## 📋 Overview

Creates HTTP endpoints that receive webhooks and can execute MCP tool pipelines automatically. Supports variable substitution, authentication, SSL, and persistent configuration.

## 🚀 Quick Start

### Basic Webhook
```bash
python -m mcp_server.run run lng_webhook_server '{
  "operation": "start",
  "name": "my-webhook",
  "port": 8080,
  "path": "/webhook",
  "response": {
    "status": 200,
    "body": {"message": "Hello ${webhook.body.user}!"}
  }
}'
```

### With Pipeline
```bash
python -m mcp_server.run run lng_webhook_server '{
  "operation": "start",
  "name": "word-counter",
  "port": 8081,
  "path": "/count",
  "pipeline": [
    {
      "tool": "lng_count_words",
      "params": {"input_text": "${webhook.body.message}"},
      "output": "stats"
    }
  ],
  "response": {
    "body": {
      "word_count": "${stats.wordCount}",
      "original": "${webhook.body.message}"
    }
  }
}'
```

## 🔧 Operations

| Operation | Description | Required Params |
|-----------|-------------|----------------|
| `start` | Create new webhook endpoint | `name`, `port`, `path` |
| `stop` | Stop webhook endpoint | `name` |
| `list` | List all active webhooks | - |
| `status` | Get webhook details | `name` |
| `test` | Send test HTTP request | `name`, `test_data` |
| `update` | Update webhook config | `name`, config params |

## 📂 Configuration Structure

```json
{
  "name": "webhook-name",
  "port": 8080,
  "path": "/endpoint",
  "bind_host": "localhost",
  "timeout": 30,
  "auth": {
    "type": "none|github_signature|bearer|basic",
    "secret": "webhook-secret"
  },
  "ssl": {
    "enabled": false,
    "cert_file": "path/to/cert.pem",
    "key_file": "path/to/key.pem"
  },
  "pipeline": [
    {
      "tool": "tool_name",
      "params": {"param": "${webhook.body.field}"},
      "output": "variable_name"
    }
  ],
  "response": {
    "status": 200,
    "headers": {"Content-Type": "application/json"},
    "body": {"result": "${variable_name.field}"}
  }
}
```

## 🔄 Variable Substitution

Use `${variable.path}` syntax to access:

### Webhook Context
- `${webhook.timestamp}` - Request timestamp (ISO format)
- `${webhook.method}` - HTTP method (GET, POST, etc.)
- `${webhook.path}` - Request path
- `${webhook.headers.header-name}` - Request headers
- `${webhook.query.param}` - Query parameters
- `${webhook.body.field}` - Request body fields
- `${webhook.remote_ip}` - Client IP address

### Pipeline Results
- `${output_name.field}` - Results from pipeline tools
- `${pipeline.success}` - Pipeline execution status
- `${pipeline.execution_time}` - Pipeline timing

## 📁 File Structure

```
lng_webhook_server/
├── tool.py              # Main tool implementation
├── http_server.py       # HTTP server with aiohttp
├── settings.yaml        # Dependencies and configuration
├── readme.md           # This file
└── stuff/
    └── test_webhook_universal.py  # Universal testing script
```

## 🧪 Testing

### Quick Test
```bash
# Create webhook
python -m mcp_server.run run lng_webhook_server '{"operation":"start","name":"test","port":8080,"path":"/test","response":{"body":{"success":true}}}'

# Test it
python -m mcp_server.run run lng_webhook_server '{"operation":"test","name":"test","test_data":{"message":"hello"}}'

# Clean up
python -m mcp_server.run run lng_webhook_server '{"operation":"stop","name":"test"}'
```

### Universal Test Suite
```bash
cd mcp_server/tools/lng_webhook_server/stuff
python test_webhook_universal.py
```

This runs comprehensive tests including:
- Basic webhook creation and HTTP testing
- Pipeline integration with multiple tools
- Error handling and edge cases
- Automatic cleanup

## 💾 Persistence

- Configurations saved to `mcp_server/config/webhook/{name}.json`
- Logs written to `mcp_server/logs/webhook/{name}_{timestamp}.log`
- Auto-restoration on MCP server restart via `init()` function

## 🔐 Authentication (Planned)

- **GitHub Signature**: Validates `X-Hub-Signature-256` header
- **Bearer Token**: Checks `Authorization: Bearer {token}` header  
- **Basic Auth**: Standard HTTP Basic authentication

## 🌐 SSL Support (Planned)

- Self-signed certificate generation
- Custom certificate files
- Automatic HTTPS redirect

## ⚡ Performance

- Async processing with aiohttp
- Request queuing for high load
- Optional async mode for non-blocking responses
- Structured logging with request IDs

## 🐛 Troubleshooting

### Common Issues

1. **Port already in use**
   ```bash
   python -m mcp_server.run run lng_webhook_server '{"operation":"list"}'
   ```

2. **Webhook not responding**
   - Check logs in `mcp_server/logs/webhook/`
   - Verify dependencies: `python -m mcp_server.run install_dependencies`

3. **Pipeline failures**
   - Test individual tools first
   - Check variable substitution syntax
   - Review pipeline tool availability

### Debug Mode
Set logging level to DEBUG for detailed information:
```python
import logging
logging.getLogger('mcp_server.tools.lng_webhook_server').setLevel(logging.DEBUG)
```
