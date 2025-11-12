from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

# ============================================================================
# Pydantic Models
# ============================================================================

class ChatRequest(BaseModel):
    session_id: str
    message: str
    context: Optional[Dict[str, Any]] = None


class TokenUsage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class ChatResponse(BaseModel):
    natural_language_answer: str
    sql_query: str
    token_usage: TokenUsage
    latency_ms: int
    provider: str
    model: str
    status: str