import json
import mcp.types as types
from mcp_server.state_manager import state_manager
from mcp_server.file_state_manager import prompts_manager
from langchain_openai import OpenAIEmbeddings
from langchain.prompts import PromptTemplate
from mcp_server.llm import llm

async def tool_info() -> dict:
    """Returns information about the lng_rag_search tool."""
    return {
        "description": """Searches the RAG (Retrieval Augmented Generation) vector database with a query and returns relevant results.

**Parameters:**
- `query` (string, required): The search query to find relevant documents in the vector database
- `k` (number, optional): The number of most relevant documents to retrieve (default: 3)
- `prompt_template` (string, required): Name of the prompt template to use with the retrieved documents
  The template should contain placeholders for `{context}` and `{query}` to format the response.
  Use lng_llm_prompt_template tool first to create templates.

**Example Usage:**
- First, create a prompt template: lng_llm_prompt_template with command="save"
- Then search for documents related to a specific topic
- Specify which template to use: prompt_template="scientific" or prompt_template="default_rag"
- The tool will retrieve relevant documents and generate a response using the specified template
- Templates must contain {context} and {query} placeholders for proper RAG functionality

This tool works together with lng_rag_add_data and lng_llm_prompt_template to provide a complete RAG workflow.""",
        "schema": {
            "type": "object",
            "required": ["query", "prompt_template"],
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query to find relevant documents in the vector database",
                },
                "k": {
                    "type": "number",
                    "description": "The number of most relevant documents to retrieve (default: 3)",
                },
                "prompt_template": {
                    "type": "string",
                    "description": "Name of the prompt template to use with the retrieved documents (required)",
                }
            },
        }
    }

async def run_tool(name: str, parameters: dict) -> list[types.Content]:
    """Searches the RAG vector database with a query."""
    query = parameters.get("query", None)
    if not query:
        error_output = {
            "error": "missing_parameter",
            "message": "'query' parameter is required",
            "required_parameter": "query"
        }
        return [types.TextContent(type="text", text=json.dumps(error_output, ensure_ascii=False, indent=2))]
    
    k = parameters.get("k", 3)
    prompt_template_name = parameters.get("prompt_template")
    
    if not prompt_template_name:
        error_output = {
            "error": "missing_parameter",
            "message": "'prompt_template' parameter is required",
            "required_parameter": "prompt_template",
            "suggestion": "Use lng_llm_prompt_template tool first to create a template, then specify its name here"
        }
        return [types.TextContent(type="text", text=json.dumps(error_output, ensure_ascii=False, indent=2))]
    
    try:
        # Get vector store from state
        vector_store = state_manager.get("vector_store")
        
        if vector_store is None:
            error_output = {
                "error": "no_vector_database",
                "message": "No vector database found",
                "suggestion": "Please add documents first using lng_llm_rag_add_data"
            }
            return [types.TextContent(type="text", text=json.dumps(error_output, ensure_ascii=False, indent=2))]
        
        # Initialize embeddings
        embeddings = OpenAIEmbeddings()
        
        # Perform similarity search
        results = vector_store.similarity_search_with_score(query, k=k)
        
        if not results:
            no_results_output = {
                "message": "No relevant documents found for your query",
                "query": query,
                "retrieved_documents": [],
                "response": None
            }
            return [types.TextContent(type="text", text=json.dumps(no_results_output, ensure_ascii=False, indent=2))]
        
        # Format results
        retrieved_docs = []
        for doc, score in results:
            retrieved_docs.append({
                "content": doc.page_content,
                "metadata": doc.metadata,
                "relevance_score": float(score)
            })
        
        # Get saved prompt template by name
        saved_template = prompts_manager.get(prompt_template_name, extension=".prompt")
        
        if saved_template is None:
            # If specified template is not found, return error with available templates
            available_templates = prompts_manager.list_files(extension=".prompt")
            error_output = {
                "error": "template_not_found",
                "message": f"Prompt template '{prompt_template_name}' not found",
                "requested_template": prompt_template_name,
                "available_templates": available_templates if available_templates else [],
                "suggestion": "Use lng_llm_prompt_template to create new templates"
            }
            return [types.TextContent(type="text", text=json.dumps(error_output, ensure_ascii=False, indent=2))]
            
        # Create a context from retrieved documents
        context = "\n\n".join([f"Document {i+1}:\n{doc['content']}" for i, doc in enumerate(retrieved_docs)])
        
        # Create prompt template with the input variables
        prompt_template = PromptTemplate(
            input_variables=["context", "query"],
            template=saved_template
        )
        
        # Format the prompt with the provided parameters
        prompt = prompt_template.format(context=context, query=query)
        
        model = llm()

        # Get response from LLM
        response = model.invoke(prompt)
        
        # Check if the response has content and convert it to string
        if hasattr(response, "content"):
            response_text = response.content
        else:
            response_text = str(response)
        
        # Add retrieved documents and LLM response to output
        output = {
            "response": response_text,
            "retrieved_documents": retrieved_docs
        }
        
        return [types.TextContent(type="text", text=json.dumps(output, ensure_ascii=False, indent=2))]
            
    except Exception as e:
        error_output = {
            "error": "exception",
            "message": f"Error searching vector database: {str(e)}",
            "exception_type": type(e).__name__,
            "query": query
        }
        return [types.TextContent(type="text", text=json.dumps(error_output, ensure_ascii=False, indent=2))]
