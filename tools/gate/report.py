"""Prose checks: counts and paths a document states must match the registry and the data."""
from __future__ import annotations

import json
import re
from pathlib import Path

from . import registry
from .common import (
    NUM_WORDS, ROOT, TOOLS, data_rows, failures, number_from_words, read_rows, rel,
)
from .registry import CHECKS


def check_gate_count_claims(pass_dir: Path) -> None:
    """A document that states how many checks this gate runs must state it right.

    The root README, a pass report and the gate's own docstring have all, at
    different times, carried a number that had drifted from the registry. A count
    that is wrong is not a typo: a reader uses it to decide whether the gate
    covers what they are about to rely on. The registry is the authority and the
    documents are checked against it.

    The gate's own source is read as the entry point `tools/validate.py` plus
    every module of `tools/gate/`, because the docstrings that describe the gate
    moved into the package when the single file was split, and a count stated in
    any of them is a count a reader will rely on.

    A count claim is a bold run (two asterisks) opening with one or two words,
    or digits, immediately followed by the word "checks", such as "twenty",
    "21" or "twenty-one" in bold before it. The examples are written without
    the asterisks here because this docstring is itself one of the documents
    this check reads. The count is read by `number_from_words`, which covers
    zero to ninety-nine. A claim in that position whose count cannot be read is
    a failure, not a pass: the first version knew only "eleven" to "twenty", so
    a bold "ten checks" or "twenty-one checks" was never compared with anything
    and the gate reported it as correct.
    """
    pattern = re.compile(
        r"\*\*(\d+|[A-Za-z]+(?:[-\s][A-Za-z]+)?)\s+checks\b", re.IGNORECASE
    )
    gate_sources = [TOOLS / "validate.py"] + sorted((TOOLS / "gate").glob("*.py"))
    for path in [ROOT / "README.md", pass_dir / "README.md"] + gate_sources:
        if not path.is_file():
            continue
        for offset, line in enumerate(
            path.read_text(encoding="utf-8", errors="replace").splitlines(), start=1
        ):
            for match in pattern.finditer(line):
                token = match.group(1)
                claimed = number_from_words(token)
                if claimed is None:
                    failures.append(
                        f"[gate-count-claims] {rel(path)} line {offset} states a count of "
                        f"checks as {token!r}, which the gate cannot read as a number, so "
                        f"it cannot be compared with the {len(CHECKS)} CHECKS registers. "
                        f"Write the count in digits or in words from zero to ninety-nine."
                    )
                    continue
                if claimed != len(CHECKS):
                    failures.append(
                        f"[gate-count-claims] {rel(path)} line {offset} says the gate runs "
                        f"{claimed} checks; CHECKS in {rel(Path(registry.__file__))} registers "
                        f"{len(CHECKS)}"
                    )


def check_report_matches_data(pass_dir: Path) -> None:
    """A path, a row count or a fetch tally the prose states must match disk.

    Three quantities are compared against the files on disk: a cited `data/`
    path, a row count the prose states for that CSV, and - through
    `_check_fetch_tallies` - the count of retrievals the report states against
    `data/fetch-log.json`. All three are claims a reader cannot check by eye.
    """
    report = pass_dir / "README.md"
    data = pass_dir / "data"
    if not report.is_file() or not data.is_dir():
        return
    text = report.read_text(encoding="utf-8", errors="replace")

    # "N rows", "N-row", "N rows per plan", immediately after a data/ path, and
    # the plainer form where the file is named and "N rows" follows.
    #
    # The third form was added because the first two missed most of a header
    # paragraph. Its citations are `(20 plan x model rows)`, `(6 independent
    # meter readings)` and `(16 SKU lookups ...)`: the count leads and the noun
    # varies, so a pattern keyed on "N rows" matched exactly one of the five
    # citations beside it. Changing "25 model rows" to "24", or "20 plan x model
    # rows" to "21", left the gate at exit 0 with a wrong number in the prose.
    # This one keys on the count itself in the parenthetical that opens right
    # after the path, so the noun does not matter. It is deliberately tighter
    # than the second: it requires the count to be the first thing inside the
    # bracket, which is where this pass writes it, so a number appearing later
    # in a sentence is not read as this file's count.
    patterns = (
        re.compile(r"data/([A-Za-z0-9._-]+\.csv)\)?\s*\((\d+)[- ]row", re.IGNORECASE),
        re.compile(r"data/([A-Za-z0-9._-]+\.csv)\b[^.\n]{0,40}?\b(\d+)\s+rows?\b",
                   re.IGNORECASE),
        re.compile(r"data/([A-Za-z0-9._-]+\.csv)\)?\s*\(\s*(\d+)\b", re.IGNORECASE),
    )
    for pattern in patterns:
        for match in pattern.finditer(text):
            name, claimed = match.group(1), int(match.group(2))
            path = data / name
            if not path.is_file():
                # A missing file is reported once, by the citation sweep below,
                # which sees every data/ path whatever form cites it. Reporting
                # it here as well printed the same failure once per pattern.
                continue
            _, rows = read_rows(path)
            actual = len(data_rows(rows))
            if actual != claimed:
                failures.append(
                    f"[report-matches-data] {rel(report)} says data/{name} has "
                    f"{claimed} rows, it has {actual}"
                )

    # Each missing target is reported once, whichever sweep sees it first and
    # however many times or forms the report cites it in.
    reported: set[Path] = set()

    # A `data/<pass>/data/<name>.csv` path is wrong unless that pass holds that file.
    for match in re.finditer(r"data/(\d{4}-\d{2}-\d{2})/data/([A-Za-z0-9._-]+\.csv)", text):
        other, name = match.group(1), match.group(2)
        target = ROOT / other / "data" / name
        if not target.is_file() and target not in reported:
            reported.add(target)
            failures.append(
                f"[report-matches-data] {rel(report)} cites data/{other}/data/{name}, "
                f"which does not exist. The pass is {pass_dir.name} and it holds no "
                f"{name}."
            )

    # Any other data/<name>.csv the report names must be in this pass's data/, or
    # in another pass's - a cross-pass citation names the other pass explicitly,
    # and that is a path a reader can open.
    citation = re.compile(
        r"(?:(?:\.\./)?(\d{4}-\d{2}-\d{2})/)?data/([A-Za-z0-9._-]+\.csv)"
    )
    for match in citation.finditer(text):
        other, name = match.group(1), match.group(2)
        target = ROOT / other / "data" / name if other else data / name
        if target.is_file() or target in reported:
            continue
        reported.add(target)
        where = rel(ROOT / other / "data") if other else rel(data)
        failures.append(
            f"[report-matches-data] {rel(report)} cites data/{name} but it is not "
            f"in {where}/"
        )

    _check_fetch_tallies(pass_dir, report, text)


def _fetch_tallies(pass_dir: Path) -> dict[str, int] | None:
    """The log's own counts, or None when this pass keeps no fetch log.

    `entries` is every recorded retrieval, `ok` the subset that returned HTTP 200,
    `archived` the distinct files the log says it wrote and `on_disk` the sources
    actually committed. The four are different quantities and the gap between
    `entries` and `archived` is the interesting one: re-fetching a page whose
    bytes came back unchanged records a retrieval without archiving a second copy,
    so a report that says "twelve fetches" and "ten distinct results" can be
    right on both and still read as a contradiction.
    """
    log = pass_dir / "data" / "fetch-log.json"
    if not log.is_file():
        return None
    try:
        entries = json.loads(log.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    if not isinstance(entries, list):
        return None
    sources = pass_dir / "sources"
    return {
        "entries": len(entries),
        "ok": sum(1 for e in entries if str(e.get("http")) == "200"),
        "archived": len({str(e.get("saved_as") or "").replace(chr(92), "/").split("/")[-1]
                         for e in entries if e.get("saved_as")}),
        "on_disk": len([p for p in sources.iterdir() if p.is_file()]) if sources.is_dir() else 0,
    }


def _check_fetch_tallies(pass_dir: Path, report: Path, text: str) -> None:
    """A report's count of its own retrievals must be the log's count.

    The row-count check above compares the report against the CSVs. Nothing
    compared it against `fetch-log.json`, so "Eleven fetches ... 11/11 returned
    200, and the nine distinct results are archived" survived against a log
    holding twelve entries and ten archived files — three wrong numbers, none of
    them near a CSV.

    Three forms are matched, because the counts appear in three grammatical
    positions and a check that reads only one of them reads none of the two
    others:

    * `N/M returned 200`, or the `all N` it is written as when the report says
      every attempt succeeded;
    * `N fetches`, and the spelled-out form;
    * `the N distinct results are archived`.

    A count is only checked in a position whose tally exists, so a pass that
    keeps no fetch log is not asked about numbers it never claimed.
    """
    tallies = _fetch_tallies(pass_dir)
    if tallies is None:
        return
    spelled = "|".join(
        sorted((w for w in NUM_WORDS if 1 <= NUM_WORDS[w] <= 99), key=len, reverse=True)
    )
    token = rf"(\d+|{spelled})"

    def as_int(raw: str) -> int | None:
        raw = raw.strip().lower()
        return int(raw) if raw.isdigit() else NUM_WORDS.get(raw)

    def claimed(match: re.Match, group: int = 1) -> int | None:
        return as_int(match.group(group))

    where = rel(report)

    def fail(position: str, said: int, actual: int) -> None:
        failures.append(
            f"[report-matches-data] {where} says {position} is {said}, "
            f"data/fetch-log.json records {actual}"
        )

    # "11/11 returned 200" - the numerator is the successes and the denominator
    # is the attempts, and both are claims about the same list.
    for match in re.finditer(rf"{token}\s*/\s*{token}\s+returned\s+200", text, re.IGNORECASE):
        numerator, denominator = claimed(match), claimed(match, 2)
        if numerator is not None and numerator != tallies["ok"]:
            fail("the number of fetches that returned 200", numerator, tallies["ok"])
        if denominator is not None and denominator != tallies["entries"]:
            fail("the number of fetches", denominator, tallies["entries"])

    # "all twelve fetches"
    for match in re.finditer(rf"all\s+{token}\s+fetches\b", text, re.IGNORECASE):
        said = claimed(match)
        if said is not None and said != tallies["entries"]:
            fail("the number of fetches", said, tallies["entries"])

    # "the nine distinct results are archived"
    for match in re.finditer(
            rf"{token}\s+distinct\s+(?:results?|sources?|pages?|files?)\s+are\s+archived",
            text, re.IGNORECASE):
        said = claimed(match)
        if said is not None and said != tallies["archived"]:
            fail("the number of distinct results archived", said, tallies["archived"])

    # A bare "20 first-party sources fetched serially", which is the form the
    # 2026-10-02 pass uses.
    for match in re.finditer(
            rf"\b{token}\s+(?:first-party\s+)?(?:fetches|sources)\s+fetched\b",
            text, re.IGNORECASE):
        said = claimed(match)
        if said is not None and said != tallies["entries"]:
            fail("the number of fetches", said, tallies["entries"])
