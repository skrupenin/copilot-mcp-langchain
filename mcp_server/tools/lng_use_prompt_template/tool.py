import mcp.types as types
from langchain_openai import OpenAI
from langchain.prompts import PromptTemplate
from mcp_server.config import OPENAI_API_KEY
from mcp_server.tools.lng_save_prompt_template.tool import saved_prompt_template

async def tool_info() -> dict:
    """Returns information about the lng_save_prompt_template tool."""
    return {
        "name": "lng_use_prompt_template",
        "description": """Uses the previously saved prompt template with provided parameters.

**Parameters:**
- Any key-value pairs that match the placeholders in your template

**Example Usage:**
- If your saved template contains {topic} and {style} placeholders
- You would provide values like "topic: artificial intelligence" and "style: a pirate"
- The system will replace the placeholders with these values and process the completed prompt

This tool works with lng_save_prompt_template to create a flexible prompt engineering system.""",
        "schema": {
            "type": "object",
            "additionalProperties": {
                "type": "string"
            },
            "description": "Key-value pairs to use as parameters in the prompt template",
        }
    }

async def run_tool(name: str, parameters: dict) -> list[types.Content]:
    """Uses the previously saved prompt template with provided parameters."""
    
    if saved_prompt_template is None:
        return [types.TextContent(type="text", text="No prompt template has been saved. Please save a template first.")]
    
    try:
        # Extract input variables from the parameters
        input_variables = list(parameters.keys())
        
        # Create prompt template with the input variables
        prompt_template = PromptTemplate(
            input_variables=input_variables,
            template=saved_prompt_template
        )
        
        # Format the prompt with the provided parameters
        prompt = prompt_template.format(**parameters)
        
        # Initialize LLM and get response
        llm = OpenAI(openai_api_key=OPENAI_API_KEY)
        response = llm.invoke(prompt)
        
        return [types.TextContent(type="text", text=response)]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Error using prompt template: {str(e)}")]
