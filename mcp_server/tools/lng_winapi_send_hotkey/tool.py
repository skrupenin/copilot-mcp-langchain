import mcp.types as types
import pywinauto
import json
import time
from pywinauto.keyboard import send_keys

async def tool_info() -> dict:
    return {
        "name": "lng_winapi_send_hotkey",
        "description": """Sends hotkeys (key combinations), system keys, or text to the main window of a process by PID.

INPUT TYPES:
• hotkey: Key combinations - '^t' (Ctrl+T), '^+i' (Ctrl+Shift+I), '%{F4}' (Alt+F4)
• key: System keys - 'F12', 'ESC', 'ENTER', 'TAB', 'HOME', 'END'
• text: Plain text - 'Hello World', 'test@example.com'
• auto: Auto-detection (default)

MODIFIERS: ^ = Ctrl, + = Shift, % = Alt, ~ = Win

EXAMPLES:
- Inspector: key='F12' or hotkey='^+i'
- New tab: hotkey='^t'
- Text input: text='Hello World'""",
        "schema": {
            "type": "object",
            "properties": {
                "pid": {
                    "type": "integer",
                    "description": "PID of the process to send hotkey, key, or text to."
                },
                "hotkey": {
                    "type": "string",
                    "description": "Hotkey (key combination), e.g. '^t' (Ctrl+T), '^+i' (Ctrl+Shift+I), '%{F4}' (Alt+F4)."
                },
                "key": {
                    "type": "string",
                    "description": "Single system key, e.g. 'F5', 'F12', 'ENTER', 'ESC', 'TAB'."
                },
                "text": {
                    "type": "string",
                    "description": "Plain text to input as is."
                },
                "input_type": {
                    "type": "string",
                    "enum": ["auto", "hotkey", "key", "text"],
                    "description": "Input type: 'auto' - auto-detection, 'hotkey' - key combination, 'key' - system key, 'text' - plain text."
                }
            },
            "required": ["pid"]
        }
    }

async def run_tool(name: str, arguments: dict) -> list[types.Content]:    
    pid = arguments.get("pid")
    hotkey = arguments.get("hotkey")
    key = arguments.get("key")
    text = arguments.get("text")
    input_type = arguments.get("input_type", "auto")
    
    if pid is None:
        return [types.TextContent(type="text", text=json.dumps({"error": "pid required"}))]
    
    # Check that at least one input parameter is provided
    if not any([hotkey, key, text]):
        return [types.TextContent(type="text", text=json.dumps({"error": "hotkey, key, or text required"}))]

    try:
        from pywinauto.keyboard import CODES, MODIFIERS
        
        # Auto-detect input type if not specified
        if input_type == "auto":
            if hotkey:
                input_type = "hotkey"
            elif key:
                # Check if key is a system key
                if key.upper() in CODES or key.startswith('VK_') or key.startswith('{'):
                    input_type = "key"
                else:
                    input_type = "text"
            elif text:
                input_type = "text"
        
        app = pywinauto.Application(backend="uia").connect(process=pid)
        main_window = None
        for w in app.windows():
            title = w.window_text()
            class_name = w.element_info.class_name
            if title and (class_name.lower().startswith("notepad++") or 
                         class_name.lower().startswith("chrome") or 
                         class_name.lower() == "notepad" or 
                         class_name.lower() == "scintilla"):
                main_window = w
                break
        if not main_window:
            main_window = app.top_window()
        
        main_window.set_focus()
        time.sleep(0.1)
        
        # Execute input based on type
        if input_type == "hotkey":
            # Send hotkey as is (key combination)
            send_keys(hotkey)
            result = {"success": True, "pid": pid, "hotkey": hotkey, "input_type": input_type}
        elif input_type == "key":
            # Send system key
            key_to_send = key or hotkey
            # If not in special format, wrap in curly braces
            if key_to_send.upper() in CODES:
                key_to_send = f"{{{key_to_send.upper()}}}"
            elif not (key_to_send.startswith('{') and key_to_send.endswith('}')):
                # If not F-key and not in special format, try to find in CODES
                if key_to_send.upper() in CODES:
                    key_to_send = f"{{{key_to_send.upper()}}}"
            send_keys(key_to_send)
            result = {"success": True, "pid": pid, "key": key_to_send, "input_type": input_type}
        elif input_type == "text":
            # Send plain text
            text_to_send = text or key or hotkey
            # Escape special characters for send_keys
            def escape_for_send_keys(s):
                # First escape curly braces, then other characters
                s = s.replace('{', '{{')
                s = s.replace('}', '}}')
                # Replace other special characters
                s = s.replace('+', '{+}')
                s = s.replace('^', '{^}')
                s = s.replace('%', '{%}')
                s = s.replace('~', '{~}')
                s = s.replace('(', '{(}')
                s = s.replace(')', '{)}')
                s = s.replace('[', '{[}')
                s = s.replace(']', '{]}')
                # Handle spaces properly
                s = s.replace(' ', '{SPACE}')
                return s
            
            escaped_text = escape_for_send_keys(text_to_send)
            send_keys(escaped_text)
            result = {"success": True, "pid": pid, "text": text_to_send, "input_type": input_type}
        
        # Add window information
        result.update({
            "window_title": main_window.window_text(),
            "window_class": main_window.element_info.class_name
        })
        
        return [types.TextContent(type="text", text=json.dumps(result))]
    except Exception as e:
        return [types.TextContent(type="text", text=json.dumps({"error": str(e)}))]
