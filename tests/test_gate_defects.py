"""Regression tests for gate defects that a plant cannot isolate on real data.

    python3 -m unittest discover -s tests

Each test builds the smallest pass directory that reproduces one defect, runs
the one check involved, and asserts on the messages it appends to the shared
`failures` list. The plants in tools/make-plants.py cover the same defects on
real repository data where a one-cell change can show them.
"""
from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from gate import arithmetic, models, provenance, report, sources
from gate.common import failures, number_from_words
from gate.registry import CHECKS


class GateCase(unittest.TestCase):
    """A temporary pass directory and a clean `failures` list per test."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.pass_dir = Path(self._tmp.name) / "2026-01-01"
        (self.pass_dir / "data").mkdir(parents=True)
        (self.pass_dir / "sources").mkdir()
        self._saved = list(failures)
        failures.clear()

    def tearDown(self):
        failures.clear()
        failures.extend(self._saved)
        self._tmp.cleanup()

    def write(self, relative: str, text: str) -> Path:
        path = self.pass_dir / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def tagged(self, tag: str) -> list[str]:
        return [m for m in failures if m.startswith(f"[{tag}]")]


class NumberWords(unittest.TestCase):
    def test_reads_zero_to_ninety_nine(self):
        cases = {
            "zero": 0, "ten": 10, "Twenty": 20, "twenty-one": 21, "twenty one": 21,
            "forty-two": 42, "ninety-nine": 99, "nineteen": 19, "21": 21, "7": 7,
        }
        for text, value in cases.items():
            self.assertEqual(number_from_words(text), value, text)

    def test_refuses_what_is_not_a_number(self):
        for text in ("umpteen", "a hundred", "twenty-ten", "ten-one", "one-two",
                     "twenty-zero", "all twenty", "the", ""):
            self.assertIsNone(number_from_words(text), text)


class GateCountClaims(GateCase):
    def claim(self, count: str) -> list[str]:
        self.write("README.md", f"# pass\n\nGated on **{count} checks**.\n")
        report.check_gate_count_claims(self.pass_dir)
        return self.tagged("gate-count-claims")

    def test_ten_is_compared(self):
        self.assertEqual(len(self.claim("ten")), 1)

    def test_hyphenated_compound_is_compared(self):
        found = self.claim("twenty-one")
        self.assertEqual(len(found), 1)
        self.assertIn("says the gate runs 21 checks", found[0])

    def test_unreadable_count_is_a_failure(self):
        found = self.claim("umpteen")
        self.assertEqual(len(found), 1)
        self.assertIn("cannot read as a number", found[0])

    def test_the_registered_count_passes_in_digits(self):
        self.assertEqual(self.claim(str(len(CHECKS))), [])

    def test_the_registered_count_passes_in_words(self):
        words = {n: w for w, n in (("ten", 10), ("twenty", 20), ("thirty", 30))}
        units = ("", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine")
        n = len(CHECKS)
        self.assertTrue(20 <= n <= 39, "extend this test's word table for this count")
        tens = words[(n // 10) * 10]
        spelled = tens if n % 10 == 0 else f"{tens}-{units[n % 10]}"
        self.assertEqual(self.claim(spelled), [])


class CostIdentityGroups(GateCase):
    HEADER = "plan,model,traffic_mix,tokens_m,monthly_pool_usd,usd_per_mtok\n"

    def run_check(self, body: str) -> list[str]:
        self.write("data/t.csv", self.HEADER + body)
        arithmetic.check_cost_identity(self.pass_dir)
        return self.tagged("cost-identity")

    def test_same_rate_different_tokens_is_refused(self):
        found = self.run_check("P,M,A,100,,1.0\nP,M,A,200,,1.0\n")
        self.assertEqual(len(found), 1, found)
        self.assertIn("tokens_m differs by 2.00x", found[0])

    def test_message_does_not_claim_an_empty_pool(self):
        found = self.run_check("P,M,A,100,,1.0\nP,M,A,200,,1.0\n")
        self.assertIn("neither carries a dollar ceiling", found[0])
        self.assertNotIn("both carry", found[0])

    def test_rate_and_tokens_in_inverse_proportion_pass(self):
        self.assertEqual(self.run_check("P,M,A,100,,1.0\nP,M,A,50,,2.0\n"), [])

    def test_different_mix_is_a_different_group(self):
        self.assertEqual(self.run_check("P,M,A,100,,1.0\nP,M,B,200,,1.0\n"), [])


class MissingCitationReportedOnce(GateCase):
    def test_count_citation_of_missing_file(self):
        self.write("README.md", "# r\n\nThe file data/missing.csv (3 rows) is cited.\n")
        report.check_report_matches_data(self.pass_dir)
        self.assertEqual(len(self.tagged("report-matches-data")), 1, failures)

    def test_link_citing_the_path_twice(self):
        self.write("README.md", "# r\n\nSee [data/x.csv](data/x.csv) and data/x.csv.\n")
        report.check_report_matches_data(self.pass_dir)
        self.assertEqual(len(self.tagged("report-matches-data")), 1, failures)

    def test_cross_pass_citation(self):
        self.write("README.md",
                   "# r\n\nSee data/2026-09-01/data/x.csv and ../2026-09-01/data/x.csv.\n")
        report.check_report_matches_data(self.pass_dir)
        self.assertEqual(len(self.tagged("report-matches-data")), 1, failures)

    def test_present_file_is_silent(self):
        self.write("data/x.csv", "a,b\n1,2\n")
        self.write("README.md", "# r\n\nSee [data/x.csv](data/x.csv) (1 row).\n")
        report.check_report_matches_data(self.pass_dir)
        self.assertEqual(failures, [])


class UntieredMessage(GateCase):
    def test_tier_message_reads_untiered(self):
        self.write("data/models-database.csv", "slug,name,intelligenceIndex\nfoo-1,Foo 1,40\n")
        self.write("data/plan-economics.csv", "plan,model,model_slug,aa_score\nP,Foo 1 Pro,foo-1,40\n")
        models.check_unscored_model(self.pass_dir)
        found = self.tagged("unscored-model")
        self.assertEqual(len(found), 1, failures)
        self.assertIn("names the untiered base model", found[0])


class OneMoneyNormalisation(GateCase):
    """Both money checks read the page through `_money_on_page` and the cell
    through `_normalise_money`, so they agree on what a page contains."""

    def test_normaliser(self):
        for raw, want in (("1,200.00", "1200"), ("10", "10"), ("10.50", "10.5"),
                          ("0.0070", "0.007"), (" 18 ", "18")):
            self.assertEqual(sources._normalise_money(raw), want, raw)

    def test_page_forms(self):
        page = 'Pro is $1,200.00 a year, Lite 18 USD, {"price": "10.0"} and $0.007.'
        self.assertEqual(sources._money_on_page(page), {"1200", "18", "10", "0.007"})

    def test_ladder_uses_the_shared_page_reader(self):
        self.write("sources/p.html", "<p>Max is $1,200.00 per year.</p>")
        self.write("data/plan-ladder.csv",
                   "plan,vendor_source,price_value,extraction\nMax,p.html,1200,PROSE\n"
                   "Pro,p.html,10,PROSE\n")
        sources.check_ladder_prices_on_page(self.pass_dir)
        found = self.tagged("ladder-price-on-page")
        self.assertEqual(len(found), 1, failures)
        self.assertIn("data row 2: 10 is attributed", found[0])

    def test_ladder_has_no_private_normaliser(self):
        source = Path(sources.__file__).read_text(encoding="utf-8")
        self.assertEqual(source.count('rstrip("0").rstrip(".")'), 1,
                         "money normalisation is implemented in more than one place")


class QuotedMoneyReadsSubfolders(GateCase):
    """A reference entry citing `sources/<topic>/page` is checked against that
    page. Before this check walked subfolders, every nested source was skipped
    and a fabricated figure on a nested citation passed."""

    ENTRY = "**[R1] Vendor** ([page](../sources/vendor/page.html))\n\nPro costs $%s a month.\n"

    def run_check(self, figure: str) -> list[str]:
        self.write("sources/vendor/page.html", "<p>Pro costs $18 a month.</p>")
        self.write("references/references.md", self.ENTRY % figure)
        sources.check_quoted_money_on_page(self.pass_dir)
        return self.tagged("quoted-money-on-page")

    def test_fabricated_figure_on_nested_source_is_refused(self):
        found = self.run_check("99")
        self.assertEqual(len(found), 1, failures)
        self.assertIn("quotes $99", found[0])

    def test_correct_figure_on_nested_source_is_accepted(self):
        self.assertEqual(self.run_check("18"), [], failures)


class FetchLogPathResolution(GateCase):
    """`fetch-log-corroborates` reads every spelling of `saved_as` in use."""

    def log(self, entries: list[dict]) -> None:
        self.write("data/fetch-log.json", json.dumps(entries))

    def entry(self, saved: str, body: bytes) -> dict:
        return {"url": "https://example.invalid/" + saved, "http": 200,
                "bytes": len(body), "sha256": hashlib.sha256(body).hexdigest(),
                "saved_as": saved}

    def run_check(self) -> list[str]:
        provenance.check_dates(self.pass_dir)
        return self.tagged("fetch-log-corroborates")

    def test_windows_separators_from_old_logs(self):
        self.write("sources/a.md", "A")
        self.log([self.entry("2026-01-01\\sources\\a.md", b"A")])
        self.assertEqual(self.run_check(), [])

    def test_posix_relative_to_root_and_to_pass(self):
        self.write("sources/a.md", "A")
        self.write("sources/b.md", "B")
        self.log([self.entry("2026-01-01/sources/a.md", b"A"),
                  self.entry("sources/b.md", b"B")])
        self.assertEqual(self.run_check(), [])

    def test_nested_source_is_found_where_the_log_says(self):
        self.write("sources/github/x.ts", "X")
        self.write("sources/x.ts", "different bytes, same basename")
        self.log([self.entry("2026-01-01/sources/github/x.ts", b"X"),
                  self.entry("2026-01-01/sources/x.ts", b"different bytes, same basename")])
        self.assertEqual(self.run_check(), [])

    def test_nested_hash_mismatch_is_refused(self):
        self.write("sources/github/x.ts", "edited")
        self.log([self.entry("2026-01-01/sources/github/x.ts", b"X")])
        found = self.run_check()
        self.assertEqual(len(found), 1, found)
        self.assertIn("does not hash", found[0])

    def test_nested_unlogged_source_is_refused(self):
        self.write("sources/a.md", "A")
        self.write("sources/github/orphan.ts", "O")
        self.log([self.entry("2026-01-01/sources/a.md", b"A")])
        found = self.run_check()
        self.assertEqual(len(found), 1, found)
        self.assertIn("github/orphan.ts", found[0])
        self.assertIn("has no entry", found[0])


if __name__ == "__main__":
    unittest.main()
