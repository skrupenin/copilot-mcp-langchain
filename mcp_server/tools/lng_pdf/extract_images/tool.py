import mcp.types as types
import os
import json
from pathlib import Path

async def tool_info() -> dict:
    """Returns information about the lng_pdf_extract_images tool."""
    return {
        "description": """Extracts all images from PDF files to PNG format with sequential naming and metadata.

**Parameters:**
- `pdf_path` (string, required): Absolute or relative path to the PDF file.

**Functionality:**
- Extracts images from all pages of the PDF
- Handles both embedded and inline images
- Saves images as PNG files in the same directory as the source PDF
- Uses sequential naming: image_001.png, image_002.png, etc.
- Returns metadata for each extracted image

**Returns:**
- JSON object with extraction results and metadata
- For each image: dimensions, original format, page number, file path
- Total count of extracted images and operation status

**Example Usage:**
- Extract images from PDF: `{"pdf_path": "document.pdf"}`
- Extract from specific path: `{"pdf_path": "/path/to/document.pdf"}`

**Error Handling:**
- Returns detailed error information if PDF cannot be opened
- Handles missing files and invalid PDF formats
- Reports any image extraction failures

This tool requires PyMuPDF library and supports all PDF versions.""",
        "schema": {
            "type": "object",
            "properties": {
                "pdf_path": {
                    "type": "string",
                    "description": "Path to the PDF file (absolute or relative)"
                }
            },
            "required": ["pdf_path"]
        }
    }

async def run_tool(name: str, parameters: dict) -> list[types.Content]:
    """Extracts all images from PDF files to PNG format with sequential naming and metadata."""
    try:
        # Import dependencies here to avoid import-time errors
        try:
            import fitz  # PyMuPDF
            from PIL import Image
        except ImportError as e:
            error_metadata = {
                "operation": "pdf_image_extraction",
                "success": False,
                "error": f"Required dependency not available: {str(e)}. Please install PyMuPDF and Pillow."
            }
            result = json.dumps({"metadata": error_metadata}, indent=2)
            return [types.TextContent(type="text", text=result)]
        
        # Extract parameters
        pdf_path = parameters.get("pdf_path", "")
        
        if not pdf_path:
            error_metadata = {
                "operation": "pdf_image_extraction",
                "success": False,
                "error": "pdf_path parameter is required"
            }
            result = json.dumps({"metadata": error_metadata}, indent=2)
            return [types.TextContent(type="text", text=result)]

        # Resolve path
        pdf_path = os.path.expanduser(pdf_path)
        if not os.path.isabs(pdf_path):
            pdf_path = os.path.abspath(pdf_path)

        # Check if file exists
        if not os.path.exists(pdf_path):
            error_metadata = {
                "operation": "pdf_image_extraction",
                "success": False,
                "error": f"PDF file not found: {pdf_path}"
            }
            result = json.dumps({"metadata": error_metadata}, indent=2)
            return [types.TextContent(type="text", text=result)]

        # Check if it's a file
        if not os.path.isfile(pdf_path):
            error_metadata = {
                "operation": "pdf_image_extraction",
                "success": False,
                "error": f"Path is not a file: {pdf_path}"
            }
            result = json.dumps({"metadata": error_metadata}, indent=2)
            return [types.TextContent(type="text", text=result)]

        # Get output directory (same as PDF)
        pdf_dir = os.path.dirname(pdf_path)
        
        try:
            # Open PDF document
            doc = fitz.open(pdf_path)
        except Exception as e:
            error_metadata = {
                "operation": "pdf_image_extraction",
                "success": False,
                "error": f"Failed to open PDF: {str(e)}"
            }
            result = json.dumps({"metadata": error_metadata}, indent=2)
            return [types.TextContent(type="text", text=result)]

        extracted_images = []
        image_count = 0
        total_pages = len(doc)  # Store page count before processing
        
        try:
            # Process each page
            for page_num in range(total_pages):
                page = doc.load_page(page_num)
                image_list = page.get_images()
                
                # Extract images from this page
                for img_index, img in enumerate(image_list):
                    try:
                        # Get image reference
                        xref = img[0]
                        
                        # Extract image data
                        base_image = doc.extract_image(xref)
                        image_bytes = base_image["image"]
                        image_ext = base_image["ext"]
                        
                        # Generate sequential filename
                        image_count += 1
                        image_filename = f"image_{image_count:03d}.png"
                        image_path = os.path.join(pdf_dir, image_filename)
                        
                        # Convert to PNG and save
                        if image_ext.lower() == "png":
                            # Already PNG, save directly
                            with open(image_path, "wb") as image_file:
                                image_file.write(image_bytes)
                        else:
                            # Convert to PNG using PIL
                            import io
                            
                            # Load image data
                            image_stream = io.BytesIO(image_bytes)
                            pil_image = Image.open(image_stream)
                            
                            # Convert to PNG
                            pil_image.save(image_path, "PNG")
                        
                        # Get image dimensions
                        with Image.open(image_path) as pil_img:
                            width, height = pil_img.size
                        
                        # Store metadata
                        image_metadata = {
                            "filename": image_filename,
                            "path": image_path,
                            "page_number": page_num + 1,  # 1-based page numbering
                            "original_format": image_ext.upper(),
                            "dimensions": {
                                "width": width,
                                "height": height
                            },
                            "size_bytes": os.path.getsize(image_path)
                        }
                        
                        extracted_images.append(image_metadata)
                        
                    except Exception as e:
                        # Log individual image extraction error but continue
                        error_info = {
                            "page_number": page_num + 1,
                            "image_index": img_index,
                            "error": str(e)
                        }
                        # Continue processing other images
                        continue
            
            # Close document
            doc.close()
            
            # Prepare result
            result_metadata = {
                "operation": "pdf_image_extraction",
                "success": True,
                "pdf_path": pdf_path,
                "output_directory": pdf_dir,
                "total_images_extracted": len(extracted_images),
                "total_pages_processed": total_pages,
                "images": extracted_images
            }
            
            result = json.dumps(result_metadata, indent=2)
            return [types.TextContent(type="text", text=result)]
            
        except Exception as e:
            # Close document if still open
            try:
                doc.close()
            except:
                pass
                
            error_metadata = {
                "operation": "pdf_image_extraction",
                "success": False,
                "error": f"Error during image extraction: {str(e)}"
            }
            result = json.dumps({"metadata": error_metadata}, indent=2)
            return [types.TextContent(type="text", text=result)]

    except Exception as e:
        error_metadata = {
            "operation": "pdf_image_extraction",
            "success": False,
            "error": f"Unexpected error: {str(e)}"
        }
        result = json.dumps({"metadata": error_metadata}, indent=2)
        return [types.TextContent(type="text", text=result)]