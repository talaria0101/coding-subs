# coding-subs

Market research on the **cheapest legitimate ways to get large amounts of frontier-level
coding-agent usage by subscription** — model landscape, provider arbitrage, published quotas,
1M-context verification, and heavy-usage economics.

## Research passes

| Date | Report | Scope |
|---|---|---|
| **2026-09-13** | [2026-09-13/README.md](2026-09-13/README.md) | Full pass: 45-model landscape (AA snapshot), 44 access plans across 26 provider groups, workload tests, rankings |
| **2026-09-20** | [2026-09-20/README.md](2026-09-20/README.md) | Re-verification + delta pass: all first-party sources re-fetched, 26 logged changes (Trae repriced upward, Kimi tiers restructured with the weekly window removed, Claude Code limits settled ~17% below the promo level, new Command Code / Devin / Kiro / Factory / Warp / Zed / Replit ladders), every non-USD price normalized at a cited FX rate, and the relay/sponsor "0.03x" market quarantined into a red-flag advisory instead of a ranking |

Each pass directory contains the report (`README.md`), the underlying databases (`data/`),
numbered citations with access dates (`references/`), and raw snapshots of primary sources
(`sources/`).

## Method in one paragraph

Model quality comes from an Artificial Analysis dataset snapshot (Intelligence Index,
Terminal-Bench v4.0, context windows, API prices, modalities). Subscription economics come from
first-party pricing pages and docs wherever possible — fetched and archived in `sources/` on the
research date — with every unverifiable number labeled ESTIMATED or UNKNOWN rather than guessed.
The subscription universe is **first-party coding-agent plans only**: API relays, sponsor
marketplaces and account resellers are excluded from rankings by policy (see the 2026-09-20
advisory) because their discounts are ToS-violating quota resale and their pricing is
advertisement, not a published rate card. Prices in non-USD currencies are normalized at a cited
FX rate with the rate date. Each pass undergoes independent reviews (recorded in
[docs/reviews.md](docs/reviews.md)) before being committed.

## Conventions

- Prices in USD unless marked otherwise; "M tokens" = millions of tokens.
- VERIFIED = read directly from the provider's own current page/docs. THIRD-PARTY = reputable
  secondary source. ESTIMATED = derived calculation. UNKNOWN = not published; never invented.
- Repo layout per pass: `YYYY-MM-DD/{README.md, data/, references/, sources/}`.
