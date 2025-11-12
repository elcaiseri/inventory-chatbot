"""
Inventory Chatbot with Present Query Output
Senior Machine Learning Engineer Assignment
"""
import os
from datetime import datetime

from fastapi import FastAPI, staticfiles
from fastapi.responses import HTMLResponse
import uvicorn

from src.chat import ChatService
from src.models import ChatRequest, ChatResponse

# ============================================================================
# FastAPI Application
# ============================================================================

# Initialize chat service
chat_service = None

def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    global chat_service
    # Startup
    chat_service = ChatService()

    yield

    # Shutdown
    chat_service.close()
    


app = FastAPI(
    title="Inventory Chatbot API",
    description="AI-powered inventory management chatbot with SQL query output",
    version="1.0.0",
    lifespan=lifespan
)

app.mount("/static", staticfiles.StaticFiles(directory="src/static"), name="static")

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Process a chat message and return natural language answer with SQL query.
    
    The endpoint maintains conversation state per session and returns the
    SQL query that would be executed to answer the question.
    """
    return chat_service.process_message(
        session_id=request.session_id,
        message=request.message,
        context=request.context
    )


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the chat UI"""
    with open("src/static/index.html") as f:
        html_content = f.read()

    return HTMLResponse(content=html_content)


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


def main():
    """Run the application"""
    port = int(os.getenv("PORT", "8000"))
    host = os.getenv("HOST", "0.0.0.0")
    
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()
