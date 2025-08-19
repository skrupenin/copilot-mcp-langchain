"""
Text uppercase conversion tool.
Converts any input text to uppercase format.
"""

import json
import mcp.types as types
from typing import Dict, Any


def convert_to_uppercase(input_text: str) -> Dict[str, Any]:
    """
    Convert input text to uppercase.
    
    Args:
        input_text: The text to convert to uppercase
        
    Returns:
        Dictionary with conversion result and metadata
    """
    if not isinstance(input_text, str):
        return {
            "success": False,
            "error": "Input must be a string",
            "input_text": str(input_text),
            "output_text": None
        }
    
    try:
        # Convert to uppercase
        uppercase_text = input_text.upper()
        
        return {
            "success": True,
            "error": None,
            "input_text": input_text,
            "output_text": uppercase_text,
            "character_count": len(input_text),
            "uppercase_character_count": len(uppercase_text)
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "input_text": input_text,
            "output_text": None
        }


async def tool_info() -> dict:
    """Returns information about the lng_text_uppercase tool."""
    return {
        "description": """Converts any input text to uppercase format with detailed metadata.

**Parameters:**
- `input_text` (string, required): The text to convert to uppercase

**Example Usage:**
- Convert text to uppercase: input_text="Hello World"
- Convert Cyrillic text: input_text="мама мыла раму"  
- Handle special characters: input_text="Hello, World! 123"

This tool is useful for text processing and formatting operations.""",
        "schema": {
            "type": "object",
            "properties": {
                "input_text": {
                    "type": "string",
                    "description": "The text to convert to uppercase"
                }
            },
            "required": ["input_text"]
        }
    }


async def run_tool(name: str, parameters: dict) -> list[types.Content]:
    """Converts the provided text to uppercase."""
    try:
        # Extract the input_text parameter
        input_text = parameters.get("input_text", "")
        
        if not input_text:
            return [types.TextContent(type="text", text='{"error": "No text provided for uppercase conversion."}')]
        
        # Convert to uppercase using our function
        result = convert_to_uppercase(input_text)
        
        # Convert to JSON string
        result_json = json.dumps(result, ensure_ascii=False, indent=2)
        
        return [types.TextContent(type="text", text=result_json)]
    except Exception as e:
        error_result = {"error": str(e), "success": False}
        return [types.TextContent(type="text", text=json.dumps(error_result))]
