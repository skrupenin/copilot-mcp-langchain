import mcp.types as types
from mcp_server.state_manager import state_manager
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
import os

async def tool_info() -> dict:
    """Returns information about the lng_rag_add_data tool."""
    return {
        "name": "lng_rag_add_data",
        "description": """Adds text data to the RAG (Retrieval Augmented Generation) vector database.

**Parameters:**
- `text` (string, required): The text content to add to the vector database
- `metadata` (object, optional): Additional metadata to associate with this text

**Example Usage:**
- Add a document or text passage to the vector database for later retrieval
- Include optional metadata like source, author, or categories for better retrieval

This tool is part of a RAG workflow that allows storage of text data in a vector database for 
later semantic search and retrieval.""",
        "schema": {
            "type": "object",
            "required": ["text"],
            "properties": {
                "text": {
                    "type": "string",
                    "description": "The text content to add to the vector database",
                },
                "metadata": {
                    "type": "object",
                    "description": "Additional metadata to associate with this text",
                }
            },
        }
    }

async def run_tool(name: str, parameters: dict) -> list[types.Content]:
    """Adds text data to the RAG vector database."""
    text = parameters.get("text", None)
    if not text:
        return [types.TextContent(type="text", text="Error: 'text' parameter is required.")]
    
    metadata = parameters.get("metadata", {})
    
    try:
        # Create text splitter for chunking the document
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        
        # Split text into chunks
        chunks = text_splitter.split_text(text)
        
        # Create Document objects with metadata
        documents = [Document(page_content=chunk, metadata=metadata) for chunk in chunks]
        
        # Initialize OpenAI embeddings
        embeddings = OpenAIEmbeddings()
        
        # Get existing vector store from state or create a new one
        vector_store = state_manager.get("vector_store")
        
        if vector_store is None:
            # If no vector store exists yet, create a new one
            vector_store = FAISS.from_documents(documents, embeddings)
            state_manager.set("vector_store", vector_store)
            return [types.TextContent(type="text", text=f"Created new vector database with {len(documents)} text chunks.")]
        else:
            # Add to existing vector store
            vector_store.add_documents(documents)
            state_manager.set("vector_store", vector_store)
            return [types.TextContent(type="text", text=f"Added {len(documents)} text chunks to existing vector database.")]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Error adding data to vector database: {str(e)}")]
