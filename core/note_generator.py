"""Study notes generator with structured formatting"""
from typing import Dict, List, Optional


class NoteGenerator:
    """Generates structured study notes from content"""
    
    def __init__(self, ai_client, model_name='openai/gpt-4o-mini'):
        """
        Initialize note generator
        
        Args:
            ai_client: AI client (OpenAI or Anthropic)
            model_name: Model name to use
        """
        self.ai_client = ai_client
        self.model_name = model_name
    
    def generate_notes(
        self,
        content: str,
        subject: Optional[str] = None,
        level: Optional[str] = "intermediate",
        focus: Optional[str] = "concept-oriented"
    ) -> Dict[str, any]:
        """
        Generate comprehensive study notes from content
        
        Args:
            content: The study material content
            subject: Subject area (e.g., "Mathematics", "Biology")
            level: Academic level (beginner/intermediate/advanced)
            focus: Focus type (concept-oriented/exam-oriented)
            
        Returns:
            Dictionary containing structured notes
        """
        
        prompt = f"""You are an expert Study Buddy and Personal Tutor. Your job is to transform the following study material into clear, comprehensive study notes.

**Study Material:**
{content}

**Student Level:** {level}
**Subject:** {subject or "General"}
**Focus:** {focus}

**Generate study notes following this structure:**

1. **Main Topic/Chapter Title**

2. **Key Concepts Overview** (Brief introduction)

3. **Detailed Sections** (For each major concept):
   ### Concept Name
   
   **Simple Definition:**
   [Easy-to-understand definition in plain language]
   
   **Detailed Explanation:**
   [Step-by-step breakdown, assuming beginner knowledge]
   [Use simple language first, then introduce technical terms]
   
   **Example:**
   [Concrete example with real numbers/scenarios]
   
   **Real-Life Analogy:**
   [Relatable comparison to everyday experience]
   
   ⭐ **Important Points:**
   - Key point 1
   - Key point 2
   
   🧠 **Formula/Keywords:**
   [Any formulas, definitions, or key terms to memorize]
   
   ⚠️ **Common Mistakes:**
   - Mistake 1 and why it's wrong
   - Mistake 2 and how to avoid it

4. **Summary (TL;DR)**
   [2-3 sentence recap of main ideas]

5. **Memory Trick**
   [Mnemonic device, analogy, or mental model to remember this]

6. **Exam Tips** (if exam-oriented focus)
   - Question types to expect
   - What examiners look for

**Guidelines:**
- Use clear headings and subheadings
- Use bullet points for lists
- Keep paragraphs short (2-4 sentences)
- Define every technical term when first used
- Include step-by-step reasoning
- Use the specified emojis (⭐⚠️🧠) for highlights
- Be friendly and encouraging
- Assume student may be learning this for the first time
"""

        try:
            response = self._get_ai_response(prompt)
            
            return {
                'success': True,
                'notes': response,
                'metadata': {
                    'subject': subject,
                    'level': level,
                    'focus': focus,
                    'word_count': len(response.split())
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def generate_section_notes(
        self,
        section_content: str,
        section_title: str,
        subject: Optional[str] = None,
        level: Optional[str] = "intermediate"
    ) -> str:
        """
        Generate notes for a specific section
        
        Args:
            section_content: Content of the section
            section_title: Title of the section
            subject: Subject area
            level: Academic level
            
        Returns:
            Formatted notes for the section
        """
        
        prompt = f"""Generate detailed study notes for this specific section:

**Section Title:** {section_title}
**Subject:** {subject or "General"}
**Student Level:** {level}

**Content:**
{section_content}

Provide:
1. Simple definition/introduction
2. Step-by-step detailed explanation (assume beginner)
3. At least one concrete example
4. A real-life analogy
5. ⭐ Important points to remember
6. 🧠 Key formulas/terms
7. ⚠️ Common mistakes
8. Brief summary
9. Memory trick

Be thorough but clear. Use simple language first, then technical terms."""

        try:
            return self._get_ai_response(prompt)
        except Exception as e:
            return f"Error generating notes for section '{section_title}': {str(e)}"
    
    def _get_ai_response(self, prompt: str) -> str:
        """
        Get response from AI client
        
        Args:
            prompt: The prompt to send
            
        Returns:
            AI response text
        """
        # This will be implemented based on the AI client type
        # Placeholder implementation
        if hasattr(self.ai_client, 'chat'):
            # OpenAI style
            response = self.ai_client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are an expert study tutor who creates clear, structured, and comprehensive study notes."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=4000
            )
            return response.choices[0].message.content
        else:
            # Anthropic style
            response = self.ai_client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=4000,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                system="You are an expert study tutor who creates clear, structured, and comprehensive study notes."
            )
            return response.content[0].text
