"""
Test webhook with persistent event loop in separate thread
"""
import asyncio
import json
import time
import threading
import requests
from mcp_server.tools.tool_registry import initialize_tools, run_tool

def run_webhook_in_thread(config, result_holder):
    """Run webhook server in dedicated thread with persistent event loop"""
    
    def run_server():
        # Create new event loop for this thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Initialize tools in this thread
            initialize_tools()
            
            # Start webhook server
            result = loop.run_until_complete(run_tool("lng_webhook_server", config))
            result_data = json.loads(result[0].text)
            result_holder['start_result'] = result_data
            
            if result_data["success"]:
                print(f"✅ Webhook started in thread: {result_data['endpoint']}")
                
                # Keep event loop running indefinitely
                try:
                    loop.run_forever()
                except KeyboardInterrupt:
                    pass
                    
        except Exception as e:
            result_holder['error'] = str(e)
            print(f"❌ Thread error: {e}")
        finally:
            try:
                # Stop webhook before closing loop
                stop_result = loop.run_until_complete(run_tool("lng_webhook_server", {
                    "operation": "stop",
                    "name": config["name"]
                }))
                print("🧹 Webhook stopped in thread")
            except:
                pass
            loop.close()
    
    # Start server in thread
    thread = threading.Thread(target=run_server, daemon=True)
    thread.start()
    return thread

def test_persistent_webhook():
    """Test webhook with persistent event loop"""
    print("=== PERSISTENT WEBHOOK TEST ===")
    
    config = {
        "operation": "start",
        "name": "persistent-test",
        "port": 8204,
        "path": "/test"
    }
    
    result_holder = {}
    
    # Start webhook in separate thread
    webhook_thread = run_webhook_in_thread(config, result_holder)
    
    # Wait for webhook to start
    time.sleep(3)
    
    if 'start_result' not in result_holder:
        print("❌ Webhook failed to start")
        return
        
    if not result_holder['start_result']['success']:
        print(f"❌ Webhook start failed: {result_holder['start_result']}")
        return
    
    # Test HTTP request
    test_url = "http://localhost:8204/test"
    print(f"Testing: {test_url}")
    
    try:
        response = requests.get(test_url, timeout=5)
        print(f"✅ HTTP SUCCESS: Status {response.status_code}, Length {len(response.text)}")
    except Exception as e:
        print(f"❌ HTTP FAILED: {e}")
    
    print("✅ Test completed - webhook thread continues running...")

if __name__ == "__main__":
    test_persistent_webhook()
    
    # Keep main thread alive for a bit to test the webhook
    print("Press Ctrl+C to exit...")
    try:
        time.sleep(30)
    except KeyboardInterrupt:
        print("Exiting...")
