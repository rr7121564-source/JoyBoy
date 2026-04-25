import threading
import os
from http.server import BaseHTTPRequestHandler, HTTPServer

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b"Bot Health: Excellent! Anti-Crash system active.")

def run_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

def keep_alive():
    """Starts the dummy server on a separate daemon thread."""
    t = threading.Thread(target=run_server)
    t.daemon = True
    t.start()
