#!/usr/bin/env python3
"""
Quick verification script for SQL pattern matching
"""

import re
from typing import Any, Dict, List


def build_query_patterns() -> List[Dict[str, Any]]:
    """Same patterns as in main.py"""
    return [
        {
            "patterns": [
                r"how many assets",
                r"total assets",
                r"count.*assets",
                r"number of assets",
            ],
            "intent": "asset_count_total",
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
                r"assets.*by site",
            ],
            "intent": "asset_count_by_site",
        },
        {
            "patterns": [
                r"assets.*by category",
                r"breakdown.*category",
                r"assets.*per category",
                r"show.*assets.*category",
                r"list.*assets.*category",
            ],
            "intent": "assets_by_category",
        },
        {
            "patterns": [r"list.*vendors", r"show.*vendors", r"all vendors"],
            "intent": "list_vendors",
        },
    ]


def match_intent(message: str, patterns: List[Dict[str, Any]]) -> str:
    """Match user message to a query pattern"""
    message_lower = message.lower().strip()

    for pattern_def in patterns:
        for pattern in pattern_def["patterns"]:
            if re.search(pattern, message_lower):
                return pattern_def["intent"]

    return "NO_MATCH"


if __name__ == "__main__":
    patterns = build_query_patterns()

    test_queries = [
        "How many assets do I have?",
        "Show me assets by site",
        "show assets by site",
        "assets by site",
        "List assets by category",
        "Show me all vendors",
        "What is the breakdown by site?",
    ]

    print("=" * 70)
    print("PATTERN MATCHING VERIFICATION")
    print("=" * 70)

    for query in test_queries:
        intent = match_intent(query, patterns)
        status = "✓" if intent != "NO_MATCH" else "✗"
        print(f"\n{status} '{query}'")
        print(f"   → Intent: {intent}")

    print("\n" + "=" * 70)
