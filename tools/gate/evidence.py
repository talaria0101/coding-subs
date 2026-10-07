"""Evidence checks: every figure carries a reachable source and a declared class."""
from __future__ import annotations

import re
from pathlib import Path

from .common import (
    CARRY_MARKER,
    EVIDENCE_CLASSES,
    _row_contract,
    data_rows,
    failures,
    read_rows,
    rel,
)


def check_evidence_labels(pass_dir: Path) -> None:
    """A figure must be attributable, and the attribution must be reachable.

    `evidence-label` covers three cases, in the order they matter. A row with no
    evidence cell at all is unsourced. An `evidence_class` outside the declared
    vocabulary is a class no reader of the evidence table can interpret. A figure
    citing no URL is not verifiable by anyone, which is the defect this check was
    originally written for and the one it silently tolerated: a non-empty string
    of any content passed as evidence.

    A `source` column that holds a bare slug (`modelsdev-api.json`,
    `peter123023/awesome-free-llm-api`) is a repository reference rather than a
    URL. Such rows are still reported, against the file's own declared
    provenance rather than as arithmetic failures.
    """
    data = pass_dir / "data"
    if not data.is_dir():
        return
    # Which columns may satisfy a row's evidence requirement. `evidence` is
    # deliberately absent: 2026-09-20's providers-database.csv and
    # agents-universe.csv use it as free text, so a pattern on it rejects correct
    # rows, and those rows carry their reference in `source` instead.
    label_cols = ("source_url", "source", "source_quality", "confidence")
    # The evidence-label check's own history is recorded in the code beside
    # COLUMN_VALUE_PATTERNS in structure.py; what is recorded here is the shape.
    # `vendor_source` is a page file, not a URL, and the check below says so
    # rather than treating every non-URL as absent.
    page_reference_columns = {"vendor_source"}
    for path in sorted(data.glob("*.csv")):
        header, rows = read_rows(path)
        if not header:
            continue
        index = {name.strip().lower(): i for i, name in enumerate(header)}
        page_cols = [index[n] for n in page_reference_columns if n in index]
        has_labels = any(c in name for name in index for c in label_cols)
        if not has_labels and "evidence_class" not in index:
            continue
        contract = _row_contract(path)
        present = [c for c in label_cols if any(c in name for name in index)]
        class_i = index.get("evidence_class")
        url_cols = [index[n] for n in index
                    if n in ("source_url", "source", "url") or n.endswith("_url")]
        date_cols = [index[n] for n in index
                     if n in ("read_date", "access_date", "fetched_date", "date")]
        siblings = {q.name for q in data.glob("*")}
        if pass_dir.joinpath("sources").is_dir():
            siblings |= {q.name for q in pass_dir.joinpath("sources").glob("*")}
        for offset, row in enumerate(data_rows(rows), start=1):
            if len(row) != len(header):
                continue
            if not any(c.strip() for c in row):
                continue
            urls = [row[i].strip() for i in url_cols if row[i].strip()]
            openable = [u for u in urls if re.match(r"^https?://\S+$", u)]
            derived = bool(contract) and bool(urls)
            values = [
                row[index[name]].strip() for name in index
                if any(c in name for c in present)
            ]
            # The two passes before 2026-10-02 name no URL anywhere, so this
            # check has nothing to compare a reference against. That is a finding
            # about those passes, recorded once in the review file rather than as
            # 118 rows on every run; `evidence-vocabulary` and
            # `fetch-log-corroborates` still cover them.
            if not openable and pass_dir.name < "2026-10-02":
                continue
            pages = [row[i].strip() for i in page_cols if row[i].strip()]
            if pages and not urls and pass_dir.joinpath("sources").is_dir():
                if all((pass_dir / "sources" / pg).is_file() for pg in pages):
                    # The row cites the archived page by file name, and the page
                    # is here. `fetch-log-corroborates` checks the bytes.
                    if class_i is not None:
                        declared = row[class_i].strip()
                        if (declared and declared != CARRY_MARKER
                                and declared not in EVIDENCE_CLASSES):
                            failures.append(
                                f"[evidence-label] {rel(path)} data row {offset}: "
                                f"evidence_class={declared!r} is outside the vocabulary "
                                f"the root README declares "
                                f"({' | '.join(sorted(EVIDENCE_CLASSES))}). A class no "
                                f"reader of that table can interpret is not an evidence "
                                f"class; pick one of the declared six, or record the row "
                                f"as {CARRY_MARKER} to say the figure was not re-verified."
                            )
                    continue
            if not any(values) and not urls:
                failures.append(
                    f"[evidence-label] {rel(path)} data row {offset} has "
                    f"no source URL and no source/quality/confidence value"
                )
                continue
            # A derived artefact names its own sources in its preamble, so a row
            # that cites another file in this repository by name is following that
            # declaration rather than failing it.
            if derived and any(u in siblings for u in urls):
                continue
            if derived and not openable:
                # A derived artefact with a stated per-row source column, and
                # some of its rows have not been filled in.
                failures.append(
                    f"[evidence-label] {rel(path)} data row {offset} carries figures "
                    f"and a label, and this file declares itself derived - "
                    f"{contract[0].lstrip('# ').strip()} - but this row's source cell "
                    f"holds {urls[0]!r} rather than a URL, and the column exists for "
                    f"exactly this."
                )
                continue
            if class_i is not None:
                declared = row[class_i].strip()
                if declared and declared != CARRY_MARKER and declared not in EVIDENCE_CLASSES:
                    failures.append(
                        f"[evidence-label] {rel(path)} data row {offset}: "
                        f"evidence_class={declared!r} is outside the vocabulary the root "
                        f"README declares ({' | '.join(sorted(EVIDENCE_CLASSES))}). A "
                        f"class no reader of that table can interpret is not an evidence "
                        f"class; pick one of the declared six, or record the row as "
                        f"{CARRY_MARKER} to say the figure was not re-verified."
                    )
            if derived or openable:
                continue
            if not urls:
                failures.append(
                    f"[evidence-label] {rel(path)} data row {offset} carries figures "
                    f"and a label, but no source. A label is not a source: nobody can "
                    f"re-derive the figure from 'VERIFIED official docs'."
                )
                continue
            failure = (
                f"[evidence-label] {rel(path)} data row {offset} cites {urls[0]!r}, "
                f"which is not a URL a reader can open."
            )
            if contract:
                failures.append(
                    failure.replace(
                        "which is not a URL a reader can open.",
                        "which is not a URL a reader can open. This file's preamble "
                        "declares it a derived artefact whose provenance is the page it "
                        f"regenerates from - {contract[0].lstrip('# ').strip()}",
                    )
                )
            else:
                failures.append(failure)
            if date_cols and not any(row[i].strip() for i in date_cols):
                failures.append(
                    f"[evidence-label] {rel(path)} data row {offset} cites a source "
                    f"but records no access date."
                )


def check_evidence_vocabulary(pass_dir: Path) -> None:
    """Every `evidence_class` cell is a member of the declared set.

    Separate from `evidence-label` because it is a different kind of claim: the
    label check asks whether a row says where its numbers came from, and this one
    asks whether the word it uses for that is one the repository defines. A
    `FIRST-PARTY` cell is not a typo to be tidied; it reads as the strongest class
    in the table while naming a different thing, and that is a stronger claim
    than the data supports.
    """
    data = pass_dir / "data"
    if not data.is_dir():
        return
    for path in sorted(data.glob("*.csv")):
        header, rows = read_rows(path)
        if not header or "evidence_class" not in header:
            continue
        i = header.index("evidence_class")
        for offset, row in enumerate(data_rows(rows), start=1):
            if len(row) <= i:
                continue
            value = row[i].strip()
            if not value or value in EVIDENCE_CLASSES:
                continue
            declared = " | ".join(sorted(EVIDENCE_CLASSES))
            if value == CARRY_MARKER:
                failures.append(
                    f"[evidence-vocabulary] {rel(path)} data row {offset}: "
                    f"evidence_class={CARRY_MARKER!r} is not one of the declared classes "
                    f"({declared}). It records that the figure was carried forward rather "
                    f"than re-verified, which is a provenance note, not an evidence class."
                )
            elif "," in value or " " in value or "://" in value or "/" in value:
                failures.append(
                    f"[evidence-vocabulary] {rel(path)} data row {offset}: "
                    f"evidence_class={value!r} holds what looks like two values - a URL, "
                    f"a date, or a URL plus a date in the evidence-class column. An "
                    f"arity-preserving column shift puts exactly that there. Reclassify "
                    f"the row into one of the declared classes."
                )
            else:
                failures.append(
                    f"[evidence-vocabulary] {rel(path)} data row {offset}: "
                    f"evidence_class={value!r} is outside the declared set ({declared}). "
                    f"Use one of the declared six, or UNKNOWN when the figure is not "
                    f"published."
                )
