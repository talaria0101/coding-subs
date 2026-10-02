# 2026-10-02 — what a $/M token price actually depends on, and what the free tier really gives

**Research date 2026-10-02 (UTC, read from the machine clock).** 20 first-party sources fetched
serially, one request each, logged with per-source http status, byte count, latency and SHA-256 in
[data/fetch-log.json](data/fetch-log.json). 20/20 returned HTTP 200. The bytes are in
[sources/](sources/).

Databases: [data/plan-economics.csv](data/plan-economics.csv) (22 rows),
[data/opencode-go-grid.csv](data/opencode-go-grid.csv) (78 rows parsed from one vendor page, 39 per
plan, of which 2 per plan are listed as Free/Unlimited and carry no computable $/M),
[data/opencode-zen-probe.json](data/opencode-zen-probe.json) (a live measurement).
Citations: [references/references.md](references/references.md).
Reviews: [../docs/reviews-2026-10-02.md](../docs/reviews-2026-10-02.md).

## The finding

Every price-per-token figure published in this repo, by every pass, including this one's
predecessor, is a number with a hidden assumption inside it. The assumption is the **traffic mix**:
what fraction of the tokens were cache reads, fresh input, and output. Vendors price those three
classes very differently, so that fraction moves the figure by between **5x and 29x** depending on
the model, with a median of 14x across the 37 priced models on the plan below. No table stated it.

I did not find this by reading. I parsed the OpenCode Go price grid out of the vendor's own page
and recomputed it under three mixes. The vendor publishes, per model, a token price for input,
output, cached read and cached write, plus a monthly dollar ceiling. That is enough to compute
$/M exactly, and enough to show what the answer depends on:

| Model (OpenCode Go, $10/mo) | 97% cache / 2.5% in / 0.5% out | 50/40/10 | no cache (0/75/25) | spread |
|---|---|---|---|---|
| Muse Spark 1.3 Contributor | **$0.0009/M** | $0.0102/M | $0.0208/M | 23x |
| MiMo-V2.6-Flash | $0.0013/M | $0.0142/M | $0.0292/M | 23x |
| DeepSeek V4.1 Flash (off-peak) | $0.0016/M | $0.0202/M | $0.0437/M | 27x |
| LongCat-2.0 | $0.0032/M | $0.0405/M | $0.0875/M | 27x |
| MiMo-V2.6-Pro | $0.0125/M | $0.0875/M | $0.3625/M | **29x** |
| GLM-5.3-Flash | $0.0059/M | $0.0208/M | $0.0396/M | 6.7x |
| GPT 6 Luna (≤272K) | $0.0098/M | $0.0633/M | $0.1333/M | 14x |
| Kimi K3 | $0.2940/M | $1.9000/M | $4.0000/M | 14x |

Same page, same method, same day. Only the assumed mix changes. The spread is widest where a vendor
prices cache reads far below fresh input and narrowest where the three classes are priced closer
together, which is why GLM-5.3-Flash is the steadiest row on the plan and MiMo-V2.6-Pro is not.
Across the 37 priced models the ratio runs 5.3x to 29.0x, median 13.6x.

**This settles a dispute the previous pass had backwards.** The 2026-10-02 pass in the fork
published OpenCode Go at $0.0013/M, then declared that figure wrong and replaced it with
$0.0208/M, describing the change as a 16x correction. Both numbers are the same method on the same
vendor page. $0.0013/M is the cache-heavy mix; $0.0208/M is the no-cache mix. Neither is a
correction of the other. What the correction actually did was pick one hidden assumption, present
it as the truth, and describe the other as an error, which is how a market ends up with a number
nobody can reproduce. The full 78-row grid in
[data/opencode-go-grid.csv](data/opencode-go-grid.csv) lets a reader recompute under any mix.

The mix is not a free choice either. Z.ai's own table proves it: it publishes the same plan's token
allowance at **three different cache hit rates** (95%, 96%, 98%) and the GLM-5.3-Flash Lite figure
moves 1,264M to 1,373M tokens across that range. A vendor that varies its own published ceiling by
8% for the cache rate is telling you the rate is the sensitive variable.

## What I kept from the fork, and what I did not

I read the fork's 2026-10-02 pass and its unmerged 2026-10-03 branch in full, then tested the
claims rather than adopting them.

**Kept, because I reproduced it independently.** Its anonymous-access probe is the most useful
thing in the fork. I re-ran its own script today: 25 endpoints, three rounds, no credential. The
result matches on all 25 (the only differences are three endpoints moving 403 to 401 behind a CDN).
The headline is real: **one** endpoint in this market serves a completion to a caller with no
account, no card and no key, and it is `space-bunny-free` on OpenCode Zen. Of the 12 models the
vendor's own catalogue labels "free", 11 refuse an external anonymous caller.

**Refuted.** The fork published a "transparency defect" finding: the endpoint "billed 89,063 prompt
tokens for a ~400,000-character prompt it had evidently read, while returning an empty
completion", and concluded that an agent trusting reported usage "will be wrong about both the cost
and the available headroom."

That is an artifact of the probe's own `max_tokens=10`, not a property of the endpoint. Evidence,
all from today, all in [data/opencode-zen-probe.json](data/opencode-zen-probe.json):

- With the identical 27k-character prompt, `finish_reason` is `length` and content is empty at
  `max_tokens` 16, 32 and 64, and is `stop` with the needle correctly retrieved at 256 and 1024.
- The model spends the whole completion budget on `reasoning_content`; it is not hiding anything,
  it is reasoning past the cap.
- Billing is a clean ~5 chars/token with no step change: 1,655 tokens at 7.4k chars, 5,730 at
  27.8k, 11,285 at 55.6k, 22,395 at 111k, 46,470 at 231k, 74,245 at 370k. On the fork's own
  400,036-char prompt I measured 97,320 tokens, which is 4.11 chars/token, not the ~2.2 that
  implied under-billing.
- The control that shows the probe can detect retrieval at all: the same model returns a correct
  diff for a real bug fix (`return a-b` → `return a+b`) and retrieves a needle at 8k, 28k, 55k,
  111k, 231k, 278k and 370k characters.

The one real observation, which I am keeping, is a genuine caveat for a caller: **a small
`max_tokens` on a reasoning model returns an empty answer while still billing for the prompt.**
That is worth knowing. It is not the defect that was published.

**Corrected in the fork's own data.** Its cost table has rows that do not match the file it cites.
Claude Pro is published at 2,300M–3,054M tokens / $0.0087-M; the cited `adopted.csv` row for
`claude-opus-5.5` at $20 is 3,054,000,000 / $0.0065488. Claude Max 20x is published at
3,054M–3,810M / $0.0655-M; the cited rows for that plan are 6,690,000,000 ($0.0299), 31,538,000,000
($0.0063) and 5,052,000,000 ($0.0396) — none of which is the published figure. The published
Max figure is roughly 2x the value it carries. Its MiniMax and GLM rows check out; I re-derived all
twelve GLM rows from the vendor's credit table and they match to the digit.

**Kept as tooling.** The serial fetcher with a per-source log, and the structural HTML table
parser are worth carrying. The tag-splitting extraction the fork shipped for the same page lost 21
of 37 rows per table and shifted columns on rows with a `-` cached-write cell, which is how a
16x error gets in. Mine parses `<table>/<tr>/<th>/<td>` and recovers all 78.

## First-party figures, re-read today

**Z.ai GLM Coding Plan** ([docs.z.ai/devpack/overview.md](sources/zai-overview.md), sha256 matches
the fork's independent 10-03 fetch, so the page did not change between the two fetches). Credits
per plan are unchanged: Lite 2,000 per 5h / 10,000 weekly at $18, Pro 12,000 / 60,000 at $72, Max
28,000 / 140,000 at $160. The credit formula is published and is worth reading, because it is the
whole answer to how the token table is built:

```
credit = (input x input_mult + cached_input x cached_mult + output x output_mult) / 10,000
GLM-5.3:        6.9 / 1.7 / 24
GLM-5.3-Flash:  2.3 / 0.56 / 8
```

Off-peak (Mon–Fri 14:00–18:00 SGT is peak) bills credits at 0.5x, which is the difference between
the low and high end of every range in their table. **From Sep 25 to Oct 7, 2026 all-day usage is
charged at the off-peak rate.** The GLM-5.3-Flash campaign runs to **Oct 7**. Both expire; a
reader arriving after that date should treat the ceiling as 2x lower, which is what the "peak
floor" column in my table already carries.

**Z.ai Team Plan** ([teamplan.md](sources/zai-teamplan.md)). Standard seat 15,000 per 5h / 66,000
weekly credits; Premium 35,000 / 155,000. **The seat price is not published on the page.** It stays
UNKNOWN in my table rather than being estimated, because every other number in this market is
published and an estimate here would be the only unsourced figure in the file. Overage beyond the
included credits bills at 10% off API list. Data is excluded from model training by default, which
is worth more to an enterprise buyer than the price gap.

**OpenCode Go / Go Plus** ([docs/go](sources/opencode-go.html)). 39 rows per plan, each with a
per-model monthly dollar ceiling ($6 to $240) and a five-window rule: 5h = 20% of the monthly
limit, weekly = 50%, monthly = 100%. The plan's request-estimate table is internally inconsistent:
**for all 37 priced models the monthly request column is 2.00x the weekly column** (1.96x for Kimi
K3, 2.02x for Qwen3.8 Max), against 4.33 weeks in a month. Either the monthly column is a separate
cap sitting on top of the weekly one, or the vendor's "month" is two weeks. The page does not say
which, so any figure that assumes the monthly column is a monthly allowance is resting on an
unstated convention. This is a real finding about the vendor's own arithmetic and it is reproducible
from the page.

**Cursor** ([cursor.com/pricing](sources/cursor-pricing.html)). The page's own schema.org `Offer`
block publishes Hobby $0 / Pro $20 / **Pro+ $60** / Ultra $200 / Teams $40 per user. The Pro+ tier
was absent from both my table and the fork's. No token allowance is published for any tier, so no
$/M is computable and the table says so.

**GitHub Copilot** ([plans](sources/github-copilot-plans.html)). Free $0, Pro $10, Pro+ $39, Max
$100 per month, each with a base-credit allowance plus a separate flex allotment billed as a dollar
amount on top ($5, $31 and $100 respectively). The page publishes the plan price and the flex
allowance as two separate figures and never states a credit count per request, so the two cannot
be turned into a $/M: the missing input is a per-request cost the vendor does not publish. The rows
say UNKNOWN rather than carrying a number.

This also corrects a row in the 2026-09-20 pass, which recorded Copilot's allowance as a single
combined figure, "500 / 7,000 / 20,000 credits per month". The current page does not publish a base
credit count that supports reading those as one allowance; it publishes a dollar flex allotment
instead. That earlier row was a reconstruction presented as a published figure, which is the same
class of error this pass is about. The vendor adds a further caveat the earlier row did not carry:
"Flex allotments may change over time", so even the dollar figure is not a fixed ceiling.

**OpenAI** ([platform.openai.com/docs/pricing](sources/openai-pricing.html)) returned 200. The fork
recorded two OpenAI URLs as 403 and marked its rows CARRIED FORWARD. `www.openai.com/chatgpt/pricing/`
still 403s from here, but the platform docs host serves the model price table, so OpenAI is no
longer unverifiable in this pass. That is a coverage improvement over the fork, not a correction of
it.

## The free tier, measured

From [data/opencode-zen-probe.json](data/opencode-zen-probe.json), today:

- `/models` on OpenCode Zen answers with no credential: 85 models, 12 labelled "free".
- 1 of those 12 serves a completion. `mimo-v2.6-flash-free`, `ling-3.0-flash-fin-free`,
  `muse-spark-1.3-contributor-free` and others return 403 "OpenCode's free tier can only be used
  from within OpenCode".
- Two of the twelve (`jev-1.13-free`, `muse-spark-1.3-contributor-free`) now return **HTTP 500**
  where the fork recorded 400/403 on 10-02. The catalogue says free; the endpoint is broken. That
  is a different failure from gated and a directory that lists both as "free" is wrong about at
  least one of them.
- "Free" in this catalogue is a price, not an access. 11 of 12 free models are unusable to an
  external anonymous caller, and one of those fails by error rather than by policy.

## Where the two open issues landed

**Issue #1, "check/add as additional sources".** All four repos were cloned and read in full, not
listed. What each one actually contributes, and what it does not, is tabulated in
[data/issue-1-source-review.csv](data/issue-1-source-review.csv). The short version: all four are
free-tier **catalogues**, and the thing this pass measured is not a catalogue property. A directory
can tell you a vendor offers something free; only a request tells you whether a caller with no key
can use it, and the probe found 1 usable endpoint in 25. What was taken from them is a discipline
rather than a number: `verified-ai-free-tiers` attaches a source URL and a check date to every one
of its 131 records and distinguishes a published ceiling from a vendor that refuses to publish one,
which is the distinction that makes the Cursor and Z.ai Team Plan rows in this pass say UNKNOWN
instead of carrying a plausible guess. Its records are check-dated 2026-08-12/13, three weeks
stale, so the discipline was adopted and the figures were not.

**Issue #2, "Publish Adjusted/Real Usage".** Both repos were read and both are better than their
reputation in the fork. `phuryn/experiments` is a real measurement: it ticks the vendor's own
weekly meter on purpose and prices every call at list price, with a floor/ceiling bracket per step.
I recomputed its SuperGrok figure from its raw `calls.csv` at its own stated list price and got
$67.79 against its published $68.86, a 1.6% gap explained by calls crossing a token-threshold price
step, and its 190x +/- 21 is a meter-tick bracket rather than a whole-run average (a whole-run
recomputation gives 246x, which is the method difference it documents). That is sound work and it is
the strongest evidence in this whole errand for what a subscription is really worth.

**No number from either repo is adopted into this pass's tables, and the reason is the point of the
pass.** This pass subscribed to nothing, so every allowance in `plan-economics.csv` is a published
ceiling. Importing someone else's meter reading into a table whose evidence class is
FIRST-PARTY-COMPUTED would be exactly the class confusion this pass was written to stop. What was
adopted is the one thing that is a method rather than a measurement: the audited traffic mix
(97% cache / 2.5% input / 0.5% output) from `real-api-pricing`'s `conventions.json`, quoted as an
input and stated beside every figure that depends on it. Full reasoning per repo, including what
each does not solve, is in [data/issue-2-source-review.csv](data/issue-2-source-review.csv).

## Known gaps, stated rather than smoothed

- **Fifteen of the twenty fetched sources carry no figure in this pass.** They are archived because
  they are the evidence base and a re-verification needs them, not because every one was mined.
  MiniMax, Anthropic, Cline, Aider, Kilo, Volcengine and the Artificial Analysis snapshot were read
  and are cited in [references/](references/references.md); no number in
  [data/plan-economics.csv](data/plan-economics.csv) is derived from them. A source list that
  implies twenty mined sources when four were mined is its own kind of overclaim.
- **No plan was subscribed to and no authenticated request was made.** Every allowance figure here
  is a published ceiling. Nothing in this pass measures what a meter actually yields, so nothing
  here should be read as a metered result.
- **The traffic mix is an assumption, and I have made it explicit rather than eliminated it.** The
  97/2.5/0.5 mix is `real-api-pricing`'s audited project standard. I did not measure my own cache
  hit rate. A reader whose workload is not cache-dominated should read the 0/75/25 column.
- **OpenCode Go's request table contradicts its own limit rule** and I could not resolve which
  reading is right from the page.
- **Z.ai's price, credit table and token table are as of 2026-10-02 and two of them expire on
  2026-10-07.** The off-peak all-day window and the Flash campaign both end that day.
- **Team Plan seat price is unpublished and is left UNKNOWN.**
- **No latency or throughput claim is made for any vendor.** The probe's `ms` values are this
  sandbox's view of one gateway on one afternoon.
- **The fork's ~30-domain relay/reseller universe was out of scope here** and is not re-verified.
- The fork's 10-03 branch claims 55 sources fetched on **2026-10-03**, a date in this sandbox's
  future (clock reads 2026-10-02), and its `fetch-log.json` entries carry no timestamps to
  corroborate the date. I have not verified that pass and do not adopt its numbers.

## What would falsify this pass

- A first-party statement of the OpenCode Go monthly-vs-weekly convention. Either reading would
  change the plan's effective ceiling by 2x, and the page supports both.
- Any reader reproducing the 78-row grid under a mix they actually measured. The grid is in the
  repo precisely so that this is a five-minute check.
- The Z.ai off-peak window and Flash campaign lapsing on 2026-10-07, which would halve every GLM
  ceiling above.
- A metered run on any plan in this table. Until one exists, every $/M here is a reading of a
  vendor's arithmetic and not a measurement of a subscription.
