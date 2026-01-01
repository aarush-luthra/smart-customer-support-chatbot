#!/usr/bin/env python3
"""
Smart Customer Support System - Main Entry Point

This is the main entry point for the Smart Customer Support System.
It starts the HTTP server and serves the frontend and API endpoints.

USAGE:
    python3 main.py
    
Then open: http://localhost:8000

DATA STRUCTURES DEMONSTRATED:
    1. Trie (Prefix Tree) - Real-time keyword suggestions
    2. Queue (deque) - FIFO query management
    3. Priority Queue (heapq) - Urgent query prioritization
    4. HashMap (dict) - O(1) FAQ response lookup
    5. Tree - Structured conversation flow
    6. Deque (bounded) - Recent interaction cache

Author: Smart Customer Support System
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
