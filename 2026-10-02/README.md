# Coding-Subscription Market Pass — 2026-10-02 (metering methods and free-tier access)

**Research date: 2026-10-02 (UTC), 08:00–08:20.** 20 first-party sources fetched serially, one
request each, with per-source HTTP status, byte count, latency and SHA-256 in
[data/fetch-log.json](data/fetch-log.json); 20/20 returned 200. Databases:
[data/plan-economics.csv](data/plan-economics.csv) (22 plan rows),
[data/opencode-go-grid.csv](data/opencode-go-grid.csv) (78 rows, the full OpenCode Go and Go Plus
per-model grid),
[data/free-tier-access.csv](data/free-tier-access.csv) (free-tier catalogue sources evaluated),
[data/subscription-measurements.csv](data/subscription-measurements.csv) (third-party metered
allowance multipliers),
[data/method-sensitivity.csv](data/method-sensitivity.csv) (the $/M sensitivity table below, per
model). Numbered citations: [references/references.md](references/references.md). Raw snapshots:
[sources/](sources/). Reviews: [../docs/reviews-2026-10-02.md](../docs/reviews-2026-10-02.md).

---

## 1. A price per million tokens is not a measurement

A $/M figure is a division. Its divisor is a traffic mix: what fraction of the traffic was cache
reads, fresh input, and output. Vendors price those three token classes very differently, so the
same plan on the same vendor page yields figures that differ by **5.3x to 29.0x** depending on the
mix assumed. Across the 37 priced models on OpenCode Go the median spread is 13.6x.

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

## 3. First-party figures, re-read 2026-10-02

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

## 4. Third-party allowance measurements, and why they are not ranked here

[data/subscription-measurements.csv](data/subscription-measurements.csv) carries metered multipliers
from an external measurement project: a weekly usage meter is ticked on purpose and every call is
priced at the vendor's public API list price, with a floor and ceiling per step bracketed from the
vendor's own client logs. Published results are SuperGrok 190x ±21, Claude Max 20x 45.3x ±1.0,
ChatGPT Pro $100 10.25x ±0.03, Muse Code High Usage 9.3x ±0.4 (standard) and 114x ±12 (contributor
vs standard API price).

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
in its own step 3.

The audited standard traffic mix used in section 1 (97% cache read / 2.5% fresh input / 0.5%
output) is taken from that project's `conventions.json`, revised 2026-09-23 after a 14-sample
audit. It is a method input, quoted as such, and is not a measurement of any workload in this
pass.

---

## 5. Free-tier catalogue sources: what each contributes

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

## 6. Known gaps

- **No plan was subscribed to and no authenticated request was made.** Every allowance figure here
  is a published ceiling. Nothing in this pass is a metered result.
- **The traffic mix is a quoted convention**, not a measurement of this pass's own workload. The
  mix is stated beside every figure that depends on it, and the sensitivity table lets a reader
  substitute a measured one.
- **Fifteen of the twenty fetched sources carry no figure in this pass.** They are archived as the
  re-verification base: MiniMax, Anthropic, Cline, Aider, Kilo, Volcengine and the Artificial
  Analysis snapshot are cited in [references/](references/references.md) and carry no number in
  [data/plan-economics.csv](data/plan-economics.csv). A source list implying twenty mined sources
  when four were mined is its own form of overclaim.
- **OpenCode Go's monthly-vs-weekly request columns are irreconcilable** and the page does not say
  which is authoritative. Not guessed.
- **Z.ai's off-peak all-day window and the GLM-5.3-Flash campaign both expire 2026-10-07**, which
  would halve every GLM ceiling in section 3.
- **Team Plan seat price is unpublished** and is left UNKNOWN.
- **No latency or throughput claim is made for any vendor.** The probe's timings are one vantage
  point on one afternoon.
- **The relay and reseller universe is out of scope** for this pass and is not re-verified. Its
  exclusion from rankings is a policy set in the 2026-09-20 pass.

---

## 7. What would falsify this pass

- A first-party statement of OpenCode Go's monthly-versus-weekly convention. Either reading changes
  the plan's effective ceiling by 2x and the page supports both.
- Any reader recomputing [data/opencode-go-grid.csv](data/opencode-go-grid.csv) under a mix they
  measured. The grid and the parser are in the repo so this is a five-minute check, and CI fails if
  the parser stops regenerating the grid byte for byte from the archived page.
- The Z.ai off-peak window and Flash campaign lapsing on 2026-10-07.
- A metered run on any plan in section 3, which would replace a published ceiling with a
  measurement and make section 4 rankable.
