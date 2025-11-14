from typing import Dict, Any, Optional

from src.completions import OpenAIService
from src.session import SessionManager
from src.query import SQLQueryMapper
from src.models import ChatResponse, TokenUsage

import time

# ============================================================================
# Chat Service
# ============================================================================

class ChatService:
    """Main chat service orchestrating LLM and SQL query generation"""
    
    SYSTEM_PROMPT = """You are a helpful inventory management assistant. 
You help users query their inventory database which includes assets, customers, vendors, 
sites, locations, bills, purchase orders, and sales orders.

When a user asks a question about their inventory, provide a clear, concise answer.
Focus on being helpful and accurate. Keep responses brief and to the point."""
    
    def __init__(self):
        self.openai_service = OpenAIService()
        self.session_manager = SessionManager()
        self.sql_mapper = SQLQueryMapper()
    
    def process_message(
        self,
        session_id: str,
        message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> ChatResponse:
        """Process a chat message and return response with SQL query"""
        start_time = time.time()
        
        try:
            # Match intent to SQL query
            intent_match = self.sql_mapper.match_intent(message)
            
            if intent_match:
                sql_query = intent_match["sql"]
                answer_template = intent_match["answer_template"]
            else:
                sql_query = "-- No matching SQL query pattern found for this question"
                answer_template = "I'll help you with that inventory question."
            
            # Add user message to session
            self.session_manager.add_message(session_id, "user", message)
            
            # Build messages for OpenAI
            messages = [{"role": "system", "content": self.SYSTEM_PROMPT}]
            messages.extend(self.session_manager.get_messages(session_id))
            
            # Add context about the matched query if available
            if intent_match:
                enhanced_message = (
                    f"{message}\n\n"
                    f"[System: intent='{intent_match['intent']}'. "
                    f"SQL query to be executed: {intent_match['sql']}. "
                    f"Answer template hint: {intent_match['answer_template']}. "
                    "Decide whether the template is useful based on the SQL result & User Message. Modify if needed. "
                    "Respond with a concise, high‑level answer as if the query executed. "
                    "Do not invent specific numbers unless the user provided them. "
                    "If results are unknown, describe what the result set would contain (entities, counts). "
                    "Do not show SQL. Keep under 60 words.]"
                )
                messages[-1]["content"] = enhanced_message
            
            # Call OpenAI
            response = self.openai_service.create_chat_completion(messages)
            
            # Extract response
            assistant_message = response["choices"][0]["message"]["content"]
            usage = response["usage"]
            
            # Add assistant response to session
            self.session_manager.add_message(session_id, "assistant", assistant_message)
            
            # Calculate latency
            latency_ms = int((time.time() - start_time) * 1000)
            
            return ChatResponse(
                natural_language_answer=assistant_message,
                sql_query=sql_query,
                token_usage=TokenUsage(
                    prompt_tokens=usage["prompt_tokens"],
                    completion_tokens=usage["completion_tokens"],
                    total_tokens=usage["total_tokens"]
                ),
                latency_ms=latency_ms,
                provider="openai",
                model=self.openai_service.model,
                status="ok"
            )
            
        except Exception as e:
            latency_ms = int((time.time() - start_time) * 1000)
            
            return ChatResponse(
                natural_language_answer=f"Error processing request: {str(e)}",
                sql_query="-- Error occurred",
                token_usage=TokenUsage(
                    prompt_tokens=0,
                    completion_tokens=0,
                    total_tokens=0
                ),
                latency_ms=latency_ms,
                provider="openai",
                model=self.openai_service.model,
                status="error"
            )

    def close(self):
        """Cleanup resources if needed"""
        return "ChatService closed."