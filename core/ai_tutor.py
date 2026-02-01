"""Main AI Tutor orchestrator"""
from typing import Dict, List, Optional
import os
from dotenv import load_dotenv

from .note_generator import NoteGenerator
from .question_gen import QuestionGenerator
from .explainer import ConceptExplainer


class AITutor:
    """Main AI-powered Study Buddy and Personal Tutor"""
    
    def __init__(self, api_key: str = None, provider: str = "openai", model: str = None):
        """
        Initialize AI Tutor
        
        Args:
            api_key: API key for AI provider
            provider: AI provider (openai or anthropic)
            model: Model name to use
        """
        load_dotenv()
        
        self.provider = provider or os.getenv('AI_PROVIDER', 'openai')
        self.api_key = api_key or self._get_api_key()
        self.model = model or self._get_default_model()
        
        # Initialize AI client
        self.ai_client = self._init_ai_client()
        
        # Initialize components with model name
        self.note_generator = NoteGenerator(self.ai_client, self.model)
        self.question_generator = QuestionGenerator(self.ai_client, self.model)
        self.explainer = ConceptExplainer(self.ai_client, self.model)
        
        # Storage for processed materials
        self.materials = {}
        self.notes_cache = {}
    
    def _get_api_key(self) -> str:
        """Get API key from environment"""
        if self.provider == 'openai':
            key = os.getenv('OPENAI_API_KEY')
            if not key:
                raise ValueError("OPENAI_API_KEY not found in environment variables")
            return key
        elif self.provider == 'anthropic':
            key = os.getenv('ANTHROPIC_API_KEY')
            if not key:
                raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
            return key
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")
    
    def _get_default_model(self) -> str:
        """Get default model for provider"""
        if self.provider == 'openai':
            # Check if using OpenRouter
            if self.api_key and self.api_key.startswith('sk-or-v1-'):
                return os.getenv('MODEL_NAME', 'openai/gpt-4o-mini')
            return os.getenv('MODEL_NAME', 'gpt-4o-mini')
        elif self.provider == 'anthropic':
            return os.getenv('MODEL_NAME', 'claude-3-opus-20240229')
        return 'gpt-4o-mini'
    
    def _init_ai_client(self):
        """Initialize AI client based on provider"""
        if self.provider == 'openai':
            from openai import OpenAI
            # Check if using OpenRouter (key starts with sk-or-v1-)
            if self.api_key.startswith('sk-or-v1-'):
                return OpenAI(
                    api_key=self.api_key,
                    base_url="https://openrouter.ai/api/v1"
                )
            else:
                return OpenAI(api_key=self.api_key)
        elif self.provider == 'anthropic':
            from anthropic import Anthropic
            return Anthropic(api_key=self.api_key)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")
    
    def add_material(self, material_id: str, content: Dict[str, any]) -> Dict[str, any]:
        """
        Add processed study material
        
        Args:
            material_id: Unique identifier for the material
            content: Processed content dictionary
            
        Returns:
            Confirmation dictionary
        """
        self.materials[material_id] = content
        
        return {
            'success': True,
            'material_id': material_id,
            'message': 'Material added successfully'
        }
    
    def generate_study_notes(
        self,
        material_id: str,
        subject: Optional[str] = None,
        level: str = "intermediate",
        focus: str = "concept-oriented"
    ) -> Dict[str, any]:
        """
        Generate comprehensive study notes for a material
        
        Args:
            material_id: ID of the material
            subject: Subject area
            level: Academic level
            focus: Focus type
            
        Returns:
            Generated notes
        """
        if material_id not in self.materials:
            return {
                'success': False,
                'error': 'Material not found'
            }
        
        material = self.materials[material_id]
        content = material.get('full_text', '')
        
        if not content:
            return {
                'success': False,
                'error': 'No content found in material'
            }
        
        # Check cache
        cache_key = f"{material_id}_{subject}_{level}_{focus}"
        if cache_key in self.notes_cache:
            return self.notes_cache[cache_key]
        
        # Generate notes
        result = self.note_generator.generate_notes(
            content=content,
            subject=subject,
            level=level,
            focus=focus
        )
        
        # Cache result
        if result['success']:
            self.notes_cache[cache_key] = result
        
        return result
    
    def ask_question(
        self,
        question: str,
        material_id: Optional[str] = None,
        level: str = "intermediate"
    ) -> Dict[str, any]:
        """
        Answer a student's question
        
        Args:
            question: The student's question
            material_id: Optional material ID for context
            level: Student level
            
        Returns:
            Explanation
        """
        # Get context if material provided
        context = None
        if material_id and material_id in self.materials:
            context = self.materials[material_id].get('full_text', '')
        
        return self.explainer.explain_concept(
            question=question,
            context=context,
            level=level
        )
    
    def request_simpler_explanation(
        self,
        original_explanation: str,
        question: str
    ) -> Dict[str, any]:
        """
        Get a simpler version of an explanation
        
        Args:
            original_explanation: Previous explanation
            question: Original question
            
        Returns:
            Simplified explanation
        """
        return self.explainer.explain_simpler(
            original_explanation=original_explanation,
            question=question
        )
    
    def generate_practice_quiz(
        self,
        material_id: str,
        num_questions: int = 5,
        difficulty: str = "mixed",
        subject: Optional[str] = None
    ) -> Dict[str, any]:
        """
        Generate practice questions for a material
        
        Args:
            material_id: ID of the material
            num_questions: Number of questions
            difficulty: Difficulty level
            subject: Subject area
            
        Returns:
            Quiz questions with solutions
        """
        if material_id not in self.materials:
            return {
                'success': False,
                'error': 'Material not found'
            }
        
        material = self.materials[material_id]
        content = material.get('full_text', '')
        
        if not content:
            return {
                'success': False,
                'error': 'No content found in material'
            }
        
        return self.question_generator.generate_questions(
            content=content,
            subject=subject,
            num_questions=num_questions,
            difficulty=difficulty
        )
    
    def explain_multiple_ways(self, concept: str) -> Dict[str, any]:
        """
        Explain a concept using multiple approaches
        
        Args:
            concept: Concept to explain
            
        Returns:
            Multiple explanations
        """
        return self.explainer.provide_multiple_approaches(concept)
    
    def get_material_summary(self, material_id: str) -> Dict[str, any]:
        """
        Get summary of uploaded material
        
        Args:
            material_id: ID of the material
            
        Returns:
            Material summary
        """
        if material_id not in self.materials:
            return {
                'success': False,
                'error': 'Material not found'
            }
        
        material = self.materials[material_id]
        
        return {
            'success': True,
            'material_id': material_id,
            'format': material.get('format'),
            'metadata': material.get('metadata', {}),
            'has_structure': 'structured_content' in material,
            'content_length': len(material.get('full_text', ''))
        }
    
    def list_materials(self) -> List[Dict[str, any]]:
        """
        List all uploaded materials
        
        Returns:
            List of material summaries
        """
        return [
            {
                'material_id': mat_id,
                'format': mat.get('format'),
                'file_name': mat.get('metadata', {}).get('file_name'),
                'content_length': len(mat.get('full_text', ''))
            }
            for mat_id, mat in self.materials.items()
        ]
