"""OCR processing for images and scanned documents"""
from PIL import Image
import pytesseract
from typing import Dict, List
import os


class OCRProcessor:
    """Handles OCR processing for images"""
    
    def __init__(self, tesseract_path: str = None):
        self.supported_formats = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif']
        
        # Set Tesseract path if provided
        if tesseract_path and os.path.exists(tesseract_path):
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
    
    def extract_text(self, file_path: str) -> Dict[str, any]:
        """
        Extract text from image using OCR
        
        Args:
            file_path: Path to image file
            
        Returns:
            Dictionary containing extracted text and metadata
        """
        try:
            # Open image
            image = Image.open(file_path)
            
            # Extract metadata
            metadata = {
                'file_name': os.path.basename(file_path),
                'file_size': os.path.getsize(file_path),
                'image_size': image.size,
                'image_mode': image.mode
            }
            
            # Perform OCR
            text = pytesseract.image_to_string(image)
            
            # Get OCR data with confidence
            ocr_data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
            
            return {
                'success': True,
                'full_text': text,
                'ocr_data': ocr_data,
                'metadata': metadata,
                'format': 'image_ocr'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'format': 'image_ocr'
            }
    
    def extract_with_structure(self, file_path: str) -> Dict[str, any]:
        """
        Extract text with basic structure detection
        
        Args:
            file_path: Path to image file
            
        Returns:
            Dictionary with structured content
        """
        result = self.extract_text(file_path)
        
        if not result['success']:
            return result
        
        # Basic structure detection from OCR text
        text = result['full_text']
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        structured_content = []
        current_section = {'heading': 'Content', 'content': []}
        
        for line in lines:
            # Simple heuristic for headings
            if len(line) < 100 and (line.isupper() or (line.istitle() and len(line.split()) <= 5)):
                if current_section['content']:
                    structured_content.append(current_section)
                current_section = {'heading': line, 'content': []}
            else:
                current_section['content'].append(line)
        
        if current_section['content']:
            structured_content.append(current_section)
        
        result['structured_content'] = structured_content
        return result
    
    def preprocess_image(self, image_path: str, output_path: str = None) -> str:
        """
        Preprocess image for better OCR results
        
        Args:
            image_path: Path to input image
            output_path: Path to save preprocessed image (optional)
            
        Returns:
            Path to preprocessed image
        """
        try:
            from PIL import ImageEnhance, ImageFilter
            
            image = Image.open(image_path)
            
            # Convert to grayscale
            image = image.convert('L')
            
            # Enhance contrast
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(2)
            
            # Sharpen
            image = image.filter(ImageFilter.SHARPEN)
            
            # Save if output path provided
            if output_path:
                image.save(output_path)
                return output_path
            
            return image_path
            
        except Exception as e:
            print(f"Error preprocessing image: {e}")
            return image_path
