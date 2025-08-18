import pytest
import asyncio
import os
import json
import tempfile
import shutil
from unittest.mock import patch, MagicMock
from pathlib import Path

# Add the tools directory to the Python path
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from tool import run_tool, tool_info

class TestPdfExtractImages:

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test files."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def sample_pdf_with_image(self, temp_dir):
        """Create a sample PDF with an image for testing."""
        try:
            import fitz
            from PIL import Image
            
            # Create a test image
            test_img = Image.new('RGB', (100, 50), color='blue')
            img_path = os.path.join(temp_dir, 'test_img.png')
            test_img.save(img_path)
            
            # Create PDF with image
            doc = fitz.open()
            page = doc.new_page(width=612, height=792)
            img_rect = fitz.Rect(50, 50, 150, 100)
            page.insert_image(img_rect, filename=img_path)
            
            pdf_path = os.path.join(temp_dir, 'test.pdf')
            doc.save(pdf_path)
            doc.close()
            
            return pdf_path
        except ImportError:
            pytest.skip("PyMuPDF or Pillow not available")

    def test_tool_info_returns_correct_schema(self):
        """Test that tool_info returns the correct schema."""
        # given
        expected_required_fields = ["pdf_path"]
        
        # when
        result = asyncio.run(tool_info())
        
        # then
        assert str(result["schema"]["required"]) == str(expected_required_fields)

    def test_tool_info_has_description(self):
        """Test that tool_info contains a description."""
        # given
        expected_type = str
        
        # when
        result = asyncio.run(tool_info())
        
        # then
        assert str(type(result["description"])) == str(expected_type)

    def test_missing_pdf_path_parameter(self):
        """Test error handling when pdf_path parameter is missing."""
        # given
        parameters = {}
        expected_error = "pdf_path parameter is required"
        
        # when
        result = asyncio.run(run_tool("lng_pdf_extract_images", parameters))
        content = json.loads(result[0].text)
        
        # then
        assert str(content["metadata"]["error"]) == str(expected_error)

    def test_empty_pdf_path_parameter(self):
        """Test error handling when pdf_path parameter is empty."""
        # given
        parameters = {"pdf_path": ""}
        expected_error = "pdf_path parameter is required"
        
        # when
        result = asyncio.run(run_tool("lng_pdf_extract_images", parameters))
        content = json.loads(result[0].text)
        
        # then
        assert str(content["metadata"]["error"]) == str(expected_error)

    def test_nonexistent_file_error(self):
        """Test error handling when PDF file does not exist."""
        # given
        parameters = {"pdf_path": "/path/to/nonexistent/file.pdf"}
        expected_error_start = "PDF file not found"
        
        # when
        result = asyncio.run(run_tool("lng_pdf_extract_images", parameters))
        content = json.loads(result[0].text)
        
        # then
        assert str(content["metadata"]["error"]).startswith(str(expected_error_start))

    def test_directory_instead_of_file_error(self, temp_dir):
        """Test error handling when path points to directory instead of file."""
        # given
        parameters = {"pdf_path": temp_dir}
        expected_error_start = "Path is not a file"
        
        # when
        result = asyncio.run(run_tool("lng_pdf_extract_images", parameters))
        content = json.loads(result[0].text)
        
        # then
        assert str(content["metadata"]["error"]).startswith(str(expected_error_start))

    def test_dependency_import_error(self):
        """Test error handling when required dependencies are not available."""
        # given
        parameters = {"pdf_path": "/some/path.pdf"}
        expected_error_start = "Required dependency not available"
        
        # when
        with patch('builtins.__import__', side_effect=ImportError("No module named 'fitz'")):
            result = asyncio.run(run_tool("lng_pdf_extract_images", parameters))
            content = json.loads(result[0].text)
        
        # then
        assert str(content["metadata"]["error"]).startswith(str(expected_error_start))

    def test_successful_image_extraction(self, sample_pdf_with_image, temp_dir):
        """Test successful image extraction from PDF."""
        # given
        parameters = {"pdf_path": sample_pdf_with_image}
        expected_success = True
        
        # when
        result = asyncio.run(run_tool("lng_pdf_extract_images", parameters))
        content = json.loads(result[0].text)
        
        # then
        assert str(content["success"]) == str(expected_success)

    def test_extracted_image_count(self, sample_pdf_with_image, temp_dir):
        """Test that correct number of images are extracted."""
        # given
        parameters = {"pdf_path": sample_pdf_with_image}
        expected_count = 1
        
        # when
        result = asyncio.run(run_tool("lng_pdf_extract_images", parameters))
        content = json.loads(result[0].text)
        
        # then
        assert str(content["total_images_extracted"]) == str(expected_count)

    def test_extracted_image_filename_format(self, sample_pdf_with_image, temp_dir):
        """Test that extracted images have correct filename format."""
        # given
        parameters = {"pdf_path": sample_pdf_with_image}
        expected_filename = "image_001.png"
        
        # when
        result = asyncio.run(run_tool("lng_pdf_extract_images", parameters))
        content = json.loads(result[0].text)
        
        # then
        assert str(content["images"][0]["filename"]) == str(expected_filename)

    def test_extracted_image_metadata_structure(self, sample_pdf_with_image, temp_dir):
        """Test that extracted image metadata contains required fields."""
        # given
        parameters = {"pdf_path": sample_pdf_with_image}
        expected_keys = ["filename", "path", "page_number", "original_format", "dimensions", "size_bytes"]
        
        # when
        result = asyncio.run(run_tool("lng_pdf_extract_images", parameters))
        content = json.loads(result[0].text)
        actual_keys = list(content["images"][0].keys())
        
        # then
        assert str(sorted(actual_keys)) == str(sorted(expected_keys))

    def test_extracted_image_dimensions(self, sample_pdf_with_image, temp_dir):
        """Test that extracted image dimensions are correct."""
        # given
        parameters = {"pdf_path": sample_pdf_with_image}
        expected_width = 100
        expected_height = 50
        
        # when
        result = asyncio.run(run_tool("lng_pdf_extract_images", parameters))
        content = json.loads(result[0].text)
        dimensions = content["images"][0]["dimensions"]
        
        # then
        assert str(dimensions["width"]) == str(expected_width)
        assert str(dimensions["height"]) == str(expected_height)

    def test_file_actually_created(self, sample_pdf_with_image, temp_dir):
        """Test that image file is actually created on disk."""
        # given
        parameters = {"pdf_path": sample_pdf_with_image}
        
        # when
        result = asyncio.run(run_tool("lng_pdf_extract_images", parameters))
        content = json.loads(result[0].text)
        image_path = content["images"][0]["path"]
        
        # then
        assert str(os.path.exists(image_path)) == str(True)

if __name__ == "__main__":
    pytest.main([__file__])