#!/usr/bin/env python3
"""Data-integrity gate for a coding-subs research pass.

    python3 tools/validate.py [PASS_DIR]      # default: newest YYYY-MM-DD dir
    python3 tools/validate.py --all           # every pass in the repo

Exit code 0 only when every check passes. Each check exists because a real,
named defect got past the previous validator; the ones with a story are listed
in CHECKS below and the failing-before evidence is in docs/reviews-*.md.

The checks that matter are the ones a reader cannot do by eye:

* field-count agreement. A surplus unquoted comma in a CSV row shifts every
  column after it, and csv.DictReader hides the shift under a None key. Four
  files in the 2026-09-20 pass shipped with that defect while every earlier
  check reported the pass clean.
* unit agreement. A cost row states a price, a token count and a $/M for one
  quantity in three units. If they disagree the row is wrong, and which of the
  three is wrong is not decidable from the row, so the row is not published.
* evidence labelling. A row that carries a number must say where the number
  came from, and a row whose number is not published must say UNKNOWN rather
  than carry a plausible figure.
"""
from __future__ import annotations

import csv
import json
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# name -> (what it enforces, what defect it was added for)
CHECKS: dict[str, str] = {
    "layout": "every pass has data/, references/, sources/ and a README",
    "field-count": "2026-09-20 shipped 38 malformed CSV rows past a green run",
    "cost-arithmetic": "a price, a token count and a $/M must describe one quantity",
    "evidence-label": "a number without a source is not evidence",
    "no-future-pass": "a pass directory cannot be dated after the machine's clock",
    "fetch-log-corroborates": "a pass whose date cannot be checked by a log says so",
    "report-matches-data": "row counts the report quotes must match the CSVs",
    "model-slug-joins": "a plan row naming a model must join to a model in the landscape",
}

failures: list[str] = []


def check(cond: bool, msg: str) -> None:
    if not cond:
        failures.append(msg)


def passes() -> list[Path]:
    return sorted(p for p in ROOT.iterdir() if p.is_dir() and re.fullmatch(r"\d{4}-\d{2}-\d{2}", p.name))


def latest() -> Path:
    found = passes()
    check(bool(found), "no YYYY-MM-DD pass directory found")
    return found[-1] if found else ROOT


def rel(path: Path) -> str:
    """Path relative to the repo root, whether or not ROOT is a prefix of it.

    A pass directory can be passed in as a relative path, and `relative_to`
    raises rather than degrading. Reporting a bare path is better than a
    traceback in a gate that is supposed to be readable.
    """
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def read_rows(path: Path) -> tuple[list[str], list[list[str]]]:
    """Rows of a CSV, skipping a leading prose preamble whose header starts '#'."""
    raw = path.read_text(encoding="utf-8", errors="replace").splitlines()
    start = 0
    while start < len(raw) and raw[start].lstrip().startswith("#"):
        start += 1
    if start >= len(raw):
        return [], []
    rows = list(csv.reader(raw[start:]))
    return (rows[0] if rows else []), rows[1:]


def check_layout(pass_dir: Path) -> None:
    for sub in ("data", "references", "sources"):
        check((pass_dir / sub).is_dir(), f"[layout] missing {sub}/ in {pass_dir.name}")
    check((pass_dir / "README.md").is_file(), f"[layout] missing README.md in {pass_dir.name}")
    check((ROOT / "README.md").is_file(), "[layout] missing root README.md")
    check((ROOT / "docs").is_dir(), "[layout] missing docs/ (reviews live there)")


def check_field_counts(pass_dir: Path) -> None:
    """The check the 2026-09-20 pass needed and did not have."""
    data = pass_dir / "data"
    if not data.is_dir():
        return
    for path in sorted(data.glob("*.csv")):
        header, rows = read_rows(path)
        if not header or len(header) < 2:
            # A single-column ledger is prose or a key/value file, not a table.
            continue
        width = len(header)
        for offset, row in enumerate(rows, start=1):
            if not row or (len(row) == 1 and not row[0].strip()):
                continue
            if len(row) != width:
                failures.append(
                    f"[field-count] {rel(path)} data row {offset} has "
                    f"{len(row)} fields, header has {width} (columns from field "
                    f"{min(len(row), width) + 1} onward are shifted)"
                )


def _num(value):
    try:
        return float(str(value).replace(",", "").replace("$", ""))
    except (TypeError, ValueError):
        return None


def check_cost_arithmetic(pass_dir: Path) -> None:
    """price, tokens and $/M must agree. A row that fails is not publishable.

    The three cells have to be the same quantity in three units, so the columns
    are matched by exact name and the check runs only where all three exist.
    Guessing a column by substring produced a confident nonsense failure on this
    pass's own data, which is worse than having no check, so a file without the
    triple is skipped instead.
    """
    data = pass_dir / "data"
    if not data.is_dir():
        return
    for path in sorted(data.glob("*.csv")):
        header, rows = read_rows(path)
        if not header:
            continue
        index = {name.strip().lower(): i for i, name in enumerate(header)}
        price_col = next((c for c in index if c in ("price_usd_month", "plan_price_usd_month", "price")), None)
        tok_col = next((c for c in index if c in ("monthly_tokens_m", "monthly_tokens", "tokens_m", "tokens_m_at_ceiling")), None)
        per_col = next((c for c in index if c in ("usd_per_mtok", "usd_per_m_tokens")), None)
        if not (price_col and tok_col and per_col):
            continue
        for offset, row in enumerate(rows, start=1):
            if len(row) <= max(index[c] for c in (price_col, tok_col, per_col)):
                continue
            price = _num(row[index[price_col]])
            tokens = _num(row[index[tok_col]])
            per_m = _num(row[index[per_col]])
            if not price or not tokens or not per_m or price <= 0 or tokens <= 0 or per_m <= 0:
                continue
            # monthly_tokens_m is already in millions, so price / tokens is $/M.
            expected = price / tokens
            ratio = expected / per_m
            if not (0.95 <= ratio <= 1.05):
                shown = row[index[per_col]]
                failures.append(
                    f"[cost-arithmetic] {rel(path)} data row {offset}: "
                    f"price {price} / {tokens:g}M tokens = ${expected:.4f}/M but the row "
                    f"states ${shown}/M ({ratio:.2f}x off)"
                )


def check_evidence_labels(pass_dir: Path) -> None:
    """Every number must be attributable, or explicitly marked unknown."""
    data = pass_dir / "data"
    if not data.is_dir():
        return
    label_cols = ("source", "source_quality", "confidence", "evidence", "class")
    for path in sorted(data.glob("*.csv")):
        header, rows = read_rows(path)
        if not header:
            continue
        index = {name.strip().lower(): i for i, name in enumerate(header)}
        present = [c for c in label_cols if any(c in name for name in index)]
        if not present:
            continue
        for offset, row in enumerate(rows, start=1):
            if len(row) != len(header) or not any(c.strip() for c in row):
                continue
            values = [row[index[name]].strip() for name in index if any(c in name for c in present)]
            if not any(values):
                failures.append(
                    f"[evidence-label] {rel(path)} data row {offset} has "
                    f"no source/quality/confidence value"
                )


def check_dates(pass_dir: Path) -> None:
    today = str(date.today())
    check(pass_dir.name <= today, f"[no-future-pass] {pass_dir.name} is after the machine date {today}")
    log = pass_dir / "data" / "fetch-log.json"
    if pass_dir.name == today and not log.is_file():
        check(
            False,
            f"[fetch-log-corroborates] pass is dated today ({today}) but "
            f"{rel(log)} is absent, so the date cannot be checked",
        )
    if log.is_file():
        try:
            entries = json.loads(log.read_text())
        except json.JSONDecodeError as exc:
            failures.append(f"[fetch-log-corroborates] {rel(log)} is not valid JSON: {exc}")
            return
        if not isinstance(entries, list) or not entries:
            failures.append(f"[fetch-log-corroborates] {rel(log)} has no entries")
            return
        for entry in entries:
            if not all(k in entry for k in ("url", "http", "sha256")):
                failures.append(
                    f"[fetch-log-corroborates] an entry in {rel(log)} is missing "
                    f"url/http/sha256, so it cannot be checked against a source"
                )
                break


def check_report_matches_data(pass_dir: Path) -> None:
    """A row count in the prose is a claim about the CSV, so check it.

    The 2026-10-02 report said "76 rows" for a file with 78. A reader cannot
    tell which is right without opening both, so the gate compares them.
    """
    report = pass_dir / "README.md"
    data = pass_dir / "data"
    if not report.is_file() or not data.is_dir():
        return
    text = report.read_text(encoding="utf-8", errors="replace")
    # "N rows", "N-row", "N rows per plan" immediately after a data/ path
    for match in re.finditer(r"data/([A-Za-z0-9._-]+\.csv)\)?\s*\((\d+)[- ]row", text):
        name, claimed = match.group(1), int(match.group(2))
        path = data / name
        if not path.is_file():
            failures.append(f"[report-matches-data] report cites data/{name} but it is not in {rel(data)}/")
            continue
        header, rows = read_rows(path)
        actual = len([r for r in rows if r and any(c.strip() for c in r)])
        if actual != claimed:
            failures.append(
                f"[report-matches-data] report says data/{name} has {claimed} rows, it has {actual}"
            )


def check_model_slug_joins(pass_dir: Path) -> None:
    """A plan row that names a model must join to a row in the model database.

    The plan table carries display names ("GLM-5.3-Flash") and the model
    database carries slugs ("glm-5-3-flash"). Joining them on the display name
    silently yields an empty ranking: the first version of this pass's ranked
    table was empty for exactly that reason and said nothing was wrong. A row
    whose model has no counterpart is therefore an error, not a gap.
    """
    data = pass_dir / "data"
    models = data / "models-database.csv"
    plans = data / "plan-economics.csv"
    if not models.is_file() or not plans.is_file():
        return
    mheader, mrows = read_rows(models)
    pheader, prows = read_rows(plans)
    if "slug" not in mheader or "model_slug" not in pheader:
        return
    mi = mheader.index("slug")
    pi = pheader.index("model_slug")
    known = {r[mi].strip() for r in mrows if len(r) > mi}
    for offset, row in enumerate(prows, start=1):
        if len(row) <= pi:
            continue
        slug = row[pi].strip()
        if not slug or slug == "UNKNOWN":
            continue
        if slug not in known:
            failures.append(
                f"[model-slug-joins] {rel(plans)} data row {offset} names model_slug "
                f"{slug!r}, which is not in data/models-database.csv"
            )


def validate(pass_dir: Path) -> None:
    check_layout(pass_dir)
    check_dates(pass_dir)
    check_field_counts(pass_dir)
    check_cost_arithmetic(pass_dir)
    check_evidence_labels(pass_dir)
    check_report_matches_data(pass_dir)
    check_model_slug_joins(pass_dir)


def main() -> int:
    args = sys.argv[1:]
    if "--all" in args:
        targets = passes()
        if not targets:
            print("no pass directories found")
            return 1
    elif args:
        targets = [Path(a) for a in args]
    else:
        targets = [latest()]

    for pass_dir in targets:
        before = len(failures)
        validate(pass_dir)
        added = len(failures) - before
        print(f"{pass_dir.name}: {'OK' if not added else f'{added} failure(s)'}")

    if failures:
        print(f"\nFAIL ({len(failures)}):")
        for message in failures:
            print("  -", message)
        return 1
    print("\nOK: all checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
