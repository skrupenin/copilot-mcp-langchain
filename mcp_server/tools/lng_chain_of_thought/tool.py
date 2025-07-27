import mcp.types as types
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.messages import HumanMessage, AIMessage
from langchain.memory import ConversationBufferMemory
from mcp_server.llm import llm

# Simple memory storage for different sessions
session_memories = {}

async def tool_info() -> dict:
    """Returns information about the lng_chain_of_thought tool."""
    return {
        "description": """Demonstrates Chain of Thought (CoT) reasoning with LangChain using memory.

**Parameters:**
- `question` (string, required): The question or problem to solve
- `session_id` (string, optional): A unique identifier for maintaining conversation state
- `new_session` (boolean, optional): Whether to start a new reasoning session (default: false)

**Example Usage:**
- Ask complex questions like math problems or logical puzzles
- Continue reasoning with follow-up questions using the same session_id
- See how memory helps in complex problem-solving

This tool shows how memory enhances Chain of Thought reasoning.""",
        "schema": {
            "type": "object",
            "required": ["question"],
            "properties": {
                "question": {
                    "type": "string",
                    "description": "The question to solve using chain of thought reasoning"
                },
                "session_id": {
                    "type": "string",
                    "description": "A unique identifier for maintaining conversation state",
                    "default": "default"
                },
                "new_session": {
                    "type": "boolean",
                    "description": "Whether to start a new reasoning session",
                    "default": False
                }
            }
        }
    }

async def run_tool(name: str, parameters: dict) -> list[types.Content]:
    """Simplified demonstration of Chain of Thought with memory."""
    
    try:
        question = parameters.get("question")
        session_id = parameters.get("session_id", "default")
        new_session = parameters.get("new_session", False)
          # 1. Memory management - create new or use existing
        if new_session or session_id not in session_memories:
            # Create new memory for this session
            memory = ConversationBufferMemory(return_messages=True)
            session_memories[session_id] = memory
        else:
            # Use existing memory
            memory = session_memories[session_id]
          # 2. Create template for Chain of Thought with memory integration
        prompt = ChatPromptTemplate.from_messages([
            ("system", "Solve problems by reasoning step by step."),
            MessagesPlaceholder(variable_name="history"),  # This is the place for previous messages from memory
            ("human", "Problem: {question}\nLet's reason step by step:")
        ])
          # 3. Create and run the chain with memory
        model = llm()        # Get history from memory directly
        history_messages = memory.chat_memory.messages
        
        # Create a chain with direct history passing
        chain = (
            {"question": lambda x: x["question"], "history": lambda _: history_messages}
            | prompt 
            | model 
            | StrOutputParser()
        )
        
        # Run the reasoning chain
        cot_result = await chain.ainvoke({"question": question})
          # 4. Save the current interaction to memory
        memory.chat_memory.add_user_message(f"Problem: {question}")
        memory.chat_memory.add_ai_message(cot_result)
        
        # 5. Format the output for display
        
        # Get previous reasoning history
        history = memory.chat_memory.messages
        history_formatted = ""
        
        # If there's history (more than just the current Q&A)
        if len(history) > 2:
            history_formatted = "## Previous Reasoning Steps\n\n"
            for i in range(0, len(history) - 2, 2):
                if isinstance(history[i], HumanMessage):
                    q = history[i].content.replace("Problem: ", "")
                    a = history[i+1].content if i+1 < len(history) else ""
                    history_formatted += f"**Question:** {q}\n\n**Answer:** {a}\n\n---\n\n"
        
        # Form the final output
        markdown_content = f"""# Chain of Thought with Memory

## Current Question
> {question}

## Reasoning Steps
{cot_result}

{history_formatted}
"""
        if session_id != "default":
            markdown_content += f"\n\nSession ID: `{session_id}`"
        
        return [types.TextContent(type="text", text=markdown_content)]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Error processing question: {str(e)}")]