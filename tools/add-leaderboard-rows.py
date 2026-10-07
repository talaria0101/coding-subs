#!/usr/bin/env python3
"""Append the leaderboard-sourced rows that the archived /models page does not carry.

    python3 tools/add-leaderboard-rows.py

The 24 rows in 2026-10-06/data/models-database.csv come out of the archived
`/models` snapshot via parse-aa-models.py, and that page does not list every
model the plans sell. On 2026-10-07 the `/leaderboards/models` payload was
fetched and archived, and it does list `mimo-v2-6-flash` at II 37.8844. A plan
row that publishes a score must be able to join to a landscape row carrying that
score, so the row is appended here rather than hand-written into the CSV.

Columns the leaderboard payload does not publish are left empty rather than
filled from another source. `UNKNOWN` is the honest value and `validate.py`'s
evidence-label check requires the row to carry a class either way.
"""
import csv
import io
import sys
from pathlib import Path

PATH = (Path(__file__).resolve().parent.parent / "2026-10-06" / "data"
        / "models-database.csv")

HEADER = [
    "slug", "name", "creator", "releaseDate", "intelligenceIndex",
    "terminalbenchV40", "terminalbenchV21", "terminalbenchHard",
    "contextWindowTokens", "isOpenWeights", "inputModalityImage",
    "price1mInputTokens", "price1mOutputTokens", "cacheHitPrice",
    "price1mBlended0To3To1", "medianOutputSpeed", "deprecated",
]

# slug -> row. `creator` comes from the payload's `modelCreatorName`.
# The API list-price columns are empty: the leaderboard payload does not publish
# them, and a price read from a different source would be a second source's
# figure in a file that is otherwise one page's bytes.
ROWS = [
    ["mimo-v2-6-flash", "MiMo-V2.6-Flash", "Xiaomi", "", "37.8844",
     "", "", "", "1000000", "yes", "", "", "", "", "", "", "no"],
]


def main() -> int:
    existing = list(csv.reader(PATH.read_text(encoding="utf-8").splitlines()))
    header, rows = existing[0], existing[1:]
    if header != HEADER:
        print(f"header is {len(header)} columns, expected {len(HEADER)}", file=sys.stderr)
        return 1

    known = {r[0] for r in rows}
    added = []
    for row in ROWS:
        if len(row) != len(HEADER):
            print(f"row {row[0]!r} has {len(row)} fields", file=sys.stderr)
            return 1
        if row[0] in known:
            continue
        rows.append(row)
        added.append(row[0])

    buf = io.StringIO()
    writer = csv.writer(buf, lineterminator="\n")
    writer.writerow(header)
    for r in rows:
        writer.writerow(r)
    PATH.write_text(buf.getvalue(), encoding="utf-8")
    print(f"{len(rows)} rows -> {PATH}")
    print(f"  added from sources/aa-leaderboard-models.html: "
          + (", ".join(added) if added else "none"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())