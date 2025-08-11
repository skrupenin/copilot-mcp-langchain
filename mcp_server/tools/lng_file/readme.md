# lng_file - File Operations Tools

Cross-platform tools for reading and writing text files with advanced features and flexible output formats.

## Tools

### lng_file_read
Reads text files with encoding support and optional offset/limit functionality.

**Key Features:**
- **Dual Output Formats**: Plain text (default) or JSON with metadata
- Support for various encodings (UTF-8, ASCII, CP1251, Latin-1, etc.)
- Offset/limit for reading specific line ranges
- Cross-platform path handling (absolute/relative paths)
- Comprehensive error handling with detailed messages
- Unicode support with proper character handling

**Parameters:**
- `file_path` (required): Path to the file to read
- `encoding` (optional): File encoding, default: 'utf-8'
- `offset` (optional): Number of lines to skip from beginning, default: 0
- `limit` (optional): Maximum number of lines to read
- `output_format` (optional): 'text' (default) or 'json'

### lng_file_write  
Writes text content to files with multiple write modes and comprehensive metadata.

**Key Features:**
- **JSON Metadata Response**: Always returns structured operation details
- Three write modes: create (default), overwrite, append
- Automatic directory creation for nested paths
- Support for various encodings (UTF-8, ASCII, CP1251, Latin-1, etc.)
- Detailed operation metadata with timestamps
- Safe file existence checks with mode validation
- Unicode content support

**Parameters:**
- `file_path` (required): Path to the file to write
- `content` (required): Text content to write
- `encoding` (optional): File encoding, default: 'utf-8'
- `mode` (optional): Write mode - 'create', 'overwrite', or 'append'

## Usage Examples

### Reading Files

```bash
# Read entire file (plain text format - default)
python -m mcp_server.run run lng_file_read '{"file_path":"data.txt"}'

# Read entire file (JSON format with metadata)
python -m mcp_server.run run lng_file_read '{"file_path":"data.txt","output_format":"json"}'

# Read with offset and limit
python -m mcp_server.run run lng_file_read '{"file_path":"data.txt","offset":9,"limit":10}'
```

### Writing Files

```bash
# Create new file
python -m mcp_server.run run lng_file_write '{"file_path":"output.txt","content":"Hello World"}'

# Append to existing file
python -m mcp_server.run run lng_file_write '{"file_path":"log.txt","content":"New entry\\n","mode":"append"}'

# Write with Unicode content
python -m mcp_server.run run lng_file_write '{"file_path":"unicode.txt","content":"Hello 🌍!","encoding":"utf-8"}'
```

## Output Formats

### lng_file_read Output Formats

**Plain Text Format (default)**
```
Line 1 of file
Line 2 of file
Line 3 of file
```

**JSON Format** (when `output_format: "json"`)
```json
{
  "content": "Line 1 of file\nLine 2 of file\nLine 3 of file\n",
  "metadata": {
    "operation": "file_read",
    "file_path": "/path/to/file.txt",
    "encoding": "utf-8",
    "file_size_bytes": 42,
    "lines_count": 3,
    "content_character_count": 39,
    "offset": 0,
    "limit": null,
    "success": true,
    "timestamp": "2025-08-11T12:00:00.000000"
  }
}
```

### lng_file_write Output Format

**Always JSON Response with Metadata**
```json
{
  "metadata": {
    "operation": "file_write",
    "file_path": "/path/to/file.txt",
    "encoding": "utf-8",
    "mode": "create",
    "content_character_count": 25,
    "content_lines_count": 2,
    "file_size_bytes": 25,
    "success": true,
    "timestamp": "2025-08-11T12:00:00.000000"
  }
}
```

## Error Handling

Both tools provide detailed error information in JSON format for common scenarios:

### Read Tool Errors
- **File not found**: Returns JSON with error details
- **Permission denied**: JSON error with access information
- **Encoding errors**: JSON with encoding mismatch details
- **Invalid parameters**: JSON with parameter validation errors

### Write Tool Errors  
- **File exists** (create mode): JSON error with conflict details
- **Permission denied**: JSON error with access information
- **Disk space issues**: JSON error with storage details
- **Invalid paths**: JSON error with path validation details
- **Missing parameters**: JSON error with parameter requirements

### Example Error Response
```json
{
  "metadata": {
    "operation": "file_read",
    "file_path": "/nonexistent/file.txt",
    "success": false,
    "error": "File not found: /nonexistent/file.txt",
    "timestamp": "2025-08-11T12:00:00.000000"
  }
}
```
