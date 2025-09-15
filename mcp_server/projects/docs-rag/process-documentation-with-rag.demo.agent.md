## Info
- This demo demonstrates automated processing of documentation files into RAG (Retrieval Augmented Generation) system using file masks and batch pipeline.

## How to ask for demo in chat
Use this case to make demo:
```
Show me demo from file:
Process all documentation files in current project into RAG system for intelligent search and question answering.
```

## 🤖 AI Instructions
1. **Run Documentation Processing Pipeline**: Use `lng_batch_run` with pipeline configuration file
   - Pipeline automatically loads file masks from `file-masks.txt`
   - Searches for documentation files using glob patterns
   - Processes each found file and adds to RAG system
   - Includes metadata (file path, type, processing time, pattern)

**Key Features**: Batch document processing, glob pattern matching, automatic RAG integration, metadata enrichment

## Important
- Uses `file-masks.txt` for glob patterns (lines starting with `#` are ignored as comments)
- Default excluded directories: `node_modules`, `.git`, `__pycache__`, `copilot-session`, `temp`, `build`
- Files must be larger than 10 characters to be processed
- Each document gets metadata: `source_file`, `file_type`, `processed_at`, `mask_pattern`
- Creates FAISS vector database for intelligent document search

## Scenario
Automatically discover and process all documentation files in a project (Markdown, text, README files) and make them searchable through RAG system for intelligent question answering.

## Step 1: Process Documentation with Pipeline
```json
{
  "pipeline_file": "mcp_server/projects/docs-rag/pipeline-config.json"
}
```

## Configuration Files

### file-masks.txt Example
```
# Documentation files
docs/**/*.md
*.txt
**/README*
**/*.rst
**/*.adoc
docs/**/*.html
```

### User Parameters (pipeline-config.json)
- **masks_file**: Path to file masks (default: `file-masks.txt`)
- **base_path**: Base directory for search (default: current directory)  
- **excluded_dirs**: Directories to exclude from processing

## Processing Workflow
1. **Load File Masks**: Reads `file-masks.txt` and parses glob patterns
2. **Search Files**: Uses `lng_file_list` for each pattern to find matching files
3. **Process Files**: For each found file:
   - Reads file content with `lng_file_read`
   - Validates file is not empty (more than 10 characters)
   - Adds to RAG system using `lng_llm_rag_add_data`
   - Enriches with metadata (file path, type, processing time, matching pattern)

## Supported File Types
- Markdown files (`**/*.md`)
- Text files (`*.txt`)
- README files (`**/README*`)
- reStructuredText (`**/*.rst`)
- AsciiDoc (`**/*.adoc`)
- HTML documentation (`docs/**/*.html`)
