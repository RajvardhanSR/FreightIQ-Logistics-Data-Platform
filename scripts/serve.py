#!/usr/bin/env python3
"""
FreightIQ Local Development Server
High-performance static server with clean URL rewrite support.
"""

import os
import sys
import mimetypes
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DIST_DIR = PROJECT_ROOT / "dist"
PORT = 8080

class CleanURLHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DIST_DIR), **kwargs)

    def do_GET(self):
        # Clean path
        req_path = self.path.split("?")[0].split("#")[0].strip("/")
        
        # 1. Root
        if not req_path:
            return super().do_GET()

        # 2. Exact match in dist
        target = DIST_DIR / req_path
        if target.is_file():
            return super().do_GET()

        # 3. Path with .html exists
        target_html = DIST_DIR / f"{req_path}.html"
        if target_html.is_file():
            self.path = f"/{req_path}.html"
            return super().do_GET()

        # 4. Path as directory with index.html
        target_dir_index = DIST_DIR / req_path / "index.html"
        if target_dir_index.is_file():
            self.path = f"/{req_path}/index.html"
            return super().do_GET()

        # Fallback to default
        return super().do_GET()

    def end_headers(self):
        # Enable CORS and caching headers for local testing
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-cache")
        super().end_headers()

def run_server():
    server_address = ("127.0.0.1", PORT)
    httpd = HTTPServer(server_address, CleanURLHandler)
    print(f" FreightIQ local server running at http://localhost:{PORT}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")

if __name__ == "__main__":
    run_server()
