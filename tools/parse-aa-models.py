#!/usr/bin/env python3
"""Extract the model landscape from the archived Artificial Analysis page.

The page ships its data as React Server Component flight payloads rather than as
a JSON island, so a regex for `"intelligenceIndex"` on the raw HTML finds
nothing and the scores have to be recovered from the concatenated, unescaped
flight chunks.

Writes data/models-database.csv with one row per model: the Intelligence Index,
Terminal-Bench 4.0 where published, context window, modalities and API prices.
"""
import csv
import io
import json
import re
import sys
from pathlib import Path

# The AA payload uses short keys in places; these are the fields this repo ranks on.
FIELDS = [
    "slug", "name", "creator", "releaseDate", "intelligenceIndex",
    "terminalbenchV40", "terminalbenchV21", "terminalbenchHard",
    "contextWindowTokens", "isOpenWeights", "inputModalityImage",
    "price1mInputTokens", "price1mOutputTokens", "cacheHitPrice",
    "price1mBlended0To3To1", "medianOutputSpeed", "deprecated",
]

def flight_blob(raw: str) -> str:
    chunks = re.findall(r'self\.__next_f\.push\(\[1,"(.*?)"\]\)', raw, re.S)
    joined = "".join(chunks)
    # The payload is a JS string literal; unescape it without mangling quotes.
    try:
        return json.loads('"' + joined.replace("\\'", "'") + '"')
    except json.JSONDecodeError:
        return joined.encode().decode("unicode_escape")


def model_objects(blob: str) -> list[dict]:
    """Every model object in the payload, identified by its slug and an II.

    The payload stores models under keys such as `initialModels` and `allModels`,
    and a model's `id` is a UUID rather than a number, so objects are located by
    their slug field and brace-matched to the closing brace. A model object
    exceeds 400 KB only in pathological cases; the practical limit here is raised
    so that a long object is not truncated mid-scan and silently dropped.
    """
    found, seen = [], set()
    for match in re.finditer(r'\{"id":"[0-9a-f\-]{36}","slug":"[a-z0-9.\-]+"', blob):
        start = match.start()
        depth, in_string, escape = 0, False, False
        for end in range(start, min(start + 2_000_000, len(blob))):
            ch = blob[end]
            if in_string:
                if escape:
                    escape = False
                elif ch == "\\":
                    escape = True
                elif ch == '"':
                    in_string = False
                continue
            if ch == '"':
                in_string = True
            elif ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    try:
                        obj = json.loads(blob[start : end + 1])
                    except json.JSONDecodeError:
                        break
                    if obj.get("intelligenceIndex") is not None:
                        key = obj.get("slug") or obj.get("id")
                        if key not in seen:
                            seen.add(key)
                            found.append(obj)
                    break
    return found


def flat(value):
    """Flatten the nested objects AA puts in some fields.

    `creator` arrives as `{"id": ..., "slug": "meta", "name": "Meta"}` and
    `inputModalityImage` may be a dict of per-modality detail. Writing the raw
    dict into a CSV cell produces a field full of braces and commas, which
    shifts every column after it, so the useful part is unwrapped here.
    """
    if isinstance(value, dict):
        for key in ("name", "slug", "value", "supported", "isSupported"):
            if key in value:
                return flat(value[key])
        return ""
    if isinstance(value, list):
        return ";".join(str(flat(v)) for v in value)
    if isinstance(value, bool):
        return "yes" if value else "no"
    if isinstance(value, float):
        return f"{value:.4f}".rstrip("0").rstrip(".")
    return "" if value is None else str(value)


def pick(obj: dict, key: str):
    if key in obj:
        return obj[key]
    for nested in ("pricing", "performance", "median", "modalities", "creator", "creators"):
        block = obj.get(nested)
        if isinstance(block, dict) and key in block:
            return block[key]
    return None


def main() -> int:
    path = Path(sys.argv[1] if len(sys.argv) > 1 else "sources/aa-models.html")
    out = Path(sys.argv[2] if len(sys.argv) > 2 else "data/models-database.csv")
    raw = path.read_text(encoding="utf-8", errors="replace")

    models = model_objects(flight_blob(raw))
    if not models:
        print("no models recovered from the flight payload", file=sys.stderr)
        return 1
    models.sort(key=lambda m: -(m.get("intelligenceIndex") or 0))

    def cell(m, key):
        return flat(pick(m, key))

    buf = io.StringIO()
    writer = csv.writer(buf, lineterminator="\n")
    writer.writerow(FIELDS)
    for m in models:
        writer.writerow([cell(m, f) for f in FIELDS])
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(buf.getvalue())

    with_tb = sum(1 for m in models if m.get("terminalbenchV40") is not None)
    print(f"{len(models)} models -> {out}")
    print(f"  with Terminal-Bench 4.0 published: {with_tb}")
    print(f"  top 5 by Intelligence Index: "
          + ", ".join(f"{(m.get('name') or m.get('slug'))} {(m.get('intelligenceIndex') or 0):.2f}"
                      for m in models[:5]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
