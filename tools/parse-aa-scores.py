#!/usr/bin/env python3
"""Look models up on the Artificial Analysis board and record the ones that are absent.

    python3 tools/parse-aa-scores.py PAGE.html OUT.csv [--probe SLUG,SLUG,...]

`parse-aa-models.py` answers "which models does the board carry, and what do
they score". This answers the question that one cannot: **what did the board say
when you asked about a model it does not carry?**

That question came up in this pass because a plan row for "Muse Spark 1.3
Contributor" was ranked at II 48.09, which is the score of a different SKU, the
base "Muse Spark 1.3". The Contributor tier has no leaderboard row at all. A
parser that drops the row it cannot find makes an unscored SKU indistinguishable
from a low-scoring one, and a low-scoring one is merely disappointing while an
unscored one cannot be ranked at all.

So this tool emits a row for **every** sought slug, including the misses, with a
`lookup_verdict` of `scored` or `notFound`, and exits non-zero when a probe
cannot be resolved anywhere. A missing row is an answer here, not a gap.
"""
from __future__ import annotations

import argparse
import csv
import importlib.util
import io
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load_sibling():
    """Import parse-aa-models.py without needing it on sys.path."""
    spec = importlib.util.spec_from_file_location("parse_aa_models", HERE / "parse-aa-models.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


FIELDS = [
    "sought_slug", "present_on_board", "intelligence_index", "name_on_board",
    "creator", "lookup_verdict", "board_model_count",
]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("page", help="archived Artificial Analysis HTML")
    parser.add_argument("out", help="CSV to write")
    parser.add_argument("--probe", default="",
                        help="comma-separated slugs to look up explicitly")
    args = parser.parse_args()

    aa = load_sibling()
    raw = Path(args.page).read_text(encoding="utf-8", errors="replace")
    models = aa.model_objects(aa.flight_blob(raw))
    if not models:
        print("no models recovered from the flight payload", file=sys.stderr)
        return 1
    by_slug = {m.get("slug"): m for m in models if m.get("slug")}

    sought = list(args.probe.split(",")) if args.probe else sorted(by_slug)
    sought = [s.strip() for s in sought if s.strip()]

    buf = io.StringIO()
    writer = csv.writer(buf, lineterminator="\n")
    writer.writerow(FIELDS)
    misses = []
    for slug in sought:
        model = by_slug.get(slug)
        if model is None:
            misses.append(slug)
            writer.writerow([slug, "no", "", "", "", "notFound", len(models)])
            continue
        index = model.get("intelligenceIndex")
        creator = aa.flat(aa.pick(model, "creator"))
        writer.writerow([
            slug, "yes",
            "" if index is None else f"{index:.4f}",
            model.get("name", ""), creator,
            "scored" if index is not None else "noIndex",
            len(models),
        ])

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(buf.getvalue(), encoding="utf-8")

    print(f"board carries {len(models)} models; {len(sought)} slugs looked up -> {args.out}")
    if misses:
        print(f"  notFound ({len(misses)}): {', '.join(misses)}")
        print("  A notFound row is a result. It means the leaderboard has no Intelligence")
        print("  Index for that SKU, so no score may be published for it and no row")
        print("  borrowing another SKU's score may be ranked.")
    return 0


if __name__ == "__main__":
    sys.exit(main())