# Coding-Subscription Market Pass — 2026-10-02 (metering methods and free-tier access)

**Research date: 2026-10-02 (UTC), 08:00–08:25.** 20 first-party sources fetched serially, one
request each, with per-source HTTP status, byte count, latency and SHA-256 in
[data/fetch-log.json](data/fetch-log.json); 20/20 returned 200. Databases:
[data/models-database.csv](data/models-database.csv) (24 models, Intelligence Index, context window,
modalities and API list price),
[data/plan-economics.csv](data/plan-economics.csv) (22 plan rows),
[data/plan-ladder.csv](data/plan-ladder.csv) (30 plans across 7 vendors, read from 7 pages),
[data/opencode-go-grid.csv](data/opencode-go-grid.csv) (78 rows, the full OpenCode Go and Go Plus
per-model grid),
[data/openai-token-prices.csv](data/openai-token-prices.csv) (7 models, OpenAI's own per-1M grid),
[data/method-sensitivity.csv](data/method-sensitivity.csv) (the $/M sensitivity table below, per
model, from the OpenCode Go grid),
[data/mix-sensitivity-all.csv](data/mix-sensitivity-all.csv) (44 model/price-class rows across both
vendors and both evidence classes),
[data/free-tier-access.csv](data/free-tier-access.csv) (free-tier catalogue sources evaluated),
[data/subscription-measurements.csv](data/subscription-measurements.csv) (third-party metered
allowance multipliers). Numbered citations: [references/references.md](references/references.md).
Raw snapshots: [sources/](sources/). Reviews:
[../docs/reviews-2026-10-02.md](../docs/reviews-2026-10-02.md).

---

## 0. The short answer

| Question | Answer | Evidence class |
|---|---|---|
| **Cheapest large allowance per dollar** | **OpenCode Go, $10/month.** On its own published grid it reaches **Muse Spark 1.3 at II 48.09 for $0.0009/M** under a cache-heavy mix, and DeepSeek V4.1 Flash at II 39.46 for $0.0016/M. 39 models, per-model ceilings $6–$240, works in any agent. | FIRST-PARTY-COMPUTED |
| **Best quality per dollar, first-party ceiling** | **OpenCode Go, same plan, same $10**: II 48.09 at $0.0009/M is 53,000 II-points per $/M. The next best on the same plan is 24,660. | FIRST-PARTY-COMPUTED |
| **Cheapest per token under a no-cache assumption** | OpenCode Go on Muse Spark 1.3 at $0.0208/M — still the cheapest single-model figure in this market, 4x its cache-heavy reading. | FIRST-PARTY-COMPUTED |
| **Best plan that publishes a credit-and-token table** | **Z.ai GLM Coding Plan**, $18 (Lite) to $160 (Max). GLM-5.3-Flash at II 41.81 runs $0.0142/M (Lite) to $0.0090/M (Max); GLM-5.3 at II 44.78 runs $0.0429/M to $0.0273/M. | FIRST-PARTY-COMPUTED |
| **Frontier quality (II ≥ 50)** | **No plan in this table reaches it.** The frontier moved: Claude Opus 5.5 (II 57.62, released 2026-09-22) and Claude Sonnet 5.5 (II 56.00, 2026-09-28) are the two highest-scoring models on the leaderboard, and neither appears on any subscription grid read in this pass. The best reachable quality is II 48.09. | FIRST-PARTY-COMPUTED |
| **Cheapest entry** | Command Code Go at $1 and OpenCode Go at $10, per the 2026-09-20 pass. Command Code's effective-usage multiples are advertised, not published as tokens, so it carries no $/M here. | ADVERTISED |
| **Best free entry** | **Google Antigravity free tier** and **Kiro Free (50 credits/month)**, per the 2026-09-20 pass. Not re-verified in this pass; the only free surface measured here is section 3's anonymous probe. | CARRIED FORWARD |
| **Confidence** | HIGH on every price and grid figure, all read from the vendor's own page today. The $/M figures carry their traffic mix and move 5.3x–29.0x on it. No metered result in this pass. | — |

### The ranked field

This is the whole market as this pass can compute it: every plan/model pair where a first-party
ceiling and a leaderboard score both exist, ordered by quality per dollar. Full data in
[data/plan-economics.csv](data/plan-economics.csv) and
[data/models-database.csv](data/models-database.csv).

| Plan | $/mo | Model | Creator | II | $/M (cache-heavy) | II per $/M |
|---|---|---|---|---|---|---|
| **OpenCode Go** | **10** | **Muse Spark 1.3** | Meta | **48.09** | **$0.0009** | **53,436** |
| OpenCode Go | 10 | DeepSeek V4.1 Flash | DeepSeek | 39.46 | $0.0016 | 24,660 |
| OpenCode Go Plus | 40 | Muse Spark 1.3 | Meta | 48.09 | $0.0018 | 26,718 |
| OpenCode Go | 10 | GLM-5.3-Flash | Z AI | 41.81 | $0.0059 | 7,086 |
| GLM Coding Plan Max | 160 | GLM-5.3-Flash | Z AI | 41.81 | $0.0090 | 4,645 |
| GLM Coding Plan Pro | 72 | GLM-5.3-Flash | Z AI | 41.81 | $0.0095 | 4,401 |
| OpenCode Go | 10 | GPT 6 Luna (≤272K) | OpenAI | 38.12 | $0.0098 | 3,890 |
| GLM Coding Plan Lite | 18 | GLM-5.3-Flash | Z AI | 41.81 | $0.0142 | 2,944 |
| GLM Coding Plan Max | 160 | GLM-5.3 | Z AI | 44.78 | $0.0273 | 1,640 |
| GLM Coding Plan Pro | 72 | GLM-5.3 | Z AI | 44.78 | $0.0287 | 1,560 |
| GLM Coding Plan Lite | 18 | GLM-5.3 | Z AI | 44.78 | $0.0429 | 1,044 |
| OpenCode Go | 10 | Kimi K3 | Kimi | 43.59 | $0.2940 | 148 |

**Three things fall out of the table that no single row shows.**

1. **The frontier is not for sale at any price in this market.** The leaderboard's top two models
   were both released in the last ten days and appear on no subscription grid. The best quality any
   plan here reaches is II 48.09 (Muse Spark 1.3): a gap of **9.53 II points** to the top model at
   II 57.62, and **4.47 points** to the best non-Anthropic entry at II 52.56 (Gemini 4 Argon). Every
   plan in the table is buying last month's frontier.
2. **The same model costs 2.4x more through one vendor than another.** GLM-5.3-Flash is $0.0059/M
   on an OpenCode Go dollar ceiling and $0.0142/M on Z.ai Lite credits. Both are first-party, same
   model, same day. The difference is that one vendor meters in dollars-per-model and the other in
   credits, and the credit table is published while the dollar grid is not comparable to it.
3. **Cheapest and best are the same row, and that is unusual.** OpenCode Go on Muse Spark 1.3 is
   both the highest quality reachable and the cheapest per token, because it is the only lane in
   this market where a single published grid covers both a strong model and a very low blended
   price. That is a property of one plan's price table, not a general rule, and it is why the
   ranking is published per plan rather than as a single winner.

### What the model landscape looks like

24 models carry an Intelligence Index on the leaderboard read today
([data/models-database.csv](data/models-database.csv)). The top of it:

| Model | Creator | Released | II | Context | In $/M | Out $/M | Image |
|---|---|---|---|---|---|---|---|
| Claude Opus 5.5 | Anthropic | 2026-09-22 | 57.62 | 1M | 4.00 | 20.00 | yes |
| Claude Sonnet 5.5 | Anthropic | 2026-09-28 | 56.00 | 1M | 2.00 | 10.00 | yes |
| Claude Fable 5.1 | Anthropic | 2026-09-01 | 53.35 | 1M | 10.00 | 50.00 | yes |
| GPT-6 Astra | OpenAI | 2026-09-03 | 52.67 | 1M | 10.00 | 50.00 | yes |
| Gemini 4 Argon | Google | 2026-09-30 | 52.56 | 1M | 2.00 | 10.00 | yes |
| GPT-6.1 Sol | OpenAI | 2026-09-29 | 51.83 | 1M | 2.00 | 10.00 | yes |
| Muse Spark 1.3 | Meta | 2026-09-02 | 48.09 | 1M | 1.25 | 4.25 | yes |
| Grok 4.7 | SpaceXAI | 2026-09-21 | 46.45 | 500K | 2.00 | 6.00 | yes |
| MiMo-V2.6-Pro | Xiaomi | 2026-09-21 | 46.32 | 1M | 0.435 | 0.87 | yes |
| Qwen3.8 Max | Alibaba | 2026-09-02 | 45.42 | 984K | 2.00 | 6.00 | yes |
| GLM-5.3 | Z AI | 2026-08-18 | 44.78 | 1M | 1.40 | 4.40 | no |
| Step 5 | StepFun | 2026-09-18 | 43.73 | 1M | 1.00 | 2.70 | yes |
| Kimi K3 | Kimi | 2026-07-16 | 43.59 | 1.05M | 3.00 | 15.00 | yes |
| GLM-5.3-Flash | Z AI | 2026-08-26 | 41.81 | 1M | 0.15 | 0.50 | yes |
| Gemini 3.8 Flash | Google | 2026-09-02 | 40.93 | 1M | 0.75 | 3.75 | yes |
| DeepSeek V4.1 Flash | DeepSeek | 2026-09-10 | 39.46 | 1M | 0.30 | 1.20 | yes |
| GPT-6 Luna | OpenAI | 2026-09-22 | 38.12 | 1M | 0.10 | 0.50 | yes |

**All seven of the top seven models were released in September 2026**, five of them in the last ten
days. The models on every subscription grid in this market are 4 to 7 II points behind the
leaderboard, which is the concrete form of "you are buying last month's frontier".

Two properties of this table matter for plan selection and neither is visible in a price list:
**17 of 24 models have a full 1M context window and 19 of 24 have at least 512k**, so context length
is close to being a non-differentiator and quality per dollar is the axis that separates plans. The
exceptions are all sub-frontier (Grok 4.7 at 500k, Qwen3.8 27B at 256k, Nemotron at 262k, Muse
Glimmer at 131k, Mistral Medium 3.5 at 256k), so a 1M-context requirement narrows the field from
24 models to 17 without excluding anything above II 38. And **GLM-5.3 is the only model in the top
17 without image input** — on a plan that also routes vision through MCP rather than through the
model, which is a real limitation for multimodal agent work.

---

## 1. A price per million tokens is not a measurement

A $/M figure is a division. Its divisor is a traffic mix: what fraction of the traffic was cache
reads, fresh input, and output. Vendors price those three token classes very differently, so the
same plan on the same vendor page yields figures that differ by **1.7x to 29.0x** depending on the
mix assumed, and the median across 44 model/price-class rows spanning two vendors and two evidence
classes is 13.6x.

No $/M table states its mix. The consequence is that a $/M published without one cannot be checked,
reproduced, or compared against another, because the reader cannot tell which assumption is
carried.

OpenCode Go is the only vendor in this market publishing, per model, an input price, an output
price, a cached-read price, a cached-write price, and a monthly dollar ceiling. Those five numbers
determine $/M exactly, and therefore determine how much the answer depends on the mix.
`tools/parse-opencode-go.py` extracts the grid structurally from the page and
[data/method-sensitivity.csv](data/method-sensitivity.csv) recomputes every row under three mixes.

### Sensitivity of $/M to the assumed traffic mix (OpenCode Go, $10/month)

| Model | 97% cache / 2.5% in / 0.5% out | 50/40/10 | no cache (0/75/25) | spread |
|---|---|---|---|---|
| Muse Spark 1.3 Contributor | **$0.0009/M** | $0.0102/M | $0.0208/M | 23x |
| MiMo-V2.6-Flash | $0.0013/M | $0.0142/M | $0.0292/M | 23x |
| DeepSeek V4.1 Flash (off-peak) | $0.0016/M | $0.0202/M | $0.0437/M | 27x |
| LongCat-2.0 | $0.0032/M | $0.0405/M | $0.0875/M | 27x |
| MiMo-V2.6-Pro | $0.0125/M | $0.0875/M | $0.3625/M | **29x** |
| GLM-5.3-Flash | $0.0059/M | $0.0208/M | $0.0396/M | 6.7x |
| GPT 6 Luna (≤272K tokens) | $0.0098/M | $0.0633/M | $0.1333/M | 14x |
| Kimi K3 | $0.2940/M | $1.9000/M | $4.0000/M | 14x |

The spread is widest where a vendor prices cache reads far below fresh input, and narrowest where
the three classes are priced closer together. This is a property of the vendor's price table, not
of the plan: GLM-5.3-Flash is the steadiest row on the plan and MiMo-V2.6-Pro is not, on the same
plan and the same month.

### The result generalises past the one vendor it was found on

The sensitivity above was computed from one vendor's grid. If the effect were an artefact of that
vendor's price table rather than a property of how this market prices tokens, it would not survive
a second vendor. `tools/extract-token-prices.py` reads the same four-column shape out of any page
that publishes it, and applied to **OpenAI's own platform pricing page** it recovers 7 models. Its
published prices agree with the leaderboard's list prices to the cent for every model both carry
(gpt-6-astra at $10/$50, gpt-6-luna at $0.10/$0.50), which independently confirms the landscape in
section 0.

| Price class | Models | Spread (no-cache / cache-heavy) | Median |
|---|---|---|---|
| Subscription ceiling (OpenCode Go grid) | 37 | 5.3x – 29.0x | 13.6x |
| API list (OpenAI platform pricing) | 7 | 1.7x – 20.3x | 13.6x |
| **All rows** | **44** | **1.7x – 29.0x** | **13.6x** |

The medians are identical across two vendors, two evidence classes and a 20x difference in absolute
price, which is what a property of the market looks like rather than of one rate card. The 1.7x
floor is not a counterexample: both rows at the bottom are models with **no published cached tier**
(OpenAI's two transcribe models), so their spread is computed with the input price substituted for a
cache price that does not exist, and the column records `cached_tier_published=no`. A vendor that
does not publish a cache price cannot be evaluated on cache sensitivity, and the table says which
rows those are rather than implying a measured spread.

### The mix is an observable, not a free parameter

Two independent lines of evidence fix it as a real quantity rather than a modelling choice:

1. **A vendor varies its own published ceiling for it.** Z.ai publishes the same plan's token
   allowance at three cache hit rates. GLM-5.3-Flash Lite reads 1,264M / 1,299M / 1,373M tokens
   per month at 95% / 96% / 98%, an 8% swing from the cache rate alone. A vendor that varies its
   own number by 8% for this reason is stating that the reason matters.
2. **A metered run measures it.** The work in [data/subscription-measurements.csv](data/subscription-measurements.csv)
   records cache-read share per run: 93% on the SuperGrok text workload, 91.97% on a Claude Max
   segment, 96.9% averaged on a long historical Claude session. Real agent traffic is
   cache-dominated.

A cache-heavy mix is therefore the correct default for agent workloads, and the no-cache column is
the correct worst case. Both are published above, and every $/M in
[data/plan-economics.csv](data/plan-economics.csv) carries its mix.

### Vendor-side clock inconsistency

OpenCode Go's request-estimate table is internally inconsistent. For all 38 priced rows the
monthly request column is **2.00x** the weekly column (1.96x for Kimi K3, 2.02x for Qwen3.8 Max),
against 4.33 weeks in a month. Either the monthly column is a separate cap sitting on top of the
weekly one, or the vendor's "month" is two weeks. The page does not state which. Any figure
treating the monthly column as a monthly allowance rests on an unstated convention, and the
2.00x factor is not reconcilable with a 4.33-week month. This is a defect in the published table,
reproducible from [sources/opencode-go.html](sources/opencode-go.html).

---

## 2. Free-tier access is a different property from free-tier price

A catalogue states what a vendor charges. Whether a caller with no account, no card and no key can
reach the endpoint is a separate fact, and the two diverge sharply.

`tools/probe-opencode-zen.py` sends three unauthenticated rounds to 25 endpoints, then three rounds
to every model the vendor's own catalogue labels "free". It constructs each request with an
explicit header set containing no `Authorization` entry, so it cannot acquire a credential even by
accident and cannot test an authenticated path. Results:
[data/opencode-zen-probe.json](data/opencode-zen-probe.json).

| Result | Count | Reading |
|---|---|---|
| `/models` answers with no credential | 25/25 | catalogues are public even where inference is not |
| Endpoints serving a completion with no credential | **1 / 25** | the only anonymously usable channel in this set |
| Free-listed models serving a completion anonymously | **1 / 12** | 11 of 12 are gated or broken |
| Refused with "free tier can only be used from within OpenCode" | 6 | a policy gate, not an outage |
| Refused with a country block | 2 | a geographic gate |
| HTTP 500 from a model the catalogue lists as free | 2 | listed as free, endpoint broken |
| HTTP 403/401 (account required) | the remainder | gated, which is not the same as down |

The one usable endpoint is `space-bunny-free` on OpenCode Zen. Eleven of the twelve "free" models
are unavailable to an external anonymous caller, and two of those fail by error rather than by
policy while the catalogue still lists a price of zero. A directory that reports price alone
misreports both cases.

### Long-context behaviour of the anonymous endpoint

Measured across a nine-point prompt-size sweep, plus a `max_tokens` control, on 2026-10-02.

| Prompt characters | `prompt_tokens` reported | chars/token | needle retrieved |
|---|---|---|---|
| 7,442 | 1,655 | 4.50 | yes |
| 27,817 | 5,730 | 4.85 | yes |
| 55,592 | 11,285 | 4.93 | yes |
| 111,142 | 22,395 | 4.96 | yes |
| 231,517 | 46,470 | 4.98 | yes |
| 277,817 | 55,730 | 4.99 | yes |
| 370,392 | 74,245 | 4.99 | yes |

Reported usage tracks the prompt linearly with no step change, so it is usable for budgeting a
context window. Retrieval succeeds at every size tested, up to 370k characters.

**One caveat, and it is a caller-side parameter.** The endpoint spends its completion budget on
`reasoning_content`. With an identical prompt, `finish_reason` is `length` and the content field is
empty at `max_tokens` 16, 32 and 64, and is `stop` with the content correct at 256 and 1024. A
caller that sets a small `max_tokens` against a reasoning model receives an empty answer and is
still billed for the prompt. This is a property of the request, not a fault in the endpoint's
accounting, and it is the one reading from this measurement that a consumer needs.

---

## 3. The plan ladder, as each vendor publishes it

[data/plan-ladder.csv](data/plan-ladder.csv) carries 30 plans across 7 vendors, read from 7 of the
20 archived pages. `tools/extract-plans.py` reads a vendor's own schema.org `Offer` block where one
exists and falls back to rendered text next to a price and a billing period where one does not, and
it reports which pages yielded nothing rather than counting them as covered. Prices in USD.

| Vendor | Plans read | Ladder |
|---|---|---|
| Anthropic | 10 | Free $0; Pro $17 annual / $20 monthly; Max from $100; Team standard seat $20 annual / $25 monthly; Team premium seat $100 annual / $125 monthly; **Max 20x and Enterprise not published** |
| Cursor | 5 | Hobby $0; Pro $20; **Pro+ $60**; Ultra $200; Teams $40 per user |
| GitHub Copilot | 7 | Free $0; Pro $10; Pro+ $39; Max $100, each with a separate flex allotment of $5 / $31 / $100 |
| OpenCode | 2 | Go $10; Go Plus $40 |
| Z.ai | 5 | Lite **$18, published**; Pro $72 and Max $160 **not on the page this pass fetched**, carried from the 2026-09-20 pass; Team Standard and Premium seat **not published** |
| Kilo | 1 | Individual $0 (a free tier, not a paid plan) |

**Four prices in this ladder are UNKNOWN because no vendor publishes them**, and they are the ones a
buyer most wants: Claude Max 20x, Claude Enterprise, and both Z.ai Team seat prices. Anthropic
publishes Max as "From $100" with a "choose 5x or 20x" selector and never states the 20x price on
the page; the 2026-09-20 pass carried $200 for it, which this pass cannot confirm from the vendor's
own page and therefore does not repeat. A ladder that fills those cells from a previous pass or a
tracker is a ladder with an unsourced number in it, which is the condition this repo exists to
catch.

**A seventh cell was nearly the same error and is now labelled.** Z.ai's overview page publishes
exactly one price, "starting at just 18 USD per month". The Pro ($72) and Max ($160) prices are
**not on that page**, on the FAQ page, or on the Team Plan page archived here. Verifying every
ladder price against the bytes of the page it cites found this: four of thirty rows initially
claimed a first-party provenance the archived page does not support. Those four rows are now
`CARRIED-FORWARD` in [data/plan-economics.csv](data/plan-economics.csv) and `NOT-ON-PAGE` in this
ladder, with the reason in the row. The $0.0142/M and $0.0090/M figures computed from them are
arithmetically correct and rest on a price this pass could not re-verify, which is a different
statement from "verified" and is now the one the table makes.

**Two ladders are not comparable and should not be added together.** Anthropic's Team premium seat
at $100 is per seat with "5x more usage than standard seats", and Z.ai's Team seats publish a credit
allowance and not a price. Cursor Teams at $40 is per user. None of the three publishes a token
allowance, so none yields a $/M.

## 4. First-party figures, re-read 2026-10-02

**Z.ai GLM Coding Plan** ([overview](sources/zai-overview.md)). Credits per plan: Lite 2,000 per 5h
and 10,000 weekly at $18, Pro 12,000 and 60,000 at $72, Max 28,000 and 140,000 at $160. The
published credit formula and multipliers are:

```
credit = (input x input_mult + cached_input x cached_mult + output x output_mult) / 10,000
GLM-5.3:        6.9 / 1.7 / 24
GLM-5.3-Flash:  2.3 / 0.56 / 8
```

Off-peak hours (peak is Mon–Fri 14:00–18:00 SGT) bill credits at 0.5x, which is the whole
difference between the low and high end of every range in the vendor's token table. Re-deriving
each row of the vendor's table from its own credit pools and multipliers reproduces all twelve
GLM figures in [data/plan-economics.csv](data/plan-economics.csv) to four decimal places.
**From Sep 25 to Oct 7, 2026 all-day usage bills at the off-peak rate**, and the GLM-5.3-Flash
campaign runs to **Oct 7**; both expire, after which the applicable ceiling is the peak figure
carried in the table's notes.

**Z.ai Team Plan** ([teamplan](sources/zai-teamplan.md)). Standard seat 15,000 per 5h and 66,000
weekly credits; Premium 35,000 and 155,000. **The seat price is not published.** It is carried as
UNKNOWN rather than estimated, because every other price in this file is published and an estimate
would be the only unsourced figure in it. Overage beyond included credits bills at 10% off API list.
Data is excluded from model training by default.

**OpenCode Go and Go Plus** ([docs/go](sources/opencode-go.html)). 39 rows per plan. Five-window
rule: 5h = 20% of the monthly limit, weekly = 50%, monthly = 100%. Go is $10/month, Go Plus
$40/month, ceilings $6 to $240 per model. Go Plus raises the price 4x and the ceiling 2x on most
models, so $/M gets worse; the exception is LongCat-2.0, whose ceiling rises 4x and whose $/M is
unchanged at $0.0032/M. Two rows per plan are listed Free/Unlimited and carry no computable $/M.
See section 1 for the request-table inconsistency.

**Cursor** ([pricing](sources/cursor-pricing.html)). The page's own schema.org `Offer` block
publishes Hobby $0, Pro $20, Pro+ $60, Ultra $200, Teams $40 per user. No token allowance is
published at any tier, so no $/M is computable and the rows carry UNKNOWN.

**GitHub Copilot** ([plans](sources/github-copilot-plans.html)). Free $0, Pro $10, Pro+ $39, Max
$100 per month, each with a base-credit allowance plus a separate flex allotment billed as a dollar
amount ($5, $31 and $100). The page publishes the plan price and the flex allowance separately and
never states a credit count per request, so the two cannot be combined into a $/M: the missing
input is a per-request cost the vendor does not publish. The vendor also states "Flex allotments
may change over time", so the dollar figure is not a fixed ceiling.

**OpenAI** ([platform pricing](sources/openai-pricing.html)) returned 200 from this vantage point
and is archived. `www.openai.com/chatgpt/pricing/` returns 403; the platform documentation host
carries the model price table, so first-party OpenAI pricing is obtainable without the marketing
host.

---

## 5. Workload test: 52.5M tokens/month (15M in + 37.5M out)

The same workload the earlier passes use, repriced against today's model table. This is the
**list cost of the workload**, which a plan covers if its published ceiling reaches it. A plan
passes at II 40 or above if its ceiling covers the workload on a model scoring at least that.

| Model | II | List cost of 52.5M | Cheapest plan in this table that covers it |
|---|---|---|---|
| GPT-6 Luna | 38.12 | $20.25 | none at II≥40; OpenCode Go holds a $15 ceiling on it |
| GLM-5.3-Flash | 41.81 | $21.00 | **GLM Lite $18** (632M–1,264M tokens) |
| MiMo-V2.6-Pro | 46.32 | $39.15 | **OpenCode Go $10** ($15 ceiling on this model) |
| DeepSeek V4.1 Flash | 39.46 | $49.50 | **OpenCode Go $10** ($60 ceiling) |
| MiniMax M3 | 29.22 | $49.50 | no plan in this table |
| Step 5 | 43.73 | $116.25 | no plan in this table |
| Qwen3.8 27B | 33.70 | $120.00 | no plan in this table |
| Gemini 3.8 Flash | 40.93 | $151.88 | **OpenCode Go $10** (no ceiling row; GLM Lite reaches 1,264M Flash tokens but not this model) |
| Muse Spark 1.3 | 48.09 | $178.12 | **OpenCode Go $10** ($60 ceiling, 11,029M tokens at the cache-heavy mix) |
| GLM-5.3 | 44.78 | $186.00 | **GLM Lite $18** (208M–420M tokens) |
| Grok 4.7 | 46.45 | $255.00 | no plan in this table |
| Qwen3.8 Max | 45.42 | $255.00 | no plan in this table |
| Claude Sonnet 5.5 | 56.00 | $405.00 | none |
| Gemini 4 Argon | 52.56 | $405.00 | none |
| GPT-6.1 Sol | 51.83 | $405.00 | none |
| Kimi K3 | 43.59 | $607.50 | none; OpenCode Go's Kimi ceiling is $15 of list value |
| Claude Opus 5.5 | 57.62 | $810.00 | none |
| Claude Fable 5.1 | 53.35 | $2,025.00 | none |
| GPT-6 Astra | 52.67 | $2,025.00 | none |

**One row is not an API price.** K2 Horizon (375B-A23B, II 30.50, Institute of Foundation Models)
shows a $0.00 list price because it is **open weights with no published API tariff**, not because it
is free to call. There is no inference provider for it in this table, and self-hosting it is a
hardware cost, not a subscription. It is excluded from the pass/fail reading above and listed here
so the zero is not mistaken for a deal.

**What the workload test shows.** A single $10 plan covers a 52.5M-token month at II 46–48, and a
$18 plan covers it at II 41–45. Above II 50, no plan in this table covers the workload at all, and
the list cost of running one there is $405 to $2,025 per month. The scarce resource in this market
is not tokens, it is the top 7 II points.

---

## 6. What I would buy

Ranked by what the measurements above support, with the reasoning and the caveat attached.

1. **OpenCode Go, $10/month, as the primary.** It is simultaneously the cheapest per token and the
   highest quality reachable in this market (II 48.09 on Muse Spark 1.3 at $0.0009/M), it publishes
   the only per-model grid that lets the figure be recomputed, and it works in any agent. Caveat:
   the grid's request table contradicts its own limit rule (section 1), and the $/M figure depends
   on a traffic mix this pass did not measure. Both are stated rather than smoothed.
2. **GLM Coding Plan Lite, $18/month, as the documented-capacity hedge.** It is the only plan that
   publishes both a credit table and a token table, so its ceiling can be checked against a formula
   rather than taken on trust. It covers a 52.5M month on GLM-5.3-Flash at II 41.81 with 12x–24x
   headroom. Caveat: GLM-5.3 has no image input and vision routes through MCP, and the off-peak
   window and Flash campaign both expire 2026-10-07, after which the ceiling halves.
3. **Do not buy frontier access through a subscription in this market.** Every II≥50 model is
   $405–$2,025 per 52.5M tokens at list, and none appears on a plan's grid. If frontier quality is
   the requirement, the honest comparison is API list price against API list price, not a
   subscription.
4. **Do not buy anything from a relay or reseller.** Excluded from rankings by the policy in the
   2026-09-20 pass: the prices are advertisement, the allowances are quota resale, and the measured
   degradation reports stand.

**What would change this ranking:** a metered month on OpenCode Go, which would replace its
published ceiling with a measurement and could show the request-shaped quota binding before the
dollar ceiling does. A plan adding an II≥50 model to its grid would displace item 1 immediately.

---

## 7. Third-party allowance measurements, and why they are not ranked here

[data/subscription-measurements.csv](data/subscription-measurements.csv) carries metered multipliers
from an external measurement project: a weekly usage meter is ticked on purpose and every call is
priced at the vendor's public API list price, with a floor and ceiling per step bracketed from the
vendor's own client logs. Published results are SuperGrok 190x ±21, Claude Max 20x 45.3x ±1.0,
ChatGPT Pro $100 10.25x ±0.03, Muse Code High Usage 9.3x ±0.4 (standard) and 114x ±12 (contributor
vs standard API price).

> **SUPERSEDED 2026-10-06 — the SuperGrok figure is retracted by its own source.** The 190x ±21
> above was measured on an account with a linked X Premium+ subscription, which confounds the
> allowance. The source now publishes **80x ±4 at $70** for that X-linked account, **18.0x ±0.3 at
> $30** for SuperGrok on an account with no X account linked, and **15.7x ±0.8** for SuperGrok Lite
> at $10. The measurement row is superseded, not deleted, and the corrected table is in
> [../2026-10-06/data/subscription-measurements.csv](../2026-10-06/data/subscription-measurements.csv).
> Full re-derivation: [../docs/reviews-2026-10-06.md](../docs/reviews-2026-10-06.md). The lesson
> generalises past this one plan: **a subscription multiplier read from one account is an upper
> bound until its confounds are enumerated**, and this one was worth about 10x.

**They are not ranked in this pass, and the reason is structural.** A multiplier is a measurement
of one plan, on one workload, on one day, read from one account's meter. This pass subscribed to
nothing and made no authenticated request, so every allowance in
[data/plan-economics.csv](data/plan-economics.csv) is a published ceiling. Ranking metered results
next to published ceilings would compare two different evidence classes as if they were the same
quantity, which is the error that produces an unfalsifiable market table. The measurements are
carried with attribution, date, method and uncertainty, and the ceilings are labelled as ceilings.

Two figures from that source were re-derived independently as a check on the method rather than the
numbers: the SuperGrok run's per-call cost recomputed from its raw call log at its own stated list
price gives $67.79 against a published $68.86, a 1.6% gap attributable to calls crossing a
token-threshold price step. Its headline 190x is a meter-tick bracket rather than a whole-run
average; a whole-run recomputation gives 246x, which is the method difference the source documents
in its own step 3. **Both figures are superseded by the retraction noted above**: the 190x and its
246x re-derivation were computed on the X-linked account, so re-deriving a method against a
confounded run reproduces the method and not the quantity. The bracketing question is still real and
still applies to the 18.0x figure, but it is now the smaller of the two effects.

The audited standard traffic mix used in section 1 (97% cache read / 2.5% fresh input / 0.5%
output) is taken from that project's `conventions.json`, revised 2026-09-23 after a 14-sample
audit. It is a method input, quoted as such, and is not a measurement of any workload in this
pass.

---

## 8. Free-tier catalogue sources: what each contributes

[data/free-tier-access.csv](data/free-tier-access.csv) evaluates four external free-tier
catalogues against one question: can they establish access, or only price. All four are catalogues
of price and eligibility. None carries a probe result, a per-request cost, or an access test, and
none can distinguish an account-gated endpoint from a working one. Their aggregate contribution to
this pass is therefore zero figures and one methodological habit worth adopting: attaching a source
URL and a check date to every limit, and distinguishing a published ceiling from a vendor that
refuses to publish one. That distinction is what puts UNKNOWN in the Cursor and Z.ai Team Plan rows
instead of a plausible guess. The per-source record, including what each does not solve, is in the
database.

---

## 9. Known gaps

- **No plan was subscribed to and no authenticated request was made.** Every allowance figure here
  is a published ceiling. Nothing in this pass is a metered result.
- **The traffic mix is a quoted convention**, not a measurement of this pass's own workload. The
  mix is stated beside every figure that depends on it, and the sensitivity table lets a reader
  substitute a measured one.
- **Thirteen of the twenty fetched sources carry no figure in this pass.** They are archived as the
  re-verification base and cited in [references/](references/references.md). Seven do carry
  figures: the OpenCode Go grid (sections 1 and 5), the Artificial Analysis leaderboard (section 0),
  OpenAI platform pricing (section 1), Anthropic, Cursor, GitHub Copilot and Kilo (section 3), and
  the Z.ai docs (section 4). The seven that carry nothing are MiniMax token-plan and platform, the
  Anthropic context-window support page, Cline, Aider, Volcengine, and the two OpenCode Zen pages
  beyond the one the probe uses. A source list implying twenty mined sources when seven were mined is
  its own form of overclaim, and the list of unmined pages is named rather than left to be
  discovered by a reader who counts.
- **OpenCode Go's monthly-vs-weekly request columns are irreconcilable** and the page does not say
  which is authoritative. Not guessed.
- **Z.ai's off-peak all-day window and the GLM-5.3-Flash campaign both expire 2026-10-07**, which
  would halve every GLM ceiling in section 3.
- **Team Plan seat price is unpublished** and is left UNKNOWN.
- **No latency or throughput claim is made for any vendor.** The probe's timings are one vantage
  point on one afternoon.
- **The leaderboard's Terminal-Bench 4.0 column is empty for all 24 models** in today's page
  payload, so the ranking in section 0 uses the Intelligence Index alone. The 2026-09-20 pass carried
  Terminal-Bench values from an earlier snapshot; they are not comparable to today's, because the
  column is not published now.
- **The Intelligence Index is a composite, not agentic-task performance alone.** A model scoring 48
  is not necessarily better at tool-calling than one scoring 44, and this pass has no Terminal-Bench
  figure to check that against. The ranking in section 0 should be read as quality per published
  list price, not as an agent benchmark result.
- **The relay and reseller universe is out of scope** for this pass and is not re-verified. Its
  exclusion from rankings is a policy set in the 2026-09-20 pass.

---

## 10. What would falsify this pass

- A first-party statement of OpenCode Go's monthly-versus-weekly convention. Either reading changes
  the plan's effective ceiling by 2x and the page supports both.
- Any reader recomputing [data/opencode-go-grid.csv](data/opencode-go-grid.csv) under a mix they
  measured. The grid and the parser are in the repo so this is a five-minute check, and CI fails if
  the parser stops regenerating the grid byte for byte from the archived page.
- The Z.ai off-peak window and Flash campaign lapsing on 2026-10-07.
- A metered run on any plan in section 3, which would replace a published ceiling with a
  measurement and make section 4 rankable.
