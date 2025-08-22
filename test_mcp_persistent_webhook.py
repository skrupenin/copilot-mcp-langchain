#!/usr/bin/env python3
"""
Test MCP HTTP Client calling MCP Webhook with persistent_mode
"""
import asyncio
import time
from mcp_server.tools.tool_registry import initialize_tools, run_tool

async def test_mcp_persistent_webhook():
    """Test MCP HTTP Client with persistent MCP Webhook Server"""
    
    # Initialize tools
    initialize_tools()
    
    print("=== MCP PERSISTENT WEBHOOK TEST ===")
    
    # Start webhook with persistent_mode
    print("1. Starting persistent webhook...")
    webhook_result = await run_tool("lng_webhook_server", {
        "operation": "start",
        "name": "mcp-test-persistent",
        "port": 8300,
        "path": "/mcp-test",
        "persistent_mode": True,  # This should enable background task mode
        "response": {
            "message": "MCP Persistent Webhook Working!"
        }
    })
    
    print(f"Webhook result: {webhook_result[0].text}")
    
    # Wait for webhook to fully initialize
    print("2. Waiting for webhook to initialize...")
    await asyncio.sleep(3)
    
    # Test with MCP HTTP Client
    print("3. Testing with MCP HTTP Client...")
    try:
        http_result = await run_tool("lng_http_client", {
            "url": "http://localhost:8300/mcp-test",
            "method": "GET",
            "timeout": 10
        })
        
        print(f"✅ HTTP Success: {http_result[0].text}")
        
    except Exception as e:
        print(f"❌ HTTP Failed: {e}")
    
    # Check webhook status
    print("4. Checking webhook status...")
    status_result = await run_tool("lng_webhook_server", {
        "operation": "list"
    })
    print(f"Webhook status: {status_result[0].text}")
    
    # Cleanup
    print("5. Stopping webhook...")
    stop_result = await run_tool("lng_webhook_server", {
        "operation": "stop", 
        "name": "mcp-test-persistent"
    })
    print(f"Stop result: {stop_result[0].text}")

if __name__ == "__main__":
    asyncio.run(test_mcp_persistent_webhook())
