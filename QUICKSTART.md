# Quick Start Guide

Get the Inventory Chatbot running in 5 minutes!

## 📋 Prerequisites

- Python 3.12 or higher
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))

## 🚀 Installation Steps

### 1. Navigate to Project Directory
```bash
cd /Users/kassem/Desktop/asap
```

### 2. Install Dependencies
```bash
pip install -e .
```

This will install:
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `openai` - OpenAI SDK
- `pydantic` - Data validation

### 3. Configure Environment

Copy the example environment file:
```bash
cp .env.example .env
```

Edit `.env` and add your OpenAI API key:
```bash
# Required
OPENAI_API_KEY=sk-your-actual-api-key-here

# Optional (defaults shown)
MODEL_NAME=gpt-3.5-turbo
HOST=0.0.0.0
PORT=8000
```

### 4. Run the Application

```bash
python main.py
```

You should see:
```
╔══════════════════════════════════════════════════════════════╗
║        Inventory Chatbot with Present Query Output          ║
╚══════════════════════════════════════════════════════════════╝

🚀 Starting server on http://0.0.0.0:8000
📊 Provider: OpenAI
🔑 API Key: ✓ Configured
🤖 Model: gpt-3.5-turbo

Press Ctrl+C to stop the server
```

### 5. Access the Web UI

Open your browser to:
```
http://localhost:8000
```

## 💬 Try These Queries

In the chat interface, try asking:

- "How many assets do I have?"
- "Show me assets by site"
- "Which vendor supplied the most assets?"
- "List all vendors"
- "How many open purchase orders?"

Each response will show:
- Natural language answer
- SQL query that would be executed
- Performance metrics (latency, tokens, model)

## 🧪 Test the API

In a new terminal window:

```bash
python test_api.py
```

Or test manually with curl:
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test-123",
    "message": "How many assets do I have?",
    "context": {}
  }'
```

## 🔧 Using Different Models

To use GPT-4 or other models, update `.env`:

```bash
# For GPT-4
MODEL_NAME=gpt-4

# For GPT-4 Turbo
MODEL_NAME=gpt-4-turbo-preview

# For GPT-3.5 Turbo (default, most cost-effective)
MODEL_NAME=gpt-3.5-turbo
```

Restart the server for changes to take effect.

## 🐛 Troubleshooting

### "OPENAI_API_KEY environment variable is required"
- Make sure you created the `.env` file
- Check that your API key is correctly set
- Verify no extra spaces or quotes around the key

### "Connection refused" or cannot access localhost:8000
- Check if port 8000 is already in use
- Try changing PORT in `.env` to 8001 or another port
- Ensure the server started successfully (check terminal output)

### API returns errors
- Verify your OpenAI API key is valid and has credits
- Check your internet connection
- Review the terminal output for detailed error messages

## 📚 Next Steps

- Read [README.md](README.md) for complete documentation
- Review [IMPLEMENTATION.md](IMPLEMENTATION.md) for technical details
- Explore the code in `main.py` to understand the implementation

## 💡 Tips

- **Session Management**: Each browser session gets a unique ID to maintain conversation context
- **SQL Queries**: The system maps natural language to predefined SQL patterns
- **No Database Required**: This is a demo that shows SQL queries without executing them
- **Cost-Effective**: Uses gpt-3.5-turbo by default (very low cost per request)

## 🛑 Stopping the Server

Press `Ctrl+C` in the terminal where the server is running.

---

That's it! You're ready to explore the Inventory Chatbot. 🎉
