#!/usr/bin/env python3
"""Parse the OpenCode Go / Go Plus tables structurally from the fetched HTML.

The earlier tag-splitting approach lost rows and shifted columns, because a row
whose "Cached Write" cell is "-" or absent does not occupy the same number of
cells as one that has a price. This reads <table>/<tr>/<th>/<td> instead, so
column identity comes from the header, not from position.

Emits CSV to stdout and a short consistency report to stderr.
"""
import csv
import html
import io
import re
import sys
from pathlib import Path

MIX = {"cached_read": 0.97, "input": 0.025, "output": 0.005}


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
    path = Path(sys.argv[1] if len(sys.argv) > 1 else "raw/opencode-go.html")
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
# translation, and pinning lineterminator to "\r\n" matches the committed bytes,
# so the output is byte-identical on either platform.
    sys.stdout.reconfigure(newline="")
    writer = csv.writer(sys.stdout, lineterminator="\r\n")
    writer.writerow(
        ["plan", "plan_price_usd_month", "model", "input_per_m", "output_per_m",
         "cached_read_per_m", "cached_write_per_m", "monthly_limit_usd",
         "blended_per_m", "tokens_m_at_ceiling", "usd_per_m_tokens",
         "requests_per_5h", "requests_per_week", "requests_per_month",
         "monthly_over_weekly"]
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
