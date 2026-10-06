# References — 2026-10-06

Every figure in this pass resolves to one of these. Access dates are UTC. Archived bytes are under
[../sources/](../sources/) with SHA-256 and byte count in [../data/fetch-log.json](../data/fetch-log.json).

## First-party vendor pages

**[R1] OpenCode — Go plan docs** — <https://opencode.ai/docs/go.md> — accessed 2026-10-06 —
HTTP 200, 39,692 B, `sha256:e62561c5c6fb7685fafc8bddc9634bdab3aa37c59944a56da83d103d047f7489`
— archived as [../sources/opencode-go.md](../sources/opencode-go.md). The two sentences this pass
turns on:

> "Usage limits are defined as monthly dollar amounts. The table below shows the monthly limit for
> each plan and the token costs for each model."

> "Each model has the following usage limits: 5-hour — 20% of the monthly limit; weekly — 50%; and
> monthly — 100%."

> "Each model's monthly limit below determines how its usage counts toward those allowances."

The third sentence is the whole dispute. "determines how its usage **counts toward those
allowances**" is compatible with a per-model budget and with a shared pool the per-model figure
bounds, and the page does not say which. The per-model grid: DeepSeek V4.1 Flash (Off-Peak)
$0.15/$0.60/$0.003 at a $60 limit; Muse Spark 1.3 Contributor $0.10/$0.20/$0.002 at $60; MiMo-V2.6-Pro
$0.435/$0.87/$0.003625 at **$15**; Grok 4.7 (≤200K) $2.00/$6.00/$0.50 at $15. Go Plus: same prices,
ceilings at $120/$60/$180. Also the privacy table's footnote:

> "Muse Spark 1.3 Contributor: Heavily discounted token pricing in exchange for permission to use
> your prompts and completions to train future Meta models. Availability is limited to regions
> permitted by Meta's Geographic Use Policy."

The page also lists **only** Contributor tiers of Muse Spark. There is no base `Muse Spark 1.3` row
on Go, so the plan's cheapest lane is a SKU the leaderboard does not carry at all.

**[R2] Artificial Analysis — models leaderboard** — <https://artificialanalysis.ai/models> —
accessed 2026-10-06 — HTTP 200, 1,368,828 B — archived as
[../sources/aa-models.html](../sources/aa-models.html). 24 models recovered from the flight payload.
`muse-spark-1-3` scores 48.0923; `deepseek-v4-1-flash` 39.4562; `glm-5-3-flash` 41.8075;
`mimo-v2-6-pro` 46.3242; `grok-4-7` 46.4466; `kimi-k3` 43.5938; `gpt-6-luna` 38.1245. **No row
exists for `muse-spark-1-3-contributor` or `mimo-v2-6-flash`.** Reproduced by
`tools/parse-aa-scores.py`; the per-SKU verdicts are in [../data/aa-lookup.csv](../data/aa-lookup.csv).

**[R3] Z.ai — GLM Coding Plan overview** — <https://docs.z.ai/devpack/overview.md> — accessed
2026-10-06 — HTTP 200, 8,315 B — archived as [../sources/zai-overview.md](../sources/zai-overview.md).
Credit formula and per-model multipliers, and a from-Sep-25-to-Oct-7 all-day off-peak window.

**[R4] Z.ai — Team Plan** — <https://docs.z.ai/devpack/teamplan.md> — accessed 2026-10-06 — HTTP
200, 10,353 B — archived as [../sources/zai-teamplan.md](../sources/zai-teamplan.md). Standard seat
15,000 credits/5h and 66,000/week; premium 35,000 and 155,000. **The seat price is not published.**

**[R5] DeepSeek — API pricing** — <https://api-docs.deepseek.com/quick_start/pricing> — accessed
2026-10-06 — HTTP 200, 23,982 B — archived as
[../sources/deepseek-pricing.html](../sources/deepseek-pricing.html). For DeepSeek-V4.1-Flash, read
out of the table: off-peak $0.007 cache hit / $0.22 input miss / $0.66 output; peak $0.014 / $0.44
/ $1.32. This is the official list price and it is the denominator the relay ratio in §7 uses.

**[R6] Command Code — GOAT plan** — <https://commandcode.ai/docs/plans/goat> — accessed 2026-10-06 —
HTTP 200, 768,429 B — archived as [../sources/commandcode-goat.html](../sources/commandcode-goat.html).

> "The GOAT plan includes the following usage limits: 5-hour limit - $14 of usage Weekly limit -
> $35 of usage Monthly limit - $70 of usage"

and a DeepSeek V4.1 Flash row at $0.15 / $0.60 / $0.003 with a $60 per-model figure. **The page
states no over-quota billing behaviour.** This pass therefore publishes no claim about whether
over-quota requests are declined or billed, because the sentence that would support it is not on the
archived page.

**[R7] xAI — Grok 4.7 model page** — <https://docs.x.ai/developers/models/grok-4.7> — accessed
2026-10-06 — HTTP 200, 376,272 B — archived as [../sources/xai-grok47.html](../sources/xai-grok47.html).
Grok 4.7 at $2.00 input / $0.50 cached / $6.00 output per 1M. The denominator used to convert a
dollar multiplier into a token count.

**[R8] Fenno AI — public rate card** — <https://api.fenno.ai/api/v1/models> — accessed 2026-10-06 —
HTTP 200, 11,905 B — archived as [../sources/fenno-models.json](../sources/fenno-models.json).
18 models. `deepseek-v4-1-flash`: `input_price` 8e-07, `output_price` 3.2e-06, `cache_read_price`
1.6e-08 per token, i.e. $0.80 / $3.20 / $0.016 per 1M. Every model's `availability` block reads
`"status": "unknown", "request_count": 0, "data_status": "pending"`.

## Issue-tracker evidence

**[R9] `anomalyco/opencode#52962`** — "go: single account-wide usage pool contradicts documented
per-model limits" — opened 2026-10-03, closed. <https://github.com/anomalyco/opencode/issues/52962>

> "After exhausting the Kimi K3 allowance, every other paid model — **including models with zero
> recorded usage** — returns `Go usage limit exceeded`. Total paid spend at that point was **$4.38**."

> "Issue the same request against `deepseek-v4.1-flash` — which has consumed **$0.29 of its
> documented $60 monthly limit (0.49%)**."

**[R10] `anomalyco/opencode#49186`** — "OpenCode Go: Kimi K3 per-model limit appeared separate but
consumed shared monthly quota" — opened 2026-09-15, open.
<https://github.com/anomalyco/opencode/issues/49186>

> "I used Kimi K3 believing its displayed usage allowance was separate from the other Go models. I
> later realized that the usage was actually deducted from the same shared Go monthly quota, which
> caused approximately 20% of my monthly allowance to be consumed unexpectedly."

**[R11] `anomalyco/opencode#47547`** — "Go subscription blocked — Monthly Usage shows 100% via sum
of per-model percentages, not actual dollars vs $60 limit" — opened 2026-09-06, open.
<https://github.com/anomalyco/opencode/issues/47547>

> "Total actual spend: $22.18 out of the $60 monthly limit = ~37%."

> "The aggregate "100%" appears to be calculated by summing the per-model percentages (47.8 + 34.7 +
> 17.5 = exactly 100.0%) rather than comparing total dollar usage against the $60 monthly limit."

**[R12] `anomalyco/opencode#46365`** — "[Go] Monthly usage shows 100% at ~$24.5, far below
documented $60 limit" — opened 2026-08-31, open.
<https://github.com/anomalyco/opencode/issues/46365>

> "According to the official documentation at https://opencode.ai/docs/go/#usage-limits: **Monthly
> limit — $60 of usage** … shows **Monthly Usage: 100%** while the sum of all model usages is only
> about **$24.53**."

**[R13] `anomalyco/opencode#53071`** — statutory-holiday off-peak not honoured — opened 2026-10-04.

> "During this National Day holiday, when I actually used DeepSeek V4.1 Flash, I found that daytime
> hours (e.g., Beijing time 10:00-12:00, 14:00-18:00) were still billed at peak rates, rather than
> the statutory holiday off-peak rate."

## Community meters

**[R14] r/opencode post `1wy907r`** — "Anybody having issues with the monthly spend cap?" —
2026-10-05. Retrieved in the archived feed
[../sources/reddit-r-opencode-search.xml](../sources/reddit-r-opencode-search.xml).

> "I seem to hit my monthly limit on 20$, when ive only used my sub on glm, deepseek and mimo."

**[R15] r/opencode post `1wy6vby`** — "Opencode go monthly limit calculations doesn't make sense" —
2026-10-05. Same feed.

> "deepseek v4.1 flash supposed to have 60$ limit, but according to this 7.56$ usage = 27% with these
> calculations i get about 28$ worth of usage per month"

## The retracted multiplier

**[R16] `phuryn/experiments`, commit `441931da3`** — 2026-10-03 —
<https://github.com/phuryn/experiments/commit/441931da3>

> "subscription-multipliers: SuperGrok on a clean account (no X linked) = 18.0x; X-linked account
> reported as SuperGrok + X Premium+ ($70) = 80x (186x vs SuperGrok price alone)"

**[R17] `phuryn/experiments`, `subscription-multipliers/01-supergrok/README.md`** — current text,
read 2026-10-06.

> "**Read with [07](../07-supergrok-no-x/).** The same plan on a fresh account with no X account
> linked measured **18.0×**. This account got ~10× that allowance. Priced at the $70 it pays for
> SuperGrok and X Premium+ together, it is **80× ± 4**; against the SuperGrok price alone, 186× ± 10."

**[R18] `phuryn/experiments`, `subscription-multipliers/07-supergrok-no-x/README.md`** — the clean
account. 1,432 calls, $125.57 to the first 100% reading, 86% of prompt tokens cached; "reported:
17.95x +/- 0.32".

## The gateway stack, and its failure modes

**[R19] `Wei-Shaw/sub2api`** — LGPL-3.0, 43,349 stars, repository created 2025-12-18 — read at commit
`b8dece9` (VERSION 0.2.13). Enforcement in `backend/internal/service/user_subscription.go`:

```go
func (s *UserSubscription) CheckMonthlyLimit(group *Group, additionalCost float64) bool {
	if !group.HasMonthlyLimit() { return true }
	return s.MonthlyUsageUSD+additionalCost <= *group.MonthlyLimitUSD
}
```

called from `CheckUsageLimits` in `subscription_service.go`, which returns `ErrMonthlyLimitExceeded`
and runs as a middleware pre-check. So a subscriber's share is an operator-chosen dollar allowance
enforced before the request, not a computed fraction of a seat.

**Failure modes, all from its own tracker:**

- *Quota shrinkage under pooling* — **#5692** (2026-08-16, 24 comments) "GPT PROX20 缩水额度问题还是存在":
  a Pro 20x account's usable weekly quota shrinks, one account from 85% to 98% consumed. **#5786**
  (2026-08-18) "[调查/RFC] Codex Pro 账号额度缩水": accounts normal on official Codex "接入 Sub2API 后
  … 账号出现明显的额度缩水或 usage limit reached；将同一账号的模式切回 off 后，额度表现又恢复正常".
- *Ban risk* — **#1141**, **#3624** (the TLS-fingerprint template is gated to Anthropic OAuth/SetupToken
  only, `account.go:1695`, so OpenAI OAuth main requests go over a plain Go transport), **#3896**,
  **#6134**, **#6180**, **#6755**, **#6892**.
- *Silent substitution and degradation* — **#7503** (2026-09-22) attributes intelligence degradation to
  the gateway's TLS fingerprint differing from the real client's.
- *Availability storms* — **#6739** (2026-09-07, 49 comments) "Our servers are currently overloaded"
  from a pool running under 3 concurrent per account; **#593**; storm threads #6967, #6794, #5973,
  #6998; **#6947** shows 5h=0% and 7d=18% with repeated 30-minute cooldowns, so window usage is not
  the binding constraint.

Repo counters read 2026-10-06: `open_issues_count` 3,570, of which 2,625 are issues and 945 are pull
requests.

## The shared-pool decision, from an independent instrument

**[R20] `FeiZhuLulu/real-api-pricing`** — MIT. Its `data/adopted.csv` carries a decision note on every
OpenCode Go row:

> `min(共享月池$60, 模型Usage $60)` … `同套餐各模型额度不可相加`

("min(shared monthly pool $60, model Usage $60) … per-model allowances within one plan are not
additive"). Its `data/conventions.json` supplies the traffic mix this pass uses, `standardTokenMix`:
97% cache / 2.5% input / 0.5% output, revised 2026-09-23 after a 14-sample audit, with the note that
it is a comparison baseline and not any platform's observed workload.

**What is taken from it, and what is not.** Its Claude Max rows read Claude Max 5x at $100 / 19,625M
tokens and Claude Max 20x at $200 / 39,250M tokens, so both price at exactly $0.0050955414 per Mtok.
That identity is the arithmetic proof that **splitting a seat N ways creates no arbitrage**:
`(P/N)/(Q/N) = P/Q`, and doubling both price and allowance leaves the per-token rate unchanged. The
identity is the finding, and it is reproducible from two published prices alone.

The *token counts* behind it are not carried. The same repository records Claude Max 20x as a 45.3x
measured dollar multiplier, which at $200 is $9,060 of API value; $9,060 buying 39,250M tokens
implies $0.2308 per Mtok, which is **45x** the $0.0050955 its own token column implies. Two rows of
one source do not reconcile, and a 10B figure derived from either would inherit that. So this pass
publishes the identity, carries Claude Max's token yield as UNKNOWN, and does not carry the
"$50.96 for 10B" figure that rests on it.

## What was not reached

Recorded because an unreached source and an empty result are different claims.

| Source | Outcome on 2026-10-06 |
|---|---|
| Reddit HTML pages | 403 to a default User-Agent; 200 with a browser-like User-Agent. RSS only, and `search.rss` ignores its query (see [references/method-notes.md](method-notes.md)). |
| Command Code over-quota terms | Not published on the GOAT page. `UNKNOWN`, not inferred. |
| Z.ai Team Plan seat price | Not published. `UNKNOWN`, not estimated. |
| Claude Max 20x price | Not published on Anthropic's own page; carried as UNKNOWN since the 2026-10-02 pass. |
| Non-US carrier bundles | Not swept in this pass. No figure is offered and none is implied. |
| Chinese-language coding-plan corpora | Not re-mined in this pass. Nothing here depends on them. |
| Any subscription | **Not subscribed to, and no authenticated request was made.** Every token figure in this pass is arithmetic on first-party published numbers. |