#!/usr/bin/env python3
"""
Test MCP HTTP Client with MCP Webhook Server using thread_mode
"""
import asyncio
import time
from mcp_server.tools.tool_registry import run_tool

async def test_thread_mode_webhook():
    """Test MCP HTTP Client calling MCP Webhook Server with thread_mode"""
    
    print("=== MCP THREAD MODE WEBHOOK TEST ===")
    
    # Test MCP tools using run_tool function
    
    # 1. Start webhook with thread_mode
    print("1. Starting thread_mode webhook...")
    webhook_config = {
        "operation": "start",
        "name": "mcp-thread-test",
        "port": 8400,
        "path": "/thread-test",
        "persistent_mode": True,
        "thread_mode": True,  # This should solve the deadlock issue
        "response": {
            "message": "Thread Mode Webhook Success!",
            "timestamp": "{! datetime.now().isoformat() !}"
        }
    }
    
    try:
        webhook_result_raw = await run_tool("lng_webhook_server", webhook_config)
        # Extract JSON from MCP response
        import json
        webhook_result = json.loads(webhook_result_raw[0].text)
        print(f"Webhook result: {webhook_result}")
        
        if not webhook_result.get("success"):
            print("❌ Webhook failed to start")
            return
            
    except Exception as e:
        print(f"❌ Webhook start error: {e}")
        return
    
    # 2. Wait for webhook to initialize
    print("2. Waiting for thread-based webhook to initialize...")
    time.sleep(3)
    
    # 3. Test with MCP HTTP Client
    print("3. Testing with MCP HTTP Client...")
    try:
        http_result_raw = await run_tool("lng_http_client", {
            "url": "http://localhost:8400/thread-test",
            "method": "GET",
            "timeout": 10
        })
        
        # Extract JSON from MCP response
        http_result = json.loads(http_result_raw[0].text)
        print(f"✅ HTTP Success: {http_result}")
        
        if http_result.get("result", {}).get("success"):
            print("🎉 SUCCESS! MCP HTTP Client successfully called MCP Webhook Server with thread_mode!")
        else:
            print(f"❌ HTTP request failed: {http_result}")
            
    except Exception as e:
        print(f"❌ HTTP request exception: {e}")
    
    # 4. Check webhook status
    print("4. Checking webhook status...")
    try:
        status_result_raw = await run_tool("lng_webhook_server", {
            "operation": "status",
            "name": "mcp-thread-test"
        })
        status_result = json.loads(status_result_raw[0].text)
        print(f"Webhook status: {status_result}")
    except Exception as e:
        print(f"Status check error: {e}")
    
    # 5. Stop webhook
    print("5. Stopping webhook...")
    try:
        stop_result_raw = await run_tool("lng_webhook_server", {
            "operation": "stop",
            "name": "mcp-thread-test"
        })
        stop_result = json.loads(stop_result_raw[0].text)
        print(f"Stop result: {stop_result}")
    except Exception as e:
        print(f"Stop error: {e}")

if __name__ == "__main__":
    asyncio.run(test_thread_mode_webhook())
