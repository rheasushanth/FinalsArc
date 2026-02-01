"""Concept explainer with adaptive difficulty"""
from typing import Dict, List, Optional


class ConceptExplainer:
    """Explains concepts with multiple approaches and adaptive difficulty"""
    
    def __init__(self, ai_client, model_name='openai/gpt-4o-mini'):
        """
        Initialize concept explainer
        
        Args:
            ai_client: AI client (OpenAI or Anthropic)
            model_name: Model name to use
        """
        self.ai_client = ai_client
        self.model_name = model_name
        self.explanation_history = []
    
    def explain_concept(
        self,
        question: str,
        context: Optional[str] = None,
        level: str = "intermediate",
        previous_attempts: Optional[List[str]] = None
    ) -> Dict[str, any]:
        """
        Explain a concept or answer a question
        
        Args:
            question: The student's question
            context: Relevant study material context
            level: Student level (beginner/intermediate/advanced)
            previous_attempts: Previous explanations that didn't work
            
        Returns:
            Dictionary containing the explanation
        """
        
        # Build context about previous attempts
        retry_context = ""
        if previous_attempts:
            retry_context = f"""
**Previous Explanations (student still confused):**
{chr(10).join(f"Attempt {i+1}: {attempt[:200]}..." for i, attempt in enumerate(previous_attempts[-2:]))}

The student is still confused, so try a DIFFERENT approach:
- Use simpler language
- More concrete examples
- Different analogies
- Break it down into smaller steps
"""

        context_section = f"""
**Relevant Study Material:**
{context[:2000]}
""" if context else ""

        prompt = f"""You are a patient, friendly Study Buddy helping a student understand a concept.

**Student's Question:**
{question}

**Student Level:** {level}

{context_section}

{retry_context}

**Provide a comprehensive explanation following this structure:**

## 🎯 Quick Answer
[1-2 sentence direct answer to their question]

## 📚 Simple Explanation
[Explain using everyday language, as if talking to someone new to this topic]
[Use short sentences and familiar words]

## 🔍 Detailed Explanation
[Now go deeper, step-by-step]
[Introduce technical terms gradually, always defining them]

**Step 1:** [First concept/step]
**Step 2:** [Second concept/step]
**Step 3:** [Continue as needed]

## 💡 Example
[Provide a concrete, worked example with real numbers or scenarios]
[Show all the steps]

## 🌍 Real-Life Analogy
[Compare to something from everyday experience]
[Make it relatable and memorable]

## ⭐ Key Points to Remember
- Most important point 1
- Most important point 2
- Most important point 3

## 🧠 Memory Trick
[Provide a mnemonic, rhyme, or mental model to remember this]

## ⚠️ Common Confusions
**Mistake:** [Common misunderstanding]
**Why it's wrong:** [Explanation]
**Correct way:** [Right approach]

## 🎓 Want to Go Deeper?
[Optional: Mention advanced connections or "what's next" for curious students]

---

**Guidelines:**
- Be warm and encouraging
- Never skip logical steps
- Define all technical terms when first used
- Use multiple examples if helpful
- Check understanding with mini-checkpoints
- If explaining math/formulas, show every step
- Use the specified emojis for sections
- Keep each paragraph short (2-4 sentences)

If the student asks for a simpler explanation, focus MORE on:
- Shorter sentences
- More familiar words
- More concrete examples
- More analogies
"""

        try:
            response = self._get_ai_response(prompt)
            
            # Store in history
            self.explanation_history.append({
                'question': question,
                'level': level,
                'response': response
            })
            
            return {
                'success': True,
                'explanation': response,
                'metadata': {
                    'level': level,
                    'has_context': context is not None,
                    'is_retry': previous_attempts is not None,
                    'word_count': len(response.split())
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def explain_simpler(self, original_explanation: str, question: str) -> Dict[str, any]:
        """
        Provide an even simpler explanation
        
        Args:
            original_explanation: The previous explanation
            question: Original question
            
        Returns:
            Simplified explanation
        """
        
        prompt = f"""A student asked: "{question}"

You provided this explanation:
{original_explanation[:1500]}

But the student is STILL confused and needs it explained MUCH simpler.

**Provide an extremely simple explanation:**

1. **Use the ELI5 (Explain Like I'm 5) approach**
   - Pretend you're explaining to a young child
   - Use only simple, everyday words
   - Very short sentences

2. **Use a concrete story or scenario**
   - Make it visual and tangible
   - Use familiar objects or situations

3. **Break it into tiny steps**
   - One small idea at a time
   - Check understanding after each step

4. **More analogies**
   - Compare to things everyone knows
   - Make it fun and memorable

**Remember:** This student is struggling, so be extra patient, extra clear, and extra encouraging!
"""

        try:
            response = self._get_ai_response(prompt)
            
            return {
                'success': True,
                'explanation': response,
                'metadata': {
                    'simplified': True,
                    'word_count': len(response.split())
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def provide_multiple_approaches(self, concept: str) -> Dict[str, any]:
        """
        Explain a concept using multiple different approaches
        
        Args:
            concept: The concept to explain
            
        Returns:
            Dictionary with multiple explanations
        """
        
        prompt = f"""Explain this concept in 3 DIFFERENT ways:

**Concept:** {concept}

**Approach 1: Visual/Spatial**
[Explain using visual descriptions, diagrams in words, spatial relationships]

**Approach 2: Logical/Step-by-Step**
[Explain using logical reasoning, cause-and-effect, step-by-step breakdown]

**Approach 3: Analogy/Story**
[Explain using a relatable story or extended analogy]

Make each approach complete and self-contained. Students learn differently, so these different perspectives should help!
"""

        try:
            response = self._get_ai_response(prompt)
            
            return {
                'success': True,
                'approaches': response,
                'metadata': {
                    'num_approaches': 3,
                    'word_count': len(response.split())
                }
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
                    {"role": "system", "content": "You are a patient, friendly tutor who excels at explaining complex concepts in simple, clear ways. You never assume prior knowledge and always break things down step-by-step."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=3000
            )
            return response.choices[0].message.content
        else:
            # Anthropic
            response = self.ai_client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=3000,
                messages=[{"role": "user", "content": prompt}],
                system="You are a patient, friendly tutor who excels at explaining complex concepts in simple, clear ways. You never assume prior knowledge and always break things down step-by-step."
            )
            return response.content[0].text
