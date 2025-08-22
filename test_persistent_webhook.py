"""
Solution: Proper webhook server with persistent event loop
"""
import asyncio
import json
import time
import threading
import requests
from mcp_server.tools.tool_registry import initialize_tools, run_tool

class PersistentWebhookServer:
    """Webhook server that runs in its own thread with persistent event loop."""
    
    def __init__(self):
        self.loop = None
        self.thread = None
        self.webhook_name = None
        self.running = False
    
    def start_webhook(self, name, port, path="/test"):
        """Start webhook in background thread with persistent event loop."""
        self.webhook_name = name
        
        def run_server():
            # Create new event loop for this thread
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            
            # Initialize tools in this thread
            initialize_tools()
            
            # Start webhook server
            try:
                result = self.loop.run_until_complete(run_tool("lng_webhook_server", {
                    "operation": "start",
                    "name": name,
                    "port": port,
                    "path": path
                }))
                
                webhook_data = json.loads(result[0].text)
                if webhook_data["success"]:
                    print(f"✅ Webhook started in background: {webhook_data['endpoint']}")
                    self.running = True
                    
                    # Keep event loop running
                    self.loop.run_forever()
                else:
                    print(f"❌ Failed to start webhook: {webhook_data}")
            except Exception as e:
                print(f"❌ Webhook thread error: {e}")
        
        # Start in background thread
        self.thread = threading.Thread(target=run_server, daemon=True)
        self.thread.start()
        
        # Wait for startup
        time.sleep(2)
        return self.running
    
    def stop_webhook(self):
        """Stop webhook server."""
        if self.loop and self.webhook_name:
            try:
                # Schedule stop in the event loop
                future = asyncio.run_coroutine_threadsafe(
                    run_tool("lng_webhook_server", {
                        "operation": "stop",
                        "name": self.webhook_name
                    }), self.loop
                )
                result = future.result(timeout=5)
                
                # Stop the event loop
                self.loop.call_soon_threadsafe(self.loop.stop)
                print("✅ Webhook stopped successfully")
                
            except Exception as e:
                print(f"❌ Error stopping webhook: {e}")

def test_persistent_webhook():
    """Test webhook with persistent event loop."""
    print("=== PERSISTENT WEBHOOK SERVER TEST ===")
    
    server = PersistentWebhookServer()
    
    try:
        # Start webhook
        if server.start_webhook("persistent-test", 8204):
            
            # Test HTTP requests
            test_url = "http://localhost:8204/test"
            print(f"\n🧪 Testing: {test_url}")
            
            try:
                response = requests.get(test_url, timeout=5)
                print(f"✅ SUCCESS: Status {response.status_code}, Length {len(response.text)}")
                
                # Test multiple requests
                for i in range(3):
                    response = requests.get(test_url, timeout=2)
                    print(f"✅ Request {i+1}: Status {response.status_code}")
                    
            except Exception as e:
                print(f"❌ HTTP test failed: {e}")
        else:
            print("❌ Failed to start webhook server")
            
    finally:
        server.stop_webhook()
        time.sleep(1)

if __name__ == "__main__":
    test_persistent_webhook()
