#!/usr/bin/env python3
"""Fetch a source over more than one route, with a backoff, without lying.

    python3 tools/fetch-source.py URL --out FILE [--via direct|jina|both]
                                     [--jina-out FILE] [--user-agent NAME]
                                     [--retries N] [--log fetch-log.json]

`fetch-firstparty.py` does one request per URL and never retries, which is the
right shape for a serial audit: "we asked once and this is what came back" is a
claim the log can support. It is the wrong shape when a search backend is
rate-limiting the vantage point, because one 429 is then indistinguishable from
a page that is genuinely unavailable.

This tool adds four things to that baseline, and each one is bounded:

* `--via` names the routes, and each route is exactly the route named.
  `direct` (the default) is a plain GET of the URL. `jina` retrieves only
  `https://r.jina.ai/<url>`, which renders JavaScript-served pages and returns
  plain text for pages a plain GET cannot read; it never tries the direct route
  first, so the bytes saved by a `--via jina` run are always jina's. `both`
  fetches the direct route into `--out` and then the jina route into
  `--jina-out` (default: `--out` with `.jina.txt` replacing its suffix), two
  files for two artefacts. Jina is a **second source**, not a better first
  source: a figure read through a text extractor is not the same artefact as the
  vendor's own HTML, so the log entry that carries `saved_as` also carries the
  `route` that produced those bytes.
* `--user-agent` picks the User-Agent: a preset name (`chrome`, the default and
  the header every earlier log was fetched with, or `curl`) or a literal string,
  logged as `custom`. Servers answer user agents differently: on 2026-10-07
  r.jina.ai answered the Chrome UA with a Cloudflare 403 and ai.google.dev with
  a 302, where a non-browser UA got 200. Every attempt records the preset name
  as `ua` and the exact header as `user_agent`.
* `--retries N` retries **only** 429 and 5xx, with exponential backoff. A 404
  is not retried, because a page that does not exist does not appear on a
  retry. A retry that succeeds is logged as an attempt that succeeded, never as
  the first attempt having succeeded.
* Every attempt is appended to the log with its route, user agent, status and
  byte count, so a reader can tell an intermittent failure from a consistently
  empty page. `saved_as` is a POSIX path relative to the working directory,
  whatever the platform, so a log written on Windows reads the same as one
  written on Linux.

It never converts a failure into a success: the exit code is zero only when
every requested route saved a 200 body, and a route that failed writes nothing.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

UA = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"
)

# Preset user agents by the name the log records. `chrome` resolves to `UA` at
# call time rather than being copied here, so a caller that rebinds `UA` on the
# module still sends, and logs, the header it set.
USER_AGENTS = {
    "chrome": None,
    "curl": "curl/8.5.0",
}

JINA_PREFIX = "https://r.jina.ai/"
RETRYABLE = {429, 500, 502, 503, 504, 522, 524}


def resolve_user_agent(value: str) -> tuple[str, str]:
    """(name the log records, header sent) for a preset name or a literal string."""
    if value in USER_AGENTS:
        header = USER_AGENTS[value]
        return value, UA if header is None else header
    return "custom", value


def posix_relative(path: Path) -> str:
    """`path` as a POSIX path relative to the working directory.

    Falls back to the absolute POSIX path only where no relative path exists,
    which is a different drive on Windows.
    """
    try:
        return Path(os.path.relpath(Path(path).resolve(), Path.cwd().resolve())).as_posix()
    except ValueError:
        return Path(path).resolve().as_posix()


def fetch_once(url: str, timeout: int = 45, user_agent: str | None = None) -> dict:
    """One HTTP request. Returns the record; never raises."""
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": UA if user_agent is None else user_agent,
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


def fetch_with_retries(url: str, route: str, retries: int, timeout: int,
                       ua: tuple[str, str] | None = None) -> list[dict]:
    """Attempt a URL up to `retries` extra times, retrying only 429 and 5xx.

    Returns every attempt, not only the last, so the log shows the shape of the
    failure. A 404 raises nothing and returns immediately: the page is absent,
    and asking again does not make it present.
    """
    ua_name, ua_header = ua if ua is not None else resolve_user_agent("chrome")
    attempts: list[dict] = []
    for attempt in range(retries + 1):
        record = fetch_once(url, timeout, ua_header)
        record["route"] = route
        record["attempt"] = attempt + 1
        record["ua"] = ua_name
        record["user_agent"] = ua_header
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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("url")
    parser.add_argument("--out", required=True,
                        help="where to save the body: the direct bytes, or the jina "
                             "bytes under --via jina")
    parser.add_argument("--via", default="direct", choices=("direct", "jina", "both"),
                        help="direct only (default), jina only, or both into two files")
    parser.add_argument("--jina-out",
                        help="under --via both, where the jina bytes go "
                             "(default: --out with its suffix replaced by .jina.txt)")
    parser.add_argument("--jina-prefix", default=JINA_PREFIX,
                        help=f"the jina reader endpoint the URL is appended to "
                             f"(default {JINA_PREFIX})")
    parser.add_argument("--user-agent", default="chrome", metavar="NAME_OR_STRING",
                        help=f"a preset ({', '.join(USER_AGENTS)}; default chrome) or a "
                             f"literal User-Agent string, logged as 'custom'")
    parser.add_argument("--retries", type=int, default=2)
    parser.add_argument("--timeout", type=int, default=45)
    parser.add_argument("--log", help="append every attempt to this JSON log")
    parser.add_argument("--append", action="store_true", help="append to the log, not replace")
    args = parser.parse_args(argv)

    out = Path(args.out)
    if args.via == "direct":
        routes = [("direct", args.url, out)]
    elif args.via == "jina":
        routes = [("jina", args.jina_prefix + args.url, out)]
    else:
        jina_out = Path(args.jina_out) if args.jina_out else out.with_suffix(".jina.txt")
        if jina_out.resolve() == out.resolve():
            parser.error("--jina-out must differ from --out under --via both")
        routes = [("direct", args.url, out), ("jina", args.jina_prefix + args.url, jina_out)]
    if args.jina_out and args.via != "both":
        parser.error("--jina-out only applies to --via both")
    ua = resolve_user_agent(args.user_agent)

    all_attempts: list[dict] = []
    failed: list[str] = []
    for route, url, target in routes:
        attempts = fetch_with_retries(url, route, args.retries, args.timeout, ua)
        for attempt in attempts:
            status = attempt["http"] if attempt["http"] is not None else "ERR"
            print(
                f"{route:>6} try{attempt['attempt']} {status!s:<5} "
                f"{attempt['bytes']:>9} B  {attempt['ms']:>5} ms  ua={attempt['ua']}  "
                f"{attempt['error'] or ''}",
                flush=True,
            )
        all_attempts.extend(attempts)
        last = attempts[-1]
        if last["http"] == 200 and last["_body"]:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(last["_body"])
            last["saved_as"] = posix_relative(target)
            print(f"saved {last['saved_as']} from route {route} ({last['bytes']} B)",
                  flush=True)
        else:
            failed.append(f"{route} ({url})")
        for attempt in attempts:
            attempt.pop("_body", None)

    if args.log:
        path = Path(args.log)
        existing = []
        if args.append and path.is_file():
            try:
                existing = json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                existing = []
        existing.extend(all_attempts)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(existing, indent=2), encoding="utf-8")

    if failed:
        print(f"no 200 body from route(s) {', '.join(failed)}; nothing written for them",
              file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())