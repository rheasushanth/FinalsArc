"""Document processor factory and manager"""
from typing import Dict, Optional
import os
from .pdf_processor import PDFProcessor
from .docx_processor import DOCXProcessor
from .pptx_processor import PPTXProcessor
from .ocr_processor import OCRProcessor


class DocumentProcessor:
    """Main document processor that routes to specific processors"""
    
    def __init__(self, tesseract_path: str = None):
        """
        Initialize all document processors
        
        Args:
            tesseract_path: Path to Tesseract executable for OCR
        """
        self.pdf_processor = PDFProcessor()
        self.docx_processor = DOCXProcessor()
        self.pptx_processor = PPTXProcessor()
        self.ocr_processor = OCRProcessor(tesseract_path)
        
        # Map file extensions to processors
        self.processor_map = {
            '.pdf': self.pdf_processor,
            '.docx': self.docx_processor,
            '.doc': self.docx_processor,
            '.pptx': self.pptx_processor,
            '.ppt': self.pptx_processor,
            '.jpg': self.ocr_processor,
            '.jpeg': self.ocr_processor,
            '.png': self.ocr_processor,
            '.bmp': self.ocr_processor,
            '.tiff': self.ocr_processor,
            '.gif': self.ocr_processor
        }
    
    def process_file(self, file_path: str, extract_structure: bool = True) -> Dict[str, any]:
        """
        Process a file and extract its content
        
        Args:
            file_path: Path to the file
            extract_structure: Whether to extract structured content
            
        Returns:
            Dictionary containing extracted content and metadata
        """
        # Get file extension
        _, ext = os.path.splitext(file_path.lower())
        
        # Get appropriate processor
        processor = self.processor_map.get(ext)
        
        if not processor:
            return {
                'success': False,
                'error': f'Unsupported file format: {ext}',
                'file_path': file_path
            }
        
        # Process file
        try:
            if extract_structure and hasattr(processor, 'extract_with_structure'):
                result = processor.extract_with_structure(file_path)
            else:
                result = processor.extract_text(file_path)
            
            result['file_path'] = file_path
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'file_path': file_path
            }
    
    def get_supported_formats(self) -> list:
        """Get list of all supported file formats"""
        return list(self.processor_map.keys())
    
    def is_supported(self, file_path: str) -> bool:
        """Check if a file format is supported"""
        _, ext = os.path.splitext(file_path.lower())
        return ext in self.processor_map
