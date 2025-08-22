"""
Test to demonstrate MCP event loop deadlock issue
"""
import asyncio
import json
import time
import requests
from mcp_server.tools.tool_registry import initialize_tools, run_tool

def test_mcp_deadlock_issue():
    """Demonstrate that MCP HTTP client cannot connect to MCP webhook server in same process."""
    initialize_tools()
    
    print("=== MCP EVENT LOOP DEADLOCK TEST ===")
    
    # Use existing webhook on port 9000
    test_url = "http://localhost:9000/cookies/test-session-deadlock"
    print(f"Testing URL: {test_url}")
    
    try:
        # Test 1: Python requests (should work)
        print("\n1. Testing Python requests...")
        try:
            response = requests.get(test_url, timeout=5)
            print(f"✅ Python requests SUCCESS: Status {response.status_code}, Length {len(response.text)}")
        except Exception as e:
            print(f"❌ Python requests FAILED: {e}")
        
        # Test 2: MCP HTTP client (should deadlock)
        print("\n2. Testing MCP HTTP client...")
        try:
            http_result = asyncio.run(run_tool("lng_http_client", {
                "mode": "request",
                "method": "GET", 
                "url": test_url,
                "timeout": 5
            }))
            http_data = json.loads(http_result[0].text)
            if http_data["result"]["success"]:
                print(f"✅ MCP HTTP client SUCCESS: Status {http_data['result']['status_code']}")
            else:
                print(f"❌ MCP HTTP client FAILED: {http_data['result']['error']}")
        except Exception as e:
            print(f"❌ MCP HTTP client EXCEPTION: {e}")
            
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
    
    print("\n=== CONCLUSION ===")
    print("If Python requests works but MCP HTTP client fails with timeout,")
    print("this confirms the MCP event loop deadlock issue.")

if __name__ == "__main__":
    test_mcp_deadlock_issue()
