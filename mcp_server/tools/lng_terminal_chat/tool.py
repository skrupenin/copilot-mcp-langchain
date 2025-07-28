import mcp.types as types
from langchain.prompts import PromptTemplate
from mcp_server.llm import llm

async def tool_info() -> dict:
    """Returns information about the lng_terminal_chat tool."""
    return {
        "description": """Terminal chat with LLM - analyzes command output and answers questions.

**Parameters:**
- command (required): The command that was executed
- command_output (required): The output of the executed command  
- question (required): The question about the command output

**Example Usage:**
- command: "docker ps -a"
- command_output: "CONTAINER ID   IMAGE     COMMAND   CREATED   STATUS..."
- question: "How many containers are running?"

This tool analyzes the command output using LLM and provides intelligent answers.""",
        "schema": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "The command that was executed"
                },
                "command_output": {
                    "type": "string", 
                    "description": "The output of the executed command"
                },
                "question": {
                    "type": "string",
                    "description": "The question about the command output"
                }
            },
            "required": ["command", "command_output", "question"]
        }
    }

async def run_tool(name: str, parameters: dict) -> list[types.Content]:
    """Execute the terminal chat tool."""
    try:
        command = parameters.get("command", "")
        command_output = parameters.get("command_output", "")
        question = parameters.get("question", "")
        
        if not command or not command_output or not question:
            return [types.TextContent(type="text", text="Error: All parameters (command, command_output, question) are required")]
        
        # Check if this is a simple question mode (no real command executed)
        if command == "echo 'Simple question mode'":
            # For simple questions, use a different template
            prompt_template = PromptTemplate(
                input_variables=["question"],
                template="""Please answer the following question: {question}

Important: When suggesting commands in your response, format them with > prefix (like "> ls -la") instead of using ```bash code blocks. Do not use markdown code blocks (```) in your response."""
            )
            
            formatted_prompt = prompt_template.format(question=question)
        else:
            # Create the prompt template based on scenario.txt for command analysis
            prompt_template = PromptTemplate(
                input_variables=["command", "log", "question"],
                template="""Imagine you have the following bash command:
\"\"\"{command}\"\"\"

With the following output log:
\"\"\"{log}\"\"\"

Based on this output log, please answer this question:
\"\"\"{question}\"\"\"

Important: When suggesting commands in your response, format them with > prefix (like "> ls -la") instead of using ```bash code blocks. Do not use markdown code blocks (```) in your response."""
            )
            
            # Format the prompt with the provided parameters
            formatted_prompt = prompt_template.format(
                command=command,
                log=command_output,
                question=question
            )
        
        # Get response from LLM
        model = llm()
        response = model.invoke(formatted_prompt)
        
        # Extract content from response if it's an AIMessage object
        if hasattr(response, 'content'):
            result = response.content
        else:
            result = str(response)
            
        return [types.TextContent(type="text", text=result)]
        
    except Exception as e:
        return [types.TextContent(type="text", text=f"Error processing request: {str(e)}")]
