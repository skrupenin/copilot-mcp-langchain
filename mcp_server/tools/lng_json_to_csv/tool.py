import mcp.types as types
import json
import pandas as pd
from typing import List, Dict, Any, Optional, Union
import re
import os
import pathlib

async def tool_info() -> dict:
    """Returns information about the lng_json_to_csv tool."""
    return {
        "description": """Converts JSON data to CSV or Markdown format using pandas.

**Two modes of operation:**

1. **Text Mode** (default):
   - `json_data` (object/array, required): JSON data as object or array
   - Returns converted result as text

2. **File Mode**:
   - `input_file_path` (string, required): Path to JSON file
   - `output_file_path` (string, required): Path for output CSV/Markdown file
   - Returns status message with paths

**Parameters:**
- `json_data` (object/array, optional): The JSON data to convert (Text Mode) - must be object or array.
- `input_file_path` (string, optional): Path to input JSON file (File Mode).
- `output_file_path` (string, optional): Path to output file (File Mode).
- `format` (string, optional): Output format - 'csv' or 'markdown'. Default: 'csv'.
- `column_delimiter` (string, optional): Column separator. Default: ','.
- `cell_left_delimiter` (string, optional): Left cell delimiter for escaping. Default: '"'.
- `cell_right_delimiter` (string, optional): Right cell delimiter for escaping. Default: '"'.
- `line_chars_need_to_be_escaped_with_cell_delimiter` (string, optional): Characters that need escaping. Default: '\\n",'.
- `header_delimiter` (string, optional): Header delimiter for markdown format. Default: null.
- `line_replacements` (array, optional): String replacements like ["\\"==>\\"\\""]. Default: ["\\"==>\\"\\""]. 
- `padding_to_max_cell_length` (boolean, optional): Pad cells to max length. Default: false.
- `remove_headers_duplicates` (boolean, optional): Remove duplicate headers. Default: true.

**Mode Selection:**
- Use Text Mode: provide `json_data` parameter
- Use File Mode: provide both `input_file_path` and `output_file_path` parameters

**Example Usage:**
- Convert simple JSON array to CSV
- Support complex nested structures
- Handle arrays within objects
- Escape special characters properly
- Process large files efficiently with File Mode

This tool flattens nested JSON structures into tabular format, preserving hierarchy through column headers.""",
        "schema": {
            "type": "object",
            "properties": {
                "json_data": {
                    "description": "JSON data to convert to CSV/Markdown (Text Mode) - object or array",
                    "oneOf": [
                        {"type": "object"},
                        {"type": "array"}
                    ]
                },
                "input_file_path": {
                    "type": "string",
                    "description": "Path to input JSON file (File Mode)"
                },
                "output_file_path": {
                    "type": "string",
                    "description": "Path to output CSV/Markdown file (File Mode)"
                },
                "format": {
                    "type": "string",
                    "enum": ["csv", "markdown"],
                    "default": "csv",
                    "description": "Output format"
                },
                "column_delimiter": {
                    "type": "string",
                    "default": ",",
                    "description": "Column delimiter"
                },
                "cell_left_delimiter": {
                    "type": "string",
                    "default": "\"",
                    "description": "Left cell delimiter for escaping"
                },
                "cell_right_delimiter": {
                    "type": "string", 
                    "default": "\"",
                    "description": "Right cell delimiter for escaping"
                },
                "line_chars_need_to_be_escaped_with_cell_delimiter": {
                    "type": "string",
                    "default": "\n\",",
                    "description": "Characters that need escaping"
                },
                "header_delimiter": {
                    "type": ["string", "null"],
                    "default": None,
                    "description": "Header delimiter (for markdown)"
                },
                "line_replacements": {
                    "type": "array",
                    "items": {"type": "string"},
                    "default": ["\"==>\"\""],
                    "description": "String replacements"
                },
                "padding_to_max_cell_length": {
                    "type": "boolean",
                    "default": False,
                    "description": "Pad cells to max length"
                },
                "remove_headers_duplicates": {
                    "type": "boolean",
                    "default": True,
                    "description": "Remove duplicate headers"
                }
            },
            "required": []
        }
    }

class Matrix:
    """Handles the tabular structure for JSON conversion."""
    
    def __init__(self, structure_info: dict = None):
        self.data: List[List[Optional[str]]] = []
        self.current_header = 0
        self.header_size = 1
        self.current_line = 0
        self.base_line = 0
        self.new_line_flag = False
        self.structure_info = structure_info or {}  # Pre-analyzed structure information
        
    def insert_row(self, row_index: int):
        """Insert a new row at the specified index."""
        new_row = []
        if self.data:
            # Fill with None values to match existing column count
            for _ in range(len(self.data[0]) if self.data else 0):
                new_row.append(None)
        self.data.insert(row_index, new_row)
        
    def insert_column(self, col_index: int):
        """Insert a new column at the specified index."""
        for row in self.data:
            row.insert(col_index, None)
            
    def get_or_create_header(self, key: str) -> int:
        """Get the column index for a key, creating it if needed - matches Java logic exactly."""
        # DEBUG: Отладочный вывод
        DEBUG = False  # Включить для отладки
        
        # Ensure header row exists
        if len(self.data) <= self.current_header:
            self.insert_row(self.current_header)
            self.current_line += 1
            self.base_line += 1
            
        header = self.data[self.current_header]
        
        # Check if key already exists
        for i, header_key in enumerate(header):
            if key == header_key:
                if DEBUG:
                    print(f"DEBUG: Found existing header '{key}' at position {i}")
                return i
                
        # For top-level headers (currentHeader == 0), use intelligent placement
        if self.current_header == 0:
            # Calculate where the next header should be placed considering all reservations
            reserved_width = self.structure_info.get(key, 1)
            
            # Find the next available position considering ALL reserved spaces
            next_pos = len(header)
            
            if DEBUG:
                print(f"DEBUG: Top-level header '{key}' - current header length={len(header)}, reserved_width={reserved_width}")
                print(f"DEBUG: Current header: {header}")
            
            # Extend header to accommodate new column and any reserved space
            while len(header) <= next_pos + reserved_width - 1:
                header.append(None)
                
            header[next_pos] = key
            
            if DEBUG:
                print(f"DEBUG: Placed '{key}' at position {next_pos}")
                print(f"DEBUG: Header after placement: {header}")
            
            return next_pos
            
        # For nested headers, use TRUE Java logic: children go to parent's position first
        if "." not in key:
            raise ValueError(f"Nested header without parent: {key}")
            
        parent_key = key.rsplit(".", 1)[0]
        
        # Find parent position by searching through ALL header levels from level 0
        parent_pos = -1
        
        # Search through all header levels to find the parent
        for level in range(self.current_header + 1):
            if level < len(self.data):
                level_header = self.data[level]
                for i, header_key in enumerate(level_header):
                    if header_key == parent_key:
                        parent_pos = i
                        break
                if parent_pos != -1:
                    break
                    
        if parent_pos == -1:
            # Parent not found - fallback to simple append
            header.append(key)
            return len(header) - 1
            
        # TRUE Java logic: Find next available position within parent's space
        # considering sibling order and their reserved widths
        parent_reserved_width = self.structure_info.get(parent_key, 1)
        parent_end = parent_pos + parent_reserved_width
        
        # Extend header to parent's reserved space
        while len(header) < parent_end:
            header.append(None)
            
        # Find all siblings that are already placed
        occupied_ranges = []
        for level in range(self.current_header + 1):
            if level < len(self.data):
                level_header = self.data[level]
                for i, header_key in enumerate(level_header):
                    if header_key and header_key.startswith(parent_key + ".") and header_key != key:
                        # This is a sibling - mark its range as occupied
                        sibling_width = self.structure_info.get(header_key, 1)
                        occupied_ranges.append((i, i + sibling_width - 1))
        
        # Find first available position within parent's range
        for pos in range(parent_pos, parent_end):
            # Check if this position is occupied by any sibling
            position_occupied = False
            for start, end in occupied_ranges:
                if start <= pos <= end:
                    position_occupied = True
                    break
            
            if not position_occupied and (pos >= len(header) or header[pos] is None or header[pos] == parent_key):
                header[pos] = key
                return pos
                
        # If no space in parent range, place at end
        next_pos = len(header)
        header.append(key)
        return next_pos
    
    def _check_all_children_in_header(self, from_y: int, x: int) -> bool:
        """Check if all children in header column are empty - matches Java logic."""
        for y in range(from_y, self.header_size):
            if y < len(self.data):
                row = self.data[y]
                if x < len(row) and row[x] is not None and row[x] != "":
                    return False
        return True
        
    def set(self, y: int, x: int, value: str):
        """Set a value at the specified position."""
        # Ensure row exists
        while len(self.data) <= y:
            self.data.append([])
            
        # Ensure column exists
        while len(self.data[y]) <= x:
            self.data[y].append(None)
            
        self.data[y][x] = value
        
    def child_header(self):
        """Move to child header level."""
        self.current_header += 1
        if self.current_header == self.header_size:
            self.insert_row(self.header_size)
            self.header_size += 1
            self.base_line += 1
            self.current_line += 1
            
    def parent_header(self):
        """Move back to parent header level."""
        self.current_header -= 1
        if self.current_header < 0:
            self.current_header = 0
            
    def inject(self, x: int, same_line: bool, value: str):
        """Inject a value at the specified column."""
        if self.new_line_flag:
            self.base_line = len(self.data)
            self.current_line = self.base_line - 1
            self.new_line_flag = False
            
        if same_line:
            if (self.base_line < len(self.data) and 
                x < len(self.data[self.base_line]) and 
                self.data[self.base_line][x] is None):
                self.current_line = self.base_line
        else:
            self.current_line += 1
            if self.current_line >= len(self.data):
                self.insert_row(len(self.data))
                
        self.set(self.current_line, x, value)
        
    def inject_at_row(self, x: int, row: int, value: str):
        """Inject a value at a specific row and column."""
        while row >= len(self.data):
            self.insert_row(len(self.data))
        self.set(row, x, value)
        
    @property
    def current_row(self):
        """Get the current row index."""
        return self.current_line
        
    def new_line(self):
        """Mark that we need a new line."""
        self.new_line_flag = True
        
    def remove_headers_duplicates(self):
        """Remove duplicate parts of headers."""
        for y in range(self.header_size):
            if y >= len(self.data):
                continue
            row = self.data[y]
            for x in range(len(row)):
                value = row[x]
                if value is None or value == "":
                    continue
                    
                value_prefix = value + "."
                for yy in range(y + 1, self.header_size):
                    if yy >= len(self.data):
                        continue
                    next_row = self.data[yy]
                    for xx in range(len(row)):
                        if xx >= len(next_row):
                            continue
                        value2 = next_row[xx]
                        if value2 and value2.startswith(value_prefix):
                            next_row[xx] = value2[len(value_prefix):]
                            
    def to_string(self, column_delimiter: str = ",", cell_left_delimiter: Optional[str] = "\"", 
                  cell_right_delimiter: Optional[str] = "\"", 
                  line_chars_need_to_be_escaped_with_cell_delimiter: Optional[str] = "\n\",",
                  header_delimiter: Optional[str] = None,
                  line_replacements: Optional[List[str]] = None,
                  padding_to_max_cell_length: bool = False) -> str:
        """Convert matrix to string format."""
        
        # Parse line replacements
        replacements = []
        if line_replacements:
            for replacement in line_replacements:
                if "==>" in replacement:
                    parts = replacement.split("==>", 1)
                    replacements.append((parts[0], parts[1]))
                    
        result = []
        max_line_length = 0
        header_delimiter_pos = 0
        
        for y in range(len(self.data)):
            row = self.data[y]
            line_parts = []
            line_length = 0
            
            # Ensure all rows have same length
            max_cols = max(len(r) for r in self.data) if self.data else 0
            while len(row) < max_cols:
                row.append(None)
                
            for x in range(len(row)):
                value = row[x] if row[x] is not None else ""
                
                # Apply line replacements
                for old, new in replacements:
                    value = value.replace(old, new)
                    
                # Check if escaping is needed
                escape = False
                if (line_chars_need_to_be_escaped_with_cell_delimiter and
                    any(c in value for c in line_chars_need_to_be_escaped_with_cell_delimiter)):
                    escape = True
                    
                # Add delimiters if escaping
                if cell_left_delimiter and escape:
                    line_parts.append(cell_left_delimiter)
                    line_length += len(cell_left_delimiter)
                    
                line_parts.append(value)
                line_length += len(value)
                
                if cell_right_delimiter and escape:
                    line_parts.append(cell_right_delimiter)
                    line_length += len(cell_right_delimiter)
                    
                # Add padding if requested
                if padding_to_max_cell_length:
                    max_length = self._get_max_cell_length(x)
                    padding = max_length - len(value)
                    if padding > 0:
                        line_parts.append(" " * padding)
                        line_length += padding
                        
                # Add column delimiter (except for last column)
                if x < len(row) - 1:
                    line_parts.append(column_delimiter)
                    line_length += len(column_delimiter)
                    
            max_line_length = max(max_line_length, line_length)
            result.append("".join(line_parts))
            
        # Add header delimiter if specified (after all header rows)
        if header_delimiter is not None:
            header_line = header_delimiter * max_line_length
            if max_line_length > 0:
                header_line = header_line[:max_line_length]
            # Insert after all header rows (like Java implementation)
            header_end_pos = min(self.header_size, len(result))
            result.insert(header_end_pos, header_line)
            
        return "\n".join(result) + "\n"
        
    def _get_max_cell_length(self, x: int) -> int:
        """Get maximum cell length for a column, considering both headers and data."""
        max_length = 0
        
        # Check all rows (including headers and data)
        for row in self.data:
            if x < len(row) and row[x] is not None:
                max_length = max(max_length, len(str(row[x])))
                
        return max_length

def process_element(matrix: Matrix, obj: Any, prefix: str, same_line: bool, depth: int):
    """Process a JSON element recursively - matching Java field ordering exactly."""
    x = 0
    if prefix:
        x = matrix.get_or_create_header(prefix)
        
    if isinstance(obj, dict):
        if depth > 1:
            matrix.child_header()
            
        # Special case: multiple arrays at the top level of a record
        # Example: {"filed": "name", "arrayField": [objects...], "numberArray": [1, 2, 3]}
        # Should be processed in parallel with row-based synchronization
        if depth == 1:
            # Check if we have multiple arrays of any type
            array_fields = []
            for key, value in obj.items():
                if isinstance(value, list) and len(value) > 0:
                    array_fields.append((key, value))
            
            if len(array_fields) > 1:
                # Process non-array fields first
                for key, value in obj.items():
                    if not isinstance(value, list):
                        new_key = f"{prefix}.{key}" if prefix else key
                        process_element(matrix, value, new_key, same_line, depth + 1)
                        same_line = True
                
                # Separate complex arrays from primitive arrays
                complex_arrays = []
                primitive_arrays = []
                for key, value in array_fields:
                    if len(value) > 0 and isinstance(value[0], (dict, list)):
                        complex_arrays.append((key, value))
                    else:
                        primitive_arrays.append((key, value))
                
                # If we have both complex and primitive arrays, need special handling
                if complex_arrays and primitive_arrays:
                    # Process complex arrays first and track how many rows each creates
                    primitive_value_index = 0
                    object_row_info = []  # Track (start_row, end_row) for each object
                    
                    # Find the main complex array (typically the first one)
                    main_complex_key, main_complex_array = complex_arrays[0]
                    
                    for complex_idx, complex_item in enumerate(main_complex_array):
                        # Remember current row position
                        start_row = matrix.current_row
                        
                        # Process the complex item
                        new_key = f"{prefix}.{main_complex_key}" if prefix else main_complex_key
                        array_same_line = same_line and (complex_idx == 0)
                        process_element(matrix, complex_item, new_key, array_same_line, depth + 1)
                        
                        # Calculate how many rows this complex item created
                        end_row = matrix.current_row
                        object_row_info.append((start_row, end_row))
                        same_line = False
                    
                    # Now distribute primitive array values across ALL created rows in sequence
                    for prim_key, prim_array in primitive_arrays:
                        value_index = 0
                        prim_header = f"{prefix}.{prim_key}" if prefix else prim_key
                        x = matrix.get_or_create_header(prim_header)
                        
                        # Go through each data row and assign the next primitive value
                        current_data_row = matrix.header_size
                        while value_index < len(prim_array):
                            # If we run out of existing rows, create new empty ones
                            if current_data_row >= len(matrix.data):
                                matrix.insert_row(len(matrix.data))
                            matrix.inject_at_row(x, current_data_row, str(prim_array[value_index]))
                            value_index += 1
                            current_data_row += 1
                else:
                    # Original logic for cases without mixed complex/primitive arrays
                    max_len = max(len(arr) for _, arr in array_fields)
                    for i in range(max_len):
                        array_same_line = same_line and (i == 0)
                        for key, value in obj.items():
                            if isinstance(value, list) and i < len(value):
                                new_key = f"{prefix}.{key}" if prefix else key
                                process_element(matrix, value[i], new_key, array_same_line, depth + 1)
                                array_same_line = True
                        same_line = False
                
                if depth > 1:
                    matrix.parent_header()
                return
        
        # Standard processing for all other cases
        for key, value in obj.items():
            new_key = f"{prefix}.{key}" if prefix else key
            process_element(matrix, value, new_key, same_line, depth + 1)
            same_line = True
            
        if depth > 1:
            matrix.parent_header()
            
    elif isinstance(obj, list):
        # For arrays, we need to handle them differently based on depth
        if depth == 0:
            # Top level arrays - process each item as a new row
            for i, item in enumerate(obj):
                matrix.new_line()
                process_element(matrix, item, prefix, False, depth + 1)
        else:
            # Nested arrays - process items inline
            for i, item in enumerate(obj):
                same_line = (i == 0)
                process_element(matrix, item, prefix, same_line, depth + 1)
            
    else:
        # Convert boolean to lowercase like Java does
        if isinstance(obj, bool):
            value = str(obj).lower()
        else:
            value = str(obj)
        matrix.inject(x, same_line, value)

def analyze_structure(data: Any, prefix: str = "") -> dict:
    """Analyze JSON structure to determine maximum width needed for each object path."""
    structure = {}
    all_leaf_paths = set()  # All leaf paths in the dataset
    path_leaf_paths = {}  # Leaf paths that belong to each object path
    
    def collect_leaf_paths(obj: Any, path: str):
        """Collect all leaf paths in the data."""
        if isinstance(obj, dict):
            for key, value in obj.items():
                child_path = f"{path}.{key}" if path else key
                if isinstance(value, (dict, list)):
                    collect_leaf_paths(value, child_path)
                else:
                    # This is a leaf field
                    all_leaf_paths.add(child_path)
        elif isinstance(obj, list):
            for item in obj:
                collect_leaf_paths(item, path)
    
    def map_leaf_paths_to_objects(obj: Any, path: str):
        """Map which leaf paths belong to which object paths."""
        if isinstance(obj, dict):
            if path:
                # Initialize if not exists
                if path not in path_leaf_paths:
                    path_leaf_paths[path] = set()
                
                # All leaves under this path belong to this object
                for leaf_path in all_leaf_paths:
                    if leaf_path.startswith(path + "."):
                        path_leaf_paths[path].add(leaf_path)
            
            # Recursively process children
            for key, value in obj.items():
                child_path = f"{path}.{key}" if path else key
                map_leaf_paths_to_objects(value, child_path)
                
        elif isinstance(obj, list):
            for item in obj:
                map_leaf_paths_to_objects(item, path)
    
    # First pass: collect all leaf paths from all data elements
    if isinstance(data, list):
        for item in data:
            collect_leaf_paths(item, prefix)
    else:
        collect_leaf_paths(data, prefix)
    
    # Second pass: map leaf paths to object paths (process all elements to ensure union)
    if isinstance(data, list):
        for item in data:
            map_leaf_paths_to_objects(item, prefix)
    else:
        map_leaf_paths_to_objects(data, prefix)
    
    # Calculate required width for each path
    for path, leaves in path_leaf_paths.items():
        structure[path] = len(leaves) if leaves else 1
    
    return structure

def json_to_csv(json_data: str, 
                column_delimiter: str = ",",
                cell_left_delimiter: Optional[str] = "\"",
                cell_right_delimiter: Optional[str] = "\"", 
                line_chars_need_to_be_escaped_with_cell_delimiter: Optional[str] = "\n\",",
                header_delimiter: Optional[str] = None,
                line_replacements: Optional[List[str]] = None,
                padding_to_max_cell_length: bool = False,
                remove_headers_duplicates: bool = True) -> str:
    """Convert JSON to CSV format."""
    
    # Only set default line replacements if None
    if line_replacements is None:
        line_replacements = ["\"==>\"\""]
        
    # Parse JSON
    data = json.loads(json_data)
    
    # Analyze structure to determine object widths (for Java compatibility)
    structure_info = analyze_structure(data)
    
    # Create matrix with structure info for intelligent column placement
    matrix = Matrix(structure_info)
    
    # Process data
    process_element(matrix, data, "", False, 0)
    
    # Remove header duplicates if requested
    if remove_headers_duplicates:
        matrix.remove_headers_duplicates()
        
    # Convert to string
    return matrix.to_string(
        column_delimiter=column_delimiter,
        cell_left_delimiter=cell_left_delimiter, 
        cell_right_delimiter=cell_right_delimiter,
        line_chars_need_to_be_escaped_with_cell_delimiter=line_chars_need_to_be_escaped_with_cell_delimiter,
        header_delimiter=header_delimiter,
        line_replacements=line_replacements,
        padding_to_max_cell_length=padding_to_max_cell_length
    )

def json_to_markdown(json_data: str) -> str:
    """Convert JSON to Markdown table format."""
    return json_to_csv(
        json_data,
        column_delimiter="|",
        cell_left_delimiter=None,
        cell_right_delimiter=None,
        line_chars_need_to_be_escaped_with_cell_delimiter=None,
        header_delimiter="-",
        line_replacements=[],  # Empty list to avoid replacements
        padding_to_max_cell_length=True,
        remove_headers_duplicates=True
    )

def read_json_file(file_path: str) -> str:
    """Read JSON data from file."""
    try:
        # Convert to absolute path and resolve any relative paths
        absolute_path = os.path.abspath(file_path)
        
        # Check if file exists
        if not os.path.exists(absolute_path):
            raise FileNotFoundError(f"Input file not found: {absolute_path}")
            
        # Check if it's a file (not directory)
        if not os.path.isfile(absolute_path):
            raise ValueError(f"Path is not a file: {absolute_path}")
            
        # Read file content
        with open(absolute_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Validate JSON
        try:
            json.loads(content)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in file {absolute_path}: {str(e)}")
            
        return content
        
    except Exception as e:
        raise Exception(f"Error reading JSON file '{file_path}': {str(e)}")

def write_output_file(file_path: str, content: str) -> str:
    """Write content to output file."""
    try:
        # Convert to absolute path
        absolute_path = os.path.abspath(file_path)
        
        # Create directory if it doesn't exist
        directory = os.path.dirname(absolute_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
            
        # Write content to file
        with open(absolute_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
        # Return absolute path for confirmation
        return absolute_path
        
    except Exception as e:
        raise Exception(f"Error writing output file '{file_path}': {str(e)}")

def get_file_size_info(file_path: str) -> dict:
    """Get file size information."""
    try:
        absolute_path = os.path.abspath(file_path)
        if os.path.exists(absolute_path):
            size_bytes = os.path.getsize(absolute_path)
            # Convert to human readable format
            if size_bytes < 1024:
                size_str = f"{size_bytes} bytes"
            elif size_bytes < 1024 * 1024:
                size_str = f"{size_bytes / 1024:.1f} KB"
            else:
                size_str = f"{size_bytes / (1024 * 1024):.1f} MB"
                
            return {
                "size_bytes": size_bytes,
                "size_formatted": size_str,
                "exists": True
            }
        else:
            return {"exists": False}
    except Exception:
        return {"exists": False}

async def run_tool(name: str, parameters: dict) -> list[types.Content]:
    """Convert JSON data to CSV or Markdown format in Text Mode or File Mode."""
    try:
        # Check which mode to use
        input_file_path = parameters.get("input_file_path")
        output_file_path = parameters.get("output_file_path") 
        json_data = parameters.get("json_data")
        
        # Determine mode
        file_mode = bool(input_file_path and output_file_path)
        text_mode = bool(json_data)
        
        if file_mode and text_mode:
            return [types.TextContent(type="text", text=json.dumps({
                "error": "Cannot use both Text Mode (json_data) and File Mode (input_file_path, output_file_path) parameters simultaneously. Choose one mode."
            }))]
            
        if not file_mode and not text_mode:
            return [types.TextContent(type="text", text=json.dumps({
                "error": "No input provided. Use Text Mode (json_data parameter) or File Mode (input_file_path and output_file_path parameters)."
            }))]
            
        # Get conversion parameters (same for both modes)
        format_type = parameters.get("format", "csv")
        column_delimiter = parameters.get("column_delimiter", ",")
        cell_left_delimiter = parameters.get("cell_left_delimiter", "\"")
        cell_right_delimiter = parameters.get("cell_right_delimiter", "\"")
        line_chars_need_to_be_escaped_with_cell_delimiter = parameters.get(
            "line_chars_need_to_be_escaped_with_cell_delimiter", "\n\","
        )
        header_delimiter = parameters.get("header_delimiter", None)
        line_replacements = parameters.get("line_replacements", ["\"==>\"\""])
        padding_to_max_cell_length = parameters.get("padding_to_max_cell_length", False)
        remove_headers_duplicates = parameters.get("remove_headers_duplicates", True)
        
        # FILE MODE
        if file_mode:
            try:
                # Read input file
                input_info = get_file_size_info(input_file_path)
                json_data = read_json_file(input_file_path)
                
                # Convert based on format
                if format_type == "markdown":
                    result = json_to_markdown(json_data)
                else:
                    result = json_to_csv(
                        json_data,
                        column_delimiter=column_delimiter,
                        cell_left_delimiter=cell_left_delimiter,
                        cell_right_delimiter=cell_right_delimiter,
                        line_chars_need_to_be_escaped_with_cell_delimiter=line_chars_need_to_be_escaped_with_cell_delimiter,
                        header_delimiter=header_delimiter,
                        line_replacements=line_replacements,
                        padding_to_max_cell_length=padding_to_max_cell_length,
                        remove_headers_duplicates=remove_headers_duplicates
                    )
                
                # Write output file
                actual_output_path = write_output_file(output_file_path, result)
                output_info = get_file_size_info(actual_output_path)
                
                # Return success message with file information
                response = {
                    "mode": "file",
                    "success": True,
                    "message": f"Successfully converted JSON to {format_type.upper()}",
                    "input_file": {
                        "path": os.path.abspath(input_file_path),
                        "size": input_info.get("size_formatted", "unknown")
                    },
                    "output_file": {
                        "path": actual_output_path,
                        "size": output_info.get("size_formatted", "unknown"),
                        "format": format_type
                    }
                }
                
                return [types.TextContent(type="text", text=json.dumps(response, indent=2))]
                
            except Exception as e:
                return [types.TextContent(type="text", text=json.dumps({
                    "mode": "file",
                    "success": False,
                    "error": str(e),
                    "input_file_path": input_file_path,
                    "output_file_path": output_file_path
                }))]
        
        # TEXT MODE
        else:
            # json_data should be already parsed JSON object/array
            if json_data is None:
                return [types.TextContent(type="text", text=json.dumps({"error": "json_data is required for text mode"}))]
            
            # Convert JSON object/array to string for internal processing
            json_data_str = json.dumps(json_data)
                
            # Convert based on format
            if format_type == "markdown":
                result = json_to_markdown(json_data_str)
            else:
                result = json_to_csv(
                    json_data_str,
                    column_delimiter=column_delimiter,
                    cell_left_delimiter=cell_left_delimiter,
                    cell_right_delimiter=cell_right_delimiter,
                    line_chars_need_to_be_escaped_with_cell_delimiter=line_chars_need_to_be_escaped_with_cell_delimiter,
                    header_delimiter=header_delimiter,
                    line_replacements=line_replacements,
                    padding_to_max_cell_length=padding_to_max_cell_length,
                    remove_headers_duplicates=remove_headers_duplicates
                )
                
            return [types.TextContent(type="text", text=result)]
        
    except Exception as e:
        return [types.TextContent(type="text", text=json.dumps({"error": str(e)}))]