import mcp.types as types
import json
import sys
import os
import re
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Union

# Excel and CSV libraries
import openpyxl
from openpyxl.utils import get_column_letter, column_index_from_string
from openpyxl.worksheet.worksheet import Worksheet
import pandas as pd

# Add the parent directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from mcp_server.pipeline.expressions import substitute_expressions, parse_substituted_string, build_default_context

async def tool_info() -> dict:
    """Returns information about the lng_xls_batch tool."""
    return {
        "name": "lng_xls_batch",
        "description": """🔄 Advanced Excel/CSV Batch Operations Tool

**🚀 Core Features:**
• **Multi-format Support** - Excel (.xlsx, .xls) and CSV files
• **Smart Copy Operations** - Values, formulas, formatting with flexible combinations
• **Expression System** - Dynamic ranges and values using {! expression !} syntax  
• **Batch Processing** - Multiple operations with automatic file saving
• **Flexible Insert Modes** - Replace or insert with row/column expansion
• **CSV Integration** - CSV files treated as single-sheet Excel internally

**⚡ Operation Modes:**
• `single` - Single copy operation (auto-detected)
• `batch` - Multiple operations with workspace management

**🎯 Copy Types:**
• `values` - Copy cell values only
• `formulas` - Copy formulas only
• `formatting` - Copy cell formatting only
• Combinations: `["values", "formulas"]`, `["values", "formatting"]`, etc.

**📁 Workspace Management:**
Define file aliases for easy reference:
```json
{
  "workspace": {
    "source": "input.xlsx",
    "target": "output.csv",
    "temp": "calculations.xlsx"
  }
}
```

**🔧 Insert Modes:**
• `"replace"` - Replace existing cells
• `["rows"]` - Insert new rows, shifting existing down
• `["columns"]` - Insert new columns, shifting existing right  
• `["rows", "columns"]` - Insert both rows and columns

**📝 Range Notation:**
• Excel files: `[fileId]SheetName!A1:C10`
• CSV files: `[fileId]A1:C10` (sheet name optional)
• Dynamic ranges: `[source]Sheet1!A1:A{! row_count !}`

**✨ Example Usage:**

**Simple Copy:**
```json
{
  "workspace": {
    "src": "data.xlsx",
    "dst": "report.xlsx"
  },
  "operations": [
    {
      "from": "[src]Sheet1!A1:C10",
      "to": "[dst]Summary!A1:C10",
      "copy": ["values", "formulas"],
      "insert": "replace"
    }
  ]
}
```

**Batch with Expressions:**
```json
{
  "workspace": {
    "input": "raw_data.csv", 
    "output": "processed.xlsx"
  },
  "defaults": {
    "copy": ["values"],
    "insert": "replace"
  },
  "operations": [
    {
      "from": "{! env.REPORT_TITLE !}",
      "to": "[output]Report!A1"
    },
    {
      "from": "=SUM(B:B)",
      "to": "[output]Report!B{! row_count + 2 !}",
      "copy": ["formulas"]
    }
  ]
}
```

**🔄 Processing Flow:**
1. Load workspace files (create if needed)
2. Process expressions in operations
3. Execute operations sequentially
4. Save files after each operation
5. Handle CSV ↔ Excel conversion automatically""",
        
        "schema": {
            "type": "object",
            "properties": {
                "workspace": {
                    "type": "object",
                    "description": "File workspace with aliases for easy reference",
                    "additionalProperties": {"type": "string"}
                },
                "defaults": {
                    "type": "object", 
                    "description": "Default settings for operations",
                    "properties": {
                        "copy": {
                            "type": "array",
                            "items": {"type": "string", "enum": ["values", "formulas", "formatting"]},
                            "default": ["values", "formulas"]
                        },
                        "insert": {
                            "oneOf": [
                                {"type": "string", "enum": ["replace"]},
                                {"type": "array", "items": {"type": "string", "enum": ["rows", "columns"]}}
                            ],
                            "default": "replace"
                        }
                    }
                },
                "operations": {
                    "type": "array",
                    "description": "List of copy operations to perform",
                    "items": {
                        "type": "object",
                        "properties": {
                            "from": {
                                "type": "string",
                                "description": "Source range, formula, or expression"
                            },
                            "to": {
                                "type": "string", 
                                "description": "Target range with file and sheet reference"
                            },
                            "copy": {
                                "type": "array",
                                "items": {"type": "string", "enum": ["values", "formulas", "formatting"]},
                                "description": "What to copy (overrides defaults)"
                            },
                            "insert": {
                                "oneOf": [
                                    {"type": "string", "enum": ["replace"]},
                                    {"type": "array", "items": {"type": "string", "enum": ["rows", "columns"]}}
                                ],
                                "description": "Insert mode (overrides defaults)"
                            }
                        },
                        "required": ["from", "to"]
                    }
                },
                "debug": {
                    "type": "boolean",
                    "default": False,
                    "description": "Enable debug logging"
                }
            },
            "required": ["workspace", "operations"]
        }
    }

async def run_tool(name: str, parameters: dict) -> list[types.Content]:
    """Run tool function for MCP server."""
    try:
        result = await main(parameters)
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
    except Exception as e:
        error_result = {"success": False, "error": str(e)}
        return [types.TextContent(type="text", text=json.dumps(error_result, indent=2))]

async def main(params: dict) -> dict:
    """Main function for lng_xls_batch tool."""
    try:
        # Set up logging
        logger = logging.getLogger(__name__)
        if params.get("debug", False):
            logger.setLevel(logging.DEBUG)
            
        # Build context for expressions
        context = build_default_context()
        
        # Extract parameters
        workspace = params.get("workspace", {})
        defaults = params.get("defaults", {
            "copy": ["values", "formulas"],
            "insert": "replace"
        })
        operations = params.get("operations", [])
        
        if not operations:
            return {
                "success": False,
                "error": "No operations specified"
            }
            
        # Validate workspace
        if not workspace:
            return {
                "success": False, 
                "error": "Workspace configuration is required"
            }
            
        # Initialize file handlers
        file_handlers = {}
        
        # Process operations
        results = []
        for i, operation in enumerate(operations):
            try:
                logger.info(f"Processing operation {i+1}/{len(operations)}")
                
                # Process expressions in operation
                processed_op = process_expressions(operation, context)
                
                # Execute operation
                result = await execute_operation(
                    processed_op, workspace, defaults, file_handlers, logger
                )
                
                results.append({
                    "operation": i + 1,
                    "success": True,
                    "result": result
                })
                
            except Exception as e:
                error_msg = f"Operation {i+1} failed: {str(e)}"
                logger.error(error_msg)
                return {
                    "success": False,
                    "error": error_msg,
                    "operation": i + 1,
                    "completed_operations": results
                }
        
        # Final save of all files
        save_results = save_all_files(file_handlers, logger)
        
        return {
            "success": True,
            "operations_completed": len(results),
            "results": results,
            "files_saved": save_results
        }
        
    except Exception as e:
        logger.error(f"Tool execution failed: {str(e)}")
        return {
            "success": False,
            "error": f"Tool execution failed: {str(e)}"
        }

def process_expressions(operation: dict, context: dict) -> dict:
    """Process expressions in operation parameters."""
    processed = {}
    
    for key, value in operation.items():
        if isinstance(value, str):
            # Process expressions in string values
            processed[key] = substitute_expressions(value, context)
        else:
            processed[key] = value
            
    return processed

async def execute_operation(operation: dict, workspace: dict, defaults: dict, 
                          file_handlers: dict, logger: logging.Logger) -> dict:
    """Execute a single copy operation."""
    
    from_source = operation["from"]
    to_target = operation["to"] 
    copy_types = operation.get("copy", defaults.get("copy", ["values", "formulas"]))
    insert_mode = operation.get("insert", defaults.get("insert", "replace"))
    
    logger.debug(f"Executing operation: {from_source} => {to_target}")
    
    # Parse source and target
    source_info = parse_range(from_source, workspace)
    target_info = parse_range(to_target, workspace)
    
    # Validate target must be a range (file reference)
    if target_info["type"] != "range":
        raise ValueError(f"Target must be a file range, got: {to_target}")
    
    # Load source and target files
    if source_info["type"] == "range":
        source_wb = load_workbook(source_info["file"], file_handlers)
        source_ws = get_worksheet(source_wb, source_info.get("sheet"))
    else:
        source_wb = None
        source_ws = None
    
    target_wb = load_workbook(target_info["file"], file_handlers)
    target_ws = get_worksheet(target_wb, target_info.get("sheet"), create=True)
    
    # Execute copy operation based on source type
    if source_info["type"] == "range":
        # Copy range
        result = copy_range(
            source_ws, source_info["range"],
            target_ws, target_info["range"], 
            copy_types, insert_mode, logger
        )
    elif source_info["type"] == "formula":
        # Copy formula
        result = copy_formula(
            source_info["formula"],
            target_ws, target_info["range"],
            copy_types, insert_mode, logger
        )
    elif source_info["type"] == "value":
        # Copy value
        result = copy_value(
            source_info["value"],
            target_ws, target_info["range"],
            copy_types, insert_mode, logger
        )
    else:
        raise ValueError(f"Unknown source type: {source_info['type']}")
    
    # Save files after operation
    if source_wb:
        save_workbook(source_info["file"], source_wb, file_handlers)
    save_workbook(target_info["file"], target_wb, file_handlers) 
    
    return result

def parse_range(range_str: str, workspace: dict) -> dict:
    """Parse range string into components."""
    # Handle different source types
    if range_str.startswith("="):
        # Formula
        return {
            "type": "formula",
            "formula": range_str
        }
    elif range_str.startswith("{!") and range_str.endswith("!}"):
        # Expression value  
        return {
            "type": "value",
            "value": range_str
        }
    elif "[" in range_str and "]" in range_str:
        # File reference with range
        # Pattern: [fileId]Sheet!Range or [fileId]Range
        match = re.match(r'\[(\w+)\](.+)', range_str)
        if not match:
            raise ValueError(f"Invalid range format: {range_str}")
            
        file_id = match.group(1)
        rest = match.group(2)
        
        if file_id not in workspace:
            raise ValueError(f"File ID '{file_id}' not found in workspace")
            
        file_path = workspace[file_id]
        
        # Check if it has sheet name
        if "!" in rest:
            sheet_name, range_part = rest.split("!", 1)
            return {
                "type": "range",
                "file": file_path,
                "sheet": sheet_name,
                "range": range_part
            }
        else:
            # No sheet name (CSV case)
            return {
                "type": "range", 
                "file": file_path,
                "sheet": None,
                "range": rest
            }
    else:
        # Simple value (fallback)
        return {
            "type": "value",
            "value": range_str
        }

def load_workbook(file_path: str, file_handlers: dict):
    """Load workbook from file or cache."""
    if file_path in file_handlers:
        return file_handlers[file_path]
    
    path = Path(file_path)
    
    if path.suffix.lower() == '.csv':
        # Load CSV as Excel
        wb = load_csv_as_excel(file_path)
    elif path.exists():
        # Load existing Excel file
        wb = openpyxl.load_workbook(file_path)
    else:
        # Create new Excel file
        wb = openpyxl.Workbook()
        
    file_handlers[file_path] = wb
    return wb

def load_csv_as_excel(csv_path: str):
    """Load CSV file as Excel workbook."""
    # Read CSV with pandas
    df = pd.read_csv(csv_path)
    
    # Create Excel workbook
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Sheet1"
    
    # Write data to Excel
    for r_idx, row in enumerate(df.itertuples(index=False), 1):
        for c_idx, value in enumerate(row, 1):
            ws.cell(row=r_idx + 1, column=c_idx, value=value)  # +1 for header
    
    # Write headers
    for c_idx, col_name in enumerate(df.columns, 1):
        ws.cell(row=1, column=c_idx, value=col_name)
    
    return wb

def get_worksheet(wb, sheet_name: Optional[str], create: bool = False):
    """Get worksheet from workbook."""
    if sheet_name is None:
        # Return active sheet (CSV case)
        return wb.active
    
    if sheet_name in wb.sheetnames:
        return wb[sheet_name]
    elif create:
        # Create new sheet
        if sheet_name in wb.sheetnames:
            return wb[sheet_name]
        else:
            return wb.create_sheet(sheet_name)
    else:
        # For new workbooks, first sheet might not be named "Sheet1"
        if len(wb.sheetnames) == 1 and sheet_name == "Sheet1":
            # Rename the active sheet to the requested name
            wb.active.title = sheet_name
            return wb.active
        raise ValueError(f"Sheet '{sheet_name}' not found")

def copy_range(source_ws: Worksheet, source_range: str, 
              target_ws: Worksheet, target_range: str,
              copy_types: List[str], insert_mode, logger: logging.Logger) -> dict:
    """Copy range between worksheets."""
    # Parse ranges
    source_cells = source_ws[source_range]
    
    # Handle insert mode
    if insert_mode != "replace":
        handle_insert_mode(target_ws, target_range, insert_mode, source_cells)
    
    target_cells = target_ws[target_range]
    
    # Ensure dimensions match for replace mode
    if insert_mode == "replace":
        if not check_dimensions_match(source_cells, target_cells):
            raise ValueError("Source and target range dimensions don't match for replace mode")
    
    # Copy data based on copy types
    copied_count = 0
    
    if isinstance(source_cells[0], tuple):
        # Multiple rows
        for src_row, tgt_row in zip(source_cells, target_cells):
            if isinstance(src_row, tuple):
                for src_cell, tgt_cell in zip(src_row, tgt_row):
                    copy_cell(src_cell, tgt_cell, copy_types)
                    copied_count += 1
            else:
                copy_cell(src_row, tgt_row, copy_types)
                copied_count += 1
    else:
        # Single row or cell
        if isinstance(source_cells, tuple):
            for src_cell, tgt_cell in zip(source_cells, target_cells):
                copy_cell(src_cell, tgt_cell, copy_types)
                copied_count += 1
        else:
            copy_cell(source_cells, target_cells, copy_types)
            copied_count += 1
    
    logger.info(f"Copied {copied_count} cells")
    return {"copied_cells": copied_count, "copy_types": copy_types}

def copy_formula(formula: str, target_ws: Worksheet, target_range: str,
                copy_types: List[str], insert_mode, logger: logging.Logger) -> dict:
    """Copy formula to target range."""
    if "formulas" not in copy_types:
        raise ValueError("Formula source requires 'formulas' in copy types")
    
    target_cells = target_ws[target_range]
    
    # Handle single cell vs range
    if hasattr(target_cells, 'coordinate'):
        # Single cell
        target_cells.value = formula
        count = 1
    else:
        # Multiple cells - set formula to first cell
        if isinstance(target_cells[0], tuple):
            target_cells[0][0].value = formula
        else:
            target_cells[0].value = formula
        count = 1
    
    logger.info(f"Set formula '{formula}' to {count} cell(s)")
    return {"formula_set": count, "formula": formula}

def copy_value(value: str, target_ws: Worksheet, target_range: str,
              copy_types: List[str], insert_mode, logger: logging.Logger) -> dict:
    """Copy value to target range."""
    if "values" not in copy_types:
        raise ValueError("Value source requires 'values' in copy types")
    
    target_cells = target_ws[target_range]
    
    # Handle single cell vs range  
    if hasattr(target_cells, 'coordinate'):
        # Single cell
        target_cells.value = value
        count = 1
    else:
        # Multiple cells - set value to all cells
        count = 0
        if isinstance(target_cells[0], tuple):
            for row in target_cells:
                for cell in row:
                    cell.value = value
                    count += 1
        else:
            for cell in target_cells:
                cell.value = value
                count += 1
    
    logger.info(f"Set value '{value}' to {count} cell(s)")
    return {"values_set": count, "value": value}

def copy_cell(source_cell, target_cell, copy_types: List[str]):
    """Copy cell content based on copy types."""
    if "values" in copy_types:
        target_cell.value = source_cell.value
    
    if "formulas" in copy_types:
        # In openpyxl, formulas are stored in value, but we can check if it starts with =
        if source_cell.value and isinstance(source_cell.value, str) and source_cell.value.startswith('='):
            target_cell.value = source_cell.value
        elif "values" not in copy_types:
            # Only copy formula if values weren't already copied
            target_cell.value = source_cell.value
        
    if "formatting" in copy_types:
        # Copy formatting
        if source_cell.font:
            target_cell.font = source_cell.font
        if source_cell.border:
            target_cell.border = source_cell.border
        if source_cell.fill:
            target_cell.fill = source_cell.fill
        if source_cell.number_format:
            target_cell.number_format = source_cell.number_format
        if source_cell.alignment:
            target_cell.alignment = source_cell.alignment

def handle_insert_mode(ws: Worksheet, target_range: str, insert_mode, source_cells):
    """Handle insert mode by inserting rows/columns."""
    # Parse target range to get starting position
    range_obj = ws[target_range] 
    
    if hasattr(range_obj, 'coordinate'):
        start_row, start_col = range_obj.row, range_obj.column
    else:
        start_row = range_obj[0][0].row if isinstance(range_obj[0], tuple) else range_obj[0].row
        start_col = range_obj[0][0].column if isinstance(range_obj[0], tuple) else range_obj[0].column
    
    # Calculate dimensions needed
    if isinstance(source_cells[0], tuple):
        rows_needed = len(source_cells)
        cols_needed = len(source_cells[0])
    else:
        rows_needed = len(source_cells) if isinstance(source_cells, tuple) else 1
        cols_needed = 1
    
    # Insert rows if needed
    if "rows" in insert_mode:
        ws.insert_rows(start_row, rows_needed)
    
    # Insert columns if needed  
    if "columns" in insert_mode:
        ws.insert_cols(start_col, cols_needed)

def check_dimensions_match(source_cells, target_cells) -> bool:
    """Check if source and target cell ranges have matching dimensions."""
    # Get dimensions of source
    if isinstance(source_cells[0], tuple):
        src_rows, src_cols = len(source_cells), len(source_cells[0])
    else:
        src_rows = len(source_cells) if isinstance(source_cells, tuple) else 1
        src_cols = 1
    
    # Get dimensions of target
    if isinstance(target_cells[0], tuple):
        tgt_rows, tgt_cols = len(target_cells), len(target_cells[0])
    else:
        tgt_rows = len(target_cells) if isinstance(target_cells, tuple) else 1
        tgt_cols = 1
        
    return src_rows == tgt_rows and src_cols == tgt_cols

def save_workbook(file_path: str, wb, file_handlers: dict):
    """Save workbook to file."""
    path = Path(file_path)
    
    if path.suffix.lower() == '.csv':
        # Save as CSV
        save_excel_as_csv(wb, file_path)
    else:
        # Save as Excel
        wb.save(file_path)

def save_excel_as_csv(wb, csv_path: str):
    """Save Excel workbook as CSV (first sheet only)."""
    ws = wb.active
    
    # Convert to pandas DataFrame
    data = []
    for row in ws.iter_rows(values_only=True):
        data.append(row)
    
    if data:
        df = pd.DataFrame(data[1:], columns=data[0])  # First row as headers
        df.to_csv(csv_path, index=False)

def save_all_files(file_handlers: dict, logger: logging.Logger) -> dict:
    """Save all loaded files."""
    saved_files = []
    
    for file_path, wb in file_handlers.items():
        try:
            save_workbook(file_path, wb, file_handlers)
            saved_files.append(file_path)
            logger.info(f"Saved file: {file_path}")
        except Exception as e:
            logger.error(f"Failed to save {file_path}: {str(e)}")
            
    return {"saved_files": saved_files}
