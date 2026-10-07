"""Structural invariants of the gate in tools/gate/.

    python3 -m unittest discover -s tests

The registry, the run order and the plant manifest each name the checks, and
nothing else holds them against one another. A check registered in CHECKS but
never run reports a coverage the gate does not have; a check run but not
registered escapes `gate-count-claims`; and a check no plant trips has never
been seen refusing anything, which tests/run-plants.sh cannot notice because it
only iterates over the plants that exist.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from gate.registry import CHECKS
from gate.runner import PIPELINE

# Checks that have no plant in tools/make-plants.py, each with the reason one
# cannot be written. An entry here is a known gap in the refusal evidence, not an
# exemption from it, and a check that gains a plant must be removed from here.
PLANTLESS_ALLOWLIST: dict[str, str] = {}

MESSAGE_TAG = re.compile(r"""["']\[([a-z]+(?:-[a-z]+)*)\] """)


def _manifest() -> dict:
    """The manifest tools/make-plants.py writes, generated the way run-plants.sh does."""
    with tempfile.TemporaryDirectory() as out:
        result = subprocess.run(
            [sys.executable, str(TOOLS / "make-plants.py"), str(Path(out) / "plants")],
            cwd=ROOT, stdin=subprocess.DEVNULL, capture_output=True, text=True,
            timeout=600,
        )
        if result.returncode != 0:
            raise AssertionError(
                f"tools/make-plants.py exited {result.returncode}:\n"
                f"{result.stdout}\n{result.stderr}"
            )
        return json.loads((Path(out) / "plants" / "manifest.json").read_text(encoding="utf-8"))


class RegistryMatchesPipeline(unittest.TestCase):
    def test_every_registered_check_is_run(self):
        run = {name for _, names in PIPELINE for name in names}
        self.assertEqual(sorted(set(CHECKS) - run), [],
                         "registered in CHECKS but no PIPELINE function emits it")

    def test_every_run_check_is_registered(self):
        run = {name for _, names in PIPELINE for name in names}
        self.assertEqual(sorted(run - set(CHECKS)), [],
                         "emitted by a PIPELINE function but not registered in CHECKS")

    def test_each_check_has_one_function(self):
        claimed = [name for _, names in PIPELINE for name in names]
        duplicates = sorted({n for n in claimed if claimed.count(n) > 1})
        self.assertEqual(duplicates, [], "a check name is claimed by two PIPELINE entries")

    def test_pipeline_entries_are_distinct_callables(self):
        functions = [run for run, _ in PIPELINE]
        for run in functions:
            self.assertTrue(callable(run), f"{run!r} in PIPELINE is not callable")
        self.assertEqual(len(functions), len(set(functions)), "a function is in PIPELINE twice")

    def test_cli_exposes_the_registry(self):
        import validate
        self.assertIs(validate.CHECKS, CHECKS)


class MessageTagsMatchRegistry(unittest.TestCase):
    """A failure message is attributed by its `[name]` tag, which is what
    tests/run-plants.sh greps for. A tag outside CHECKS is a refusal no plant
    can be matched to, and a registered check whose tag appears in no source
    cannot emit anything at all."""

    @classmethod
    def setUpClass(cls):
        cls.tags: dict[str, set[str]] = {}
        for path in sorted((TOOLS / "gate").glob("*.py")):
            for tag in MESSAGE_TAG.findall(path.read_text(encoding="utf-8")):
                cls.tags.setdefault(tag, set()).add(path.name)

    def test_every_tag_is_registered(self):
        self.assertEqual(sorted(set(self.tags) - set(CHECKS)), [],
                         "a message tag in tools/gate/ is not a CHECKS key")

    def test_every_registered_check_has_a_message(self):
        self.assertEqual(sorted(set(CHECKS) - set(self.tags)), [],
                         "a CHECKS key appears in no failure message in tools/gate/")


class PlantsCoverRegistry(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = _manifest()
        cls.planted = {name for plant in cls.manifest["plants"] for name in plant["expects"]}

    def test_manifest_is_not_empty(self):
        self.assertTrue(self.manifest["plants"], "tools/make-plants.py produced no plants")

    def test_every_planted_check_is_registered(self):
        self.assertEqual(sorted(self.planted - set(CHECKS)), [],
                         "a plant expects a check that is not in CHECKS")

    def test_every_registered_check_is_planted_or_allowlisted(self):
        missing = sorted(set(CHECKS) - self.planted - set(PLANTLESS_ALLOWLIST))
        self.assertEqual(missing, [],
                         "a registered check has no plant and no PLANTLESS_ALLOWLIST reason")

    def test_allowlist_is_current(self):
        self.assertEqual(sorted(set(PLANTLESS_ALLOWLIST) - set(CHECKS)), [],
                         "PLANTLESS_ALLOWLIST names a check that is not registered")
        self.assertEqual(sorted(set(PLANTLESS_ALLOWLIST) & self.planted), [],
                         "PLANTLESS_ALLOWLIST names a check that now has a plant")
        for name, reason in PLANTLESS_ALLOWLIST.items():
            self.assertTrue(reason.strip(), f"PLANTLESS_ALLOWLIST[{name!r}] gives no reason")


if __name__ == "__main__":
    unittest.main()
