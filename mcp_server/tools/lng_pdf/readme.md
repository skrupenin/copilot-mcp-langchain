# lng_pdf

PDF processing tools for extracting and manipulating PDF content.

## Tools

### extract_images
Extracts all images from PDF files preserving original format and compression.

**Features:**
- Preserves original image format (JPEG, PNG, etc.)  
- Maintains original compression and quality
- Names files as: image_<page_number>_<image_number_on_page>.<extension>
- Page numbering starts from 1
- Handles password-protected and corrupted PDF files gracefully

**Parameters:**
- `pdf_path` (string, required): Absolute path to the PDF file
- `output_directory` (string, optional): Directory to save extracted images

**Example:**
```json
{
  "pdf_path": "C:\\Documents\\report.pdf",
  "output_directory": "C:\\Images\\extracted"
}
```

**Returns:**
- total_images: Number of images extracted
- extracted_files: List of saved file paths  
- pages_processed: Number of pages processed
- output_directory: Directory where images were saved
- error_message: Error details if extraction failed

## Dependencies

- `PyMuPDF` (fitz) - For PDF processing and image extraction
