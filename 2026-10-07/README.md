# Coding-Subscription Market Pass - 2026-10-07 (the negative result is not proved)

**Research date: 2026-10-07 (UTC, read from the machine with `date -u`).** No plan was subscribed to,
no account was created and no authenticated request was made. This pass re-checks the 2026-10-06 pass
against its own archived bytes and against seven fresh research sweeps whose claims were re-read in the
bytes archived here before any of them was published. 87 retrieval attempts are logged in
[data/fetch-log.json](data/fetch-log.json); **73/87 returned 200, and the 73 distinct results are
archived** under [sources/](sources/), one subdirectory per research topic, 9,266,537 bytes in total.
The 14 failures (8 r.jina.ai 403s, 6 vendor 404s) are kept in the log because some of them are cited.

Databases:
[data/citation-audit.csv](data/citation-audit.csv) (17 claims in the 2026-10-06 pass found wrong, unsupported or overstated),
[data/free-lanes.csv](data/free-lanes.csv) (7 $0 or free-trial lanes),
[data/vendor-sweep.csv](data/vendor-sweep.csv) (11 cheapest-price rows),
[data/aa-lookup.csv](data/aa-lookup.csv) (19 slug lookups against the archived leaderboard payload),
[data/capability-rows.csv](data/capability-rows.csv) (14 source-by-model capability rows),
[data/zai-ceilings.csv](data/zai-ceilings.csv) (30 Z.ai plan x model x schedule rows),
[data/drift-check.csv](data/drift-check.csv) (8 page re-fetches compared with the 2026-10-06 bytes),
[data/relay-evaluation.csv](data/relay-evaluation.csv) (7 relay rows against the four-part standard).
Citations: [references/references.md](references/references.md). Retrieval notes:
[references/method-notes.md](references/method-notes.md).

---

## 0. The short answer

| Question | Answer | Evidence class |
|---|---|---|
| **Is "no plan reaches >=10,000M tokens/month for <=$10 on a model scored at or above II 39.4562" proved?** | **No. It is not shown either way.** The 2026-10-06 proof divides $10 by the cheapest price, and a $0 lane escapes that division. One live $0 lane is a candidate: Command Code lists **Ling 3.1 Flash at $0 input, output and cache**, "with no daily request limit ... while it lasts", and the leaderboard scores the slug `ling-3-1-flash` at **II 41.0906**, above the bar. Two things are unverified: whether the free endpoint serves the checkpoint and reasoning mode that was scored, and how many tokens it delivers in a month (no ceiling is published). | FIRST-PARTY-COMPUTED / UNKNOWN |
| **What the price arithmetic does bound** | $10 of raw credit at the cheapest **qualifying** non-zero price on the 2026-10-06 grid, DeepSeek V4.1 Flash off-peak at $0.003 per 1M cached read, buys at most **3,333M** under a 100%-cache upper bound and **1,035M** at the repo's 97/2.5/0.5 mix. The 2026-10-06 figure of 5,000M used $0.002, which is the price of the unscored Muse Spark Contributor SKUs. | FIRST-PARTY-COMPUTED |
| **The other free lanes** | NVIDIA build serves DeepSeek V4.1 Flash on a free trial at "Up to 40 rpm" and "10,000 requests per day", and its trial terms bar production use. Gemini 3.8 Flash's free tier is "Free of charge" with its limits visible only inside AI Studio. OpenRouter lists `inclusionai/ling-3.1-flash` at $0 with no published limit for that ID. None publishes a monthly token ceiling. | DOCUMENTED / FIRST-PARTY-PRICE-ONLY |
| **Strongest paid counter-example** | StepFun Step Plan Flash Plus, $9.99/month, on `step-5-preview`, which the board names "Step 5 Preview" at II 43.7343: **4,571M** at 100% cache and **2,627M** at the 97% mix. Under half the target. | FIRST-PARTY-COMPUTED |
| **Capability side** | The re-fetched leaderboard payload changed hash and gained one scored slug, `solar-pro-2` (II 6.9984); nothing was removed or rescored. Neither Contributor SKU nor `mimo-v2-5` is scored. Meta says the `max` effort is "not available on Contributor-tier models", so the base model's Max score cannot transfer. | DOCUMENTED |
| **OpenCode Go pool** | The vendor's public fallback code meters **one weighted shared counter** per user: `quotaCost = Math.round(cost * modelInfo.costMultiplier)` is added to a single `monthlyUsage` for every model. Production traffic is first forwarded to a separate inference service whose limiter is not public, so the production rule is **UNKNOWN**. | DOCUMENTED / UNKNOWN |
| **Z.ai** | Pages unchanged; no successor campaign announced. The 2026-10-06 claim that "every Z.ai ceiling roughly halves from 2026-10-08" is **wrong**: the 50% off-peak rate is a standing rule and only its all-day extension ends. The 2026-10-06 Pro $72 and Max $160 are legacy V2 prices; the current V3 bundle carries $80 and $168. | FIRST-PARTY-COMPUTED / DOCUMENTED |
| **Corrections to the 2026-10-06 pass** | 17 claims, listed with file:line and the bytes that contradict them in the citation audit. The two that move the headline are the 5,000M bound and the falsifier "a qualifying price below $0.001/M ... Neither exists", which the pass's own Command Code archive meets on price. Command Code's over-quota rule, recorded as UNKNOWN, is printed in that same archive. | DOCUMENTED |
| **Relays** | 0 of 6 evaluated operators pass all four tests; Sub2api is software. Fenno's "never recorded a single request" reads a pending one-hour counter as a lifetime total. | DOCUMENTED |
| **Confidence** | HIGH that the 2026-10-06 proof does not cover $0 lanes (arithmetic on its own archived pages). HIGH on every quoted price and limit (re-read in archived bytes). LOW on the Ling candidate either way: identity and delivery are both unpublished. **No metered result in this pass.** | - |

---

## 1. The headline, re-derived

### 1.1 What the 2026-10-06 arithmetic proves, and what it does not

The 2026-10-06 pass argued that no plan could reach 10,000M tokens a month for $10 on a qualifying
model, because "$10 of raw API credit buys at most 5,000M tokens on the cheapest qualifying price",
$0.002 per 1M ([../2026-10-06/README.md](../2026-10-06/README.md) line 31). Two things are wrong with
that step.

1. **$0.002 is not a qualifying price.** It is the cached-read price of Muse Spark 1.3 and 1.2
   Contributor (grid lines 172-173 of [sources/opencode-go/opencode-go.md](sources/opencode-go/opencode-go.md)),
   and neither SKU has an Intelligence Index ([data/aa-lookup.csv](data/aa-lookup.csv)). Every non-zero
   grid row priced below $0.003 is one of the two Contributor rows or MiMo-V2.6-Flash and MiMo-V2.5 at
   $0.0028 (scored 37.8844, and notFound). At exactly $0.003 sits DeepSeek V4.1 Flash off-peak (line
   178), which scores 39.4562, the bar itself. So the cheapest qualifying non-zero price is $0.003:

   ```
   100% cache-read upper bound:   $10 / $0.003 per 1M    = 3,333M tokens
   97/2.5/0.5 mix:                $10 / $0.00966 per 1M  = 1,035M tokens
   ```

   The conclusion for priced lanes gets stronger, not weaker: the raw-credit route is a third of the
   target even under the bound no workload reaches.

2. **A $0 lane is outside the division.** `$10 / $0` is not a yield. The 2026-10-06 pass recognised this
   for one lane (LongCat 2.5 Preview Free, carried as UNKNOWN) and then wrote "a credit balance therefore
   cannot produce 10B for $10 at any vendor; only a subscription with a multiplier can", which does not
   follow. Its own falsifier was "a qualifying price below $0.001/M from any vendor. Neither exists on
   the pages read today" (line 100). The Command Code GOAT page it archived carries a Ling 3.1 Flash row
   priced Free ("Free while it lasts. Every request is billed $0."), and the leaderboard page it
   archived scores `ling-3-1-flash` at 41.0906. On price, its falsifier was met by its own bytes.

The verdict therefore moves from "no, structurally" to **"not shown, with one live candidate whose
identity and delivery are unverified"**.

### 1.2 The candidate: Ling 3.1 Flash at $0

| | Command Code free deal | Leaderboard `ling-3-1-flash` |
|---|---|---|
| Price per 1M (input / output / cache) | 0 / 0 / 0 | listed at 0.3 / 0.9 / 0.06 in the payload |
| Context window | "262K-token context" | 1,000,000 (`contextWindowTokens`) |
| Reasoning | "low, medium, and high reasoning effort" | `isReasoning: true` |
| Served from | "Novita's endpoint" | no endpoint named |
| Score | "not yet scored" in Command Code's own model table | II 41.0906 |
| Monthly ceiling | "No daily request limit"; no RPM, TPM or monthly figure | - |
| Term | "while it lasts" | - |

Sources: [sources/free-lanes/commandcode-pricing-limits.html](sources/free-lanes/commandcode-pricing-limits.html),
[sources/drift-vendors/commandcode-goat.html](sources/drift-vendors/commandcode-goat.html),
[sources/aa-leaderboard-models.html](sources/aa-leaderboard-models.html). OpenRouter's only endpoint
for the same model is named "Novita | inclusionai/ling-3.1-flash-20261002" at 262,144 tokens of context
([sources/free-lanes/openrouter-endpoints.json](sources/free-lanes/openrouter-endpoints.json)).

**Identity verdict: UNKNOWN.** Three readings were tested. *Same checkpoint and mode*: would need the
leaderboard to name the endpoint it measured, or a vendor to name the checkpoint the board scored;
neither is published. *A non-reasoning variant only*: contradicted, since both Command Code and
OpenRouter's catalog (`default_enabled: true`) offer reasoning. *A related checkpoint at a smaller
deployment context*: consistent with the 262K-versus-1M gap and with Command Code itself declining to
attach a score, but not shown either, since a provider can cap context on the same weights. The context
gap is a reason for doubt, not a refutation.

**Delivery verdict: UNKNOWN.** 10,000M tokens in a 30-day month is 3,858 tokens per second, every
second of the month. No page states a rate, a concurrency limit or a monthly ceiling for this lane,
and "no daily request limit" is not a token ceiling.

**Cost to enter.** The deal is available on every Command Code plan. The cheapest is Go at $1 a month
"+ processing fee" ([sources/free-lanes/commandcode-pricing.html](sources/free-lanes/commandcode-pricing.html)),
and a session needs "$1 of credits in your account to start". Free requests "don't draw down your
per-model allowances". The processing fee is not printed on any archived page, so whether the entry
cost stays at or under $10 is UNKNOWN, though it would take a fee above $8 to break it.

**What would settle it**, in order of cost:

1. The leaderboard naming the provider, checkpoint and reasoning effort behind its `ling-3-1-flash` row,
   or Command Code or Novita naming the checkpoint they serve in a way the leaderboard row can be joined
   to. Either settles identity without running anything.
2. A published rate limit or monthly ceiling for the free lane, or one metered month on it showing
   the tokens actually delivered. A month at or above 10,000M on an identity-matched endpoint would
   falsify the 2026-10-06 headline outright; a throttled month would close the candidate.
3. The deal still being live when the measurement is made. It is promotional, with no end date.

### 1.3 The other free lanes

All seven rows, with price, delivery ceiling, terms and an identity verdict, are in
[data/free-lanes.csv](data/free-lanes.csv). The four that matter:

| Lane | Published ceiling | Terms | Identity |
|---|---|---|---|
| Command Code Ling 3.1 Flash | "No daily request limit"; monthly UNKNOWN | "while it lasts" | UNKNOWN (above) |
| OpenRouter `inclusionai/ling-3.1-flash` at $0 | None for this ID. The documented free limits (20 RPM; 50 or 1,000 requests a day) are stated for IDs ending `:free`, and this ID does not | terms page not archived | UNKNOWN |
| NVIDIA build DeepSeek V4.1 Flash | "Up to 40 rpm", "10,000 requests per day", throttling allowed | Trial only: "without use of the API Service or Generated Content in production" | name matches the bar model; mode not established |
| Gemini API `gemini-3.8-flash` free tier | Visible only in AI Studio; "Specified rate limits are not guaranteed" | Free-tier content "Used to improve our products" | board scores High 40.9262, Medium 39.7740, Low 33.4548; mode not established |

NVIDIA's trial cannot be a coding plan because its terms bar production. Gemini's free tier publishes
no number to plan against. LongCat 2.5 Preview Free on OpenCode Go, Ling 3.0 Flash Sante (100 requests
a day) and Laguna S 2.1 on Command Code are free but have no scored slug on the payload.

### 1.4 The vendor sweep

[data/vendor-sweep.csv](data/vendor-sweep.csv) carries the cheapest cache-read price found on each
vendor page archived here and what a stated spend buys at a 100%-cache bound and at the 97% mix.

| Vendor and model | Cache read per 1M | 100% cache | 97% mix | Why it fails |
|---|---|---|---|---|
| StepFun Flash Plus ($9.99), `step-5-preview` (II 43.7343 by name) | $0.05 | 4,571M | 2,627M | Under half the target even at 100% cache; credit conversion is "approximately" |
| Volcengine Ark, DeepSeek V4.1 Flash idle period | CNY 0.02 = $0.002983 | 3,352M | 1,041M | Above zero; excludes a cache-storage charge |
| OpenCode Go / DeepSeek / Command Code, DeepSeek V4.1 Flash off-peak | $0.003 | 3,333M | 1,035M | The cheapest qualifying grid price |
| OpenRouter, DeepSeek V4.1 Flash `:batch` | $0.00336 | 2,976M | 1,292M | Batch only |
| Cloudflare Workers AI, GLM-5.3-Flash | $0.030 | 333M | 283M | Ten times the DeepSeek cache price |
| Moonshot, Kimi K3 | $0.30 | 33M | 23M | A hundred times |

The Volcengine price sits below $0.003 and so lowers nothing that matters: the bound moves from 3,333M
to 3,352M. The Muse Spark Contributor price ($0.002, 5,000M) and MiMo-V2.6-Flash ($0.0028, 3,571M) are
cheaper still and fail on capability. No priced lane in the sweep reaches 10,000M for $10 under any mix;
the open question is confined to $0 lanes.

---

## 2. The capability side

The leaderboard payload was re-fetched on 2026-10-07 and compared with the copy the 2026-10-06 pass
fetched the same day. The hash changed (`06e5272f...` to `d0750caf...`). Parsed with
`tools/parse-aa-models.py`, the old payload carries 680 scored slugs and the new one 681; the only
difference is the added `solar-pro-2` at II 6.9984. No slug was removed and no score changed. Neither
the hash change nor the new slug touches any lane in this market.

| SKU | Board | Other sources | Verdict |
|---|---|---|---|
| `muse-spark-1-3-contributor` | notFound; per-model page HTTP 404 | Command Code: "not yet scored"; Meta: `max` effort "not available on Contributor-tier models" | unscored |
| `muse-spark-1-2-contributor` | notFound; per-model page HTTP 404 | Command Code: "not yet scored" | unscored |
| `mimo-v2-5` | notFound; a different slug, `mimo-v2-5-0424`, is named "MiMo-V2.5" at 25.1743 | Command Code prints 25.2 for its MiMo V2.5 | unscored as sold; if it is the same model, 14 points below the bar |
| `mimo-v2-6-flash` | 37.8844 | - | below the bar |
| `ling-3-1-flash` | 41.0906 (reasoning, 1M context) | Command Code: "not yet scored" for its free Ling 3.1 Flash | scored checkpoint qualifies; served endpoint UNKNOWN |

The base `muse-spark-1-3` scores 48.0923 as "Muse Spark 1.3 (Max)". Meta's reasoning documentation says
the `max` effort is "Standard-tier muse-spark-1.3 only; not available on Contributor-tier models"
([sources/leaderboard/meta-reasoning.html](sources/leaderboard/meta-reasoning.html)), so that score
cannot transfer to a Contributor SKU even if the weights are shared. The next base configuration,
`muse-spark-1-3-xhigh`, scores 45.0733; whether a Contributor SKU at `xhigh` matches it was not tested.

An earlier worker found an Arena Elo and a Xiaomi-published SWE-Bench Pro figure for a model named
MiMo-V2.5. Both are on scales that do not convert to the Intelligence Index, the pages were not
archived here, and the figures are not published. Row-by-row sources are in
[data/capability-rows.csv](data/capability-rows.csv); every Intelligence Index above is reproduced by
[data/aa-lookup.csv](data/aa-lookup.csv), which the gate re-checks against the archived payload.

---

## 3. The OpenCode Go pool: what the vendor's public code meters

The docs page is byte-identical to the 2026-10-06 copy, and its sentence "Each model's monthly limit
below determines how its usage counts toward those allowances" still does not say how usage is
aggregated. The vendor's own console code does, for the path it publishes. It was read at commit
`ecc4916b5a9608c30e6dd58a67f2137b594407ca` (committed 2026-10-06T22:32:45Z) and archived under
[sources/opencode-go/github/](sources/opencode-go/github/).

- `LiteTable` holds `rollingUsage`, `weeklyUsage` and `monthlyUsage` with a unique index on workspace
  and user, and no model column (`packages/console/core/src/schema/billing.sql.ts:74-88`).
- Every billed Go request computes `const quotaCost = Math.round(cost * modelInfo.costMultiplier)` and
  adds it to all three counters whatever the model (`packages/console/app/src/routes/zen/util/handler.ts:1194`,
  with the additions at lines 1202, 1215 and 1227).
- The request gate compares those three counters with one set of limits and throws `GoUsageLimitError`
  (lines 911, 931, 951). No model ID reaches the comparison.
- The console's per-model display divides one limit by a model's multiplier (`return limit / multiplier`,
  `packages/console/app/src/lib/lite-usage.ts:67`), and apportions the one overall percentage across
  models by `quotaCost` so that the contributions sum to it (lines 42-55; the test at
  `packages/console/app/test/liteUsage.test.ts:23` asserts the sum).
- **But production may not run this code.** The handler first calls `proxyInference(...)` and returns its
  response if there is one (`handler.ts:112-123`). The proxy forwards new `oc_sk_` keys and migrated
  workspaces to `Resource.ConsoleMigration.inferenceUrl` (`inference-proxy.ts:46-53`), which in
  production is `https://opencode.ai/inference` (`infra/console.ts:224-229`), a separate service whose
  limiter and configuration are not in the repository. The deployed limit values and multipliers come
  from runtime resources (`ZEN_LIMITS`, `ZEN_MODELS1`) that are not published either.

| Reading | Public fallback code | Production |
|---|---|---|
| One shared pool | **Confirmed, weighted by model multiplier.** An unweighted dollar pool is refuted wherever multipliers differ. | Plausible; not established |
| Independent per-model budgets | **Refuted**: one counter per user, no model key | UNKNOWN |
| `min(shared dollar pool, per-model cap)` as two separate checks | **Refuted** as that implementation: there is one weighted check, and the per-model figure is a display conversion of it | UNKNOWN |

For a single model all three readings produce the same published limit, which is why the docs page
could never settle the question. They diverge for mixed use: the code's rule stops at
`sum(cost x multiplier) >= limit`, which can block a user whose raw dollar spend is well below the
published figure.

**Correction to the 2026-10-06 statement about displayed percentages.** That pass read issue #47547's
per-model percentages summing to exactly 100.0% at 37% of the dollars as "a distinct mechanism ... A
shared-pool model does not predict that; a meter that sums per-model percentages does"
([../2026-10-06/README.md](../2026-10-06/README.md) lines 127-129). In the public code the displayed
per-model percentages sum to the overall meter by construction, and a weighted shared counter reaches
100% before raw dollars do whenever some multiplier exceeds 1. A weighted shared pool predicts both
observations. The reporter's numbers were not re-fetched here and are not vouched for; what changes is
that they no longer argue against a pool.

The two Contributor SKUs each show a $60 limit on Go and $120 on Go Plus (grid lines 172-173 and
217-218). Under the public code they draw on the same counter, not $60 + $60. Both also require the
user's training consent (`packages/console/app/src/routes/zen/util/trainingConsent.ts`).

---

## 4. Z.ai

**Unchanged pages, no successor campaign.** `docs.z.ai/devpack/overview.md` and `teamplan.md` are
byte-identical to the 2026-10-06 copies ([data/drift-check.csv](data/drift-check.csv)). The docs
sitemap, llms.txt, the campaign notice and the GLM-5.3 guide announce no successor or extension; the
blog index returned HTTP 404. The campaign notice gives its period as "September 3, 2026 to October 7,
2026" in UTC+8; the exact end time is not published.

**The ceilings do not halve.** The overview states a standing rule, "During off-peak hours, model usage
is charged at 50% of the standard credit rate" (line 135), with peak hours "Monday to Friday,
14:00-18:00" UTC+8 (line 138): 20 of 168 hours a week. What ends on October 7 is the tip "From
September 25 to October 7, 2026, all-day usage will be charged at the off-peak rate" (line 142). The
page's own range definition says the maximum is all-off-peak use and the minimum all-peak use (lines
164-165), and its Lite GLM-5.3 range at 95% cache, 48-97M a week, is exactly that factor of two. After
the window:

| Schedule | Share of the page maximum |
|---|---|
| Off-peak only | 1.000 (unchanged) |
| Uniform 24x7 | 0.894 (= 0.5 / ((20 x 1.0 + 148 x 0.5) / 168)) |
| Peak only | 0.500 |

Only a user who works entirely in the Singapore weekday afternoon loses half.

**Prices.** The docs print only "Starting at just 18 USD per month". The subscribe-page bundle carries
monthly products tagged `version:"V3"` at Lite 18, Pro 80 and Max 168, and products tagged
`version:"V2"` with Pro `oldMoney:72` and Max `oldMoney:160`
([sources/zai/zai-subscribe-chunk-38aiay3p71_3a.js](sources/zai/zai-subscribe-chunk-38aiay3p71_3a.js)).
The July 30, 2026 notice says previous plans "are no longer sold to new users". The $72 and $160 in
[../2026-10-06/data/plan-economics.csv](../2026-10-06/data/plan-economics.csv) are therefore legacy
prices; the token ceilings on those rows are unaffected. The bundle values are static fallbacks; the
live checkout endpoint refused an anonymous request, so the price a new buyer pays is DOCUMENTED, not
verified. Team seat prices are not on the Team Plan page and stay UNKNOWN.

**Ceilings.** [data/zai-ceilings.csv](data/zai-ceilings.csv) recomputes every plan x model x schedule
from page inputs at the 97/2.5/0.5 mix. Selected rows, M tokens a month:

| Plan | Model | Off-peak only | Uniform 24x7 | Peak only | $/M uniform |
|---|---|---|---|---|---|
| Lite ($18) | GLM-5.3 | 446 | 399 | 223 | 0.0452 |
| Lite ($18) | GLM-5.3-Flash | 1,352 | 1,208 | 676 | 0.0149 |
| Pro ($80, V3 bundle) | GLM-5.3-Flash | 8,110 | 7,247 | 4,055 | 0.0110 |
| Max ($168, V3 bundle) | GLM-5.3-Flash | 18,923 | 16,910 | 9,462 | 0.0099 |

No Z.ai plan at or under $10 exists, so none of these bears on the headline.

---

## 5. Drift, and Command Code

**Drift.** DeepSeek's pricing page and Fenno's rate card came back byte-identical. Command Code's GOAT
page and xAI's Grok 4.7 page changed bytes but no published figure: the GOAT page gained three visible
strings, one of them "Cloud access: run the agent on a cloud machine against your GitHub repo.", and the
xAI page's visible text is identical. Details in [data/drift-check.csv](data/drift-check.csv).

**Command Code's over-quota rule is published.** The 2026-10-06 pass recorded it as UNKNOWN ("The GOAT
page publishes the limits and no billing rule"). Its own archive,
`2026-10-06/sources/commandcode-goat.html` line 66, says:

> "Past a limit, requests fall back to those credits - and without them, paid models pause until the
> window or cycle resets while the free models keep working."

The sentence before it says extra credits "bill at the model's regular rate". Today's copy carries both.

**Plan ladder** ([sources/free-lanes/commandcode-pricing-limits.html](sources/free-lanes/commandcode-pricing-limits.html)):

| Plan | Price/mo | Credits/mo |
|---|---|---|
| Go | $1 | $10 |
| GOAT | $10 | $70 |
| Pro | $20 | $80 |
| Provider | $15 | pay as you go |
| Max 10x | $100 | $150 |
| Max 20x | $200 | $300 |
| Team Pro | $40 | - |

The pricing page prints "+ processing fee" beside every plan without stating it. DeepSeek V4.1 Flash
carries a boosted allowance "with no end date": "$10 on the $1 Go plan (the plan's full pool), $60 on the
$10 GOAT plan and $70 on the $20 Pro plan", at the same off-peak tariff as DeepSeek's own page
($0.15 / $0.60 / $0.003). At the 97% mix the $1 Go plan's $10 buys 1,035M of DeepSeek V4.1 Flash, the
lowest dollars-per-token of any qualifying lane in this market before the unstated fee. It is one plan
of 1,035M, not 10,000M.

**DeepSeek's off-peak schedule** is on its pricing page: "Peak hours are 01:00 - 04:00 and 06:00 - 10:00
UTC, Monday through Friday, excluding Chinese public holidays. All other hours are off-peak, including
weekends and Chinese public holidays in full." Command Code labels the same window "01-04 & 06-10 UTC,
Mon-Fri (7h/day)".

---

## 6. Relays

The four-part standard of the 2026-10-06 pass (rate card, quantified reputation, documented delivery
ceiling, failure modes from named issue evidence) applied to seven rows in
[data/relay-evaluation.csv](data/relay-evaluation.csv): **0 of 6 operators pass all four**, and Sub2api
is software, not an operator.

- **R20 is now archived.** The independent instrument the 2026-10-06 pass cited without an archived copy
  (its R20, `FeiZhuLulu/real-api-pricing`) was fetched at commit
  `dce850df080582f2926a3376f97a2edf6020a508`. Its OpenCode Go rows carry the decision note quoted by the earlier
  pass, min(shared monthly pool $60, model usage $60) (`r20-adopted.csv` lines 106-107), and its traffic
  mix is 97/2.5/0.5, as quoted. Its Claude Max 5x and 20x rows at 19,625M and 39,250M
  are `claude-sonnet-5` rows derived from the Opus rows by a 2.5 list-price ratio, and the 20x row says
  in Chinese that it is not a measured Sonnet figure (line 255); the `claude-opus-5` rows read 7,850M and 15,700M. The
  per-token identity within one SKU still holds; the earlier pass's quotation dropped the SKU and the
  derived status.
- **Fenno.** "The platform has never recorded a single request on any model it lists" reads every model's
  `"window":"1h"`, `"data_status":"pending"`, `"request_count":0` as a lifetime total. It is a pending
  one-hour counter; lifetime traffic is UNKNOWN. The 5.33x price ratio stands: $0.05152 per 1M at the
  97% mix against DeepSeek's off-peak $0.00966.
- **Issue citations.** Of the Sub2api issues the earlier pass grouped as "Ban risk", #3624 is a feature
  request for fingerprint support, #3896 warns of a possible future ban, and #6134 reports a falling
  quota. Its "Silent substitution" heading cites #7503, which reports degradation and blames the TLS
  fingerprint; the one substitution report, #7360, attributes the routing upstream. None of the 13
  issues carries a label. Each is a row in [data/citation-audit.csv](data/citation-audit.csv).
- **Three new rate cards.** OpenRouter (public per-token catalog), Requesty ("A model that costs $10 per
  1M tokens from OpenAI costs $10.50 through Requesty", "5% markup") and NanoGPT (public price list) each
  pass test 1. None passes test 2 (the only countable figures are SDK and CLI repository stars, a
  software signal) or test 4 (the archived issues are client-side reports). Requesty's and NanoGPT's
  delivery ceilings were reported by an earlier worker from pages not archived here, so test 3 is not
  counted for them. All three are pay-as-you-go with no monthly allowance, so none could be ranked as a
  $10 plan whatever the tests said.

---

## 7. What is unreachable

- **Whether the $0 Ling endpoints serve the scored checkpoint.** Neither the leaderboard nor any vendor
  names the checkpoint, provider and effort level on both sides. Section 1.2 lists what would settle it.
- **The monthly delivery of any free lane.** No free lane publishes a token ceiling; delivery can only be
  measured, and this pass made no authenticated request.
- **OpenCode Go's production limiter.** The public code meters a weighted shared counter; production
  traffic is forwarded to a service whose source and configuration are not public. A maintainer
  statement, the inference service's limiter, or a controlled measurement across two models would settle
  it.
- **Logged-in prices.** Z.ai's live checkout price and Team seat prices, Command Code's processing fee,
  Gemini's free-tier rate limits and every relay's subscription price.
- **Not archived, so not published.** The Artificial Analysis `/models` page and per-model Ling page,
  LMArena, SWE-bench, Aider and LiveBench, Requesty's and NanoGPT's limits pages, Sub2api source files, and
  the Alibaba, Anthropic and GitHub Copilot pricing pages were read by earlier workers and left out to
  keep the archive under 10 MB. None of them was a counter-example. The full list is at the end of
  [references/references.md](references/references.md).

---

## 8. What would falsify this pass

- **A month on Command Code's or OpenRouter's free Ling 3.1 Flash delivering >=10,000M tokens, on an
  endpoint shown to be the scored checkpoint.** That falsifies the 2026-10-06 headline outright, and this
  pass says only that it is not ruled out.
- **A published rate limit on the free Ling lane below about 3,858 tokens per second sustained**, or the
  deal's withdrawal. Either closes the candidate and restores the negative result for every lane this
  pass can see.
- **The leaderboard naming a 1M-context endpoint, or a paid provider, as the one it measured.** That
  makes the identity of the 262K free endpoint doubtful enough to treat it as a different model.
- **A qualifying non-zero price below $0.001 per 1M.** A cached-read price below $0.001 would put $10 of
  raw credit above 10,000M under the 100%-cache bound; a blended rate below $0.001 would do it at the
  97% mix.
- **A score for either Contributor SKU or for `mimo-v2-5` at or above 39.4562.** The Contributor lanes
  reach 11,029M on the Go grid's advertised ceiling, subject to the shared-pool question in section 3.
- **OpenCode Go's production limiter turning out to be independent per model.** That reverses section 3's
  production verdict from plausible-pool to per-model.

---

## 9. What this pass changed in the repo

| Artefact | Change |
|---|---|
| `2026-10-07/` | This pass: eight CSVs, a merged fetch log of 87 attempts, 73 archived sources (9,266,537 bytes), references and method notes. |
| `2026-10-06/README.md` | A dated `SUPERSEDED 2026-10-07` blockquote beside each claim this pass finds wrong or unsupported; no superseded text was deleted or rewritten. |
| `2026-10-06/references/references.md` | Not edited: this pass corrects its entries through the README notes and [data/citation-audit.csv](data/citation-audit.csv). |
| `2026-10-06/data/plan-economics.csv` | A dated note appended to the `notes` cell of the Z.ai Pro and Max rows and the Command Code GOAT row; no number changed. |
| `README.md` (root) | The 2026-10-07 row added to the passes table. |
| Tooling | Earlier this session the integrity gate was split into `tools/gate/` by responsibility and five gate defects and four fetch-tool defects were fixed, each with a plant or test, as recorded in the git log; this pass changed nothing under `tools/` or `tests/`. |
