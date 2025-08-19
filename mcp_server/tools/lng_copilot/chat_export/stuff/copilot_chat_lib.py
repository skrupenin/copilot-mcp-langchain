"""
Shared library for GitHub Copilot chat export tools.
Contains common functionality extracted from SimpleChatExporter.
"""

import json
import logging
import os
import re
import sys
from datetime import datetime
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CopilotChatExporter:
    """Core functionality for GitHub Copilot chat export operations."""
    
    def __init__(self, vscode_path: str, output_dir: str = "work/copilot_export"):
        self.vscode_path = Path(vscode_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def find_workspaces(self):
        """Find all workspaces with chat sessions."""
        workspace_storage = self.vscode_path / "User" / "workspaceStorage"
        workspaces = []
        
        if not workspace_storage.exists():
            logger.warning(f"Workspace storage not found: {workspace_storage}")
            return []
        
        for workspace_dir in workspace_storage.iterdir():
            if workspace_dir.is_dir() and (workspace_dir / "chatSessions").exists():
                # Get workspace info
                workspace_info = {
                    'id': workspace_dir.name,
                    'path': str(workspace_dir),
                    'chat_dir': str(workspace_dir / "chatSessions"),
                    'sessions_count': 0,
                    'workspace_name': 'Unknown'
                }
                
                # Count sessions
                chat_dir = workspace_dir / "chatSessions"
                if chat_dir.exists():
                    workspace_info['sessions_count'] = len(list(chat_dir.glob("*.json")))
                
                # Try to get workspace name from workspace.json
                workspace_json = workspace_dir / "workspace.json"
                if workspace_json.exists():
                    try:
                        with open(workspace_json, 'r', encoding='utf-8') as f:
                            ws_data = json.load(f)
                            # Extract folder path for workspace name
                            if 'folder' in ws_data:
                                folder_path = ws_data['folder']
                                if isinstance(folder_path, str):
                                    workspace_info['workspace_name'] = os.path.basename(folder_path)
                    except Exception as e:
                        logger.debug(f"Failed to read workspace.json: {e}")
                
                workspaces.append(workspace_info)
        
        logger.info(f"Found {len(workspaces)} workspaces with chat sessions")
        return workspaces
    
    def list_sessions_in_workspace(self, workspace_id: str):
        """List all chat sessions in a specific workspace."""
        workspace_storage = self.vscode_path / "User" / "workspaceStorage"
        workspace_dir = workspace_storage / workspace_id
        chat_dir = workspace_dir / "chatSessions"
        
        if not chat_dir.exists():
            return []
        
        sessions = []
        for session_file in chat_dir.glob("*.json"):
            session_info = {
                'id': session_file.stem,
                'file_path': str(session_file),
                'file_size': session_file.stat().st_size,
                'modified_time': datetime.fromtimestamp(session_file.stat().st_mtime).isoformat(),
                'messages_count': 0
            }
            
            # Try to count messages
            try:
                with open(session_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if 'requests' in data:
                        session_info['messages_count'] = len(data['requests'])
            except Exception as e:
                logger.debug(f"Failed to read session {session_file}: {e}")
            
            sessions.append(session_info)
        
        return sessions
    
    def read_session(self, workspace_id: str, session_id: str):
        """Read a specific chat session."""
        workspace_storage = self.vscode_path / "User" / "workspaceStorage"
        session_file = workspace_storage / workspace_id / "chatSessions" / f"{session_id}.json"
        
        if not session_file.exists():
            return None
        
        try:
            with open(session_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                data['_file'] = session_file.name
                data['_workspace'] = workspace_id
                return data
        except Exception as e:
            logger.error(f"Failed to read session {session_file}: {e}")
            return None
    
    def escape_html(self, text):
        """Escape HTML characters."""
        if not text:
            return ""
        return (text.replace('&', '&amp;')
                   .replace('<', '&lt;')
                   .replace('>', '&gt;')
                   .replace('"', '&quot;'))
    
    def extract_text_from_response(self, response):
        """Extract text and tool calls from response for Markdown rendering."""
        if isinstance(response, list):
            parts = []
            i = 0
            
            while i < len(response):
                item = response[i]
                
                if 'value' in item:
                    parts.append(str(item['value']))
                    i += 1
                elif item.get('kind') == 'inlineReference':
                    # Process inlineReference objects
                    fs_path = item.get('inlineReference', {}).get('fsPath', '')
                    if fs_path:
                        folder_name = os.path.basename(fs_path) or os.path.basename(os.path.dirname(fs_path))
                        parts.append(f'📁<a href="file:///{fs_path.replace(chr(92), "/")}" style="color: #58a6ff; text-decoration: none; margin-left: 4px;" title="{fs_path}">{folder_name}</a>')
                    i += 1
                elif item.get('kind') == 'prepareToolInvocation':
                    # Look for corresponding toolInvocationSerialized
                    tool_name = item.get('toolName')
                    serialized_item = None
                    j = i + 1
                    
                    while j < len(response):
                        if (response[j].get('kind') == 'toolInvocationSerialized' and 
                            response[j].get('toolId') == tool_name):
                            serialized_item = response[j]
                            break
                        j += 1
                    
                    # Format combined tool call
                    if serialized_item:
                        tool_html = self.format_tool_call_combined(item, serialized_item)
                        parts.append(tool_html)
                        # Skip the serialized item when we encounter it
                        if j < len(response):
                            response[j]['_processed'] = True
                    else:
                        parts.append(f'🔧 Tool: {tool_name} (preparing...)')
                        
                    i += 1
                elif item.get('kind') == 'toolInvocationSerialized':
                    # Check if this wasn't already processed with a prepare item
                    if not item.get('_processed'):
                        tool_html = self.format_tool_call(item)
                        parts.append(tool_html)
                    i += 1
                else:
                    i += 1
            
            return '\n'.join(parts)
        elif isinstance(response, dict) and 'value' in response:
            return str(response['value'])
        return ""
    
    def simple_markdown_to_html(self, text):
        """Convert basic Markdown to HTML with simple patterns, preserving HTML tool calls."""
        if not text:
            return ""
        
        # Process inline references first (before any HTML escaping)
        text = self.process_inline_references(text)
        
        # First find and extract HTML tool calls AND inlineReference links
        protected_html = {}
        placeholder_counter = 0
        
        # Find all tool calls and replace them with placeholders
        def replace_html_content(match):
            nonlocal placeholder_counter
            html_content = match.group(0)
            placeholder = f"__PROTECTED_HTML_{placeholder_counter}__"
            protected_html[placeholder] = html_content
            placeholder_counter += 1
            return placeholder
        
        # Extract tool calls (they are complete HTML blocks)
        text_with_placeholders = text
        
        # First protect inlineReference links (📁<a href="...">...</a>)
        inline_ref_pattern = r'📁<a href="[^"]*"[^>]*>.*?</a>'
        
        # Count matches first for debugging
        matches = re.findall(inline_ref_pattern, text_with_placeholders, flags=re.DOTALL)
        if matches:
            logger.info(f"Found {len(matches)} inlineReference links to protect")
        
        text_with_placeholders = re.sub(inline_ref_pattern, replace_html_content, text_with_placeholders, flags=re.DOTALL)
        
        # Then protect tool-call divs
        start_tag = '<div class="tool-call">'
        end_tag = '</div>'
        
        while start_tag in text_with_placeholders:
            start_pos = text_with_placeholders.find(start_tag)
            if start_pos == -1:
                break
                
            # Find the matching end tag by counting nested divs
            current_pos = start_pos + len(start_tag)
            div_count = 1
            while div_count > 0 and current_pos < len(text_with_placeholders):
                next_div_start = text_with_placeholders.find('<div', current_pos)
                next_div_end = text_with_placeholders.find('</div>', current_pos)
                
                if next_div_end == -1:
                    break
                    
                if next_div_start != -1 and next_div_start < next_div_end:
                    div_count += 1
                    current_pos = next_div_start + 4
                else:
                    div_count -= 1
                    current_pos = next_div_end + 6
            
            if div_count == 0:
                # Found complete tool-call block
                tool_html = text_with_placeholders[start_pos:current_pos]
                placeholder = f"__PROTECTED_HTML_{placeholder_counter}__"
                protected_html[placeholder] = tool_html
                text_with_placeholders = text_with_placeholders[:start_pos] + placeholder + text_with_placeholders[current_pos:]
                placeholder_counter += 1
            else:
                break
        
        # Now escape HTML for the remaining text
        html = self.escape_html(text_with_placeholders)
        
        # Convert code blocks (```code```)
        html = re.sub(r'```([^`]*?)```', r'<pre style="background: #161b22; padding: 8px; border-radius: 4px; border: 1px solid #30363d;"><code>\1</code></pre>', html, flags=re.DOTALL)
        
        # Convert inline code (`code`)
        html = re.sub(r'`([^`]+?)`', r'<code style="background: #161b22; padding: 2px 4px; border-radius: 3px; font-size: 0.9em;">\1</code>', html)
        
        # Convert headers (## header)
        html = re.sub(r'^### ([^\n]+)', r'<h3 style="color: #f0f6fc; margin: 16px 0 8px 0; font-size: 1.25em; font-weight: 600;">\1</h3>', html, flags=re.MULTILINE)
        html = re.sub(r'^## ([^\n]+)', r'<h2 style="color: #f0f6fc; margin: 20px 0 10px 0; font-size: 1.5em; font-weight: 600; border-bottom: 1px solid #30363d; padding-bottom: 8px;">\1</h2>', html, flags=re.MULTILINE)
        html = re.sub(r'^# ([^\n]+)', r'<h1 style="color: #f0f6fc; margin: 24px 0 16px 0; font-size: 2em; font-weight: 600; border-bottom: 1px solid #30363d; padding-bottom: 10px;">\1</h1>', html, flags=re.MULTILINE)
        
        # Convert bold (**text**)
        html = re.sub(r'\*\*([^*]+?)\*\*', r'<strong>\1</strong>', html)
        
        # Convert italic (*text*)
        html = re.sub(r'\*([^*]+?)\*', r'<em>\1</em>', html)
        
        # Convert links [text](url)
        html = re.sub(r'\[([^\]]+?)\]\(([^)]+?)\)', r'<a href="\2" style="color: #58a6ff;" target="_blank">\1</a>', html)
        
        # Convert line breaks
        html = html.replace('\n', '<br>')
        
        # Clean up extra <br> tags around headers (before tool call restoration)
        html = re.sub(r'<br>\s*(<h[123][^>]*>)', r'\1', html)
        html = re.sub(r'(</h[123]>)\s*<br>', r'\1', html)
        
        # Restore protected HTML (tool calls and inlineReference links)
        for placeholder, protected_html_content in protected_html.items():
            is_inline_reference = protected_html_content.startswith('📁<a href=')
            
            placeholder_with_br = '<br>' + placeholder
            if placeholder_with_br in html:
                if is_inline_reference:
                    html = html.replace(placeholder_with_br, '<br>' + protected_html_content)
                else:
                    html = html.replace(placeholder_with_br, ' ' + protected_html_content)
            else:
                if is_inline_reference:
                    html = html.replace(placeholder, protected_html_content)
                else:
                    html = html.replace(placeholder, ' ' + protected_html_content)

        # Additional cleanup after protected HTML restoration
        html = re.sub(r'<br>\s*🔧', '🔧', html)
        html = re.sub(r'<br>\s*📋', '📋', html)
        html = re.sub(r'<br>\s*📁(<a[^>]*>[^<]*</a>)', r'📁\1<br>', html)
        
        return html
    
    def process_inline_references(self, content):
        """Process JSON inline references and convert them to file links."""
        pattern = r'\{\s*"kind":\s*"inlineReference",\s*"inlineReference":\s*\{[^}]*"fsPath":\s*"([^"]+)"[^}]*\}[^}]*\}'
        
        def replace_reference(match):
            try:
                json_text = match.group(0)
                json_obj = json.loads(json_text)
                fs_path = json_obj.get('inlineReference', {}).get('fsPath', '')
                
                if fs_path:
                    folder_name = os.path.basename(fs_path) or os.path.basename(os.path.dirname(fs_path))
                    logger.info(f"Converting inlineReference: {fs_path} -> {folder_name}")
                    return f'📁<a href="file:///{fs_path.replace(chr(92), "/")}" style="color: #58a6ff; text-decoration: none; margin-left: 4px;" title="{fs_path}">{folder_name}</a>'
                
            except Exception as e:
                logger.warning(f"Failed to parse inlineReference: {e}")
            
            return match.group(0)
        
        return re.sub(pattern, replace_reference, content)
    
    def format_tool_call(self, tool_item):
        """Format a tool call as expandable HTML block."""
        # Implementation from original script (simplified)
        tool_id = tool_item.get('toolId', 'unknown')
        tool_call_id = tool_item.get('toolCallId', 'unknown')
        
        display_tool_name = self.format_tool_name(tool_id)
        tool_html_id = f"tool_{tool_call_id.replace('-', '_')}"
        
        return f'''<div class="tool-call"><div class="tool-header" onclick="toggleAttachment('{tool_html_id}')"><span class="tool-icon">🔧</span><span class="tool-name">{self.escape_html(display_tool_name)}</span><span class="tool-status">✅</span></div><div class="attachment-details" id="{tool_html_id}">Tool details...</div></div>'''
    
    def format_tool_call_combined(self, prepare_item, serialized_item):
        """Format combined tool call from prepare and serialized items."""
        return self.format_tool_call(serialized_item)
    
    def format_tool_name(self, tool_id):
        """Format tool name for display."""
        if tool_id.startswith('mcp_') and '-mcp_lng_' in tool_id:
            parts = tool_id.split('-mcp_lng_')
            if len(parts) == 2:
                server_name = parts[0]
                tool_name = parts[1]
                return f"[MCP] {server_name}: lng_{tool_name}"
        return tool_id
    
    def create_html(self, session_data):
        """Create HTML from session data (simplified version)."""
        session_id = session_data.get('_file', 'unknown').replace('.json', '')
        workspace_info = session_data.get('_workspace', 'Unknown Workspace')
        requests = session_data.get('requests', [])
        
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Copilot Chat - {session_id[:8]}</title>
    <style>
        body {{ font-family: system-ui; background: #1e1e1e; color: #cccccc; margin: 0; padding: 20px; }}
        .message {{ margin-bottom: 20px; padding: 15px; background: #2d2d30; border-radius: 8px; }}
        .user {{ border-left: 3px solid #0078d4; }}
        .assistant {{ border-left: 3px solid #569cd6; }}
        pre {{ background: #161b22; padding: 10px; border-radius: 4px; overflow-x: auto; }}
        code {{ background: #161b22; padding: 2px 4px; border-radius: 3px; }}
    </style>
</head>
<body>
    <h1>GitHub Copilot Chat</h1>
    <p>Session: {session_id} | Workspace: {workspace_info}</p>
"""
        
        for i, request in enumerate(requests):
            # User message
            if 'message' in request:
                user_text = request['message']
                html_content += f'<div class="message user"><strong>You:</strong><br>{self.simple_markdown_to_html(user_text)}</div>'
            
            # Assistant response
            if 'response' in request:
                assistant_text = self.extract_text_from_response(request['response'])
                html_content += f'<div class="message assistant"><strong>GitHub Copilot:</strong><br>{self.simple_markdown_to_html(assistant_text)}</div>'
        
        html_content += """
</body>
</html>"""
        
        return html_content
    
    def export_session(self, workspace_id: str, session_id: str, output_filename: str = None):
        """Export a single session to HTML."""
        session_data = self.read_session(workspace_id, session_id)
        if not session_data:
            return None
        
        if not output_filename:
            output_filename = f"chat_{session_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        
        html_content = self.create_html(session_data)
        output_file = self.output_dir / output_filename
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return str(output_file)
