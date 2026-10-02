#!/usr/bin/env python3
"""Extract per-model token price grids from an archived vendor pricing page.

Reads `<table>` markup structurally and looks for the four-column shape that
makes a $/M figure computable: input, cached input, and output per 1M tokens.
Pages that publish only input and output (no cached tier) are still extracted,
and the missing column is left empty so the sensitivity table can show that the
figure is not computable rather than silently assuming a cache rate.

    python3 extract-token-prices.py PAGE OUT_CSV [--market]

`--market` records whether the prices are a metered market (API list prices) or
a subscription ceiling, because the two are different evidence classes and the
distinction is what the report rests on.
"""
import csv
import html
import io
import re
import sys
from pathlib import Path

SLUG = re.compile(r"^[a-z0-9][a-z0-9.\-]{2,48}$")
MONEY = re.compile(r"^\$?([\d,]+(?:\.\d+)?)$")


def money(cell: str):
    text = (cell or "").replace("−", "-").strip()
    if text in ("", "-", "—", "n/a"):
        return None
    match = MONEY.match(text)
    return float(match.group(1).replace(",", "")) if match else None


def tables(raw: str):
    """Yield (header, rows) per table.

    A page that splits pricing into 'Short context' and 'Long context' blocks puts
    a `colspan` group header above the real column names. Reading only the first
    `<tr>` as the header yields the group labels rather than the column names, and
    the table is then silently skipped, so every leading run of `<th>` rows is
    collected and the one that names a column role wins.
    """
    for block in re.finditer(r"(?is)<table\b[^>]*>(.*?)</table>", raw):
        header, rows = None, []
        pending, header, rows = [], None, []
        for row in re.finditer(r"(?is)<tr\b[^>]*>(.*?)</tr>", block.group(1)):
            is_header = bool(re.search(r"(?is)<th\b", row.group(1)))
            cells = [
                re.sub(r"\s+", " ", html.unescape(re.sub(r"(?s)<[^>]+>", " ", c))).strip()
                for c in re.findall(r"(?is)<t[hd]\b[^>]*>(.*?)</t[hd]>", row.group(1))
            ]
            if not cells:
                continue
            if is_header:
                pending.append(cells)
                if any(re.search(r"(?i)^(input|output|cached input|cache write)", c) for c in cells):
                    header = cells
                    pending = []
                continue
            if header is None and pending:
                for candidate in reversed(pending):
                    if any(re.search(r"(?i)^(input|output)", c) for c in candidate):
                        header = candidate
                        break
                pending = []
            if header is not None:
                rows.append(cells)
        if header:
            yield header, rows


def header_index(header: list[str]) -> dict:
    """Column roles, resolved by name. 'short context' and 'long context' blocks
    repeat the same roles, so the first block of each role wins."""
    roles = {}
    for i, col in enumerate(header):
        low = col.lower()
        for role, pattern in (
            ("input", r"^input"),
            ("cached", r"^cached input"),
            ("cache_write", r"^cache write"),
            ("output", r"^output"),
        ):
            if re.search(pattern, low) and role not in roles:
                roles[role] = i
    return roles


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    market = "--market" in sys.argv
    page = Path(args[0])
    out = Path(args[1] if len(args) > 1 else "data/token-prices.csv")
    raw = page.read_text(encoding="utf-8", errors="replace")

    rows, seen = [], set()
    for header, body in tables(raw):
        roles = header_index(header)
        if "input" not in roles or "output" not in roles:
            continue
        for cells in body:
            model = cells[0].strip().lower() if cells else ""
            if not SLUG.match(model) or model in seen:
                continue
            width = max(roles.values()) + 1
            if len(cells) <= width:
                continue
            record = {
                "model_slug": model,
                "input_per_m": money(cells[roles["input"]]),
                "cached_read_per_m": money(cells[roles["cached"]]) if "cached" in roles else None,
                "cache_write_per_m": money(cells[roles["cache_write"]]) if "cache_write" in roles else None,
                "output_per_m": money(cells[roles["output"]]),
            }
            if record["input_per_m"] is None and record["output_per_m"] is None:
                continue
            seen.add(model)
            record["price_class"] = "API-LIST" if market else "UNKNOWN"
            record["source"] = page.name
            record["read_date"] = "2026-10-02"
            rows.append(record)

    buf = io.StringIO()
    fields = ["model_slug", "input_per_m", "cached_read_per_m", "cache_write_per_m",
              "output_per_m", "price_class", "source", "read_date"]
    writer = csv.DictWriter(buf, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    for record in rows:
        writer.writerow({k: ("" if record.get(k) is None else record.get(k)) for k in fields})
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(buf.getvalue())

    print(f"{len(rows)} models with a token price grid -> {out}")
    for record in rows[:6]:
        print(f"  {record['model_slug']:<24} in {record['input_per_m']}  cached {record['cached_read_per_m']}  out {record['output_per_m']}")
    if len(rows) > 6:
        print(f"  ... and {len(rows) - 6} more")
    return 0


if __name__ == "__main__":
    sys.exit(main())
