#!/usr/bin/env python3
"""
Full-featured HTTP proxy server for MCP
Implements complete MCP initialization cycle and tool execution
"""

import json
import sys
import os
import subprocess
import threading
import time
import logging
import asyncio
import psutil  # Add psutil for process management
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

# Simple logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MCPClient:
    """Client for working with MCP server through proper MCP protocol"""
    def __init__(self):
        self.session = None
        self.client = None
        self.streams = None
        self.initialized = False
        self.tools_list = []
        self.lock = threading.Lock()
        
    def start_and_initialize(self):
        """Synchronous MCP server initialization"""
        try:
            logger.info("Starting MCP client connection...")
            
            # Simple initialization in synchronous mode
            import subprocess
            import json
            
            # Launch MCP server as subprocess
            self.process = subprocess.Popen(
                [sys.executable, "-m", "mcp_server.server"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True,
                encoding='utf-8',
                errors='replace'
            )
            
            logger.info("MCP server process started")
            
            # Send initialize request
            initialize_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "clientInfo": {"name": "proxy-client", "version": "1.0.0"}
                }
            }
            
            request_json = json.dumps(initialize_request) + "\n"
            self.process.stdin.write(request_json)
            self.process.stdin.flush()
            
            # Read initialize response
            response_line = self.process.stdout.readline().strip()
            if response_line:
                response_data = json.loads(response_line)
                if "error" not in response_data:
                    logger.info("Initialize successful")
                    
                    # Send initialized notification
                    initialized_notification = {
                        "method": "notifications/initialized",
                        "jsonrpc": "2.0"
                    }
                    notification_json = json.dumps(initialized_notification) + "\n"
                    self.process.stdin.write(notification_json)
                    self.process.stdin.flush()
                    
                    # Request list of tools
                    tools_request = {
                        "jsonrpc": "2.0",
                        "id": 2,
                        "method": "tools/list",
                        "params": {}
                    }
                    tools_json = json.dumps(tools_request) + "\n"
                    self.process.stdin.write(tools_json)
                    self.process.stdin.flush()
                    
                    # Read list of tools
                    tools_response = self.process.stdout.readline().strip()
                    if tools_response:
                        tools_data = json.loads(tools_response)
                        if "result" in tools_data and "tools" in tools_data["result"]:
                            self.tools_list = tools_data["result"]["tools"]
                            self.initialized = True
                            logger.info(f"✅ MCP initialized with {len(self.tools_list)} tools")
                            return True
            
            logger.error("Failed to initialize MCP properly")
            return False
            
        except Exception as e:
            logger.error(f"Failed to initialize MCP client: {e}")
            self.initialized = False
            return False
    def call_tool(self, tool_name, arguments):
        """Synchronous tool call via JSON-RPC"""
        try:
            if not self.initialized or not self.process:
                raise Exception("MCP client not initialized")
            
            logger.info(f"Calling tool: {tool_name} with arguments: {arguments}")
            
            # Create JSON-RPC request for tool call
            call_request = {
                "jsonrpc": "2.0",
                "id": 4,
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": arguments
                }
            }
            
            request_json = json.dumps(call_request) + "\n"
            self.process.stdin.write(request_json)
            self.process.stdin.flush()
            
            # Read response
            response_line = self.process.stdout.readline().strip()
            if response_line:
                response_data = json.loads(response_line)
                logger.info(f"✅ Tool {tool_name} executed successfully")
                return response_data
            else:
                raise Exception("No response from MCP server")
                
        except Exception as e:
            logger.error(f"Error calling tool {tool_name}: {e}")
            return {"error": str(e)}
    
    def get_tools_info(self):
        """Getting information about available tools"""
        return {
            "tools": self.tools_list,
            "count": len(self.tools_list),
            "initialized": self.initialized
        }
    def stop(self):
        """Stopping MCP client"""
        try:
            if self.process:
                self.process.terminate()
                self.process.wait(timeout=5)
                logger.info("MCP client stopped")
        except Exception as e:
            logger.error(f"Error stopping MCP client: {e}")

# Global MCP client instance
mcp_client = MCPClient()

def kill_existing_proxy_processes(port=8080):
    """Automatically terminates process using our port"""
    try:
        import os
        import socket
        
        logger.info(f"🔍 Checking if port {port} is in use...")
        
        # Check if port is in use
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)  # Timeout 1 second
        result = sock.connect_ex(('127.0.0.1', port))
        sock.close()
        
        if result != 0:
            # Port is free
            logger.info(f"✅ Port {port} is free, no cleanup needed")
            return
        
        # Port is in use - look for the process using it
        logger.info(f"🔄 Port {port} is in use, looking for the process...")
        killed_count = 0
        current_pid = os.getpid()
        for process in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                # Check process connections
                connections = process.net_connections(kind='inet')
                for conn in connections:
                    if (conn.laddr.port == port and 
                        conn.laddr.ip in ['127.0.0.1', '0.0.0.0'] and
                        conn.status == 'LISTEN'):
                        
                        # Don't terminate ourselves
                        if process.pid == current_pid:
                            logger.info(f"⏭️ Skipping current process PID: {current_pid}")
                            continue
                        
                        # Check that this is really our proxy server
                        cmdline = process.info.get('cmdline', [])
                        if any('proxy.py' in str(arg) for arg in cmdline):
                            logger.info(f"🔄 Terminating proxy process PID: {process.pid} using port {port}")
                            process.terminate()
                            killed_count += 1
                            
                            # Wait a bit for graceful shutdown
                            try:
                                process.wait(timeout=3)
                                logger.info(f"✅ Process PID: {process.pid} terminated gracefully")
                            except psutil.TimeoutExpired:
                                logger.warning(f"⚡ Force killing process PID: {process.pid}")
                                process.kill()
                            
                            # Check if port is freed
                            time.sleep(1)
                            test_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            test_sock.settimeout(1)
                            test_result = test_sock.connect_ex(('127.0.0.1', port))
                            test_sock.close()
                            
                            if test_result != 0:
                                logger.info(f"✅ Port {port} is now free")
                                return
                        else:
                            logger.warning(f"⚠️ Port {port} is used by non-proxy process PID: {process.pid}")
                        
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess, OSError):
                # Process is inaccessible or already terminated
                continue
        
        if killed_count == 0:
            logger.warning(f"⚠️ Port {port} is in use but couldn't find/terminate the process")
        else:
            logger.info(f"✅ Terminated {killed_count} process(es) using port {port}")
            
    except ImportError:
        logger.warning("⚠️ psutil not available, skipping port cleanup")
    except Exception as e:
        logger.error(f"❌ Error during port cleanup: {e}")

class MCPHandler(BaseHTTPRequestHandler):
    """HTTP request handler for MCP"""
    
    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                "status": "healthy",
                "mcp_initialized": mcp_client.initialized,
                "tools_count": len(mcp_client.tools_list),
                "timestamp": time.time()
            }
            self.wfile.write(json.dumps(response).encode())
            
        elif self.path == '/tools':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = mcp_client.get_tools_info()
            self.wfile.write(json.dumps(response).encode())
            
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        """Handle POST requests"""
        if self.path == '/execute':
            try:
                # Read request data
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                request_data = json.loads(post_data.decode('utf-8'))
                
                tool = request_data.get('tool')
                params = request_data.get('params', {})
                
                logger.info(f"Executing tool: {tool} with params: {params}")
                  # Execute real tool call via MCP
                start_time = time.time()
                mcp_result = mcp_client.call_tool(tool, params)
                execution_time = time.time() - start_time
                  # Process result
                if "result" in mcp_result and "content" in mcp_result["result"]:
                    # Successful execution - extract content from JSON-RPC response
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    
                    # Extract text from JSON-RPC result
                    result_text = []
                    content_items = mcp_result["result"]["content"]
                    
                    for item in content_items:
                        if isinstance(item, dict) and "text" in item:
                            # Try to parse JSON from text field
                            try:
                                parsed_json = json.loads(item["text"])
                                result_text.append(parsed_json)
                            except json.JSONDecodeError:
                                # If not JSON, just add text
                                result_text.append(item["text"])
                        else:
                            result_text.append(str(item))
                    
                    response = {
                        "success": True,
                        "result": result_text,
                        "execution_time": execution_time,
                        "timestamp": time.time()
                    }
                elif "error" in mcp_result:
                    # Execution error
                    self.send_response(500)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    
                    response = {
                        "success": False,
                        "error": mcp_result["error"],
                        "execution_time": execution_time,
                        "timestamp": time.time()
                    }
                else:
                    # Unexpected response format
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    
                    response = {
                        "success": True,
                        "result": [str(mcp_result)],
                        "execution_time": execution_time,
                        "timestamp": time.time()
                    }
                
                self.wfile.write(json.dumps(response).encode())
                logger.info(f"Tool {tool} processed in {execution_time:.2f}s")
                
            except Exception as e:
                logger.error(f"Error processing request: {e}")
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                
                response = {
                    "success": False,
                    "error": str(e),
                    "execution_time": 0.0,
                    "timestamp": time.time()
                }
                
                self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        """Override logging for cleaner output"""
        logger.info(format % args)

def run_server(host='127.0.0.1', port=8080):
    """Start HTTP server"""
    
    # Automatically terminate existing proxy processes
    kill_existing_proxy_processes()
    
    # Start MCP server
    try:
        logger.info("🚀 Starting MCP HTTP Proxy Server...")
        
        # Use synchronous initialization
        success = mcp_client.start_and_initialize()
        if not success:
            logger.error("❌ Failed to initialize MCP server")
            return
        
        logger.info(f"✅ MCP server initialized with {len(mcp_client.tools_list)} tools")
        
    except Exception as e:
        logger.error(f"❌ Failed to start MCP server: {e}")
        return
    
    # Start HTTP server
    server_address = (host, port)
    httpd = HTTPServer(server_address, MCPHandler)
    
    print(f"🚀 MCP HTTP Proxy Server running on http://{host}:{port}")
    print("📍 Available endpoints:")
    print("  GET  /health  - Check server health")
    print("  GET  /tools   - List available tools")
    print("  POST /execute - Execute tools")
    print("⏹️  Press Ctrl+C to stop")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Stopping server...")
        mcp_client.stop()
        httpd.server_close()
        print("✅ Server stopped")

if __name__ == "__main__":
    kill_existing_proxy_processes()
    run_server()
