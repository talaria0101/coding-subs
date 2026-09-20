# Coding-Subscription Market Pass — 2026-09-20 (re-verification + new entrants)

**Research date: 2026-09-20 (UTC), 06:47-07:30.** This pass re-verifies every first-party
coding-subscription source from the [2026-09-13 pass](../2026-09-13/README.md) seven days later,
logs what changed, adds the new entrants the old pass missed, normalizes every non-USD price to
dollars at a cited FX rate, and quarantines the relay/reseller "sponsor" market into an advisory
instead of a ranking. Databases: [data/providers-database.csv](data/providers-database.csv)
(68 plan rows, 30 provider groups), [data/models-database.csv](data/models-database.csv)
(48 models with a fresh Intelligence-Index column), [data/delta-vs-2026-09-13.csv](data/delta-vs-2026-09-13.csv)
(26 logged changes), [data/relay-market-flags.csv](data/relay-market-flags.csv) (12 red flags),
[data/currency-normalization.csv](data/currency-normalization.csv). Numbered citations:
[references/references.md](references/references.md). Raw snapshots: [sources/](sources/).

Why a same-week pass: the 2026-09-13 report's own freshness warnings had expiry dates inside
seven days (GLM Flash campaign ending Sep 20, Claude limits changing Sep 14, Gemini intro pricing
burning toward Dec 31), and a public fork of this repo (`Nemo-010/coding-subs`) published a
"2026-09-20" pass whose universe was paid sponsor advertisements rather than subscriptions.
This pass supersedes it; see [What was taken from the fork](#what-was-taken-from-the-fork-and-what-was-thrown-back).

---

## Conflict-of-interest disclosure, and what it changed (rev 2)

**This pass was researched by an agent running on `glm-5.3-flash` via a Z.ai coding-plan key**
(session env: `PI_MODEL=glm-5.3-flash`, `PI_PROVIDER=zai-coding-cn`; disclosed after a reader
called the GLM-first ranking biased). That is a real conflict of interest for a report ranking
Z.ai's plan, and the challenge exposed two separate problems:

1. **Identity bias.** Is GLM at the top because the author is GLM? The criteria
   (30% capacity / 25% quality / 15% 1M-context / 10% multimodal / 10% price / 10% multi-model)
   and every GLM number cite first-party pages, not preference - but identity alone is not a
   satisfying answer, because of:
2. **A genuine methodological flaw:** GLM won the capacity column largely because **it was the
   only vendor publishing token tables at all** - and its tables assume 95% cache hits for the top
   of each range. Vendors publishing nothing scored UNKNOWN and lost by default. "Most transparent"
   was masquerading as "most generous."

Changes in this revision:

- **Evidence classes are explicit**: DOCUMENTED (vendor tables, self-graded), VERIFIED-TABLE
  (published per-model grid), USER-REPORTED (subscriber numbers, labeled), ADVERTISED, UNKNOWN.
- **The Muse Code datapoint was added**: a subscriber reports ~3B tokens/week on a $15/mo plan
  (price third-party-corroborated). On those numbers Muse is the best deal in this market by
  roughly an order of magnitude, and it dethrones GLM Lite on any honest reading. See below.
- **OpenCode Go ($10/mo) was added** after a reader correctly flagged it as missed; it competes
  directly with Command Code GOAT.
- A bias-audit review is recorded in [../../docs/reviews.md](../../docs/reviews.md) (Review 6).

---

## BEST DEAL FOUND (concise answer)

Ranked by evidence class. The classes mean: DOCUMENTED = vendor-published tables (self-graded);
VERIFIED-TABLE = published per-model grid read from the vendor's page; USER-REPORTED = subscriber
numbers, labeled as such; ADVERTISED = marketing; UNKNOWN = unpublished, never guessed.

| Field | Value |
|---|---|
| **BEST DEAL FOUND (reported)** | **Meta Muse Code High Usage — $15/month, ~3B tokens/week as reported by a subscriber** (price corroborated by a third-party tracker, first recorded 2026-09-17; usage USER-REPORTED; Meta publishes no quotas) |
| **Why it outranks everything** | ~13B tokens/month on a model rated II 48.09. At Muse Spark 1.3 API list ($1.25/$4.25) that usage is worth **$16,200–$55,200/month** (all-input to all-output bounds) — **1,082–3,680×** the price, the largest subsidy in this market by far |
| **What would falsify it** | launch-window generosity; mix skews to cheap input tokens; throttling after the promo; dashboard "tokens" != model tokens. Treat as the deal to verify first-hand this month, not a guarantee |
| **BEST DEAL (documented)** | **Z.ai GLM Coding Plan Lite — $18/month**: the only vendor publishing token tables (Lite GLM-5.3 @95% cache: **48–97M tokens/week ≈ 208–420M/month**). Now ranked below Muse on the numbers; its earlier #1 was substantially an artifact of being the only vendor with published tables. The Flash campaign's bonus quota ended Sep 20 |
| **BEST DEAL (verified $10 tier)** | **OpenCode Go — $10/month** (rev 2, previously missed): published per-model request/usage grid across 27 open models, up to ~$60/mo of list-value usage; runs in any agent |
| **CHEAPEST ENTRY** | **Command Code Go — $1/month** ($10 credits, up to ~$20 usage with deals, ~15K requests, up to 1M context) — deal multiples ADVERTISED, unmeasured |
| **CHEAPEST FRONTIER QUALITY** | ChatGPT Plus $20 (GPT-5.6 Sol II 46.97) and Claude Pro $20 (1M-context Claude Code) — both re-verified, unchanged |
| **BEST FREE** | Google Antigravity free tier — Gemini 3.8/3.7/3.6 Flash + 3.1 Pro + Claude Sonnet 4.6 & Opus 4.6 (thinking) + gpt-oss-120b, weekly-refreshed quota |
| **CONFIDENCE** | HIGH on first-party prices; MEDIUM on Muse (USER-REPORTED usage, onboarding-only pricing); remember GLM's published ranges assume 95% cache hits — top-of-range figures are best-case, not typical |


The one material *loss* since 2026-09-13: **Claude Code weekly limits dropped ~17% for heavy
users** on Sep 14 — the permanent level is +25% vs the pre-May baseline, but that baseline is
below the 50% promo level that ran May 13–Sep 13 ([ref 8](references/references.md)).

---

## What changed in 7 days (full log in [data/delta-vs-2026-09-13.csv](data/delta-vs-2026-09-13.csv))

**Repriced upward (the "unlimited era" keeps closing):**
- **Trae**: Lite $3 retired, Pro $10 → **$20**, new Pro+ **$60** and Ultra **$200**.
- **Augment**: $20/seat Standard → **$20 flat per team** (up to 50 seats, $20 usage included) —
  cheaper per seat for teams, same price for solo devs with a rebrand (Cosmos).
- **Claude Code weekly limits**: promo level ended Sep 13; permanent level is ~17% below it.

**New ladders published (were UNKNOWN or single-tier):**
- **Kiro** (AWS): Free 50cr / Pro $20 = 1,000cr / Pro+ $40 = 2,000cr / Pro Max $100 = 5,000cr /
  Power $200 = 10,000cr, add-ons $0.04/credit. Token value per credit still unpublished.
- **Devin** (Cognition): first consumer ladder — Free / **Pro $20** / **Max $200**, Teams $80 + $40/seat.
- **Factory Droid**: Pro $20 / Plus $100 (~5x) / Max $200 (~10x).
- **Replit**: new **Pro $100** ($90 annual) above Core $20.
- **Warp**: Build from $20/mo, Max from $200/mo ("pay as you go, starting at" = a floor, not a cap).
- **Zed**: Pro **$10/mo** with $5 of tokens, then API list +10% — the cheapest hosted-model entry
  among editors.

**Restructured:**
- **Kimi (Moonshot)**: tiers renamed (legacy Andante→Vivace become Go/Plus/Pro/…), **weekly quota
  window removed for new members** (5h rolling only), K3 access moves up to Plus+, K3 1M context to
  Pro+; docs say pricing is unchanged. Legacy members keep legacy rules. CN help-center list prices
  for legacy tiers: ¥49/¥99/¥199/¥699 = **$7.30/$14.74/$29.62/$104.05** at today's FX — the same
  Allegretto tier sells for $39 international, so the CN price sits 24% under the international
  price for the identical tier.

**New entrant worth a full look:**
- **Command Code** (`commandcode.ai`) — absent from the 2026-09-13 pass and from both gateway
  repos; found by enumerating the agent category rather than string-searching (method adopted from
  the fork, verified first-party by this pass): Go $1 / GOAT $10 / Pro $20 / Max 10x $100 /
  Max 20x $200 / API plan $15 + zero-markup PAYG / Teams $40. Credits $10/$70/$80/$150/$300,
  per-model allowances on GOAT ($70 GPT-5.6 Sol, $70 GLM-5.2, $70 Tencent Hy3, $70 Qwen 3.8 27B,
  $60 DeepSeek V4 Flash + 29 more), up to 1M context, "up to 2x/5x effective usage" deals on
  MiniMax M3 / MiMo V2.5 (**ADVERTISED, unmeasured**), "+ processing fee" at checkout.

**Unchanged (re-verified today):** Z.ai ($18/$72/$160), MiniMax ($22/$55/$132), OpenAI Codex
($8/$20/$100/$200), Anthropic ($20/$100/$200; Pro annual $17), Google AI Pro $19.99 + Ultra
$99.99/$199.99, Copilot ($10/$39/$100, now with flex-credit totals 1,500/7,000/20,000/mo),
Muse Code (3 tiers; prices still first-party-unpublished, but High Usage is $15/mo per a
third-party tracker + a subscriber report - see the disclosure section), Alibaba Model Studio
Coding Plan Pro $50
(supported-model list actually narrowed to qwen3-coder-next/plus + glm-4.7), Mistral Le Chat Pro
$14.99, Kilo Pass from $19, OpenCode Zen $20 zero-markup top-ups. **Cerebras Code: still sold out.**

**Model landscape (fresh AA leaderboard, [data/aa-leaderboard-2026-09-20.json](data/aa-leaderboard-2026-09-20.json)):**
Qwen3.8 Max is the 7-day mover (II 40.3 → **45.42**, now above GLM-5.3's 44.78); **Step 5 Preview**
enters at 43.73; a new lab's **Inkling** at 24.98. Top-5 stable: Fable 5.1 53.35 · GPT-6 Astra 52.67 ·
Opus 5 50.78 · Muse Spark 1.3 48.09 · GPT-5.6 Sol 46.97.

---

## The re-verified top ten (all prices USD)

Weighting as before: 30% capacity, 25% quality, 15% 1M-context, 10% multimodal, 10% price,
10% multi-model. Full data: [data/providers-database.csv](data/providers-database.csv).

| # | Plan | Price/mo | Best model (II 2026-09-20) | Why it's here | Main limitation |
|---|---|---|---|---|---|
| 1 | **Muse Code High Usage (Meta)** | **$15** | Muse Spark 1.3 (48.09) | **USER-REPORTED ~3B tokens/week (≈13B/mo)** on a II-48 model — 1,082–3,680× API value at list; price corroborated by a tracker ($15, recorded 2026-09-17) | Usage USER-REPORTED, quotas undocumented by Meta; verify first-hand; telemetry caveats from 09-13 stand |
| 2 | **Z.ai GLM Coding Plan Lite** | **$18** | GLM-5.3 (44.78) | The only DOCUMENTED capacity: official 208–420M tokens/mo (@95% cache), 1M ctx, works in Claude Code/OpenCode/Cline/etc | Flash campaign ended today; 95%-cache assumption is best-case; GLM-5.3 below Opus-5 class; vision via MCP only |
| 3 | **OpenCode Go** | **$10** | 27 open models incl. Kimi K3 (43.59), DeepSeek V4.1 Flash | VERIFIED-TABLE: published per-model grid worth up to ~$60/mo at list; works in ANY agent; zero-markup sibling (Zen) for overflow | Open-models only (no Claude/GPT-premium); request-shaped quotas, not tokens |
| 4 | **Command Code GOAT** | **$10** | per-model allowances incl. GPT-5.6 Sol (46.97) | $10 buys $70 of earmarked credits (+ deals to ~$100 usage); ~75K requests; 1M ctx; $1 Go tier is the cheapest paid entry anywhere | Deal multiples ADVERTISED; "+ processing fee"; young vendor, no third-party track record |
| 5 | **ChatGPT Plus (Codex)** | $20 | GPT-5.6 Sol (46.97) | Frontier quality, official message tables (Sol 10–100/5h), flex credits with an explicit rate card | Message-based; weekly caps; GPT-5.5 retires Oct 14 (migration churn) |
| 6 | **Claude Pro** | $20 | Opus 5 (50.78) / Fable 5.1 (53.35) | 1M context in Claude Code (documented); the only true-frontier escape hatch at $20 | Weekly limits now ~17% below the spring promo level; Pro needs usage credits enabled for Opus 1M |
| 7 | **Google AI Pro (+ Antigravity 2.0)** | $19.99 | Gemini 3.8 Flash (40.93) + Claude Sonnet/Opus 4.6 (thinking) | Three labs in one sub; best multimodal agent; free tier exists | Quotas are opaque compute units; 3.8 Flash API intro price doubles Jan 1, 2027 (subscription pricing so far unaffected) |
| 8 | **Claude Max 5x** | $100 | Opus 5 (50.78) / Fable 5.1 (53.35) | The real Opus-5-class experience, 1M verified, priority access | ~5x Pro ESTIMATED ~50M+/mo; 5.5x the price of #1; limits −17% vs promo |
| 9 | **Muse Code Power (Meta)** | onboarding-only | Muse Spark 1.3 (48.09) | 20x tier of the best reported deal; 1M ctx; image+video uploads | Prices still shown only at onboarding; young product |
| 10 | **Z.ai GLM Coding Plan Pro** | $72 | GLM-5.3 (44.78) | Official 1.26–2.51B tokens/mo estimate — heavy-usage king per dollar among DOCUMENTED plans | Same ceiling as #2 |
| 11 | **Kimi Code (new Plus/Pro tiers)** | from ~$19–39 (THIRD-PARTY, "pricing unchanged") | Kimi K3 (43.59, 1M ctx from Pro) | Weekly window GONE for new members — only a 5h rolling window now; genuinely better fairness than legacy | New-tier prices not published outside the JS paywall; CN pricing 24% under international for the same legacy tier |
| 12 | **Kiro Pro / Pro Max** | $20 / $100 | premium models (unspecified credits) | Clear credit ladder with $0.04 add-on pricing — the most honest metered ladder on the West coast | Credit-to-token value unpublished; capacity UNKNOWN |

Dropped from the old top-10: Trae Pro (doubled in price), Copilot Pro+ (breadth at API-parity
credits; Command Code GOAT and OpenCode Go take the multi-model slots at a quarter to half the
price), MiniMax Plus (capacity still unpublished; M3 slipped to II 29.22).

---

## THE HIDDEN DEALS (September refresh)

1. **Command Code API plan, $15/mo zero-markup PAYG** — if the "zero markup" claim survives
   contact, this is the first subscription whose overflow pricing is *better* than every Western
   list card (top-ups roll over, never expire). Verify the invoice math on month one; the claim is
   ADVERTISED.
2. **Antigravity free tier** — unchanged model set (Gemini + Claude thinking + gpt-oss-120b) under
   the Antigravity 2.0 rebrand; still the only $0 route to Claude Opus-class tokens, weekly-refreshed.
3. **Google student promo** — AI Plus free for a year (official subscriptions page, live today);
   stacks with the free Antigravity tier.
4. **Kimi's weekly-window removal** — quiet but real: new members no longer lose 1/7th of their
   month to a weekly window. On a $19–39 tier this is the best fairness-per-dollar change of the week.
5. **Kimi CN vs international pricing** — legacy Allegretto: ¥199 ($29.62) in CN vs $39
   international. If you can legitimately pay CN billing, that is a ~24% discount on the identical
   tier; Tmall storefronts remain the official route (CN account/payment required).
6. **Qwen3.8 Max's jump (II 45.42)** — Alibaba's Coding Plan Pro ($50) supports qwen3-coder-next/plus,
   so its supported-model quality silently improved this week even though its request quota (90K/mo)
   did not. Watch for a Qwen3.8-Max coding plan from Alibaba or a Z.ai-style unlimited tier.
7. **OpenCode Go's Muse Spark contributor lane** — inside the $10 Go grid, Muse Spark 1.3 shows
   45,300 requests/5h at ~$60/mo list value: a Contributor-labeled routing of Meta's model through
   OpenCode's own agreement. Cheapest second route to Spark if the Muse subscription is throttle-prone.
8. **Cerebras restock watch** — still sold out at $50/$200 on GLM-4.7; if it restocks on GLM-5.3 at
   1,000+ tok/s, the speed arbitrage returns.
8. **Zed Pro $10** — $5 of tokens at API list +10% is not an arbitrage, but as a *BYOK-first* editor
   it is the cheapest way to put any subscription key (GLM/Kimi/Command Code) behind a GUI.
9. **Copilot flex credits, documented** — 1,500/7,000/20,000 total monthly credits (base + flex)
   is now official; at 1 credit = $0.01 that confirms Copilot remains API-parity (breadth, not
   discount), useful as a benchmark line, not a deal.
10. **Augment Cosmos flat $20/team** — for a 3–5 person team, $20/mo flat with $20 usage is now the
    cheapest legitimate team plan in the market; solo it is merely average.

---

## THE ARBITRAGE OPPORTUNITIES (updated)

| Route | Subscription | What the same usage costs at API list | Multiple |
|---|---|---|---|
| GLM-5.3 via GLM Coding Plan Lite | $18/mo | $737–$1,489/mo capacity value at GLM API rates | **41–83×** (unchanged, re-derived) |
| GPT-5.6 Sol via Codex Pro 20x | $200/mo | ≈ $9,000–10,000/mo (community measurement, Jul 2026) | ~45× |
| GLM-5.3-Flash quota on Lite | $18/mo | $254–$508/mo at Flash API rates | 14–28× (the campaign's end today removes the temporary 2x multiplier) |
| Claude Opus 4.6 inside Antigravity free | $0 | Anthropic Opus-class API | ∞ until weekly quota |
| Command Code GOAT credits on deal models | $10/mo | $70 earmarked + "up to ~$100 usage with deals" | up to 10× ADVERTISED (unmeasured) |
| Kimi CN legacy pricing | ¥199 ≈ $29.62 | $39 international for the same tier | 1.32× regional arbitrage (official CN billing required) |
| Gemini 3.8 Flash via AI Pro / free Antigravity | $19.99 / $0 | $152/mo for the reference workload at intro API rates; 2× after Dec 31, 2026 | quota-limited |
| Muse Spark 1.3 via Muse Code High Usage (USER-REPORTED) | $15/mo | ~13B reported tokens/mo = $16,238–$55,208 at Spark list (all-input/all-output bounds) | **1,082–3,680×**, launch-window subsidy, unverified |
| Open models via OpenCode Go (VERIFIED-TABLE) | $10/mo | up to ~$60/mo of list-value usage across 27 models | ~6× face |

**Where there is still NO arbitrage:** Copilot (API-parity credits), OpenCode Zen (explicit zero
markup), Cline/Roo (BYOK), Cursor (usage-metered overage), Zed (API +10%), Kilo Pass (provider
rates ± bonus credits). And the entire relay/reseller market — its "0.03×" multiples are not an
arbitrage, they are a different product with a different risk (see the advisory below).

---

## THE RELAY MARKET IS NOT A DEAL — advisory (rankings-excluded)

A public fork of this repo published a "2026-09-20" pass ranking the paid sponsor table of
`Wei-Shaw/sub2api` (and `CLIProxyAPI`) by advertised cheapness. This pass re-verified the live
sponsor table today and **excludes the entire category from every ranking**. The short version:

- **It is paid placement, not a market.** The README invites sponsors by mail; every sponsor link
  carries an affiliate code (`?aff=SUB2API`). Inclusion is an advertisement ([ref 33]).
- **The platform itself warns the mechanism violates upstream ToS** ("may violate the terms of
  service of Anthropic and other upstream providers") while the same README's sponsors promise
  "zero risk of account suspension" — the two sentences cannot both be true ([flags R01, R02]).
- **The supporting infrastructure sells ToS-evasion**: the sponsor table includes residential-proxy
  and anti-detect vendors marketing "reduces the probability of association-based risk control"
  ([R03]).
- **The ads fail their own arithmetic**: "0.16× … roughly 2.2% of official" (16% ≠ 2.2%), "0.03×,
  just 0.35% of official" (3% ≠ 0.35%) ([R04, R05]). An offer that cannot multiply is not evidence
  of cheapness.
- **The cheap pools degrade by design**: quota resale of consumer subscriptions is exactly what the
  platform's own tracker documents breaking ("降智"/intelligence-degradation issues; a sponsor's own
  docs calling its cheapest pool "unstable") ([R09, R11]).
- **Nothing in it is independently measurable**: even the fork's "reachability" numbers were taken
  through a third-party reverse proxy ([R12]); no model-identity, cache-behavior, or uptime
  measurement exists for any of it.
- **Currency games**: CNY list prices (e.g. ¥399/4-weeks "with $440 credit") are meaningless
  without the unpublished internal spend rate; the honest USD equivalents are in
  [data/currency-normalization.csv](data/currency-normalization.csv) and they are not cheap once
  the credit-spend assumption is exposed as unverifiable.

Full register with quotes: [data/relay-market-flags.csv](data/relay-market-flags.csv). If an offer
mentions Claude Code/Codex "pools", "0.0x×" multiples, or account resale — treat it as R01–R12 and
walk away. Resold shared accounts violate provider ToS and can die with your code history inside them.

### What was taken from the fork, and what was thrown back

**Kept (genuinely valuable, with credit in [references](references/references.md) §32, §34, §36):**
1. The **category-enumeration method** (enumerate every coding agent, then check each — a bare
   string search misses products like Command Code and false-positives on the word "continue").
2. The **`agents-universe.csv`** enumeration (30 agents, 18 absent from all prior sources) — carried
   into `data/` with two new rows added by this pass.
3. The **models.dev registry cost tables** (`modelsdev-providers.csv`, `cheapest-per-model.csv`),
   re-based on a fresh registry pull today (222 providers / 7,869 models).
4. **Reusable tooling patterns** (batch first-party fetchers, snapshot layout), re-implemented in
   [tools/fetch-firstparty.py](../tools/fetch-firstparty.py) without the reverse-proxy dependency.
5. Its relay-market snapshots, **as evidence for the advisory above** — the one thing that pass
   documented well.

**Thrown back:** ranking sponsor advertisements as if they were a market; leaving CNY prices
unconverted; treating API relays as if they were coding subscriptions; reachability numbers
measured through someone else's proxy; and "BEST DEAL" verdicts built on copy whose own
arithmetic fails.

---

## Workload test (52.5M tokens/month = 15M in + 37.5M out)

Verdicts per the five levels; "capacity" = published allowance, never a relay's promise.

| Plan | 10M | 25M | 50M | 52.5M | 100M | Basis |
|---|---|---|---|---|---|---|
| GLM Coding Plan Lite ($18) | PASS | PASS | PASS | **PASS** | PASS | official 208–420M/mo (GLM-5.3 @95%) |
| GLM Coding Plan Pro ($72) | PASS | PASS | PASS | **PASS** | PASS | official 1.26–2.51B/mo |
| Claude Pro ($20) | PARTIAL | FAIL | FAIL | **FAIL** | FAIL | ≈10M/mo practical (client benchmark, ESTIMATED) |
| Claude Max 5x ($100) | PASS | PARTIAL | PARTIAL | **PARTIAL** | FAIL | ≈5x Pro; now on the post-Sep-14 (−17% vs promo) limits |
| Claude Max 20x ($200) | PASS | PASS | PASS | **PASS** | PARTIAL | ≈20x Pro, ESTIMATED |
| Codex Plus ($20) | PASS | PARTIAL | PARTIAL | **PARTIAL** | PARTIAL | message caps + weekly limits |
| Codex Pro 20x ($200) | PASS | PASS | PASS | **PASS** | PASS | ≈$9–10k/mo API-equivalent (community) |
| **Muse Code High Usage ($15)** | PASS | PASS | PASS | **PASS** | PASS | USER-REPORTED ~3B tokens/week (≈13B/mo); Meta publishes no tables — verify first-hand |
| OpenCode Go ($10) | PASS | PASS | PARTIAL | **PARTIAL** | FAIL | VERIFIED-TABLE caps ≈$60/mo list value; the 52.5M mix fits on cheap open models (DeepSeek V4.1 Flash ≈ $49.5) but not K3 |
| Command Code Go / GOAT ($1/$10) | UNKNOWN | UNKNOWN | UNKNOWN | **UNKNOWN** | UNKNOWN | credit-denominated; "~15K/~75K requests" is request-shaped, not token-shaped |
| Command Code Max 20x ($200) | UNKNOWN | UNKNOWN | UNKNOWN | **UNKNOWN** | PARTIAL (credit math suggests yes) | $300 credits ≈ $600 usage with deals, ADVERTISED |
| Google AI Pro ($19.99) | UNKNOWN | UNKNOWN | UNKNOWN | **UNKNOWN** | UNKNOWN | compute units unpublished |
| Antigravity free ($0) | PARTIAL | FAIL | FAIL | **FAIL** | FAIL | "meaningful quota, refreshed weekly" |
| Muse Code High (~$50) | PASS | PARTIAL | UNKNOWN | **UNKNOWN** | UNKNOWN | prompt caps; onboarding-only pricing |
| Kimi new Plus/Pro (~$19–39) | UNKNOWN | UNKNOWN | UNKNOWN | **UNKNOWN** | UNKNOWN | quotas unpublished post-restructure |
| Kiro Pro ($20 = 1,000cr) | UNKNOWN | UNKNOWN | FAIL | **FAIL** | FAIL | credit-to-token unpublished; at the $0.04 add-on rate 1,000cr ≈ $40 of usage at list |
| Devin Pro ($20) | UNKNOWN | UNKNOWN | UNKNOWN | **UNKNOWN** | UNKNOWN | quota unpublished |
| Trae Pro ($20) | PARTIAL | FAIL | FAIL | **FAIL** | FAIL | $20 usage value |
| Factory Droid Pro ($20) | UNKNOWN | UNKNOWN | UNKNOWN | **UNKNOWN** | UNKNOWN | rolling limits unpublished |
| Replit Core ($20) | PARTIAL | FAIL | FAIL | **FAIL** | FAIL | $20 model credit + effort pricing |
| Copilot Pro+ ($39) | PASS | FAIL | FAIL | **FAIL** | FAIL | 7,000 credits ≈ $70 of tokens at API parity |
| Kilo Pass Starter ($19) | PASS | PARTIAL | FAIL | **FAIL** | FAIL | $26.60 credits at provider rates |
| Cerebras Max ($200) | — | — | — | **N/A** | — | still sold out |
| *Any relay/reseller offer* | — | — | — | **EXCLUDED** | — | ToS-violating quota resale; see advisory |

---

## 1M-context deep dive (finalists, re-verified)

| Finalist | Model ctx | Agent ctx | 1M actually usable? | Changed this week? |
|---|---|---|---|---|
| GLM Coding Plan (GLM-5.3) | 1M | via Claude Code/OpenCode/etc (harness-dependent) | YES | no |
| Claude Pro/Max (Opus 5 / Fable 5.1) | 1M | Claude Code 1M documented (official, [ref 7]) | **YES (best-documented)** | limits reshuffled Sep 14, context unchanged |
| Codex Plus/Pro (GPT-5.6 Sol) | 1M (AA) | undocumented harness cap | UNKNOWN | no |
| Gemini 3.8 Flash (Antigravity 2.0) | 1M | undocumented | UNKNOWN (likely) | UI rebrand only |
| Muse Code (Spark 1.3) | 1M | undocumented | UNKNOWN | no |
| Kimi K3 (new Pro tier and up) | 1,048,576 | vendor-documented for Kimi Code | YES, now gated at **Pro+** (was Allegretto+) | **threshold moved** |
| Command Code | "up to 1M" (plan table) | vendor page | CLAIMED (ADVERTISED) | new this week |

## Multimodal deep dive (can the agent actually send it?)

| Plan | Image in | PDF in | Video in | Audio in | Note |
|---|---|---|---|---|---|
| Claude Pro/Max | YES | YES (files) | no | no | unchanged |
| GLM Coding Plan | via Flash / Vision MCP | via reader MCP | no | no | unchanged |
| Codex (GPT-5.6) | YES | via tools | no | no | unchanged |
| Antigravity / AI Pro | YES | YES | **YES** (Gemini 3.8) | **YES** | unchanged; still the only video+audio in-agent |
| Muse Code | YES | via tools | YES | voice mode | unchanged |
| Kimi K3 tiers | YES (native vision) | YES | K2.7-class video | no | unchanged |
| Command Code | UNKNOWN (per-model flags not published) | UNKNOWN | UNKNOWN | UNKNOWN | new vendor; UNKNOWN, not assumed |

---

## Rankings

**Weighted (30/25/15/10/10/10):**
1. **Best reported deal:** **Muse Code High Usage $15** (USER-REPORTED ~3B tokens/week) — verify
   first-hand this month; if it holds even half, nothing else in the market is close.
2. **Best documented deal:** **GLM Coding Plan Lite $18** — the only published token tables, best-case
   at the top of each range. It is no longer "best value overall" on the evidence; it is "best
   guaranteed-capacity that a vendor will put in writing."
3. **Best verified $10 tier:** **OpenCode Go** (published grid, any agent, 27 open models).
4. **Cheapest viable:** Antigravity free ($0); cheapest paid entry: **Command Code Go $1**
   (deal multiples ADVERTISED until measured).
5. **Best at $20:** Claude Pro (quality ceiling + documented 1M) and ChatGPT Plus (frontier Sol);
   pick by harness preference.
6. **Best heavy-usage (documented):** GLM Pro $72 (1.26–2.51B tokens/mo official estimate);
   runner-up Codex Pro 20x $200.
7. **Best multi-model:** OpenCode Go and Command Code GOAT ($10, published/advertised grids across
   5+ labs) replace Copilot Pro+ ($39 of API-parity credits); free pick remains Antigravity.
8. **Best 1M-context:** Claude Max (documented in-agent); budget route GLM Lite via third-party harnesses.
9. **Best team plan:** Augment Cosmos $20 flat (up to 50 seats) — new leader at that price point.
10. **Best obscure/niche:** Step 5 Preview's arrival (II 43.73) with no Western plan yet; Qoder and
    CodeBuddy remain UNKNOWN and unranked for another week; Xiaomi MiMo unchanged.
11. **Best regional arbitrage:** Kimi CN legacy pricing (24% under international for the same tier).
12. **Maximum tokens/$ (reported):** Muse Code High Usage at ≈**$0.0012/M tokens** effective (13B tokens for $15).
    Maximum tokens/$ (documented): GLM Lite on GLM-5.3-Flash ≈ $0.014/M at the low end (standard
    rate; the campaign's extra multiplier is gone as of today).

**Frontier quality per dollar (quality-only):** 1. GLM Lite (TB-v4 0.419 at $18) · 2. ChatGPT Plus
(Sol 46.97 at $20) · 3. Command Code GOAT (Sol allowance at $10, unproven) · 4. Muse Code
(Spark 1.3 48.09) · 5. Claude Pro (Opus 5) · 6. Alibaba Coding Plan Pro (Qwen3.8-Max-class models
at $50) · 7. Kimi Pro · 8. Google AI Pro · 9. Claude Max 5x · 10. Copilot Max.

---

## WHAT I WOULD BUY

1. **First buy of the month: Muse Code High Usage $15 — and measure it.** A subscriber reports
   ~3B tokens/week; a tracker corroborates the $15 price. If your dashboard shows even 10% of that,
   it is the best deal in this market. Meta publishes nothing, so your own first month is the
   verification pass. (Pair with OpenCode Go's Spark contributor lane as a backup route to Spark.)
2. **Documented workhorse: GLM Coding Plan Lite ($18) + Claude Pro ($20).** GLM carries the bulk
   with ~4× headroom over a 52.5M/mo workload; Claude Pro remains the verified-1M true-frontier
   escape hatch. Total $38/mo.
3. **$10 experiment slot: OpenCode Go and/or Command Code GOAT.** Go's grid is published and
   works in any agent; GOAT's allowances are bigger on paper but ADVERTISED. Treat month one of
   either as a measurement, not a commitment.
4. **If you were riding the Claude promo levels:** re-run `/usage` against your August numbers
   before renewing Max — the Sep 14 settlement is ~17% below what heavy users had. GLM Pro ($72)
   is the capacity backfill; Codex Pro 20x is the frontier backfill.
5. **Do not buy:** anything from the relay/reseller sponsor tables, however many decimal places
   their "0.03×" has. See the advisory.

---

## Method & caveats

- **Universe:** first-party coding-agent subscriptions only (labs and agent vendors selling their
  own plans). API relays, sponsor marketplaces and account resellers are excluded from rankings by
  policy and documented in the advisory instead.
- **Verification:** every price was read from a first-party page snapshotted 2026-09-20
  (`sources/`); nothing was taken from the fork's tables except where explicitly credited as
  THIRD-PARTY corroboration. Every unverifiable number is labeled UNKNOWN, never guessed.
- **Currency:** prices normalized to USD at 1 USD = 6.7184 CNY (open.er-api.com, 2026-09-20T00:02Z,
  [ref 31]); conversions are ESTIMATED and listed in
  [data/currency-normalization.csv](data/currency-normalization.csv).
- **Model numbers:** Intelligence Index refreshed 2026-09-20 from AA's embedded leaderboard
  (`aa_ii_asof` column); Terminal-Bench, context and API prices carried from the 2026-09-13
  snapshot where the source does not republish them weekly. Effort variants normalized as before.
- **Carried-forward rows:** plans not re-fetched this week are marked `UNCHANGED, not re-verified`
  in the database (Devin Desktop, Abacus, Tmall, CodeBuddy, iFlow status rows).
- **Known gaps:** Muse Code tier prices/quotas remain first-party-unpublished (High Usage $15 is
  THIRD-PARTY-corroborated; the ~3B tokens/week figure is a single-subscriber report and needs
  first-hand verification); Kimi's new-tier USD prices sit behind a client-rendered paywall
  (structure VERIFIED, price THIRD-PARTY); Cursor Pro+/Ultra behind a JS tab; Qoder and CodeBuddy
  still JS-rendered shells; Command Code's deal multiples and Kimi/Kiro/Devin/Droid
  credit-to-token values are unpublished; Google's quotas remain opaque compute units. The AA
  leaderboard exposes only II for the top 20 — deeper model fields are week-old by design and
  labeled.
- **Bias statement:** the researching agent ran on a Z.ai GLM plan (see the disclosure section).
  The GLM rows are cited to first-party pages like every other row, but readers should weight the
  USER-REPORTED and VERIFIED-TABLE classes — which rank above GLM in this revision — accordingly,
  and re-run the measurements themselves where a decision matters.
- **Freshness half-life:** GLM Flash campaign ended TODAY; GPT-5.5 retires Oct 14; Gemini 3.8 Flash
  API intro pricing doubles Jan 1, 2027; Kimi legacy rules persist only while legacy subscriptions
  renew. Re-verify anything you buy.

## Provenance

| Source | Date reached | Depth |
|---|---|---|
| 20 first-party pricing/docs pages + 2 support pages + AA leaderboard + models.dev + FX API | 2026-09-20 06:47–07:30 UTC | full-page snapshots in `sources/` |
| Wei-Shaw/sub2api README (live) | `fbb9006adef8`, pushed 2026-09-20T06:57Z | sponsor table + ToS warning quoted |
| Nemo-010/coding-subs fork pass 2026-09-20 | commit `036c319` | method + 3 data files adopted with credit; rankings rejected |
| OpenCode Go product page | 2026-09-20 | $10/mo, 27-model grid snapshotted (`sources/opencode-go.html`) |
| CreditsPlan — Muse Code High Usage | first recorded 2026-09-17, fetched 2026-09-20 | $15/mo price corroboration (`sources/thirdparty-creditsplan-muse-high.html`) |
| Subscriber report (chat) | 2026-09-20 | ~3B tokens/week on Muse Code at $15/mo — USER-REPORTED, gated the re-ranking |
| This repo's 2026-09-13 pass | `8a22993` | 44 provider rows re-verified/updated row-by-row; delta in `data/delta-vs-2026-09-13.csv` |
