import mcp.types as types
import psutil
import json
import ctypes
import ctypes.wintypes

async def tool_info() -> dict:
    return {
        "name": "lng_winapi_list_processes",
        "description": "Возвращает список процессов, соответствующих фильтру: pid, имя, путь. Можно отфильтровать только процессы с окнами.",
        "schema": {
            "type": "object",
            "properties": {
                "filter": {
                    "type": "string",
                    "description": "Фильтр для поиска по имени или пути процесса (регистронезависимо)."
                },
                "only_with_windows": {
                    "type": "boolean",
                    "description": "Показывать только процессы, у которых есть хотя бы одно окно, которое можно развернуть на весь экран (основное окно)."
                }
            },
            "required": []
        }
    }

async def run_tool(name: str, arguments: dict) -> list[types.Content]:    
    filter_str = arguments.get("filter", "").lower()
    only_with_windows = arguments.get("only_with_windows", False)
    user32 = ctypes.windll.user32

    def has_main_window(pid):
        found = False
        def callback(hwnd, lparam):
            lpdwProcessId = ctypes.wintypes.DWORD()
            user32.GetWindowThreadProcessId(hwnd, ctypes.byref(lpdwProcessId))
            if lpdwProcessId.value == pid:
                # Проверяем, что это главное окно (видимое, не дочернее, можно развернуть)
                if user32.IsWindowVisible(hwnd) and user32.GetParent(hwnd) == 0:
                    # Проверяем, что окно не имеет стиля WS_DISABLED
                    style = user32.GetWindowLongW(hwnd, -16)  # GWL_STYLE
                    WS_DISABLED = 0x08000000
                    if not (style & WS_DISABLED):
                        nonlocal found
                        found = True
                        return False  # Прерываем перебор
            return True
        CMPFUNC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.wintypes.HWND, ctypes.wintypes.LPARAM)
        user32.EnumWindows(CMPFUNC(callback), 0)
        return found

    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'exe']):
        try:
            info = proc.info
            name = info.get("name", "") or ""
            exe = info.get("exe", "") or ""
            if not filter_str or (filter_str in name.lower() or filter_str in exe.lower()):
                if only_with_windows:
                    if has_main_window(info.get("pid")):
                        processes.append({
                            "pid": info.get("pid"),
                            "name": name,
                            "exe": exe
                        })
                else:
                    processes.append({
                        "pid": info.get("pid"),
                        "name": name,
                        "exe": exe
                    })
        except Exception:
            continue
    return [types.TextContent(type="text", text=json.dumps(processes, ensure_ascii=False, indent=2))]
