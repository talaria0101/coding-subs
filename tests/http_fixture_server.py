#!/usr/bin/env python3
"""A local HTTP server that imitates the answers the fetch tools have to survive.

    python3 tests/http_fixture_server.py READY_FILE            # TCP, 127.0.0.1
    python3 tests/http_fixture_server.py READY_FILE --unix SOCK

Binds 127.0.0.1 on a free port and writes the port number to READY_FILE once it
is listening, then serves until killed. tests/test_fetch_tools.py starts it
detached, waits on GET /health with a deadline, and kills it when the tests
finish, so no test needs the external network.

`--unix SOCK` serves the same routes over a Unix domain socket instead, and
writes "unix" to READY_FILE. It exists for sandboxes that refuse every TCP bind,
including on loopback; tests/unix_http_shim.py routes urllib's HTTP connections
to the socket. What it does not exercise is the TCP connect itself and proxy
bypass for 127.0.0.1, which only the TCP mode covers.

Routes, chosen to reproduce what was observed on 2026-10-07:

    /health         200 "ok"
    /page           200 "DIRECT BYTES" for any user agent
    /ua-gated       403 for a Chrome user agent (the Cloudflare answer), 200
                    "UA-GATED BYTES" for anything else
    /jina/<url>     a stand-in for r.jina.ai: 403 for a Chrome user agent, 200
                    "JINA BYTES for <url>" for anything else
    /missing        404
"""
from __future__ import annotations

import socketserver
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


class ThreadingUnixHTTPServer(socketserver.ThreadingMixIn, socketserver.UnixStreamServer):
    daemon_threads = True


def is_chrome(agent: str) -> bool:
    return "Chrome/" in agent


class Handler(BaseHTTPRequestHandler):
    def _send(self, status: int, body: bytes) -> None:
        self.send_response(status)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802 - the http.server interface
        agent = self.headers.get("User-Agent", "")
        if self.path == "/health":
            self._send(200, b"ok")
        elif self.path == "/page":
            self._send(200, b"DIRECT BYTES")
        elif self.path == "/ua-gated":
            if is_chrome(agent):
                self._send(403, b"Attention Required! | Cloudflare")
            else:
                self._send(200, b"UA-GATED BYTES")
        elif self.path.startswith("/jina/"):
            if is_chrome(agent):
                self._send(403, b"Attention Required! | Cloudflare")
            else:
                self._send(200, b"JINA BYTES for " + self.path[len("/jina/"):].encode())
        else:
            self._send(404, b"not found")

    def log_message(self, *args) -> None:
        pass


def main() -> int:
    ready = Path(sys.argv[1])
    if len(sys.argv) == 4 and sys.argv[2] == "--unix":
        server = ThreadingUnixHTTPServer(sys.argv[3], Handler)
        marker = "unix"
    elif len(sys.argv) == 2:
        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        marker = str(server.server_address[1])
    else:
        print(__doc__, file=sys.stderr)
        return 2
    tmp = ready.with_suffix(".tmp")
    tmp.write_text(marker, encoding="utf-8")
    tmp.replace(ready)
    server.serve_forever()
    return 0


if __name__ == "__main__":
    sys.exit(main())
