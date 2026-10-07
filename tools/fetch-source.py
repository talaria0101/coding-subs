#!/usr/bin/env python3
"""Fetch a source over more than one route, with a backoff, without lying.

    python3 tools/fetch-source.py URL --out FILE [--via direct|jina|both]
                                     [--retries N] [--log fetch-log.json]

`fetch-firstparty.py` does one request per URL and never retries, which is the
right shape for a serial audit: "we asked once and this is what came back" is a
claim the log can support. It is the wrong shape when a search backend is
rate-limiting the vantage point, because one 429 is then indistinguishable from
a page that is genuinely unavailable.

This tool adds three things to that baseline, and each one is bounded:

* `--via jina` retrieves `https://r.jina.ai/<url>`, which renders
  JavaScript-served pages and returns plain text for pages a plain GET cannot
  read. It is a **second source**, not a better first source: the log records
  which route produced the bytes, because a figure read through a text extractor
  is not the same artefact as the vendor's own HTML.
* `--retries N` retries **only** 429 and 5xx, with exponential backoff. A 404
  is not retried, because a page that does not exist does not appear on a
  retry. A retry that succeeds is logged as an attempt that succeeded, never as
  the first attempt having succeeded.
* Every attempt is appended to the log with its route, status and byte count, so
  a reader can tell an intermittent failure from a consistently empty page.

It never converts a failure into a success: if every route and every attempt
fails, the exit code is non-zero and the saved file is the error body or
nothing at all.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

UA = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"
)

JINA_PREFIX = "https://r.jina.ai/"
RETRYABLE = {429, 500, 502, 503, 504, 522, 524}


def fetch_once(url: str, timeout: int = 45) -> dict:
    """One HTTP request. Returns the record; never raises."""
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": UA,
            "Accept": "text/html,application/xhtml+xml,application/json,text/plain,*/*",
            "Accept-Language": "en-US,en;q=0.9",
        },
    )
    started = time.time()
    status = None
    body = b""
    error = None
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            status = response.status
            body = response.read()
    except urllib.error.HTTPError as exc:
        status = exc.code
        body = exc.read()
        error = f"HTTP {exc.code}"
    except Exception as exc:  # noqa: BLE001 - the point is to record, not to raise
        error = f"{type(exc).__name__}: {exc}"[:200]
    return {
        "url": url,
        "http": status,
        "bytes": len(body),
        "ms": int((time.time() - started) * 1000),
        "sha256": hashlib.sha256(body).hexdigest() if body else None,
        "error": error,
        "_body": body,
    }


def fetch_with_retries(url: str, route: str, retries: int, timeout: int) -> list[dict]:
    """Attempt a URL up to `retries` extra times, retrying only 429 and 5xx.

    Returns every attempt, not only the last, so the log shows the shape of the
    failure. A 404 raises nothing and returns immediately: the page is absent,
    and asking again does not make it present.
    """
    attempts: list[dict] = []
    for attempt in range(retries + 1):
        record = fetch_once(url, timeout)
        record["route"] = route
        record["attempt"] = attempt + 1
        attempts.append(record)
        status = record["http"]
        if status == 200:
            break
        if status is not None and status not in RETRYABLE:
            break
        if attempt < retries:
            # Exponential backoff. A rate limiter that is asked again
            # immediately is a rate limiter that keeps answering 429.
            time.sleep(min(2 ** attempt, 30))
    return attempts


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url")
    parser.add_argument("--out", required=True, help="where to save the body")
    parser.add_argument("--via", default="direct", choices=("direct", "jina", "both"))
    parser.add_argument("--retries", type=int, default=2)
    parser.add_argument("--timeout", type=int, default=45)
    parser.add_argument("--log", help="append every attempt to this JSON log")
    parser.add_argument("--append", action="store_true", help="append to the log, not replace")
    args = parser.parse_args()

    routes = [("direct", args.url)]
    if args.via in ("jina", "both"):
        routes.append(("jina", JINA_PREFIX + args.url))

    all_attempts: list[dict] = []
    saved = False
    for route, url in routes:
        attempts = fetch_with_retries(url, route, args.retries, args.timeout)
        for attempt in attempts:
            status = attempt["http"] if attempt["http"] is not None else "ERR"
            print(
                f"{route:>6} try{attempt['attempt']} {status!s:<5} "
                f"{attempt['bytes']:>9} B  {attempt['ms']:>5} ms  {attempt['error'] or ''}",
                flush=True,
            )
        all_attempts.extend(attempts)
        if attempts[-1]["http"] == 200 and attempts[-1]["_body"]:
            body = attempts[-1].pop("_body")
            out = Path(args.out)
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_bytes(body)
            attempts[-1]["saved_as"] = str(out)
            for attempt in attempts[:-1]:
                attempt["_body"] = None
            saved = True
            break
        for attempt in attempts:
            attempt["_body"] = None

    if args.log:
        path = Path(args.log)
        existing = []
        if args.append and path.is_file():
            try:
                existing = json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                existing = []
        for attempt in all_attempts:
            attempt.pop("_body", None)
        existing.extend(all_attempts)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(existing, indent=2), encoding="utf-8")

    if not saved:
        print(f"no route returned 200 for {args.url}; nothing written to {args.out}",
              file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())