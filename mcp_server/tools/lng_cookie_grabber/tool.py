import mcp.types as types
import json
import logging
import os
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger('mcp_server.tools.lng_cookie_grabber')

async def tool_info() -> dict:
    return {
        "description": """Cookie Grabber Tool for Managing WebSocket/Webhook Servers and Processing Cookie Data.

**Universal Cookie Grabber Management System**
Complete solution for cookie collection with Chrome extension and server management.

**Operations:**
• `start` - Start webhook and websocket servers for cookie collection (stops existing first)
• `stop` - Stop webhook and websocket servers
• `process` - Process cookie data and save to organized files

**Features:**
**Direct Server Management** - Direct Python imports for deterministic control
**Cookie Processing** - Parse and organize cookie data by domain
**File Organization** - Save cookies to config/cookies/<sessionId>/<domain>.txt
**Session Support** - Support for sessionId-based cookie organization
**Error Handling** - Comprehensive error handling and logging

**Start Operation:**
Starts both webhook (port 9000) and websocket (port 9001) servers using 
the configuration files from the cookie grabber directory. Automatically
stops existing servers first for clean restart.

**Stop Operation:**
Stops both webhook and websocket servers cleanly.

**Process Operation:**
Processes cookie data in the format:
```
domain1.example.com
cookie=value1; another=value2
domain2.example.com
cookie=value3; another=value4
```

Saves each domain's cookies to separate files:
- `config/cookies/<sessionId>/domain1.example.com.txt`
- `config/cookies/<sessionId>/domain2.example.com.txt`

**Example Usage:**

Start servers:
```json
{
  "operation": "start"
}
```

Process cookies:
```json
{
  "operation": "process",
  "cookies": "domain1.com\\ncookie=value1\\ndomain2.com\\ncookie=value2",
  "session": "my_session_123"
}
```

Stop servers:
```json
{
  "operation": "stop"
}
```
""",
        "schema": {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "description": "Operation to perform",
                    "enum": ["start", "stop", "process"]
                },
                "cookies": {
                    "type": "string", 
                    "description": "Cookie data to process (required for 'process' operation). Format: domain\\ncookies\\ndomain\\ncookies..."
                },
                "session": {
                    "type": "string",
                    "description": "Session ID for organizing cookie files (required for 'process' operation)"
                }
            },
            "required": ["operation"]
        }
    }

async def run_tool(name: str, parameters: dict) -> list[types.Content]:
    """Execute cookie grabber operations."""
    
    try:
        operation = parameters.get("operation")
        
        if operation == "start":
            return await start_servers()
        elif operation == "stop":
            return await stop_servers()
        elif operation == "process":
            cookies = parameters.get("cookies")
            session = parameters.get("session")
            
            if not cookies:
                raise ValueError("'cookies' parameter is required for process operation")
            if not session:
                raise ValueError("'session' parameter is required for process operation")
                
            return await process_cookies(cookies, session)
        else:
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "success": False,
                    "error": f"Unknown operation: {operation}"
                }, indent=2)
            )]
            
    except Exception as e:
        logger.error(f"Error in lng_cookie_grabber: {e}")
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "success": False,
                "error": str(e)
            }, indent=2)
        )]

async def start_servers() -> list[types.Content]:
    """Start webhook and websocket servers. Stops existing servers first."""
    try:
        logger.info("Starting cookie grabber servers (stopping existing first)...")
        
        # Stop existing servers first
        try:
            await stop_servers()
            logger.info("Existing servers stopped")
        except Exception as e:
            logger.warning(f"Error stopping existing servers (may not exist): {e}")
        
        results = []
        
        # Start webhook server
        try:
            from ..lng_webhook_server.tool import run_tool as run_webhook_tool
            
            webhook_params = {
                "operation": "start",
                "config_file": "mcp_server/tools/lng_cookie_grabber/webhook.json",
                "name": "cookie-status-server",
                "thread_mode": True
            }
            
            webhook_result = await run_webhook_tool("lng_webhook_server", webhook_params)
            webhook_data = json.loads(webhook_result[0].text)
            results.append({
                "service": "webhook",
                "status": "started" if webhook_data.get("success") else "failed",
                "details": webhook_data
            })
            
            logger.info(f"Webhook server: {webhook_data.get('message', 'Unknown result')}")
            
        except Exception as e:
            logger.error(f"Failed to start webhook server: {e}")
            results.append({
                "service": "webhook", 
                "status": "failed",
                "error": str(e)
            })
        
        # Start websocket server
        try:
            from ..lng_websocket_server.tool import run_tool as run_websocket_tool
            
            websocket_params = {
                "operation": "server_start",
                "config_file": "mcp_server/tools/lng_cookie_grabber/websocket.json",
                "name": "cookie-websocket-server"
            }
            
            websocket_result = await run_websocket_tool("lng_websocket_server", websocket_params)
            websocket_data = json.loads(websocket_result[0].text)
            results.append({
                "service": "websocket",
                "status": "started" if websocket_data.get("success") else "failed", 
                "details": websocket_data
            })
            
            logger.info(f"WebSocket server: {websocket_data.get('message', 'Unknown result')}")
            
        except Exception as e:
            logger.error(f"Failed to start websocket server: {e}")
            results.append({
                "service": "websocket",
                "status": "failed", 
                "error": str(e)
            })
        
        # Determine overall success
        all_started = all(r["status"] == "started" for r in results)
        
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "success": all_started,
                "message": f"Cookie grabber servers {'started successfully' if all_started else 'failed to start'}",
                "operation": "start",
                "timestamp": datetime.now().isoformat(),
                "services": results
            }, indent=2)
        )]
        
    except Exception as e:
        logger.error(f"Failed to start cookie grabber servers: {e}")
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "success": False,
                "error": str(e),
                "operation": "start"
            }, indent=2)
        )]

async def stop_servers() -> list[types.Content]:
    """Stop webhook and websocket servers."""
    try:
        logger.info("Stopping cookie grabber servers...")
        
        results = []
        
        # Stop webhook server
        try:
            from ..lng_webhook_server.tool import run_tool as run_webhook_tool
            
            webhook_params = {
                "operation": "stop",
                "name": "cookie-status-server"
            }
            
            webhook_result = await run_webhook_tool("lng_webhook_server", webhook_params)
            webhook_data = json.loads(webhook_result[0].text)
            results.append({
                "service": "webhook",
                "status": "stopped" if webhook_data.get("success") else "failed",
                "details": webhook_data
            })
            
            logger.info(f"Webhook server: {webhook_data.get('message', 'Unknown result')}")
            
        except Exception as e:
            logger.error(f"Failed to stop webhook server: {e}")
            results.append({
                "service": "webhook",
                "status": "failed",
                "error": str(e)
            })
        
        # Stop websocket server
        try:
            from ..lng_websocket_server.tool import run_tool as run_websocket_tool
            
            websocket_params = {
                "operation": "server_stop", 
                "name": "cookie-websocket-server"
            }
            
            websocket_result = await run_websocket_tool("lng_websocket_server", websocket_params)
            websocket_data = json.loads(websocket_result[0].text)
            results.append({
                "service": "websocket",
                "status": "stopped" if websocket_data.get("success") else "failed",
                "details": websocket_data
            })
            
            logger.info(f"WebSocket server: {websocket_data.get('message', 'Unknown result')}")
            
        except Exception as e:
            logger.error(f"Failed to stop websocket server: {e}")
            results.append({
                "service": "websocket",
                "status": "failed",
                "error": str(e)
            })
        
        # Determine overall success  
        all_stopped = all(r["status"] == "stopped" for r in results)
        
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "success": all_stopped,
                "message": f"Cookie grabber servers {'stopped successfully' if all_stopped else 'failed to stop'}",
                "operation": "stop",
                "timestamp": datetime.now().isoformat(),
                "services": results
            }, indent=2)
        )]
        
    except Exception as e:
        logger.error(f"Failed to stop cookie grabber servers: {e}")
        return [types.TextContent(
            type="text", 
            text=json.dumps({
                "success": False,
                "error": str(e),
                "operation": "stop"
            }, indent=2)
        )]

async def process_cookies(cookies: str, session: str) -> list[types.Content]:
    """Process cookie data and save to organized files."""
    try:
        logger.info(f"Processing cookies for session: {session}")
        
        # Create session directory
        session_dir = f"mcp_server/config/cookies/{session}"
        os.makedirs(session_dir, exist_ok=True)
        
        # Parse cookie data
        lines = cookies.strip().split('\n')
        processed_domains = []
        current_domain = None
        
        saved_files = []
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
                
            # Even lines (0, 2, 4...) are domains, odd lines (1, 3, 5...) are cookies
            if i % 2 == 0:  # Domain line
                current_domain = line
                logger.debug(f"Processing domain: {current_domain}")
            else:  # Cookie line
                if current_domain:
                    # Save cookies for this domain
                    cookie_file = os.path.join(session_dir, f"{current_domain}.txt")
                    
                    try:
                        with open(cookie_file, 'w', encoding='utf-8') as f:
                            f.write(line)
                        
                        saved_files.append({
                            "domain": current_domain,
                            "file": cookie_file,
                            "cookie_length": len(line),
                            "cookie_preview": line[:50] + ("..." if len(line) > 50 else "")
                        })
                        
                        processed_domains.append(current_domain)
                        logger.debug(f"Saved cookies for {current_domain} to {cookie_file}")
                        
                    except Exception as e:
                        logger.error(f"Failed to save cookies for {current_domain}: {e}")
                    
                    current_domain = None
        
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "success": True,
                "message": f"Successfully processed cookies for {len(processed_domains)} domains",
                "operation": "process", 
                "session": session,
                "timestamp": datetime.now().isoformat(),
                "processed_domains": processed_domains,
                "saved_files": saved_files,
                "session_directory": session_dir,
                "total_files": len(saved_files)
            }, indent=2)
        )]
        
    except Exception as e:
        logger.error(f"Failed to process cookies: {e}")
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "success": False,
                "error": str(e),
                "operation": "process",
                "session": session
            }, indent=2)
        )]
