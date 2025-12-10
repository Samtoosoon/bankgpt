# groq_integration.py - Groq API integration for conversation
"""
Groq API integration for fast, high-quality LLM responses.
Using Groq's Mixtral-8x7b model for loan conversation.
"""

import os
from typing import Optional
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Groq client
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
if GROQ_API_KEY:
    CLIENT = Groq(api_key=GROQ_API_KEY)
else:
    CLIENT = None


class GroqClient:
    """Wrapper for Groq API interactions."""
    
    @staticmethod
    def is_available() -> bool:
        """Check if Groq API is configured."""
        return CLIENT is not None
    
    @staticmethod
    def generate_text(prompt: str, max_tokens: int = 500) -> Optional[str]:
        """
        Generate text using Groq API.
        
        Args:
            prompt: The prompt to send to Groq
            max_tokens: Maximum tokens in response
            
        Returns:
            Generated text or None if error
        """
        if not GroqClient.is_available():
            return None
        
        try:
            message = CLIENT.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model="llama-3.3-70b-versatile",  # Current active model
                max_tokens=max_tokens,
                temperature=0.7,
            )
            return message.choices[0].message.content
        except Exception as e:
            print(f"Groq API error: {e}")
            return None
