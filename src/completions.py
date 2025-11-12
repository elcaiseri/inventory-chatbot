from typing import List, Dict, Any
import os

# ============================================================================
# OpenAI Integration
# ============================================================================

class OpenAIService:
    """Service for interacting with OpenAI API"""
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        self.model = os.getenv("MODEL_NAME", "gpt-4o-mini")
        
        # Initialize OpenAI client
        from openai import OpenAI
        self.client = OpenAI(api_key=self.api_key)
    
    def create_chat_completion(
            self,
            messages: List[Dict[str, str]]
        ) -> Dict[str, Any]:
        """Call OpenAI chat completion API using official SDK"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                timeout=30,
            )
            
            # Convert response to dict format for consistency
            return {
                "choices": [
                    {
                        "message": {
                            "content": response.choices[0].message.content,
                            "role": response.choices[0].message.role
                        }
                    }
                ],
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")
