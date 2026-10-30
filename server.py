#!/usr/bin/env python3
"""Serve this folder locally and open index.html."""

import http.server
import socketserver
import os
import webbrowser

PORT = 8004
HOST = "127.0.0.1"


class NoCacheHandler(http.server.SimpleHTTPRequestHandler):
    """Tell the browser not to cache, so a reload always shows the latest edits."""

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


if __name__ == "__main__":
    root = os.path.dirname(os.path.abspath(__file__))
    os.chdir(root)
    handler = NoCacheHandler
    url = f"http://{HOST}:{PORT}/"
    print(f"Serving {root} at {url}")
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer((HOST, PORT), handler) as httpd:
        webbrowser.open(url)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nStopped")
