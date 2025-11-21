"""
Test script for Inventory Chatbot API
"""

import json
import urllib.error
import urllib.request
from typing import Any, Dict


def test_chat_api(base_url: str = "http://localhost:8000"):
    """Test the chat API with various queries"""

    test_queries = [
        "How many assets do I have?",
        "Show me assets by site",
        "What is the total value of assets per site?",
        "Which vendor supplied the most assets?",
        "How many open purchase orders are pending?",
        "List all vendors",
        "Show me assets by category",
    ]

    session_id = f"test_session_{id(test_queries)}"

    print("=" * 70)
    print("INVENTORY CHATBOT API TEST")
    print("=" * 70)
    print(f"\nBase URL: {base_url}")
    print(f"Session ID: {session_id}\n")

    for i, query in enumerate(test_queries, 1):
        print(f"\n[Test {i}/{len(test_queries)}]")
        print(f"Query: {query}")
        print("-" * 70)

        try:
            result = call_chat_api(base_url, session_id, query)

            if result["status"] == "ok":
                print(f"✓ Status: {result['status']}")
                print(f"\nAnswer: {result['natural_language_answer']}")
                print(f"\nSQL Query:\n{result['sql_query']}")
                print("\nMetrics:")
                print(f"  - Latency: {result['latency_ms']}ms")
                print(f"  - Tokens: {result['token_usage']['total_tokens']}")
                print(f"  - Model: {result['model']}")
            else:
                print(f"✗ Status: {result['status']}")
                print(f"Error: {result['natural_language_answer']}")

        except Exception as e:
            print(f"✗ Error: {str(e)}")

        print("-" * 70)

    print("\n" + "=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)


def call_chat_api(base_url: str, session_id: str, message: str) -> Dict[str, Any]:
    """Make a request to the chat API"""

    url = f"{base_url}/api/chat"

    data = {"session_id": session_id, "message": message, "context": {}}

    request = urllib.request.Request(
        url,
        data=json.dumps(data).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        raise Exception(f"HTTP {e.code}: {error_body}")
    except urllib.error.URLError as e:
        raise Exception(f"Connection error: {str(e)}")


def test_health_check(base_url: str = "http://localhost:8000"):
    """Test the health check endpoint"""

    print("\n" + "=" * 70)
    print("HEALTH CHECK TEST")
    print("=" * 70)

    url = f"{base_url}/health"

    try:
        request = urllib.request.Request(url)
        with urllib.request.urlopen(request, timeout=5) as response:
            result = json.loads(response.read().decode("utf-8"))
            print(f"✓ Status: {result['status']}")
            print(f"✓ Timestamp: {result['timestamp']}")
    except Exception as e:
        print(f"✗ Error: {str(e)}")

    print("=" * 70)


if __name__ == "__main__":
    import sys

    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"

    # Test health check first
    test_health_check(base_url)

    # Test chat API
    test_chat_api(base_url)
