import json
from typing import Dict, Any, List
import mcp.types as types
from pydantic import BaseModel, Field
from mcp_server.llm import llm

from langchain.output_parsers import (
    StructuredOutputParser,
    ResponseSchema,
    PydanticOutputParser, 
    XMLOutputParser,
    OutputFixingParser
)
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence
import yaml

async def tool_info() -> dict:
    """Returns information about the lng_structured_output tool."""
    return {
        "description": """Demonstrates various structured output formats in LangChain using OutputParser.

**Parameters:**
- `question` (string, required): The question about a movie to be answered in a structured format
- `output_format` (string, required): Output data format (json, xml, csv, yaml, pydantic)

**Example Usage:**
- Provide a question about a movie and specify the desired output format
- The system will return structured information about the movie in the requested format
- Use different formats to see how LangChain structures the same information

This tool demonstrates the OutputParser capabilities in LangChain for transforming LLM outputs into structured formats.""",
        "schema": {
            "type": "object",
            "required": ["question", "output_format"],
            "properties": {
                "question": {
                    "type": "string",
                    "description": "The question about a movie to be answered in a structured format",
                },
                "output_format": {
                    "type": "string",
                    "description": "Output data format",
                    "enum": ["json", "xml", "csv", "yaml", "pydantic"]
                }
            },
        }
    }

class MovieReview(BaseModel):
    """Movie Review"""
    title: str = Field(description="Movie title")
    director: str = Field(description="Movie director")
    year: int = Field(description="Release year")
    rating: float = Field(description="Movie rating on a scale from 1 to 10")
    genres: List[str] = Field(description="Movie genres")
    review: str = Field(description="Brief movie review")


async def format_as_json(question: str) -> str:
    """Format the response as JSON using StructuredOutputParser."""
    model = llm()
    
    # Define the response schema for a movie
    response_schemas = [
        ResponseSchema(name="title", description="Movie title"),
        ResponseSchema(name="director", description="Movie director"),
        ResponseSchema(name="year", description="Release year (number)"),
        ResponseSchema(name="rating", description="Rating on a scale from 1 to 10 (number)"),
        ResponseSchema(name="genres", description="List of genres, comma-separated"),
        ResponseSchema(name="review", description="Brief movie review")
    ]
    
    # Create parser and prompt template
    parser = StructuredOutputParser.from_response_schemas(response_schemas)
    format_instructions = parser.get_format_instructions()
    
    template = """
    Answer the following question about a movie with structured information:
    
    {question}
    
    {format_instructions}
    """
    
    prompt = PromptTemplate(
        template=template,
        input_variables=["question"],
        partial_variables={"format_instructions": format_instructions}
    )
      # Create and run the chain using RunnableSequence
    chain = prompt | model
    response = await chain.ainvoke({"question": question})
    
    # Extract content from AIMessage if needed
    result = response.content if hasattr(response, 'content') else response
    
    # Parse the result and format it as JSON
    try:
        parsed_result = parser.parse(result)
        # Convert string lists to actual lists
        if isinstance(parsed_result.get("genres"), str) and "," in parsed_result.get("genres", ""):
            parsed_result["genres"] = [item.strip() for item in parsed_result["genres"].split(",")]
        
        return json.dumps(parsed_result, ensure_ascii=False, indent=2)
    except Exception as e:
        # If parsing failed, use OutputFixingParser for correction
        fixing_parser = OutputFixingParser.from_llm(parser=parser, llm=model)
        try:
            fixed_result = fixing_parser.parse(result)
            if isinstance(fixed_result.get("genres"), str) and "," in fixed_result.get("genres", ""):
                fixed_result["genres"] = [item.strip() for item in fixed_result["genres"].split(",")]
            return json.dumps(fixed_result, ensure_ascii=False, indent=2)
        except Exception as e2:
            return f"Parsing error: {str(e2)}\nOriginal response:\n{result}"


async def format_as_xml(question: str) -> str:
    """Format the response as XML using XMLOutputParser."""
    model = llm()
    
    # Use XMLOutputParser
    parser = XMLOutputParser(root_tag="response")
    
    # Define the XML structure we want
    xml_structure = """
    <response>
      <movie>
        <title>Movie title</title>
        <director>Movie director</director>
        <year>Release year (number only)</year>
        <rating>Rating (number only from 1 to 10)</rating>
        <genres>
          <genre>Genre 1</genre>
          <genre>Genre 2</genre>
          <!-- Additional genres -->
        </genres>
        <review>Brief movie review</review>
      </movie>
    </response>
    """
    
    # Get formatting instructions from the parser
    instructions = f"""
    Answer the question about a movie in XML format. Use the following structure:
    
    {xml_structure}
    """

    # Create prompt template
    template = """
    {format_instructions}
    
    Question about a movie: {question}
    
    Answer in XML:
    """
    
    prompt = PromptTemplate(
        template=template,
        input_variables=["question"],
        partial_variables={"format_instructions": instructions}
    )
    
    # Create and run the chain using RunnableSequence, incorporating the parser
    chain = prompt | model | parser
    
    try:
        # The parser will automatically format the response as XML
        response = await chain.ainvoke({"question": question})
        
        # Return the XML string - the parser has already formatted it properly
        return response
    except Exception as e:
        # If parsing fails, fall back to manual extraction
        try:
            # Get the raw response without using the parser
            raw_chain = prompt | model
            raw_response = await raw_chain.ainvoke({"question": question})
            
            # Extract content from AIMessage if needed
            result = raw_response.content if hasattr(raw_response, 'content') else raw_response
            # Manual cleanup as fallback

            start_idx = result.find("<")
            end_idx = result.rfind(">") + 1
            if start_idx >= 0 and end_idx > 0:
                clean_xml = result[start_idx:end_idx]
                return clean_xml
            return result
        except Exception as e2:
            # Safely handle the case where result might not be defined
            raw_result = "Response not available due to error"
            if 'raw_response' in locals():
                raw_result = raw_response.content if hasattr(raw_response, 'content') else str(raw_response)
            return f"XML formatting error: {str(e2)}\nOriginal response:\n{raw_result}"


async def format_as_csv(question: str) -> str:
    """Format the response as CSV."""
    model = llm()
    
    headers = "title,director,year,rating,genres,review"
    instructions = f"""
    Answer the question about a movie in CSV format. The first line should contain headers:
    {headers}
    
    The second line should contain values. Year and rating should be numbers.
    Genres should be listed in a single cell, separated by semicolons.
    """
    
    # Create prompt template
    template = """
    {instructions}
    
    Question about a movie: {question}
    
    Answer in CSV:
    """
    
    prompt = PromptTemplate(
        template=template,
        input_variables=["question"],
        partial_variables={"instructions": instructions}
    )
      # Create and run the chain using RunnableSequence
    chain = prompt | model
    response = await chain.ainvoke({"question": question})
    
    # Extract content from AIMessage if needed
    result = response.content if hasattr(response, 'content') else response
    
    # Process the result
    try:
        # Remove extra lines before and after CSV
        lines = [line.strip() for line in result.split("\n") if line.strip()]
        csv_lines = []
        
        # Look for lines that resemble CSV (contain commas)
        for line in lines:
            if "," in line:
                csv_lines.append(line)
        
        if len(csv_lines) >= 2:  # We should have at least 2 lines (headers and data)
            return "\n".join(csv_lines[:2])  # Take only the first two lines
        else:
            return result  # Return the original result if we couldn't extract CSV
    except Exception as e:
        return f"CSV formatting error: {str(e)}\nOriginal response:\n{result}"


async def format_as_yaml(question: str) -> str:
    """Format the response as YAML."""
    model = llm()
    
    yaml_example = """
    movie:
      title: Movie title
      director: Movie director
      year: 2020  # Release year (number)
      rating: 8.5  # Rating (number from 1 to 10)
      genres:
        - Genre 1
        - Genre 2
      review: Brief movie review
    """
    
    instructions = """
    Answer the question about a movie in YAML format. Use the following structure:
    
    movie:
      title: Movie title
      director: Movie director
      year: 2020  # must be a number
      rating: 8.5  # must be a number from 1 to 10
      genres:
        - Genre 1
        - Genre 2
      review: Brief movie review
    """
    
    # Create prompt template
    template = """
    {instructions}
    
    Question about a movie: {question}
    
    Answer in YAML:
    """
    
    prompt = PromptTemplate(
        template=template,
        input_variables=["question"],
        partial_variables={"instructions": instructions}
    )
      # Create and run the chain using RunnableSequence
    chain = prompt | model
    response = await chain.ainvoke({"question": question})
    
    # Extract content from AIMessage if needed
    result = response.content if hasattr(response, 'content') else response
      # Process the result
    try:
        # Extract YAML from the response, handling Markdown code blocks
        lines = result.split("\n")
        yaml_lines = []
        in_yaml = False
        in_code_block = False
        
        for line in lines:
            # Check for the start of a code block
            if line.strip().startswith("```"):
                # Toggle code block state
                in_code_block = not in_code_block
                # Skip the code block markers
                continue
                
            # Look for the start of the YAML block
            if not in_yaml and line.strip().startswith("movie:"):
                in_yaml = True
            
            # Include the line if we're in a YAML block or in a code block (after skipping the markers)
            if in_yaml or in_code_block:
                yaml_lines.append(line)
        
        if yaml_lines:
            yaml_content = "\n".join(yaml_lines)
            # Verify that it's valid YAML by loading it and then serializing it again
            parsed_yaml = yaml.safe_load(yaml_content)
            formatted_yaml = yaml.dump(parsed_yaml, default_flow_style=False, allow_unicode=True)
            return formatted_yaml
        else:
            # If we couldn't extract YAML, try parsing the whole response as YAML
            # This might work if the response is already valid YAML
            try:
                # Remove code block markers if present
                clean_result = result
                if "```yaml" in result or "```" in result:
                    clean_result = "\n".join([
                        line for line in result.split("\n") 
                        if not line.strip().startswith("```")
                    ])
                parsed_yaml = yaml.safe_load(clean_result)
                formatted_yaml = yaml.dump(parsed_yaml, default_flow_style=False, allow_unicode=True)
                return formatted_yaml
            except:
                return result
    except Exception as e:
        return f"YAML formatting error: {str(e)}\nOriginal response:\n{result}"


async def format_as_pydantic(question: str) -> str:
    """Format the response using PydanticOutputParser."""
    model = llm()
    
    # Use the MovieReview model
    parser = PydanticOutputParser(pydantic_object=MovieReview)
    
    # Get formatting instructions
    format_instructions = parser.get_format_instructions()
    
    # Create prompt template
    template = """
    Answer the following question about a movie using a structured format:
    
    {question}
    
    {format_instructions}
    """
    
    prompt = PromptTemplate(
        template=template,
        input_variables=["question"],
        partial_variables={"format_instructions": format_instructions}
    )
      # Create and run the chain using RunnableSequence
    chain = prompt | model
    response = await chain.ainvoke({"question": question})
    
    # Extract content from AIMessage if needed
    result = response.content if hasattr(response, 'content') else response
      # Process the result to handle Markdown code blocks
    try:
        # Extract clean content if it's in a code block
        clean_result = result
        if "```json" in result or "```" in result:
            # Extract content between code block markers
            code_blocks = []
            lines = result.split("\n")
            in_code_block = False
            current_block = []
            
            for line in lines:
                if line.strip().startswith("```"):
                    if in_code_block:
                        # End of a code block, add it to our list
                        code_blocks.append("\n".join(current_block))
                        current_block = []
                    in_code_block = not in_code_block
                    continue  # Skip the marker line
                
                if in_code_block:
                    current_block.append(line)
            
            # Use the first code block we found (if any)
            if code_blocks:
                clean_result = code_blocks[0]
        
        # Now try to parse the cleaned result
        parsed_obj = parser.parse(clean_result)
        # Use model_dump_json instead of json method for newer Pydantic versions
        if hasattr(parsed_obj, "model_dump_json"):
            return parsed_obj.model_dump_json(indent=2)
        else:
            # Fallback for older Pydantic versions
            return parsed_obj.json(indent=2)
    except Exception as e:
        # If parsing failed, try to extract JSON from the response and create a MovieReview object directly
        try:
            # Try to find JSON in the response
            if "```json" in result or "```" in result:
                # Extract content between code block markers
                code_blocks = []
                lines = result.split("\n")
                in_code_block = False
                current_block = []
                
                for line in lines:
                    if line.strip().startswith("```"):
                        if in_code_block:
                            # End of a code block, add it to our list
                            code_blocks.append("\n".join(current_block))
                            current_block = []
                        in_code_block = not in_code_block
                        continue  # Skip the marker line
                    
                    if in_code_block:
                        current_block.append(line)
                
                # Use the first code block we found (if any)
                if code_blocks:
                    json_data = json.loads(code_blocks[0])
                    # Create a MovieReview object from the JSON data
                    movie_review = MovieReview(**json_data)
                    # Serialize it back to JSON
                    if hasattr(movie_review, "model_dump_json"):
                        return movie_review.model_dump_json(indent=2)
                    else:
                        return movie_review.json(indent=2)
            
            # If we couldn't extract a code block or the above failed, use the OutputFixingParser
            fixing_parser = OutputFixingParser.from_llm(parser=parser, llm=model)
            fixed_obj = fixing_parser.parse(clean_result)
            if hasattr(fixed_obj, "model_dump_json"):
                return fixed_obj.model_dump_json(indent=2)
            else:
                return fixed_obj.json(indent=2)
        except Exception as e2:
            return f"Parsing error: {str(e2)}\nOriginal response:\n{result}"

async def run_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Runs the tool with the specified arguments."""
    question = arguments.get("question", "")
    output_format = arguments.get("output_format", "json")
    
    try:
        if output_format == "json":
            result = await format_as_json(question)
        elif output_format == "xml":
            result = await format_as_xml(question)
        elif output_format == "csv":
            result = await format_as_csv(question)
        elif output_format == "yaml":
            result = await format_as_yaml(question)
        elif output_format == "pydantic":
            result = await format_as_pydantic(question)
        else:
            result = f"Unsupported format: {output_format}"
        
        return [types.TextContent(type="text", text=result)]
    except Exception as e:
        error_text = f"An error occurred while formatting to {output_format}: {str(e)}"
        return [types.TextContent(type="text", text=error_text)]