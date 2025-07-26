import mcp.types as types
import pywinauto
import json
import time
from pywinauto.keyboard import send_keys
import win32gui
import win32con
import win32api

async def tool_info() -> dict:
    return {
        "name": "lng_winapi_send_hotkey",
        "description": """Sends hotkeys, system keys, or text to the main window of a process by PID. Supports single actions and complex sequences.

SINGLE ACTION MODES:
• hotkey: Key combinations - '^t' (Ctrl+T), '^+i' (Ctrl+Shift+I), '%{F4}' (Alt+F4)
• key: System keys - 'F12', 'ESC', 'ENTER', 'TAB', 'HOME', 'END'
• text: Plain text - 'Hello World', 'test@example.com'
• auto: Auto-detection (default for single actions)

SEQUENCE MODE:
• sequence: Array of actions executed in order
  Format: [{"type": "hotkey", "value": "^+p"}, {"type": "text", "value": "console"}, {"type": "key", "value": "ENTER"}]
  
DELAY & FOCUS SUPPORT:
• delay: Pause between actions in milliseconds (default: 100ms)
• Per-action delay: {"type": "delay", "value": 500}
• Window refocus: {"type": "focus", "value": "any"} - forces window focus

MODIFIERS: ^ = Ctrl, + = Shift, % = Alt, ~ = Win

EXAMPLES:
Single: hotkey='^t' or key='F12' or text='Hello'
Sequence: sequence=[{"type":"hotkey","value":"^+p"},{"type":"text","value":"console"},{"type":"key","value":"ENTER"}]
With delays: sequence=[{"type":"hotkey","value":"^+i"},{"type":"delay","value":500},{"type":"key","value":"F12"}]""",
        "schema": {
            "type": "object",
            "properties": {
                "pid": {
                    "type": "integer",
                    "description": "PID of the process to send input to."
                },
                "hotkey": {
                    "type": "string",
                    "description": "Single hotkey (key combination), e.g. '^t' (Ctrl+T), '^+i' (Ctrl+Shift+I)."
                },
                "key": {
                    "type": "string",
                    "description": "Single system key, e.g. 'F5', 'F12', 'ENTER', 'ESC', 'TAB'."
                },
                "text": {
                    "type": "string",
                    "description": "Single plain text input."
                },
                "sequence": {
                    "type": "array",
                    "description": "Array of actions to execute in order. Each action has 'type' and 'value' fields.",
                    "items": {
                        "type": "object",
                        "properties": {
                            "type": {
                                "type": "string",
                                "enum": ["hotkey", "key", "text", "delay", "focus"],
                                "description": "Type of action: hotkey, key, text, delay, or focus"
                            },
                            "value": {
                                "description": "Value for the action: key combination, system key, text, or delay in ms"
                            }
                        },
                        "required": ["type", "value"]
                    }
                },
                "delay": {
                    "type": "integer",
                    "description": "Default delay between sequence actions in milliseconds (default: 100)."
                },
                "input_type": {
                    "type": "string",
                    "enum": ["auto", "hotkey", "key", "text"],
                    "description": "Input type for single actions: 'auto' - auto-detection, others for explicit type."
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
    sequence = arguments.get("sequence")
    delay = arguments.get("delay", 100)  # Default 100ms delay
    input_type = arguments.get("input_type", "auto")
    
    if pid is None:
        return [types.TextContent(type="text", text=json.dumps({"error": "pid required"}))]
    
    # Check that at least one input parameter is provided
    if not any([hotkey, key, text, sequence]):
        return [types.TextContent(type="text", text=json.dumps({"error": "hotkey, key, text, or sequence required"}))]

    try:
        from pywinauto.keyboard import CODES, MODIFIERS
        
        # Connect to application and get main window
        app = pywinauto.Application(backend="uia").connect(process=pid)
        main_window = None
        
        # Try to find the best window for interaction
        for w in app.windows():
            title = w.window_text()
            class_name = w.element_info.class_name
            
            # Prioritize main Chrome window
            if title and (class_name.lower().startswith("chrome_widgetwin_1") or 
                         class_name.lower().startswith("chrome") and "1" in class_name):
                main_window = w
                break
                
        # Fallback to other Chrome windows
        if not main_window:
            for w in app.windows():
                title = w.window_text()
                class_name = w.element_info.class_name
                if (class_name.lower().startswith("notepad++") or 
                    class_name.lower().startswith("chrome") or 
                    class_name.lower() == "notepad" or 
                    class_name.lower() == "scintilla"):
                    main_window = w
                    break
                    
        if not main_window:
            main_window = app.top_window()
        
        # Enhanced focus management
        try:
            main_window.set_focus()
            time.sleep(0.2)  # Increased delay for focus
            
            # Try to bring window to front
            main_window.restore()
            main_window.set_focus()
            time.sleep(0.1)
        except:
            # If focus fails, continue anyway
            pass
        
        # Universal virtual key code mapping for all letters and common keys
        VK_MAP = {
            'a': 0x41, 'b': 0x42, 'c': 0x43, 'd': 0x44, 'e': 0x45, 'f': 0x46, 'g': 0x47, 'h': 0x48,
            'i': 0x49, 'j': 0x4A, 'k': 0x4B, 'l': 0x4C, 'm': 0x4D, 'n': 0x4E, 'o': 0x4F, 'p': 0x50,
            'q': 0x51, 'r': 0x52, 's': 0x53, 't': 0x54, 'u': 0x55, 'v': 0x56, 'w': 0x57, 'x': 0x58,
            'y': 0x59, 'z': 0x5A,
            '0': 0x30, '1': 0x31, '2': 0x32, '3': 0x33, '4': 0x34, '5': 0x35, '6': 0x36, '7': 0x37,
            '8': 0x38, '9': 0x39,
            'f1': 0x70, 'f2': 0x71, 'f3': 0x72, 'f4': 0x73, 'f5': 0x74, 'f6': 0x75, 'f7': 0x76,
            'f8': 0x77, 'f9': 0x78, 'f10': 0x79, 'f11': 0x7A, 'f12': 0x7B,
            'space': 0x20, 'enter': 0x0D, 'tab': 0x09, 'esc': 0x1B, 'escape': 0x1B,
            'backspace': 0x08, 'delete': 0x2E, 'insert': 0x2D, 'home': 0x24, 'end': 0x23,
            'pageup': 0x21, 'pagedown': 0x22, 'up': 0x26, 'down': 0x28, 'left': 0x25, 'right': 0x27
        }
        
        # Helper function to parse hotkey string into components
        def parse_hotkey(hotkey_str):
            """Parse hotkey string like '^+t' into modifiers and key"""
            hotkey_str = hotkey_str.lower()
            
            ctrl = '^' in hotkey_str
            shift = '+' in hotkey_str and not hotkey_str.startswith('+')  # Handle cases like '+a' vs '^+a'
            alt = '%' in hotkey_str
            win = '~' in hotkey_str
            
            # Extract the main key by removing all modifiers
            key_part = hotkey_str.replace('^', '').replace('%', '').replace('~', '')
            # Handle shift modifier carefully - it can be both modifier and part of key
            if ctrl or alt or win:
                key_part = key_part.replace('+', '')
            elif hotkey_str.startswith('+') and len(hotkey_str) > 1:
                # This is shift+key combination
                shift = True
                key_part = hotkey_str[1:]
            
            # Handle special key formats like {F4}
            if key_part.startswith('{') and key_part.endswith('}'):
                key_part = key_part[1:-1].lower()
            
            return {
                'ctrl': ctrl,
                'shift': shift, 
                'alt': alt,
                'win': win,
                'key': key_part
            }
        
        # Helper function to send hotkey via SendInput (global) - Universal version
        def send_hotkey_sendinput(hotkey_str):
            """Universal global hotkey method using SendInput"""
            try:
                parsed = parse_hotkey(hotkey_str)
                key_name = parsed['key']
                
                if key_name not in VK_MAP:
                    return False
                    
                vk_code = VK_MAP[key_name]
                
                # Use win32api for SendInput-like behavior
                if parsed['ctrl']:
                    win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
                if parsed['shift']:
                    win32api.keybd_event(win32con.VK_SHIFT, 0, 0, 0)
                if parsed['alt']:
                    win32api.keybd_event(win32con.VK_MENU, 0, 0, 0)
                
                # Main key
                win32api.keybd_event(vk_code, 0, 0, 0)
                time.sleep(0.01)
                win32api.keybd_event(vk_code, 0, win32con.KEYEVENTF_KEYUP, 0)
                
                # Release modifiers in reverse order
                if parsed['alt']:
                    win32api.keybd_event(win32con.VK_MENU, 0, win32con.KEYEVENTF_KEYUP, 0)
                if parsed['shift']:
                    win32api.keybd_event(win32con.VK_SHIFT, 0, win32con.KEYEVENTF_KEYUP, 0)
                if parsed['ctrl']:
                    win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
                
                return True
            except Exception as e:
                return False
        
        # Helper function to send hotkey via Windows API - Universal version
            except:
                return False
        
        # Helper function to send hotkey via Windows API - Universal version
        def send_hotkey_winapi(hwnd, hotkey_str):
            """Universal method using Windows API messages"""
            try:
                parsed = parse_hotkey(hotkey_str)
                key_name = parsed['key']
                
                if key_name not in VK_MAP:
                    return False
                    
                vk_code = VK_MAP[key_name]
                
                # Try multiple approaches
                success = False
                
                # Method 1: Direct WM_KEYDOWN/WM_KEYUP messages
                try:
                    # Send key down events for modifiers
                    if parsed['ctrl']:
                        win32gui.PostMessage(hwnd, win32con.WM_KEYDOWN, win32con.VK_CONTROL, 0)
                    if parsed['shift']:
                        win32gui.PostMessage(hwnd, win32con.WM_KEYDOWN, win32con.VK_SHIFT, 0)
                    if parsed['alt']:
                        win32gui.PostMessage(hwnd, win32con.WM_KEYDOWN, win32con.VK_MENU, 0)
                    
                    # Send main key
                    win32gui.PostMessage(hwnd, win32con.WM_KEYDOWN, vk_code, 0)
                    time.sleep(0.01)
                    win32gui.PostMessage(hwnd, win32con.WM_KEYUP, vk_code, 0)
                    
                    # Send key up events for modifiers (reverse order)
                    if parsed['alt']:
                        win32gui.PostMessage(hwnd, win32con.WM_KEYUP, win32con.VK_MENU, 0)
                    if parsed['shift']:
                        win32gui.PostMessage(hwnd, win32con.WM_KEYUP, win32con.VK_SHIFT, 0)
                    if parsed['ctrl']:
                        win32gui.PostMessage(hwnd, win32con.WM_KEYUP, win32con.VK_CONTROL, 0)
                    
                    success = True
                except:
                    pass
                
                return success
            except Exception as e:
                return False
        
        # Helper function to escape text for send_keys
        def escape_for_send_keys(s):
            s = s.replace('{', '{{')
            s = s.replace('}', '}}')
            s = s.replace('+', '{+}')
            s = s.replace('^', '{^}')
            s = s.replace('%', '{%}')
            s = s.replace('~', '{~}')
            s = s.replace('(', '{(}')
            s = s.replace(')', '{)}')
            s = s.replace('[', '{[}')
            s = s.replace(']', '{]}')
            s = s.replace(' ', '{SPACE}')
            return s
        
        # Helper function to execute a single action
        def execute_action(action_type, value):
            # Ensure window focus before each important action
            if action_type in ["hotkey", "key"]:
                try:
                    main_window.set_focus()
                    time.sleep(0.05)
                except:
                    pass
            
            if action_type == "hotkey":
                hotkey_str = str(value)
                
                # Helper function to check if hotkey can be handled by our enhanced methods
                def can_handle_hotkey(hotkey_str):
                    try:
                        parsed = parse_hotkey(hotkey_str)
                        return parsed['key'] in VK_MAP
                    except:
                        return False
                
                # Try SendInput method first if we can parse the hotkey
                if can_handle_hotkey(hotkey_str):
                    if send_hotkey_sendinput(hotkey_str):
                        return {"type": "hotkey", "value": value, "method": "sendinput"}
                
                # Try WinAPI method second if we can parse the hotkey
                if can_handle_hotkey(hotkey_str):
                    hwnd = main_window.handle
                    if send_hotkey_winapi(hwnd, hotkey_str):
                        return {"type": "hotkey", "value": value, "method": "winapi"}
                
                # Fallback to send_keys
                send_keys(hotkey_str)
                return {"type": "hotkey", "value": value, "method": "send_keys"}
                
            elif action_type == "key":
                key_to_send = str(value)
                if key_to_send.upper() in CODES:
                    key_to_send = f"{{{key_to_send.upper()}}}"
                elif not (key_to_send.startswith('{') and key_to_send.endswith('}')):
                    if key_to_send.upper() in CODES:
                        key_to_send = f"{{{key_to_send.upper()}}}"
                send_keys(key_to_send)
                return {"type": "key", "value": key_to_send}
            elif action_type == "text":
                escaped_text = escape_for_send_keys(str(value))
                send_keys(escaped_text)
                return {"type": "text", "value": value}
            elif action_type == "delay":
                delay_ms = int(value)
                time.sleep(delay_ms / 1000)
                return {"type": "delay", "value": delay_ms}
            elif action_type == "focus":
                # Special action to refocus window
                try:
                    main_window.set_focus()
                    main_window.restore()
                    time.sleep(0.1)
                    return {"type": "focus", "value": "window_focused"}
                except Exception as e:
                    return {"type": "focus", "value": f"focus_failed: {str(e)}"}
            else:
                raise ValueError(f"Unknown action type: {action_type}")
        
        result = {
            "success": True, 
            "pid": pid, 
            "window_title": main_window.window_text(),
            "window_class": main_window.element_info.class_name
        }
        
        # Execute sequence or single action
        if sequence:
            # Execute sequence of actions
            executed_actions = []
            for i, action in enumerate(sequence):
                action_type = action.get("type")
                value = action.get("value")
                
                if not action_type or value is None:
                    return [types.TextContent(type="text", text=json.dumps({
                        "error": f"Invalid action at index {i}: missing 'type' or 'value'"
                    }))]
                
                try:
                    executed_action = execute_action(action_type, value)
                    executed_actions.append(executed_action)
                    
                    # Add delay between actions (except after delay actions and last action)
                    if action_type != "delay" and i < len(sequence) - 1:
                        time.sleep(delay / 1000)
                        
                except Exception as e:
                    return [types.TextContent(type="text", text=json.dumps({
                        "error": f"Error executing action {i} ({action_type}: {value}): {str(e)}"
                    }))]
            
            result.update({
                "mode": "sequence",
                "actions_executed": executed_actions,
                "total_actions": len(executed_actions),
                "default_delay_ms": delay
            })
        else:
            # Execute single action
            # Auto-detect input type if not specified
            if input_type == "auto":
                if hotkey:
                    input_type = "hotkey"
                elif key:
                    if key.upper() in CODES or key.startswith('VK_') or key.startswith('{'):
                        input_type = "key"
                    else:
                        input_type = "text"
                elif text:
                    input_type = "text"
            
            value_to_use = hotkey or key or text
            executed_action = execute_action(input_type, value_to_use)
            
            result.update({
                "mode": "single",
                "action_executed": executed_action,
                "input_type": input_type
            })
        
        return [types.TextContent(type="text", text=json.dumps(result))]
    except Exception as e:
        return [types.TextContent(type="text", text=json.dumps({"error": str(e)}))]
