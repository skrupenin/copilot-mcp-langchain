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
                # Универсальный pretty print для результатов
                for item in result.get("result", []):
                    if isinstance(item, (dict, list)):
                        # Используем json.dumps для красивого форматирования (как в Parameters)
                        formatted_json = json.dumps(item, indent=2, ensure_ascii=False)
                        print(formatted_json)
                    else:
                        # Для простых значений (строки, числа)
                        print(f"  {item}")
            else:
                print(f"❌ Error: {result.get('error', 'Unknown error')}")
                
        else:
            print(f"❌ HTTP Error {response.status_code}: {response.text}")
            
    except requests.exceptions.Timeout:
        print(f"⏰ Request timed out after {timeout} seconds")
    except requests.exceptions.ConnectionError:
        print("🔌 Connection error - is the proxy server running?")
        print("💡 Start it with: python mcp_server/proxy.py")
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
            mcp_running = health.get("mcp_initialized", False)  
            tools_count = health.get("tools_count", 0)
            
            print(f"🏥 Server Status: {status}")
            print(f"🔧 MCP Running: {mcp_running}")
            print(f"🛠️  Tools Available: {tools_count}")
            
            if status == "healthy" and mcp_running:
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

def list_tools(host: str = "127.0.0.1", port: int = 8080):
    """Получение списка доступных инструментов"""
    try:
        url = f"http://{host}:{port}/tools"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            tools_info = response.json()
            tools = tools_info.get("tools", [])
            count = tools_info.get("count", 0)
            initialized = tools_info.get("initialized", False)
            
            print(f"🔧 Available Tools ({count} total)")
            print(f"📊 MCP Initialized: {initialized}")
            print("="*60)
            
            for i, tool in enumerate(tools, 1):
                name = tool.get("name", "Unknown")
                description = tool.get("description", "No description")
                
                print(f"{i}. {name}")
                print(f"   📝 {description[:100]}{'...' if len(description) > 100 else ''}")
                
                # Показываем параметры
                schema = tool.get("inputSchema", {})
                properties = schema.get("properties", {})
                required = schema.get("required", [])
                
                if properties:
                    print("   📋 Parameters:")
                    for param_name, param_info in properties.items():
                        param_type = param_info.get("type", "unknown")
                        param_desc = param_info.get("description", "No description")
                        is_required = param_name in required
                        req_mark = "✅" if is_required else "⚪"
                        print(f"      {req_mark} {param_name} ({param_type}): {param_desc}")
                
                print()
                
            return True
        else:
            print(f"❌ HTTP Error {response.status_code}: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Server is not available")
        print("💡 Start it with: python mcp_proxy_full.py")
        return False
    except Exception as e:
        print(f"❌ Error listing tools: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Simple MCP Client")
    parser.add_argument("--host", default="127.0.0.1", help="Proxy server host")
    parser.add_argument("--port", type=int, default=8080, help="Proxy server port")
    parser.add_argument("--timeout", type=int, default=30, help="Request timeout in seconds")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Health check command
    health_parser = subparsers.add_parser("health", help="Check server health")
    
    # List tools command
    list_parser = subparsers.add_parser("list", help="List available tools")
    
    # Execute command
    exec_parser = subparsers.add_parser("exec", help="Execute a tool")
    exec_parser.add_argument("tool", help="Tool name to execute")
    exec_parser.add_argument("--params", help="JSON parameters for the tool")
    
    # Quick examples
    examples_parser = subparsers.add_parser("examples", help="Show usage examples")
    args = parser.parse_args()
    
    if args.command == "health":
        check_health(args.host, args.port)
        
    elif args.command == "list":
        list_tools(args.host, args.port)
        
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
        print("   python mcp_server/execute.py health")
        print()
        print("2. All tools info:")
        print('   python mcp_server/execute.py exec lng_get_tools_info --params \'{}\'')
        print()
        print("3. Count words in text:")
        print('   python mcp_server/execute.py exec lng_count_words --params \'{\\"input_text\\": \\"Hello world\\"}\'')
        print()
        print("4. Math calculation:")
        print('   python mcp_server/execute.py exec lng_math_calculator --params \'{\\"expression\\": \\"2 + 3 * 4\\"}\'')
        print()
        print("5. Chain of thought reasoning:")
        print('   python mcp_server/execute.py exec lng_chain_of_thought --params \'{\\"question\\": \\"What is 15 * 24?\\"}\'')
        print()
        
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
