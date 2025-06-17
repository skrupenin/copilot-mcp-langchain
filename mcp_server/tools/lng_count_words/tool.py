import mcp.types as types

async def tool_info() -> dict:
    """Returns information about the lng_count_words tool."""
    return {
        "name": "lng_count_words",
        "description": """Counts the number of words in the provided text.

**Parameters:**
- `text` (string, required): The text to count words in.

**Example Usage:**
- Provide any text input to count the words.
- The system will return the total word count and additional statistics.

This tool is useful for text analysis, helping to understand the length and complexity of a given text.""",
        "schema": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "The text to count words in"
                }
            },
            "required": ["text"]
        }
    }

async def run_tool(name: str, parameters: dict) -> list[types.Content]:
    """Counts the number of words in the provided text."""
    
    try:
        # Extract the text parameter
        text = parameters.get("text", "")
        
        if not text:
            return [types.TextContent(type="text", text='{"error": "No text provided to count words."}')]
        
        # Count words
        words = text.split()
        word_count = len(words)
        
        # Count characters
        char_count = len(text)
        char_count_no_spaces = len(text.replace(" ", ""))
        
        # Calculate additional statistics
        unique_words = len(set(word.lower() for word in words))
        avg_word_length = sum(len(word) for word in words) / word_count if word_count > 0 else 0
        
        # Create JSON result
        import json
        result_dict = {
            "wordCount": word_count,
            "uniqueWords": unique_words,
            "charactersWithSpaces": char_count,
            "charactersWithoutSpaces": char_count_no_spaces,
            "averageWordLength": round(avg_word_length, 2)
        }
        
        # Convert to JSON string
        result = json.dumps(result_dict, indent=2)
        
        return [types.TextContent(type="text", text=result)]
    except Exception as e:
        return [types.TextContent(type="text", text=json.dumps({"error": str(e)}))]
