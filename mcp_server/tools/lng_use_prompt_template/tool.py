import mcp.types as types
from langchain.prompts import PromptTemplate
from mcp_server.state_manager import state_manager
from mcp_server.llm import llm

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
    
    saved_template = state_manager.get("prompt_template")
    if saved_template is None:
        return [types.TextContent(type="text", text="No prompt template has been saved. Please save a template first.")]
    
    try:
        # Extract input variables from the parameters
        input_variables = list(parameters.keys())
        
        # Create prompt template with the input variables
        prompt_template = PromptTemplate(
            input_variables=input_variables,
            template=saved_template
        )
        
        # Format the prompt with the provided parameters
        prompt = prompt_template.format(**parameters)
        
        # Initialize LLM and get response
        response = llm().invoke(prompt)

        # Check if the response has content and convert it to string
        if hasattr(response, "content"):
            response_text = response.content
        else:
            response_text = str(response)
        
        return [types.TextContent(type="text", text=response_text)]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Error using prompt template: {str(e)}")]
