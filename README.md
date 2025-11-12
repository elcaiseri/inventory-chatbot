# Inventory Chatbot with "Present Query" Output

A minimal AI-powered inventory management chatbot that answers business questions and returns the exact SQL query for each answer.

## 🎯 Features

- **Natural Language Interface**: Ask questions about your inventory in plain English
- **SQL Query Transparency**: See the exact SQL query that would be executed for each question
- **Session Management**: Maintains conversation context across multiple questions
- **OpenAI Integration**: Powered by GPT models for intelligent responses
- **Web UI**: Simple, responsive chat interface
- **REST API**: Clean REST API for integration
- **Zero External Dependencies**: Only uses standard library + Pydantic & FastAPI

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- OpenAI API key

### Installation

1. Clone the repository:
```bash
cd /Users/kassem/Desktop/asap
```

2. Install dependencies:
```bash
pip install -e .
```

3. Configure environment variables:
```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

4. Run the application:
```bash
python main.py
```

5. Open your browser to `http://localhost:8000`

## 🔧 Configuration

Environment variables in `.env`:

```bash
# Required
OPENAI_API_KEY=sk-...

# Optional
MODEL_NAME=gpt-3.5-turbo  # or gpt-4, gpt-4-turbo, etc.
HOST=0.0.0.0
PORT=8000
```

## 📡 API Reference

### POST /api/chat

Send a message and receive an answer with SQL query.

**Request:**
```json
{
  "session_id": "unique-session-id",
  "message": "How many assets do I have?",
  "context": {}
}
```

**Response:**
```json
{
  "natural_language_answer": "You have 150 assets in your inventory.",
  "sql_query": "SELECT COUNT(*) AS AssetCount FROM Assets WHERE Status <> 'Disposed';",
  "token_usage": {
    "prompt_tokens": 120,
    "completion_tokens": 25,
    "total_tokens": 145
  },
  "latency_ms": 850,
  "provider": "openai",
  "model": "gpt-3.5-turbo",
  "status": "ok"
}
```

### GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-11-12T10:30:00.000000"
}
```

## 💬 Supported Queries

The chatbot supports various inventory-related questions:

### Assets
- "How many assets do I have?"
- "Show me assets by site"
- "What is the total value of assets per site?"
- "How many assets were purchased this year?"
- "Show me assets by category"

### Vendors & Customers
- "Which vendor supplied the most assets?"
- "List all vendors"
- "List all customers"

### Purchase Orders
- "How many open purchase orders are currently pending?"

### Sales Orders
- "How many sales orders were created for customers last month?"

### Bills
- "What is the total billed amount for the last quarter?"

### Sites & Locations
- "List all sites"

## 🗄️ Database Schema

The system maps to a SQL Server schema with the following tables:

- **Customers**: Customer information and billing details
- **Vendors**: Vendor information and contacts
- **Sites**: Physical locations/warehouses
- **Locations**: Specific locations within sites
- **Items**: Item catalog
- **Assets**: Physical assets with tracking information
- **Bills**: Accounts payable
- **PurchaseOrders** / **PurchaseOrderLines**: PO management
- **SalesOrders** / **SalesOrderLines**: SO management
- **AssetTransactions**: Asset movement history

See `main.py` for complete schema details.

## 🏗️ Architecture

```
┌─────────────────┐
│   Web UI        │
│  (HTML/JS)      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  FastAPI        │
│  REST API       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  ChatService    │
│  - Session Mgmt │
│  - SQL Mapping  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  OpenAI API     │
│  (urllib)       │
└─────────────────┘
```

## 🧪 Testing

### Manual Testing

```bash
# Start the server
python main.py

# In another terminal, test the API
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test-123",
    "message": "How many assets do I have?",
    "context": {}
  }'
```

### Using the Test Script

```bash
python test_api.py
```

## 📝 Implementation Notes

### Design Decisions

1. **No External Libraries (except required)**: Uses Python's `urllib` for HTTP instead of `requests` or OpenAI SDK
2. **In-Memory Sessions**: Simple dictionary-based session storage (suitable for demo, would use Redis in production)
3. **Pattern Matching**: Regex-based intent matching for SQL query selection
4. **Embedded UI**: Single HTML page served by FastAPI (no separate frontend build)

### SQL Query Mapping

The system uses a pattern-matching approach:
- User messages are matched against predefined regex patterns
- Each pattern maps to a specific SQL query template
- The LLM provides natural language answers while the system provides the SQL

### Limitations

- In-memory session storage (lost on restart)
- SQL queries are templates, not executed against a real database
- Pattern matching is simple (could be enhanced with semantic similarity)
- No authentication/authorization

## 🚢 Deployment

### Using Docker

```bash
# Build
docker build -t inventory-chatbot .

# Run
docker run -p 8000:8000 \
  -e OPENAI_API_KEY=your-key \
  inventory-chatbot
```

### Using systemd (Linux)

```bash
# Copy the service file
sudo cp inventory-chatbot.service /etc/systemd/system/

# Enable and start
sudo systemctl enable inventory-chatbot
sudo systemctl start inventory-chatbot
```

## 📄 License

MIT

## 👤 Author

Senior ML Engineer Assignment - November 2025
