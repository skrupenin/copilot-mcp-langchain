import mcp.types as types
import json
from langchain.agents import initialize_agent, AgentType
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.chains import LLMChain
from langchain.tools import BaseTool
from langchain.prompts import PromptTemplate
from mcp_server.llm import llm 

async def tool_info() -> dict:
    """Returns information about the lng_agent_demo tool."""
    return {
        "name": "lng_agent_demo",
        "description": """Demonstrates a LangChain agent that can process text using three different tools:
        
**Parameters:**
- `input_text` (string, required): The text to process.
- `task` (string, required): The task description for the agent.

**Available Agent Tools:**
1. `reverse_text_tool`: Reverses the order of characters in a text.
2. `capitalize_words_tool`: Capitalizes the first letter of each word in a text.
3. `count_characters_tool`: Counts the number of characters in a text.

**Example Usage:**
- Provide input_text: "hello world"
- Provide task: "Capitalize this text and then count its characters"

The agent will decide which tools to use based on the task description.""",
        "schema": {
            "type": "object",
            "properties": {
                "input_text": {
                    "type": "string",
                    "description": "The text to process with the agent"
                },
                "task": {
                    "type": "string",
                    "description": "The task description for the agent"
                }
            },
            "required": ["input_text", "task"]
        }
    }

# Define our three string processing tools as functions
def reverse_text(text):
    """Reverses the input text."""
    return text[::-1]

def capitalize_words(text):
    """Capitalizes the first letter of each word in the text."""
    return ' '.join(word.capitalize() for word in text.split())

def count_characters(text):
    """Counts the number of characters in the text, including spaces."""
    char_count = len(text)
    char_count_no_spaces = len(text.replace(" ", ""))
    return {
        "total_characters": char_count,
        "characters_without_spaces": char_count_no_spaces
    }

# Wrap these functions as LangChain tools
class ReverseTextTool(BaseTool):
    name: str = "reverse_text_tool"
    description: str = "Useful when you need to reverse the order of characters in a text."
    
    def _run(self, text: str) -> str:
        return reverse_text(text)
    
    async def _arun(self, text: str) -> str:
        return reverse_text(text)

class CapitalizeWordsTool(BaseTool):
    name: str = "capitalize_words_tool"
    description: str = "Useful when you need to capitalize the first letter of each word in a text."
    
    def _run(self, text: str) -> str:
        return capitalize_words(text)
    
    async def _arun(self, text: str) -> str:
        return capitalize_words(text)

class CountCharactersTool(BaseTool):
    name: str = "count_characters_tool"
    description: str = "Useful when you need to count the number of characters in a text."
    
    def _run(self, text: str) -> str:
        result = count_characters(text)
        return json.dumps(result)
    
    async def _arun(self, text: str) -> str:
        result = count_characters(text)
        return json.dumps(result)

async def run_tool(name: str, parameters: dict) -> list[types.Content]:
    """Runs the LangChain agent demo with the specified parameters."""
    
    try:
        # Extract parameters
        text = parameters.get("input_text", "")
        task = parameters.get("task", "")
        
        if not text:
            return [types.TextContent(type="text", text='{"error": "No text provided to process."}')]
        if not task:
            return [types.TextContent(type="text", text='{"error": "No task provided for the agent."}')]        # Initialize the tools
        tools = [
            ReverseTextTool(),
            CapitalizeWordsTool(),
            CountCharactersTool()
        ]
        
        # Create a callback_manager for console output
        callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])

        # Create LLM with our callback_manager         
        model = llm(callbacks=callback_manager, verbose=True)
        
        # Create the agent with our LLM
        agent = initialize_agent(
            tools=tools,
            llm=model,
            agent=AgentType.CHAT_ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True
        )
        
        # Create the system prompt
        system_prompt = """You are a helpful text processing assistant. 
You have access to the following tools to help process text:
1. reverse_text_tool: Reverses the order of characters in a text.
2. capitalize_words_tool: Capitalizes the first letter of each word in a text.
3. count_characters_tool: Counts the number of characters in a text.

Use these tools to complete the user's request regarding text processing.
Be precise and efficient in your use of tools.
Explain your thought process and each step you take."""
        
        # Run the agent
        agent_input = {
            "input": f"I have the following text: '{text}'. My task is to: {task}",
            "agent_scratchpad": "",
            "chat_history": []
        }
        
        result = agent.invoke(agent_input)
        
        # Extract the output
        agent_output = result.get("output", "The agent did not provide a clear output.")
        
        # Create a structured response
        response = {
            "original_text": text,
            "task": task,
            "agent_output": agent_output
        }
        
        return [types.TextContent(type="text", text=json.dumps(response, indent=2))]
    except Exception as e:
        return [types.TextContent(type="text", text=json.dumps({"error": str(e)}))]
