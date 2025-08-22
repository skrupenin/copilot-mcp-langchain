import asyncio
import json
from mcp_server.tools.tool_registry import initialize_tools, run_tool

initialize_tools()

print('=== DETAILED WEBHOOK INVESTIGATION ===')

# Create webhook
result = asyncio.run(run_tool('lng_webhook_server', {
    'operation': 'start',
    'name': 'debug-investigation',
    'port': 8203,
    'path': '/test'
}))

data = json.loads(result[0].text)
print('Webhook creation:', data['success'])
print('Server info:', data.get('config', {}).get('server_info', 'N/A'))

# Check list
list_result = asyncio.run(run_tool('lng_webhook_server', {'operation': 'list'}))
list_data = json.loads(list_result[0].text)
print('Active webhooks:', list_data['active_webhooks'])

# Check if event loop is running
import threading
import os
print('Current thread:', threading.current_thread().name)
print('Process ID:', os.getpid())

try:
    loop = asyncio.get_running_loop()
    print('Event loop is running:', loop)
except RuntimeError:
    print('No running event loop')

# Try HTTP request
import requests
import time
time.sleep(2)
try:
    response = requests.get('http://localhost:8203/test', timeout=3)
    print('HTTP SUCCESS:', response.status_code)
except Exception as e:
    print('HTTP FAILED:', str(e))
