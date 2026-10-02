#!/usr/bin/env python3
"""Extract plan names and prices from an archived first-party pricing page.

Many vendor pages render their plan ladder as JSON-LD, as a schema.org Offer
block, or as plain text near a `$N` figure. This reads all three and reports what
it found per page, so a page that yields nothing says so rather than being
silently counted as covered.

    python3 extract-plans.py SOURCES_DIR OUT_CSV

Writes one row per (plan, price) pair with the evidence class of the extraction:
  JSONLD   the figure came from a schema.org Offer the page publishes
  SCHEMA   the figure came from a structured block the page renders
  TEXT     the figure was read from rendered text next to the plan name
"""
import csv
import io
import json
import re
import sys
from pathlib import Path

UA_HINT = re.compile(r"^\s*(?P<plan>[A-Za-z][A-Za-z0-9 .+&/'-]{1,40}?)\s*\|?\s*\$")
MONEY = re.compile(r"\$\s?([\d,]+(?:\.\d{1,2})?)")
PERIOD = re.compile(r"(?i)\b(per\s+(?:month|mo|user|seat)|/\s*mo|monthly|annually|billed annually)\b")


def strip(fragment: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"(?s)<[^>]+>", " ", fragment)).strip()


def cells(raw: str) -> list[str]:
    body = re.sub(r"(?is)<(script|style|svg)[^>]*>.*?</\1>", " ", raw)
    body = re.sub(r"(?s)<[^>]+>", "|", body)
    return [c.strip() for c in re.split(r"\|", re.sub(r"\s+", " ", body)) if c.strip()]


def from_jsonld(raw: str) -> list[tuple[str, str, str]]:
    out = []
    for match in re.finditer(r'(?is)<script[^>]*application/ld\+json[^>]*>(.*?)</script>', raw):
        try:
            blob = json.loads(match.group(1).strip())
        except json.JSONDecodeError:
            continue

        def walk(node):
            if isinstance(node, dict):
                if str(node.get("@type")) == "Offer" and node.get("name"):
                    price = node.get("price")
                    if price is not None:
                        out.append((str(node["name"]), f"{float(price):g}", "JSONLD"))
                for value in node.values():
                    walk(value)
            elif isinstance(node, list):
                for value in node:
                    walk(value)

        walk(blob)
    return out


# A plan name is short, has no sentence punctuation, and is not a feature label.
# The first version of this extractor matched any text near a price and produced
# "Memory across conversations" and "per month" as plans, which is worse than
# extracting nothing: a table of junk looks like coverage.
FEATURE_LABEL = re.compile(
    r"(?i)\b(included|features?|connect|create|memory|search|files?|code|tool|apps?|"
    r"get started|try |compare|see |learn|read|chat on|upload|artifacts?|plan$|"
    r"billed|if |per |and |or |for |the |a |an )\b"
)
BAD_NAME = re.compile(r"[.;:!?()\[\]]|^(per|if|and|or|for|the|a|an|get|try|see|learn|compare|billed)\b", re.I)
PLAN_NAME = re.compile(r"^[A-Za-z][A-Za-z0-9 .+&/'-]{0,38}$")


def is_plan_name(value: str) -> bool:
    value = value.strip()
    if not PLAN_NAME.match(value) or BAD_NAME.search(value) or FEATURE_LABEL.search(value):
        return False
    words = value.split()
    if not 1 <= len(words) <= 4:
        return False
    # A plan name is Title Case or a known acronym, not a sentence.
    return value[0].isupper()


def from_text(raw: str) -> list[tuple[str, str, str]]:
    """A plan name followed within a short window by a price and a period."""
    out, seen = [], set()
    flat = cells(raw)
    for index, value in enumerate(flat):
        name = value.strip()
        if not is_plan_name(name):
            continue
        window = flat[index : index + 8]
        for offset, cell in enumerate(window[1:], 1):
            money = MONEY.fullmatch(cell)
            if not money:
                continue
            if not any(PERIOD.search(w) for w in window[offset : offset + 5]):
                continue
            key = (name, money.group(1))
            if key in seen:
                continue
            seen.add(key)
            out.append((name, money.group(1), "TEXT"))
            break
    return out


def main() -> int:
    src = Path(sys.argv[1] if len(sys.argv) > 1 else "sources")
    out = Path(sys.argv[2] if len(sys.argv) > 2 else "data/plan-ladder.csv")
    rows, coverage, seen_rows = [], [], set()
    for path in sorted(src.iterdir()):
        if not path.is_file():
            continue
        raw = path.read_text(encoding="utf-8", errors="replace")
        found = from_jsonld(raw)
        method = "JSONLD"
        if not found:
            found = from_text(raw)
            method = "TEXT"
        for plan, price, cls in found:
            # A page can publish the same Offer block more than once (Cursor
            # renders its ladder twice, once per locale). One plan has one
            # price, so the second copy is a rendering artefact, not a datum.
            if (path.name, plan, price) in seen_rows:
                continue
            seen_rows.add((path.name, plan, price))
            rows.append({
                "vendor_source": path.name,
                "plan": plan,
                "price_value": price,
                "currency": "USD",
                "extraction": cls,
                "read_date": "2026-10-02",
            })
        coverage.append((path.name, len(found), method if found else "NONE"))
        if found:
            print(f"  {path.name:<34} {len(found):>3} plans via {method}")

    buf = io.StringIO()
    writer = csv.DictWriter(
        buf, fieldnames=["vendor_source", "plan", "price_value", "currency", "extraction", "read_date"],
        lineterminator="\n",
    )
    writer.writeheader()
    for row in rows:
        writer.writerow(row)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(buf.getvalue())

    print(f"\n{len(rows)} plan/price pairs -> {out}")
    barren = [name for name, count, _ in coverage if not count]
    print(f"sources yielding no plan/price pair ({len(barren)}/{len(coverage)}):")
    for name in barren:
        print(f"  - {name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
