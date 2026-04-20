#!/usr/bin/env python3
"""Serve this folder locally and open index.html."""

import http.server
import socketserver
import os
import webbrowser

PORT = 8003
HOST = "127.0.0.1"

if __name__ == "__main__":
    root = os.path.dirname(os.path.abspath(__file__))
    os.chdir(root)
    handler = http.server.SimpleHTTPRequestHandler
    url = f"http://{HOST}:{PORT}/"
    print(f"Serving {root} at {url}")
    webbrowser.open(url)
    with socketserver.TCPServer((HOST, PORT), handler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nStopped")
