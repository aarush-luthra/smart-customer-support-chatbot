"""
HTTP Server for the Smart Customer Support System

This module provides a simple HTTP server using Python's built-in http.server.
No external libraries are used.

Endpoints:
    GET /              - Serves the frontend HTML
    GET /styles.css    - Serves the CSS file
    GET /app.js        - Serves the JavaScript file
    POST /api/message  - Process a user message
    GET /api/suggestions?prefix=xxx - Get auto-suggestions
    GET /api/context   - Get recent interaction context
    GET /api/stats     - Get system statistics
    POST /api/reset    - Reset conversation

Author: Smart Customer Support System
"""

import json
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from typing import Dict, Any

from backend.support_engine import get_engine


# Determine paths
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(BACKEND_DIR)
FRONTEND_DIR = os.path.join(PROJECT_DIR, "frontend")


class SupportHandler(BaseHTTPRequestHandler):
    """
    HTTP request handler for the customer support system.
    
    Handles both static file serving and API endpoints.
    """
    
    def do_GET(self):
        """Handle GET requests."""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        # API endpoints
        if path.startswith("/api/"):
            self._handle_api_get(parsed_path)
        # Static files
        elif path == "/" or path == "/index.html":
            self._serve_file("index.html", "text/html")
        elif path == "/styles.css":
            self._serve_file("styles.css", "text/css")
        elif path == "/app.js":
            self._serve_file("app.js", "application/javascript")
        else:
            self._send_404()
    
    def do_POST(self):
        """Handle POST requests."""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        if path.startswith("/api/"):
            self._handle_api_post(parsed_path)
        else:
            self._send_404()
    
    def _handle_api_get(self, parsed_path):
        """Handle API GET requests."""
        path = parsed_path.path
        query_params = parse_qs(parsed_path.query)
        
        engine = get_engine()
        
        if path == "/api/suggestions":
            # Get auto-suggestions from Trie
            prefix = query_params.get("prefix", [""])[0]
            result = engine.get_suggestions(prefix)
            self._send_json(result)
        
        elif path == "/api/context":
            # Get recent interaction context
            result = engine.get_recent_context()
            self._send_json(result)
        
        elif path == "/api/stats":
            # Get system statistics
            result = engine.get_system_stats()
            self._send_json(result)
        
        elif path == "/api/queue":
            # Get queue status
            result = engine.get_queue_status()
            self._send_json(result)
        
        else:
            self._send_404()
    
    def _handle_api_post(self, parsed_path):
        """Handle API POST requests."""
        path = parsed_path.path
        
        # Read request body
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8")
        
        try:
            data = json.loads(body) if body else {}
        except json.JSONDecodeError:
            self._send_error(400, "Invalid JSON")
            return
        
        engine = get_engine()
        
        if path == "/api/message":
            # Process user message
            message = data.get("message", "")
            user_id = data.get("user_id", "default_user")
            
            result = engine.process_message(user_id, message)
            self._send_json(result)
        
        elif path == "/api/reset":
            # Reset conversation
            user_id = data.get("user_id", "default_user")
            result = engine.reset_conversation(user_id)
            self._send_json(result)
        
        else:
            self._send_404()
    
    def _serve_file(self, filename: str, content_type: str):
        """Serve a static file from the frontend directory."""
        filepath = os.path.join(FRONTEND_DIR, filename)
        
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            
            self.send_response(200)
            self.send_header("Content-Type", f"{content_type}; charset=utf-8")
            self.send_header("Content-Length", len(content.encode("utf-8")))
            self.end_headers()
            self.wfile.write(content.encode("utf-8"))
        
        except FileNotFoundError:
            self._send_404()
    
    def _send_json(self, data: Dict[str, Any]):
        """Send a JSON response."""
        response = json.dumps(data, ensure_ascii=False)
        response_bytes = response.encode("utf-8")
        
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", len(response_bytes))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(response_bytes)
    
    def _send_error(self, code: int, message: str):
        """Send an error response."""
        error_data = {"error": message}
        response = json.dumps(error_data)
        response_bytes = response.encode("utf-8")
        
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", len(response_bytes))
        self.end_headers()
        self.wfile.write(response_bytes)
    
    def _send_404(self):
        """Send a 404 Not Found response."""
        self._send_error(404, "Not Found")
    
    def log_message(self, format, *args):
        """Custom log format."""
        print(f"[{self.log_date_time_string()}] {format % args}")


def run_server(host: str = "localhost", port: int = 8000):
    """
    Start the HTTP server.
    
    Args:
        host: The host to bind to
        port: The port to listen on
    """
    server_address = (host, port)
    httpd = HTTPServer(server_address, SupportHandler)
    
    print("=" * 60)
    print("   E-SHOP CUSTOMER SUPPORT CHATBOT")
    print("   Demonstrating 6 Data Structures in Action")
    print("=" * 60)
    print()
    print(f"   Server running at: http://{host}:{port}")
    print()
    print("   Data Structures Used:")
    print("   1. Trie (Prefix Tree) - Auto-complete suggestions")
    print("   2. HashMap (dict) - O(1) FAQ lookups")
    print("   3. Decision Tree - Conversation flow")
    print("   4. Stack - Go back navigation")
    print("   5. Union-Find - Synonym intent grouping")
    print("   6. Weighted Graph - Next best actions")
    print()
    print("   Press Ctrl+C to stop the server")
    print("=" * 60)
    print()
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\nServer stopped.")
        httpd.server_close()


if __name__ == "__main__":
    run_server()
