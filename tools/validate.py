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

Four further properties, added after the 2026-10-06 pass found four more
defects a reader cannot see:

* unit scale. A token figure whose magnitude disagrees with its own column
  header is a units error, and a CJK magnitude suffix copied out of a note
  rather than converted produces exactly that error. 25.81亿 was read as
  25.81 billion when the stored row said 2581000000.
* unscored models. A capability score must be traceable to a row of the
  leaderboard payload or be marked notFound. A score inherited from a
  different SKU is indistinguishable from a score, and that is how an unscored
  contributor tier came to be ranked at its base model's Intelligence Index.
* shared caps. A per-model ceiling means nothing without saying whether it is
  independent or drawn against a shared monthly pool, because the two differ by
  the number of models used in the month.
* declared mixes. A derived $/M or tokens/month figure whose row does not state
  the traffic mix it was computed under is a figure with a hidden divisor.
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
    "field-columns": "an arity-preserving column shift puts every value in the wrong column",
    "cost-arithmetic": "a price, a token count and a $/M must describe one quantity",
    "evidence-label": "a number without a source is not evidence",
    "no-future-pass": "a pass directory cannot be dated after the machine's clock",
    "fetch-log-corroborates": "a pass whose date cannot be checked by a log says so",
    "report-matches-data": "row counts the report quotes must match the CSVs",
    "model-slug-joins": "a plan row naming a model must join to a model in the landscape",
    "ladder-price-on-page": "a ladder price must appear in the page it cites",
    "quoted-money-on-page": "a figure quoted in references/*.md must be on the page it cites",
    "unit-scale": "25.81亿 (10^8) was read as 25.81 billion and reached a headline verdict",
    "unscored-model": "a score inherited from a different SKU ranks as a real capability score",
    "shared-cap": "a per-model ceiling was published without saying the ceilings share a pool",
    "mix-declared": "a derived $/M or tokens/month figure whose row omits its traffic mix",
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


# A column name states what kind of value belongs in it. A row whose field count
# is right but whose values do not match their header names has been shifted
# sideways: a surplus unquoted comma paired with a missing empty cell keeps the
# arity and defeats the count check entirely. That is not a hypothetical - it is
# how 2026-10-06/data/relay-providers.csv carried a URL in its evidence-class
# column and a date in its source column while the gate reported the file clean.
#
# Each entry is deliberately narrow, and the set is small on purpose. A pattern
# wide enough to catch a shift is also wide enough to reject correct data, and a
# check that rejects correct data is worse than one that passes a defect. Three
# attempts at a wider set failed on this repo's own history: a pattern on
# `evidence` rejected 37 rows of 2026-09-20's agents-universe.csv that
# legitimately hold a URL or a file path, a pattern on `source_quality` rejected
# 43 rows of 2026-09-13's providers-database.csv whose values are free text by
# design ("VERIFIED official docs"), and a pattern on `model_slug` rejected 100+
# rows of 2026-10-02's mix-sensitivity-all.csv, where the column holds display
# names rather than slugs. Only columns whose values are a URL, a date or a
# yes/no are checked, because nothing else is reliably typed across passes.
COLUMN_VALUE_PATTERNS: tuple[tuple[str, str], ...] = (
    ("source_url", r"^https?://\S+$"),
    ("read_date", r"^\d{4}-\d{2}-\d{2}$"),
    ("lookup_verdict", r"^(scored|notFound|noIndex|scored-\d{4}-\d{2}-\d{2})$"),
    ("present_on_board", r"^(yes|no)$"),
)


def check_column_values(pass_dir: Path) -> None:
    """A cell must hold the kind of value its column name promises.

    `field-count` catches a row with the wrong number of fields. It cannot catch
    a row with the right number of fields whose values have slid sideways, and a
    sideways shift is the quieter failure: the file parses, the arity is right,
    and every value from the shift onward reads as plausible content of the wrong
    kind. This check reads the values against the header names.
    """
    data = pass_dir / "data"
    if not data.is_dir():
        return
    for path in sorted(data.glob("*.csv")):
        header, rows = read_rows(path)
        if not header:
            continue
        expectations = []
        for i, name in enumerate(header):
            lowered = name.strip().lower()
            for key, pattern in COLUMN_VALUE_PATTERNS:
                if lowered == key:
                    expectations.append((i, lowered, re.compile(pattern)))
        if not expectations:
            continue
        for offset, row in enumerate(rows, start=1):
            if not row or len(row) != len(header):
                continue
            for i, name, pattern in expectations:
                value = row[i].strip()
                if not value:
                    continue
                if pattern.match(value):
                    continue
                failures.append(
                    f"[field-columns] {rel(path)} data row {offset}: column "
                    f"{name!r} holds {value!r}, which is not a value of the kind "
                    f"that column is for. Either this value belongs in another "
                    f"column or the row has slid sideways: a surplus unquoted "
                    f"comma paired with a missing empty cell keeps the field "
                    f"count correct while shifting every value after it."
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

    The one legitimate exception is a SKU the leaderboard does not carry at all,
    and it has to be said so rather than inferred: a row whose
    `aa_score_provenance` cell begins `unscored:` is declaring that the leaderboard
    has no row for it. Skipping those is not a loophole, because `unscored-model`
    below requires the marker to be present whenever the score cannot be joined,
    so marking the absence is the only way through, and an unmarked mismatch still
    fails here.
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
    pi_prov = pheader.index("aa_score_provenance") if "aa_score_provenance" in pheader else None
    known = {r[mi].strip() for r in mrows if len(r) > mi}
    for offset, row in enumerate(prows, start=1):
        if len(row) <= pi:
            continue
        slug = row[pi].strip()
        if not slug or slug == "UNKNOWN":
            continue
        if slug in known:
            continue
        prov = row[pi_prov].strip().lower() if pi_prov is not None and len(row) > pi_prov else ""
        if prov.startswith("unscored:"):
            continue
        failures.append(
            f"[model-slug-joins] {rel(plans)} data row {offset} names model_slug "
            f"{slug!r}, which is not in data/models-database.csv and is not marked "
            f"unscored: in aa_score_provenance"
        )


def check_ladder_prices_on_page(pass_dir: Path) -> None:
    """A ladder price must appear in the bytes of the page it cites.

    The plan ladder records, per row, which archived page the figure was read
    from. Verifying each price against that page found four of thirty rows whose
    cited page does not contain the price: Z.ai's overview page publishes only
    "starting at just 18 USD", so the Pro and Max prices attributed to it came
    from an earlier pass. A price with the wrong provenance is worse than a
    missing one, because it looks sourced.
    """
    ladder = pass_dir / "data" / "plan-ladder.csv"
    sources = pass_dir / "sources"
    if not ladder.is_file() or not sources.is_dir():
        return
    header, rows = read_rows(ladder)
    if "vendor_source" not in header or "price_value" not in header:
        return
    src_i, price_i = header.index("vendor_source"), header.index("price_value")
    ext_i = header.index("extraction") if "extraction" in header else None

    money_on_page: dict[str, set[str]] = {}
    for path in sorted(sources.iterdir()):
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        # Normalise thousands separators and the ".00" a page may or may not print,
        # so $1,200 and 1200 and 1200.00 compare equal. Three forms are collected
        # because a vendor writes its price three ways: "$18" in prose, "18 USD"
        # in a sentence, and "price":18 in a JSON-LD Offer block. Checking only
        # the first reports correct rows as missing, which is a false positive
        # that trains a reader to ignore the check.
        found = set()

        def add(token: str) -> None:
            token = token.replace(",", "").strip()
            if token:
                found.add(token.rstrip("0").rstrip(".") if "." in token else token)

        for token in re.findall(r"\$\s?([\d,]+(?:\.\d+)?)", text):
            add(token)
        for token in re.findall(r"(\d+(?:\.\d+)?)\s*(?:USD|dollars)\b", text):
            add(token)
        for token in re.findall(r'"price"\s*:\s*"?([\d.]+)"?', text):
            add(token)
        money_on_page[path.name] = found

    for offset, row in enumerate(rows, start=1):
        if len(row) <= max(src_i, price_i):
            continue
        page, price = row[src_i].strip(), row[price_i].strip()
        if not price or price == "UNKNOWN" or not page:
            continue
        if ext_i is not None and len(row) > ext_i and row[ext_i].strip() in (
            "NOT-ON-PAGE", "NOT-PUBLISHED", "CARRIED-FORWARD",
        ):
            continue
        # Normalise the same way `add` does: strip a trailing ".00", not every
        # trailing zero. `rstrip("0")` on "10" yields "1", which reports a price
        # the page plainly contains as missing.
        norm = price.replace(",", "").strip()
        if "." in norm:
            norm = norm.rstrip("0").rstrip(".")
        if norm not in money_on_page.get(page, set()):
            failures.append(
                f"[ladder-price-on-page] {rel(ladder)} data row {offset}: {price} is attributed to "
                f"sources/{page}, which does not contain that figure. Re-read the page, or mark the "
                f"row NOT-ON-PAGE / CARRIED-FORWARD."
            )


# --- the 2026-10-06 checks -------------------------------------------------
#
# Each of the four below was written after a specific defect reached a
# published verdict, and each is demonstrated twice in
# docs/reviews-2026-10-06.md: once against a planted defect, once against the
# corrected data. A check that has only been seen failing is indistinguishable
# from a check that cannot pass.


def _money_on_page(text: str) -> set[str]:
    """Every money figure a page carries, normalised for comparison.

    A vendor writes the same price several ways: "$18" in prose, "18 USD" in a
    sentence, and `"price":18` in a JSON-LD Offer block, and a price of $10 may
    be printed as 10, 10.0 or 10.00. Checking only the first form reports correct
    figures as missing, which is a false positive that trains a reader to ignore
    the check, so all three forms are collected and normalised the same way.
    """
    found: set[str] = set()

    def add(token: str) -> None:
        token = token.replace(",", "").strip()
        if token:
            found.add(token.rstrip("0").rstrip(".") if "." in token else token)

    for token in re.findall(r"\$\s?([\d,]+(?:\.\d+)?)", text):
        add(token)
    for token in re.findall(r"(\d+(?:\.\d+)?)\s*(?:USD|dollars)\b", text):
        add(token)
    for token in re.findall(r'"price"\s*:\s*"?([\d.]+)"?', text):
        add(token)
    return found


def _normalise_money(value: str) -> str:
    norm = value.replace(",", "").strip()
    return norm.rstrip("0").rstrip(".") if "." in norm else norm


def check_quoted_money_on_page(pass_dir: Path) -> None:
    """A money figure quoted in references/*.md must be on the page it cites.

    `ladder-price-on-page` above does this for the plan-ladder CSV, and it found
    four rows whose cited page did not contain the price. It returns early unless
    `data/plan-ladder.csv` exists, and only the 2026-10-02 pass has one, so the
    check never touched the pass that needed it.

    The defect this was written for is worse than a missing price. 2026-10-06's
    references file quoted the DeepSeek price table as "off-peak $0.007 cache
    hit / $0.22 input miss / $0.66 output; peak $0.014 / $0.44 / $1.32". Four of
    those six figures are not on the page, and they propagated into a blended
    rate, two cost-per-10B figures, two multipliers and the relay ratio. A
    fabricated quotation is indistinguishable from a real one in the file it sits
    in, so the only defence is comparing the quoted figure against the archived
    bytes.

    Every `$N` figure in a references file is checked against the archived source
    the same entry cites. A figure that is not on that page is reported. Where an
    entry deliberately quotes a superseded figure to record a correction, the
    entry carries a `CORRECTED` marker naming the date and the check skips it -
    a correction is documented, not deleted, and the marker is what tells the two
    apart.
    """
    references = pass_dir / "references"
    sources = pass_dir / "sources"
    if not references.is_dir() or not sources.is_dir():
        return

    pages: dict[str, set[str]] = {}
    for path in sorted(sources.iterdir()):
        if path.is_file():
            pages[path.name] = _money_on_page(
                path.read_text(encoding="utf-8", errors="replace")
            )

    # A money figure derived by dividing two published numbers is not on the
    # page and is not expected to be; a per-1M rate blended from a table is the
    # same. Those are checked by arithmetic elsewhere, not here.
    derived_markers = ("per 1m", "/m", "blended", "per mtok", "per month x", "x 4.33")

    # Each `**[Rn]` entry is a unit. An entry that names no archived source under
    # ../sources/ is not quoting a page this repo holds the bytes of - an
    # issue-tracker quote, a community post, a repository file - and its figures
    # are not checked here. Carrying the previous entry's page forward across
    # such an entry would check a GitHub quote against an unrelated vendor page
    # and produce a false positive on correct data.
    entry_re = re.compile(r"^\*\*\[R\d+\]")

    for path in sorted(references.glob("*.md")):
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        current_page: str | None = None
        corrected = False
        for offset, line in enumerate(lines, start=1):
            if entry_re.match(line):
                current_page = None
                corrected = False
            # An entry names its own archived page on a `sources/...` link.
            named = re.search(r"\(\.\./sources/([^)]+)\)", line)
            if named:
                current_page = named.group(1)
            # A dated CORRECTED marker means the figures quoted after it are the
            # superseded ones being recorded, and the check stops objecting.
            if re.search(r"\*\*CORRECTED\s+\d{4}-\d{2}-\d{2}", line):
                corrected = True
            if current_page is None or corrected:
                continue
            on_page = pages.get(current_page)
            if on_page is None:
                continue
            lowered = line.lower()
            if any(marker in lowered for marker in derived_markers):
                continue
            for token in re.findall(r"\$\s?(\d[\d,]*\.?\d*)", line):
                norm = _normalise_money(token)
                if norm in on_page:
                    continue
                failures.append(
                    f"[quoted-money-on-page] {rel(path)} line {offset} quotes "
                    f"${token}, which is not on sources/{current_page}, the page "
                    f"this entry cites. A quotation that is not in the source is "
                    f"not evidence; re-read the page, or mark the entry CORRECTED "
                    f"with a date if the figure is deliberately superseded."
                )

# CJK magnitude suffixes and the power of ten each stands for. A note carrying
# one of these has to be converted against the stored row, never copied: 亿 is
# 10^8, so 25.81亿 is 2,581,000,000 and not 25.81 billion.
CJK_SCALE = {"万": 1e4, "萬": 1e4, "亿": 1e8, "億": 1e8, "兆": 1e12}

# A token column's own unit, so a value can be checked against its header rather
# than against a guess. `tokens` with no suffix is taken as raw tokens, which is
# the one convention that makes the stored-row comparison meaningful.
TOKEN_COLUMN_UNITS = {
    "monthly_tokens": 1,
    "monthly_tokens_m": 1e6,
    "tokens_m_advertised": 1e6,
    "tokens_m_converted": 1e6,
    "tokens": 1,
    "tokens_m": 1e6,
    "tokens_m_at_ceiling": 1e6,
    "plan_monthly_tokens": 1,
    "monthly_yi": 1e8,
    "monthly_yi_value": 1e8,
}

# Any token-bearing column is matched against this list, and one that is not on
# it is refused rather than skipped. The first version compared only enumerated
# pairs, which meant (a) a file with a single token column could not be checked
# at all - the common case, and the shape the 亿 defect had - and (b) a column
# called `monthly_tokens_b` carrying an 11.029-vs-11029 error passed silently,
# because the check had never heard of it. An unknown unit column is a column
# whose header makes no promise about scale, and that is the ambiguity this
# check exists to resolve rather than pass over.
TOKEN_COLUMN_PATTERN = re.compile(r"^(monthly_|plan_monthly_)?tokens|token_|_(tokens|token)$|tokens_")

# Columns that state the SAME quantity under different units, compared by default.
# Only column pairs listed here are checked against each other, because "any two
# token columns must agree" is wrong in general: `tokens_m_advertised` and
# `tokens_m_measured` are two different quantities on purpose (a vendor ceiling
# and a user meter), and treating them as one produced a false positive on
# correct data when this check was first written. A check that is confidently
# wrong is worse than no check.
SAME_QUANTITY_GROUPS = (
    frozenset({"monthly_tokens", "monthly_tokens_m"}),
    frozenset({"monthly_tokens", "tokens_m"}),
    frozenset({"monthly_tokens_m", "tokens_m"}),
    frozenset({"monthly_tokens_m", "tokens_m_at_ceiling"}),
    frozenset({"tokens_m_advertised", "monthly_tokens"}),
    frozenset({"tokens_m_advertised", "monthly_tokens_m"}),
    frozenset({"tokens_m_advertised", "tokens_m"}),
    frozenset({"tokens_m_advertised", "monthly_yi"}),
    frozenset({"tokens_m_converted", "monthly_tokens_m"}),
    frozenset({"monthly_tokens_m", "monthly_yi"}),
    frozenset({"tokens_m", "monthly_yi"}),
    frozenset({"plan_monthly_tokens", "monthly_yi"}),
    frozenset({"monthly_yi", "monthly_yi_value"}),
)

# A column whose name carries this suffix is a deliberately different quantity
# and is excluded from the comparison above. `tokens_m_measured` is one: it is a
# user meter reading, not the vendor ceiling in the adjacent column, and the two
# are expected to disagree by a large factor.
DIFFERENT_QUANTITY_SUFFIX = "_measured"

# A token column carrying a magnitude letter in its own name states that letter's
# power of ten. `monthly_tokens_b` is billions, `monthly_tokens_m` millions,
# `monthly_tokens_k` thousands. This is what makes a single-column file
# checkable: the header itself carries the unit, so a value can be read against
# it without a second column to compare against.
NAME_SUFFIX_UNITS = {"k": 1e3, "m": 1e6, "b": 1e9, "bn": 1e9, "g": 1e9, "t": 1e12}

# Below this, a token count is not a token count. A monthly subscription plan in
# this market ranges from ~34M (Kimi K3 at a $15 cap) to ~22,059M (Muse Spark
# Contributor on Go Plus). A single-token reading is a magnitude error by
# construction, and a threshold this low cannot fire on a legitimate figure.
MIN_PLAUSIBLE_MONTHLY_TOKENS = 1e6


def _declared_unit_from_name(name: str) -> float | None:
    """The multiplier a column name's trailing unit letter declares, if any.

    A compound name like `monthly_tokens_m_converted` declares its unit in the
    middle rather than at the end, so the token stem is located first and the
    letter immediately after it is read.
    """
    tail = name.rsplit("_", 1)
    if len(tail) == 2 and tail[1].lower() in NAME_SUFFIX_UNITS:
        return NAME_SUFFIX_UNITS[tail[1].lower()]
    stem = re.search(r"tokens?_([a-z]+)", name)
    if stem:
        return NAME_SUFFIX_UNITS.get(stem.group(1))
    return None


def _parse_token_value(raw: str):
    """A token count as a float, or None. Accepts CJK magnitude suffixes."""
    text = raw.strip().replace(",", "")
    if not text or text.upper() == "UNKNOWN":
        return None
    scale = 1.0
    for suffix, factor in CJK_SCALE.items():
        if text.endswith(suffix):
            scale = factor
            text = text[: -len(suffix)].strip()
            break
    try:
        return float(text) * scale
    except ValueError:
        return None


def _check_single_token_column(path: Path, offset: int, name: str, raw: str,
                               unit: float | None) -> None:
    """A lone token column is checked against the unit its own header declares.

    The pair comparison below needs two columns to exist, so a file with one
    token column was unchecked - and one token column is the common case, and
    the shape the 亿 defect actually had. The column's own unit is applied
    first, so `tokens_m_at_ceiling=1697` is 1.697 billion tokens and is not an
    error, while a `monthly_tokens_m_converted` cell reading 0.453 is 453,000
    tokens and is.

    A value whose magnitude cannot be a monthly allowance is a count that
    arrived divided or multiplied by a power of ten. In this market a monthly
    allowance runs from ~34M (Kimi K3 at a $15 cap) to ~22,059M, so a million
    is a threshold nothing legitimate sits near.
    """
    value = _parse_token_value(raw)
    if value is None:
        return
    if unit is None:
        failures.append(
            f"[unit-scale] {rel(path)} data row {offset}: column {name!r} holds a "
            f"token count but its header declares no unit, so {raw.strip()} cannot "
            f"be read against anything. Name the unit in the column "
            f"(tokens_m, monthly_tokens, monthly_tokens_b) or give it a companion "
            f"column in a stated unit."
        )
        return
    tokens = value * unit
    if 0 < tokens < MIN_PLAUSIBLE_MONTHLY_TOKENS:
        failures.append(
            f"[unit-scale] {rel(path)} data row {offset}: {name}={raw.strip()} is "
            f"{tokens:,.0f} tokens in that column's unit. No monthly token "
            f"allowance in this market is below "
            f"{MIN_PLAUSIBLE_MONTHLY_TOKENS:,.0f}, so this is a magnitude error "
            f"rather than a small figure. A count that arrived divided or "
            f"multiplied by a power of ten on the way in produces exactly this."
        )


def check_unit_scale(pass_dir: Path) -> None:
    """Two columns stating one quantity must agree once each is read in its unit.

    A source row stored `monthly_tokens: 2581000000` and, alongside it, a
    human-readable `25.81` under a `monthly_yi` header. yi is 10^8, so those two
    cells agree and describe 2.58 billion. Reading the second cell as 25.81
    billion is a 10x error; it survived a reconciler and flipped a HIT only when
    a second reconciler re-checked the arithmetic against the stored row. This
    check is that re-check made structural.

    Only column pairs listed in SAME_QUANTITY_GROUPS are compared. The first
    version compared every token column against every other and reported the
    correct `tokens_m_advertised=6211` / `tokens_m_measured=2900` row as a 2.1x
    magnitude error, because those two columns are deliberately different
    quantities: one is a vendor ceiling and the other is a user meter. A check
    that is confidently wrong is worse than no check.

    That restraint then over-corrected: pair comparison alone cannot fire on a
    file with a single token column, which is the common case and the shape the
    亿 defect actually had, and it silently passed a `monthly_tokens_b` column
    carrying an 11.029-vs-11029 error because the column was not on the list. So
    every token-bearing column is now also checked on its own against the unit
    its header declares and against what a monthly allowance can physically be.
    """
    data = pass_dir / "data"
    if not data.is_dir():
        return
    for path in sorted(data.glob("*.csv")):
        header, rows = read_rows(path)
        if not header:
            continue
        index = {name.strip().lower(): i for i, name in enumerate(header)}
        present_names = {
            name for name in index
            if name in TOKEN_COLUMN_UNITS and not name.endswith(DIFFERENT_QUANTITY_SUFFIX)
        }
        # Every column that looks like a token count, whether or not the check
        # has seen it before. An unrecognised unit column is the case the old
        # enumerated-pairs version could not reach, so a column whose name
        # declares a magnitude letter gets that letter as its unit.
        token_like = {}
        for name in index:
            if name in present_names or name.endswith(DIFFERENT_QUANTITY_SUFFIX):
                continue
            if not TOKEN_COLUMN_PATTERN.match(name):
                continue
            token_like[name] = _declared_unit_from_name(name)
        pairs = [
            (a, b) for group in SAME_QUANTITY_GROUPS
            for a, b in [sorted(group)]
            if a in present_names and b in present_names
        ]
        for offset, row in enumerate(rows, start=1):
            if len(row) != len(header):
                continue
            for name in sorted(present_names):
                if len(row) <= index[name]:
                    continue
                _check_single_token_column(
                    path, offset, name, row[index[name]], TOKEN_COLUMN_UNITS[name]
                )
            for name, unit in sorted(token_like.items()):
                if len(row) <= index[name]:
                    continue
                _check_single_token_column(path, offset, name, row[index[name]], unit)
            for a_name, b_name in pairs:
                a_raw = _parse_token_value(row[index[a_name]])
                b_raw = _parse_token_value(row[index[b_name]])
                if a_raw is None or b_raw is None:
                    continue
                # Each cell as written, then as tokens under its own column unit.
                a_tok = a_raw * TOKEN_COLUMN_UNITS[a_name]
                b_tok = b_raw * TOKEN_COLUMN_UNITS[b_name]
                if not a_tok or not b_tok:
                    continue
                ratio = max(a_tok, b_tok) / min(a_tok, b_tok)
                # One quantity in two units, so anything past 2x is a unit or
                # magnitude disagreement rather than rounding.
                if ratio > 2.0:
                    failures.append(
                        f"[unit-scale] {rel(path)} data row {offset}: {a_name}='{row[index[a_name]].strip()}' "
                        f"is {a_tok:,.0f} tokens and {b_name}='{row[index[b_name]].strip()}' is "
                        f"{b_tok:,.0f} tokens. Both columns state the same quantity and they "
                        f"differ by {ratio:.1f}x. A CJK magnitude suffix (wan/yi/zhao, "
                        f"10^4/10^8/10^12) copied instead of converted produces exactly this."
                    )


def _normalise_identity(text: str) -> str:
    """Fold a display name or slug to comparable form.

    "Muse Spark 1.3 Contributor" and "muse-spark-1-3" are the same underlying
    model; "Muse Spark 1.3 Contributor" and "muse-spark-1-3-contributor" are
    different SKUs of it. That difference is the whole defect, so tier words are
    kept as separate tokens rather than normalised away.
    """
    text = text.lower().replace("-", " ").replace("_", " ")
    text = re.sub(r"\(.*?\)", " ", text)
    text = re.sub(r"[^a-z0-9 ]+", " ", text)
    return " ".join(text.split())


# Words that qualify a model into a different SKU rather than naming it. A plan
# row selling one of these is not selling the row it joined to.
SKU_TIER_WORDS = ("contributor", "pro", "max", "lite", "mini", "flash", "preview")


def check_unscored_model(pass_dir: Path) -> None:
    """A capability score must come from a leaderboard row or be marked absent.

    `model-slug-joins` only asks whether a slug is in the landscape. It cannot
    see a row that joined cleanly to a *different* SKU: the plan sells
    "Muse Spark 1.3 Contributor", the landscape carries "Muse Spark 1.3", and
    the base model's 48.09 was carried across to the Contributor SKU. That
    Contributor tier has no Intelligence Index at all, and it is the lane that
    reaches 11,029M tokens, so the inherited score is what made an unverified
    SKU look like the pass's answer.

    The first version of this check tested slug *presence*, which is why it
    passed on that defect: `muse-spark-1-3` is in the landscape, so the check
    returned clean. It now compares **identity**, not presence:

    * the plan row's displayed model name against the landscape row's name, and
    * the SKU tier words on each side.

    A plan row selling a tiered SKU whose slug resolves to an untilereded
    landscape row is the inheritance defect, whether or not the slug is present.
    The escape hatch is unchanged and still the only way through: `unscored:`
    in `aa_score_provenance`.
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
    name_i = mheader.index("name") if "name" in mheader else None
    pi = pheader.index("model_slug")
    model_i = pheader.index("model") if "model" in pheader else None
    prov_i = pheader.index("aa_score_provenance") if "aa_score_provenance" in pheader else None
    score_cols = [
        i for i, name in enumerate(pheader)
        if name.strip().lower() in ("intelligence_index", "aa_intelligence_index",
                                    "aa_score", "quality_index")
    ]
    if prov_i is None and not score_cols:
        return

    # slug -> the identity tokens of the landscape row it names.
    landscape: dict[str, tuple[str, ...]] = {}
    for r in mrows:
        if len(r) <= mi:
            continue
        slug = r[mi].strip()
        if not slug:
            continue
        display = r[name_i] if name_i is not None and len(r) > name_i else slug
        landscape[slug] = tuple(_normalise_identity(display).split())

    for offset, row in enumerate(prows, start=1):
        if len(row) <= pi or len(row) != len(pheader):
            continue
        slug = row[pi].strip()
        if not slug or slug == "UNKNOWN":
            continue
        prov = row[prov_i].strip().lower() if prov_i is not None and len(row) > prov_i else ""
        if prov.startswith("unscored:"):
            continue
        published = [
            row[c].strip() for c in score_cols
            if row[c].strip() and row[c].strip().upper() != "UNKNOWN"
        ]
        asserts_score = published or prov.startswith("leaderboard:")

        if slug not in landscape:
            # Not on the board at all: only an unscored marker saves it.
            if published:
                failures.append(
                    f"[unscored-model] {rel(plans)} data row {offset} publishes "
                    f"{published[0]} for model_slug {slug!r}, which has no row in "
                    f"data/models-database.csv. Either the score belongs to a "
                    f"different SKU, or aa_score_provenance must read "
                    f"'unscored:<reason>'."
                )
            elif prov.startswith("leaderboard:"):
                claimed = prov.split(":", 1)[1].strip()
                failures.append(
                    f"[unscored-model] {rel(plans)} data row {offset} asserts "
                    f"aa_score_provenance {prov!r} for model_slug {slug!r}, which is not in "
                    f"data/models-database.csv. If {claimed!r} is a different SKU then this row "
                    f"is borrowing its score; write 'unscored:<reason>' instead."
                )
            continue

        # The slug IS on the board, which is exactly where the 2026-10-02 defect
        # slipped through. The question is whether the row sells the same SKU the
        # landscape row describes.
        if model_i is None or not asserts_score:
            continue
        sold = _normalise_identity(row[model_i] if len(row) > model_i else slug)
        sold_tokens = set(sold.split())
        board_tokens = set(landscape[slug])

        sold_tier = {w for w in SKU_TIER_WORDS if w in sold_tokens}
        board_tier = {w for w in SKU_TIER_WORDS if w in board_tokens}

        # A row selling a tiered SKU that joins to an untilereded landscape row
        # is borrowing the base model's score. This is the inheritance defect.
        if sold_tier and not board_tier and sold_tokens - board_tier - {"<=", "and", "or"}:
            tier = ", ".join(sorted(sold_tier))
            failures.append(
                f"[unscored-model] {rel(plans)} data row {offset} sells "
                f"{row[model_i].strip()!r} - a {tier} tier - but model_slug "
                f"{slug!r} names the untilereded base model, and this row asserts a "
                f"score for it. A tiered SKU is a different product from its base "
                f"model and does not inherit its Intelligence Index; look the tier "
                f"itself up, or write 'unscored:<reason>'."
            )


def check_shared_cap(pass_dir: Path) -> None:
    """A per-model dollar ceiling must say whether it is independent or pooled.

    OpenCode Go publishes a $60 monthly limit per model and says "Each model's
    monthly limit below determines how its usage counts toward those
    allowances", which reads as independent budgets. Several open issues report
    the opposite: models blocked at $0 recorded spend, one at $4.38 total
    account spend against a $60 pool. An independent-per-model table and a
    shared-pool table produce the same headline number for a single model and
    differ by the number of models a buyer uses, so a row publishing the
    ceiling without recording which it is cannot be planned against.

    The pool model may be declared in either `cap_model` (the 2026-10-06 column)
    or `meter_basis` (the 2026-10-02 column), and a ceiling may be published in
    `monthly_ceiling_usd`, `per_model_cap_usd` or `monthly_pool_usd`. A file
    that carries none of them has nothing to check and is skipped rather than
    guessed at.

    `cap_model` / `meter_basis` is **authoritative**. The first version also
    accepted the bare token "pool" appearing anywhere in the free-text notes,
    which lets a row whose `cap_model` literally reads `PER-MODEL` pass as long
    as some sentence in its notes happens to mention a pool. The notes are
    where the reading is argued; the column is where it is declared, and a
    check that reads the argument instead of the declaration is checking prose.
    """
    plans = pass_dir / "data" / "plan-economics.csv"
    if not plans.is_file():
        return
    header, rows = read_rows(plans)
    if not header:
        return
    cap_cols = [c for c in ("monthly_ceiling_usd", "per_model_cap_usd", "monthly_pool_usd")
                if c in header]
    model_cols = [c for c in ("cap_model", "meter_basis") if c in header]
    if not cap_cols or not model_cols:
        return
    cap_idx = [header.index(c) for c in cap_cols]
    model_idx = [header.index(c) for c in model_cols]
    for offset, row in enumerate(rows, start=1):
        if len(row) != len(header):
            continue
        ceilings = [(row[i] or "").strip() for i in cap_idx]
        if not any(c and _num(c) is not None for c in ceilings):
            continue
        declared = " ".join((row[i] or "") for i in model_idx).lower()
        if not declared.strip():
            failures.append(
                f"[shared-cap] {rel(plans)} data row {offset} publishes a dollar "
                f"ceiling but its {'/'.join(model_cols)} cell is empty. A per-model "
                f"ceiling means nothing without saying whether it is independent or "
                f"drawn against a shared monthly pool, because the two differ by the "
                f"number of models a buyer uses in the month."
            )
            continue
        if any(token in declared for token in ("pool", "shared", "additive")):
            continue
        shown = next(c for c in ceilings if c and _num(c) is not None)
        failures.append(
            f"[shared-cap] {rel(plans)} data row {offset}: ceiling ${shown} is "
            f"published with {'/'.join(model_cols)}={row[model_idx[0]].strip()!r} and "
            f"nothing recording whether it is independent or drawn against a shared "
            f"monthly pool. State it in the cap_model column, not in the notes: a "
            f"pooled cap changes the plan's yield by the number of models a buyer "
            f"uses in the month, and that column is what a reader reads."
        )


def check_mix_declared(pass_dir: Path) -> None:
    """A derived $/M or tokens/month row must state the traffic mix behind it.

    A $/M figure is a division and its divisor is a traffic mix. The same plan on
    the same page yields figures 5.3x to 29.0x apart depending on the mix, and
    the 2026-10-02 pass exists because a $/M was published without one and a
    second was published to contradict it. A row carrying a derived price or a
    derived monthly token count without recording the mix it was computed under
    has published an assumption as a result.

    The mix must be in a **column**, and that column must be non-empty. The first
    version also accepted the substring "cache", "mix" or "%" anywhere in the
    notes, which satisfies a row whose notes read "Vendor caches nothing beyond
    the discounted tier" - a sentence that says nothing about the mix the row's
    $/M was computed under. Prose is where the assumption hides, so prose no
    longer counts.
    """
    data = pass_dir / "data"
    if not data.is_dir():
        return
    for path in sorted(data.glob("*.csv")):
        header, rows = read_rows(path)
        if not header:
            continue
        index = {name.strip().lower(): i for i, name in enumerate(header)}
        derived = [c for c in ("usd_per_mtok", "monthly_tokens_m", "tokens_m",
                               "tokens_m_at_ceiling", "blended_usd_per_mtok")
                   if c in index]
        if not derived:
            continue
        # A dedicated mix column, if the file has one. `cache` alone is not a
        # mix column: `cached_read_per_m` is a price, and a file whose only
        # "cache"-ish column is a price has declared no mix.
        mix_cols = [
            c for c in index
            if c in ("traffic_mix", "mix", "traffic_mix_used", "mix_used",
                     "assumed_mix")
        ]
        has_mix_column = bool(mix_cols)
        for offset, row in enumerate(rows, start=1):
            if len(row) != len(header):
                continue
            values = [row[index[c]] for c in derived
                      if _num(row[index[c]]) is not None and _num(row[index[c]]) > 0]
            if not values:
                continue
            if has_mix_column:
                if any(row[index[c]].strip() for c in mix_cols):
                    continue
                failures.append(
                    f"[mix-declared] {rel(path)} data row {offset} carries a "
                    f"derived $/M or tokens/month figure but its "
                    f"{'/'.join(sorted(mix_cols))} cell is empty. The mix is the "
                    f"divisor of every figure in this row; state it there."
                )
                continue
            # No mix column exists in this file at all. Then the check cannot
            # demand one on a file that was never built with the idea, so it is
            # skipped rather than guessed at - the same restraint
            # `cost-arithmetic` applies when its three columns are absent.
            continue


def validate(pass_dir: Path) -> None:
    check_layout(pass_dir)
    check_dates(pass_dir)
    check_field_counts(pass_dir)
    check_column_values(pass_dir)
    check_cost_arithmetic(pass_dir)
    check_evidence_labels(pass_dir)
    check_report_matches_data(pass_dir)
    check_model_slug_joins(pass_dir)
    check_ladder_prices_on_page(pass_dir)
    check_quoted_money_on_page(pass_dir)
    check_unit_scale(pass_dir)
    check_unscored_model(pass_dir)
    check_shared_cap(pass_dir)
    check_mix_declared(pass_dir)


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
