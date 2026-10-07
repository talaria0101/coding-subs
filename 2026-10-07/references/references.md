# References - 2026-10-07

Every figure in this pass resolves to one of these. All were accessed 2026-10-07 (UTC, from `date -u`
on the machine that assembled the pass). Archived bytes are under [../sources/](../sources/), one
subdirectory per research topic, with the full SHA-256, byte count, route and HTTP status of every
attempt in [../data/fetch-log.json](../data/fetch-log.json). Hash prefixes below are the first 16 hex
digits of that SHA-256. Pages archived by the 2026-10-06 pass are cited at their `2026-10-06/sources/`
path and are not copied again.

## Leaderboard and capability

**[R1] Artificial Analysis - leaderboard models page** - <https://artificialanalysis.ai/leaderboards/models>
- accessed 2026-10-07 - HTTP 200, 2,430,384 B, `sha256:d0750cafb27ea1d8` - archived as
[../sources/aa-leaderboard-models.html](../sources/aa-leaderboard-models.html). Archived at the top of
`sources/` rather than in a topic subdirectory so that the gate's `lookup-against-board` check re-parses
it against [../data/aa-lookup.csv](../data/aa-lookup.csv). `tools/parse-aa-models.py` recovers 681
scored slugs; the 2026-10-06 copy of the same URL (`sha256:06e5272f174c38e8`, also fetched 2026-10-07)
yields 680. The only difference is the added slug `solar-pro-2` (II 6.9984). For `ling-3-1-flash` the
payload carries `"isReasoning":true`, `"contextWindowTokens":1000000` and an Intelligence Index of
41.0906; `deepseek-v4-1-flash` scores 39.4562; `muse-spark-1-3-contributor`,
`muse-spark-1-2-contributor` and `mimo-v2-5` are absent.

**[R2] Artificial Analysis - per-model pages for both Contributor SKUs** -
<https://artificialanalysis.ai/models/muse-spark-1-3-contributor> and `.../muse-spark-1-2-contributor`
- accessed 2026-10-07 - **HTTP 404** each (267,122 B of error page, not archived). Recorded as failures
in the log.

**[R3] Meta - Muse Spark reasoning documentation** - <https://dev.meta.ai/docs/reasoning> - accessed
2026-10-07 - HTTP 200, 369,047 B, `sha256:60c757e5deea10ed` - archived as
[../sources/leaderboard/meta-reasoning.html](../sources/leaderboard/meta-reasoning.html). Of the `"max"`
effort:

> "Standard-tier muse-spark-1.3 only; not available on Contributor-tier models."

## OpenCode Go

**[R4] OpenCode - Go plan docs** - <https://opencode.ai/docs/go.md> - accessed 2026-10-07 - HTTP 200,
39,692 B, `sha256:e62561c5c6fb7685` - archived as
[../sources/opencode-go/opencode-go.md](../sources/opencode-go/opencode-go.md). Byte-identical to
`2026-10-06/sources/opencode-go.md`. Line 149 is unchanged: "Each model's monthly limit below
determines how its usage counts toward those allowances." Grid rows used here: line 172-173 (both Muse
Spark Contributor SKUs), 166 and 168 (MiMo-V2.6-Flash and MiMo-V2.5), 165 (LongCat 2.5 Preview Free),
178 (DeepSeek V4.1 Flash off-peak).

**[R5] anomalyco/opencode at commit `ecc4916b5a9608c30e6dd58a67f2137b594407ca`** - commit metadata
<https://api.github.com/repos/anomalyco/opencode/commits/ecc4916b5a9608c30e6dd58a67f2137b594407ca>
(HTTP 200, 9,049 B, `sha256:55378f3566c863fc`, committed 2026-10-06T22:32:45Z) and eleven source files
fetched from `raw.githubusercontent.com/anomalyco/opencode/ecc4916b.../<path>`, archived under
[../sources/opencode-go/github/](../sources/opencode-go/github/) at their repository paths. The lines
this pass rests on:

- `packages/console/app/src/routes/zen/util/handler.ts:1194` -
  `const quotaCost = Math.round(cost * modelInfo.costMultiplier)`, added to `LiteTable.monthlyUsage`
  (line 1202), `weeklyUsage` (1215) and `rollingUsage` (1227) whatever the model.
- `packages/console/core/src/schema/billing.sql.ts:74-88` - `LiteTable` has `rollingUsage`,
  `weeklyUsage`, `monthlyUsage` and a unique index on workspace and user; no model column.
- `handler.ts:895-955` - the request gate compares those three counters with `LiteData.getLimits()` and
  throws `GoUsageLimitError` (lines 911, 931, 951).
- `handler.ts:112-123` - `proxyInference(...)` runs first and `if (response) return response`.
- `packages/console/app/src/lib/inference-proxy.ts:46-53` - `const legacy = !key.startsWith("oc_sk_")`,
  `if (legacy && !workspace) return undefined`, then a request to `Resource.ConsoleMigration.inferenceUrl`.
- `infra/console.ts:224-229` - in production that URL is `https://opencode.ai/inference`, a separate
  service whose limiter is not in this repository.
- `packages/console/app/src/lib/lite-usage.ts:42-55` - one `usagePercent` is apportioned across models
  by `quotaCost`; line 67 `return limit / multiplier` converts one limit into a per-model display figure.
- `packages/console/app/test/liteUsage.test.ts:23` - asserts the per-model `contributionPercent` values
  sum to `usagePercent`. Read, not executed.

## Z.ai

**[R6] Z.ai - GLM Coding Plan overview** - <https://docs.z.ai/devpack/overview.md> - accessed
2026-10-07 - HTTP 200, 8,315 B, `sha256:594793a77de76dcd` - archived as
[../sources/zai/zai-overview.md](../sources/zai/zai-overview.md). Byte-identical to the 2026-10-06
copy. Line 135: "During off-peak hours, model usage is charged at 50% of the standard credit rate".
Line 138: "Peak hours: Monday to Friday, 14:00-18:00 Singapore Standard Time (UTC+8)" (the page uses an
en dash). Line 142: the September 25 to October 7 all-day off-peak tip. Lines 65-67 credits, 97-108
multipliers, 164-165 the rule that the maximum is all-off-peak and the minimum all-peak.

**[R7] Z.ai - Team Plan** - <https://docs.z.ai/devpack/teamplan.md> - accessed 2026-10-07 - HTTP 200,
10,353 B, `sha256:246b67a7efbbcab3` - [../sources/zai/zai-teamplan.md](../sources/zai/zai-teamplan.md).
Byte-identical to the 2026-10-06 copy. Lines 30-31: Standard Seat 15,000 / 66,000 and Premium Seat
35,000 / 155,000 credits per 5 hours / week. No seat price.

**[R8] Z.ai - subscribe page bundle** - <https://z.ai/_next/static/chunks/38aiay3p71_3a.js> - accessed
2026-10-07 - HTTP 200, 34,542 B, `sha256:a90663918ca690cd` -
[../sources/zai/zai-subscribe-chunk-38aiay3p71_3a.js](../sources/zai/zai-subscribe-chunk-38aiay3p71_3a.js).
Monthly products tagged `version:"V3"`: Lite `money:18`, Pro `money:80,oldMoney:80`, Max
`money:168,oldMoney:168`. Tagged `version:"V2"`: Pro `money:64.8,oldMoney:72`, Max
`money:144,oldMoney:160`. These are the page's static values; the live checkout price is served by an
endpoint that refused an anonymous request, so it is not established.

**[R9] Z.ai - plan update notice** - <https://docs.z.ai/devpack/notice/usage-revision.md> - accessed
2026-10-07 - HTTP 200, 10,063 B, `sha256:0c12925094f86290` -
[../sources/zai/zai-devpack_notice_usage-revision.md](../sources/zai/zai-devpack_notice_usage-revision.md).
"Publication date: July 30, 2026" and "Previous plans are no longer sold to new users."

**[R10] Z.ai - transition notice** - <https://docs.z.ai/devpack/transition.md> - accessed 2026-10-07 -
HTTP 200, 5,323 B, `sha256:14e37269e96a98d4` -
[../sources/zai/zai-devpack_transition.md](../sources/zai/zai-devpack_transition.md). Dated April 21,
2026; its "Current Standard Price" table is the source of the $72 and $160 figures, which predate R9.

**[R11] Z.ai - GLM-5.3-Flash campaign notice, GLM-5.3 guide, llms.txt and sitemap** - archived under
[../sources/zai/](../sources/zai/) (hashes in the log). The notice: "Campaign period: September 3, 2026
to October 7, 2026" with times in UTC+8. The guide, line 73: "Model calls made during off-peak hours,
including all day on weekends, consume only 50% of the standard points". The sitemap and llms.txt list
no successor notice. `https://z.ai/blog` and `https://z.ai/blog/` returned **HTTP 404**.

## Command Code, DeepSeek, xAI, Fenno

**[R12] Command Code - pricing and limits (deals)** - <https://commandcode.ai/docs/resources/pricing-limits>
- accessed 2026-10-07 - HTTP 200, 829,534 B, `sha256:fcc5035b38957bb4` -
[../sources/free-lanes/commandcode-pricing-limits.html](../sources/free-lanes/commandcode-pricing-limits.html).

> "ling-3.1-flash:free is free, with no daily request limit. while it lasts"

> "a 560B-parameter MoE (25B active per token) with a 262K-token context and low, medium, and high
> reasoning effort, served directly from Novita's endpoint"

> "Need to have $1 of credits in your account to start a session."

Also the plan table (Go, GOAT, Pro, Provider, Max 10x, Max 20x, Team Pro), the DeepSeek V4.1 Flash
allowance ("$10 on the $1 Go plan (the plan's full pool), $60 on the $10 GOAT plan and $70 on the $20
Pro plan"), the DeepSeek off-peak row at $0.15 / $0.60 / $0.003, the Ling 3.0 Flash Sante limit ("100
requests a day, per account") and the Laguna S 2.1 term ("while capacity lasts").

**[R13] Command Code - pricing page** - <https://commandcode.ai/pricing> - accessed 2026-10-07 - HTTP
200, 328,041 B, `sha256:3b28b97303cc15be` -
[../sources/free-lanes/commandcode-pricing.html](../sources/free-lanes/commandcode-pricing.html). Every
plan is printed with "+ processing fee"; the fee amount is not on the page.

**[R14] Command Code - GOAT plan** - <https://commandcode.ai/docs/plans/goat> - accessed 2026-10-07 -
HTTP 200, 771,371 B, `sha256:d9aef7129acf058d` -
[../sources/drift-vendors/commandcode-goat.html](../sources/drift-vendors/commandcode-goat.html).
Differs from `2026-10-06/sources/commandcode-goat.html` (`sha256:55b166b3fc8ebc4b`) by three visible
strings, one of them "Cloud access: run the agent on a cloud machine against your GitHub repo." Both
copies carry:

> "Past a limit, requests fall back to those credits - and without them, paid models pause until the
> window or cycle resets while the free models keep working."

Its model table prints "not yet scored" for Muse Spark 1.3 Contributor, Muse Spark 1.2 Contributor and
Ling 3.1 Flash, and 25.2 for MiMo V2.5.

**[R15] DeepSeek - API pricing** - <https://api-docs.deepseek.com/quick_start/pricing> - accessed
2026-10-07 - HTTP 200, 23,982 B, `sha256:210f102275ccf1a6` -
[../sources/drift-vendors/deepseek-pricing.html](../sources/drift-vendors/deepseek-pricing.html).
Byte-identical to the 2026-10-06 copy.

> "(2) Off-peak rates are half of the peak rates. Peak hours are 01:00 - 04:00 and 06:00 - 10:00 UTC,
> Monday through Friday, excluding Chinese public holidays. All other hours are off-peak, including
> weekends and Chinese public holidays in full."

**[R16] xAI - Grok 4.7 model page** - <https://docs.x.ai/developers/models/grok-4.7> - accessed
2026-10-07 - HTTP 200, 376,272 B, `sha256:33ccb25a06d9d79f` -
[../sources/drift-vendors/xai-grok47.html](../sources/drift-vendors/xai-grok47.html). Different bytes
from the 2026-10-06 copy, same byte count, identical visible text: $2.00 input, $0.50 cached, $6.00
output per 1M.

**[R17] Fenno AI - public rate card** - <https://api.fenno.ai/api/v1/models> - accessed 2026-10-07 -
HTTP 200, 11,905 B, `sha256:46ff5fead0acdb72` -
[../sources/drift-vendors/fenno-models.json](../sources/drift-vendors/fenno-models.json).
Byte-identical to the 2026-10-06 copy. All 18 entries: `"window": "1h"`, `"data_status": "pending"`,
`"request_count": 0`.

## Free lanes and the vendor sweep

**[R18] OpenRouter - model catalog** - <https://openrouter.ai/api/v1/models> - accessed 2026-10-07 -
HTTP 200, 774,402 B, `sha256:698558e29491f3c5` -
[../sources/free-lanes/openrouter-models.json](../sources/free-lanes/openrouter-models.json).
`inclusionai/ling-3.1-flash`: prompt and completion `"0"`, context 262144, reasoning
`default_enabled: true`. `deepseek/deepseek-v4.1-flash` and its `:batch` variant: per-token prices in
[../data/vendor-sweep.csv](../data/vendor-sweep.csv).

**[R19] OpenRouter - Ling 3.1 Flash endpoints** -
<https://openrouter.ai/api/v1/models/inclusionai/ling-3.1-flash-20261002/endpoints> - accessed
2026-10-07 - HTTP 200, 1,338 B, `sha256:544ac5fc8a76bf6c` -
[../sources/free-lanes/openrouter-endpoints.json](../sources/free-lanes/openrouter-endpoints.json). One
endpoint, "Novita | inclusionai/ling-3.1-flash-20261002", context 262144, max completion 32768,
quantization "unknown".

**[R20] OpenRouter - limits documentation** - <https://openrouter.ai/docs/api_reference/limits.md> -
accessed 2026-10-07 - HTTP 200, 20,651 B, `sha256:d7db3497873d8323` -
[../sources/free-lanes/openrouter-limits.md](../sources/free-lanes/openrouter-limits.md). Constants
`FREE_MODEL_RATE_LIMIT_RPM = 20`, `FREE_MODEL_NO_CREDITS_RPD = 50`, `FREE_MODEL_HAS_CREDITS_RPD = 1000`,
applied "If you're using a free model variant (with an ID ending in" the free suffix.

**[R21] NVIDIA build - DeepSeek V4.1 Flash, llms.txt and the API Trial Terms** - model page
<https://build.nvidia.com/deepseek-ai/deepseek-v4.1-flash> (HTTP 200, 1,442,175 B,
`sha256:2a0e61dc98c55789`), <https://build.nvidia.com/llms.txt> (HTTP 200, 1,372 B) and the terms PDF
(HTTP 200, 214,700 B, `sha256:afd5df0322615ff9`), archived under
[../sources/falsify-wall/](../sources/falsify-wall/). The model page embeds `"requestsPerMinute":"Up to
40 rpm"` and `"requestsPerDay":"10,000 requests per day"`. llms.txt: "All models offer a free trial tier
with no credit card required." The PDF, text extracted with pypdf: "NVIDIA will provide you access to
the API Service for limited trial purposes only and without use of the API Service or Generated Content
in production."

**[R22] Google - Gemini API pricing and rate limits** - <https://ai.google.dev/gemini-api/docs/pricing>
(HTTP 200, 259,692 B, `sha256:ab9a3e10f27f7808`) and `.../rate-limits` (HTTP 200, 105,570 B), archived
under [../sources/falsify-wall/](../sources/falsify-wall/). For `gemini-3.8-flash` the Free Tier
column reads "Free of charge" for input, output and context caching, and "Used to improve our products"
reads Yes. Rate limits "can be viewed in Google AI Studio".

**[R23] Volcengine Ark pricing, rendered by r.jina.ai** -
<https://r.jina.ai/https://www.volcengine.com/docs/82379/1544106> - accessed 2026-10-07 - one HTTP 403,
then HTTP 200, 31,299 B, `sha256:31acddd2604b9971` -
[../sources/falsify-wall/volcengine-pricing-1544106.jina.md](../sources/falsify-wall/volcengine-pricing-1544106.jina.md).
The `deepseek-v4-1-flash` idle-period row: CNY 1.00 input, 0.017 cache storage per hour, 0.02 cache hit,
4.00 output, per 1M (non-audio). The bytes are the proxy's rendering of the vendor page, not the
vendor's own bytes.

**[R24] ECB euro foreign exchange reference rates** -
<https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml> - HTTP 200, 1,547 B -
[../sources/falsify-wall/ecb-eurofxref-daily.xml](../sources/falsify-wall/ecb-eurofxref-daily.xml).
Rates dated 2026-10-06: USD 1.1269 and CNY 7.5554 per EUR, so 6.7046 CNY per USD.

**[R25] StepFun - Step Plan overview and pricing details** -
<https://platform.stepfun.ai/docs/en/step-plan/overview.md> (HTTP 200, 9,809 B) and
<https://platform.stepfun.ai/docs/en/guides/pricing/details.md> (HTTP 200, 6,058 B), archived under
[../sources/falsify-wall/](../sources/falsify-wall/). Flash Plus: 1,600M Credits per month at $9.99;
"approximately $1 = 7M Credits" (the page uses the approximately-equal sign); `step-5-preview` is a
supported model at $1.00 cache-miss input, $0.05 cache-hit input and $2.70 output per 1M.

**[R26] Cloudflare Workers AI, Moonshot, Xiaomi MiMo and Kimi Code pages** - archived under
[../sources/falsify-wall/](../sources/falsify-wall/), hashes in the log. Cloudflare
`@cf/zai-org/glm-5.3-flash`: $0.150 input, $0.030 cached input, $0.500 output per M. Moonshot
`kimi-k3`: $0.30 cached, $3.00 input, $15.00 output. Xiaomi Token Plan Lite (r.jina.ai rendering): $6 a
month or $5.28 billed yearly, "49.2 Billion Credits" labelled "Yearly package total". Kimi Code (r.jina.ai
rendering): "K3 available on Plus plans and above", Plus at $19 a month or $15 a month billed annually.

## Relays

**[R27] FeiZhuLulu/real-api-pricing at commit `dce850df080582f2926a3376f97a2edf6020a508`** - README,
`data/adopted.csv` and `data/conventions.json` fetched from
`raw.githubusercontent.com/FeiZhuLulu/real-api-pricing/dce850df.../`, HTTP 200 each, archived under
[../sources/relays/](../sources/relays/) (`adopted.csv`: 236,095 B, `sha256:7f1b7be81c8867bb`). This is
the 2026-10-06 pass's R20, now archived at a pinned commit for the first time. Lines 106-107: the
OpenCode Go rows' `min(共享月池$60, 模型Usage $60)` and `同套餐各模型额度不可相加` ("min(shared monthly pool $60, model usage $60)" and "per-model allowances
within one plan are not additive"). Lines 255 and 258:
the Claude Max 20x and 5x rows the earlier pass quoted are `claude-sonnet-5` rows derived from the Opus
rows by a list-price ratio of 2.5. Lines 22-23: the `claude-opus-5` rows. `conventions.json`
`standardTokenMix`: cache 0.97, input 0.025, output 0.005.

**[R28] Wei-Shaw/sub2api - repository metadata, labels and 13 issues** - <https://api.github.com/repos/Wei-Shaw/sub2api>
and `.../issues/<n>`, HTTP 200 each, archived under [../sources/relays/](../sources/relays/). Repository:
43,361 stars, `open_issues_count` 3,564, pushed 2026-10-07T02:03:02Z. Labels: the nine GitHub defaults.
Issues #7360, #7503, #5692, #5786, #1141, #3624, #3896, #6134, #6180, #6755, #6892, #6739, #593: none
carries a label. Titles and openings used are quoted in [../data/citation-audit.csv](../data/citation-audit.csv).

**[R29] Requesty, NanoGPT, PPToken pages and the OpenRouter SDK / Requesty CLI repositories** - archived
under [../sources/relays/](../sources/relays/), hashes in the log. Requesty: "A model that costs $10 per
1M tokens from OpenAI costs $10.50 through Requesty", "5% markup", free tier "200 requests per day".
NanoGPT: Claude Opus 5.5 $4.00 input / $20.00 output per 1M. PPToken model directory: "不含价格信息" ("contains no price information").
OpenRouterTeam/ai-sdk-provider: 690 stars; issues #494 and #538. requestyai/cli: 9 stars; issues #19
and #34. Failures recorded in the log: r.jina.ai **403** for api.pptoken.cc and cctk.ai, and **404** for
the anonymous `/api/v1/model-plaza` route on both.

## What was not reached, or not archived

| Source | Outcome on 2026-10-07 |
|---|---|
| Live Z.ai checkout price | The price endpoint refused an anonymous request; not established. |
| Z.ai blog | HTTP 404 at `/blog` and `/blog/`. |
| AA per-model pages for both Contributor SKUs | HTTP 404. |
| Artificial Analysis `/models` page | Re-fetched by an earlier worker; not archived here, and no claim in this pass rests on it. |
| AA per-model page for `ling-3-1-flash` (4 MB) | Not archived; the leaderboard payload [R1] carries the reasoning flag and context window this pass uses. |
| LMArena, SWE-bench, Aider, LiveBench | Read by an earlier worker; not archived, so no figure from them is published. r.jina.ai returned 403 for LiveBench and SWE-bench. |
| Requesty and NanoGPT limits documentation | Read by an earlier worker; not archived. The ceilings they report are marked as not re-verified. |
| Sub2api source files | Read by an earlier worker at commit `3f1a2ea0`; not archived. No code claim about Sub2api is published here. |
| Alibaba Model Studio, Anthropic, GitHub Copilot pricing pages | Read by an earlier worker; left out to bound the archive (0.7 MB, 0.9 MB and 1.3 MB). None was a counter-example: no qualifying score, or no published token allowance. |
| Command Code processing fee | Not printed on any archived page. `UNKNOWN`. |
| Any authenticated request | None was made. No account, key, subscription or metered run. |
