# MCP Tools Web Interface

A Swagger-like web interface for MCP (Model Context Protocol) tools, providing universal browser-based access to all available MCP tools.

## Overview

This project creates a web interface that allows users to interact with MCP tools through a browser without needing an IDE. It provides the 4th access method for MCP tools:

1. **Terminal** - Direct command-line usage
2. **MCP Protocol** - Through MCP-enabled IDEs and clients  
3. **Pipeline** - Via `lng_batch_run` tool
4. **Web Interface** - Universal browser-based access ⬅️ **This project**

## Quick Start

### Prerequisites

- Python MCP server with activated virtual environment
- All MCP tools installed and configured
- Modern web browser (Chrome, Firefox, Edge with ES6+ support)

### Running the Web Interface

1. **Start the server:**
   ```powershell
   .\run.ps1
   ```

2. **Open your browser:**
   - Local access: http://localhost:8080
   - Network access: http://your-ip:8080 (if configured)

3. **Stop the server:**
   - Press `Ctrl+C` in the terminal where the server is running

## Configuration

### Server Configuration
Edit `config/webhook_config.json` to customize:
- **Port**: Default 8080
- **Host binding**: `localhost` for local only, `0.0.0.0` for network access
- **Template variables**: TITLE, VERSION, BASE_URL

### Network Access
To allow access from other machines, change in `config/webhook_config.json`:
```json
"bind_host": "0.0.0.0"
```

## Project Structure

```
web-mcp/
├── config/
│   └── webhook_config.json     # Server configuration
├── static/
│   └── index.html             # Single page web application
├── architecture.md            # Detailed architecture documentation
├── tasklist.md               # Implementation phases breakdown
├── readme.md                 # This file
└── run.ps1                   # Quick start script
```

## Features (Development Phases)

- ✅ **Phase 1**: Project structure and basic server
- ⏳ **Phase 2**: Tool discovery API (`/api/tools`)
- ⏳ **Phase 3**: Tool execution API (`/api/execute`) 
- ⏳ **Phase 4**: HTML structure and responsive CSS
- ⏳ **Phase 5**: Dynamic tool loading and display
- ⏳ **Phase 6**: Search and filtering functionality
- ⏳ **Phase 7**: Dynamic form generation from schemas
- ⏳ **Phase 8**: Tool execution integration
- ⏳ **Phase 9**: Results display with smart formatting
- ⏳ **Phase 10**: Polish and comprehensive testing

## API Endpoints (When Complete)

- `GET /` - Web interface
- `GET /api/tools` - List all available tools with schemas
- `POST /api/execute` - Execute any tool with parameters

## Technical Stack

- **Backend**: `lng_webhook_server` with pipeline integration
- **Frontend**: Vanilla HTML/JavaScript/CSS (no frameworks)
- **Architecture**: Single page application with embedded styles and scripts

## Development

### Testing Current Phase
Each phase has specific testable outcomes. For Phase 1:
- Files exist in correct structure
- Webhook server starts without errors
- Web interface loads at configured URL

### Next Steps
See `tasklist.md` for detailed breakdown of all implementation phases.

## Troubleshooting

### Server Won't Start
- Ensure virtual environment is activated
- Check if port 8080 is available
- Verify MCP server is running properly

### Template Variables Not Replaced
- Check `html_routes` configuration in webhook_config.json
- Verify template path is correct
- Ensure `lng_webhook_server` supports template mapping

### Can't Access from Network
- Change `bind_host` to `"0.0.0.0"` in config
- Check firewall settings
- Verify correct IP address in BASE_URL

## Documentation

- `architecture.md` - Complete architecture and technical details
- `tasklist.md` - Phase-by-phase implementation breakdown

---
**Version**: 1.0.0  
**Status**: Phase 1 - Basic Setup Complete
