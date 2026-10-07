#!/usr/bin/env python3
"""Parse the OpenCode Go / Go Plus tables structurally from the fetched HTML.

    python3 tools/parse-opencode-go.py PAGE.html > grid.csv

The earlier tag-splitting approach lost rows and shifted columns, because a row
whose "Cached Write" cell is "-" or absent does not occupy the same number of
cells as one that has a price. This reads <table>/<tr>/<th>/<td> instead, so
column identity comes from the header, not from position.

The page argument is **required**. It used to default to `raw/opencode-go.html`, a
path that does not exist in this repository - `.gitignore` excludes `research-raw/`
and the archived pages live under `<pass>/sources/` - so the default could only
ever have produced a traceback. A tool that fails with a file-not-found at the
end of a pipeline is worse than one that refuses before reading anything.

Emits CSV to stdout and a short consistency report to stderr. The MIX below is
the one standard traffic mix this repository uses (97% cache read / 2.5% input /
0.5% output); every blended figure the parser prints is a function of it.
"""

# The three comment lines the parser writes ahead of the header. They are here
# rather than in the committed file alone so that this tool regenerates the
# committed file byte for byte, which is what the CI step diffs.
PREAMBLE = [
    "# Derived by tools/parse-opencode-go.py from sources/opencode-go.html, read "
    "2026-10-02,",
    "# and regenerable from it byte for byte. Every blended and derived column "
    "is a",
    "# function of the traffic_mix column, which is why the grid carries it per "
    "row.",
]
import csv
import html
import io
import re
import sys
from pathlib import Path

# The standard traffic mix this repository computes every blended rate under:
# 97% cache read / 2.5% fresh input / 0.5% output. It is a quoted convention
# (references R20), not a measurement, and it is the only free parameter in every
# `blended_per_m` and `tokens_m_at_ceiling` cell this parser emits.
MIX = {"cached_read": 0.97, "input": 0.025, "output": 0.005}

# The access date of the archived page, carried into the grid so every row's
# provenance is in the row. Taken from the fetch log rather than from the clock.
READ_DATE = "2026-10-02"


def strip_tags(fragment: str) -> str:
    text = re.sub(r"(?s)<[^>]+>", " ", fragment)
    return re.sub(r"\s+", " ", html.unescape(text)).strip()


def tables(raw: str):
    for match in re.finditer(r"(?is)<table\b[^>]*>(.*?)</table>", raw):
        block = match.group(1)
        header, body = None, []
        for row in re.finditer(r"(?is)<tr\b[^>]*>(.*?)</tr>", block):
            cells = [
                strip_tags(c.group(1))
                for c in re.finditer(r"(?is)<t[hd]\b[^>]*>(.*?)</t[hd]>", row.group(1))
            ]
            if not cells:
                continue
            if header is None and any(c.strip() == "Model" for c in cells):
                header = cells
            elif header is not None:
                body.append(cells)
        if header:
            yield header, body


def money(cell: str):
    if re.match(r"(?i)free", cell or ""):
        return 0.0
    m = re.fullmatch(r"\$([\d,]+(?:\.\d+)?)", (cell or "").strip())
    return float(m.group(1).replace(",", "")) if m else None


def pick(header: list[str], row: list[str], name: str):
    """Look a column up by header name; short rows simply yield None."""
    for index, column in enumerate(header):
        if column.strip().lower().startswith(name.lower()):
            return row[index] if index < len(row) else None
    return None


def main() -> int:
    if len(sys.argv) < 2 or sys.argv[1].startswith("-"):
        print("usage: parse-opencode-go.py PAGE.html > grid.csv\n"
              "  PAGE.html is an archived OpenCode Go page, e.g.\n"
              "  2026-10-02/sources/opencode-go.html", file=sys.stderr)
        return 2
    path = Path(sys.argv[1])
    if not path.is_file():
        print(f"{path} is not a file. Pass the archived page this grid is parsed "
              f"from; the archived pages live under <pass>/sources/.", file=sys.stderr)
        return 2
    raw = path.read_text(encoding="utf-8", errors="replace")

    price_tables, request_tables = [], []
    for header, body in tables(raw):
        columns = [c.strip().lower() for c in header]
        if columns[:1] == ["model"] and any("monthly limit" in c for c in columns):
            price_tables.append((header, body))
        elif columns[:1] == ["model"] and any("5 hours" in c for c in columns):
            request_tables.append((header, body))

    if not price_tables:
        print("no price table found", file=sys.stderr)
        return 1

    # Line terminator is pinned and the stream is reconfigured so that no platform
# translates it again. `csv.writer` defaults to "\r\n"; on Linux stdout is
# already binary as far as newlines go and emits "\r\n" unchanged, which is what
# the committed CSV contains. On Windows, text-mode stdout translates each "\n"
# into a second "\r", so the same command emits "\r\r\n" and `diff -u` against
# the committed file fails there. Reconfiguring stdout to newline="" removes the
# translation, and pinning lineterminator to "\r\n" matches the committed bytes.
#
# The encoding is pinned too, and the newline fix above did not cover it.
# Reconfiguring for newlines made the *line terminator* platform-independent but
# left stdout's *encoding* as whatever the console defaults to, which on a stock
# Windows host is cp1252. The preamble carries a character cp1252 cannot encode,
# so the bare CI step still died on Windows with `UnicodeEncodeError: 'charmap'
# codec can't encode character ...` while passing on Linux. The committed bytes
# are UTF-8, so the output encoding is pinned to UTF-8 rather than inherited from
# the environment.
    sys.stdout.reconfigure(encoding="utf-8", newline="")
    writer = csv.writer(sys.stdout, lineterminator="\r\n")
    # The preamble is written straight to the stream rather than through
    # `csv.writer`, which quotes any field containing the delimiter. The
    # committed lines carry no quoting, so a writer would not reproduce them.
    # It is emitted here rather than added to the file by hand, because the CI
    # step that proves this file is reproducible diffs this output against the
    # committed bytes: a preamble that exists only in the committed file is a
    # preamble CI cannot reproduce.
    for line in PREAMBLE:
        sys.stdout.write(line + "\r\n")
    writer.writerow(
        ["plan", "plan_price_usd_month", "model", "input_per_m", "output_per_m",
         "cached_read_per_m", "cached_write_per_m", "monthly_limit_usd",
         "blended_per_m", "tokens_m_at_ceiling", "usd_per_m_tokens",
         "requests_per_5h", "requests_per_week", "requests_per_month",
         "monthly_over_weekly", "traffic_mix", "source", "read_date"]
    )
    problems = []
    for index, (header, body) in enumerate(price_tables):
        plan = "Go" if index == 0 else "Go Plus"
        plan_price = 10.0 if index == 0 else 40.0
        requests = {}
        if index < len(request_tables):
            rheader, rbody = request_tables[index]
            for rrow in rbody:
                model = (rrow[0] if rrow else "").strip()
                vals = []
                for col in rheader[1:]:
                    cell = pick(rheader, rrow, col)
                    vals.append(int(re.sub(r"[^\d]", "", cell)) if cell and re.search(r"\d", cell) else None)
                if model:
                    requests[model] = vals
        for row in body:
            model = (row[0] if row else "").strip()
            if not model or model.lower() in ("model", "unlimited"):
                continue
            inp = money(pick(header, row, "Input"))
            out = money(pick(header, row, "Output"))
            cread = money(pick(header, row, "Cached Read"))
            cwrite = money(pick(header, row, "Cached Write"))
            limit = money(pick(header, row, "Monthly limit"))
            if inp is None and out is None:
                continue  # a "Free"/"limited time" annotation row, not a price row
            blended = None
            if None not in (cread, inp, out):
                blended = MIX["cached_read"] * cread + MIX["input"] * inp + MIX["output"] * out
            tokens = (limit / blended) if (limit and blended) else None
            per_m = (plan_price / tokens) if tokens else None
            req = requests.get(model, [None, None, None])
            ratio = ""
            if req[1] and req[2]:
                r = req[2] / req[1]
                ratio = f"{r:.2f}"
                if not (4.0 <= r <= 4.6):
                    problems.append(f"{plan}/{model}: monthly is {r:.2f}x weekly, not ~4.33x")
            writer.writerow([
                plan, f"{plan_price:.0f}", model,
                "" if inp is None else inp, "" if out is None else out,
                "" if cread is None else cread, "" if cwrite is None else cwrite,
                "" if limit is None else f"{limit:.0f}",
                "" if blended is None else f"{blended:.4f}",
                "" if tokens is None else f"{tokens:.0f}",
                "" if per_m is None else f"{per_m:.4f}",
                *(str(v) if v is not None else "" for v in req), ratio,
                # Every blended and derived figure above is a function of this
                # one mix, so the grid carries it per row rather than leaving a
                # reader to find it in the tool's source.
                f"{MIX['cached_read'] * 100:g}% cache read / "
                f"{MIX['input'] * 100:g}% fresh input / "
                f"{MIX['output'] * 100:g}% output",
                path.name, READ_DATE,
            ])

    print(f"# price tables: {len(price_tables)}, request tables: {len(request_tables)}", file=sys.stderr)
    if problems:
        print("# window-column inconsistencies (vendor's own two clocks):", file=sys.stderr)
        for p in problems:
            print(f"#   {p}", file=sys.stderr)
    else:
        print("# every model's monthly request column is ~4.33x its weekly column", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
