"""Input validation utilities"""
from typing import List, Optional
import os


class FileValidator:
    """Validates uploaded files"""
    
    # Supported file extensions
    SUPPORTED_EXTENSIONS = [
        '.pdf', '.docx', '.doc', '.pptx', '.ppt',
        '.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif'
    ]
    
    # Max file size in bytes (default 10MB)
    MAX_FILE_SIZE = 10 * 1024 * 1024
    
    @classmethod
    def set_max_file_size(cls, size_mb: int):
        """Set maximum file size in MB"""
        cls.MAX_FILE_SIZE = size_mb * 1024 * 1024
    
    @classmethod
    def validate_file(cls, file_path: str, max_size: Optional[int] = None) -> dict:
        """
        Validate a file
        
        Args:
            file_path: Path to file
            max_size: Maximum file size in bytes (optional)
            
        Returns:
            Validation result dictionary
        """
        max_size = max_size or cls.MAX_FILE_SIZE
        
        # Check file exists
        if not os.path.exists(file_path):
            return {
                'valid': False,
                'error': 'File does not exist'
            }
        
        # Check file extension
        _, ext = os.path.splitext(file_path.lower())
        if ext not in cls.SUPPORTED_EXTENSIONS:
            return {
                'valid': False,
                'error': f'Unsupported file format: {ext}',
                'supported_formats': cls.SUPPORTED_EXTENSIONS
            }
        
        # Check file size
        file_size = os.path.getsize(file_path)
        if file_size > max_size:
            return {
                'valid': False,
                'error': f'File too large: {file_size} bytes (max: {max_size} bytes)'
            }
        
        # Check if file is readable
        try:
            with open(file_path, 'rb') as f:
                f.read(1)
        except Exception as e:
            return {
                'valid': False,
                'error': f'File not readable: {str(e)}'
            }
        
        return {
            'valid': True,
            'file_path': file_path,
            'extension': ext,
            'size': file_size
        }
    
    @classmethod
    def validate_multiple_files(cls, file_paths: List[str]) -> dict:
        """
        Validate multiple files
        
        Args:
            file_paths: List of file paths
            
        Returns:
            Validation results
        """
        results = []
        valid_files = []
        invalid_files = []
        
        for file_path in file_paths:
            result = cls.validate_file(file_path)
            results.append(result)
            
            if result['valid']:
                valid_files.append(file_path)
            else:
                invalid_files.append({
                    'file': file_path,
                    'error': result['error']
                })
        
        return {
            'all_valid': len(invalid_files) == 0,
            'valid_count': len(valid_files),
            'invalid_count': len(invalid_files),
            'valid_files': valid_files,
            'invalid_files': invalid_files,
            'results': results
        }


class InputValidator:
    """Validates user inputs"""
    
    VALID_LEVELS = ['beginner', 'intermediate', 'advanced']
    VALID_DIFFICULTIES = ['easy', 'medium', 'hard', 'mixed']
    VALID_FOCUS_TYPES = ['concept-oriented', 'exam-oriented']
    
    @classmethod
    def validate_level(cls, level: str) -> dict:
        """Validate academic level"""
        level = level.lower() if level else 'intermediate'
        
        if level not in cls.VALID_LEVELS:
            return {
                'valid': False,
                'error': f'Invalid level: {level}',
                'valid_options': cls.VALID_LEVELS,
                'default': 'intermediate'
            }
        
        return {
            'valid': True,
            'level': level
        }
    
    @classmethod
    def validate_difficulty(cls, difficulty: str) -> dict:
        """Validate difficulty level"""
        difficulty = difficulty.lower() if difficulty else 'mixed'
        
        if difficulty not in cls.VALID_DIFFICULTIES:
            return {
                'valid': False,
                'error': f'Invalid difficulty: {difficulty}',
                'valid_options': cls.VALID_DIFFICULTIES,
                'default': 'mixed'
            }
        
        return {
            'valid': True,
            'difficulty': difficulty
        }
    
    @classmethod
    def validate_focus(cls, focus: str) -> dict:
        """Validate focus type"""
        focus = focus.lower() if focus else 'concept-oriented'
        
        if focus not in cls.VALID_FOCUS_TYPES:
            return {
                'valid': False,
                'error': f'Invalid focus: {focus}',
                'valid_options': cls.VALID_FOCUS_TYPES,
                'default': 'concept-oriented'
            }
        
        return {
            'valid': True,
            'focus': focus
        }
    
    @classmethod
    def validate_num_questions(cls, num: int) -> dict:
        """Validate number of questions"""
        if not isinstance(num, int):
            try:
                num = int(num)
            except (ValueError, TypeError):
                return {
                    'valid': False,
                    'error': 'Number of questions must be an integer',
                    'default': 5
                }
        
        if num < 1:
            return {
                'valid': False,
                'error': 'Number of questions must be at least 1',
                'default': 5
            }
        
        if num > 20:
            return {
                'valid': False,
                'error': 'Number of questions cannot exceed 20',
                'default': 20
            }
        
        return {
            'valid': True,
            'num_questions': num
        }
    
    @classmethod
    def sanitize_text(cls, text: str, max_length: Optional[int] = None) -> str:
        """
        Sanitize text input
        
        Args:
            text: Input text
            max_length: Maximum allowed length
            
        Returns:
            Sanitized text
        """
        if not text:
            return ""
        
        # Remove leading/trailing whitespace
        text = text.strip()
        
        # Limit length if specified
        if max_length and len(text) > max_length:
            text = text[:max_length]
        
        return text
