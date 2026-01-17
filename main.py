#!/usr/bin/env python3
"""
E-Commerce Customer Support Chatbot - Main Entry Point

Demonstrates 6 Data Structures in a practical chatbot:

DATA STRUCTURES:
    1. Trie (Prefix Tree) - Auto-complete suggestions
    2. HashMap (Dictionary) - O(1) FAQ lookups
    3. Decision Tree - Conversation flow with branching
    4. Stack - "Go back" navigation
    5. Union-Find (Disjoint Set) - Synonym intent grouping
    6. Weighted Graph - Next best action suggestions

USAGE:
    python3 main.py
    
Then open: http://localhost:8000

Author: E-Shop Customer Support System
"""


import sys
import os

# Add the project root to Python path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

from backend.server import run_server


def main():
    """Main entry point for the application."""
    print()
    print("Starting Smart Customer Support System...")
    print()
    
    # Run the server on port 8000
    run_server(host="localhost", port=8000)


if __name__ == "__main__":
    main()
