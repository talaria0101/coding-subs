"""The fetch tools against a local HTTP fixture: routes, user agents, log paths.

    python3 -m unittest discover -s tests

tests/http_fixture_server.py is started detached, health-checked with a
deadline, and killed when the class finishes. It listens on 127.0.0.1 where the
machine allows a TCP bind. Where the sandbox refuses every bind, including on
loopback, it serves the same routes over a Unix socket and the tools run under
tests/unix_http_shim.py, which carries urllib's HTTP over that socket without
changing the tool. The mode in use is printed to stderr once per run. The Unix
mode does not exercise the TCP connect or proxy bypass for 127.0.0.1.

No test touches the external network. Proxy variables are cleared for 127.0.0.1
in TCP mode, because urllib otherwise sends loopback requests to the proxy.
"""
from __future__ import annotations

import http.client
import importlib.util
import json
import os
import signal
import socket
import subprocess
import sys
import tempfile
import time
import types
import unittest
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TESTS = ROOT / "tests"
TOOLS = ROOT / "tools"
FETCH_SOURCE = TOOLS / "fetch-source.py"
FETCH_FIRSTPARTY = TOOLS / "fetch-firstparty.py"
FETCH_COMMUNITY = TOOLS / "fetch-community.py"
SERVER = TESTS / "http_fixture_server.py"
SHIM = TESTS / "unix_http_shim.py"

HEALTH_DEADLINE_S = 10.0


def _tcp_bind_allowed() -> str | None:
    """None if a loopback TCP bind works here, else the reason it does not."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind(("127.0.0.1", 0))
        return None
    except OSError as exc:
        return f"{type(exc).__name__}: {exc}"
    finally:
        sock.close()


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class FixtureServer:
    """The detached fixture server and how to reach it."""

    def __init__(self, workdir: Path):
        self.workdir = workdir
        self.ready = workdir / "ready"
        self.socket_path = workdir / "fixture.sock"
        self.log = workdir / "server.log"
        self.refused = _tcp_bind_allowed()
        self.mode = "tcp" if self.refused is None else "unix"
        self.process: subprocess.Popen | None = None
        self.base = ""

    def start(self) -> None:
        command = [sys.executable, str(SERVER), str(self.ready)]
        if self.mode == "unix":
            command += ["--unix", str(self.socket_path)]
        with open(self.log, "wb") as log:
            self.process = subprocess.Popen(
                command, stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT,
                start_new_session=True,
            )
        deadline = time.monotonic() + HEALTH_DEADLINE_S
        last_error = "server never wrote its ready file"
        while time.monotonic() < deadline:
            if self.process.poll() is not None:
                break
            if self.ready.is_file():
                marker = self.ready.read_text(encoding="utf-8").strip()
                self.base = ("http://fixture" if self.mode == "unix"
                             else f"http://127.0.0.1:{marker}")
                try:
                    if self.health() == "ok":
                        return
                except OSError as exc:
                    last_error = f"{type(exc).__name__}: {exc}"
            time.sleep(0.05)
        self.stop()
        raise RuntimeError(
            f"fixture server ({self.mode}) not healthy within {HEALTH_DEADLINE_S}s: "
            f"{last_error}; exit={self.process.returncode if self.process else None}; "
            f"log: {self.log.read_text(errors='replace') if self.log.is_file() else ''}"
        )

    def health(self) -> str:
        if self.mode == "unix":
            shim = _load(SHIM, "unix_http_shim_for_health")
            conn = shim.UnixHTTPConnection(str(self.socket_path), "fixture", timeout=2)
            try:
                conn.request("GET", "/health")
                return conn.getresponse().read().decode()
            finally:
                conn.close()
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        with opener.open(self.base + "/health", timeout=2) as response:
            return response.read().decode()

    def stop(self) -> None:
        if self.process is None or self.process.poll() is not None:
            return
        try:
            os.killpg(self.process.pid, signal.SIGTERM)
        except ProcessLookupError:
            return
        try:
            self.process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            os.killpg(self.process.pid, signal.SIGKILL)
            self.process.wait(timeout=5)

    def command(self, script: Path, *args: str) -> list[str]:
        if self.mode == "unix":
            return [sys.executable, str(SHIM), str(self.socket_path), str(script), *args]
        return [sys.executable, str(script), *args]

    def env(self) -> dict[str, str]:
        env = dict(os.environ)
        if self.mode == "tcp":
            for name in ("NO_PROXY", "no_proxy"):
                env[name] = ",".join(filter(None, [env.get(name), "127.0.0.1", "localhost"]))
        return env


class FetchCase(unittest.TestCase):
    server: FixtureServer

    @classmethod
    def setUpClass(cls):
        cls._server_dir = tempfile.TemporaryDirectory()
        cls.server = FixtureServer(Path(cls._server_dir.name))
        reason = f" (TCP bind refused: {cls.server.refused})" if cls.server.refused else ""
        print(f"\n[fetch fixture] transport: {cls.server.mode}{reason}", file=sys.stderr)
        cls.server.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.stop()
        cls._server_dir.cleanup()

    def setUp(self):
        self._work = tempfile.TemporaryDirectory()
        self.work = Path(self._work.name)

    def tearDown(self):
        self._work.cleanup()

    def run_tool(self, script: Path, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            self.server.command(script, *args), cwd=self.work, env=self.server.env(),
            stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=60,
        )

    def fetch(self, path: str, *args: str) -> tuple[subprocess.CompletedProcess, list[dict]]:
        log = self.work / "log.json"
        result = self.run_tool(
            FETCH_SOURCE, self.server.base + path, "--retries", "0",
            "--jina-prefix", self.server.base + "/jina/", "--log", str(log), *args,
        )
        records = json.loads(log.read_text(encoding="utf-8")) if log.is_file() else []
        return result, records


class ViaRoutes(FetchCase):
    def test_via_jina_fetches_only_jina(self):
        result, records = self.fetch("/page", "--via", "jina", "--user-agent", "curl",
                                     "--out", "page.txt")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual([r["route"] for r in records], ["jina"])
        self.assertTrue(records[0]["url"].startswith(self.server.base + "/jina/"))
        self.assertTrue((self.work / "page.txt").read_bytes().startswith(b"JINA BYTES"))
        self.assertEqual(records[0]["saved_as"], "page.txt")

    def test_via_jina_failure_does_not_fall_back_to_direct(self):
        result, records = self.fetch("/page", "--via", "jina", "--out", "page.txt")
        self.assertEqual(result.returncode, 1)
        self.assertEqual([(r["route"], r["http"]) for r in records], [("jina", 403)])
        self.assertFalse((self.work / "page.txt").exists())

    def test_via_both_saves_two_files_each_with_its_route(self):
        result, records = self.fetch("/page", "--via", "both", "--user-agent", "curl",
                                     "--out", "sub/page.html")
        self.assertEqual(result.returncode, 0, result.stderr)
        saved = {r["route"]: r["saved_as"] for r in records if r.get("saved_as")}
        self.assertEqual(saved, {"direct": "sub/page.html", "jina": "sub/page.jina.txt"})
        self.assertEqual((self.work / "sub/page.html").read_bytes(), b"DIRECT BYTES")
        self.assertTrue((self.work / "sub/page.jina.txt").read_bytes().startswith(b"JINA BYTES"))

    def test_via_both_with_one_route_failing_exits_nonzero_and_keeps_the_other(self):
        result, records = self.fetch("/page", "--via", "both", "--out", "page.html")
        self.assertEqual(result.returncode, 1)
        self.assertEqual((self.work / "page.html").read_bytes(), b"DIRECT BYTES")
        self.assertFalse((self.work / "page.jina.txt").exists())
        self.assertEqual([(r["route"], r["http"]) for r in records],
                         [("direct", 200), ("jina", 403)])

    def test_direct_is_the_default_and_only_route(self):
        result, records = self.fetch("/page", "--out", "page.html")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual([r["route"] for r in records], ["direct"])

    def test_missing_page_is_a_failure(self):
        result, records = self.fetch("/missing", "--out", "page.html")
        self.assertEqual(result.returncode, 1)
        self.assertEqual(records[0]["http"], 404)
        self.assertFalse((self.work / "page.html").exists())


class UserAgents(FetchCase):
    def test_default_is_chrome_and_is_recorded(self):
        result, records = self.fetch("/ua-gated", "--out", "g.txt")
        self.assertEqual(result.returncode, 1)
        self.assertEqual(records[0]["http"], 403)
        self.assertEqual(records[0]["ua"], "chrome")
        self.assertIn("Chrome/", records[0]["user_agent"])

    def test_curl_preset_gets_through(self):
        result, records = self.fetch("/ua-gated", "--user-agent", "curl", "--out", "g.txt")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((records[0]["ua"], records[0]["http"]), ("curl", 200))
        self.assertEqual((self.work / "g.txt").read_bytes(), b"UA-GATED BYTES")

    def test_literal_string_is_logged_as_custom(self):
        result, records = self.fetch("/ua-gated", "--user-agent", "coding-subs-test/1.0",
                                     "--out", "g.txt")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(records[0]["ua"], "custom")
        self.assertEqual(records[0]["user_agent"], "coding-subs-test/1.0")


class SavedAsIsPosixRelative(FetchCase):
    def assert_posix_relative(self, saved: str) -> None:
        self.assertNotIn("\\", saved)
        self.assertFalse(saved.startswith("/"), saved)

    def test_fetch_source_absolute_out_is_logged_relative(self):
        out = self.work / "2026-10-07" / "sources" / "page.html"
        result, records = self.fetch("/page", "--out", str(out))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(records[0]["saved_as"], "2026-10-07/sources/page.html")

    def test_fetch_firstparty(self):
        tsv = self.work / "sources.tsv"
        tsv.write_text(f"page.html\t{self.server.base}/page\tnote\n", encoding="utf-8")
        log = self.work / "pass" / "data" / "fetch-log.json"
        result = self.run_tool(FETCH_FIRSTPARTY, "pass/sources", str(log), str(tsv))
        self.assertEqual(result.returncode, 0, result.stderr)
        records = json.loads(log.read_text(encoding="utf-8"))
        self.assertEqual(records[0]["saved_as"], "sources/page.html")
        self.assert_posix_relative(records[0]["saved_as"])

    def test_fetch_community_append_log(self):
        community = _load(FETCH_COMMUNITY, "fetch_community_under_test")
        pass_dir = self.work / "2026-10-07"
        (pass_dir / "data").mkdir(parents=True)
        (pass_dir / "data" / "fetch-log.json").write_text("[]", encoding="utf-8")
        out = pass_dir / "sources" / "feed.xml"
        cwd = os.getcwd()
        os.chdir(self.work)
        try:
            code = community.append_log(str(pass_dir), "https://example.invalid/r.rss", 200,
                                        b"<feed/>", out, types.SimpleNamespace(note=""))
        finally:
            os.chdir(cwd)
        self.assertEqual(code, 0)
        records = json.loads((pass_dir / "data" / "fetch-log.json").read_text(encoding="utf-8"))
        self.assertEqual(records[0]["saved_as"], "2026-10-07/sources/feed.xml")


if __name__ == "__main__":
    unittest.main()
