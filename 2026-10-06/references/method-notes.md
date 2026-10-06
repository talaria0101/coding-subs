# Method notes

Retrieval and measurement techniques that generalise past this pass, with the limitation each one
has. No host details, no session history.

---

## 1. A second route for a page that will not serve a plain GET

`https://r.jina.ai/<url>` retrieves a URL and returns the readable content as plain text. It renders
JavaScript-served pages and gets past some Cloudflare interstitials, so it is worth one attempt when
a direct request returns a 403, a 429, or an empty shell. `tools/fetch-source.py --via jina` does
this and records which route produced the bytes.

Measured on this pass:

| URL | direct | via `r.jina.ai` |
|---|---|---|
| `https://docs.anthropic.com/en/docs/about-claude/pricing` | 301, 167 B | **200, 31,314 B** |
| `https://www.reddit.com/r/opencode/` | 403, 1,522 B | 200, 469 B — and the body is Reddit's own block page |
| `https://imagen.runpod.io/` | — | 422, 246 B |

**Limitation.** It is a second source, not a better first source. The text is an extraction of
someone else's render, so a figure read this way is not the vendor's bytes and the log records the
route for that reason. The Reddit row is the instructive one: `r.jina.ai` returned HTTP 200 with
469 bytes whose content was `You've been blocked by network security.` **A 200 from the extractor is
not a 200 from the origin**, and a reader who treats it as one would record a page as reached that
was not. Read what came back before recording it.

## 2. Reddit as a feed, and the trap in `search.rss`

Two endpoints return full post bodies with no authentication:

```
https://www.reddit.com/r/<sub>/.rss
https://www.reddit.com/r/<sub>/search.rss?q=<query>&restrict_sr=1&sort=new
```

**The second one silently ignores the query.** Measured: `search.rss?q=zzzznonexistentterm` on
r/opencode returned HTTP 200, a well-formed Atom feed, and **0 entries**. A request for a term that
does not exist and a successful search are indistinguishable from the status line and the XML alone.

The query also appears in the feed's own `<id>` and `<link>` elements, so a naive "does my term
appear in this document" test passes on the echo. `tools/fetch-community.py` checks the post
`<title>` and `<content>` only, treats zero entries as failure, and exits 2 when the query was not
honoured. Treat the output as a feed to read, never as a result set to filter.

**Limitation.** These endpoints are undocumented and rate-limit. Reddit returned 403 to a default
curl User-Agent on this pass and 200 to a browser-like one, which means reachability here is a
property of the request headers and not of the network. Record a 403 as unreachable rather than as
an empty result; an empty result and a refused request are different claims.

## 3. `gh api` with `--paginate`, and the counter that overcounts

`gh api --paginate` is how a large issue tracker gets mined. Two things to know before quoting a
count:

**GitHub's `open_issues_count` includes pull requests.** Measured on two repos in this pass:

| repo | `open_issues_count` | issues only (`is:issue is:open`) | PRs only (`is:pr is:open`) |
|---|---|---|---|
| `anomalyco/opencode` | 6,242 | 4,615 | 1,627 |
| `Wei-Shaw/sub2api` | 3,570 | 2,625 | 945 |

Both sum exactly. A tracker quoted as "3,571 open issues" is overcounting by 945, which is a 56%
overstatement and it reads as a health signal when it is a mix of two different things.

```bash
gh api "search/issues?q=repo:OWNER/NAME+is:issue+is:open&per_page=1" --jq .total_count
gh api "search/issues?q=repo:OWNER/NAME+is:pr+is:open&per_page=1"     --jq .total_count
```

**Limitation.** Search totals are eventually consistent and can lag a few seconds behind the repo
metadata endpoint. Quote both numbers and the date, and never quote `open_issues_count` alone.

## 4. Machine-readable JSON out of a rendered shell

Several vendor and leaderboard pages ship their data inside a React Server Component flight payload
rather than as a JSON island, so a regex for `"intelligenceIndex"` over the raw HTML finds nothing.
The payload is the concatenation of `self.__next_f.push([1,"…"])` chunks, and each chunk is a JS
string literal that has to be unescaped before it will parse as JSON. `tools/parse-aa-models.py`
does this, and `tools/parse-aa-scores.py` uses it to answer the question a landscape parser cannot:
what the board returned for a model it does not carry.

**Limitation.** Brace-matching over a payload that has no closing delimiter is a guess about where
an object ends, so the scan has to fail loudly on a truncated object rather than silently emit a
partial one. A parser that drops the rows it cannot parse is the exact defect this pass exists to
correct, so the parser must report a count and the reader must compare it against an independent
count: the payload here holds 48 UUID-and-slug objects, 24 of which are models and 24 providers.

## 5. `/llms.txt` and `/docs/*.md`

Several vendors publish a plain-Markdown rendering of their docs alongside the HTML, and the Markdown
is usually the better archive: it is smaller, it is not a client-rendered shell, and it diffs
cleanly between passes. `https://opencode.ai/docs/go.md` served 39,692 bytes of the whole usage-limits
table as Markdown where the HTML page needs JavaScript to render the same table. When both exist,
archive the Markdown and say so, because a figure read from it was read from a different artefact
than the same figure read from the HTML.

**Limitation.** A Markdown rendering can lag or lead the HTML, and there is no published rule saying
which is authoritative. Both URLs for a source, both hashes in the log.

## 6. The discipline that changed the answers

**Enumerate at least three candidate explanations for a figure before testing one.** The pooled-meter
question had three live readings and each was testable: (a) the docs are right and the ceilings are
independent, (b) the ceilings are a shared pool, (c) the meter is a sum of per-model percentages
rather than a ratio of dollars to a pool. The third reading turned out to be a *distinct* mechanism
with its own arithmetic — `anomalyco/opencode#47547` reports 47.8 + 34.7 + 17.5 = 100.0% exactly,
which no shared-pool model predicts — and it would have been invisible had the pool reading been
accepted first because it also fits the other four issues.

**Require a control run to detect a rate limit rather than inferring one.** A 403 from one host is
indistinguishable from a 403 from that host's edge. Two controls settle it: fetch a known-good URL
from the same vantage point at the same moment, and fetch the failing URL through a second route.
On this pass, direct Anthropic returned 301 while `r.jina.ai` returned 200 with content, which
locates the failure at the edge rather than in the network; and Reddit returned 403 to a default
User-Agent and 200 to a browser-like one, which locates it in the request.

**A number's unit is a claim, so check it against a stored row.** The one arithmetic error in this
research was `25.81亿` read as 25.81 billion when the stored row said `monthly_tokens:
2581000000`. Two independent analysts made the same mis-read from the same file, which is the
strongest possible evidence that reading a number is not the same as checking one. What catches it
is not care: it is re-deriving from the stored row, which is now `unit-scale` in `tools/validate.py`.