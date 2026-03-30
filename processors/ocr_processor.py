class OCRProcessor:
    def __init__(self, tesseract_path=None):
        self.available = False

    def process_image(self, file_path):
        return {
            'success': False,
            'error': 'OCR not available in this deployment'
        }