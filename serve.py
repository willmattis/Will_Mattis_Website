#!/usr/bin/env python3
"""
Tiny local preview server for the portfolio.

Why this exists: the 3D STEP viewer uses JavaScript *modules*, which browsers
only run when the server reports a JavaScript MIME type. Python's built-in
`python -m http.server` mislabels .js as text/plain on some systems (notably
Windows), which makes the viewer fail locally. This server fixes the MIME types.

Usage:
    python serve.py            # serves the ./site folder at http://localhost:8123
    python serve.py 9000       # use a different port

(On the live GitHub Pages site this isn't needed — GitHub serves correct types.)
"""
import http.server
import socketserver
import sys
import os

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8123
DIRECTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "site")


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)


# Force correct MIME types regardless of the OS registry.
Handler.extensions_map.update({
    ".js": "text/javascript",
    ".mjs": "text/javascript",
    ".wasm": "application/wasm",
    ".step": "application/octet-stream",
    ".stp": "application/octet-stream",
    ".svg": "image/svg+xml",
})

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print("Portfolio preview running at http://localhost:%d  (Ctrl+C to stop)" % PORT)
        httpd.serve_forever()
