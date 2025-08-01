import mcp.types as types
import json
import asyncio
import os
import subprocess
import sys
from pathlib import Path
from mcp_server.logging_config import setup_logging

logger = setup_logging("mcp_hotkey_listener", "INFO")

async def tool_info() -> dict:
    return {
        "description": """Manages a system-wide hotkey service that calls MCP tools when hotkeys are pressed.

This tool communicates with a background hotkey service to:
• Start/stop the hotkey service automatically
• Register global hotkeys that work across all applications
• Automatically trigger other MCP tools when hotkeys are pressed
• Manage multiple hotkey listeners simultaneously

**Hotkey Format:**
• Single keys: 'f1', 'f12', 'space', 'enter'
• With modifiers: 'ctrl+f1', 'ctrl+shift+s', 'alt+tab'
• Supported modifiers: ctrl/control, shift, alt, win/windows
• Supported keys: a-z, 0-9, f1-f12, space, enter, tab, esc, etc.

**Operations:**
• 'start_service': Start the background hotkey service
• 'stop_service': Stop the background hotkey service
• 'service_status': Check if the service is running
• 'register': Register a new hotkey listener (with conflict detection)
• 'unregister': Remove a specific hotkey listener
• 'list': List all active hotkey listeners
• 'unregister_all': Remove all hotkey listeners

**Error Handling:**
• Detects hotkey conflicts with other applications
• Suggests alternative hotkey combinations
• Shows list of currently registered hotkeys
• Auto-starts service if not running during registration

**Examples:**
Start service: operation="start_service"
Register: operation="register", hotkey="ctrl+shift+f1", tool_name="lng_count_words", tool_json={"input_text": "test"}
List registered hotkeys: operation="list"
Unregister specific: operation="unregister", hotkey="ctrl+shift+f1"
Stop service: operation="stop_service"
""",
        "schema": {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["start_service", "stop_service", "service_status", "register", "unregister", "list", "unregister_all"],
                    "description": "Operation to perform"
                },
                "hotkey": {
                    "type": "string",
                    "description": "Hotkey combination (e.g., 'ctrl+shift+f1', 'alt+space'). Required for register/unregister."
                },
                "tool_name": {
                    "type": "string", 
                    "description": "Name of the MCP tool to call when hotkey is pressed. Required for register."
                },
                "tool_json": {
                    "type": "object",
                    "description": "JSON parameters to pass to the tool. Required for register."
                }
            },
            "required": ["operation"]
        }
    }

async def run_tool(name: str, arguments: dict) -> list[types.Content]:
    operation = arguments.get("operation")
    hotkey = arguments.get("hotkey", "").strip()
    tool_name = arguments.get("tool_name", "").strip()
    tool_json = arguments.get("tool_json", {})
    
    # Путь к сервису
    service_script = Path(__file__).parent / "hotkey_service.py"
    
    try:
        if operation == "start_service":
            # Проверяем, не запущен ли уже сервис
            result = await run_service_command(service_script, ["status"])
            if result.get("success") and result.get("running"):
                return [types.TextContent(type="text", text=json.dumps({
                    "success": True,
                    "message": "Hotkey service is already running",
                    "pid": result.get("pid"),
                    "hotkeys_count": result.get("hotkeys_count", 0)
                }, ensure_ascii=False, indent=2))]
            
            # Запускаем сервис в фоне
            try:
                # Используем правильный путь к Python из виртуальной среды
                python_exe = Path(__file__).parent.parent.parent.parent.parent / ".virtualenv" / "Scripts" / "python.exe"
                if not python_exe.exists():
                    python_exe = sys.executable  # Fallback
                
                # Запуск в detached режиме (не блокирующий)
                if sys.platform == "win32":
                    # Windows - используем CREATE_NEW_PROCESS_GROUP и DETACHED_PROCESS
                    process = subprocess.Popen(
                        [str(python_exe), str(service_script), "daemon"],
                        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        stdin=subprocess.DEVNULL,
                        cwd=Path(__file__).parent.parent.parent.parent.parent  # Устанавливаем рабочую директорию
                    )
                else:
                    # Unix-like системы
                    process = subprocess.Popen(
                        [sys.executable, str(service_script), "daemon"],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        stdin=subprocess.DEVNULL,
                        preexec_fn=os.setpgrp
                    )
                
                logger.info(f"Started service process with PID: {process.pid}")
                
                # Ждем немного, чтобы сервис запустился
                await asyncio.sleep(3)
                
            except Exception as e:
                logger.error(f"Failed to start service process: {e}")
                return [types.TextContent(type="text", text=json.dumps({
                    "success": False,
                    "error": f"Failed to start service process: {str(e)}"
                }, ensure_ascii=False, indent=2))]
            
            # Проверяем, что сервис действительно запустился
            result = await run_service_command(service_script, ["status"])
            if result.get("success") and result.get("running"):
                return [types.TextContent(type="text", text=json.dumps({
                    "success": True,
                    "message": "Hotkey service started successfully",
                    "pid": result.get("pid")
                }, ensure_ascii=False, indent=2))]
            else:
                return [types.TextContent(type="text", text=json.dumps({
                    "success": False,
                    "error": "Failed to start hotkey service"
                }, ensure_ascii=False, indent=2))]
        
        elif operation == "stop_service":
            result = await run_service_command(service_script, ["stop"])
            return [types.TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]
        
        elif operation == "service_status":
            result = await run_service_command(service_script, ["status"])
            return [types.TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]
        
        elif operation == "register":
            if not hotkey:
                return [types.TextContent(type="text", text=json.dumps({
                    "success": False,
                    "error": "hotkey parameter is required for register operation"
                }, ensure_ascii=False, indent=2))]
            
            if not tool_name:
                return [types.TextContent(type="text", text=json.dumps({
                    "success": False,
                    "error": "tool_name parameter is required for register operation"
                }, ensure_ascii=False, indent=2))]
            
            # Проверяем, что сервис запущен
            status_result = await run_service_command(service_script, ["status"])
            if not (status_result.get("success") and status_result.get("running")):
                # Автоматически запускаем сервис
                start_result = await run_tool(name, {"operation": "start_service"})
                start_data = json.loads(start_result[0].text)
                if not start_data.get("success"):
                    return [types.TextContent(type="text", text=json.dumps({
                        "success": False,
                        "error": "Service is not running and failed to start automatically"
                    }, ensure_ascii=False, indent=2))]
            
            # Регистрируем хоткей
            tool_json_str = json.dumps(tool_json)
            result = await run_service_command(service_script, ["register", hotkey, tool_name, tool_json_str])
            
            # Если регистрация не удалась, добавляем дополнительную информацию
            if not result.get("success"):
                error_msg = result.get("error", "Unknown error")
                
                # Проверяем, если хоткей уже зарегистрирован
                if "already registered" in error_msg.lower() or "listener thread registration failed" in error_msg.lower():
                    result["error"] = f"Hotkey '{hotkey}' is already registered by another application or process. Please choose a different hotkey combination."
                    result["suggestion"] = f"Try using: 'ctrl+shift+{hotkey.split('+')[-1]}' or 'win+{hotkey.split('+')[-1]}' instead"
                    
                    # Показываем список уже зарегистрированных хоткеев
                    list_result = await run_service_command(service_script, ["list"])
                    if list_result.get("success"):
                        result["registered_hotkeys"] = list_result.get("hotkeys", [])
            
            return [types.TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]
        
        elif operation == "unregister":
            if not hotkey:
                return [types.TextContent(type="text", text=json.dumps({
                    "success": False,
                    "error": "hotkey parameter is required for unregister operation"
                }, ensure_ascii=False, indent=2))]
            
            result = await run_service_command(service_script, ["unregister", hotkey])
            return [types.TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]
        
        elif operation == "list":
            result = await run_service_command(service_script, ["list"])
            return [types.TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]
        
        elif operation == "unregister_all":
            result = await run_service_command(service_script, ["unregister_all"])
            return [types.TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]
        
        else:
            return [types.TextContent(type="text", text=json.dumps({
                "success": False,
                "error": f"Unknown operation: {operation}. Supported operations: start_service, stop_service, service_status, register, unregister, list, unregister_all"
            }, ensure_ascii=False, indent=2))]
    
    except Exception as e:
        logger.error(f"Error in hotkey_listener tool: {e}")
        return [types.TextContent(type="text", text=json.dumps({
            "success": False,
            "error": f"Internal error: {str(e)}"
        }, ensure_ascii=False, indent=2))]

async def run_service_command(service_script: Path, args: list) -> dict:
    """Выполняет команду к hotkey service и возвращает результат"""
    try:
        # Используем правильный путь к Python из виртуальной среды
        python_exe = Path(__file__).parent.parent.parent.parent.parent / ".virtualenv" / "Scripts" / "python.exe"
        if not python_exe.exists():
            python_exe = sys.executable  # Fallback
        
        cmd = [str(python_exe), str(service_script)] + args
        logger.info(f"Executing service command: {cmd}")
        logger.info(f"Working directory: {os.getcwd()}")
        
        # Запускаем команду синхронно для простых команд (status, list, etc.)
        logger.info(f"About to run subprocess with timeout=30")
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,  # Увеличиваем таймаут до 30 секунд
            cwd=Path(__file__).parent.parent.parent.parent.parent  # Устанавливаем рабочую директорию в корень проекта
        )
        logger.info(f"Subprocess completed with returncode: {result.returncode}")
        
        if result.returncode == 0:
            try:
                response_data = json.loads(result.stdout)
                logger.info(f"Service command result: {response_data}")
                return response_data
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse service response: {e}")
                return {
                    "success": False,
                    "error": f"Invalid JSON response from service: {result.stdout}"
                }
        else:
            error_msg = result.stderr if result.stderr else f"Command failed with exit code {result.returncode}"
            logger.error(f"Service command failed: {error_msg}")
            return {
                "success": False,
                "error": error_msg
            }
    
    except subprocess.TimeoutExpired:
        logger.error("Service command timed out")
        return {
            "success": False,
            "error": "Service command timed out"
        }
    except Exception as e:
        logger.error(f"Error executing service command: {e}")
        return {
            "success": False,
            "error": f"Failed to execute service command: {str(e)}"
        }
