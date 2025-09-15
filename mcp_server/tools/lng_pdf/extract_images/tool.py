import mcp.types as types
import os
import fitz  # PyMuPDF
import json

async def tool_info() -> dict:
    """Returns information about the lng_pdf_extract_images tool."""
    return {
        "description": """Extracts all images from PDF files preserving original format and compression.

**Parameters:**
- `pdf_path` (string, required): Absolute path to the PDF file to extract images from.
- `output_directory` (string, optional): Directory to save extracted images. If not specified, saves to the same directory as the PDF file.

**Features:**
- Preserves original image format (JPEG, PNG, etc.)
- Maintains original compression and quality
- Names files as: image_<page_number>_<image_number_on_page>.<extension>
- Page numbering starts from 1
- Handles password-protected and corrupted PDF files gracefully

**Example Usage:**
- Extract to same folder: `{"pdf_path": "C:\\Documents\\document.pdf"}`
- Extract to specific folder: `{"pdf_path": "C:\\Documents\\document.pdf", "output_directory": "C:\\Images"}`

**Returns:**
- JSON with extraction results including:
  - total_images: Number of images extracted
  - extracted_files: List of saved file paths
  - pages_processed: Number of pages processed
  - error_message: Error details if extraction failed

**Error Handling:**
- Password-protected PDFs: Returns error message
- Corrupted PDFs: Returns error message  
- No images found: Returns success with zero images
- File not found: Returns error message

This tool uses PyMuPDF library for reliable PDF processing and image extraction.""",
        "schema": {
            "type": "object",
            "properties": {
                "pdf_path": {
                    "type": "string",
                    "description": "Absolute path to the PDF file"
                },
                "output_directory": {
                    "type": "string",
                    "description": "Directory to save extracted images (optional, defaults to PDF directory)"
                }
            },
            "required": ["pdf_path"]
        }
    }

async def tool_handler(arguments: dict) -> types.TextContent:
    """Handles the lng_pdf_extract_images tool execution."""
    
    try:
        # Get parameters
        pdf_path = arguments.get("pdf_path", "").strip()
        output_directory = arguments.get("output_directory", "").strip()
        
        # Validate PDF path
        if not pdf_path:
            return types.TextContent(
                type="text",
                text=json.dumps({
                    "success": False,
                    "error_message": "PDF path is required",
                    "total_images": 0,
                    "extracted_files": [],
                    "pages_processed": 0
                }, indent=2)
            )
        
        # Check if PDF file exists
        if not os.path.isfile(pdf_path):
            return types.TextContent(
                type="text", 
                text=json.dumps({
                    "success": False,
                    "error_message": f"PDF file not found: {pdf_path}",
                    "total_images": 0,
                    "extracted_files": [],
                    "pages_processed": 0
                }, indent=2)
            )
        
        # Set output directory
        if not output_directory:
            output_directory = os.path.dirname(pdf_path)
        
        # Create output directory if it doesn't exist
        os.makedirs(output_directory, exist_ok=True)
        
        # Initialize result tracking
        extracted_files = []
        total_images = 0
        pages_processed = 0
        
        try:
            # Open PDF document
            pdf_document = fitz.open(pdf_path)
            
            # Check if PDF is encrypted
            if pdf_document.is_encrypted:
                pdf_document.close()
                return types.TextContent(
                    type="text",
                    text=json.dumps({
                        "success": False,
                        "error_message": "PDF file is password-protected and cannot be processed",
                        "total_images": 0,
                        "extracted_files": [],
                        "pages_processed": 0
                    }, indent=2)
                )
            
            # Process each page
            for page_num in range(pdf_document.page_count):
                page = pdf_document[page_num]
                image_list = page.get_images()
                pages_processed += 1
                
                # Extract images from current page
                for img_index, img in enumerate(image_list):
                    # Get image data
                    xref = img[0]
                    base_image = pdf_document.extract_image(xref)
                    image_bytes = base_image["image"]
                    image_ext = base_image["ext"]
                    
                    # Generate filename: image_page_imagenum.ext
                    # Page numbering starts from 1
                    filename = f"image_{page_num + 1}_{img_index + 1}.{image_ext}"
                    filepath = os.path.join(output_directory, filename)
                    
                    # Save image preserving original format and compression
                    with open(filepath, "wb") as image_file:
                        image_file.write(image_bytes)
                    
                    extracted_files.append(filepath)
                    total_images += 1
            
            pdf_document.close()
            
            # Return success result
            return types.TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "total_images": total_images,
                    "extracted_files": extracted_files,
                    "pages_processed": pages_processed,
                    "output_directory": output_directory,
                    "message": f"Successfully extracted {total_images} images from {pages_processed} pages" if total_images > 0 else f"No images found in PDF (processed {pages_processed} pages)"
                }, indent=2)
            )
            
        except Exception as pdf_error:
            # Handle PDF processing errors
            error_msg = str(pdf_error)
            if "damaged" in error_msg.lower() or "corrupt" in error_msg.lower():
                error_message = "PDF file appears to be corrupted or damaged"
            elif "password" in error_msg.lower() or "encrypted" in error_msg.lower():
                error_message = "PDF file is password-protected"
            else:
                error_message = f"Error processing PDF: {error_msg}"
            
            return types.TextContent(
                type="text",
                text=json.dumps({
                    "success": False,
                    "error_message": error_message,
                    "total_images": total_images,
                    "extracted_files": extracted_files,
                    "pages_processed": pages_processed
                }, indent=2)
            )
            
    except Exception as e:
        # Handle general errors
        return types.TextContent(
            type="text",
            text=json.dumps({
                "success": False,
                "error_message": f"Unexpected error: {str(e)}",
                "total_images": 0,
                "extracted_files": [],
                "pages_processed": 0
            }, indent=2)
        )

async def run_tool(name: str, parameters: dict) -> list[types.Content]:
    """Extracts all images from PDF files preserving original format and compression."""
    try:
        # Get parameters
        pdf_path = parameters.get("pdf_path", "").strip()
        output_directory = parameters.get("output_directory", "").strip()
        
        # Validate PDF path
        if not pdf_path:
            error_result = {
                "success": False,
                "error_message": "PDF path is required",
                "total_images": 0,
                "extracted_files": [],
                "pages_processed": 0
            }
            return [types.TextContent(type="text", text=json.dumps(error_result, indent=2))]
        
        # Check if PDF file exists
        if not os.path.isfile(pdf_path):
            error_result = {
                "success": False,
                "error_message": f"PDF file not found: {pdf_path}",
                "total_images": 0,
                "extracted_files": [],
                "pages_processed": 0
            }
            return [types.TextContent(type="text", text=json.dumps(error_result, indent=2))]
        
        # Set output directory
        if not output_directory:
            output_directory = os.path.dirname(pdf_path)
        
        # Create output directory if it doesn't exist
        os.makedirs(output_directory, exist_ok=True)
        
        # Initialize result tracking
        extracted_files = []
        total_images = 0
        pages_processed = 0
        
        try:
            # Open PDF document
            pdf_document = fitz.open(pdf_path)
            
            # Check if PDF is encrypted
            if pdf_document.is_encrypted:
                pdf_document.close()
                error_result = {
                    "success": False,
                    "error_message": "PDF file is password-protected and cannot be processed",
                    "total_images": 0,
                    "extracted_files": [],
                    "pages_processed": 0
                }
                return [types.TextContent(type="text", text=json.dumps(error_result, indent=2))]
            
            # Process each page
            for page_num in range(pdf_document.page_count):
                page = pdf_document[page_num]
                image_list = page.get_images()
                pages_processed += 1
                
                # Extract images from current page
                for img_index, img in enumerate(image_list):
                    # Get image data
                    xref = img[0]
                    base_image = pdf_document.extract_image(xref)
                    image_bytes = base_image["image"]
                    image_ext = base_image["ext"]
                    
                    # Generate filename: image_page_imagenum.ext
                    # Page numbering starts from 1
                    filename = f"image_{page_num + 1}_{img_index + 1}.{image_ext}"
                    filepath = os.path.join(output_directory, filename)
                    
                    # Save image preserving original format and compression
                    with open(filepath, "wb") as image_file:
                        image_file.write(image_bytes)
                    
                    extracted_files.append(filepath)
                    total_images += 1
            
            pdf_document.close()
            
            # Return success result
            success_result = {
                "success": True,
                "total_images": total_images,
                "extracted_files": extracted_files,
                "pages_processed": pages_processed,
                "output_directory": output_directory,
                "message": f"Successfully extracted {total_images} images from {pages_processed} pages" if total_images > 0 else f"No images found in PDF (processed {pages_processed} pages)"
            }
            return [types.TextContent(type="text", text=json.dumps(success_result, indent=2))]
            
        except Exception as pdf_error:
            # Handle PDF processing errors
            error_msg = str(pdf_error)
            if "damaged" in error_msg.lower() or "corrupt" in error_msg.lower():
                error_message = "PDF file appears to be corrupted or damaged"
            elif "password" in error_msg.lower() or "encrypted" in error_msg.lower():
                error_message = "PDF file is password-protected"
            else:
                error_message = f"Error processing PDF: {error_msg}"
            
            error_result = {
                "success": False,
                "error_message": error_message,
                "total_images": total_images,
                "extracted_files": extracted_files,
                "pages_processed": pages_processed
            }
            return [types.TextContent(type="text", text=json.dumps(error_result, indent=2))]
            
    except Exception as e:
        # Handle general errors
        error_result = {
            "success": False,
            "error_message": f"Unexpected error: {str(e)}",
            "total_images": 0,
            "extracted_files": [],
            "pages_processed": 0
        }
        return [types.TextContent(type="text", text=json.dumps(error_result, indent=2))]
