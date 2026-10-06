#!/usr/bin/env python3
"""Compute a plan's monthly token yield from a dollar ceiling, and print the arithmetic.

    python3 tools/derive-yields.py --ceiling 60 --input 0.15 --output 0.60 --cache 0.003
    python3 tools/derive-yields.py --ceiling 60 --input 0.10 --output 0.20 --cache 0.002 \
        --mix 100/0/0 --ceiling-basis min --pool 60 --cap 60

Every figure in this repo that is written "N tokens/month for $X" is this
division:

    blended $/M  = cache_share*cache + input_share*input + output_share*output
    tokens M     = ceiling_usd / blended $/M

The blended rate is the whole difficulty. It moves 5.3x to 29.0x across mixes
on this market's own price grids, so a yield published without its mix is a
number with an unstated divisor, which is the defect `mix-declared` in
validate.py exists to refuse. `--mix` takes cache/input/output as three
percentages or three fractions and defaults to the audited standard mix.

`--ceiling-basis min` is the other half. Where a plan publishes a per-model cap
against a shared monthly pool, the drawable ceiling is min(pool, cap) and not the
cap alone. Passing `--cap` below `--pool` reproduces that, and the tool says so
rather than leaving the reader to notice.

The arithmetic is printed in full, including the no-cache worst case, because a
yield that can only be reproduced by re-deriving it is an assertion.
"""
from __future__ import annotations

import argparse
import sys

DEFAULT_MIX = (97.0, 2.5, 0.5)


def parse_mix(text: str) -> tuple[float, float, float]:
    parts = [p.strip() for p in text.replace(",", "/").split("/") if p.strip() != ""]
    if len(parts) != 3:
        raise SystemExit(f"--mix takes three numbers cache/input/output, got {text!r}")
    try:
        values = [float(p) for p in parts]
    except ValueError as exc:
        raise SystemExit(f"--mix must be three numbers: {exc}")
    total = sum(values)
    if total <= 0:
        raise SystemExit("--mix must be positive")
    # Accept either percentages or fractions. Three numbers summing to 1 are
    # already fractions; three summing to 100 are percentages. Anything else is
    # a typo, and guessing at a mix is how an unstated divisor gets published.
    if abs(total - 1.0) < 1e-9:
        return tuple(values)  # type: ignore[return-value]
    if abs(total - 100.0) < 1e-9:
        return tuple(v / 100.0 for v in values)  # type: ignore[return-value]
    raise SystemExit(
        f"--mix values sum to {total:g}, which is neither 1 nor 100. "
        f"Pass three fractions (0.97/0.025/0.005) or three percentages (97/2.5/0.5)."
    )


def blended(cache_share, input_share, output_share, cache, inp, out) -> float:
    return cache_share * cache + input_share * inp + output_share * out


def report(args) -> None:
    cs, is_, os_ = parse_mix(args.mix)
    ceiling = args.ceiling
    if args.ceiling_basis == "min":
        if args.pool is None or args.cap is None:
            raise SystemExit("--ceiling-basis min needs both --pool and --cap")
        ceiling = min(args.pool, args.cap)
        taken = "pool" if args.pool <= args.cap else "cap"
        print(f"ceiling      = min(pool ${args.pool:g}, cap ${args.cap:g}) = ${ceiling:g}  (the {taken} binds)")
    else:
        print(f"ceiling      = ${ceiling:g}  (independent per-model ceiling; use "
              f"--ceiling-basis min --pool P --cap C where a pool exists)")

    print(f"prices       = input ${args.input:g}  output ${args.output:g}  cache read ${args.cache:g} per 1M")
    print(f"mix          = {cs * 100:g}% cache read / {is_ * 100:g}% fresh input / {os_ * 100:g}% output")

    b = blended(cs, is_, os_, args.cache, args.input, args.output)
    print()
    print("  blended $/M = "
          f"({cs:g}*{args.cache:g} + {is_:g}*{args.input:g} + {os_:g}*{args.output:g})")
    print(f"             = {b:.6f} $/M")

    if b > 0:
        tokens = ceiling / b
        print()
        print(f"  yield       = ${ceiling:g} / {b:.6f} $/M")
        print(f"             = {tokens:,.0f} M tokens/month = {tokens / 1000:.3f} B")

    worst = blended(0.0, 0.75, 0.25, args.cache, args.input, args.output)
    if worst > 0:
        wt = ceiling / worst
        print()
        print("  no-cache worst case (0% / 75% / 25%):")
        print(f"    blended   = (0.75*{args.input:g} + 0.25*{args.output:g}) = {worst:.6f} $/M")
        print(f"    yield     = {wt:,.0f} M = {wt / 1000:.3f} B")
        if b > 0:
            print(f"    the mix moves this yield by {tokens / wt:.1f}x")

    cache_only = args.cache
    if cache_only > 0:
        ct = ceiling / cache_only
        print()
        print("  100% cache read floor (the cheapest possible traffic):")
        print(f"    yield     = ${ceiling:g} / ${cache_only:g} = {ct:,.0f} M = {ct / 1000:.3f} B")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--ceiling", type=float, required=True,
                        help="drawable monthly ceiling in USD")
    parser.add_argument("--input", type=float, required=True, help="input $/1M")
    parser.add_argument("--output", type=float, required=True, help="output $/1M")
    parser.add_argument("--cache", type=float, required=True, help="cached read $/1M")
    parser.add_argument("--mix", default="97/2.5/0.5",
                        help="cache/input/output, as fractions summing to 1 or percentages summing to 100")
    parser.add_argument("--ceiling-basis", default="independent", choices=("independent", "min"))
    parser.add_argument("--pool", type=float, help="shared monthly pool in USD")
    parser.add_argument("--cap", type=float, help="per-model cap in USD")
    args = parser.parse_args()
    report(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())