import mcp.types as types
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from mcp_server.llm import llm

async def tool_info() -> dict:
    """Returns information about the lng_chain_of_thought tool."""
    return {
        "name": "lng_chain_of_thought",
        "description": """Demonstrates Chain of Thought (CoT) reasoning with LangChain.

**Parameters:**
- `question` (string, required): The question or problem to solve using chain of thought reasoning
- `include_examples` (boolean, optional): Whether to include examples in the prompt (default: true)

**Example Usage:**
- Ask complex reasoning questions like math problems or logical puzzles
- The system will show step-by-step reasoning and analysis of the reasoning process
- See how the model breaks down complex problems into manageable steps

This tool shows how prompting LLMs to think step by step improves performance on complex reasoning tasks.""",
        "schema": {
            "type": "object",
            "required": ["question"],
            "properties": {
                "question": {
                    "type": "string",
                    "description": "The question or problem to solve using chain of thought reasoning"
                },
                "include_examples": {
                    "type": "boolean",
                    "description": "Whether to include examples in the prompt (default: true)",
                    "default": True
                }
            }
        }
    }

async def run_tool(name: str, parameters: dict) -> list[types.Content]:
    """Demonstrates Chain of Thought (CoT) reasoning with LangChain."""
    
    try: 
        question = parameters.get("question")
        include_examples = parameters.get("include_examples", True)
        
        # Define CoT examples
        cot_examples = """
Example 1:
Question: If I have 5 apples and I buy 2 more, then give 3 to my friend, how many apples do I have left?
Let's think step by step:
1. Initially, I have 5 apples.
2. I buy 2 more apples, so now I have 5 + 2 = 7 apples.
3. I give 3 apples to my friend, so I have 7 - 3 = 4 apples left.
Therefore, I have 4 apples left.

Example 2:
Question: If a train travels 120 miles in 2 hours, what is its average speed in miles per hour?
Let's think step by step:
1. The train traveled 120 miles in 2 hours.
2. Average speed is calculated as distance divided by time.
3. So, the average speed is 120 miles / 2 hours = 60 miles per hour.
Therefore, the train's average speed is 60 miles per hour.
"""
    
        # Define template for CoT
        if include_examples:
            cot_template = f"""You are an assistant that solves problems by carefully reasoning step by step.
{cot_examples}

Question: {{question}}
Let's think step by step:"""
        else:
            cot_template = """You are an assistant that solves problems by carefully reasoning step by step.

Question: {question}
Let's think step by step:"""
    
        # Create prompt from template
        cot_prompt = PromptTemplate(template=cot_template, input_variables=["question"])
        
        # Create modern runnable for CoT
        model = llm()
        cot_chain = cot_prompt | model | StrOutputParser()
        
        # Run the Chain of Thought approach
        cot_result = await cot_chain.ainvoke({"question": question})
        
        # Format the results for display focusing only on the reasoning process
        markdown_content = f"""# Chain of Thought Reasoning Analysis

## The Question
> {question}

## Step-by-Step Reasoning Process
{cot_result}

## Analysis of the Reasoning Chain
Let's examine the reasoning process above:

1. **Initial Problem Understanding**: The question requires tracking a changing quantity through multiple operations
2. **Sequential Operations**: The model breaks down the problem into discrete mathematical steps
3. **Intermediate States**: Each step captures the state of the system after each operation
4. **Logical Flow**: The reasoning follows a clear cause-effect relationship between actions and results
5. **Conclusion Verification**: The final answer is derived directly from the preceding steps
"""
        # Use proper MCP type for markdown content
        return [types.TextContent(type="text", text=markdown_content)]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Error saving prompt template: {str(e)}")]