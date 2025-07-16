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

# Простое логирование
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MCPClient:
    """Клиент для работы с MCP сервером через subprocess"""
    
    def __init__(self):
        self.process = None
        self.initialized = False
        self.tools_list = []
        self.next_id = 1
        self.lock = threading.Lock()
        
    def get_next_id(self):
        """Получить следующий ID для JSON-RPC запроса"""
        with self.lock:
            current_id = self.next_id
            self.next_id += 1
            return current_id
    
    def start_mcp_server(self):
        """Запуск MCP сервера как подпроцесса"""
        try:
            logger.info("Starting MCP server subprocess...")
              # Запускаем MCP сервер как подпроцесс
            self.process = subprocess.Popen(
                [sys.executable, "-m", "mcp_server.server"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,  # Буферизация построчно
                universal_newlines=True,
                encoding='utf-8',  # Явно указываем UTF-8 кодировку
                errors='replace'   # Заменяем проблемные символы
            )
            
            logger.info(f"MCP server started with PID: {self.process.pid}")
            
            # Выполняем инициализацию MCP
            self.initialize_mcp()
            
        except Exception as e:
            logger.error(f"Failed to start MCP server: {e}")
            raise
    
    def initialize_mcp(self):
        """Выполнение полного цикла инициализации MCP"""
        try:
            # Шаг 1: Отправляем initialize запрос
            logger.info("Step 1: Sending initialize request...")
            initialize_request = {
                "jsonrpc": "2.0",
                "id": self.get_next_id(),
                "method": "initialize",
                "params": {
                    "protocolVersion": "2025-03-26",
                    "capabilities": {"roots": {"listChanged": True}},
                    "clientInfo": {
                        "name": "MCP HTTP Proxy",
                        "version": "1.0.0"
                    }
                }
            }
            
            response = self.send_request(initialize_request)
            if response and "error" not in response:
                logger.info("✅ Initialize request successful")
            else:
                logger.error(f"❌ Initialize request failed: {response}")
                return False
            
            # Шаг 2: Отправляем notifications/initialized
            logger.info("Step 2: Sending initialized notification...")
            initialized_notification = {
                "method": "notifications/initialized",
                "jsonrpc": "2.0"
            }
            
            # Для уведомлений не ждем ответа
            self.send_notification(initialized_notification)
            
            # Шаг 3: Получаем список инструментов
            logger.info("Step 3: Requesting tools list...")
            tools_request = {
                "jsonrpc": "2.0",
                "id": self.get_next_id(),
                "method": "tools/list",
                "params": {}
            }
            
            response = self.send_request(tools_request)
            if response and "result" in response:
                self.tools_list = response["result"].get("tools", [])
                logger.info(f"✅ Retrieved {len(self.tools_list)} tools")
                self.initialized = True
                return True
            else:
                logger.error(f"❌ Tools list request failed: {response}")
                return False
                
        except Exception as e:
            logger.error(f"MCP initialization failed: {e}")
            return False
    
    def send_request(self, request):
        """Отправка JSON-RPC запроса и получение ответа"""
        try:
            if not self.process:
                raise Exception("MCP server not started")
            
            # Отправляем запрос
            request_json = json.dumps(request) + "\n"
            logger.debug(f"Sending request: {request_json.strip()}")
            
            self.process.stdin.write(request_json)
            self.process.stdin.flush()
            
            # Читаем ответ
            response_line = self.process.stdout.readline()
            if not response_line:
                raise Exception("No response from MCP server")
            
            response = json.loads(response_line.strip())
            logger.debug(f"Received response: {response}")
            
            return response
            
        except Exception as e:
            logger.error(f"Error sending request: {e}")
            return {"error": {"message": str(e)}}
    
    def send_notification(self, notification):
        """Отправка уведомления (без ожидания ответа)"""
        try:
            if not self.process:
                raise Exception("MCP server not started")
            
            # Отправляем уведомление
            notification_json = json.dumps(notification) + "\n"
            logger.debug(f"Sending notification: {notification_json.strip()}")
            
            self.process.stdin.write(notification_json)
            self.process.stdin.flush()
            
        except Exception as e:
            logger.error(f"Error sending notification: {e}")
    
    def call_tool(self, tool_name, arguments):
        """Вызов конкретного инструмента"""
        try:
            if not self.initialized:
                raise Exception("MCP not initialized")
            
            # Создаем запрос на вызов инструмента
            call_request = {
                "jsonrpc": "2.0",
                "id": self.get_next_id(),
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": arguments
                }
            }
            
            logger.info(f"Calling tool: {tool_name} with arguments: {arguments}")
            response = self.send_request(call_request)
            
            if response and "result" in response:
                result = response["result"]
                logger.info(f"✅ Tool {tool_name} executed successfully")
                return result
            else:
                error_msg = response.get("error", {}).get("message", "Unknown error")
                logger.error(f"❌ Tool {tool_name} failed: {error_msg}")
                return {"error": error_msg}
                
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
        """Остановка MCP сервера"""
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
                logger.info("MCP server stopped")
            except subprocess.TimeoutExpired:
                self.process.kill()
                logger.warning("MCP server forcefully killed")
            except Exception as e:
                logger.error(f"Error stopping MCP server: {e}")

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
                if "error" in mcp_result:
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
                    # Успешное выполнение
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    
                    # Извлекаем текст из результата MCP
                    result_text = []
                    content = mcp_result.get("content", [])
                    
                    for item in content:
                        if isinstance(item, dict) and "text" in item:
                            result_text.append(item["text"])
                        else:
                            result_text.append(str(item))
                    
                    response = {
                        "success": True,
                        "result": result_text,
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
        mcp_client.start_mcp_server()
        
        if not mcp_client.initialized:
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
