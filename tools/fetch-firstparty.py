#!/usr/bin/env python3
"""Serial first-party fetcher for the coding-subs pass.

One URL, one request, one file, one log line. No retries: a failure is recorded
as a failure rather than retried into a success, because "we asked twice" is a
different claim from "the page says this" and the log has to support the weaker
one honestly.

Usage:
    python3 fetch_firstparty.py OUT_DIR LOG_JSON SOURCES_TSV

SOURCES_TSV is tab-separated: label<TAB>url[<TAB>note]
"""
import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.request

UA = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"
)


def one_request(url: str, timeout: int = 45) -> dict:
    """Exactly one HTTP request. Returns the record; never raises."""
    req = urllib.request.Request(
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
        with urllib.request.urlopen(req, timeout=timeout) as response:
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


def main() -> int:
    out_dir, log_path, sources_path = sys.argv[1], sys.argv[2], sys.argv[3]
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(os.path.dirname(log_path) or ".", exist_ok=True)

    wanted: list[tuple[str, str, str]] = []
    with open(sources_path) as handle:
        for line in handle:
            line = line.rstrip("\n")
            if not line or line.startswith("#"):
                continue
            parts = line.split("\t")
            wanted.append((parts[0], parts[1], parts[2] if len(parts) > 2 else ""))

    log = []
    for index, (label, url, note) in enumerate(wanted, 1):
        record = one_request(url)
        body = record.pop("_body", b"")
        # The bytes are the evidence. Keep them whenever the server said 200,
        # and never for an error page, which is not the source.
        if record["http"] == 200 and body:
            path = os.path.join(out_dir, label)
            os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
            with open(path, "wb") as handle:
                handle.write(body)
            record["saved_as"] = os.path.relpath(path, os.path.dirname(out_dir) or ".")
        else:
            record["saved_as"] = None
        record["label"] = label
        record["note"] = note
        log.append(record)
        status = record["http"] if record["http"] is not None else "ERR"
        print(
            f"[{index:>2}/{len(wanted)}] {label:<34} {status!s:<5} "
            f"{record['bytes']:>9} B  {record['ms']:>5} ms  {record['error'] or ''}",
            flush=True,
        )
        # Politeness, and it keeps a serial pass from looking like a burst.
        time.sleep(0.7)

    with open(log_path, "w") as handle:
        json.dump(log, handle, indent=2)

    ok = sum(1 for r in log if r["http"] == 200)
    print(f"\n{ok}/{len(log)} returned HTTP 200; log written to {log_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
