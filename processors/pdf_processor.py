"""PDF text extraction and processing"""
import PyPDF2
from typing import Dict, List
import os


class PDFProcessor:
    """Handles PDF document processing and text extraction"""
    
    def __init__(self):
        self.supported_formats = ['.pdf']
    
    def extract_text(self, file_path: str) -> Dict[str, any]:
        """
        Extract text from PDF file
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Dictionary containing extracted text and metadata
        """
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                # Extract metadata
                metadata = {
                    'num_pages': len(pdf_reader.pages),
                    'file_name': os.path.basename(file_path),
                    'file_size': os.path.getsize(file_path)
                }
                
                # Extract text from all pages
                full_text = []
                page_texts = []
                
                for page_num, page in enumerate(pdf_reader.pages, 1):
                    text = page.extract_text()
                    page_texts.append({
                        'page_number': page_num,
                        'text': text
                    })
                    full_text.append(text)
                
                return {
                    'success': True,
                    'full_text': '\n\n'.join(full_text),
                    'pages': page_texts,
                    'metadata': metadata,
                    'format': 'pdf'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'format': 'pdf'
            }
    
    def extract_with_structure(self, file_path: str) -> Dict[str, any]:
        """
        Extract text with structural information (headings, paragraphs)
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Dictionary with structured content
        """
        result = self.extract_text(file_path)
        
        if not result['success']:
            return result
        
        # Basic structure detection
        text = result['full_text']
        lines = text.split('\n')
        
        structured_content = []
        current_section = {'heading': 'Introduction', 'content': []}
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Simple heuristic: short lines in ALL CAPS or title case might be headings
            if len(line) < 100 and (line.isupper() or line.istitle()):
                if current_section['content']:
                    structured_content.append(current_section)
                current_section = {'heading': line, 'content': []}
            else:
                current_section['content'].append(line)
        
        if current_section['content']:
            structured_content.append(current_section)
        
        result['structured_content'] = structured_content
        return result
