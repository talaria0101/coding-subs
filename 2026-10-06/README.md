# Coding-Subscription Market Pass — 2026-10-06 (the negative result, and two corrections)

**Research date: 2026-10-06 (UTC), with four source re-fetches on 2026-10-07 recorded separately in
the same log.** No plan was subscribed to and no authenticated request was made.
Every token figure in this pass is arithmetic on first-party published numbers, with the arithmetic
printed and reproducible. Twelve fetches with a per-attempt log
([data/fetch-log.json](data/fetch-log.json)); **12/12 returned 200, and the ten distinct results are
archived** under [sources/](sources/) with their SHA-256. Two of the twelve are re-fetches of pages
already archived, whose bytes came back unchanged and are therefore not written twice — the log
records their `sha256` against the URL but leaves `saved_as` empty. Databases:
[data/plan-economics.csv](data/plan-economics.csv) (20 plan x model rows),
[data/pool-meter-reports.csv](data/pool-meter-reports.csv) (6 independent meter readings),
[data/aa-lookup.csv](data/aa-lookup.csv) (18 SKU lookups over 15 distinct slugs, including the
four that are absent from both archived pages),
[data/models-database.csv](data/models-database.csv) (25 model rows from the leaderboard payload),
[data/subscription-measurements.csv](data/subscription-measurements.csv) (9 multiplier rows, with
the superseded ones kept),
[data/relay-providers.csv](data/relay-providers.csv) (4 rows — the relay class measured rather than
excluded by category).
Citations: [references/references.md](references/references.md). Retrieval techniques and their
limits: [references/method-notes.md](references/method-notes.md). Reviews:
[../docs/reviews-2026-10-06.md](../docs/reviews-2026-10-06.md).

---

## 0. The short answer

| Question | Answer | Evidence class |
|---|---|---|
| **Does any plan reach >=10,000M tokens/month for <=$10 on a model verified at or above DeepSeek V4.1 Flash?** | **No, and this is a structural result rather than a gap in searching.** Two lanes clear 10,000M on a $10 OpenCode Go plan — Muse Spark 1.3 Contributor and Muse Spark 1.2 Contributor, both at 11,029M — and **neither has an Intelligence Index at all**. The next-largest lane, MiMo-V2.6-Flash at 7,878M, does not clear 10,000M and is the largest lane in the market the board does score; it scores **II 37.8844**, below the 39.4562 bar. So the result does not rest on how many lanes clear the threshold — **not one of them is a model the leaderboard scores at or above the bar.** The best verified lane is DeepSeek V4.1 Flash, 6,211M advertised and 2,070–2,899M measured, where that range is the $20 and $28 meters divided by the same $0.00966/M rate. | FIRST-PARTY-COMPUTED |
| **Why is it structural** | At a 100%-cache-read mix — an upper bound no real workload reaches — **$10 of raw API credit buys at most 5,000M tokens** on the cheapest qualifying price in the sweep — $0.002 per 1M across the OpenCode Go grid, the Z.ai docs, the DeepSeek pricing page, the Command Code GOAT page and the xAI Grok docs. At this pass's own audited 97% mix it buys **1,838M**. A credit balance therefore cannot produce 10B for $10 at any vendor; only a subscription with a multiplier can, and the multipliers measured in this market run from **9.3x** (Muse Code High Usage at its standard list price) and **10.25x** (ChatGPT Pro at $100) up to **15.7x** (SuperGrok Lite). One further reading, **114x**, is the same Muse Code run as the 9.3x figure priced at the standard API list rather than the discounted Contributor list price: it is two denominators for one measurement, not a second measurement, and a multiplier without a stated denominator is not a comparison. On any single consistent basis the measured range is 9.3x to 15.7x — so a multiplier is not the obstacle either. What fails is the conjunction: none of the cheap plans and none of the high-multiplier subscriptions are simultaneously cheap enough and scored high enough. | FIRST-PARTY-COMPUTED |
| **Best lane that is actually verified** | **OpenCode Go on DeepSeek V4.1 Flash (off-peak), II 39.4562.** 6,211M advertised; **2,070–2,899M measured**, because the $60 is a shared pool rather than a per-model budget. | FIRST-PARTY-COMPUTED / THIRD-PARTY |
| **Highest verified quality reachable** | GLM-5.3-Flash at II 41.8075 on the same $10 plan (1,697M), or MiMo-V2.6-Pro at **II 46.3242** on the same plan for 800M, whose ceiling is the $15 per-model cap rather than the $60 pool. | FIRST-PARTY-COMPUTED |
| **Correction to the 2026-10-02 pass** | Its top row ranked Muse Spark 1.3 Contributor at **II 48.09**. That is the **base model's** score. The Contributor tier is a different, discounted SKU with no score, and it is one of only two Go models that train on your prompts with no zero data retention (ZDR) — the two Contributor tiers, 1.3 and 1.2. | DOCUMENTED |
| **Correction to the 2026-10-02 pass** | Its SuperGrok row published **190x ±21**. The source **retracted** that on 2026-10-03: the measuring account had a linked X Premium+ subscription. Correct figures are 80x ±4 at $70, 18.0x ±0.3 at $30, 15.7x ±0.8 for Lite. | MEASURED |
| **Relays** | No longer excluded by category. Measured against a four-part standard (§8), **0 of 3** evaluated providers are rankable and the fourth row is software, not a provider. The one with a public rate card prices at **5.33x the official rate for the same model**. | FIRST-PARTY |
| **Confidence** | **HIGH on the ceilings, MEDIUM on the blended $/M figures, and not HIGH on everything.** The ceilings are read from each vendor's own page. The $/M figures depend on a quoted traffic mix, not a measured workload. One price quotation in this pass was found to be wrong on 2026-10-07 after publication (R5, DeepSeek) and four published numbers inherited it — a price read from a page is evidence only while it still matches that page, which is why `validate.py` now checks every quoted figure against the archived bytes. **No metered result in this pass.** | — |

> **SUPERSEDED 2026-10-07:** the first two rows of this table are not proved by their own arithmetic.
> $0.002 is the price of the unscored Muse Spark Contributor SKUs, so it is not a qualifying price; the
> cheapest qualifying non-zero price on the grid is DeepSeek V4.1 Flash off-peak at $0.003, a 3,333M
> bound. A $0 lane is outside the division altogether, and the Command Code GOAT page archived here lists
> Ling 3.1 Flash at Free while the leaderboard archived here scores `ling-3-1-flash` at 41.0906. The
> verdict becomes "not shown, with one live candidate whose identity and delivery are unverified". The
> Relays row's class `FIRST-PARTY` is not one of the six classes the root README declares. See
> [../2026-10-07/README.md](../2026-10-07/README.md) section 1 and [../2026-10-07/data/citation-audit.csv](../2026-10-07/data/citation-audit.csv).

---

## 1. The result, and why it is structural

The target is >=10,000M tokens/month for <=$10 on a model verified at or above DeepSeek V4.1 Flash
(II 39.4562). No plan in this market meets it. The interesting part is that **it could not**, and
that fact is arithmetic rather than an absence of searching.

**Across the pages this pass read — the OpenCode Go grid [R1], the Z.ai dev-pack and team-plan
docs, the DeepSeek pricing page [R4], the Command Code GOAT page and the xAI Grok docs, plus the
relay rate cards in §8 — the cheapest qualifying price is $0.002 per 1M**: the cached-read rate on
Muse Spark 1.3 Contributor on OpenCode Go [R1]. That is a bound on the pages fetched and read here,
not a claim about every vendor in the market; a vendor whose page this pass did not read could in
principle price below it. Two bounds on the yield, because they are different claims and only one
of them is an upper bound:

```
100% cache-read mix (upper bound):   $10 / $0.002 per 1M  =  5,000M tokens
audited 97% agent mix (this pass):   $10 / $0.00544 per 1M  =  1,838M tokens
```

`tools/derive-yields.py --ceiling 10 --input 0.10 --output 0.20 --cache 0.002 --mix 100/0/0` prints
the first division in full. **5,000M is a ceiling no real workload reaches** — it assumes every
token is a cache read — and it is half the target. At the 97% mix this pass audited across a real
coding workload, the same $10 buys **1,838M**, a factor of 2.7 lower. **The conclusion does not
depend on which bound a reader prefers**: both are below 10,000M.

> **SUPERSEDED 2026-10-07:** both bounds divide by $0.002, the cached-read price of Muse Spark 1.3
> Contributor, which has no Intelligence Index. At the cheapest qualifying price, $0.003, the 100%-cache
> bound is 3,333M and the 97% figure 1,035M. Neither bound covers a $0 lane, so "the credit route is
> closed by arithmetic" holds for priced lanes only. See [../2026-10-07/README.md](../2026-10-07/README.md)
> section 1.1.

So the credit route is closed by arithmetic before any provider is considered. Three corollaries,
each checked against a named source rather than assumed:

1. **A 10B-for-$10 route must be a subscription, and its multiplier must exceed 2x.** On the
   qualifying model's own published prices the gap is larger still: 10,000M of DeepSeek V4.1 Flash at
   OpenCode Go's off-peak blended rate costs $96.60, which is **9.7x** a $10 ceiling, and at
   DeepSeek's own official off-peak list rate ($0.00966/M blended, [R5]) it costs $96.60 as well,
   because Go's DeepSeek tariff is DeepSeek's own off-peak tariff to the cent. At the peak tariff
   ($0.01932/M) 10,000M costs $193.20, which is **19.3x**. The 2x figure is the floor; the
   9.7x–19.3x figures are what the market actually offers. This pass does not publish a single
   blended "44x" figure, because no price source it can verify reproduces one, and an unsourced
   multiplier is the defect this repo exists to catch.
   > **CORRECTED 2026-10-07.** This paragraph previously read "$0.01559/M blended … $155.90 …
   > **15.6x**" off-peak and "$0.03118/M … $311.80 … 31.2x" at peak. That blended rate came from a
   > misquotation of the DeepSeek price table: $0.007, $0.22, $0.014 and $0.44 are not on the page.
   > The corrected off-peak blend is **$0.00966/M** and the peak blend **$0.01932/M**. See
   > [references/references.md](references/references.md) [R5].
2. **Seat splitting cannot create the multiplier.** Splitting a seat N ways gives `(P/N)/(Q/N) = P/Q`
   [R20], so the per-token rate is unchanged. Claude Max 5x at $100 and Claude Max 20x at $200 price
   identically per token in the one instrument that records both. The identity is the finding; the
   token counts behind it are not carried, and the reason is in [references/references.md](references/references.md) [R20].
   > **SUPERSEDED 2026-10-07:** the two Claude Max rows the [R20] entry quotes (19,625M and 39,250M) are
   > `claude-sonnet-5` rows in that repository's adopted-plans CSV, derived from its Opus rows by a 2.5
   > list-price ratio and not measured; the `claude-opus-5` rows read 7,850M and 15,700M. The identity
   > holds within one SKU. The file is now archived at a pinned commit by the 2026-10-07 pass; see
   > [../2026-10-07/data/citation-audit.csv](../2026-10-07/data/citation-audit.csv).
3. **All four of the cheapest lanes in the market are unscored or below the bar.** The archived grid
   carries four prices at or below $0.0028/M — Muse Spark 1.3 Contributor ($0.002/M blended
   $0.00544), Muse Spark 1.2 Contributor ($0.002), MiMo-V2.6-Flash ($0.0028) and MiMo-V2.5
   ($0.0028). Looked up on 2026-10-07, the three Contributor and 2.5 SKUs are **notFound** on the
   archived leaderboard page, and MiMo-V2.6-Flash scores **II 37.8844** — below the 39.4562 bar.
   **Not one of the four clears the gate.** The earlier version of this section claimed there were
   only two such lanes; there are four, and two of them had not been looked up at all. That weakens
   the structural story rather than strengthening it: a four-for-four pattern read off one grid is
   suggestive, but two of the four observations did not exist until this correction added them.
   > **CORRECTED 2026-10-07.** The 100%-cache-read ceiling is restated above alongside the 97%
   > figure; the original put only the 100% number in §0, where the headline lives.

**What would falsify this.** A subscription whose multiplier exceeds 2x on a model the leaderboard
scores, or a qualifying price below $0.001/M from any vendor. Neither exists on the pages read
today. §7 lists the rest.

> **SUPERSEDED 2026-10-07:** the second falsifier is met on price by this pass's own archive.
> `sources/commandcode-goat.html` carries a Ling 3.1 Flash row priced Free ("Free while it lasts. Every
> request is billed $0."), and `sources/aa-leaderboard-models.html` scores `ling-3-1-flash` at 41.0906.
> Whether the free endpoint serves that checkpoint is unknown. See
> [../2026-10-07/README.md](../2026-10-07/README.md) section 1.2.

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

> **SUPERSEDED 2026-10-07:** the vendor's public console code (anomalyco/opencode at commit
> `ecc4916b`) keeps one `monthlyUsage` counter per user, adds
> `quotaCost = Math.round(cost * modelInfo.costMultiplier)` to it for every model, and apportions the one
> overall percentage across models so that the per-model figures sum to it by construction. A weighted
> shared pool therefore predicts both observations in #47547, and they do not argue against a pool.
> Production traffic is forwarded to a separate inference service whose limiter is not public, so the
> production rule stays open. See [../2026-10-07/README.md](../2026-10-07/README.md) section 3.

An independent instrument reached the same model of the world and recorded it per row:
`min(共享月池$60, 模型Usage $60)` — "per-model allowances within one plan are not additive" [R20].

**The honest planning number is therefore 11,029M advertised / 2,070–2,899M measured** on the
qualifying lane. That range is two independent meters at the two ends: the lower bound is a user
blocked at **$20** of total account spend [R14], the upper a user reading **$7.56** of spend
against a meter showing 27% consumed, which extrapolates to **$28** [R15]. Both are divided by
the same off-peak blended rate of $0.00966/M: 20 / 0.00966 = 2,070 and 28 / 0.00966 = 2,899. The
ratio between the two bounds is **1.4x**, not the 2.9x an earlier version of this README stated.
Two further meters sit inside the range ($22.18 → 2,296M and $24.53 → 2,539M) and a third sits
well below it: **$4.38 → 453M, which is 4.6x lower than the 2,070M lower bound** and is the lower
anchor of the widest spread in the file, **6.4x**, from $4.38 to $28. That meter reports a user blocked
at less than a fifth of the pool the other two reach, which is a real observation about a metered
service and not a contradiction of the ceiling — and it is why the range is quoted from the two
bracketing meters rather than as an average of four.

`data/plan-economics.csv` carries `cap_model`, `monthly_pool_usd`,
`per_model_cap_usd` and `tokens_m_advertised` / `tokens_m_measured` as separate columns so the two
cannot be read as one figure.

**What the vendor's page actually shows about Go Plus, stated without the assumption.** The
archived page publishes a **$60** monthly limit for DeepSeek V4.1 Flash under Go
([sources/opencode-go.md](../2026-10-06/sources/opencode-go.md) line 178) and **$120** for the same
model under Go Plus (line 223). The price goes $10 → $40. So on the vendor's own numbers:

| | Go ($10) | Go Plus ($40) | Change |
|---|---|---|---|
| DeepSeek per-model monthly limit | $60 | $120 | **2x** |
| Plan price | $10 | $40 | **4x** |
| Yield at the same blended rate | 6,211M | 12,423M | 2x |
| Cost per 1M at $10 of plan price | $0.0016 | $0.0032 | **2x worse** |

**The published per-model limit doubles cleanly and the price quadruples**, so $/M worsens 2x under
any reading of how the money is divided. That much is arithmetic on the page.

> **CORRECTED 2026-10-07 — this exhibit was previously overstated.** It read "the DeepSeek
> per-model cap only 2x (**$60 → $60 against a $120 pool**), so buying Go Plus does not double that
> row's yield", and presented it as "the cleanest evidence available and it is first-party". **There
> is no separate pool figure anywhere on the page.** Line 223 reads `$120` under Go Plus, exactly as
> line 178 reads `$60` under Go; the page publishes a *monthly limit* per model and nothing else.
> The "$60 against a $120 pool" was an assumption, and it was the assumption carrying the
> conclusion: under the additive reading the cap also doubles, both readings predict the same table,
> and the row therefore **proves nothing about pooling on its own**.
>
> What survives is weaker and still worth carrying: the limit doubles while the price quadruples, so
> $/M worsens 2x, and **whether $120 is a pool the other models divide or an independent per-model
> budget is the open question**. The page is consistent with the pool reading and does not settle
> it. This row is demoted from "decisive first-party evidence" to "consistent with, not decisive";
> the six reports above and the independent instrument remain the actual evidence for the pool, and
> the planning number remains a range for exactly this reason.
>
> `data/plan-economics.csv` row 17 was corrected with it. It carried
> `monthly_pool_usd=120, per_model_cap_usd=60` alongside `tokens_m_advertised=12423` — the full
> $120 at the blended rate, ignoring the cap on the same row — while its own notes cell said "the
> per-model cap is $60 on a $120 pool, so min() takes the $60". It now carries the published $120
> per-model limit, which yields 12,423M consistently.

**This also corrects the 2026-09-20 pass**, which reached the same additive reading and ranked on it:
"up to ~$60/mo of list-value usage across 27 models" and "~6x face". That row now carries a dated
superseding note in `2026-09-20/data/providers-database.csv` and in its README, and the correction is
in [../docs/reviews-2026-10-06.md](../docs/reviews-2026-10-06.md). The "~6× face" figure is itself
marked SUPERSEDED and was never 6x on any reading: the Go plan's grid publishes **39 rows**, of
which **38 carry a dollar monthly limit** and one (LongCat 2.5 Preview Free) is marked Unlimited. The
38 dollar ceilings sum to **$1,365** against a $10 plan, which is **136.5x summed** and 6x only for a
single $60 model. The Go Plus grid has the same 39 rows and sums to **$4,410**, or 441x.
> **CORRECTED 2026-10-07.** This paragraph previously said "37 per-model ceilings" and "$1,335".
> Both were wrong: the archived grid at [sources/opencode-go.md](sources/opencode-go.md) has 38 dollar
> ceilings summing to $1,365. A check now recomputes the count and the sum from the archived table.

---

## 3. The ranked field

**The filter, stated because it is a filter.** Rows here satisfy **all three**:

1. a first-party published ceiling (not a measured meter),
2. a leaderboard Intelligence Index **for that exact SKU**, and
3. the SKU scores at or above **39.4562**, DeepSeek V4.1 Flash.

Of the 20 rows in [data/plan-economics.csv](data/plan-economics.csv), **11 satisfy all three
conditions**. Six are shown below; the other five are named here with the reason, so the count is
reproducible from the CSV rather than asserted:

| Qualifying row not shown | Why it is omitted |
|---|---|
| DeepSeek V4.1 Flash **peak**, OpenCode Go | Same SKU as the ranked off-peak row under the second published tariff. The off-peak tariff is the qualifying one; peak is 2x the rate. |
| DeepSeek V4.1 Flash, **OpenCode Go Plus** | Same SKU on a $40 plan. Ranks behind the $10 row on every figure a buyer compares. |
| GLM-5.3-Flash, **GLM Coding Plan Lite** | Same model as the ranked GLM-5.3 row, on the cheaper plan; ranks behind it. |
| GLM-5.3-Flash, **GLM Coding Plan Pro** | Same model, higher price. |
| GLM-5.3-Flash, **GLM Coding Plan Max** | Same model, highest price. |

The nine rows that do **not** satisfy all three conditions are: five with a first-party ceiling and
no leaderboard score for that SKU (both Muse Spark Contributor tiers on Go and Go Plus, MiMo-V2.5,
LongCat 2.5 Preview Free — the last with no published ceiling at all); GPT 6 Luna at II 38.1245,
below the bar; MiMo-V2.6-Flash at II 37.8844, below the bar; SuperGrok Lite, which carries a
score (Grok 4.7 at II 46.4466) but publishes no token allowance, so there is no first-party ceiling
to convert; and the **GLM Team Plan Standard Seat** row, which is scored but whose seat price is
`UNKNOWN` and whose `tokens_m_advertised` is `UNKNOWN`, so it has no first-party ceiling in dollars
to convert either. The first five fail on verification, the next two on the capability bar, and the
last two on the absence of a published allowance.

> **CORRECTED 2026-10-07.** This section previously said **14** qualifying rows and **eight**
> omitted, and attributed the omissions to three causes including rows "that are `CARRIED-FORWARD`".
> Neither number is derivable from [data/plan-economics.csv](data/plan-economics.csv): the filter
> above selects **11**, and the four Z.ai Pro/Max rows it used to cite as un-verifiable are now
> `DOCUMENTED` for their ceilings and `UNKNOWN` for their $/M. The six rows in the table are the
> six that are not a duplicate SKU-under-another-plan.

> **CORRECTED 2026-10-07 (earlier).** This section previously opened "Every plan x model where a
> first-party ceiling and a leaderboard score both exist", which claims completeness the table does
> not have. The filter is written out and the count is stated rather than implied.

Ordered by tokens per dollar. `tools/derive-yields.py` recomputes any row.

| Plan | $/mo | Model | II | Verdict | Yield (M/mo) | $/M |
|---|---|---|---|---|---|---|
| **OpenCode Go** | **10** | **DeepSeek V4.1 Flash (off-peak)** | **39.4562** | **best verified lane** | **6,211 advertised / 2,070–2,899 measured** ($20 and $28 meters at $0.00966/M) | **$0.0016** |
| OpenCode Go | 10 | GLM-5.3-Flash | 41.8075 | best quality at volume | 1,697 | $0.0059 |
| OpenCode Go | 10 | MiMo-V2.6-Pro | **46.3242** | best II per dollar; $15 cap binds | 800 | $0.0125 |
| OpenCode Go | 10 | Kimi K3 | 43.5938 | $15 cap, dearest model | 34 | $0.2940 |
| GLM Coding Plan Lite | 18 | GLM-5.3 | 44.7774 | campaign expires 2026-10-07 | 420 | $0.0429 |
| Command Code GOAT | 10 | DeepSeek V4.1 Flash | 39.4562 | $70 monthly ceiling over a $35 weekly window | 6,211 per-model / 7,246 plan-wide ceiling | $0.0016 |

**Five rows are ranked nowhere**, and they are the point of this pass. Four of the five are the four
cheapest lanes in the market:

| SKU | Yield (M/mo) | Why it is not ranked |
|---|---|---|
| Muse Spark 1.3 Contributor (OpenCode Go) | 11,029 | **No Intelligence Index.** `notFound` on the archived leaderboard page [R2]. Cheapest lane in this sweep, region-limited, and — with 1.2 Contributor below — one of the only two Go models with prompt training on and no zero data retention (ZDR). |
| Muse Spark 1.2 Contributor (OpenCode Go) | 11,029 | **No Intelligence Index.** Also `notFound`. Same prices, same $60 cap, same yield as 1.3 Contributor — the pass's earlier claim that 1.3 Contributor was the only lane above 10,000M was false on its own archived page. |
| MiMo-V2.6-Flash (OpenCode Go) | 7,878 | **Scored at II 37.8844**, observed 2026-10-07 on `/leaderboards/models`. Below the 39.4562 bar, so it fails the gate — but by 1.57 points, not by absence. |
| MiMo-V2.5 (OpenCode Go) | 7,878 | **No Intelligence Index.** `notFound`. Identical prices to V2.6-Flash, so identical yield. |
| LongCat 2.5 Preview Free (OpenCode Go) | **UNKNOWN** | **$0 lane.** Every token class priced Free with an "Unlimited" monthly limit annotated "limited time", and **no ceiling published**, so no yield can be computed without estimating one. Also `notFound`. A structural negative result has to address a free lane; §1 and this row are where it is addressed. |

The second-place lane in the yield ranking is a SKU the board cannot verify above the bar, and the
2026-10-02 pass ranked four of these five. §4 of that pass published the top row at **II 48.09**;
that number is the **base** Muse Spark 1.3's score, carried across from a row that exists to a SKU
that does not.

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

> **SUPERSEDED 2026-10-07:** two lanes, not one, sit above 10,000M: Muse Spark 1.3 Contributor and Muse
> Spark 1.2 Contributor, as section 3 of this README already says.

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
  maintainer has replied; this pass cannot check without a paid account. Carried as a range. §2's
  Go Plus exhibit, which was previously presented as decisive on this point, is demoted to
  "consistent with, not decisive": the page publishes $60 under Go and $120 under Go Plus and no
  separate pool figure at all.
- **Z.ai's off-peak all-day window and its GLM-5.3-Flash campaign both expire 2026-10-07 — which is
  today.** The archived page states "During September 3 – October 7" and "From September 25 to
  October 7, 2026, all-day usage will be charged at the **off-peak rate**". Every Z.ai ceiling in §3
  roughly halves from 2026-10-08. The page was re-fetched on 2026-10-07 and its SHA-256 is unchanged
  from the 2026-10-02 fetch, so **no successor campaign is announced in the page this pass holds.**
  Whether one exists elsewhere is not established, and the Z.ai rows in §3 should be read as
  expiring within the day.
  > **SUPERSEDED 2026-10-07:** the ceilings do not halve. The 50% off-peak rate is a standing rule
  > (`sources/zai-overview.md` line 135) and peak is 20 of 168 hours a week (line 138); only the
  > all-day extension ends. The page maximum stays reachable off-peak, uniform use gets 0.894 of it and
  > only all-peak use gets half. See [../2026-10-07/README.md](../2026-10-07/README.md) section 4.
- **Command Code's over-quota behaviour is UNKNOWN.** The GOAT page publishes the limits and no
  billing rule, so this pass makes no claim about whether over-quota requests are declined.
  > **SUPERSEDED 2026-10-07:** the rule is published in this pass's own archive,
  > `sources/commandcode-goat.html` line 66: "Past a limit, requests fall back to those credits - and
  > without them, paid models pause until the window or cycle resets while the free models keep
  > working." The same correction applies to [R6] and to the "Command Code over-quota terms" row of
  > [references/references.md](references/references.md).
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
- **A leaderboard score for `muse-spark-1-3-contributor`, `muse-spark-1-2-contributor` or
  `mimo-v2-5` at or above 39.4562.** That alone turns the market's negative result into a hit, and
  it is the cheapest possible refutation: the lanes exist, the prices exist, only the verification is
  missing. `mimo-v2-6-flash` is no longer on this list — it was scored at II 37.8844 on 2026-10-07
  and is 1.57 points short, so it would need to be *re-scored upward*, not looked up.
- **Any qualifying price below $0.001 per 1M.** $10 of credit would then exceed 10,000M unaided and
  the arithmetic wall in §1 would no longer hold.
- **A recomputation under a mix the reader measured.** Every grid and both parsers are in the repo so
  this is a five-minute check, and CI fails if a parser stops regenerating its CSV byte for byte.

---

## 8. The relay measurement standard

The 2026-09-20 and 2026-10-02 passes excluded relays and resellers **by category**. Excluding a
class by category means the class is never measured, and the reasons given were assertions about
what the class *is* rather than observations of what its members *do*. This pass replaces the
category rule with a standard a reader can apply to any operator.

**A relay may be ranked if and only if all four of these hold.**

| # | Test | What passes it | What it is for |
|---|---|---|---|
| 1 | **Publishes a rate card or an allowance** | A per-model price list at a reachable endpoint, or a stated allowance | A price you cannot see cannot be cheaper than the vendor's |
| 2 | **Quantifies its reputation** | A countable public figure — stars, age, registered companies | An operator with no measurable history is an unknown |
| 3 | **Documents a delivery ceiling** | A stated throughput, capacity or usage limit | Unbounded is not unlimited; an undocumented ceiling cannot be planned against |
| 4 | **Records failure modes from issue evidence** | Named issues with dates and quotes, not marketing copy | A claim of reliability is only as good as the evidence contradicting it |

**The four verdicts the standard returns.** Every row in
[data/relay-providers.csv](data/relay-providers.csv) carries exactly one, and the count is a
property of the roster rather than an impression:

| Verdict | Meaning | Count in this roster |
|---|---|---|
| `yes` | All four tests pass; the row may be ranked | **0** |
| `no` | At least one test fails; the failing test names why | **3** |
| `not-applicable` | The row is not a provider (software, an aggregator) | **1** |
| *blank* | **Not a verdict.** A blank cell is not a count and must never be tallied as one | **0** |

The earlier statement "0 of 4 are rankable" counted a blank `rankable` cell on the Sub2api row as a
verdict. It now reads `not-applicable`, and the honest count is **0 of 3 evaluated providers** plus
one row that is software rather than a provider.

**The more serious finding is not the price.** Every one of Fenno's 18 models carries
`availability.status: "unknown"`, `request_count: 0` and `data_status: "pending"` — counted across the
whole payload in `sources/fenno-models.json`, not read off one row. **The platform has never recorded a
single request on any model it lists.** The 5.33x ratio is therefore the smaller result: it prices a
service whose own counters say nothing has ever run through it. A reader deciding whether to rely on
this row should weigh that before the markup, and the pass's own §8 standard counts a provider that
cannot show one completed request as not rankable for that reason as well as for its price.

> **SUPERSEDED 2026-10-07:** every availability block reads `"window": "1h"` and
> `"data_status": "pending"` beside `"request_count": 0`. A pending counter over a one-hour window does
> not establish that the platform has never served a request; lifetime traffic is unknown. The 5.33x
> price ratio is unaffected. The issue citations under [R19] (#3624, #3896 and #6134 grouped as ban
> risk; #7503 under "silent substitution") are corrected in [../2026-10-07/data/citation-audit.csv](../2026-10-07/data/citation-audit.csv).

**What the one measurable member's number says.** Fenno publishes a full 18-model rate card at a
public endpoint. Its `deepseek-v4-1-flash` prices at $0.80 / $3.20 / $0.016 per 1M, which blends to
**$0.05152/M** under the standard mix, against DeepSeek's own published off-peak list of
**$0.00966/M** [R5]: **5.33x the official price**. $10 buys **194M tokens**, missing a 10B bar by
**51x**. The relay is more than five times *more* expensive than buying from the vendor, and that is
now a measurement rather than a red flag.
> **CORRECTED 2026-10-07.** This ratio was published as 3.30x against a $0.01559/M official
> reference. That reference came from the misquotation corrected at [R5]; the corrected ratio is
> **5.33x** (0.05152 / 0.00966), which makes the finding stronger, not weaker.

**The four verdicts for the roster, row by row, are in the CSV.** What is not there is coverage of
the wider roster: this standard was applied to four operators this pass could reach with a public
surface, and no figure is offered for any other.

---

## 9. What this pass changed in the repo

| Artefact | Change |
|---|---|
| `2026-10-02/README.md`, `docs/reviews-2026-10-02.md` | 190x marked SUPERSEDED with the corrected figures and the reason |
| `2026-10-02/data/plan-economics.csv` | Contributor row re-slugged and marked `unscored:`; every DOLLAR-CEILING row records the pool; `traffic_mix` and `aa_score_provenance` columns added |
| `2026-09-20/` | The additive-pooling row and the "~6x face" and "across 27 models" readings carry dated superseding notes; the category exclusion of relays is marked superseded by a measurement standard, and the pointer to that standard corrected from §7 (which was "What would falsify this pass") to §8 here |
| `2026-10-06/` | **Corrected 2026-10-07.** R5's DeepSeek price quotation replaced with the bytes on the page and four derived numbers restated; the Go Plus exhibit demoted from decisive to consistent-with; the `mimo-v2-6-flash` leaderboard row superseded with its 2026-10-07 score; four plan rows added (Muse Spark 1.2 Contributor, MiMo-V2.5, LongCat 2.5 Preview Free, and the corrected Go Plus DeepSeek row); the Z.ai blended $/M cells reclassified from `FIRST-PARTY-COMPUTED` to UNKNOWN |
| `tools/validate.py` | Four checks added: `unit-scale`, `unscored-model`, `shared-cap`, `mix-declared`. **Corrected 2026-10-07:** **seven** checks rewritten after each was shown not to fire on the defect it was written for (the four above, plus `field-columns`, `cost-arithmetic` and `fetch-log-corroborates`), and **three** added — `field-columns` (an arity-preserving column shift), `quoted-money-on-page` (a figure quoted in `references/*.md` that is not on the page it cites), and `evidence-vocabulary` (an evidence class outside the declared set). The per-check evidence is in [../docs/reviews-2026-10-06.md](../docs/reviews-2026-10-06.md) §11 and §12; the count the registry holds is `python3 tools/validate.py --all`'s own `gate-count-claims` check. |
| `tools/` | `fetch-source.py`, `fetch-community.py`, `parse-aa-scores.py`, `derive-yields.py`, `add-leaderboard-rows.py` added. **Corrected 2026-10-07:** `parse-aa-models.py` accepts the bare `{"slug":…}` object shape the leaderboard page ships, and `parse-opencode-go.py` pins its line terminator and disables newline translation so its output is byte-identical on Linux and Windows |
| `README.md` (root) | This pass listed; the relay exclusion replaced by the measurement standard; the gate description corrected to match the number of checks `validate.py` registers |