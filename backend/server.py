"""
HTTP Server for the Smart Customer Support System
"""

import json
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from typing import Dict, Any

from support_engine import get_engine


# Determine paths
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(BACKEND_DIR)
FRONTEND_DIR = os.path.join(PROJECT_DIR, "frontend")


class SupportHandler(BaseHTTPRequestHandler):
    """
    HTTP request handler for the customer support system.
    """

    def do_GET(self):
        """Handle GET requests."""
        parsed_path = urlparse(self.path)
        path = parsed_path.path

        # 🔑 OAUTH CALLBACK FIX (prevents blank screen)
        if "code=" in self.path:
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"""
                <html>
                    <body>
                        <h2>Login Successful</h2>
                        <p>You can close this tab and return to the application.</p>
                    </body>
                </html>
            """)
            return

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

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def end_headers(self):
        # ✅ Safe CORS headers
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        super().end_headers()

    def _handle_api_get(self, parsed_path):
        path = parsed_path.path
        query_params = parse_qs(parsed_path.query)

        engine = get_engine()

        if path == "/api/suggestions":
            prefix = query_params.get("prefix", [""])[0]
            result = engine.get_suggestions(prefix)
            self._send_json(result)

        elif path == "/api/order":
            order_id = query_params.get("order_id", [""])[0]
            result = engine.lookup_order(order_id)
            self._send_json(result)

        elif path == "/api/stats":
            result = engine.get_system_stats()
            self._send_json(result)

        else:
            self._send_404()

    def _handle_api_post(self, parsed_path):
        path = parsed_path.path

        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8")

        try:
            data = json.loads(body) if body else {}
        except json.JSONDecodeError:
            self._send_error(400, "Invalid JSON")
            return

        engine = get_engine()

        if path == "/api/message":
            message = data.get("message", "")
            user_id = data.get("user_id", "default_user")
            result = engine.process_message(user_id, message)
            self._send_json(result)

        elif path == "/api/reset":
            user_id = data.get("user_id", "default_user")
            result = engine.reset_conversation(user_id)
            self._send_json(result)

        else:
            self._send_404()

    def _serve_file(self, filename: str, content_type: str):
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
        response = json.dumps(data, ensure_ascii=False)
        response_bytes = response.encode("utf-8")

        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", len(response_bytes))
        self.end_headers()
        self.wfile.write(response_bytes)

    def _send_error(self, code: int, message: str):
        error_data = {"error": message}
        response = json.dumps(error_data).encode("utf-8")

        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", len(response))
        self.end_headers()
        self.wfile.write(response)

    def _send_404(self):
        self._send_error(404, "Not Found")

    def log_message(self, format, *args):
        print(f"[{self.log_date_time_string()}] {format % args}")


def run_server(host: str = "127.0.0.1", port: int = 8000):
    server_address = (host, port)
    httpd = HTTPServer(server_address, SupportHandler)

    print("=" * 60)
    print("   E-SHOP CUSTOMER SUPPORT CHATBOT")
    print("   Demonstrating 7 Data Structures in Action")
    print("=" * 60)
    print(f"\n   Server running at: http://{host}:{port}\n")
    print("   Press Ctrl+C to stop the server")
    print("=" * 60)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
        httpd.server_close()


if __name__ == "__main__":
    run_server()
