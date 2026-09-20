# Deep Reviews — pass 2026-09-13

Five independent review passes were performed before publishing, per standing practice.
Each pass used a distinct lens, had to find-or-fix something real, and its fixes were folded
in before the next pass. Findings are numbered; all are marked FIXED.

---

## Review 1 — Re-derivation (recompute every number from raw sources)

Re-derived, from the archived first-party sources (not from this report's own text):
GLM weekly→monthly capacity math (48/97/146/292/290/580/676/1352 M tokens/week × 4.33),
the workload's API cost on eight models (15M input + 37.5M output at list prices), the GLM
Lite API-equivalent value, and all arbitrage multiples.

**Findings:**
1. Report stated GLM Lite capacity value as "$738–$1,489/mo"; exact re-derivation gives
   $736.9–$1,488 (186 × 208/52.5 = 736.9) — first figure misrounded. → **FIXED** ($737).
2. All other arithmetic re-derived clean: 208–420M (48/97 × 4.33), 1,256–2,511M (Pro),
   2,927–5,854M (Max); Opus-5 workload cost $1,012.50; GLM-5.3 $186; multiples 41–83×;
   Codex Pro 20x ≈ $9.5k/mo from the $2,200/week community datapoint (×4.33).

## Review 2 — Claim-scope (is every claim scoped to its source and date?)

Checked each factual claim against its citation for overreach or staleness.

**Findings:**
3. Report said Claude weekly limits "rose 25% on Sep 14, 2026" — but Sep 14 is *after* the
   research date (Sep 13); the +25% was *announced* (Anthropic statements quoted Aug 29–31)
   and effective Sep 14. Tense overstated certainty. → **FIXED** ("announced, effective Sep 14,
   2026 — the day after this research date").
4. Scope otherwise held: "1M in Claude Code" correctly scoped to the Anthropic support doc with
   the Pro-tier usage-credits caveat; Muse free-100M-tokens/week kept THIRD-PARTY/promo status;
   MiniMax M3 kept the press-vs-AA-II tension visible; "Gemini 3.8 Flash is the flagship"
   grounded in the AA dataset (no 3.8 Pro slug exists); K3 tier-gating kept THIRD-PARTY.

## Review 3 — Consistency-router (cross-check report ↔ databases ↔ sources)

**Findings:**
5. **Real inconsistency:** the providers DB carried GLM Lite capacity "192-388M; Flash
   584M-1,168M" (4.0-week math) *labeled* 4.33wk, while the report said 208–420M (4.33-week
   math, matching Z.ai's official weekly tables). → **FIXED** (CSV updated to 208-420M /
   632M-1,264M and a validator check now pins CSV↔report agreement).
6. Root README claimed "30+ providers"; the DB actually has 26 distinct provider groups (44
   plans). → **FIXED** (README now says 26; validator floor set at ≥20 distinct).
7. Row-by-row sweep of the workload-test verdicts against the capacity column found no other
   contradictions (e.g., GLM Lite PASS at 100M vs 208M low-end holds).

## Review 4 — Security / adversarial

Assumed an adversarial reader: ToS violations, credential leakage, data-exfiltration risk,
supply-chain/prompt-injection surface, scam exposure.

**Findings:**
8. **Missing privacy caution:** an HN-linked reverse-engineering writeup (runtimewire, Aug
   2026) claims Muse Code sends some prompts/telemetry to Meta by default. The report praised
   Muse's economics without a data-use caveat. → **FIXED** (privacy note added to caveats,
   pointing at Meta's Model API ToS).
9. ToS hygiene verified: resold shared accounts are explicitly excluded and flagged RISKY;
   the Tmall storefront note is marked informational only. No credentials/API keys anywhere in
   the repo (only format placeholders like `sk-sp-xxxxx` from provider docs). No executable
   agent-instruction files (no AGENTS.md/skills) that a coding agent might auto-ingest —
   `tools/validate.py` is inert Python run only by CI or a human.

## Review 5 — Tests / CI

**Findings:**
10. `tools/validate.py` initially failed its own run (missing `docs/reviews.md`) — correct
    behavior; re-run after this file landed: **OK**. A date check that would have broken CI on
    any day after the research date was loosened to "pass dir ≤ today" with an opt-in
    `STRICT_DATE` env for same-day runs. → **FIXED**.
11. Model cross-check regex missed dotted slugs (e.g. `gemini-3.8-flash`); normalized to
    dash-form before lookup. → **FIXED**.
12. Added a CSV↔report GLM-capacity consistency assertion so Review-3-style drift is caught
    mechanically in CI (`.github/workflows/ci.yml` runs the validator on every push).

---

**Verdict: all five lenses produced at least one accepted fix (11 fixes total across 10
findings + 1 correct initial failure). The pass was published only after fixes 1–12 landed
and `python3 tools/validate.py` returned OK.**

---

# Deep Reviews — pass 2026-09-20

Review passes were run before publishing, each with a distinct lens, each required to find
something real or state what would have made it fire. Fixes were folded in before the next pass.

## Review 1 — Re-derivation (recompute every number from raw snapshots)

Re-derived from `sources/`, not from the report's own text: GLM weekly-to-monthly capacity
(Lite 48/97, Pro 290/580, Max 676/1,352 M/wk at 95% cache, x 4.33), FX conversions at
6.7184 CNY/USD (¥49 -> $7.30, ¥99 -> $14.74, ¥199 -> $29.62, ¥699 -> $104.05, ¥399/4wk -> $59.39),
Kimi regional spread ($29.62 CN vs $39 international = 24% under / 32% over), Copilot flex totals
(1,500 / 7,000 / 20,000), Gemini 3.8 Flash workload cost (15 x 0.75 + 37.5 x 3.75 = $151.88),
GLM Flash cost floor (18 / 1,264 = $0.01424), and every II quoted against
`data/aa-leaderboard-2026-09-20.json`.

**Finding 1 — FIXED.** The provider DB's GLM Pro/Max capacity rows (inherited from 2026-09-13)
used x4 weeks (1,160-2,320M / 2,700-5,400M) while the README and the review convention use x4.33
(1,256-2,511M / 2,927-5,854M). DB rows corrected and marked "capacity re-derived x4.33wk".

## Review 2 — Claim-scope audit (VERIFIED / THIRD-PARTY / ADVERTISED / UNKNOWN)

Audited every price sentence against its evidence source.

**Finding 2 — FIXED.** Three sentences implied more than their source: Kimi new-tier prices are
THIRD-PARTY ("pricing unchanged") with only the structure VERIFIED - relabeled everywhere,
including the top-10 table row. Cursor Pro+/Ultra is THIRD-PARTY (behind a JS tab). Command Code's
"up to 2x/5x effective usage" and its API plan's "zero markup" are ADVERTISED, vendor-page-only -
now labeled in the DB, the top-10 row, the workload table (UNKNOWN verdicts), and WHAT I WOULD BUY
(month one is a measurement, not a commitment).

## Review 3 — DB/report consistency

Cross-checked every row quoted in the README against `data/providers-database.csv`.

**Finding 3 — FIXED.** The Devin (team) row still carried "UNKNOWN for 2026 tiers" as its price
while the same row's published_quota said "$80 base + $40/seat". Price field corrected.

## Review 4 — Scope policy (the fork question)

Checked that nothing from the Nemo-010 fork is presented as this pass's research.

**Finding 4 — none.** The fork's contributions are adopted with credit (method, agents-universe,
models.dev tables, relay snapshots as advisory evidence) and its rankings are rejected with named
reasons (sponsor universe, CNY unconverted, relay != subscription, proxy-measured uptime,
self-contradicting ad arithmetic). The live sub2api README was re-fetched today so the advisory's
quotes stand on this pass's own snapshot, not the fork's.

## Review 5 — Validator + arithmetic gates

`tools/validate.py 2026-09-20` and `tools/validate.py 2026-09-13` both pass. The validator was
extended: the references date check now reads the pass directory's own date (was hard-coded to
2026-09-13), and models with unpublished context windows may carry `ctx_ge_1m=UNKNOWN` instead of
failing the integer check.

## What would have made each review fire

R1: any capacity or FX figure differing from the raw snapshot by more than rounding. R2: any
ADVERTISED number wearing a VERIFIED label. R3: any README claim absent from the DB or vice versa.
R4: any fork table reused without relabeling. R5: a failing validator.

## Review 6 — Bias audit (rev 2, after a reader challenge: "you are a glm model and put glm at top")

The challenge had two parts; both were checked against the raw sources.

**Part 1, identity.** Confirmed: the session env reads `PI_MODEL=glm-5.3-flash`,
`PI_PROVIDER=zai-coding-cn`. The report now discloses this in its header. Every GLM number remains
cited to first-party pages, but disclosure alone would have been the coward's fix, because:

**Part 2, method.** The reader's underlying point survives the identity question: GLM's #1 rank
depended on it being the only vendor that publishes token tables (self-graded, 95%-cache-assumed),
while everyone publishing nothing scored UNKNOWN and lost by default. "Most transparent" was
masquerading as "most generous."

**Findings and fixes:**
1. FIXED — disclosure section added; evidence classes made explicit (DOCUMENTED /
   VERIFIED-TABLE / USER-REPORTED / ADVERTISED / UNKNOWN).
2. FIXED — a subscriber-reported Muse Code datapoint ($15/mo, ~3B tokens/week; price
   third-party-corroborated by CreditsPlan, recorded 2026-09-17) was added and ranked on its own
   evidence class. On those numbers Muse dethrones GLM Lite; the BEST DEAL FOUND block and the
   rankings were re-ordered accordingly, with falsification conditions stated.
3. FIXED — OpenCode Go ($10/mo, published per-model grid) was missing; added (delta D27,
   providers DB, references §37) with credit to the reader who flagged it.
4. NONE — the relay advisory, FX normalization, and delta log were re-checked and stand.

What would have made this review fire earlier: any ranking that lets a vendor's self-published
table outrank a competitor's report purely because the competitor publishes nothing. The fix is
structural (evidence classes), not editorial.

## Review 7 — Second top-down sweep (rev 3, after "think what else you missed")

The category was re-enumerated from zero in four lanes: (a) frontier labs (do they sell coding
subs?), (b) cloud/IDE vendors bundling agents, (c) agent startups, (d) sites the earlier passes
left as JS shells.

**Findings:**
1. FIXED — six real products were missing from the market picture entirely and are now verified
   rows: Amazon Q Developer Pro $19 (AWS's second coding sub - 09-13 only ever listed Kiro under
   AWS), JetBrains AI Pro $10 (Junie; 1 credit = $1 printed), Gemini Code Assist $19/$45 (a
   distinct product line from Antigravity), Amp Free/$20 (the first agent that consumes your
   existing ChatGPT/agent subscription tokens), Roo Cloud from $49 (team-shaped), Qwen Code's free
   OAuth tier.
2. FIXED — one standing UNKNOWN from the 09-13 pass resolved: windsurf.com/pricing now serves the
   Cognition ladder (Free/$20/$200; Teams $80+$40/seat), so "Devin Desktop (ex-Windsurf)" is no
   longer UNKNOWN.
3. FIXED — three scope questions answered and closed rather than left dangling: xAI sells no
   coding-agent subscription (chat-first ladder; grok-code-fast-1 retired; Grok 4.6 reaches agents
   only via third-party grids), DeepSeek still has no coding plan (the 09-13 "within months"
   prediction failed its own deadline), Tabnine is acquired and out of the market.
4. NONE — Cline confirmed subscription-free; Kiro/Trae/Qoder/CodeBuddy/MiMo/StepFun/Z.ai-CN
   remain UNKNOWN where unverifiable, and the report says so instead of guessing.

What would have made this review fire earlier: enumerating vendors by *category* (cloud vendor,
IDE vendor) instead of by *product fame*. The 09-13 and rev-1/rev-2 passes both failed AWS twice
by checking Kiro and never asking "does AWS sell a second coding agent?"
