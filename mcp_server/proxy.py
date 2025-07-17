#!/usr/bin/env python3
"""
Полноценный HTTP прокси сервер для MCP
Реализует полный цикл инициализации MCP и выполнения инструментов
"""

import json
import sys
import subprocess
import threading
import time
import logging
import asyncio
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

# Простое логирование
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MCPClient:
    """Клиент для работы с MCP сервером через правильный MCP протокол"""
    def __init__(self):
        self.session = None
        self.client = None
        self.streams = None
        self.initialized = False
        self.tools_list = []
        self.lock = threading.Lock()
        
    def start_and_initialize(self):
        """Синхронная инициализация MCP сервера"""
        try:
            logger.info("Starting MCP client connection...")
            
            # Простая инициализация в синхронном режиме
            import subprocess
            import json
            
            # Запускаем MCP сервер как подпроцесс
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
            
            # Отправляем initialize запрос
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
            
            # Читаем ответ на initialize
            response_line = self.process.stdout.readline().strip()
            if response_line:
                response_data = json.loads(response_line)
                if "error" not in response_data:
                    logger.info("Initialize successful")
                    
                    # Отправляем initialized notification
                    initialized_notification = {
                        "method": "notifications/initialized",
                        "jsonrpc": "2.0"
                    }
                    notification_json = json.dumps(initialized_notification) + "\n"
                    self.process.stdin.write(notification_json)
                    self.process.stdin.flush()
                    
                    # Запрашиваем список инструментов
                    tools_request = {
                        "jsonrpc": "2.0",
                        "id": 2,
                        "method": "tools/list",
                        "params": {}
                    }
                    tools_json = json.dumps(tools_request) + "\n"
                    self.process.stdin.write(tools_json)
                    self.process.stdin.flush()
                    
                    # Читаем список инструментов
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
        """Синхронный вызов инструмента через JSON-RPC"""
        try:
            if not self.initialized or not self.process:
                raise Exception("MCP client not initialized")
            
            logger.info(f"Calling tool: {tool_name} with arguments: {arguments}")
            
            # Создаем JSON-RPC запрос для вызова инструмента
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
            
            # Читаем ответ
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
        """Получение информации о доступных инструментах"""
        return {
            "tools": self.tools_list,
            "count": len(self.tools_list),
            "initialized": self.initialized
        }
    def stop(self):
        """Остановка MCP клиента"""
        try:
            if self.process:
                self.process.terminate()
                self.process.wait(timeout=5)
                logger.info("MCP client stopped")
        except Exception as e:
            logger.error(f"Error stopping MCP client: {e}")

# Глобальный экземпляр MCP клиента
mcp_client = MCPClient()

class MCPHandler(BaseHTTPRequestHandler):
    """Обработчик HTTP запросов для MCP"""
    
    def do_GET(self):
        """Обработка GET запросов"""
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
        """Обработка POST запросов"""
        if self.path == '/execute':
            try:
                # Читаем данные запроса
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                request_data = json.loads(post_data.decode('utf-8'))
                
                tool = request_data.get('tool')
                params = request_data.get('params', {})
                
                logger.info(f"Executing tool: {tool} with params: {params}")
                  # Выполняем реальный вызов инструмента через MCP
                start_time = time.time()
                mcp_result = mcp_client.call_tool(tool, params)
                execution_time = time.time() - start_time
                  # Обрабатываем результат
                if "result" in mcp_result and "content" in mcp_result["result"]:
                    # Успешное выполнение - извлекаем содержимое из JSON-RPC ответа
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    
                    # Извлекаем текст из результата JSON-RPC
                    result_text = []
                    content_items = mcp_result["result"]["content"]
                    
                    for item in content_items:
                        if isinstance(item, dict) and "text" in item:
                            # Пытаемся распарсить JSON из text поля
                            try:
                                parsed_json = json.loads(item["text"])
                                result_text.append(parsed_json)
                            except json.JSONDecodeError:
                                # Если не JSON, просто добавляем текст
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
                    # Ошибка выполнения
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
                    # Неожиданный формат ответа
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
        """Переопределяем логирование для более чистого вывода"""
        logger.info(format % args)

def run_server(host='127.0.0.1', port=8080):
    """Запуск HTTP сервера"""
    
    # Запускаем MCP сервер
    try:
        logger.info("🚀 Starting MCP HTTP Proxy Server...")
        
        # Используем синхронную инициализацию
        success = mcp_client.start_and_initialize()
        if not success:
            logger.error("❌ Failed to initialize MCP server")
            return
        
        logger.info(f"✅ MCP server initialized with {len(mcp_client.tools_list)} tools")
        
    except Exception as e:
        logger.error(f"❌ Failed to start MCP server: {e}")
        return
    
    # Запускаем HTTP сервер
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
    run_server()
