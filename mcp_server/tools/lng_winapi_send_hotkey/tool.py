import mcp.types as types
import pywinauto
import json
import time
from pywinauto.keyboard import send_keys

async def tool_info() -> dict:
    return {
        "name": "lng_winapi_send_hotkey",
        "description": "Отправляет хоткей (комбинацию клавиш) или одиночную кнопку в главное окно процесса по PID.",
        "schema": {
            "type": "object",
            "properties": {
                "pid": {
                    "type": "integer",
                    "description": "PID процесса, которому отправить хоткей или кнопку."
                },
                "hotkey": {
                    "type": "string",
                    "description": "Хоткей, например '^n', '^+i', 'F5'."
                },
                "key": {
                    "type": "string",
                    "description": "Одиночная кнопка, например 'n', 'F5'. Если указано, отправляется только эта кнопка."
                }
            },
            "required": ["pid"]
        }
    }

async def run_tool(name: str, arguments: dict) -> list[types.Content]:    
    pid = arguments.get("pid")
    hotkey = arguments.get("hotkey")
    key = arguments.get("key")
    if pid is None:
        return [types.TextContent(type="text", text=json.dumps({"error": "pid required"}))]
    if not hotkey and not key:
        return [types.TextContent(type="text", text=json.dumps({"error": "hotkey or key required"}))]

    try:
        app = pywinauto.Application(backend="uia").connect(process=pid)
        main_window = None
        for w in app.windows():
            title = w.window_text()
            class_name = w.element_info.class_name
            if title and (class_name.lower().startswith("notepad++") or class_name.lower().startswith("chrome") or class_name.lower() == "notepad" or class_name.lower() == "scintilla"):
                main_window = w
                break
        if not main_window:
            main_window = app.top_window()
        main_window.set_focus()
        time.sleep(0.1)
        # Исправлено: экранируем пробелы для send_keys
        def escape_for_send_keys(s):
            # двойное экранирование скобок для печати как символов
            return s.replace(' ', '{SPACE}').replace('(', '{{(}}').replace(')', '{{)}}')
        if key:
            send_keys(escape_for_send_keys(key))
            result = {"success": True, "pid": pid, "key": key, "window_title": main_window.window_text(), "window_class": main_window.element_info.class_name}
        else:
            send_keys(hotkey)
            result = {"success": True, "pid": pid, "hotkey": hotkey, "window_title": main_window.window_text(), "window_class": main_window.element_info.class_name}
        return [types.TextContent(type="text", text=json.dumps(result))]
    except Exception as e:
        return [types.TextContent(type="text", text=json.dumps({"error": str(e)}))]
