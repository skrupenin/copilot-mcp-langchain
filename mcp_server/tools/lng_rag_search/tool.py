import mcp.types as types
from mcp_server.state_manager import state_manager
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
- `use_prompt_template` (boolean, optional): Whether to use the saved prompt template with the retrieved documents (default: true)
  It should contain placeholders for `{context}` and `{query}` to format the response.

**Example Usage:**
- Search for documents related to a specific topic
- Retrieve the most relevant documents and generate a response using the saved prompt template
- Combine search results with the LLM to get context-aware responses

This tool works together with lng_rag_add_data and lng_save_prompt_template to provide a complete RAG workflow.""",
        "schema": {
            "type": "object",
            "required": ["query"],
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query to find relevant documents in the vector database",
                },
                "k": {
                    "type": "number",
                    "description": "The number of most relevant documents to retrieve (default: 3)",
                },
                "use_prompt_template": {
                    "type": "boolean",
                    "description": "Whether to use the saved prompt template with the retrieved documents (default: true)",
                }
            },
        }
    }

async def run_tool(name: str, parameters: dict) -> list[types.Content]:
    """Searches the RAG vector database with a query."""
    query = parameters.get("query", None)
    if not query:
        return [types.TextContent(type="text", text="Error: 'query' parameter is required.")]
    
    k = parameters.get("k", 3)
    use_prompt_template = parameters.get("use_prompt_template", True)
    
    try:
        # Get vector store from state
        vector_store = state_manager.get("vector_store")
        
        if vector_store is None:
            return [types.TextContent(type="text", text="Error: No vector database found. Please add documents first using lng_RAG_add_data.")]
        
        # Initialize embeddings
        embeddings = OpenAIEmbeddings()
        
        # Perform similarity search
        results = vector_store.similarity_search_with_score(query, k=k)
        
        if not results:
            return [types.TextContent(type="text", text="No relevant documents found for your query.")]
        
        # Format results
        retrieved_docs = []
        for doc, score in results:
            retrieved_docs.append({
                "content": doc.page_content,
                "metadata": doc.metadata,
                "relevance_score": float(score)
            })
        
        if use_prompt_template:
            # Get saved prompt template
            saved_template = state_manager.get("prompt_template")
            
            if saved_template is None:
                # If no template is saved, use a default one
                saved_template = "Based on the following context:\n\n{context}\n\nAnswer this query: {query}"
            
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
            
            return [types.TextContent(type="text", text=str(output))]
        else:
            # Just return the retrieved documents
            return [types.TextContent(type="text", text=str(retrieved_docs))]
            
    except Exception as e:
        return [types.TextContent(type="text", text=f"Error searching vector database: {str(e)}")]
