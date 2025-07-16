#!/usr/bin/env python3
"""
Очень простой HTTP сервер для тестирования MCP инструментов
"""

import json
import sys
import subprocess
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
import logging

# Простое логирование
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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
                "timestamp": time.time()
            }
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
                
                # Простая имитация выполнения инструмента
                if tool == "f1e_lng_count_words":
                    text = params.get('input_text', '')
                    word_count = len(text.split())
                    result = f"Word count: {word_count}"
                    
                elif tool == "f1e_lng_math_calculator":
                    expression = params.get('expression', '')
                    try:
                        # Простая математика (небезопасно для продакшена!)
                        result = str(eval(expression))
                    except:
                        result = "Error: Invalid expression"
                        
                else:
                    result = f"Tool '{tool}' executed with params: {params}"
                
                # Отправляем ответ
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                
                response = {
                    "success": True,
                    "result": [result],
                    "execution_time": 0.1,
                    "timestamp": time.time()
                }
                
                self.wfile.write(json.dumps(response).encode())
                logger.info(f"Tool {tool} executed successfully")
                
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
    server_address = (host, port)
    httpd = HTTPServer(server_address, MCPHandler)
    
    print(f"🚀 Starting test server on http://{host}:{port}")
    print("📍 Available endpoints:")
    print("  GET  /health  - Check server health")
    print("  POST /execute - Execute tools")
    print("⏹️  Press Ctrl+C to stop")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        httpd.server_close()

if __name__ == "__main__":
    run_server()
