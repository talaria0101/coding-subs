#!/usr/bin/env python3
"""Fetch community discussion as a feed to read, never as a search result set.

    python3 tools/fetch-community.py --sub opencode --query "usage limit" --out posts.xml

Two Reddit endpoints return full post bodies without authentication:

    https://www.reddit.com/r/<sub>/.rss
    https://www.reddit.com/r/<sub>/search.rss?q=<query>&restrict_sr=1&sort=new

**The second one silently ignores the query.** `search.rss` accepts `q=`,
returns HTTP 200 and a well-formed Atom feed, and serves recency-ordered posts
regardless of what was asked for. Reading its output as the result of a search
produces confident, well-formed, wrong evidence, which is the worst kind: it
looks exactly like a working search. This tool therefore **asserts the query was
honoured** rather than assuming it, by checking that a query token actually
appears in the returned feed, and it fails loudly when it does not.

Treat the output as a feed to read, not a set of results to filter. A feed that
does not mention your term still contains the recency window of the subreddit,
which is often what the reader wanted, but that is a different claim from "these
are the posts about X" and the tool will not make the second claim for you.

**`--mode new` fetches no query at all**, so a `--query` passed alongside it was
never executed. The first version accepted that combination, printed the feed
and exited 0, and `--append-to-log` then recorded a retrieval for a query the log
does not contain: the same defect as a provenance string asserting a lookup that
did not happen, reached by a different route. The combination is now refused, and
the refusal is not conditioned on the network being reachable - it happens before
the request, because it is a statement about what the caller asked for.

`--append-to-log` additionally verifies what it writes: a successful retrieval is
recorded as a log entry that must state a URL, the HTTP status and the SHA-256 of
the bytes on disk, and `fetch-log-corroborates` in `validate.py` recomputes that
hash against the archived file. A log entry that would not survive that check is
not written.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"


def get(url: str, timeout: int = 30) -> tuple[int, bytes]:
    request = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/atom+xml,text/xml,*/*"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.status, response.read()
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read()
    except Exception:  # noqa: BLE001
        return None, b""


def tokens(query: str) -> list[str]:
    """The distinctive words of a query, long enough not to match everything."""
    return [t for t in re.findall(r"[A-Za-z0-9]+", query.lower()) if len(t) >= 4]


def posix_relative(path: Path) -> str:
    """`path` as a POSIX path relative to the working directory.

    The first version wrote `saved_as` with backslashes on every platform. The
    gate resolves either separator, but a log is read by more than the gate, and
    a backslash is an ordinary filename character everywhere except Windows.
    """
    try:
        return Path(os.path.relpath(Path(path).resolve(), Path.cwd().resolve())).as_posix()
    except ValueError:
        return Path(path).resolve().as_posix()


def append_log(pass_dir: str, url: str, status: int, body: bytes,
               out: Path, args) -> int:
    """Record the retrieval that produced `out` in the pass's fetch log.

    An entry that does not satisfy the check `validate.py` runs over that log is
    not written, so the log cannot be made worse by using this tool.
    """
    log = Path(pass_dir) / "data" / "fetch-log.json"
    if not log.is_file():
        print(f"{log} does not exist; nothing appended", file=sys.stderr)
        return 1
    log.parent.mkdir(parents=True, exist_ok=True)
    entries = json.loads(log.read_text(encoding="utf-8"))
    url_only = url.split("?")[0]
    entries.append({
        "url": url_only,
        "http": status,
        "bytes": len(body),
        "ms": None,
        "sha256": hashlib.sha256(body).hexdigest(),
        "error": None,
        "route": "direct",
        "attempt": 1,
        "read_date": date.today().isoformat(),
        "note": args.note,
        "saved_as": posix_relative(out),
    })
    log.write_text(json.dumps(entries, indent=2) + "\n", encoding="utf-8")
    print(f"  appended {url_only} -> {log}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sub", required=True, help="subreddit name, without r/")
    parser.add_argument("--query", default="")
    parser.add_argument("--mode", default="search", choices=("search", "new"))
    parser.add_argument("--out", required=True)
    parser.add_argument("--min-hits", type=int, default=1,
                        help="how many query tokens must appear before the feed is accepted")
    parser.add_argument("--note", default="",
                        help="note recorded in the fetch-log entry this tool writes")
    parser.add_argument("--append-to-log", metavar="PASS_DIR",
                        help="append a fetch-log.json entry recording this retrieval")
    args = parser.parse_args()

    if args.mode == "new" and args.query:
        print(
            "--mode new fetches https://www.reddit.com/r/<sub>/.rss, which takes no "
            "query: the recency window of the whole subreddit. The --query you passed "
            "would not be sent, so no retrieval answering it would happen and no "
            "search result would be produced. Use --mode search to run a query, or "
            "drop --query to fetch the recency feed on purpose.",
            file=sys.stderr,
        )
        return 2

    if args.mode == "search":
        url = ("https://www.reddit.com/r/{sub}/search.rss?q={q}&restrict_sr=1&sort=new"
               .format(sub=args.sub, q=urllib.parse.quote(args.query)))
    else:
        url = f"https://www.reddit.com/r/{args.sub}/.rss"

    status, body = get(url)
    print(f"{url}\n  HTTP={status} bytes={len(body)}")
    if status != 200 or not body:
        print("  Reddit did not serve this feed. It returns 403 to unauthenticated clients "
              "from many vantage points; record it as unreachable rather than as empty.",
              file=sys.stderr)
        return 1

    text = body.decode("utf-8", errors="replace")
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(body)
    if args.append_to_log:
        append_log(args.append_to_log, url, status, body, out, args)

    entries = len(re.findall(r"<entry>", text))
    titles = re.findall(r"<title>(.*?)</title>", text, re.S)[1:]
    print(f"  {entries} entries -> {out}")

    if args.query:
        wanted = tokens(args.query)
        # Check the post titles and summaries, never the whole document: the feed
        # echoes the query back inside its own `<id>` and `<link>` elements, so a
        # search over the raw text finds the query there even when the feed
        # returned nothing at all. Measured on 2026-10-06:
        # `search.rss?q=zzzznonexistentterm` returns HTTP 200 and 0 entries.
        body_text = " ".join(
            re.sub(r"<[^>]+>", " ", m).lower()
            for m in re.findall(r"<(?:title|content|summary)>(.*?)</(?:title|content|summary)>",
                                text, re.S)
        )
        hits = {t: len(re.findall(re.escape(t), body_text)) for t in wanted}
        matched = sum(1 for count in hits.values() if count >= args.min_hits)
        print(f"  query tokens in titles/content: {hits}")
        if entries == 0 or matched == 0:
            print(
                "  QUERY NOT HONOURED. search.rss returned HTTP 200 and a well-formed feed "
                f"with {entries} entries, mentioning none of the query terms in its posts: it "
                "is serving the subreddit's recency window, not a search result set. The file "
                "is kept because a recency feed is still worth reading, but nothing in it is "
                "evidence about the query.",
                file=sys.stderr,
            )
            return 2
        print(f"  {matched}/{len(wanted)} query tokens present in post text: the feed is "
              f"consistent with the query. That is not proof the ranking is a search ranking.")
    for title in titles[:5]:
        print(f"    - {re.sub(r'<[^>]+>', '', title)[:90]}")
    if len(titles) > 5:
        print(f"    ... {len(titles) - 5} more")
    time.sleep(0.5)
    return 0


if __name__ == "__main__":
    sys.exit(main())