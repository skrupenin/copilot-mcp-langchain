import mcp.types as types
import json
import logging
from langchain.agents import initialize_agent, AgentType
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.callbacks.base import BaseCallbackHandler
from langchain.chains import LLMChain
from langchain.tools import BaseTool
from langchain.prompts import PromptTemplate
from mcp_server.llm import llm

# Initialize logger for agent demo
logger = logging.getLogger('mcp_server.tools.lng_agent_demo')

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
        
        # Create a callback_manager with both console output and logging
        callback_manager = CallbackManager([
            StreamingStdOutCallbackHandler(),  # Console output
            AgentLoggingCallbackHandler()      # Log file output
        ])

        # Create LLM with our callback_manager         
        model = llm(callbacks=callback_manager, verbose=True)
        
        logger.info(f"Starting agent demo with text: '{text}' and task: '{task}'")
        
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

class AgentLoggingCallbackHandler(BaseCallbackHandler):
    """Custom callback handler that logs all agent actions to the log file with readable formatting."""
    
    def _log_separator(self, title=""):
        """Add a visual separator in logs for better readability."""
        separator = "=" * 60
        if title:
            logger.info(f"{separator} {title} {separator}")
        else:
            logger.info(separator)
    
    def _format_dict(self, data, indent=2):
        """Format dictionary data for readable logging."""
        if isinstance(data, dict):
            formatted_lines = []
            for key, value in data.items():
                if isinstance(value, (dict, list)) and len(str(value)) > 100:
                    formatted_lines.append(f"{' ' * indent}{key}:")
                    if isinstance(value, dict):
                        for sub_key, sub_value in value.items():
                            formatted_lines.append(f"{' ' * (indent + 2)}{sub_key}: {sub_value}")
                    elif isinstance(value, list):
                        for i, item in enumerate(value):
                            formatted_lines.append(f"{' ' * (indent + 2)}[{i}]: {item}")
                else:
                    formatted_lines.append(f"{' ' * indent}{key}: {value}")
            return "\n".join(formatted_lines)
        return str(data)
    
    def on_agent_action(self, action, **kwargs):
        """Called when agent takes an action."""
        self._log_separator("AGENT ACTION")
        logger.info(f"🔧 Tool Selected: {action.tool}")
        logger.info(f"📝 Tool Input: {action.tool_input}")
        if hasattr(action, 'log') and action.log:
            logger.info(f"🤔 Agent Reasoning:")
            # Split multi-line reasoning into separate log entries for readability
            for line in str(action.log).split('\n'):
                if line.strip():
                    logger.info(f"    {line.strip()}")
    
    def on_agent_finish(self, finish, **kwargs):
        """Called when agent finishes."""
        self._log_separator("AGENT FINISH")
        logger.info(f"✅ Final Output:")
        logger.info(self._format_dict(finish.return_values))
        if hasattr(finish, 'log') and finish.log:
            logger.info(f"📋 Final Agent Log:")
            for line in str(finish.log).split('\n'):
                if line.strip():
                    logger.info(f"    {line.strip()}")
    
    def on_tool_start(self, serialized, input_str, **kwargs):
        """Called when tool starts."""
        tool_name = serialized.get("name", "Unknown")
        logger.info(f"🚀 TOOL START: {tool_name}")
        logger.info(f"📨 Input: {input_str}")
    
    def on_tool_end(self, output, **kwargs):
        """Called when tool ends."""
        logger.info(f"✅ TOOL END - Output: {output}")
    
    def on_tool_error(self, error, **kwargs):
        """Called when tool encounters error."""
        logger.error(f"❌ TOOL ERROR: {error}")
    
    def on_llm_start(self, serialized, prompts, **kwargs):
        """Called when LLM starts."""
        logger.info(f"🤖 LLM START - Processing {len(prompts)} prompt(s)")
        for i, prompt in enumerate(prompts):
            logger.info(f"📤 LLM PROMPT [{i}]:")
            # Format multi-line prompts
            for line in str(prompt).split('\n'):
                if line.strip():
                    logger.info(f"    {line.strip()}")
    
    def on_llm_end(self, response, **kwargs):
        """Called when LLM ends."""
        logger.info(f"📥 LLM END - Response received")
        
        # Extract meaningful information from the response
        if hasattr(response, 'generations') and response.generations:
            for i, generation_list in enumerate(response.generations):
                for j, generation in enumerate(generation_list):
                    if hasattr(generation, 'text'):
                        logger.info(f"💬 Response Text [{i}.{j}]:")
                        for line in generation.text.split('\n'):
                            if line.strip():
                                logger.info(f"    {line.strip()}")
                    
                    # Log token usage if available
                    if hasattr(generation, 'generation_info') and generation.generation_info:
                        info = generation.generation_info
                        if 'finish_reason' in info:
                            logger.info(f"🏁 Finish Reason: {info['finish_reason']}")
        
        # Log token usage from llm_output if available
        if hasattr(response, 'llm_output') and response.llm_output and 'token_usage' in response.llm_output:
            usage = response.llm_output['token_usage']
            logger.info(f"📊 Token Usage: {usage.get('total_tokens', 'N/A')} total "
                       f"({usage.get('prompt_tokens', 'N/A')} prompt + {usage.get('completion_tokens', 'N/A')} completion)")
    
    def on_llm_error(self, error, **kwargs):
        """Called when LLM encounters error."""
        logger.error(f"❌ LLM ERROR: {error}")
    
    def on_chain_start(self, serialized, inputs, **kwargs):
        """Called when chain starts."""
        chain_name = serialized.get("name", "Unknown")
        logger.info(f"🔗 CHAIN START: {chain_name}")
        logger.info(f"📨 Inputs: {self._format_dict(inputs)}")
    
    def on_chain_end(self, outputs, **kwargs):
        """Called when chain ends."""
        logger.info(f"🔗 CHAIN END")
        logger.info(f"📤 Outputs: {self._format_dict(outputs)}")
    
    def on_chain_error(self, error, **kwargs):
        """Called when chain encounters error."""
        logger.error(f"❌ CHAIN ERROR: {error}")
    
    def on_text(self, text, **kwargs):
        """Called on any text."""
        if text.strip():
            logger.info(f"💭 AGENT TEXT: {text.strip()}")