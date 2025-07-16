#!/usr/bin/env python3
"""
Простой клиент для быстрых запросов к MCP серверу через HTTP proxy
"""

import json
import sys
import time
import argparse
import requests
from typing import Dict, Any, Optional

def make_request(tool: str, params: Dict[str, Any] = None, host: str = "127.0.0.1", port: int = 8080, timeout: int = 30):
    """Отправка запроса к proxy серверу"""
    if params is None:
        params = {}
    
    url = f"http://{host}:{port}/execute"
    payload = {
        "tool": tool,
        "params": params
    }
    
    try:
        print(f"🚀 Executing tool: {tool}")
        print(f"📝 Parameters: {json.dumps(params, indent=2)}")
        print("⏳ Waiting for response...")
        
        start_time = time.time()
        response = requests.post(url, json=payload, timeout=timeout)
        end_time = time.time()
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"✅ Success! (took {end_time - start_time:.2f}s)")
            print("📄 Result:")
            
            if result.get("success"):
                # Красивый вывод результата
                for item in result.get("result", []):
                    print(f"  {item}")
            else:
                print(f"❌ Error: {result.get('error', 'Unknown error')}")
                
        else:
            print(f"❌ HTTP Error {response.status_code}: {response.text}")
            
    except requests.exceptions.Timeout:
        print(f"⏰ Request timed out after {timeout} seconds")
    except requests.exceptions.ConnectionError:
        print("🔌 Connection error - is the proxy server running?")
        print("💡 Start it with: python simple_proxy.py")
    except Exception as e:
        print(f"❌ Error: {e}")

def check_health(host: str = "127.0.0.1", port: int = 8080):
    """Проверка состояния сервера"""
    try:
        url = f"http://{host}:{port}/health"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            health = response.json()
            status = health.get("status", "unknown")
            mcp_executening = health.get("mcp_executening", False)
            
            print(f"🏥 Server Status: {status}")
            print(f"🔧 MCP Running: {mcp_executening}")
            
            if status == "healthy" and mcp_executening:
                print("✅ System is ready!")
                return True
            else:
                print("⚠️  System is not fully ready")
                return False
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Server is not available")
        print("💡 Start it with: python simple_proxy.py")
        return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Simple MCP Client")
    parser.add_argument("--host", default="127.0.0.1", help="Proxy server host")
    parser.add_argument("--port", type=int, default=8080, help="Proxy server port")
    parser.add_argument("--timeout", type=int, default=30, help="Request timeout in seconds")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Health check command
    health_parser = subparsers.add_parser("health", help="Check server health")
    
    # Execute command
    exec_parser = subparsers.add_parser("exec", help="Execute a tool")
    exec_parser.add_argument("tool", help="Tool name to execute")
    exec_parser.add_argument("--params", help="JSON parameters for the tool")
    
    # Quick examples
    examples_parser = subparsers.add_parser("examples", help="Show usage examples")
    
    args = parser.parse_args()
    
    if args.command == "health":
        check_health(args.host, args.port)
        
    elif args.command == "exec":
        params = {}
        if args.params:
            try:
                params = json.loads(args.params)
            except json.JSONDecodeError as e:
                print(f"❌ Invalid JSON parameters: {e}")
                sys.exit(1)
        
        make_request(args.tool, params, args.host, args.port, args.timeout)
        
    elif args.command == "examples":
        print("🔧 Usage Examples:")
        print()
        print("1. Check server health:")
        print("   python mcp_execute.py health")
        print()
        print("2. All tools info:")
        print('   python mcp_execute.py exec f1e_lng_get_tools_info --params \'{}\'')
        print()
        print("3. Count words in text:")
        print('   python mcp_execute.py exec f1e_lng_count_words --params \'{\\"input_text\\": \\"Hello world\\"}\'')
        print()
        print("4. Math calculation:")
        print('   python mcp_execute.py exec f1e_lng_math_calculator --params \'{\\"expression\\": \\"2 + 3 * 4\\"}\'')
        print()
        print("5. Chain of thought reasoning:")
        print('   python mcp_execute.py exec f1e_lng_chain_of_thought --params \'{\\"question\\": \\"What is 15 * 24?\\"}\'')
        print()
        
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
