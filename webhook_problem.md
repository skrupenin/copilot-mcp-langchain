# MCP Webhook Server Event Loop Problem Investigation

## Проблема

При попытке использовать MCP HTTP Client для вызова MCP Webhook Server возникает deadlock из-за конфликта event loops в asyncio.

## Суть проблемы

1. **MCP Webhook Server** создается через `asyncio.run()`, который создает новый event loop
2. **MCP HTTP Client** тоже использует asyncio для выполнения запросов
3. Когда MCP HTTP Client пытается обратиться к MCP Webhook Server, происходит deadlock
4. Проблема в том, что `asyncio.run()` создает временный event loop, который завершается после выполнения

## Симптомы

```
requests.exceptions.ReadTimeout: HTTPConnectionPool(host='127.0.0.1', port=8080): Read timed out.
```

## Исследование

### Скрипт 1: test_mcp_deadlock.py
```python
#!/usr/bin/env python3
import asyncio
from mcp_server.tools.tool_registry import get_tool

async def test_mcp_interaction():
    """Test MCP HTTP Client calling MCP Webhook Server"""
    
    # Get MCP tools
    webhook_tool = get_tool("lng_webhook_server")
    http_tool = get_tool("lng_http_client")
    
    print("Starting webhook server...")
    webhook_result = await webhook_tool({
        "operation": "start",
        "name": "test-webhook",
        "port": 8080,
        "path": "/test",
        "response": {"message": "Hello from MCP webhook!"}
    })
    print(f"Webhook result: {webhook_result}")
    
    # Give server time to start
    await asyncio.sleep(2)
    
    print("Making HTTP request...")
    try:
        http_result = await http_tool({
            "url": "http://127.0.0.1:8080/test",
            "method": "GET"
        })
        print(f"HTTP result: {http_result}")
    except Exception as e:
        print(f"HTTP request failed: {e}")
    
    # Stop webhook
    stop_result = await webhook_tool({
        "operation": "stop",
        "name": "test-webhook"
    })
    print(f"Stop result: {stop_result}")

if __name__ == "__main__":
    asyncio.run(test_mcp_interaction())
```

**Результат**: Успешное взаимодействие! MCP HTTP Client смог обратиться к MCP Webhook Server.

### Скрипт 2: test_mcp_http_vs_requests.py
```python
#!/usr/bin/env python3
import asyncio
import requests
import time
from mcp_server.tools.tool_registry import get_tool

async def test_with_mcp_http_client():
    """Test using MCP HTTP Client with external webhook"""
    webhook_tool = get_tool("lng_webhook_server") 
    http_tool = get_tool("lng_http_client")
    
    # Start webhook via MCP
    print("Starting webhook via MCP...")
    webhook_result = await webhook_tool({
        "operation": "start",
        "name": "test-webhook", 
        "port": 8080,
        "path": "/test",
        "response": {"message": "Hello from MCP webhook!"}
    })
    print(f"Webhook started: {webhook_result}")
    
    await asyncio.sleep(1)
    
    # Test with MCP HTTP Client
    print("Testing with MCP HTTP Client...")
    try:
        http_result = await http_tool({
            "url": "http://127.0.0.1:8080/test",
            "method": "GET",
            "timeout": 5
        })
        print(f"MCP HTTP Client result: {http_result}")
    except Exception as e:
        print(f"MCP HTTP Client failed: {e}")
    
    # Stop webhook
    await webhook_tool({"operation": "stop", "name": "test-webhook"})

def test_with_python_requests():
    """Test using Python requests with asyncio.run webhook"""
    import subprocess
    import time
    
    # Start webhook in subprocess
    print("Starting webhook in subprocess...")
    webhook_process = subprocess.Popen([
        'python', '-c', '''
import asyncio
from mcp_server.tools.tool_registry import get_tool

async def start_webhook():
    tool = get_tool("lng_webhook_server")
    result = await tool({
        "operation": "start",
        "name": "test-webhook",
        "port": 8080, 
        "path": "/test",
        "response": {"message": "Hello from subprocess webhook!"}
    })
    print(f"Webhook started: {result}")
    # Keep running
    await asyncio.sleep(10)

asyncio.run(start_webhook())
'''
    ])
    
    time.sleep(2)  # Wait for webhook to start
    
    # Test with requests
    print("Testing with Python requests...")
    try:
        response = requests.get("http://127.0.0.1:8080/test", timeout=5)
        print(f"Python requests result: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"Python requests failed: {e}")
    
    webhook_process.terminate()
    webhook_process.wait()

if __name__ == "__main__":
    print("=== Testing MCP HTTP Client with MCP Webhook ===")
    asyncio.run(test_with_mcp_http_client())
    
    print("\n=== Testing Python Requests with subprocess Webhook ===") 
    test_with_python_requests()
```

**Результат**: MCP HTTP Client работает с MCP Webhook в рамках одного event loop, но Python requests не может подключиться к webhook, созданному через `asyncio.run()`.

## Решение: Persistent Webhook Thread

### Скрипт 3: test_persistent_webhook_thread.py
```python
#!/usr/bin/env python3
import threading
import asyncio
import time
import requests
from mcp_server.tools.tool_registry import get_tool

def run_persistent_webhook():
    """Run webhook server in persistent event loop"""
    async def start_webhook():
        webhook_tool = get_tool("lng_webhook_server")
        
        # Start webhook
        result = await webhook_tool({
            "operation": "start",
            "name": "persistent-webhook",
            "port": 8080,
            "path": "/test",
            "response": {"message": "Hello from persistent webhook!"}
        })
        print(f"Webhook started: {result}")
        
        # Keep event loop running
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("Stopping webhook...")
            await webhook_tool({
                "operation": "stop", 
                "name": "persistent-webhook"
            })

    # Create new event loop for this thread
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        loop.run_until_complete(start_webhook())
    finally:
        loop.close()

def test_persistent_webhook():
    """Test webhook server running in separate thread"""
    
    # Start webhook in separate thread
    webhook_thread = threading.Thread(target=run_persistent_webhook, daemon=True)
    webhook_thread.start()
    
    # Wait for webhook to start
    time.sleep(2)
    
    # Test with Python requests
    try:
        response = requests.get("http://127.0.0.1:8080/test", timeout=5)
        print(f"✅ Success! Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"❌ Failed: {e}")
    
    print("Test completed.")

if __name__ == "__main__":
    test_persistent_webhook()
```

**Результат**: ✅ Успех! Python requests может успешно обращаться к webhook server, запущенному в отдельном thread с persistent event loop.

## Применение в тестах

Модифицированная функция в `mcp_server/tools/lng_webhook_server/stuff/test.py`:

```python
def test_context_variables_content(self):
    """Test context variables in actual HTTP response content"""
    import threading
    import time
    import requests
    
    def run_persistent_webhook():
        """Run webhook server in persistent event loop"""
        async def start_webhook():
            webhook_tool = get_tool("lng_webhook_server")
            
            # Start webhook with HTML route
            result = await webhook_tool({
                "operation": "start",
                "name": "test-context-webhook",
                "port": 8081,
                "path": "/test-context",
                "response": {
                    "status": 200,
                    "headers": {"Content-Type": "text/html"},
                    "body": """
<!DOCTYPE html>
<html>
<head><title>Context Test</title></head>
<body>
    <div>URL: {! url !}</div>
    <div>Method: {! request.method !}</div>
    <div>Query: {! JSON.stringify(query) !}</div>
    <div>Environment: {! env.PATH ? 'Found' : 'Not Found' !}</div>
</body>
</html>
                    """
                }
            })
            print(f"Webhook started: {result}")
            
            # Keep event loop running
            try:
                while True:
                    await asyncio.sleep(1)
            except:
                await webhook_tool({
                    "operation": "stop",
                    "name": "test-context-webhook"
                })

        # Create new event loop for this thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            loop.run_until_complete(start_webhook())
        finally:
            loop.close()

    # Start webhook in separate thread  
    webhook_thread = threading.Thread(target=run_persistent_webhook, daemon=True)
    webhook_thread.start()
    
    # Wait for webhook to start
    time.sleep(2)
    
    # Test HTTP request
    try:
        response = requests.get(
            "http://127.0.0.1:8081/test-context?param1=value1&param2=value2",
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Content:\n{response.text}")
        
        # Verify context variables were replaced
        self.assertEqual(response.status_code, 200)
        self.assertIn("URL: http://127.0.0.1:8081/test-context", response.text)
        self.assertIn("Method: GET", response.text) 
        self.assertIn("param1", response.text)
        self.assertIn("Environment: Found", response.text)
        
        print("✅ All context variables were properly replaced!")
        
    except Exception as e:
        self.fail(f"HTTP request failed: {e}")
    
    print("Context variables content test completed.")
```

## Выводы

1. **MCP Event Loop Conflict**: Основная проблема в том, что `asyncio.run()` создает временный event loop
2. **Persistent Thread Solution**: Запуск webhook server в отдельном thread с persistent event loop решает проблему  
3. **MCP Tools Interaction**: MCP tools могут успешно взаимодействовать друг с другом в рамках одного event loop
4. **Python Requests vs MCP HTTP**: Python requests более надежен для тестирования, чем MCP HTTP Client в рамках одного процесса

## Рекомендации

1. Для production webhook servers используйте persistent event loop в отдельном thread
2. Для тестирования webhook functionality используйте Python requests с thread-based webhook
3. MCP HTTP Client лучше использовать для внешних API, а не для внутренних MCP webhook servers
4. При создании long-running services через MCP учитывайте lifecycle event loop

## Статус скриптов

- ✅ `test_mcp_deadlock.py` - Демонстрирует успешное MCP-to-MCP взаимодействие
- ✅ `test_mcp_http_vs_requests.py` - Сравнивает разные подходы к тестированию  
- ✅ `test_persistent_webhook_thread.py` - Решение с persistent thread
- ✅ Модифицированная функция `test_context_variables_content` - Применение решения в тестах
