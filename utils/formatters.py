"""Formatting utilities for study notes and responses"""
import re
from typing import Dict, List


class ResponseFormatter:
    """Formats AI responses for better readability"""
    
    @staticmethod
    def format_notes(notes: str) -> str:
        """
        Format study notes with proper Markdown
        
        Args:
            notes: Raw notes text
            
        Returns:
            Formatted notes
        """
        # Ensure consistent formatting
        formatted = notes
        
        # Add spacing around headings
        formatted = re.sub(r'\n(#{1,6}\s)', r'\n\n\1', formatted)
        formatted = re.sub(r'(#{1,6}\s[^\n]+)\n', r'\1\n\n', formatted)
        
        # Ensure emoji markers are properly spaced
        formatted = re.sub(r'([⭐⚠️🧠])\s*\*\*', r'\1 **', formatted)
        
        return formatted.strip()
    
    @staticmethod
    def highlight_important(text: str) -> str:
        """
        Add visual highlighting to important points
        
        Args:
            text: Input text
            
        Returns:
            Text with highlights
        """
        # Already using emojis, but could add more formatting
        return text
    
    @staticmethod
    def format_question(question: Dict[str, any]) -> str:
        """
        Format a question for display
        
        Args:
            question: Question dictionary
            
        Returns:
            Formatted question string
        """
        formatted = f"**Question {question.get('id', '')}** ({question.get('difficulty', 'medium')})\n\n"
        formatted += f"{question.get('question', '')}\n\n"
        
        if question.get('type') == 'multiple_choice' and question.get('options'):
            formatted += "**Options:**\n"
            for option in question['options']:
                formatted += f"{option}\n"
            formatted += "\n"
        
        return formatted
    
    @staticmethod
    def format_solution(question: Dict[str, any], show_answer: bool = True) -> str:
        """
        Format a question solution
        
        Args:
            question: Question dictionary
            show_answer: Whether to show the answer
            
        Returns:
            Formatted solution
        """
        solution = ""
        
        if show_answer:
            solution += f"**✅ Correct Answer:** {question.get('correct_answer', 'N/A')}\n\n"
        
        solution += "**💡 Explanation:**\n"
        solution += f"{question.get('explanation', 'No explanation provided.')}\n\n"
        
        if question.get('hints'):
            solution += "**🔍 Hints:**\n"
            for i, hint in enumerate(question['hints'], 1):
                solution += f"{i}. {hint}\n"
            solution += "\n"
        
        if question.get('key_concept'):
            solution += f"**🎯 Key Concept:** {question['key_concept']}\n"
        
        return solution
    
    @staticmethod
    def create_summary_box(title: str, content: str) -> str:
        """
        Create a formatted summary box
        
        Args:
            title: Box title
            content: Box content
            
        Returns:
            Formatted box
        """
        box = f"\n{'='*60}\n"
        box += f"  {title.upper()}\n"
        box += f"{'='*60}\n\n"
        box += content
        box += f"\n{'='*60}\n"
        
        return box


class EmojiHelper:
    """Helper for consistent emoji usage"""
    
    IMPORTANT = "⭐"
    WARNING = "⚠️"
    BRAIN = "🧠"
    TARGET = "🎯"
    BOOK = "📚"
    MAGNIFY = "🔍"
    BULB = "💡"
    WORLD = "🌍"
    GRADUATION = "🎓"
    CHECKMARK = "✅"
    CROSS = "❌"
    FIRE = "🔥"
    SPARKLES = "✨"
    
    @classmethod
    def get_difficulty_emoji(cls, difficulty: str) -> str:
        """Get emoji for difficulty level"""
        mapping = {
            'easy': '🟢',
            'medium': '🟡',
            'hard': '🔴'
        }
        return mapping.get(difficulty.lower(), '⚪')
    
    @classmethod
    def get_subject_emoji(cls, subject: str) -> str:
        """Get emoji for subject"""
        subject_lower = subject.lower() if subject else ''
        
        mapping = {
            'math': '🔢',
            'mathematics': '🔢',
            'science': '🔬',
            'physics': '⚛️',
            'chemistry': '🧪',
            'biology': '🧬',
            'history': '📜',
            'english': '📖',
            'literature': '📚',
            'computer': '💻',
            'programming': '💻',
            'art': '🎨',
            'music': '🎵'
        }
        
        for key, emoji in mapping.items():
            if key in subject_lower:
                return emoji
        
        return '📚'


class MarkdownHelper:
    """Helper for Markdown formatting"""
    
    @staticmethod
    def heading(text: str, level: int = 1) -> str:
        """Create Markdown heading"""
        return f"{'#' * level} {text}\n\n"
    
    @staticmethod
    def bold(text: str) -> str:
        """Make text bold"""
        return f"**{text}**"
    
    @staticmethod
    def italic(text: str) -> str:
        """Make text italic"""
        return f"*{text}*"
    
    @staticmethod
    def code(text: str, block: bool = False) -> str:
        """Format as code"""
        if block:
            return f"```\n{text}\n```"
        return f"`{text}`"
    
    @staticmethod
    def bullet_list(items: List[str]) -> str:
        """Create bullet list"""
        return '\n'.join(f"- {item}" for item in items) + '\n\n'
    
    @staticmethod
    def numbered_list(items: List[str]) -> str:
        """Create numbered list"""
        return '\n'.join(f"{i}. {item}" for i, item in enumerate(items, 1)) + '\n\n'
    
    @staticmethod
    def quote(text: str) -> str:
        """Create block quote"""
        return '\n'.join(f"> {line}" for line in text.split('\n')) + '\n\n'
    
    @staticmethod
    def divider() -> str:
        """Create horizontal divider"""
        return "\n---\n\n"
