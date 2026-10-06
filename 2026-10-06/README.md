# Coding-Subscription Market Pass — 2026-10-06 (the negative result, and two corrections)

**Research date: 2026-10-06 (UTC).** No plan was subscribed to and no authenticated request was made.
Every token figure in this pass is arithmetic on first-party published numbers, with the arithmetic
printed and reproducible. Eight first-party sources fetched with a per-attempt log
([data/fetch-log.json](data/fetch-log.json)); 8/8 returned 200, and every one is archived under
[sources/](sources/) with its SHA-256. Databases:
[data/plan-economics.csv](data/plan-economics.csv) (17 plan x model rows),
[data/pool-meter-reports.csv](data/pool-meter-reports.csv) (6 independent meter readings),
[data/aa-lookup.csv](data/aa-lookup.csv) (9 SKU lookups against the leaderboard, including the two
that are absent from it),
[data/subscription-measurements.csv](data/subscription-measurements.csv) (the corrected multiplier
table, with the superseded rows kept),
[data/relay-providers.csv](data/relay-providers.csv) (the relay class measured rather than excluded).
Citations: [references/references.md](references/references.md). Retrieval techniques and their
limits: [references/method-notes.md](references/method-notes.md). Reviews:
[../docs/reviews-2026-10-06.md](../docs/reviews-2026-10-06.md).

---

## 0. The short answer

| Question | Answer | Evidence class |
|---|---|---|
| **Does any plan reach >=10,000M tokens/month for <=$10 on a model verified at or above DeepSeek V4.1 Flash?** | **No, and this is a structural result rather than a gap in searching.** The only route that nominally clears 10,000M is OpenCode Go on Muse Spark 1.3 Contributor, and that SKU **has no Intelligence Index at all** — it is absent from the leaderboard. The next lane, DeepSeek V4.1 Flash, is 6,211M advertised and 2,070–2,899M measured. | FIRST-PARTY-COMPUTED |
| **Why is it structural** | At a 100%-cache-read mix, **$10 of raw API credit buys at most 5,000M tokens** on the cheapest qualifying price in existence. A credit balance therefore cannot produce 10B for $10 at any vendor; only a subscription with a multiplier can, and every multiplier in this market is below 2x. | FIRST-PARTY-COMPUTED |
| **Best lane that is actually verified** | **OpenCode Go on DeepSeek V4.1 Flash (off-peak), II 39.4562.** 6,211M advertised; **2,070–2,899M measured**, because the $60 is a shared pool rather than a per-model budget. | FIRST-PARTY-COMPUTED / THIRD-PARTY |
| **Highest verified quality reachable** | GLM-5.3-Flash at II 41.8075 on the same $10 plan (1,697M), or MiMo-V2.6-Pro at **II 46.3242** on the same plan for 800M, whose ceiling is the $15 per-model cap rather than the $60 pool. | FIRST-PARTY-COMPUTED |
| **Correction to the 2026-10-02 pass** | Its top row ranked Muse Spark 1.3 Contributor at **II 48.09**. That is the **base model's** score. The Contributor tier is a different, discounted SKU with no score, and it is the only Go model that trains on your prompts with no ZDR. | DOCUMENTED |
| **Correction to the 2026-10-02 pass** | Its SuperGrok row published **190x ±21**. The source **retracted** that on 2026-10-03: the measuring account had a linked X Premium+ subscription. Correct figures are 80x ±4 at $70, 18.0x ±0.3 at $30, 15.7x ±0.8 for Lite. | MEASURED |
| **Relays** | No longer excluded by category. Measured against a four-part standard, **0 of 4** evaluated providers are rankable, and the reasons are properties, not categories. The one with a public rate card prices at **3.30x the official rate for the same model**. | FIRST-PARTY |
| **Confidence** | HIGH on every price and cap, all read from the vendor's own page today. The traffic mix is a quoted convention, stated beside every figure that depends on it. **No metered result in this pass.** | — |

---

## 1. The result, and why it is structural

The target is >=10,000M tokens/month for <=$10 on a model verified at or above DeepSeek V4.1 Flash
(II 39.4562). No plan in this market meets it. The interesting part is that **it could not**, and
that fact is arithmetic rather than an absence of searching.

**The cheapest qualifying price in existence is $0.002 per 1M** — the cached-read rate on Muse Spark
1.3 Contributor on OpenCode Go [R1]. At a **100% cache-read mix**, which is the most favourable
traffic any real workload can produce, $10 of raw API credit buys:

```
$10 / $0.002 per 1M  =  5,000M tokens
```

`tools/derive-yields.py --ceiling 10 --input 0.10 --output 0.20 --cache 0.002 --mix 100/0/0` prints
that division in full. **5,000M is the ceiling, and it is half the target.** The same $10 at the
audited 97% agent mix buys 1,838M, a factor of 2.7 lower.

So the credit route is closed by arithmetic before any provider is considered. Three corollaries,
each checked against a named source rather than assumed:

1. **A 10B-for-$10 route must be a subscription, and its multiplier must exceed 2x.** On the
   qualifying model's own published prices the gap is larger still: 10,000M of DeepSeek V4.1 Flash at
   OpenCode Go's off-peak blended rate costs $96.60, which is **9.7x** a $10 ceiling, and at
   DeepSeek's own official off-peak list rate ($0.01559/M blended) it costs $155.90, which is
   **15.6x**. The 2x figure is the floor; the 9.7x–15.6x figures are what the market actually
   offers. This pass does not publish a single blended "44x" figure, because no price source it can
   verify reproduces one, and an unsourced multiplier is the defect this repo exists to catch.
2. **Seat splitting cannot create the multiplier.** Splitting a seat N ways gives `(P/N)/(Q/N) = P/Q`
   [R20], so the per-token rate is unchanged. Claude Max 5x at $100 and Claude Max 20x at $200 price
   identically per token in the one instrument that records both. The identity is the finding; the
   token counts behind it are not carried, and the reason is in [references/references.md](references/references.md) [R20].
3. **The two SKUs that would close the gap are not verified.** The only two prices at or below
   $0.0028/M in the whole market are the two models the leaderboard **does not carry**. The cheapest
   lane in existence is unscored, and so is the second-cheapest. That is not a coincidence to be
   explained away; it is what a discounted contributor tier is.

**What would falsify this.** A subscription whose multiplier exceeds 2x on a model the leaderboard
scores, or a qualifying price below $0.001/M from any vendor. Neither exists on the pages read
today. §7 lists the rest.

---

## 2. The shared pool: the correction that moves the number

This is the substantive correction to the 2026-10-02 pass.

That pass read `docs/go/` as publishing **independent per-model dollar ceilings** and ranked on that.
Its top row was 11,029M tokens/month for $10, the whole month spent on one model.

**The vendor's own sentence does not say that.** [R1]:

> "Each model's monthly limit below determines how its usage counts toward those allowances."

"Counts **toward those allowances**" is compatible with a per-model budget and with a shared pool the
per-model figure bounds. The page does not say which, so the page alone cannot settle it. Six
independent reports say the second:

| Report | Date | What it records |
|---|---|---|
| `anomalyco/opencode#49186` [R10] | 2026-09-15 | "the usage was actually deducted from the same shared Go monthly quota" — **open** |
| `anomalyco/opencode#47547` [R11] | 2026-09-06 | 100% shown at **$22.18 of $60**; the reporter notes 47.8 + 34.7 + 17.5 = **exactly 100.0%** |
| `anomalyco/opencode#52962` [R9] | 2026-10-03 | every paid model blocked at **$4.38** total spend, including models with **zero** recorded usage |
| `anomalyco/opencode#46365` [R12] | 2026-08-31 | 100% shown at **$24.53**, "far below documented $60 limit" |
| r/opencode `1wy907r` [R14] | 2026-10-05 | "I seem to hit my monthly limit on 20$, when ive only used my sub on glm, deepseek and mimo." |
| r/opencode `1wy6vby` [R15] | 2026-10-05 | "7.56$ usage = 27% … i get about **28$** worth of usage per month" |

**#47547 is a distinct mechanism and would have been invisible had the pool reading been accepted
first.** Its percentages sum to exactly 100.0 while the dollars are at 37%. A shared-pool model does
not predict that; a meter that sums per-model percentages does. It is the reason the shared-pool
reading is carried as *a* reading and not as *the* resolution: no maintainer has replied in any of
these threads, and this pass has no paid account with which to settle it.

An independent instrument reached the same model of the world and recorded it per row:
`min(共享月池$60, 模型Usage $60)` — "per-model allowances within one plan are not additive" [R20].

**The honest planning number is therefore 11,029M advertised / 2,070–2,899M measured** on the
qualifying lane, and `data/plan-economics.csv` carries `cap_model`, `monthly_pool_usd`,
`per_model_cap_usd` and `tokens_m_advertised` / `tokens_m_measured` as separate columns so the two
cannot be read as one figure. The clearest single demonstration that the caps are pooled and not
additive is on the vendor's own page: **Go Plus raises the price 4x and the DeepSeek per-model cap
only 2x** ($60 → $60 against a $120 pool), so buying Go Plus does not double that row's yield.

**This also corrects the 2026-09-20 pass**, which reached the same additive reading and ranked on it:
"up to ~$60/mo of list-value usage across 27 models" and "~6x face". That row now carries a dated
superseding note in `2026-09-20/data/providers-database.csv` and in its README, and the correction is
in [../docs/reviews-2026-10-06.md](../docs/reviews-2026-10-06.md).

---

## 3. The ranked field

Every plan x model where a first-party ceiling and a leaderboard score both exist, ordered by
tokens per dollar. `tools/derive-yields.py` recomputes any row.

| Plan | $/mo | Model | II | Verdict | Yield (M/mo) | $/M |
|---|---|---|---|---|---|---|
| **OpenCode Go** | **10** | **DeepSeek V4.1 Flash (off-peak)** | **39.4562** | **best verified lane** | **6,211 advertised / 2,070–2,899 measured** | **$0.0016** |
| OpenCode Go | 10 | GLM-5.3-Flash | 41.8075 | best quality at volume | 1,697 | $0.0059 |
| OpenCode Go | 10 | MiMo-V2.6-Pro | **46.3242** | best II per dollar; $15 cap binds | 800 | $0.0125 |
| OpenCode Go | 10 | Kimi K3 | 43.5938 | $15 cap, dearest model | 34 | $0.2940 |
| GLM Coding Plan Lite | 18 | GLM-5.3 | 44.7774 | campaign expires 2026-10-07 | 420 | $0.0429 |
| Command Code GOAT | 10 | DeepSeek V4.1 Flash | 39.4562 | $70 monthly ceiling over a $35 weekly window | 6,211 per-model / 7,246 plan-wide ceiling | $0.0016 |

**Two rows are ranked nowhere**, and both are the point of this pass:

| SKU | Yield (M/mo) | Why it is not ranked |
|---|---|---|
| Muse Spark 1.3 Contributor (OpenCode Go) | 11,029 | **No Intelligence Index.** `notFound` on the leaderboard [R2]. Cheapest lane in existence, region-limited, and the only Go model with prompt training on and no ZDR. |
| MiMo-V2.6-Flash (OpenCode Go) | 7,878 | **No Intelligence Index.** Also `notFound` [R2]. A 37.88 score is quoted for it in third-party material and is not carried here, because it cannot be checked against a board that does not list the model. |

The second-place lane in the yield ranking is an unverifiable SKU, and the 2026-10-02 pass ranked
both. §4 of that pass published the top row at **II 48.09**; that number is the **base** Muse Spark
1.3's score, carried across from a row that exists to a SKU that does not.

---

## 4. Two corrections, in full

### 4.1 The 190x multiplier is retracted by its own source

The 2026-10-02 pass published "SuperGrok 190x ±21" [its review §3]. On 2026-10-03 the measuring
project retracted it [R16]:

> "SuperGrok on a clean account (no X linked) = 18.0x; X-linked account reported as SuperGrok +
> X Premium+ ($70) = 80x (186x vs SuperGrok price alone)"

| Account | Price | Multiplier | Date | Status |
|---|---|---|---|---|
| SuperGrok, **X Premium+ linked** | $70 | **80x ± 4** | 2026-10-03 | current |
| SuperGrok, **no X account linked** | $30 | **18.0x ± 0.3** | 2026-10-03 | current, replaces 190x |
| SuperGrok Lite | $10 | **15.7x ± 0.8** | 2026-10-02 | current |
| SuperGrok, X Premium+ linked | $30 | 190x ± 21 | 2026-10-01 | **SUPERSEDED** |

The confound was worth about **10x** and the price basis another 2.3x. The 2026-10-02 pass had
already noticed the linked subscription and recorded it as a caveat on the 190x, then published the
number in three places anyway. **A caveat on a figure is not a correction to it.** The old rows are
kept in [data/subscription-measurements.csv](data/subscription-measurements.csv) marked `SUPERSEDED`
rather than deleted, because the correction is the finding.

The generalisable lesson is in the report and not only in the table: **a subscription multiplier read
from one account is an upper bound until its confounds are enumerated.**

### 4.2 A score was inherited from a different SKU

`Muse Spark 1.3 Contributor` was ranked at **II 48.09** in the 2026-10-02 pass. The leaderboard's
`muse-spark-1-3` scores **48.0923** — the base model. The Contributor tier is a separate, heavily
discounted SKU [R1] and the leaderboard carries no row for it [R2]. Both vendors that publish a
score column print "not yet scored" for it.

Because the Contributor is the **only** lane in the market above 10,000M, this one inheritance is
what made an unverified SKU the answer to the market. Both SKUs are now recorded `notFound` in
[data/aa-lookup.csv](data/aa-lookup.csv) and marked `unscored:` in
[data/plan-economics.csv](data/plan-economics.csv), and `unscored-model` in `tools/validate.py`
refuses the defect from now on.

---

## 5. What the traffic mix does to every number

Unchanged from the 2026-10-02 method and re-derived here with `tools/derive-yields.py`: a $/M is a
division and its divisor is the mix. On DeepSeek V4.1 Flash at OpenCode Go's off-peak card:

| Mix | Blended $/M | Yield from $60 |
|---|---|---|
| 97% cache / 2.5% in / 0.5% out | $0.00966 | 6,211M |
| no cache (0/75/25) | $0.26250 | 229M |
| 100% cache read | $0.00300 | 20,000M |

**27.2x between the audited mix and the worst case.** On MiMo-V2.6-Pro the same spread is **29.0x**.
Every row in [data/plan-economics.csv](data/plan-economics.csv) carries its `traffic_mix`, and
`mix-declared` in the validator refuses a derived figure whose row does not.

---

## 6. What is unreachable, and one dated cliff

- **No plan was subscribed to and no authenticated request was made.** Every figure is arithmetic on
  published numbers. Nothing in this pass is a metered result.
- **The pool question is not settled.** Six reports say shared; the vendor's page is ambiguous; no
  maintainer has replied; this pass cannot check without a paid account. Carried as a range.
- **Z.ai's off-peak all-day window and its GLM-5.3-Flash campaign both expire 2026-10-07**, the day
  after this pass. Every Z.ai ceiling in §3 roughly halves from 2026-10-08. The archived page's
  SHA-256 is unchanged from the 2026-10-02 fetch, so no successor campaign is announced.
- **Command Code's over-quota behaviour is UNKNOWN.** The GOAT page publishes the limits and no
  billing rule, so this pass makes no claim about whether over-quota requests are declined.
- **Reddit's `search.rss` silently ignores its query.** Measured: a nonsense term returns HTTP 200 and
  a well-formed feed with 0 entries. The two community meters in §2 come from a recency feed, read as
  a feed, and `tools/fetch-community.py` refuses to present such a feed as a search result.
- **Not swept here:** non-US carrier bundles, Chinese-language coding-plan corpora, startup
  programmes, GPU registries. No figure is offered and none is implied.

---

## 7. What would falsify this pass

- **A metered month on any plan here.** It would replace a published ceiling with a measurement and
  settle §2 outright. The single most valuable missing evidence.
- **A maintainer statement on whether OpenCode Go's monthly limits are per-model or pooled.** Either
  reading moves the best verified lane between 2,899M and 6,211M, and the vendor's own sentence
  supports both.
- **A leaderboard score for `muse-spark-1-3-contributor` or `mimo-v2-6-flash` at or above 39.4562.**
  That alone turns the market's negative result into a hit, and it is the cheapest possible refutation:
  the lanes exist, the prices exist, only the verification is missing.
- **Any qualifying price below $0.001 per 1M.** $10 of credit would then exceed 10,000M unaided and
  the arithmetic wall in §1 would no longer hold.
- **A recomputation under a mix the reader measured.** Every grid and both parsers are in the repo so
  this is a five-minute check, and CI fails if a parser stops regenerating its CSV byte for byte.

---

## 8. What this pass changed in the repo

| Artefact | Change |
|---|---|
| `2026-10-02/README.md`, `docs/reviews-2026-10-02.md` | 190x marked SUPERSEDED with the corrected figures and the reason |
| `2026-10-02/data/plan-economics.csv` | Contributor row re-slugged and marked `unscored:`; every DOLLAR-CEILING row records the pool; `traffic_mix` and `aa_score_provenance` columns added |
| `2026-09-20/` | The additive-pooling row and the "~6x face" and "across 27 models" readings carry dated superseding notes; the category exclusion of relays is marked superseded by a measurement standard |
| `tools/validate.py` | Four checks added: `unit-scale`, `unscored-model`, `shared-cap`, `mix-declared` |
| `tools/` | `fetch-source.py`, `fetch-community.py`, `parse-aa-scores.py`, `derive-yields.py` added |
| `README.md` (root) | This pass listed; the relay exclusion replaced by the measurement standard; the gate description extended from four checks to eight |