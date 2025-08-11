import mcp.types as types
import os
import json
from pathlib import Path

async def tool_info() -> dict:
    """Returns information about the lng_file_list tool."""
    return {
        "description": """Lists all files and directories in a specified directory.

**Parameters:**
- `directory_path` (string, required): Absolute or relative path to the directory to list.
- `path_type` (string, optional): Type of paths to return. Default: 'relative'. Options:
  - 'relative': Return paths relative to the specified directory
  - 'absolute': Return full absolute paths
- `include_directories` (boolean, optional): Include directories in the listing. Default: true.
- `include_files` (boolean, optional): Include files in the listing. Default: true.
- `recursive` (boolean, optional): List files recursively in subdirectories. Default: false.
- `pattern` (string, optional): Filter files by pattern (glob-style). Example: '*.txt', '*.py', etc.
- `show_hidden` (boolean, optional): Include hidden files/directories (starting with '.'). Default: false.
- `output_format` (string, optional): Output format. Default: 'list'. Options:
  - 'list': Simple list of paths
  - 'detailed': Detailed information including size, modified time, type
  - 'json': JSON format with metadata

**Example Usage:**
- List all files in directory: `{"directory_path": "/path/to/dir"}`
- List only files with absolute paths: `{"directory_path": "/path/to/dir", "path_type": "absolute", "include_directories": false}`
- List Python files recursively: `{"directory_path": "/path/to/dir", "recursive": true, "pattern": "*.py"}`
- Detailed listing: `{"directory_path": "/path/to/dir", "output_format": "detailed"}`

**Returns:**
- List of file/directory paths based on parameters
- Detailed metadata when output_format="detailed" or "json"
- Error information if operation fails

This tool is cross-platform and handles both absolute and relative directory paths.""",
        "schema": {
            "type": "object",
            "properties": {
                "directory_path": {
                    "type": "string",
                    "description": "Path to the directory to list (absolute or relative)"
                },
                "path_type": {
                    "type": "string",
                    "description": "Type of paths to return (default: relative)",
                    "enum": ["relative", "absolute"],
                    "default": "relative"
                },
                "include_directories": {
                    "type": "boolean",
                    "description": "Include directories in the listing (default: true)",
                    "default": True
                },
                "include_files": {
                    "type": "boolean",
                    "description": "Include files in the listing (default: true)",
                    "default": True
                },
                "recursive": {
                    "type": "boolean",
                    "description": "List files recursively in subdirectories (default: false)",
                    "default": False
                },
                "pattern": {
                    "type": "string",
                    "description": "Filter files by pattern (glob-style, e.g., '*.txt')"
                },
                "show_hidden": {
                    "type": "boolean",
                    "description": "Include hidden files/directories (default: false)",
                    "default": False
                },
                "output_format": {
                    "type": "string",
                    "description": "Output format (default: list)",
                    "enum": ["list", "detailed", "json"],
                    "default": "list"
                }
            },
            "required": ["directory_path"]
        }
    }

async def run_tool(name: str, parameters: dict) -> list[types.Content]:
    """Lists all files and directories in a specified directory."""
    try:
        # Extract parameters
        directory_path = parameters.get("directory_path", "")
        path_type = parameters.get("path_type", "relative")
        include_directories = parameters.get("include_directories", True)
        include_files = parameters.get("include_files", True)
        recursive = parameters.get("recursive", False)
        pattern = parameters.get("pattern")
        show_hidden = parameters.get("show_hidden", False)
        output_format = parameters.get("output_format", "list")
        
        if not directory_path:
            error_metadata = {
                "operation": "file_list",
                "success": False,
                "error": "directory_path parameter is required"
            }
            result = json.dumps({"metadata": error_metadata}, indent=2)
            return [types.TextContent(type="text", text=result)]
        
        # Convert relative path to absolute if needed
        if not os.path.isabs(directory_path):
            directory_path = os.path.abspath(directory_path)
        
        # Check if directory exists
        if not os.path.exists(directory_path):
            error_metadata = {
                "operation": "file_list",
                "directory_path": directory_path,
                "success": False,
                "error": f"Directory not found: {directory_path}"
            }
            result = json.dumps({"metadata": error_metadata}, indent=2)
            return [types.TextContent(type="text", text=result)]
        
        # Check if it's a directory
        if not os.path.isdir(directory_path):
            error_metadata = {
                "operation": "file_list",
                "directory_path": directory_path,
                "success": False,
                "error": f"Path is not a directory: {directory_path}"
            }
            result = json.dumps({"metadata": error_metadata}, indent=2)
            return [types.TextContent(type="text", text=result)]
        
        # Get list of files and directories
        items = []
        base_path = Path(directory_path)
        
        try:
            if recursive:
                # Recursive listing
                if pattern:
                    paths = base_path.rglob(pattern)
                else:
                    paths = base_path.rglob("*")
            else:
                # Non-recursive listing
                if pattern:
                    paths = base_path.glob(pattern)
                else:
                    paths = base_path.glob("*")
            
            for path in sorted(paths):
                # Skip hidden files/directories if not requested
                if not show_hidden and any(part.startswith('.') for part in path.parts[len(base_path.parts):]):
                    continue
                
                # Filter by type
                if path.is_file() and not include_files:
                    continue
                if path.is_dir() and not include_directories:
                    continue
                
                # Determine path to return
                if path_type == "absolute":
                    item_path = str(path.absolute())
                else:  # relative
                    try:
                        item_path = str(path.relative_to(base_path))
                    except ValueError:
                        # Fallback to absolute if relative calculation fails
                        item_path = str(path.absolute())
                
                # Collect item information
                item_info = {
                    "path": item_path,
                    "name": path.name,
                    "type": "directory" if path.is_dir() else "file"
                }
                
                # Add detailed information if requested
                if output_format in ["detailed", "json"]:
                    try:
                        stat_info = path.stat()
                        item_info.update({
                            "size": stat_info.st_size if path.is_file() else None,
                            "modified_time": stat_info.st_mtime,
                            "permissions": oct(stat_info.st_mode)[-3:],
                            "is_hidden": path.name.startswith('.'),
                            "absolute_path": str(path.absolute())
                        })
                    except (OSError, PermissionError):
                        item_info.update({
                            "size": None,
                            "modified_time": None,
                            "permissions": None,
                            "is_hidden": path.name.startswith('.'),
                            "absolute_path": str(path.absolute()),
                            "error": "Unable to get file stats"
                        })
                
                items.append(item_info)
        
        except PermissionError:
            error_metadata = {
                "operation": "file_list",
                "directory_path": directory_path,
                "success": False,
                "error": f"Permission denied accessing directory: {directory_path}"
            }
            result = json.dumps({"metadata": error_metadata}, indent=2)
            return [types.TextContent(type="text", text=result)]
        except Exception as e:
            error_metadata = {
                "operation": "file_list",
                "directory_path": directory_path,
                "success": False,
                "error": f"Error listing directory: {str(e)}"
            }
            result = json.dumps({"metadata": error_metadata}, indent=2)
            return [types.TextContent(type="text", text=result)]
        
        # Create metadata
        metadata = {
            "operation": "file_list",
            "directory_path": directory_path,
            "path_type": path_type,
            "include_directories": include_directories,
            "include_files": include_files,
            "recursive": recursive,
            "show_hidden": show_hidden,
            "pattern": pattern,
            "total_items": len(items),
            "success": True
        }
        
        # Return result based on output_format
        if output_format == "json":
            result = {
                "items": items,
                "metadata": metadata
            }
            return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
        elif output_format == "detailed":
            # Format detailed output as readable text
            lines = [f"Directory listing: {directory_path}"]
            lines.append(f"Total items: {len(items)}")
            lines.append("")
            
            for item in items:
                line = f"{item['type']:>9}: {item['path']}"
                if item.get('size') is not None:
                    line += f" ({item['size']} bytes)"
                if item.get('error'):
                    line += f" [ERROR: {item['error']}]"
                lines.append(line)
            
            return [types.TextContent(type="text", text="\n".join(lines))]
        else:
            # Default: simple list
            paths = [item['path'] for item in items]
            return [types.TextContent(type="text", text="\n".join(paths))]
        
    except Exception as e:
        error_metadata = {
            "operation": "file_list",
            "success": False,
            "error": str(e)
        }
        result = json.dumps({"metadata": error_metadata}, indent=2)
        return [types.TextContent(type="text", text=result)]
