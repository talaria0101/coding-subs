#!/usr/bin/env python3
"""Run a script with urllib's plain-HTTP requests carried over a Unix socket.

    python3 tests/unix_http_shim.py SOCK SCRIPT [ARGS ...]

Installs a global urllib opener whose HTTP handler connects to SOCK instead of
the host named in the URL, then runs SCRIPT as `__main__` with ARGS. The script
is unmodified: it still builds its own `Request`, sends its own headers and
reads the response through `urllib.request.urlopen`. Only the transport under
the HTTP connection changes. The opener carries no proxy handler, so a proxy
set in the environment cannot intercept the fixture.

This is the substitute for a 127.0.0.1 server on a machine whose sandbox
refuses every TCP bind. It does not exercise the TCP connect or the proxy
bypass for loopback addresses; the TCP mode of tests/test_fetch_tools.py does.
"""
from __future__ import annotations

import http.client
import runpy
import socket
import sys
import urllib.request


class UnixHTTPConnection(http.client.HTTPConnection):
    def __init__(self, socket_path: str, host: str, **kwargs):
        super().__init__(host, **kwargs)
        self._socket_path = socket_path

    def connect(self) -> None:
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        if self.timeout is not None and self.timeout is not socket._GLOBAL_DEFAULT_TIMEOUT:
            sock.settimeout(self.timeout)
        sock.connect(self._socket_path)
        self.sock = sock


class UnixHTTPHandler(urllib.request.HTTPHandler):
    def __init__(self, socket_path: str):
        super().__init__()
        self._socket_path = socket_path

    def http_open(self, req):
        def factory(host, **kwargs):
            return UnixHTTPConnection(self._socket_path, host, **kwargs)
        return self.do_open(factory, req)


def install(socket_path: str) -> None:
    opener = urllib.request.build_opener(
        urllib.request.ProxyHandler({}), UnixHTTPHandler(socket_path)
    )
    urllib.request.install_opener(opener)


def main() -> int:
    if len(sys.argv) < 3:
        print(__doc__, file=sys.stderr)
        return 2
    socket_path, script = sys.argv[1], sys.argv[2]
    install(socket_path)
    sys.argv = [script] + sys.argv[3:]
    runpy.run_path(script, run_name="__main__")
    return 0


if __name__ == "__main__":
    sys.exit(main())
