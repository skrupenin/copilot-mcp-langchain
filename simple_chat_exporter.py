#!/usr/bin/env python3
"""
Simple GitHub Copilot Chat Exporter with Attachments Support
Creates clean VSCode-like chat interface with attachment display
"""

import json
import os
from pathlib import Path
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleChatExporter:
    def __init__(self, vscode_path: str, output_dir: str = "simple_chat_export"):
        self.vscode_path = Path(vscode_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def find_workspaces(self):
        workspace_storage = self.vscode_path / "User" / "workspaceStorage"
        workspaces = []
        
        for workspace_dir in workspace_storage.iterdir():
            if workspace_dir.is_dir() and (workspace_dir / "chatSessions").exists():
                workspaces.append(workspace_dir)
        
        logger.info(f"Found {len(workspaces)} workspaces")
        return workspaces
    
    def read_session(self, workspace_path: Path):
        chat_dir = workspace_path / "chatSessions"
        for session_file in chat_dir.glob("*.json"):
            try:
                with open(session_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    data['_file'] = session_file.name
                    return data
            except Exception as e:
                logger.warning(f"Failed to read {session_file}: {e}")
        return None
    
    def escape_html(self, text):
        if not text:
            return ""
        return (text.replace('&', '&amp;')
                   .replace('<', '&lt;')
                   .replace('>', '&gt;')
                   .replace('"', '&quot;'))
    
    def format_attachment(self, variable):
        """Format attachment/variable for display"""
        kind = variable.get('kind', 'unknown')
        name = variable.get('name', 'Unknown')
        model_desc = variable.get('modelDescription', '')
        
        # Get icon based on type
        if kind == 'file':
            icon = "📄"
            # Extract file info
            if 'value' in variable and 'uri' in variable['value']:
                uri = variable['value']['uri']
                file_path = uri.get('path', uri.get('fsPath', ''))
                if 'range' in variable['value']:
                    range_info = variable['value']['range']
                    line = range_info.get('startLineNumber', '')
                    if line:
                        name += f":{line}"
        elif kind == 'promptFile':
            icon = "📋"
        else:
            icon = "🔗"
        
        return {
            'icon': icon,
            'name': name,
            'description': model_desc,
            'kind': kind,
            'raw_data': variable  # Добавляем сырые данные для детального просмотра
        }
    
    def read_file_content(self, file_path, range_info=None):
        """Read file content, optionally limited to a specific range"""
        try:
            # Convert path format if needed
            if file_path.startswith('/c:'):
                file_path = file_path.replace('/c:', 'C:').replace('/', '\\')
            
            file_path = Path(file_path)
            if not file_path.exists():
                return f"File not found: {file_path}"
            
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            if range_info:
                start_line = range_info.get('startLineNumber', 1) - 1  # Convert to 0-based
                end_line = range_info.get('endLineNumber', len(lines)) - 1
                start_col = range_info.get('startColumn', 1) - 1
                end_col = range_info.get('endColumn', len(lines[end_line]) if end_line < len(lines) else 0) - 1
                
                if start_line == end_line and start_line < len(lines):
                    # Single line selection - include context
                    context_start = max(0, start_line - 2)
                    context_end = min(len(lines), end_line + 3)
                    context_lines = []
                    
                    for i in range(context_start, context_end):
                        line_num = i + 1
                        line_content = lines[i].rstrip()
                        if i == start_line:
                            # Highlight the selected part with yellow background
                            before = self.escape_html(line_content[:start_col])
                            selected = self.escape_html(line_content[start_col:end_col])
                            after = self.escape_html(line_content[end_col:])
                            line_content = f"{before}<mark class='highlight' title='This text was selected in the original file'>{selected}</mark>{after}"
                        else:
                            # Escape HTML for context lines
                            line_content = self.escape_html(line_content)
                        context_lines.append(f"{line_num:4d}: {line_content}")
                    
                    return "<br>".join(context_lines)
                else:
                    # Multi-line selection
                    selected_lines = lines[start_line:end_line + 1]
                    result = []
                    for i, line in enumerate(selected_lines):
                        line_num = start_line + i + 1
                        result.append(f"{line_num:4d}: {self.escape_html(line.rstrip())}")
                    return "<br>".join(result)
            else:
                # Return first 20 lines for prompt files
                preview_lines = lines[:20]
                result = []
                for i, line in enumerate(preview_lines):
                    result.append(f"{i+1:4d}: {self.escape_html(line.rstrip())}")
                if len(lines) > 20:
                    result.append("... (truncated)")
                return "<br>".join(result)
                
        except Exception as e:
            return f"Error reading file: {e}"

    def process_response_with_tools(self, response_list):
        """Process response array integrating tool calls with text"""
        html_parts = []
        i = 0
        
        while i < len(response_list):
            item = response_list[i]
            
            if 'value' in item:
                # Regular text response
                html_parts.append(self.escape_html(str(item['value'])))
                i += 1
            elif item.get('kind') == 'prepareToolInvocation':
                # Find the corresponding toolInvocationSerialized
                prepare_item = item
                serialized_item = None
                
                # Look for the next toolInvocationSerialized with same toolName
                tool_name = prepare_item.get('toolName')
                j = i + 1
                while j < len(response_list) and serialized_item is None:
                    next_item = response_list[j]
                    if (next_item.get('kind') == 'toolInvocationSerialized' and 
                        next_item.get('toolId') == tool_name):
                        serialized_item = next_item
                        break
                    j += 1
                
                # Format combined tool call
                if serialized_item:
                    tool_html = self.format_tool_call_combined(prepare_item, serialized_item)
                    html_parts.append(tool_html)
                    i = j + 1  # Skip both prepare and serialized items
                else:
                    # If no serialized found, just show prepare
                    tool_html = self.format_tool_call(prepare_item)
                    html_parts.append(tool_html)
                    i += 1
                    
            elif item.get('kind') == 'toolInvocationSerialized':
                # Check if this wasn't already processed with a prepare item
                # (this handles orphaned toolInvocationSerialized)
                tool_html = self.format_tool_call(item)
                html_parts.append(tool_html)
                i += 1
            else:
                i += 1
        
        return ''.join(html_parts)
    
    def format_tool_name(self, tool_id):
        """Format tool name for display"""
        if tool_id.startswith('mcp_') and '-mcp_lng_' in tool_id:
            # Parse MCP tool name: mcp_langchain-mcp_lng_file_list -> [MCP] mcp_langchain: lng_file_list
            parts = tool_id.split('-mcp_lng_')
            if len(parts) == 2:
                server_name = parts[0]  # mcp_langchain
                tool_name = parts[1]    # file_list
                return f"[MCP] {server_name}: lng_{tool_name}"
        return tool_id
    
    def format_json_string_content(self, content):
        """Format JSON string content with proper line breaks"""
        if isinstance(content, str):
            # Handle different types of JSON string encoding
            
            # Case 1: String that contains literal newlines and is wrapped in quotes
            if content.startswith('"') and content.endswith('"'):
                try:
                    # Remove outer quotes first
                    inner_content = content[1:-1]
                    
                    # Try to parse it directly as JSON (it might already be valid)
                    try:
                        inner_json = json.loads(inner_content)
                        if isinstance(inner_json, (dict, list)):
                            formatted_json = json.dumps(inner_json, indent=2)
                            return self.escape_html(formatted_json).replace('\n', '<br>')
                    except json.JSONDecodeError:
                        # If direct parsing failed, try to fix literal newlines
                        fixed_content = inner_content.replace('\n', '\\n').replace('\t', '\\t').replace('\r', '\\r')
                        try:
                            inner_json = json.loads(fixed_content)
                            if isinstance(inner_json, (dict, list)):
                                formatted_json = json.dumps(inner_json, indent=2)
                                return self.escape_html(formatted_json).replace('\n', '<br>')
                        except json.JSONDecodeError:
                            pass
                
                except json.JSONDecodeError:
                    pass
                
                # If we can't parse it as JSON, just format it nicely
                inner_content = content[1:-1]
                # Unescape common JSON escapes
                inner_content = inner_content.replace('\\"', '"')
                inner_content = inner_content.replace('\\\\', '\\')
                inner_content = inner_content.replace('\\n', '\n')
                inner_content = inner_content.replace('\\t', '\t')
                return self.escape_html(inner_content).replace('\n', '<br>')
            
            # Case 2: Direct JSON string content (without outer quotes)
            try:
                inner_json = json.loads(content)
                if isinstance(inner_json, (dict, list)):
                    formatted_json = json.dumps(inner_json, indent=2)
                    return self.escape_html(formatted_json).replace('\n', '<br>')
            except json.JSONDecodeError:
                pass
            
            # Case 3: Regular string with \n sequences - convert them to actual line breaks
            if '\\n' in content:
                formatted = content.replace('\\n', '<br>')
                return self.escape_html(formatted)
        
        # For non-string content, format as JSON with proper indentation
        if content is not None:
            try:
                json_str = json.dumps(content, indent=2)
                return self.escape_html(json_str).replace('\n', '<br>')
            except:
                return self.escape_html(str(content))
        
        return "No data"
    
    def format_output_blocks(self, output_data):
        """Format output data as multiple blocks"""
        if not output_data:
            return "No output data"
        
        if isinstance(output_data, list):
            blocks = []
            for i, item in enumerate(output_data):
                if isinstance(item, dict):
                    item_type = item.get('type', 'unknown')
                    is_text = item.get('isText', False)
                    has_error = item.get('error', False)
                    value = item.get('value', '')
                    
                    # Format status icon
                    status_icon = "❌" if has_error else "✅"
                    
                    # Format value content
                    if is_text and isinstance(value, str):
                        formatted_value = self.format_json_string_content(value)
                    else:
                        formatted_value = self.format_json_string_content(value)
                    
                    blocks.append(f'''<div style="margin: 8px 0; padding: 8px; background: #161b22; border: 1px solid #30363d; border-radius: 4px;">
<strong>Block {i+1} ({item_type}) {status_icon}:</strong><br>
{formatted_value}
</div>''')
            return ''.join(blocks)
        else:
            # Single output
            return self.format_json_string_content(output_data)
    
    def get_tool_status_icon(self, tool_item):
        """Get status icon for tool based on completion and errors"""
        is_complete = tool_item.get('isComplete', False)
        
        # Check for errors in resultDetails output
        if 'resultDetails' in tool_item and 'output' in tool_item['resultDetails']:
            output_data = tool_item['resultDetails']['output']
            if isinstance(output_data, list):
                # Check if any output block has error
                for item in output_data:
                    if isinstance(item, dict) and item.get('error', False):
                        return '❌'
        
        return '✅' if is_complete else '⏳'
    
    def format_tool_call_combined(self, prepare_item, serialized_item):
        """Format combined tool call from prepare and serialized items"""
        tool_id = serialized_item.get('toolId', prepare_item.get('toolName', 'unknown'))
        tool_call_id = serialized_item.get('toolCallId', 'unknown')
        
        # Get invocation message from serialized item
        invocation_msg = ""
        if 'invocationMessage' in serialized_item:
            if isinstance(serialized_item['invocationMessage'], dict):
                invocation_msg = serialized_item['invocationMessage'].get('value', '')
            else:
                invocation_msg = str(serialized_item['invocationMessage'])
        
        # Get command details for terminal tools and file operations
        command_info = ""
        is_terminal_tool = False
        preview_html = ""
        
        if 'toolSpecificData' in serialized_item and serialized_item['toolSpecificData'].get('kind') == 'terminal':
            is_terminal_tool = True
            command_data = serialized_item['toolSpecificData']
            if 'commandLine' in command_data:
                command = command_data['commandLine'].get('original', '')
                command_info = f"<strong>Command:</strong> <code>{self.escape_html(command)}</code>"
        
        # Check for file operations (readFile, listDirectory)
        elif tool_id in ['copilot_readFile', 'copilot_listDirectory']:
            # Extract path from serialized_item uris
            if 'invocationMessage' in serialized_item and 'uris' in serialized_item['invocationMessage']:
                uris = serialized_item['invocationMessage']['uris']
                # Get first URI path
                for uri_key, uri_data in uris.items():
                    if 'path' in uri_data:
                        file_path = uri_data['path']
                        if tool_id == 'copilot_readFile':
                            preview_html = f'''<div class="tool-preview">📄 <code>{self.escape_html(file_path)}</code></div>'''
                        elif tool_id == 'copilot_listDirectory':
                            preview_html = f'''<div class="tool-preview">📁 <code>{self.escape_html(file_path)}</code></div>'''
                        break
        
        # For terminal tools, show only command, not the generic invocation message
        if is_terminal_tool and command_info:
            tool_invocation_content = command_info
        else:
            tool_invocation_content = self.escape_html(invocation_msg) + command_info
        
        # Check if it's an MCP tool and extract Input/Output
        input_output_html = ""
        if 'resultDetails' in serialized_item:
            result_details = serialized_item['resultDetails']
            if 'input' in result_details or 'output' in result_details:
                input_data = result_details.get('input', '')
                output_data = result_details.get('output', '')
                
                # Format input
                input_formatted = self.format_json_string_content(input_data) if input_data else "No input data"
                
                # Format output with multiple blocks support
                output_formatted = self.format_output_blocks(output_data) if output_data else "No output data"
                
                input_output_html = f'''
<strong>📥 Input:</strong>
<div style="margin: 8px 0; padding: 8px; background: #161b22; border: 1px solid #30363d; border-radius: 4px;">
{input_formatted}
</div>

<strong>📤 Output:</strong>
<div style="margin: 8px 0;">
{output_formatted}
</div>
'''
        
        # Create combined JSON metadata as array (like in original)
        combined_metadata = [prepare_item, serialized_item]
        metadata_json = json.dumps(combined_metadata, indent=2)
        metadata_json_html = self.escape_html(metadata_json).replace('\n', '<br>')
        
        # Format tool name for display
        display_tool_name = self.format_tool_name(tool_id)
        
        # Create unique ID for this tool call
        tool_html_id = f"tool_{tool_call_id.replace('-', '_')}"
        
        # Get status icon (with error checking)
        status_icon = self.get_tool_status_icon(serialized_item)
        
        # Build the details content based on tool type
        if input_output_html:
            # MCP tools with Input/Output
            details_content = f'''<strong>📋 Tool Invocation:</strong><pre>{tool_invocation_content}</pre>{input_output_html}<strong>🔧 Raw Metadata:</strong><pre>{metadata_json_html}</pre>'''
        else:
            # Regular tools
            details_content = f'''<strong>📋 Tool Invocation:</strong><pre>{tool_invocation_content}</pre><strong>🔧 Raw Metadata:</strong><pre>{metadata_json_html}</pre>'''
        
        # For terminal tools, show command preview outside the expandable block
        if is_terminal_tool and command_info:
            return f'''<div class="tool-call"><div class="tool-header" onclick="toggleAttachment('{tool_html_id}')"><span class="tool-icon">🔧</span><span class="tool-name">{self.escape_html(display_tool_name)}</span><span class="tool-status">{status_icon}</span></div><div class="tool-preview"><code>{self.escape_html(command_data['commandLine'].get('original', ''))}</code></div><div class="attachment-details" id="{tool_html_id}">{details_content}</div></div>'''
        # For file operations, show preview as well  
        elif preview_html:
            return f'''<div class="tool-call"><div class="tool-header" onclick="toggleAttachment('{tool_html_id}')"><span class="tool-icon">🔧</span><span class="tool-name">{self.escape_html(display_tool_name)}</span><span class="tool-status">{status_icon}</span></div>{preview_html}<div class="attachment-details" id="{tool_html_id}">{details_content}</div></div>'''
        else:
            return f'''<div class="tool-call"><div class="tool-header" onclick="toggleAttachment('{tool_html_id}')"><span class="tool-icon">🔧</span><span class="tool-name">{self.escape_html(display_tool_name)}</span><span class="tool-status">{status_icon}</span></div><div class="attachment-details" id="{tool_html_id}">{details_content}</div></div>'''
    
    def format_tool_call(self, tool_item):
        """Format a tool call as expandable HTML block"""
        tool_id = tool_item.get('toolId', 'unknown')
        tool_call_id = tool_item.get('toolCallId', 'unknown')
        
        # Get invocation message
        invocation_msg = ""
        if 'invocationMessage' in tool_item:
            if isinstance(tool_item['invocationMessage'], dict):
                invocation_msg = tool_item['invocationMessage'].get('value', '')
            else:
                invocation_msg = str(tool_item['invocationMessage'])
        
        # Get command details for terminal tools and file operations
        command_info = ""
        is_terminal_tool = False
        preview_html = ""
        
        if 'toolSpecificData' in tool_item and tool_item['toolSpecificData'].get('kind') == 'terminal':
            is_terminal_tool = True
            command_data = tool_item['toolSpecificData']
            if 'commandLine' in command_data:
                command = command_data['commandLine'].get('original', '')
                command_info = f"<strong>Command:</strong> <code>{self.escape_html(command)}</code>"
                # Create preview for outside expandable block
                preview_html = f'''<div class="tool-preview"><code>{self.escape_html(command)}</code></div>'''
        
        # Check for file operations (readFile, listDirectory) 
        elif tool_id in ['copilot_readFile', 'copilot_listDirectory']:
            # Extract path from tool_item uris
            if 'invocationMessage' in tool_item and 'uris' in tool_item['invocationMessage']:
                uris = tool_item['invocationMessage']['uris']
                # Get first URI path
                for uri_key, uri_data in uris.items():
                    if 'path' in uri_data:
                        file_path = uri_data['path']
                        if tool_id == 'copilot_readFile':
                            preview_html = f'''<div class="tool-preview">📄 <code>{self.escape_html(file_path)}</code></div>'''
                        elif tool_id == 'copilot_listDirectory':
                            preview_html = f'''<div class="tool-preview">📁 <code>{self.escape_html(file_path)}</code></div>'''
                        break
        
        # For terminal tools, show only command, not the generic invocation message
        if is_terminal_tool and command_info:
            tool_invocation_content = command_info
        else:
            tool_invocation_content = self.escape_html(invocation_msg) + command_info
        
        # Check if it's an MCP tool and extract Input/Output
        input_output_html = ""
        if 'resultDetails' in tool_item:
            result_details = tool_item['resultDetails']
            if 'input' in result_details or 'output' in result_details:
                input_data = result_details.get('input', '')
                output_data = result_details.get('output', '')
                
                # Format input
                input_formatted = self.format_json_string_content(input_data) if input_data else "No input data"
                
                # Format output with multiple blocks support
                output_formatted = self.format_output_blocks(output_data) if output_data else "No output data"
                
                input_output_html = f'''
<strong>📥 Input:</strong>
<div style="margin: 8px 0; padding: 8px; background: #161b22; border: 1px solid #30363d; border-radius: 4px;">
{input_formatted}
</div>

<strong>📤 Output:</strong>
<div style="margin: 8px 0;">
{output_formatted}
</div>
'''
        
        # Create JSON metadata for display
        metadata_json = json.dumps(tool_item, indent=2)
        # Convert \n to <br> for proper HTML display
        metadata_json_html = self.escape_html(metadata_json).replace('\n', '<br>')
        
        # Format tool name for display
        display_tool_name = self.format_tool_name(tool_id)
        
        # Create unique ID for this tool call
        tool_html_id = f"tool_{tool_call_id.replace('-', '_')}"
        
        # Get status icon (with error checking)
        status_icon = self.get_tool_status_icon(tool_item)
        
        # Build the details content based on tool type
        if input_output_html:
            # MCP tools with Input/Output
            details_content = f'''<strong>📋 Tool Invocation:</strong><pre>{tool_invocation_content}</pre>{input_output_html}<strong>🔧 Raw Metadata:</strong><pre>{metadata_json_html}</pre>'''
        else:
            # Regular tools
            details_content = f'''<strong>📋 Tool Invocation:</strong><pre>{tool_invocation_content}</pre><strong>🔧 Raw Metadata:</strong><pre>{metadata_json_html}</pre>'''
        
        return f'''<div class="tool-call"><div class="tool-header" onclick="toggleAttachment('{tool_html_id}')"><span class="tool-icon">🔧</span><span class="tool-name">{self.escape_html(display_tool_name)}</span><span class="tool-status">{status_icon}</span></div>{preview_html}<div class="attachment-details" id="{tool_html_id}">{details_content}</div></div>'''
    
    def create_html(self, session_data):
        session_id = session_data.get('_file', 'unknown').replace('.json', '')
        workspace_info = session_data.get('_workspace', 'Unknown Workspace')
        requests = session_data.get('requests', [])
        
        html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Copilot Chat - {session_id[:8]}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
            background: #1e1e1e;
            color: #cccccc;
            margin: 0;
            padding: 0;
            line-height: 1.5;
        }}
        
        .chat-container {{
            max-width: 800px;
            margin: 0 auto;
            height: 100vh;
            display: flex;
            flex-direction: column;
        }}
        
        .header {{
            background: #252526;
            padding: 16px 20px;
            border-bottom: 1px solid #3c3c3c;
            display: flex;
            align-items: center;
            gap: 12px;
        }}
        
        .header h1 {{
            margin: 0;
            font-size: 16px;
            font-weight: 600;
        }}
        
        .messages {{
            flex: 1;
            overflow-y: auto;
            padding: 20px;
        }}
        
        .message {{
            margin-bottom: 24px;
            display: flex;
            gap: 12px;
        }}
        
        .avatar {{
            width: 32px;
            height: 32px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
            font-weight: 600;
            font-size: 12px;
        }}
        
        .user-avatar {{
            background: #0e639c;
            color: white;
        }}
        
        .assistant-avatar {{
            background: linear-gradient(45deg, #0078d4, #005a9e);
            color: white;
        }}
        
        .message-content {{
            flex: 1;
        }}
        
        .message-header {{
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 8px;
        }}
        
        .author {{
            font-weight: 600;
            font-size: 14px;
        }}
        
        .timestamp {{
            color: #8c8c8c;
            font-size: 12px;
        }}
        
        .message-body {{
            background: #2d2d30;
            padding: 12px 16px;
            border-radius: 8px;
            border: 1px solid #3c3c3c;
            white-space: pre-wrap;
            word-break: break-word;
        }}
        
        .assistant .message-body {{
            background: #262626;
        }}
        
        .attachments {{
            margin-top: 8px;
            padding: 0;
        }}
        
        .attachment {{
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 8px 12px;
            margin: 4px 0;
            background: #1a1a1a;
            border: 1px solid #404040;
            border-radius: 4px;
            font-size: 12px;
            color: #9cdcfe;
            cursor: pointer;
            transition: background-color 0.2s;
        }}
        
        .attachment:hover {{
            background: #2a2a2a;
        }}
        
        .attachment.expanded {{
            border-color: #569cd6;
        }}
        
        .attachment-details {{
            margin-top: 8px;
            padding: 12px;
            background: #0d1117;
            border: 1px solid #404040;
            border-radius: 4px;
            font-family: 'Consolas', 'Liberation Mono', monospace;
            font-size: 11px;
            white-space: pre-wrap;
            max-height: 400px;
            max-width: 100%;
            overflow: auto;
            display: none;
            box-sizing: border-box;
        }}
        
        .attachment.expanded .attachment-details {{
            display: block;
        }}
        
        .attachment-details pre {{
            white-space: pre-wrap;
            word-wrap: break-word;
            margin: 0;
            padding: 8px;
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 3px;
            overflow-x: auto;
            max-width: 100%;
            box-sizing: border-box;
        }}
        
        .highlight {{
            background-color: #ffeb3b;
            color: #000;
            padding: 2px 4px;
            border-radius: 2px;
        }}
        
        .tool-call {{
            margin: 8px 0;
            border: 1px solid #404040;
            border-radius: 4px;
            background: #1e1e1e;
        }}
        
        .tool-header {{
            padding: 8px 12px;
            background: #252526;
            border-radius: 4px 4px 0 0;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        
        .tool-header:hover {{
            background: #2d2d30;
        }}
        
        .tool-icon {{
            font-size: 14px;
        }}
        
        .tool-name {{
            flex: 1;
            font-weight: 500;
        }}
        
        .tool-status {{
            font-size: 12px;
        }}
        
        .tool-preview {{
            padding: 8px 12px;
            background: #0d1117;
            border-top: 1px solid #404040;
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 13px;
            color: #f0f6fc;
        }}
        
        .tool-preview code {{
            background: transparent;
            color: #7dd3fc;
            padding: 0;
        }}
        
        .attachment-icon {{
            width: 16px;
            height: 16px;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        
        .attachment-info {{
            flex: 1;
            display: flex;
            flex-direction: column;
            gap: 2px;
        }}
        
        .attachment-name {{
            font-weight: 500;
        }}
        
        .attachment-desc {{
            color: #8c8c8c;
            font-size: 11px;
        }}
        
        .technical-info {{
            margin-top: 8px;
            padding: 8px 12px;
            background: #1a3151;
            border: 1px solid #2d5a87;
            border-radius: 6px;
            font-size: 12px;
            cursor: pointer;
        }}
        
        .technical-info:hover {{
            background: #1f3a5f;
        }}
        
        .footer {{
            padding: 12px 20px;
            border-top: 1px solid #3c3c3c;
            background: #252526;
            font-size: 12px;
            color: #8c8c8c;
            text-align: center;
        }}
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="header">
            <div style="width: 24px; height: 24px; background: linear-gradient(45deg, #0078d4, #005a9e); border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; font-size: 12px;">AI</div>
            <h1>GitHub Copilot Chat</h1>
        </div>
        
        <div class="messages">
'''
        
        if not requests:
            html += '''
            <div style="text-align: center; padding: 60px; color: #8c8c8c;">
                <p>Нет сообщений в этом чате</p>
            </div>
'''
        else:
            for i, request in enumerate(requests):
                # User message
                user_text = ""
                if 'message' in request:
                    msg = request['message']
                    if 'text' in msg:
                        user_text = msg['text']
                    elif 'parts' in msg:
                        for part in msg['parts']:
                            if 'text' in part:
                                user_text += part['text']
                
                html += f'''
            <div class="message user">
                <div class="avatar user-avatar">U</div>
                <div class="message-content">
                    <div class="message-header">
                        <span class="author">You</span>
                    </div>
                    <div class="message-body">{self.escape_html(user_text)}</div>
'''
                
                # Add attachments/variables
                if 'variableData' in request and 'variables' in request['variableData']:
                    variables = request['variableData']['variables']
                    if variables:
                        html += '''
                    <div class="attachments">
'''
                        for j, var in enumerate(variables):
                            attachment = self.format_attachment(var)
                            attachment_id = f"attachment_{i}_{j}_{hash(str(var))}"
                            
                            # Get file content if available
                            file_content = ""
                            metadata_json = ""
                            
                            if attachment['kind'] == 'file' and 'value' in var:
                                if 'uri' in var['value']:
                                    uri = var['value']['uri']
                                    file_path = uri.get('path', uri.get('fsPath', ''))
                                    range_info = var['value'].get('range')
                                    file_content = self.read_file_content(file_path, range_info)
                                    
                            elif attachment['kind'] == 'promptFile' and 'value' in var:
                                file_path = var['value'].get('path', '')
                                file_content = self.read_file_content(file_path)
                            
                            # Create JSON metadata for display
                            metadata_json = json.dumps(var, indent=2)
                            # Convert \n to <br> for proper HTML display
                            metadata_json_html = self.escape_html(metadata_json).replace('\n', '<br>')
                            
                            html += f'''
                        <div class="attachment" onclick="toggleAttachment('{attachment_id}')">
                            <div class="attachment-icon">{attachment['icon']}</div>
                            <div class="attachment-info">
                                <div class="attachment-name">{self.escape_html(attachment['name'])}</div>
                                <div class="attachment-desc">{self.escape_html(attachment['description'])}</div>
                            </div>
                        </div>
                        <div class="attachment-details" id="{attachment_id}">
<strong>📄 File Content:</strong>
<pre>{file_content}</pre>

<strong>🔧 Raw Metadata:</strong>
<pre>{metadata_json_html}</pre>
                        </div>
'''
                        html += '''
                    </div>
'''
                
                html += '''
                </div>
            </div>
'''
                
                # Assistant response with tool calls integration
                assistant_html = ""
                if 'response' in request:
                    response = request['response']
                    if isinstance(response, list):
                        assistant_html = self.process_response_with_tools(response)
                    elif isinstance(response, dict) and 'value' in response:
                        assistant_html = self.escape_html(str(response['value']))
                
                html += f'''
            <div class="message assistant">
                <div class="avatar assistant-avatar">AI</div>
                <div class="message-content">
                    <div class="message-header">
                        <span class="author">GitHub Copilot</span>
                    </div>
                    <div class="message-body">{assistant_html}</div>
                </div>
            </div>
'''
        
        html += f'''
        </div>
        
        <div class="footer">
            Session: {session_id} • Workspace: {workspace_info} • Exported: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </div>
    </div>
    
    <script>
        function toggleAttachment(id) {{
            const element = document.getElementById(id);
            const attachment = element.previousElementSibling;
            
            if (element.style.display === 'block') {{
                element.style.display = 'none';
                attachment.classList.remove('expanded');
            }} else {{
                element.style.display = 'block';
                attachment.classList.add('expanded');
            }}
        }}
    </script>
</body>
</html>'''
        
        return html
    
    def export_specific_session(self, session_id: str):
        """Export specific chat session by ID"""
        logger.info(f"Searching for session: {session_id}")
        
        workspaces = self.find_workspaces()
        if not workspaces:
            logger.error("No workspaces found")
            return
        
        # Search for the specific session across all workspaces
        for workspace in workspaces:
            session_file = workspace / "chatSessions" / f"{session_id}.json"
            if session_file.exists():
                logger.info(f"Found session in workspace: {workspace.name}")
                try:
                    with open(session_file, 'r', encoding='utf-8') as f:
                        session_data = json.load(f)
                        session_data['_file'] = session_file.name
                        session_data['_workspace'] = workspace.name
                    
                    html_content = self.create_html(session_data)
                    output_file = self.output_dir / f"chat_{session_id}.html"
                    
                    with open(output_file, 'w', encoding='utf-8') as f:
                        f.write(html_content)
                    
                    logger.info(f"✅ Exported session to: {output_file}")
                    return output_file
                    
                except Exception as e:
                    logger.error(f"Failed to export session: {e}")
                    return None
        
        logger.error(f"Session {session_id} not found in any workspace")
        return None

    def export_test(self):
        logger.info("Starting test export...")
        
        workspaces = self.find_workspaces()
        if not workspaces:
            logger.error("No workspaces found")
            return
        
        workspace = workspaces[0]
        session_data = self.read_session(workspace)
        
        if not session_data:
            logger.error("No session data found")
            return
        
        html_content = self.create_html(session_data)
        output_file = self.output_dir / "test_chat.html"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"Exported to: {output_file}")

def main():
    import sys
    
    print(f"Arguments: {sys.argv}")
    
    if len(sys.argv) > 1:
        session_id = sys.argv[1]
        print(f"Exporting session: {session_id}")
        exporter = SimpleChatExporter(r'C:\Java\VSCode-settings')
        result = exporter.export_specific_session(session_id)
        if result:
            print(f"✅ Chat exported: {result}")
        else:
            print(f"❌ Failed to export session: {session_id}")
    else:
        print("No session ID provided, running test export")
        exporter = SimpleChatExporter(r'C:\Java\VSCode-settings')
        exporter.export_test()
        print("✅ Test chat exported: simple_chat_export/test_chat.html")

if __name__ == '__main__':
    main()
