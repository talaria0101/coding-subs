# coding-subs

Market research on the **cheapest legitimate ways to get large amounts of frontier-level
coding-agent usage by subscription** — model landscape, provider arbitrage, published quotas,
1M-context verification, and heavy-usage economics.

## Research passes

| Date | Report | Scope |
|---|---|---|
| **2026-09-13** | [2026-09-13/README.md](2026-09-13/README.md) | Full pass: 45-model landscape (AA snapshot), 44 access plans across 26 provider groups, workload tests, rankings |
| **2026-09-20** | [2026-09-20/README.md](2026-09-20/README.md) | Re-verification + delta pass: all first-party sources re-fetched, 26 logged changes (Trae repriced upward, Kimi tiers restructured with the weekly window removed, Claude Code limits settled ~17% below the promo level, new Command Code / Devin / Kiro / Factory / Warp / Zed / Replit ladders), every non-USD price normalized at a cited FX rate, and the relay/sponsor "0.03x" market quarantined into a red-flag advisory instead of a ranking |
| **2026-10-02** | [2026-10-02/README.md](2026-10-02/README.md) | Method pass: 20 first-party sources fetched serially with a per-source log, the OpenCode Go per-model grid parsed to 78 reproducible rows, the finding that a $/M token price is undefined until its traffic mix is stated (5.3x to 29.0x swing, median 13.6x), an anonymous-access measurement of 25 free-tier endpoints, and a re-derivation of a metered allowance project |
| **2026-10-06** | [2026-10-06/README.md](2026-10-06/README.md) | Correction pass: the market's negative result stated as arithmetic rather than as a search gap (**no plan reaches >=10,000M tokens/month for <=$10 on a verified model**; $10 of raw credit buys at most 5,000M on the cheapest qualifying price), two corrections to earlier passes (**OpenCode Go's $60 is a shared pool, not independent per-model budgets**; the **190x SuperGrok multiplier is retracted by its own source**), the two SKUs whose scores were inherited from other models, relays measured rather than excluded by category, and four new integrity checks |

Each pass directory contains the report (`README.md`), the underlying databases (`data/`),
numbered citations with access dates (`references/`), and raw snapshots of primary sources
(`sources/`).

## Read this before using any $/M figure in this repo

A price per million tokens is not a measurement. It is a division, and the divisor is a traffic
mix: what fraction of the traffic was cache reads, fresh input, and output. Vendors price those
three very differently, so the same plan on the same page yields figures that differ by 5x to 29x
depending on the mix you assume. The 2026-10-02 pass exists because a previous pass published
$0.0013/M, declared it wrong, and republished $0.0208/M as a 16x correction, when the two numbers
are the same method under two different unstated assumptions.

Every $/M in the 2026-10-02 tables is therefore published next to the mix that produced it, and the
full 78-row vendor grid is in the repo so a reader can recompute under a mix they actually
measured. Older passes predate this and their $/M figures should be treated as unit conversions
with a hidden assumption rather than as findings.

## Evidence classes

A published ceiling and a measured meter are different quantities, and this repo does not rank them
in the same table.

| Class | Means |
|---|---|
| `FIRST-PARTY-COMPUTED` | Every input read from the vendor's own current page, arithmetic done here. The strongest class in the repo. |
| `FIRST-PARTY-PRICE-ONLY` | Price read from the vendor, allowance not published, so no derived figure is offered. |
| `MEASURED` | A meter was ticked and a number observed. Carried in `subscription-measurements.csv` and not ranked against ceilings. |
| `DOCUMENTED` | A vendor published a table; read, not tested. |
| `THIRD-PARTY` | A source outside the vendor, carried with attribution, date and uncertainty. |
| `UNKNOWN` | Not published. Never estimated, never filled from a secondary source. |

## Method in one paragraph

Every claim is traceable to an archived source: `data/fetch-log.json` records the HTTP status, byte
count, latency and SHA-256 of each first-party page at the moment it was read, and the raw bytes
are committed under `sources/`, so any figure in any pass can be recomputed from the evidence in
the repo rather than taken on trust. Subscription economics come from first-party pricing pages and
docs wherever possible, with every unverifiable number labeled UNKNOWN rather than guessed. Prices
in non-USD currencies are normalized at a cited FX rate with the rate date. **The relay and reseller
class was excluded from rankings by category until the 2026-10-06 pass replaced that policy with a
measurement standard**: a relay or reseller may be ranked if its operator publishes a rate card or an
allowance, its reputation is quantified, its delivery ceiling is documented, and its failure modes
are recorded from issue evidence, and every exclusion must name a measured property rather than a
category.

`python3 tools/validate.py --all` gates every pass on eight things a reader cannot check by eye:
CSV field-count agreement (a surplus unquoted comma shifts every later column, and 7 rows across
three files shipped that way in the 2026-09-20 pass while the old validator reported clean);
agreement between a price, a token count and a $/M on the same row; the presence of a source on every
number; agreement between row counts quoted in prose and the CSV they describe; **a token figure's
magnitude against its own column unit** (25.81亿 was read as 25.81 billion when the stored row said
2,581,000,000); **a capability score traceable to a leaderboard row or explicitly marked notFound**;
**a per-model ceiling that says whether it is independent or drawn against a shared pool**; and **a
derived $/M or tokens/month figure that states its traffic mix**. Each check refuses a planted
defect and accepts correct input; the failing-before evidence is in
[docs/reviews-2026-10-02.md](docs/reviews-2026-10-02.md) and
[docs/reviews-2026-10-06.md](docs/reviews-2026-10-06.md).

## Conventions

- Prices in USD unless marked otherwise; "M tokens" = millions of tokens.
- VERIFIED = read directly from the provider's own current page/docs. THIRD-PARTY = reputable
  secondary source. ESTIMATED = derived calculation. UNKNOWN = not published; never invented.
- Repo layout per pass: `YYYY-MM-DD/{README.md, data/, references/, sources/}`.
- Reviews live in `docs/`, one file per pass.

## Tools

| Tool | What it does |
|---|---|
| `tools/validate.py` | The data-integrity gate. `python3 tools/validate.py --all` runs every pass and every check. |
| `tools/fetch-firstparty.py` | Serial fetcher: one URL, one request, one file, one log line. Never retries a failure into a success. |
| `tools/fetch-source.py` | Fetcher with more than one route: `--via jina` adds a text-extraction second source for JS-rendered or blocked pages, `--retries` backs off on 429/5xx only, and every attempt is logged with the route that produced it. Never converts a failure into a success. |
| `tools/fetch-community.py` | Fetches Reddit as a feed and **asserts the query was honoured** rather than assuming it: `search.rss` silently ignores `q=` and returns recency-ordered posts. Exits non-zero when it was ignored. |
| `tools/parse-opencode-go.py` | Structurally parses `<table>` markup out of the OpenCode Go page into a CSV. Re-running it on the archived snapshot reproduces the committed CSV byte for byte. |
| `tools/parse-aa-models.py` | Extracts the model landscape from the leaderboard's React Server Component payload. |
| `tools/parse-aa-scores.py` | Looks specific SKUs up on that board and **records the ones it cannot find**, so an unscored model is distinguishable from a low-scoring one. |
| `tools/derive-yields.py` | Computes a plan's monthly token yield from a ceiling, a price grid and a `--mix`, printing the whole division including the no-cache worst case. Accepts `--ceiling-basis min --pool P --cap C` for pooled plans. |
| `tools/probe-opencode-zen.py` | Live anonymous-access probe. Sends no `Authorization` header of any kind, by construction, so it cannot test an authenticated path and does not claim to. |
