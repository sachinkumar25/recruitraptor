"""Unit tests for TextExtractor class."""

import pytest
from unittest.mock import Mock, patch
from resume_parser.core.extractor import TextExtractor

class TestTextExtractor:
    """Test cases for TextExtractor class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.extractor = TextExtractor()
    
    def test_validate_file_type(self):
        """Test file type validation."""
        assert self.extractor.validate_file_type('pdf') == True
        assert self.extractor.validate_file_type('docx') == True
        assert self.extractor.validate_file_type('txt') == True
        assert self.extractor.validate_file_type('jpg') == False
        assert self.extractor.validate_file_type('exe') == False
    
    def test_get_supported_types(self):
        """Test getting supported file types."""
        supported_types = self.extractor.get_supported_types()
        assert 'pdf' in supported_types
        assert 'docx' in supported_types
        assert 'txt' in supported_types
    
    def test_extract_invalid_file_type(self):
        """Test extraction with invalid file type."""
        with pytest.raises(ValueError, match="Unsupported file type"):
            self.extractor.extract(b"test content", "invalid")
    
    def test_extract_empty_file(self):
        """Test extraction with empty file."""
        with pytest.raises(ValueError, match="File is empty"):
            self.extractor.extract(b"", "txt")
    
    def test_extract_file_too_large(self):
        """Test extraction with file exceeding size limit."""
        large_content = b"x" * (self.extractor.MAX_FILE_SIZE + 1)
        with pytest.raises(ValueError, match="exceeds maximum"):
            self.extractor.extract(large_content, "txt")
    
    def test_extract_txt_success(self):
        """Test successful TXT file extraction."""
        content = b"This is a test resume with more than 100 words. " * 75  # Ensure >150 words
        text, metadata = self.extractor.extract(content, "txt")
        
        assert isinstance(text, str)
        assert len(text) > 0
        assert metadata['file_type'] == 'txt'
        assert metadata['extraction_method'] == 'text-encoding-detection'
        assert metadata['encoding'] == 'utf-8'
        assert metadata['word_count'] >= 100
    
    def test_extract_txt_encoding_detection(self):
        """Test TXT file with different encodings."""
        # Test with UTF-8
        content = "Test resume content with more words to meet minimum requirement. " * 15
        text, metadata = self.extractor.extract(content.encode('utf-8'), "txt")
        assert metadata['encoding'] == 'utf-8'
        
        # Test with Latin-1
        content = "Test resume content with more words to meet minimum requirement. " * 15
        text, metadata = self.extractor.extract(content.encode('latin-1'), "txt")
        assert metadata['encoding'] == 'latin-1'
    
    def test_clean_text(self):
        """Test text cleaning functionality."""
        dirty_text = "  This   is\na\ttest\n\n\nresume  "
        cleaned = self.extractor._clean_text(dirty_text)
        assert cleaned == "This is a test resume"
    
    def test_clean_text_empty(self):
        """Test cleaning empty text."""
        assert self.extractor._clean_text("") == ""
        assert self.extractor._clean_text(None) == ""
    
    @patch('resume_parser.core.extractor.PyPDF2.PdfReader')
    def test_extract_pdf_success(self, mock_pdf_reader):
        """Test successful PDF extraction."""
        # Mock PDF reader
        mock_reader = Mock()
        mock_reader.is_encrypted = False
        mock_page = Mock()
        mock_page.extract_text.return_value = "Test PDF content with more words to meet minimum requirement. " * 25
        mock_reader.pages = [mock_page]
        mock_pdf_reader.return_value = mock_reader
        
        content = b"fake pdf content"
        text, metadata = self.extractor.extract(content, "pdf")
        
        assert isinstance(text, str)
        assert len(text) > 0
        assert metadata['extraction_method'] == 'pypdf2'
    
    @patch('resume_parser.core.extractor.PyPDF2.PdfReader')
    def test_extract_pdf_encrypted(self, mock_pdf_reader):
        """Test PDF extraction with encrypted file."""
        # Mock encrypted PDF
        mock_reader = Mock()
        mock_reader.is_encrypted = True
        mock_pdf_reader.return_value = mock_reader
        
        content = b"fake encrypted pdf content"
        with pytest.raises(RuntimeError, match="Password-protected PDFs"):
            self.extractor.extract(content, "pdf")
    
    @patch('resume_parser.core.extractor.Document')
    def test_extract_docx_success(self, mock_document):
        """Test successful DOCX extraction."""
        # Mock DOCX document
        mock_doc = Mock()
        mock_paragraph = Mock()
        mock_paragraph.text = "Test DOCX content with more words to meet minimum requirement. " * 25
        mock_doc.paragraphs = [mock_paragraph]
        mock_doc.tables = []
        mock_document.return_value = mock_doc
        
        content = b"fake docx content"
        text, metadata = self.extractor.extract(content, "docx")
        
        assert isinstance(text, str)
        assert len(text) > 0
        assert metadata['extraction_method'] == 'python-docx'
    
    def test_minimum_word_count_validation(self):
        """Test minimum word count validation."""
        short_content = b"This is a short resume with only a few words"
        with pytest.raises(ValueError, match="minimum required"):
            self.extractor.extract(short_content, "txt")
