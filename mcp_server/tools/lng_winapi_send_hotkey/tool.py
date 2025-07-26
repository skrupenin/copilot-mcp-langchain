import mcp.types as types
import pywinauto
import json
import time
from pywinauto.keyboard import send_keys

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
  
DELAY SUPPORT:
• delay: Pause between actions in milliseconds (default: 100ms)
• Per-action delay: {"type": "delay", "value": 500}

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
                                "enum": ["hotkey", "key", "text", "delay"],
                                "description": "Type of action: hotkey, key, text, or delay"
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
            if action_type == "hotkey":
                send_keys(str(value))
                return {"type": "hotkey", "value": value}
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
