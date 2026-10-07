"""tools/merge-fetch-logs.py: rewriting, copying, collisions and hash checks.

    python3 -m unittest discover -s tests

Every fixture is built in a temporary directory: two scratch directories, each
with a `sources/` and a fetch log in one of the `saved_as` spellings in use
(relative to the log, absolute, and with Windows separators), and a destination
standing in for the repository root.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MERGE = ROOT / "tools" / "merge-fetch-logs.py"


def record(url: str, body: bytes | None, saved: str | None, **extra) -> dict:
    entry = {
        "url": url,
        "http": 200 if body is not None else 404,
        "bytes": len(body) if body is not None else 0,
        "sha256": hashlib.sha256(body).hexdigest() if body is not None else None,
        "route": "direct",
        "attempt": 1,
    }
    if saved is not None:
        entry["saved_as"] = saved
    entry.update(extra)
    return entry


class MergeCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.a = self.tmp / "scratch" / "a"
        self.b = self.tmp / "scratch" / "b"
        self.dest = self.tmp / "repo"
        for d in (self.a / "sources" / "nested", self.b / "sources", self.dest):
            d.mkdir(parents=True)
        (self.a / "sources" / "one.html").write_bytes(b"ONE")
        (self.a / "sources" / "nested" / "deep.ts").write_bytes(b"DEEP")
        (self.b / "sources" / "two.md").write_bytes(b"TWO")
        self.write_log(self.a, [
            record("https://x.invalid/one", b"ONE", "sources/one.html"),
            record("https://x.invalid/deep", b"DEEP", "sources\\nested\\deep.ts"),
            record("https://x.invalid/gone", None, None),
        ])
        self.write_log(self.b, [
            record("https://x.invalid/two", b"TWO", str(self.b / "sources" / "two.md")),
        ])

    def tearDown(self):
        self._tmp.cleanup()

    def write_log(self, where: Path, entries: list[dict]) -> Path:
        path = where / "fetch-log.json"
        path.write_text(json.dumps(entries, indent=2), encoding="utf-8")
        return path

    def maps(self) -> list[str]:
        return ["--map", f"{self.a / 'sources'}=2026-10-07/sources",
                "--map", f"{self.b / 'sources'}=2026-10-07/sources"]

    def run_merge(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(MERGE), *args], cwd=self.tmp, stdin=subprocess.DEVNULL,
            capture_output=True, text=True, timeout=60,
        )

    def merge_both(self, *extra: str) -> subprocess.CompletedProcess:
        return self.run_merge(str(self.a / "fetch-log.json"), str(self.b / "fetch-log.json"),
                              *self.maps(), *extra)


class Rewrites(MergeCase):
    def test_merge_rewrites_every_spelling_to_posix_relative(self):
        out = self.tmp / "merged.json"
        result = self.merge_both("--out", str(out))
        self.assertEqual(result.returncode, 0, result.stderr)
        merged = json.loads(out.read_text(encoding="utf-8"))
        self.assertEqual(len(merged), 4)
        self.assertEqual([r.get("saved_as") for r in merged], [
            "2026-10-07/sources/one.html",
            "2026-10-07/sources/nested/deep.ts",
            None,
            "2026-10-07/sources/two.md",
        ])
        self.assertEqual(merged[2]["http"], 404, "a failed attempt passes through unchanged")

    def test_copy_sources_copies_then_verifies(self):
        out = self.tmp / "merged.json"
        result = self.merge_both("--out", str(out), "--copy-sources", str(self.dest))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((self.dest / "2026-10-07/sources/nested/deep.ts").read_bytes(), b"DEEP")
        self.assertEqual((self.dest / "2026-10-07/sources/two.md").read_bytes(), b"TWO")
        again = self.merge_both("--out", str(out), "--copy-sources", str(self.dest))
        self.assertEqual(again.returncode, 0, again.stderr)
        self.assertIn("verified", again.stdout)

    def test_identical_bytes_at_one_destination_are_not_a_collision(self):
        (self.b / "sources" / "one.html").write_bytes(b"ONE")
        self.write_log(self.b, [record("https://y.invalid/one", b"ONE", "sources/one.html")])
        result = self.merge_both("--out", str(self.tmp / "merged.json"))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("identical bytes", result.stdout)

    def test_dry_run_writes_and_copies_nothing(self):
        out = self.tmp / "merged.json"
        result = self.merge_both("--dry-run", "--out", str(out), "--copy-sources", str(self.dest))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(out.exists())
        self.assertEqual(list(self.dest.iterdir()), [])
        self.assertIn("would copy", result.stdout)


class Refusals(MergeCase):
    def assert_refused(self, result: subprocess.CompletedProcess, *needles: str) -> None:
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("nothing written", result.stderr)
        for needle in needles:
            self.assertIn(needle, result.stderr)
        self.assertFalse((self.tmp / "merged.json").exists())
        self.assertEqual(list(self.dest.iterdir()), [])

    def test_collision_between_inputs_lists_both(self):
        (self.b / "sources" / "one.html").write_bytes(b"NOT ONE")
        self.write_log(self.b, [record("https://y.invalid/one", b"NOT ONE", "sources/one.html")])
        result = self.merge_both("--out", str(self.tmp / "merged.json"),
                                 "--copy-sources", str(self.dest))
        self.assert_refused(result, "collision at 2026-10-07/sources/one.html",
                            str(self.a / "sources" / "one.html"),
                            str(self.b / "sources" / "one.html"))

    def test_collision_with_existing_destination_file(self):
        target = self.dest / "2026-10-07" / "sources" / "two.md"
        target.parent.mkdir(parents=True)
        target.write_bytes(b"SOMETHING ELSE")
        result = self.merge_both("--out", str(self.tmp / "merged.json"),
                                 "--copy-sources", str(self.dest))
        self.assertEqual(result.returncode, 1)
        self.assertIn(f"collision at {target}", result.stderr)
        self.assertEqual(target.read_bytes(), b"SOMETHING ELSE")
        self.assertFalse((self.dest / "2026-10-07" / "sources" / "one.html").exists())

    def test_sha256_mismatch(self):
        (self.a / "sources" / "one.html").write_bytes(b"EDITED")
        result = self.merge_both("--out", str(self.tmp / "merged.json"))
        self.assert_refused(result, "hashes to", hashlib.sha256(b"ONE").hexdigest())

    def test_byte_count_mismatch(self):
        entry = record("https://x.invalid/one", b"ONE", "sources/one.html")
        entry["bytes"] = 99
        self.write_log(self.a, [entry])
        result = self.merge_both("--out", str(self.tmp / "merged.json"))
        self.assert_refused(result, "is 3 bytes, the log records 99")

    def test_missing_file(self):
        (self.b / "sources" / "two.md").unlink()
        result = self.merge_both("--out", str(self.tmp / "merged.json"))
        self.assert_refused(result, "names no file")

    def test_unmapped_file(self):
        result = self.run_merge(str(self.a / "fetch-log.json"), str(self.b / "fetch-log.json"),
                                "--map", f"{self.a / 'sources'}=2026-10-07/sources",
                                "--out", str(self.tmp / "merged.json"))
        self.assert_refused(result, "under no --map OLD_PREFIX")

    def test_prefix_matches_whole_components(self):
        result = self.run_merge(str(self.b / "fetch-log.json"),
                                "--map", f"{self.b / 'sourc'}=2026-10-07/sources",
                                "--out", str(self.tmp / "merged.json"))
        self.assert_refused(result, "under no --map OLD_PREFIX")

    def test_dry_run_still_refuses(self):
        (self.a / "sources" / "one.html").write_bytes(b"EDITED")
        result = self.merge_both("--dry-run")
        self.assertEqual(result.returncode, 1)

    def test_absolute_new_prefix_is_a_usage_error(self):
        result = self.run_merge(str(self.a / "fetch-log.json"),
                                "--map", f"{self.a / 'sources'}=/abs/sources", "--dry-run")
        self.assertEqual(result.returncode, 2)
        self.assertIn("NEW_PREFIX must be a relative path", result.stderr)

    def test_out_is_required_without_dry_run(self):
        result = self.merge_both()
        self.assertEqual(result.returncode, 2)


if __name__ == "__main__":
    unittest.main()
