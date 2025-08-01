#!/usr/bin/env python3
"""
Hotkey Service - постоянно работающий сервис для обработки хоткеев
Поддерживает командную строку и интерактивный режим
"""

import asyncio
import json
import sys
import time
import signal
import threading
import os
import logging
import argparse
import tempfile
import uuid
from pathlib import Path

# Добавляем пути к mcp_server в sys.path
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from mcp_server.tools.lng_winapi.hotkey_listener.hotkey_core import (
    register_hotkey, unregister_hotkey, list_hotkeys, unregister_all_hotkeys
)
from mcp_server.logging_config import setup_logging

logger = setup_logging("hotkey_service", logging.INFO)

# Файлы для хранения PID запущенного сервиса и IPC
# Используем проектную директорию для постоянного хранения хоткеев
PROJECT_HOTKEYS_DIR = project_root / "mcp_server" / "hotkeys"
PROJECT_HOTKEYS_DIR.mkdir(exist_ok=True)

# Временные файлы для управления процессом (остаются в temp)
PID_FILE = Path(tempfile.gettempdir()) / "hotkey_service.pid"

# Постоянные файлы для хранения состояния (в проектной директории)
STATUS_FILE = PROJECT_HOTKEYS_DIR / "hotkey_service_status.json"

# IPC файлы для взаимодействия между процессами (временные)
COMMAND_DIR = Path(tempfile.gettempdir()) / "hotkey_service_commands"
RESPONSE_DIR = Path(tempfile.gettempdir()) / "hotkey_service_responses"

class HotkeyService:
    def __init__(self):
        self.running = True
        self.hotkeys = {}
        self.loop = None
        # Создаем директории для IPC
        COMMAND_DIR.mkdir(exist_ok=True)
        RESPONSE_DIR.mkdir(exist_ok=True)
        # Убеждаемся, что директория для хоткеев существует
        PROJECT_HOTKEYS_DIR.mkdir(exist_ok=True)
        
    def signal_handler(self, signum, frame):
        logger.info(f"Получен сигнал {signum}, завершаем работу...")
        self.running = False
        if self.loop:
            self.loop.stop()
        
    async def register_hotkey(self, hotkey: str, tool_name: str, tool_json: dict):
        """Регистрирует хоткей"""
        try:
            from mcp_server.tools.lng_winapi.hotkey_listener.hotkey_core import register_hotkey as core_register
            result = await core_register(hotkey, tool_name, tool_json)
            
            if result.get("success"):
                self.hotkeys[hotkey] = {
                    "tool_name": tool_name,
                    "tool_json": tool_json,
                    "hotkey_id": result.get("hotkey_id")
                }
                logger.info(f"Хоткей {hotkey} зарегистрирован успешно")
                self.save_status()
                return result
            else:
                logger.error(f"Ошибка регистрации хоткея {hotkey}: {result}")
                return result
        except Exception as e:
            logger.error(f"Исключение при регистрации хоткея {hotkey}: {e}")
            return {"success": False, "error": str(e)}
        
    async def unregister_hotkey(self, hotkey: str):
        """Отменяет регистрацию хоткея"""
        try:
            from mcp_server.tools.lng_winapi.hotkey_listener.hotkey_core import unregister_hotkey as core_unregister
            result = await core_unregister(hotkey)
            
            if result.get("success"):
                if hotkey in self.hotkeys:
                    del self.hotkeys[hotkey]
                self.save_status()
                return result
            else:
                return result
        except Exception as e:
            logger.error(f"Исключение при отмене регистрации хоткея {hotkey}: {e}")
            return {"success": False, "error": str(e)}
        
    async def list_hotkeys(self):
        """Показывает активные хоткеи"""
        try:
            from mcp_server.tools.lng_winapi.hotkey_listener.hotkey_core import list_hotkeys as core_list
            result = await core_list()
            return result
        except Exception as e:
            logger.error(f"Исключение при получении списка хоткеев: {e}")
            return {"success": False, "error": str(e)}
        
    async def unregister_all(self):
        """Очищает все хоткеи"""
        try:
            from mcp_server.tools.lng_winapi.hotkey_listener.hotkey_core import unregister_all_hotkeys as core_unregister_all
            result = await core_unregister_all()
            
            if result.get("success"):
                self.hotkeys.clear()
                self.save_status()
                return result
            else:
                return result
        except Exception as e:
            logger.error(f"Исключение при очистке всех хоткеев: {e}")
            return {"success": False, "error": str(e)}
    
    async def save_status(self):
        """Сохраняет текущий статус в файл, синхронизируясь с реальным состоянием core"""
        try:
            # Получаем реальное состояние из core
            from mcp_server.tools.lng_winapi.hotkey_listener.hotkey_core import list_hotkeys as core_list
            core_result = await core_list()
            
            # Преобразуем в формат для сохранения
            hotkeys_for_save = {}
            if core_result.get("success"):
                for hotkey_info in core_result.get("active_hotkeys", []):
                    hotkey = hotkey_info["hotkey"]
                    hotkeys_for_save[hotkey] = {
                        "tool_name": hotkey_info["tool_name"],
                        "tool_json": hotkey_info["tool_json"],
                        "hotkey_id": hotkey_info["hotkey_id"]
                    }
            
            # Синхронизируем self.hotkeys с реальным состоянием
            self.hotkeys = hotkeys_for_save
            
            status = {
                "pid": os.getpid(),
                "hotkeys": self.hotkeys,
                "running": self.running,
                "timestamp": time.time()
            }
            with open(STATUS_FILE, 'w', encoding='utf-8') as f:
                json.dump(status, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Ошибка сохранения статуса: {e}")
            
    def save_status_sync(self):
        """Синхронная версия сохранения статуса (для совместимости)"""
        try:
            status = {
                "pid": os.getpid(),
                "hotkeys": self.hotkeys,
                "running": self.running,
                "timestamp": time.time()
            }
            with open(STATUS_FILE, 'w', encoding='utf-8') as f:
                json.dump(status, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Ошибка сохранения статуса: {e}")
            
    async def load_status(self):
        """Загружает статус из файла и восстанавливает хоткеи"""
        try:
            if STATUS_FILE.exists():
                with open(STATUS_FILE, 'r', encoding='utf-8') as f:
                    status = json.load(f)
                    saved_hotkeys = status.get("hotkeys", {})
                    logger.info(f"Найдено {len(saved_hotkeys)} сохраненных хоткеев")
                    
                    # Восстанавливаем хоткеи в core
                    restored_count = 0
                    for hotkey, hotkey_info in saved_hotkeys.items():
                        try:
                            tool_name = hotkey_info.get("tool_name")
                            tool_json = hotkey_info.get("tool_json")
                            
                            if tool_name and tool_json:
                                result = await self.register_hotkey(hotkey, tool_name, tool_json)
                                if result.get("success"):
                                    restored_count += 1
                                    logger.info(f"Восстановлен хоткей: {hotkey}")
                                else:
                                    logger.error(f"Не удалось восстановить хоткей {hotkey}: {result}")
                        except Exception as e:
                            logger.error(f"Ошибка восстановления хоткея {hotkey}: {e}")
                    
                    logger.info(f"Восстановлено {restored_count}/{len(saved_hotkeys)} хоткеев")
        except Exception as e:
            logger.error(f"Ошибка загрузки статуса: {e}")
            
    async def run_daemon(self):
        """Запуск в режиме daemon (фоновый процесс)"""
        # Записываем PID
        with open(PID_FILE, 'w') as f:
            f.write(str(os.getpid()))
        
        logger.info(f"Hotkey Service запущен в daemon режиме (PID: {os.getpid()})")
        
        # Устанавливаем обработчик сигналов
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        # Загружаем предыдущий статус
        await self.load_status()
        
        # Запускаем обработку IPC команд в отдельной задаче
        ipc_task = asyncio.create_task(self.handle_ipc_commands())
        
        # Основной цикл - просто ждем
        try:
            while self.running:
                await self.save_status()
                await asyncio.sleep(5)  # Обновляем статус каждые 5 секунд
        except Exception as e:
            logger.error(f"Ошибка в daemon цикле: {e}")
        finally:
            await self.cleanup()
            ipc_task.cancel()
    
    async def handle_ipc_commands(self):
        """Обработка IPC команд от клиентов"""
        while self.running:
            try:
                # Проверяем новые команды
                for command_file in COMMAND_DIR.glob("*.json"):
                    try:
                        with open(command_file, 'r', encoding='utf-8') as f:
                            command_data = json.load(f)
                        
                        # Обрабатываем команду
                        response = await self.process_command(command_data)
                        
                        # Сохраняем ответ
                        response_file = RESPONSE_DIR / f"{command_file.stem}.json"
                        with open(response_file, 'w', encoding='utf-8') as f:
                            json.dump(response, f, ensure_ascii=False, indent=2)
                        
                        # Удаляем обработанную команду
                        command_file.unlink()
                        
                    except Exception as e:
                        logger.error(f"Ошибка обработки команды {command_file}: {e}")
                        try:
                            command_file.unlink()
                        except:
                            pass
                
                await asyncio.sleep(0.1)  # Небольшая пауза
            except Exception as e:
                logger.error(f"Ошибка в IPC обработчике: {e}")
                await asyncio.sleep(1)
    
    async def process_command(self, command_data):
        """Обработка отдельной команды"""
        try:
            command = command_data.get('command')
            args = command_data.get('args', {})
            
            if command == 'register':
                hotkey = args.get('hotkey')
                tool_name = args.get('tool_name')
                tool_json = args.get('tool_json')
                return await self.register_hotkey(hotkey, tool_name, tool_json)
            
            elif command == 'unregister':
                hotkey = args.get('hotkey')
                return await self.unregister_hotkey(hotkey)
            
            elif command == 'list':
                return await self.list_hotkeys()
            
            elif command == 'unregister_all':
                return await self.unregister_all_hotkeys()
            
            else:
                return {
                    "success": False,
                    "error": f"Unknown command: {command}"
                }
        except Exception as e:
            logger.error(f"Ошибка выполнения команды: {e}")
            return {
                "success": False,
                "error": str(e)
            }
            
    async def run_interactive(self):
        """Запуск в интерактивном режиме"""
        logger.info("Hotkey Service запущен в интерактивном режиме")
        print("📋 Команды:")
        print("  - register <hotkey> <tool_name> <json>  - зарегистрировать хоткей")
        print("  - unregister <hotkey>                   - отменить регистрацию хоткея")
        print("  - list                                  - показать активные хоткеи") 
        print("  - clear                                 - очистить все хоткеи")
        print("  - quit                                  - выйти")
        print("  - Ctrl+C                               - выйти")
        print()
        
        # Устанавливаем обработчик сигналов
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        # Загружаем предыдущий статус
        await self.load_status()
        
        while self.running:
            try:
                # Простой интерактивный интерфейс
                cmd = input("🎮 Введите команду: ").strip().split()
                
                if not cmd:
                    continue
                    
                if cmd[0] == "quit":
                    break
                elif cmd[0] == "list":
                    result = await self.list_hotkeys()
                    print(json.dumps(result, indent=2, ensure_ascii=False))
                elif cmd[0] == "clear":
                    result = await self.unregister_all()
                    print(json.dumps(result, indent=2, ensure_ascii=False))
                elif cmd[0] == "unregister" and len(cmd) >= 2:
                    hotkey = cmd[1]
                    result = await self.unregister_hotkey(hotkey)
                    print(json.dumps(result, indent=2, ensure_ascii=False))
                elif cmd[0] == "register" and len(cmd) >= 4:
                    hotkey = cmd[1]
                    tool_name = cmd[2]
                    try:
                        tool_json = json.loads(" ".join(cmd[3:]))
                        result = await self.register_hotkey(hotkey, tool_name, tool_json)
                        print(json.dumps(result, indent=2, ensure_ascii=False))
                    except json.JSONDecodeError as e:
                        print(f"❌ Ошибка JSON: {e}")
                else:
                    print("❌ Неизвестная команда или неправильные аргументы")
                    
            except KeyboardInterrupt:
                break
            except EOFError:
                break
            except Exception as e:
                logger.error(f"Ошибка в интерактивном режиме: {e}")
                
        await self.cleanup()
        
    async def cleanup(self):
        """Очистка ресурсов"""
        try:
            await self.unregister_all()
            logger.info("Все хоткеи очищены")
        except Exception as e:
            logger.error(f"Ошибка при очистке: {e}")
        finally:
            # Удаляем PID файл
            try:
                if PID_FILE.exists():
                    PID_FILE.unlink()
            except Exception as e:
                logger.error(f"Ошибка удаления PID файла: {e}")
        
        logger.info("Hotkey Service завершён")

def is_service_running():
    """Проверяет, запущен ли сервис"""
    try:
        if not PID_FILE.exists():
            return False, None
        
        with open(PID_FILE, 'r') as f:
            pid = int(f.read().strip())
        
        # Проверяем, существует ли процесс
        import platform
        import subprocess
        
        if platform.system() == "Windows":
            try:
                # В Windows используем tasklist для проверки процесса
                result = subprocess.run(['tasklist', '/FI', f'PID eq {pid}'], 
                                      capture_output=True, text=True, check=True)
                if str(pid) in result.stdout:
                    return True, pid
                else:
                    # Процесс не существует, удаляем старый PID файл
                    PID_FILE.unlink()
                    return False, None
            except subprocess.CalledProcessError:
                # Процесс не существует, удаляем старый PID файл
                PID_FILE.unlink()
                return False, None
        else:
            # Unix-like системы
            try:
                os.kill(pid, 0)  # Не убивает процесс, просто проверяет существование
                return True, pid
            except OSError:
                # Процесс не существует, удаляем старый PID файл
                PID_FILE.unlink()
                return False, None
            
    except Exception as e:
        logger.error(f"Ошибка проверки статуса сервиса: {e}")
        return False, None

def stop_service():
    """Останавливает запущенный сервис"""
    running, pid = is_service_running()
    if not running:
        return {"success": False, "error": "Service is not running"}
    
    try:
        import subprocess
        import platform
        
        if platform.system() == "Windows":
            # В Windows используем taskkill
            try:
                subprocess.run(['taskkill', '/F', '/PID', str(pid)], 
                             check=True, capture_output=True, text=True)
                
                # Ждем завершения
                for _ in range(10):  # Ждем до 5 секунд
                    if not is_service_running()[0]:
                        return {"success": True, "message": f"Service (PID: {pid}) stopped successfully"}
                    time.sleep(0.5)
                    
                return {"success": False, "error": f"Failed to stop service (PID: {pid})"}
                
            except subprocess.CalledProcessError as e:
                return {"success": False, "error": f"Failed to stop service (PID: {pid}): {e.stderr}"}
        else:
            # Unix-like системы
            os.kill(pid, signal.SIGTERM)
            
            # Ждем завершения
            for _ in range(10):  # Ждем до 5 секунд
                if not is_service_running()[0]:
                    return {"success": True, "message": f"Service (PID: {pid}) stopped successfully"}
                time.sleep(0.5)
            
            # Если не завершился, принудительно
            try:
                os.kill(pid, signal.SIGKILL)
                return {"success": True, "message": f"Service (PID: {pid}) force killed"}
            except:
                pass
            
            return {"success": False, "error": f"Failed to stop service (PID: {pid})"}
        
    except Exception as e:
        return {"success": False, "error": f"Error stopping service: {e}"}

async def handle_command(args):
    """Обработка команд для запущенного сервиса"""
    service = HotkeyService()
    
    if args.command == 'register':
        try:
            tool_json = json.loads(args.tool_json)
            result = await service.register_hotkey(args.hotkey, args.tool_name, tool_json)
            return result
        except json.JSONDecodeError as e:
            return {"success": False, "error": f"Invalid JSON: {e}"}
    
    elif args.command == 'unregister':
        result = await service.unregister_hotkey(args.hotkey)
        return result
    
    elif args.command == 'list':
        result = await service.list_hotkeys()
        return result
    
    elif args.command == 'unregister_all':
        result = await service.unregister_all()
        return result
    
    else:
        return {"success": False, "error": f"Unknown command: {args.command}"}

def send_command_to_daemon(command, args_dict):
    """Отправляет команду в daemon через IPC"""
    try:
        # Создаем уникальный ID для команды
        command_id = str(uuid.uuid4())
        
        # Подготавливаем данные команды
        command_data = {
            'command': command,
            'args': args_dict
        }
        
        # Сохраняем команду в файл
        command_file = COMMAND_DIR / f"{command_id}.json"
        with open(command_file, 'w', encoding='utf-8') as f:
            json.dump(command_data, f, ensure_ascii=False, indent=2)
        
        # Ждем ответа
        response_file = RESPONSE_DIR / f"{command_id}.json"
        timeout = 10  # 10 секунд таймаут
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if response_file.exists():
                with open(response_file, 'r', encoding='utf-8') as f:
                    response = json.load(f)
                response_file.unlink()  # Удаляем файл ответа
                return response
            time.sleep(0.1)
        
        # Таймаут
        return {
            "success": False,
            "error": "Timeout waiting for daemon response"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"IPC error: {str(e)}"
        }

def main():
    parser = argparse.ArgumentParser(description='Hotkey Service - управление глобальными хоткеями')
    
    subparsers = parser.add_subparsers(dest='mode', help='Режим работы')
    
    # Режим daemon
    daemon_parser = subparsers.add_parser('daemon', help='Запуск в фоновом режиме')
    
    # Интерактивный режим
    interactive_parser = subparsers.add_parser('interactive', help='Запуск в интерактивном режиме')
    
    # Остановка сервиса
    stop_parser = subparsers.add_parser('stop', help='Остановить запущенный сервис')
    
    # Статус сервиса
    status_parser = subparsers.add_parser('status', help='Показать статус сервиса')
    
    # Команды для управления хоткеями
    register_parser = subparsers.add_parser('register', help='Зарегистрировать хоткей')
    register_parser.add_argument('hotkey', help='Hotkey combination (e.g., Ctrl+Shift+F5)')
    register_parser.add_argument('tool_name', help='MCP tool name to call')
    register_parser.add_argument('tool_json', help='JSON parameters for the tool')
    
    unregister_parser = subparsers.add_parser('unregister', help='Отменить регистрацию хоткея')
    unregister_parser.add_argument('hotkey', help='Hotkey combination to unregister')
    
    list_parser = subparsers.add_parser('list', help='Показать список активных хоткеев')
    
    unregister_all_parser = subparsers.add_parser('unregister_all', help='Отменить регистрацию всех хоткеев')
    
    args = parser.parse_args()
    
    # Если нет аргументов - запускаем интерактивный режим
    if not args.mode:
        args.mode = 'interactive'
    
    if args.mode == 'daemon':
        # Запуск в фоновом режиме
        service = HotkeyService()
        asyncio.run(service.run_daemon())
        
    elif args.mode == 'interactive':
        # Интерактивный режим
        service = HotkeyService()
        asyncio.run(service.run_interactive())
        
    elif args.mode == 'stop':
        # Остановка сервиса
        result = stop_service()
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
    elif args.mode == 'status':
        # Проверка статуса
        running, pid = is_service_running()
        if running:
            try:
                if STATUS_FILE.exists():
                    with open(STATUS_FILE, 'r', encoding='utf-8') as f:
                        status = json.load(f)
                    print(json.dumps({
                        "success": True,
                        "running": True,
                        "pid": pid,
                        "hotkeys_count": len(status.get("hotkeys", {})),
                        "hotkeys": status.get("hotkeys", {}),
                        "timestamp": status.get("timestamp")
                    }, indent=2, ensure_ascii=False))
                else:
                    print(json.dumps({
                        "success": True,
                        "running": True,
                        "pid": pid,
                        "status": "No status file found"
                    }, indent=2, ensure_ascii=False))
            except Exception as e:
                print(json.dumps({
                    "success": True,
                    "running": True,
                    "pid": pid,
                    "error": f"Error reading status: {e}"
                }, indent=2, ensure_ascii=False))
        else:
            print(json.dumps({
                "success": True,
                "running": False,
                "message": "Service is not running"
            }, indent=2, ensure_ascii=False))
            
    elif args.mode in ['register', 'unregister', 'list', 'unregister_all']:
        # Команды управления - проверяем, что сервис запущен
        running, pid = is_service_running()
        if not running:
            print(json.dumps({
                "success": False,
                "error": "Service is not running. Start it first with: python hotkey_service.py daemon"
            }, indent=2, ensure_ascii=False))
            sys.exit(1)
        
        # Подготавливаем аргументы для команды
        args_dict = {}
        if args.mode == 'register':
            args_dict = {
                'hotkey': args.hotkey,
                'tool_name': args.tool_name,
                'tool_json': json.loads(args.tool_json)
            }
        elif args.mode == 'unregister':
            args_dict = {
                'hotkey': args.hotkey
            }
        
        # Отправляем команду в daemon через IPC
        result = send_command_to_daemon(args.mode, args_dict)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
