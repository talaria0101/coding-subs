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
| **2026-10-06** | [2026-10-06/README.md](2026-10-06/README.md) | Correction pass: the market's negative result stated as arithmetic rather than as a search gap (**no plan reaches >=10,000M tokens/month for <=$10 on a verified model**; $10 of raw credit buys at most 5,000M on the cheapest qualifying price under a 100%-cache upper bound, and 1,838M at the audited 97% mix), corrections to earlier passes (**the 190x SuperGrok multiplier is retracted by its own source**; OpenCode Go's $60 read as a shared pool, with the vendor-page exhibit demoted to "consistent with, not decisive" on re-reading), the SKUs whose scores were inherited from other models, relays measured against a published four-test standard rather than excluded by category, and twenty integrity checks |

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

`python3 tools/validate.py --all` gates every pass on **twenty checks** a reader cannot check by eye,
registered in the `CHECKS` table in `tools/gate/registry.py`. The ones with a history: CSV field-count
agreement (a surplus unquoted comma shifts every later column, and 7 rows across three files shipped
that way in the 2026-09-13 and 2026-09-20 passes while the old validator reported clean - **two rows
in `2026-09-13/data/providers-database.csv`, one in `2026-09-20/data/agents-universe.csv`, four in
`2026-09-20/data/delta-vs-2026-09-13.csv`**, so the defect spans two passes and the root README's
earlier "across three files" was wrong on both the count and the files); agreement between a price, a
token count and a $/M on the same row, resolved by role rather than by a fixed column list; **a row's
token count being the division the row states it performed**, which is a second quantity on the same
row and is invisible to the first; the presence of a source on every number; **an evidence class
drawn from the table above**; agreement between row counts, cited paths **and the fetch tallies** in
prose and what is on disk; a plan row's model joining to a row in the landscape; a ladder price appearing in the page it
cites, **a price of zero refused rather than matched against any bare digit on the page**; **a money
figure quoted in `references/*.md` appearing in the archived page that entry cites, attributed to the
entry rather than to a line, and a dated correction exempting only the lines that record the
superseded figure**; **a cell holding the kind of value its column name promises**, which is what an
arity-preserving column shift looks like; **a token figure's magnitude against its own column unit,
at both ends of the plausible band** (25.81亿 is 10^8, so 25.81 of them is 2,581,000,000 and not 25.81
billion); **a capability score traceable to a leaderboard row for that exact SKU or explicitly marked
notFound**; **a leaderboard-lookup row checked against the archived payload itself, so the file every
other check treats as the authority cannot assert a SKU or a score the board does not carry**; **a
per-model ceiling that says in its `cap_model` column whether it is independent or
drawn against a shared pool**; **a derived $/M or tokens/month figure that states its traffic mix in a
column**; **every recorded SHA-256 recomputed against the archived bytes, and every archived source
accounted for by a log entry**; **a provenance string forbidden from asserting a dated reading no
fetch log entry records**; and **a document's claim of how many checks this gate runs checked against
the registry**.

Each check refuses a planted defect and accepts correct input; the failing-before evidence is in
[docs/reviews-2026-10-02.md](docs/reviews-2026-10-02.md) and
[docs/reviews-2026-10-06.md](docs/reviews-2026-10-06.md). **Seven of the 2026-10-06 checks were
rewritten on 2026-10-07 after each was shown to exit 0 on the very defect it was written for**, and
three more were added after the same review found checks that verified nothing. Both rounds are
recorded in the review rather than quietly fixed. Every plant the checks are demonstrated against is
generated by `tools/make-plants.py` and run by `bash tests/run-plants.sh`, so a reader can re-run the
refusals as well as read about them.

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
| `tools/make-plants.py` | Generates the 27 plant fixtures each check is demonstrated against, from real repository data with one cell changed, and writes `manifest.json` naming the check each plant must trip. |
| `tests/run-plants.sh` | Runs every plant once and asserts it is caught **by the check it is named for**, then runs each pass and the whole repository showing the acceptance. Exits non-zero if a plant passes, or if one is refused by a check other than its own. |
| `tools/fetch-firstparty.py` | Serial fetcher: one URL, one request, one file, one log line. Never retries a failure into a success. |
| `tools/fetch-source.py` | Fetcher with explicit routes: `--via direct` (default), `jina` (jina only) or `both` (two files); `--user-agent chrome\|curl\|<string>`; `--retries` backs off on 429/5xx only; every attempt logs route, UA and a POSIX relative `saved_as`. Never converts a failure into a success. |
| `tools/merge-fetch-logs.py` | Merges fetch logs, rewriting `saved_as` via `--map OLD=NEW`, re-hashing every file, refusing collisions; `--copy-sources DEST` copies or verifies, `--dry-run` writes nothing. |
| `tools/fetch-community.py` | Fetches Reddit as a feed and **asserts the query was honoured** rather than assuming it: `search.rss` silently ignores `q=` and returns recency-ordered posts. Exits non-zero when it was ignored. |
| `tools/parse-opencode-go.py` | Structurally parses `<table>` markup out of the OpenCode Go page into a CSV. Re-running it on the archived snapshot reproduces the committed CSV byte for byte. |
| `tools/parse-aa-models.py` | Extracts the model landscape from the leaderboard's React Server Component payload. |
| `tools/parse-aa-scores.py` | Looks specific SKUs up on that board and **records the ones it cannot find**, so an unscored model is distinguishable from a low-scoring one. |
| `tools/derive-yields.py` | Computes a plan's monthly token yield from a ceiling, a price grid and a `--mix`, printing the whole division including the no-cache worst case. Accepts `--ceiling-basis min --pool P --cap C` for pooled plans. |
| `tools/probe-opencode-zen.py` | Live anonymous-access probe. Sends no `Authorization` header of any kind, by construction, so it cannot test an authenticated path and does not claim to. |
