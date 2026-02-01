"""Practice question generator with solutions"""
from typing import Dict, List, Optional
import json


class QuestionGenerator:
    """Generates practice questions with detailed solutions"""
    
    def __init__(self, ai_client, model_name='openai/gpt-4o-mini'):
        """
        Initialize question generator
        
        Args:
            ai_client: AI client (OpenAI or Anthropic)
            model_name: Model name to use
        """
        self.ai_client = ai_client
        self.model_name = model_name
    
    def generate_questions(
        self,
        content: str,
        subject: Optional[str] = None,
        num_questions: int = 5,
        difficulty: Optional[str] = "mixed"
    ) -> Dict[str, any]:
        """
        Generate practice questions from content
        
        Args:
            content: The study material content
            subject: Subject area
            num_questions: Number of questions to generate
            difficulty: Difficulty level (easy/medium/hard/mixed)
            
        Returns:
            Dictionary containing questions and solutions
        """
        
        difficulty_distribution = {
            'easy': {'easy': num_questions, 'medium': 0, 'hard': 0},
            'medium': {'easy': 0, 'medium': num_questions, 'hard': 0},
            'hard': {'easy': 0, 'medium': 0, 'hard': num_questions},
            'mixed': {
                'easy': num_questions // 3 + (1 if num_questions % 3 > 0 else 0),
                'medium': num_questions // 3 + (1 if num_questions % 3 > 1 else 0),
                'hard': num_questions // 3
            }
        }
        
        dist = difficulty_distribution.get(difficulty, difficulty_distribution['mixed'])
        
        # Limit content length to avoid token limits
        prompt = f"""You are an expert tutor creating practice questions for students.

**Study Material:**
{content[:3000]}

**Subject:** {subject or "General"}
**Difficulty Distribution:**
- Easy Questions: {dist['easy']}
- Medium Questions: {dist['medium']}
- Hard Questions: {dist['hard']}

**Generate practice questions following this EXACT JSON format:**

{{
  "questions": [
    {{
      "id": 1,
      "difficulty": "easy",
      "question": "Question text here?",
      "type": "multiple_choice",
      "options": ["A) Option 1", "B) Option 2", "C) Option 3", "D) Option 4"],
      "correct_answer": "B) Option 2",
      "explanation": "Step 1: [First step of solution]\\nStep 2: [Second step]\\nStep 3: [Final answer with reasoning]",
      "key_concept": "Main concept being tested",
      "hints": ["Hint 1 if student is stuck", "Hint 2 for additional help"]
    }}
  ]
}}

**Question Types to Use:**
- multiple_choice (most common)
- true_false
- short_answer
- calculation
- explanation

**Requirements:**
1. **Easy questions:** Test basic definitions and simple concepts
2. **Medium questions:** Test understanding and application
3. **Hard questions:** Test synthesis, analysis, and complex problem-solving

4. For EVERY question, provide:
   - Clear, unambiguous question text
   - For multiple choice: 4 options with one clearly correct answer
   - Detailed step-by-step explanation of the solution
   - Why other options are wrong (for multiple choice)
   - 2-3 helpful hints

5. Make questions exam-relevant and practical
6. Cover different aspects of the material
7. Include worked examples in explanations

**Return ONLY valid JSON, no additional text.**
"""

        try:
            response = self._get_ai_response(prompt)
            
            # Parse JSON response
            # Clean up response if needed
            response = response.strip()
            if response.startswith('```json'):
                response = response[7:]
            if response.startswith('```'):
                response = response[3:]
            if response.endswith('```'):
                response = response[:-3]
            response = response.strip()
            
            questions_data = json.loads(response)
            
            return {
                'success': True,
                'questions': questions_data.get('questions', []),
                'metadata': {
                    'total_questions': len(questions_data.get('questions', [])),
                    'subject': subject,
                    'difficulty': difficulty
                }
            }
            
        except json.JSONDecodeError as e:
            return {
                'success': False,
                'error': f'Failed to parse questions: {str(e)}',
                'raw_response': response
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def generate_single_question(
        self,
        topic: str,
        difficulty: str = "medium",
        question_type: str = "multiple_choice"
    ) -> Dict[str, any]:
        """
        Generate a single question on a specific topic
        
        Args:
            topic: Topic for the question
            difficulty: Difficulty level
            question_type: Type of question
            
        Returns:
            Dictionary containing the question
        """
        
        prompt = f"""Create ONE {difficulty} difficulty {question_type} question about: {topic}

Return in this JSON format:
{{
  "question": "Question text?",
  "type": "{question_type}",
  "options": ["A) Option 1", "B) Option 2", "C) Option 3", "D) Option 4"],
  "correct_answer": "Correct option",
  "explanation": "Detailed step-by-step solution",
  "hints": ["Hint 1", "Hint 2"]
}}

Make it exam-relevant and include a thorough explanation."""

        try:
            response = self._get_ai_response(prompt)
            
            # Clean and parse JSON
            response = response.strip()
            if response.startswith('```json'):
                response = response[7:]
            if response.startswith('```'):
                response = response[3:]
            if response.endswith('```'):
                response = response[:-3]
            
            question = json.loads(response.strip())
            
            return {
                'success': True,
                'question': question
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _get_ai_response(self, prompt: str) -> str:
        """Get response from AI client"""
        if hasattr(self.ai_client, 'chat'):
            # OpenAI
            response = self.ai_client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are an expert at creating educational practice questions with detailed solutions."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=3000
            )
            return response.choices[0].message.content
        else:
            # Anthropic
            response = self.ai_client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=3000,
                messages=[{"role": "user", "content": prompt}],
                system="You are an expert at creating educational practice questions with detailed solutions."
            )
            return response.content[0].text
