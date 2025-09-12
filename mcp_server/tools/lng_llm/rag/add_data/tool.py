import mcp.types as types
from mcp_server.state_manager import state_manager
from langchain.schema import Document
from langchain.text_splitter import (
    RecursiveCharacterTextSplitter, CharacterTextSplitter, TokenTextSplitter,
    MarkdownTextSplitter, PythonCodeTextSplitter, HTMLHeaderTextSplitter,
    LatexTextSplitter, NLTKTextSplitter, SpacyTextSplitter
)
import os
from mcp_server.llm import embeddings

def problem_imports():
    global FAISS
    from langchain_community.vectorstores import FAISS

problem_imports()

async def tool_info() -> dict:
    """Returns information about the lng_rag_add_data tool."""
    return {
        "description": """Adds text data to the RAG (Retrieval Augmented Generation) vector database.

**Parameters:**
- `input_text` (string, required): The text content to add to the vector database
- `metadata` (object, optional): Additional metadata to associate with this text
- `splitter` (object, optional): Text splitter configuration with type and config parameters

**Splitter Configuration:**
The splitter parameter should have the structure:
```json
{
  "type": "SplitterClassName",
  "config": {
    "param1": "value1",
    "param2": "value2"
  }
}
```

**Supported Splitters:**
- `RecursiveCharacterTextSplitter` (default): chunk_size, chunk_overlap, separators, keep_separator, etc.
- `CharacterTextSplitter`: separator, chunk_size, chunk_overlap, etc.
- `TokenTextSplitter`: encoding_name, model_name, chunk_size, chunk_overlap, etc.
- `MarkdownTextSplitter`: chunk_size, chunk_overlap, etc.
- `PythonCodeTextSplitter`: chunk_size, chunk_overlap, etc.
- `HTMLHeaderTextSplitter`: headers_to_split_on, return_each_element
- `LatexTextSplitter`: chunk_size, chunk_overlap, etc.
- `NLTKTextSplitter`: separator, language, chunk_size, chunk_overlap, etc.
- `SpacyTextSplitter`: separator, pipeline, max_length, chunk_size, chunk_overlap, etc.

**Common Parameters (for most splitters):**
- chunk_size: Maximum size of each chunk (default: 1000)
- chunk_overlap: Number of characters to overlap between chunks (default: 200)
- keep_separator: Whether to keep the separator in the chunks
- add_start_index: Whether to add start index to metadata
- strip_whitespace: Whether to strip whitespace from chunks

**Example Usage:**
- Default: `{"input_text": "Some text"}`
- Custom splitter: `{"input_text": "Some text", "splitter": {"type": "CharacterTextSplitter", "config": {"separator": "\\n", "chunk_size": 500}}}`
- Markdown: `{"input_text": "# Title\\n\\nContent", "splitter": {"type": "MarkdownTextSplitter", "config": {"chunk_size": 800}}}`

This tool is part of a RAG workflow that allows storage of text data in a vector database for 
later semantic search and retrieval.""",
        "schema": {
            "type": "object",
            "required": ["input_text"],
            "properties": {
                "input_text": {
                    "type": "string",
                    "description": "The text content to add to the vector database",
                },
                "metadata": {
                    "type": "object",
                    "description": "Additional metadata to associate with this text",
                },
                "splitter": {
                    "type": "object",
                    "description": "Text splitter configuration with type and config parameters",
                    "properties": {
                        "type": {
                            "type": "string",
                            "description": "Name of the text splitter class to use",
                            "enum": [
                                "RecursiveCharacterTextSplitter",
                                "CharacterTextSplitter", 
                                "TokenTextSplitter",
                                "MarkdownTextSplitter",
                                "PythonCodeTextSplitter",
                                "HTMLHeaderTextSplitter",
                                "LatexTextSplitter",
                                "NLTKTextSplitter",
                                "SpacyTextSplitter"
                            ]
                        },
                        "config": {
                            "type": "object",
                            "description": "Configuration parameters for the selected splitter"
                        }
                    },
                    "required": ["type"]
                }
            },
        }
    }

def create_text_splitter(splitter_config: dict):
    """Creates a text splitter based on the provided configuration."""
    splitter_type = splitter_config.get("type", "RecursiveCharacterTextSplitter")
    config = splitter_config.get("config", {})
    
    # Default configuration for RecursiveCharacterTextSplitter
    if splitter_type == "RecursiveCharacterTextSplitter" and not config:
        config = {"chunk_size": 1000, "chunk_overlap": 200}
    
    # Map of available splitters
    splitter_classes = {
        "RecursiveCharacterTextSplitter": RecursiveCharacterTextSplitter,
        "CharacterTextSplitter": CharacterTextSplitter,
        "TokenTextSplitter": TokenTextSplitter,
        "MarkdownTextSplitter": MarkdownTextSplitter,
        "PythonCodeTextSplitter": PythonCodeTextSplitter,
        "HTMLHeaderTextSplitter": HTMLHeaderTextSplitter,
        "LatexTextSplitter": LatexTextSplitter,
        "NLTKTextSplitter": NLTKTextSplitter,
        "SpacyTextSplitter": SpacyTextSplitter,
    }
    
    if splitter_type not in splitter_classes:
        raise ValueError(f"Unsupported splitter type: {splitter_type}. Supported types: {list(splitter_classes.keys())}")
    
    splitter_class = splitter_classes[splitter_type]
    
    try:
        return splitter_class(**config)
    except Exception as e:
        raise ValueError(f"Error creating {splitter_type} with config {config}: {str(e)}")


async def run_tool(name: str, parameters: dict) -> list[types.Content]:
    """Adds text data to the RAG vector database."""
    import json
    
    text = parameters.get("input_text", None)
    if not text:
        error_result = {
            "success": False,
            "error": "'input_text' parameter is required."
        }
        return [types.TextContent(type="text", text=json.dumps(error_result, indent=2))]
    
    metadata = parameters.get("metadata", {})
    splitter_config = parameters.get("splitter", {"type": "RecursiveCharacterTextSplitter"})
    
    try:
        # Create text splitter based on configuration
        text_splitter = create_text_splitter(splitter_config)
        
        # Split text into chunks
        chunks = text_splitter.split_text(text)
        
        # Create Document objects with metadata
        documents = [Document(page_content=chunk, metadata=metadata) for chunk in chunks]
        
        # Get vector store from state or create a new one
        vector_store = state_manager.get("vector_store")
        
        if vector_store is None:
            # If no vector store exists yet, create a new one
            vector_store = FAISS.from_documents(documents, embeddings())
            state_manager.set("vector_store", vector_store)
            operation = "created_new"
        else:
            # Add to existing vector store
            vector_store.add_documents(documents)
            state_manager.set("vector_store", vector_store)
            operation = "added_to_existing"
        
        # Create JSON result
        result = {
            "success": True,
            "operation": operation,
            "chunks_added": len(documents),
            "chunks_content": [chunk for chunk in chunks],
            "metadata": metadata,
            "splitter": {
                "type": splitter_config.get('type', 'RecursiveCharacterTextSplitter'),
                "config": splitter_config.get('config', {})
            },
            "total_characters": len(text),
            "average_chunk_size": sum(len(chunk) for chunk in chunks) // len(chunks) if chunks else 0
        }
        
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
        
    except Exception as e:
        error_result = {
            "success": False,
            "error": str(e)
        }
        return [types.TextContent(type="text", text=json.dumps(error_result, indent=2))]
