import mcp.types as types
import pywinauto
import json
import time
import win32gui
import win32con
from pywinauto.controls.uiawrapper import UIAWrapper

async def tool_info() -> dict:
    return {
        "name": "lng_winapi_get_window_content",
        "description": """Deep analysis of Windows application content. Extracts comprehensive information from all UI elements including text, states, positions, and properties.

CAPABILITIES:
• Text extraction: Input fields, labels, buttons, menus, console output
• Element states: Enabled/disabled, visible/hidden, selected/unselected
• Positions & sizes: Exact coordinates and dimensions of elements
• Properties: Class names, automation IDs, control types
• Hierarchical structure: Parent-child relationships with full nesting
• Interactive elements: Buttons, links, input fields, dropdowns

EXTRACTION MODES:
• full: Complete deep scan of all elements (default)
• text_only: Focus on text content extraction
• interactive: Only interactive elements (buttons, inputs)
• structure: UI hierarchy without detailed properties

FILTERING:
• element_types: Filter by control types (Button, Edit, Text, etc.)
• max_depth: Limit traversal depth (default: unlimited)
• include_invisible: Include hidden elements (default: false)

OUTPUT FORMAT:
• Hierarchical JSON with full element details
• Text content with context and positioning
• Interactive elements with their capabilities
• Element relationships and nesting structure""",
        "schema": {
            "type": "object",
            "properties": {
                "pid": {
                    "type": "integer",
                    "description": "PID of the process to analyze."
                },
                "mode": {
                    "type": "string",
                    "enum": ["full", "text_only", "interactive", "structure"],
                    "description": "Analysis mode: full, text_only, interactive, or structure."
                },
                "element_types": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Filter by element types: Button, Edit, Text, List, Tree, etc."
                },
                "max_depth": {
                    "type": "integer",
                    "description": "Maximum traversal depth (default: unlimited)."
                },
                "include_invisible": {
                    "type": "boolean",
                    "description": "Include hidden/invisible elements (default: false)."
                },
                "target_window": {
                    "type": "string",
                    "description": "Target specific window by title pattern (optional)."
                }
            },
            "required": ["pid"]
        }
    }

async def run_tool(name: str, arguments: dict) -> list[types.Content]:    
    pid = arguments.get("pid")
    mode = arguments.get("mode", "full")
    element_types = arguments.get("element_types", [])
    max_depth = arguments.get("max_depth", None)
    include_invisible = arguments.get("include_invisible", False)
    target_window = arguments.get("target_window", None)
    
    if pid is None:
        return [types.TextContent(type="text", text=json.dumps({"error": "pid required"}))]

    try:
        # Connect to application
        app = pywinauto.Application(backend="uia").connect(process=pid)
        
        # Find target window
        windows = app.windows()
        target_windows = []
        
        if target_window:
            # Filter by title pattern
            for w in windows:
                if target_window.lower() in w.window_text().lower():
                    target_windows.append(w)
        else:
            target_windows = windows
        
        if not target_windows:
            return [types.TextContent(type="text", text=json.dumps({
                "error": "No matching windows found"
            }))]
        
        # Deep content extraction function
        def extract_element_content(element, depth=0, max_depth=None):
            """Recursively extract comprehensive element information"""
            if max_depth is not None and depth > max_depth:
                return None
                
            try:
                # Basic element information
                element_info = {
                    "depth": depth,
                    "control_type": "unknown",
                    "class_name": "",
                    "automation_id": "",
                    "name": "",
                    "text": "",
                    "value": "",
                    "is_visible": True,
                    "is_enabled": True,
                    "is_selected": False,
                    "position": {"x": 0, "y": 0, "width": 0, "height": 0},
                    "properties": {},
                    "children": []
                }
                
                # Extract basic properties
                try:
                    element_info["control_type"] = element.element_info.control_type
                    element_info["class_name"] = element.element_info.class_name
                    element_info["automation_id"] = getattr(element.element_info, 'automation_id', '')
                    element_info["name"] = element.window_text()
                except:
                    pass
                
                # Extract text content
                try:
                    # Try different methods to get text
                    text_methods = [
                        lambda: element.window_text(),
                        lambda: getattr(element, 'texts', lambda: [''])()[0] if hasattr(element, 'texts') else '',
                        lambda: getattr(element.element_info, 'name', ''),
                        lambda: str(getattr(element.element_info, 'value', ''))
                    ]
                    
                    for method in text_methods:
                        try:
                            text = method()
                            if text and text.strip():
                                element_info["text"] = text.strip()
                                break
                        except:
                            continue
                            
                    # For edit controls, try to get current value
                    if "edit" in element_info["control_type"].lower():
                        try:
                            element_info["value"] = element.get_value()
                        except:
                            pass
                            
                except:
                    pass
                
                # Extract state information
                try:
                    element_info["is_visible"] = element.is_visible()
                    element_info["is_enabled"] = element.is_enabled()
                    
                    # Check if element is selected (for lists, trees, etc.)
                    try:
                        element_info["is_selected"] = element.is_selected()
                    except:
                        pass
                        
                except:
                    pass
                
                # Extract position and size
                try:
                    rect = element.rectangle()
                    element_info["position"] = {
                        "x": rect.left,
                        "y": rect.top, 
                        "width": rect.right - rect.left,
                        "height": rect.bottom - rect.top
                    }
                except:
                    pass
                
                # Extract additional properties based on control type
                try:
                    control_type = element_info["control_type"].lower()
                    
                    if "button" in control_type:
                        element_info["properties"]["clickable"] = True
                        try:
                            element_info["properties"]["is_default"] = getattr(element.element_info, 'is_default', False)
                        except:
                            pass
                            
                    elif "edit" in control_type:
                        element_info["properties"]["editable"] = True
                        try:
                            element_info["properties"]["is_password"] = getattr(element.element_info, 'is_password', False)
                            element_info["properties"]["is_readonly"] = getattr(element.element_info, 'is_readonly', False)
                        except:
                            pass
                            
                    elif "list" in control_type:
                        try:
                            element_info["properties"]["item_count"] = element.item_count()
                            element_info["properties"]["selected_items"] = [item.window_text() for item in element.selected_items()]
                        except:
                            pass
                            
                    elif "tree" in control_type:
                        try:
                            element_info["properties"]["item_count"] = element.item_count()
                        except:
                            pass
                            
                except:
                    pass
                
                # Filter by element types if specified
                if element_types and not any(et.lower() in element_info["control_type"].lower() for et in element_types):
                    return None
                
                # Filter invisible elements if not requested
                if not include_invisible and not element_info["is_visible"]:
                    return None
                
                # Process children recursively
                try:
                    children = element.children()
                    for child in children:
                        child_info = extract_element_content(child, depth + 1, max_depth)
                        if child_info:
                            element_info["children"].append(child_info)
                except:
                    pass
                
                # Apply mode filtering
                if mode == "text_only" and not element_info["text"] and not element_info["value"]:
                    # Only return if has text content or has children with text
                    if not any(child.get("text") or child.get("value") for child in element_info["children"]):
                        return None
                        
                elif mode == "interactive" and not element_info["properties"].get("clickable") and not element_info["properties"].get("editable"):
                    # Only return interactive elements or containers of interactive elements
                    if not any(child.get("properties", {}).get("clickable") or child.get("properties", {}).get("editable") 
                              for child in element_info["children"]):
                        return None
                
                elif mode == "structure":
                    # Remove detailed content, keep only structure
                    element_info = {
                        "depth": element_info["depth"],
                        "control_type": element_info["control_type"],
                        "class_name": element_info["class_name"],
                        "name": element_info["name"][:50] + "..." if len(element_info["name"]) > 50 else element_info["name"],
                        "is_visible": element_info["is_visible"],
                        "children": element_info["children"]
                    }
                
                return element_info
                
            except Exception as e:
                return {
                    "depth": depth,
                    "error": f"Failed to extract element: {str(e)}",
                    "children": []
                }
        
        # Extract content from all target windows
        results = []
        for window in target_windows:
            try:
                # Check if window is active by comparing with foreground window
                is_active = False
                try:
                    import win32gui
                    foreground_hwnd = win32gui.GetForegroundWindow()
                    is_active = (window.handle == foreground_hwnd)
                except:
                    is_active = False
                
                window_info = {
                    "window_title": window.window_text(),
                    "window_class": window.element_info.class_name,
                    "window_handle": window.handle,
                    "is_active": is_active,
                    "content": extract_element_content(window, 0, max_depth)
                }
                results.append(window_info)
            except Exception as e:
                results.append({
                    "window_title": "Unknown",
                    "error": str(e)
                })
        
        # Compile final result
        result = {
            "success": True,
            "pid": pid,
            "mode": mode,
            "analysis_time": time.time(),
            "windows_analyzed": len(results),
            "filters": {
                "element_types": element_types,
                "max_depth": max_depth,
                "include_invisible": include_invisible,
                "target_window": target_window
            },
            "windows": results
        }
        
        return [types.TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]
        
    except Exception as e:
        return [types.TextContent(type="text", text=json.dumps({
            "error": f"Failed to analyze window content: {str(e)}"
        }))]
