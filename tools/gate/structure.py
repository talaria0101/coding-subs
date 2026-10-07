"""Shape checks on a pass directory and its CSVs: layout, arity and column kinds."""
from __future__ import annotations

import re
from pathlib import Path

from .common import CARRY_MARKER, EVIDENCE_CLASSES, ROOT, check, failures, read_rows, rel


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


# What kind of value each column name promises. A column name is a type
# declaration, and a cell that cannot be that type is either in the wrong column
# or the row has slid sideways.
#
# Each entry is deliberately narrow. A pattern wide enough to catch every shift
# is also wide enough to reject correct data, and a check that rejects correct
# data is worse than one that passes a defect. Three wider attempts failed on
# this repo's own history and are recorded in docs/reviews-2026-10-06.md: a
# pattern on `evidence` rejected 37 rows of 2026-09-20's agents-universe.csv that
# legitimately hold a URL or a file path, a pattern on `source_quality` rejected
# 43 rows of 2026-09-13's providers-database.csv whose values are free text by
# design, and a pattern on `model_slug` rejected 100+ rows of 2026-10-02's
# mix-sensitivity-all.csv, where the column holds display names rather than slugs.
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
            # An evidence class is a class drawn from the declared vocabulary,
            # plus the one carry marker. Those are the only values a reader of
            # that column can interpret, so they are the values it may hold.
            # Membership is also checked by `evidence-vocabulary`; listing them
            # here as well means a shift that lands a URL or a date in this column
            # is caught by shape first, with the membership message available
            # when nothing has been shifted.
            #
            # The check is gated on the column being present, because a vocabulary
            # is a property of a repository and cannot be retrofitted onto a pass
            # that predates the table. 2026-10-02 is the first pass carrying
            # `evidence_class`.
            if lowered == "evidence_class":
                expectations.append(
                    (i, lowered, tuple(sorted(EVIDENCE_CLASSES)) + (CARRY_MARKER,))
                )
        if not expectations:
            continue
        for offset, row in enumerate(rows, start=1):
            if not row or len(row) != len(header):
                continue
            for i, name, pattern in expectations:
                value = row[i].strip()
                if not value:
                    continue
                if isinstance(pattern, tuple):
                    if value in pattern:
                        continue
                elif pattern.match(value):
                    continue
                failures.append(
                    f"[field-columns] {rel(path)} data row {offset}: column "
                    f"{name!r} holds {value!r}, which is not a value of the kind "
                    f"that column is for. Either this value belongs in another "
                    f"column or the row has slid sideways: a surplus unquoted "
                    f"comma paired with a missing empty cell keeps the field "
                    f"count correct while shifting every value after it."
                )
