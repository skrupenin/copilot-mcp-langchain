import mcp.types as types
import ctypes
import ctypes.wintypes
import json

async def tool_info() -> dict:
    return {
        "description": "Показывает дерево окон и контролов для указанного процесса (по pid) через WinAPI.",
        "schema": {
            "type": "object",
            "properties": {
                "pid": {
                    "type": "integer",
                    "description": "PID процесса, для которого нужно построить дерево окон."
                }
            },
            "required": ["pid"]
        }
    }

async def run_tool(name: str, arguments: dict) -> list[types.Content]:    
    user32 = ctypes.windll.user32
    pid = arguments.get("pid")
    if pid is None:
        return [types.TextContent(type="text", text=json.dumps({"error": "pid is required"}))]

    def get_window_text(hwnd):
        length = user32.GetWindowTextLengthW(hwnd)
        buffer = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(hwnd, buffer, length + 1)
        return buffer.value

    def get_class_name(hwnd):
        buffer = ctypes.create_unicode_buffer(256)
        user32.GetClassNameW(hwnd, buffer, 256)
        return buffer.value

    def enum_child_windows(hwnd):
        children = []
        def callback(child_hwnd, lparam):
            children.append(child_hwnd)
            return True
        CMPFUNC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.wintypes.HWND, ctypes.wintypes.LPARAM)
        user32.EnumChildWindows(hwnd, CMPFUNC(callback), 0)
        return children

    def build_tree(hwnd):
        node = {
            "hwnd": hwnd,
            "title": get_window_text(hwnd),
            "class": get_class_name(hwnd),
            "children": []
        }
        for child in enum_child_windows(hwnd):
            node["children"].append(build_tree(child))
        return node

    def enum_windows_for_pid(pid):
        result = []
        def callback(hwnd, lparam):
            lpdwProcessId = ctypes.wintypes.DWORD()
            user32.GetWindowThreadProcessId(hwnd, ctypes.byref(lpdwProcessId))
            if lpdwProcessId.value == pid:
                result.append(hwnd)
            return True
        CMPFUNC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.wintypes.HWND, ctypes.wintypes.LPARAM)
        user32.EnumWindows(CMPFUNC(callback), 0)
        return result

    tree = []
    for hwnd in enum_windows_for_pid(pid):
        tree.append(build_tree(hwnd))

    return [types.TextContent(type="text", text=json.dumps(tree, ensure_ascii=False, indent=2))]
