"""
Inventory Chatbot with Present Query Output
Senior Machine Learning Engineer Assignment
"""
import os
import json
import time
import re
from typing import Dict, List, Optional, Any
from datetime import datetime
from collections import defaultdict

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
import uvicorn


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


# ============================================================================
# SQL Query Mapping
# ============================================================================

class SQLQueryMapper:
    """Maps user intents to SQL queries based on inventory schema"""
    
    def __init__(self):
        self.query_patterns = self._build_query_patterns()
    
    def _build_query_patterns(self) -> List[Dict[str, Any]]:
        """Define all supported query patterns with their SQL mappings"""
        return [
            {
                "patterns": [
                    r"how many assets",
                    r"total assets",
                    r"count.*assets",
                    r"number of assets"
                ],
                "sql": "SELECT COUNT(*) AS AssetCount FROM Assets WHERE Status <> 'Disposed';",
                "answer_template": "You have {AssetCount} assets in your inventory.",
                "intent": "asset_count_total"
            },
            {
                "patterns": [
                    r"how many assets.*by site",
                    r"assets.*per site",
                    r"asset count.*site",
                    r"breakdown.*site",
                    r"show.*assets.*by site",
                    r"show.*assets.*site",
                    r"list.*assets.*by site",
                    r"assets.*by site"
                ],
                "sql": """SELECT s.SiteName, COUNT(*) AS AssetCount 
FROM Assets a 
JOIN Sites s ON s.SiteId = a.SiteId 
WHERE a.Status <> 'Disposed' 
GROUP BY s.SiteName 
ORDER BY AssetCount DESC;""",
                "answer_template": "Here's the asset count by site: {results}",
                "intent": "asset_count_by_site"
            },
            {
                "patterns": [
                    r"total value.*assets.*site",
                    r"asset value.*site",
                    r"value.*assets.*per site"
                ],
                "sql": """SELECT s.SiteName, SUM(ISNULL(a.Cost, 0)) AS TotalValue
FROM Assets a
JOIN Sites s ON s.SiteId = a.SiteId
WHERE a.Status <> 'Disposed'
GROUP BY s.SiteName
ORDER BY TotalValue DESC;""",
                "answer_template": "Here's the total asset value by site: {results}",
                "intent": "asset_value_by_site"
            },
            {
                "patterns": [
                    r"assets purchased.*this year",
                    r"assets.*bought.*year",
                    r"how many.*purchased.*current year"
                ],
                "sql": """SELECT COUNT(*) AS AssetCount
FROM Assets
WHERE YEAR(PurchaseDate) = YEAR(GETDATE())
AND Status <> 'Disposed';""",
                "answer_template": "You purchased {AssetCount} assets this year.",
                "intent": "assets_purchased_this_year"
            },
            {
                "patterns": [
                    r"which vendor.*most assets",
                    r"vendor.*supplied.*most",
                    r"top vendor.*assets"
                ],
                "sql": """SELECT TOP 1 v.VendorName, COUNT(*) AS AssetCount
FROM Assets a
JOIN Vendors v ON v.VendorId = a.VendorId
WHERE a.Status <> 'Disposed'
GROUP BY v.VendorName
ORDER BY AssetCount DESC;""",
                "answer_template": "The vendor that supplied the most assets is {VendorName} with {AssetCount} assets.",
                "intent": "top_vendor_by_assets"
            },
            {
                "patterns": [
                    r"total billed.*last quarter",
                    r"bills.*last quarter",
                    r"amount billed.*quarter"
                ],
                "sql": """SELECT SUM(TotalAmount) AS TotalBilled
FROM Bills
WHERE BillDate >= DATEADD(QUARTER, DATEDIFF(QUARTER, 0, GETDATE()) - 1, 0)
AND BillDate < DATEADD(QUARTER, DATEDIFF(QUARTER, 0, GETDATE()), 0);""",
                "answer_template": "The total billed amount for the last quarter is ${TotalBilled:,.2f}.",
                "intent": "total_billed_last_quarter"
            },
            {
                "patterns": [
                    r"how many.*open.*purchase orders",
                    r"pending.*purchase orders",
                    r"open.*po"
                ],
                "sql": """SELECT COUNT(*) AS OpenPOCount
FROM PurchaseOrders
WHERE Status = 'Open';""",
                "answer_template": "There are {OpenPOCount} open purchase orders currently pending.",
                "intent": "open_purchase_orders"
            },
            {
                "patterns": [
                    r"assets.*by category",
                    r"breakdown.*category",
                    r"assets.*per category",
                    r"show.*assets.*category",
                    r"list.*assets.*category"
                ],
                "sql": """SELECT Category, COUNT(*) AS AssetCount
FROM Assets
WHERE Status <> 'Disposed'
GROUP BY Category
ORDER BY AssetCount DESC;""",
                "answer_template": "Here's the breakdown of assets by category: {results}",
                "intent": "assets_by_category"
            },
            {
                "patterns": [
                    r"sales orders.*customer.*last month",
                    r"how many.*sales orders.*month",
                    r"so.*created.*customer"
                ],
                "sql": """SELECT c.CustomerName, COUNT(*) AS SOCount
FROM SalesOrders so
JOIN Customers c ON c.CustomerId = so.CustomerId
WHERE so.SODate >= DATEADD(MONTH, -1, GETDATE())
GROUP BY c.CustomerName
ORDER BY SOCount DESC;""",
                "answer_template": "Here are the sales orders created for customers last month: {results}",
                "intent": "sales_orders_by_customer_last_month"
            },
            {
                "patterns": [
                    r"list.*vendors",
                    r"show.*vendors",
                    r"all vendors"
                ],
                "sql": """SELECT VendorCode, VendorName, Email, Phone
FROM Vendors
WHERE IsActive = 1
ORDER BY VendorName;""",
                "answer_template": "Here are all active vendors: {results}",
                "intent": "list_vendors"
            },
            {
                "patterns": [
                    r"list.*customers",
                    r"show.*customers",
                    r"all customers"
                ],
                "sql": """SELECT CustomerCode, CustomerName, Email, Phone
FROM Customers
WHERE IsActive = 1
ORDER BY CustomerName;""",
                "answer_template": "Here are all active customers: {results}",
                "intent": "list_customers"
            },
            {
                "patterns": [
                    r"list.*sites",
                    r"show.*sites",
                    r"all sites"
                ],
                "sql": """SELECT SiteCode, SiteName, City, Country
FROM Sites
WHERE IsActive = 1
ORDER BY SiteName;""",
                "answer_template": "Here are all active sites: {results}",
                "intent": "list_sites"
            }
        ]
    
    def match_intent(self, message: str) -> Optional[Dict[str, Any]]:
        """Match user message to a query pattern"""
        message_lower = message.lower().strip()
        
        for pattern_def in self.query_patterns:
            for pattern in pattern_def["patterns"]:
                if re.search(pattern, message_lower):
                    return {
                        "sql": pattern_def["sql"],
                        "answer_template": pattern_def["answer_template"],
                        "intent": pattern_def["intent"]
                    }
        
        return None


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


# ============================================================================
# Session Management
# ============================================================================

class SessionManager:
    """In-memory session management for conversations"""
    
    def __init__(self):
        self.sessions: Dict[str, List[Dict[str, str]]] = defaultdict(list)
    
    def add_message(self, session_id: str, role: str, content: str):
        """Add a message to session history"""
        self.sessions[session_id].append({
            "role": role,
            "content": content
        })
    
    def get_messages(self, session_id: str) -> List[Dict[str, str]]:
        """Get all messages for a session"""
        return self.sessions[session_id]
    
    def clear_session(self, session_id: str):
        """Clear a session"""
        if session_id in self.sessions:
            del self.sessions[session_id]


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
                enhanced_message = f"{message}\n\n[System: This maps to intent '{intent_match['intent']}']"
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


# ============================================================================
# FastAPI Application
# ============================================================================

app = FastAPI(
    title="Inventory Chatbot API",
    description="AI-powered inventory management chatbot with SQL query output",
    version="1.0.0"
)

# Initialize chat service
chat_service = ChatService()


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
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Inventory Chatbot</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        
        .container {
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            width: 100%;
            max-width: 900px;
            height: 90vh;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 24px;
            margin-bottom: 5px;
        }
        
        .header p {
            font-size: 14px;
            opacity: 0.9;
        }
        
        .chat-container {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            background: #f5f5f5;
        }
        
        .message {
            margin-bottom: 20px;
            animation: fadeIn 0.3s ease-in;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .message-user {
            text-align: right;
        }
        
        .message-assistant {
            text-align: left;
        }
        
        .message-bubble {
            display: inline-block;
            max-width: 70%;
            padding: 12px 16px;
            border-radius: 12px;
            word-wrap: break-word;
        }
        
        .message-user .message-bubble {
            background: #667eea;
            color: white;
        }
        
        .message-assistant .message-bubble {
            background: white;
            color: #333;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        
        .sql-query {
            background: #282c34;
            color: #abb2bf;
            padding: 12px;
            border-radius: 8px;
            margin-top: 10px;
            font-family: 'Courier New', monospace;
            font-size: 13px;
            overflow-x: auto;
            white-space: pre-wrap;
        }
        
        .metadata {
            font-size: 11px;
            color: #888;
            margin-top: 5px;
            display: inline-block;
        }
        
        .input-container {
            padding: 20px;
            background: white;
            border-top: 1px solid #e0e0e0;
        }
        
        .input-wrapper {
            display: flex;
            gap: 10px;
        }
        
        #messageInput {
            flex: 1;
            padding: 12px 16px;
            border: 2px solid #e0e0e0;
            border-radius: 24px;
            font-size: 14px;
            outline: none;
            transition: border-color 0.3s;
        }
        
        #messageInput:focus {
            border-color: #667eea;
        }
        
        #sendButton {
            padding: 12px 24px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 24px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        
        #sendButton:hover:not(:disabled) {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        
        #sendButton:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        
        .examples {
            padding: 10px 20px;
            background: #f9f9f9;
            border-top: 1px solid #e0e0e0;
            font-size: 12px;
            color: #666;
        }
        
        .examples strong {
            color: #333;
        }
        
        .example-link {
            color: #667eea;
            cursor: pointer;
            text-decoration: underline;
            margin: 0 5px;
        }
        
        .example-link:hover {
            color: #764ba2;
        }
        
        .loading {
            display: inline-block;
            width: 12px;
            height: 12px;
            border: 2px solid #f3f3f3;
            border-top: 2px solid #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏭 Inventory Management Chatbot</h1>
            <p>Ask questions about your inventory and see the SQL queries</p>
        </div>
        
        <div class="chat-container" id="chatContainer">
            <div class="message message-assistant">
                <div class="message-bubble">
                    👋 Welcome! I can help you query your inventory database. 
                    Ask me about assets, vendors, customers, purchase orders, or sales orders.
                </div>
            </div>
        </div>
        
        <div class="examples">
            <strong>Try:</strong>
            <span class="example-link" onclick="sendExample('How many assets do I have?')">How many assets?</span> •
            <span class="example-link" onclick="sendExample('Show me assets by site')">Assets by site</span> •
            <span class="example-link" onclick="sendExample('Which vendor supplied the most assets?')">Top vendor</span> •
            <span class="example-link" onclick="sendExample('How many open purchase orders?')">Open POs</span>
        </div>
        
        <div class="input-container">
            <div class="input-wrapper">
                <input 
                    type="text" 
                    id="messageInput" 
                    placeholder="Ask about your inventory..."
                    onkeypress="handleKeyPress(event)"
                />
                <button id="sendButton" onclick="sendMessage()">Send</button>
            </div>
        </div>
    </div>

    <script>
        // Generate a unique session ID
        const sessionId = 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        
        function handleKeyPress(event) {
            if (event.key === 'Enter' && !event.shiftKey) {
                event.preventDefault();
                sendMessage();
            }
        }
        
        function sendExample(message) {
            document.getElementById('messageInput').value = message;
            sendMessage();
        }
        
        async function sendMessage() {
            const input = document.getElementById('messageInput');
            const sendButton = document.getElementById('sendButton');
            const message = input.value.trim();
            
            if (!message) return;
            
            // Add user message to chat
            addMessage(message, 'user');
            
            // Clear input and disable button
            input.value = '';
            sendButton.disabled = true;
            
            // Show loading indicator
            const loadingId = addLoadingMessage();
            
            try {
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        session_id: sessionId,
                        message: message,
                        context: {}
                    })
                });
                
                const data = await response.json();
                
                // Remove loading indicator
                removeMessage(loadingId);
                
                // Add assistant response
                addAssistantMessage(data);
                
            } catch (error) {
                removeMessage(loadingId);
                addMessage('Error: ' + error.message, 'assistant');
            } finally {
                sendButton.disabled = false;
                input.focus();
            }
        }
        
        function addMessage(text, sender) {
            const chatContainer = document.getElementById('chatContainer');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message message-${sender}`;
            messageDiv.innerHTML = `
                <div class="message-bubble">${escapeHtml(text)}</div>
            `;
            chatContainer.appendChild(messageDiv);
            scrollToBottom();
        }
        
        function addLoadingMessage() {
            const chatContainer = document.getElementById('chatContainer');
            const messageDiv = document.createElement('div');
            const loadingId = 'loading_' + Date.now();
            messageDiv.id = loadingId;
            messageDiv.className = 'message message-assistant';
            messageDiv.innerHTML = `
                <div class="message-bubble">
                    <span class="loading"></span>
                </div>
            `;
            chatContainer.appendChild(messageDiv);
            scrollToBottom();
            return loadingId;
        }
        
        function removeMessage(id) {
            const element = document.getElementById(id);
            if (element) {
                element.remove();
            }
        }
        
        function addAssistantMessage(data) {
            const chatContainer = document.getElementById('chatContainer');
            const messageDiv = document.createElement('div');
            messageDiv.className = 'message message-assistant';
            
            let html = `<div class="message-bubble">${escapeHtml(data.natural_language_answer)}`;
            
            if (data.sql_query && !data.sql_query.startsWith('-- No matching')) {
                html += `<div class="sql-query"><strong>SQL Query:</strong>\n${escapeHtml(data.sql_query)}</div>`;
            }
            
            html += `<div class="metadata">
                ⚡ ${data.latency_ms}ms • 
                🎯 ${data.token_usage.total_tokens} tokens • 
                📊 ${data.provider} (${data.model})
            </div>`;
            
            html += '</div>';
            messageDiv.innerHTML = html;
            chatContainer.appendChild(messageDiv);
            scrollToBottom();
        }
        
        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
        
        function scrollToBottom() {
            const chatContainer = document.getElementById('chatContainer');
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }
        
        // Focus input on load
        document.getElementById('messageInput').focus();
    </script>
</body>
</html>
    """
    return HTMLResponse(content=html_content)


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


def main():
    """Run the application"""
    port = int(os.getenv("PORT", "8000"))
    host = os.getenv("HOST", "0.0.0.0")
    
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║        Inventory Chatbot with Present Query Output          ║
╚══════════════════════════════════════════════════════════════╝

🚀 Starting server on http://{host}:{port}
📊 Provider: OpenAI
🔑 API Key: {'✓ Configured' if os.getenv('OPENAI_API_KEY') else '✗ Missing'}
🤖 Model: {os.getenv('MODEL_NAME', 'gpt-5')}

Press Ctrl+C to stop the server
    """)
    
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()
