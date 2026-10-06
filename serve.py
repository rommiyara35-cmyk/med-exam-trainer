#!/usr/bin/env python3
"""
Quick dev server for Med-Exam Trainer PWA.
Serves with correct MIME types and CORS headers for local development.
Run: python3 serve.py
Then open: http://localhost:3000
"""
import http.server
import socketserver
import os

PORT = 3000
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-cache')
        # Required for service workers
        self.send_header('Service-Worker-Allowed', '/')
        super().end_headers()

    def guess_type(self, path):
        if path.endswith('.json'): return 'application/json'
        if path.endswith('.js'): return 'application/javascript'
        if path.endswith('.webmanifest') or path.endswith('manifest.json'): return 'application/manifest+json'
        return super().guess_type(path)

    def log_message(self, format, *args):
        print(f"  {self.address_string()} → {format % args}")

print(f"\n🔬 Med-Exam Trainer Dev Server")
print(f"📱 Open on desktop: http://localhost:{PORT}")
print(f"📲 For iPhone: find your Mac's local IP and open http://<IP>:{PORT}")
print(f"   (macOS: System Settings → Wi-Fi → Details → IP Address)\n")

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n✅ Server stopped.")
