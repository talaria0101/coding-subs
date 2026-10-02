# References — 2026-10-02 pass

Every source below was fetched on **2026-10-02 (UTC)** with one request each and archived under
[sources/](../sources/). Per-source HTTP status, byte count, latency and SHA-256 are in
[data/fetch-log.json](../data/fetch-log.json); 20 of 20 returned 200.

## First-party (the evidence for every computed figure in this pass)

| # | Source | URL | Local snapshot |
|---|---|---|---|
| 1 | Z.ai GLM Coding Plan overview (credit table, multipliers, token allowance) | https://docs.z.ai/devpack/overview.md | `zai-overview.md` |
| 2 | Z.ai devpack FAQ | https://docs.z.ai/devpack/faq.md | `zai-faq.md` |
| 3 | Z.ai Team Plan benefits (seat credits, overage, training exclusion) | https://docs.z.ai/devpack/teamplan.md | `zai-teamplan.md` |
| 4 | Z.ai API landing | https://api.z.ai/ | `zai-api-home.html` |
| 5 | OpenCode Zen catalogue | https://opencode.ai/zen/ | `opencode-zen.html` |
| 6 | OpenCode Zen documentation | https://opencode.ai/docs/zen/ | `opencode-zen-docs.html` |
| 7 | **OpenCode Go / Go Plus price grid** (per-model ceilings, token prices, window rules, request estimates) | https://opencode.ai/docs/go/ | `opencode-go.html` |
| 8 | MiniMax global site | https://www.minimax.io/ | `minimax-home.html` |
| 9 | MiniMax token-plan pricing | https://platform.minimax.io/docs/guides/pricing-token-plan | `minimax-token-plan.md` |
| 10 | Anthropic plan pricing | https://www.anthropic.com/pricing | `anthropic-pricing.html` |
| 11 | Anthropic 1M context window support | https://support.anthropic.com/en/articles/9797557-1m-context-window | `anthropic-context.html` |
| 12 | **OpenAI platform pricing** (200; `www.openai.com/chatgpt/pricing/` 403s from here) | https://platform.openai.com/docs/pricing | `openai-pricing.html` |
| 13 | Cursor pricing (schema.org `Offer` block: Hobby 0 / Pro 20 / Pro+ 60 / Ultra 200 / Teams 40) | https://cursor.com/pricing | `cursor-pricing.html` |
| 14 | GitHub Copilot plans | https://github.com/features/copilot/plans | `github-copilot-plans.html` |
| 15 | Cline documentation | https://docs.cline.bot/ | `cline-docs.html` |
| 16 | Aider | https://aider.chat/ | `aider-home.html` |
| 17 | Kilo Code | https://kilo.ai/ | `kilo-home.html` |
| 18 | Volcengine (ByteDance) | https://www.volcengine.com/ | `volcengine-home.html` |
| 19 | Artificial Analysis model leaderboard | https://artificialanalysis.ai/models | `aa-models-page.html` |
| 20 | MiniMax platform | https://platform.minimax.io/ | `minimax-api.html` |

## Live measurement, not a document

- **OpenCode Zen anonymous probe** — `tools/probe-opencode-zen.py`, results in
  [data/opencode-zen-probe.json](../data/opencode-zen-probe.json). Three requests per model across
  12 free-listed models plus a nine-point prompt-size sweep and a `max_tokens` control. No
  `Authorization` header of any kind is sent, by construction; the script cannot test an
  authenticated path and does not claim to.

## Third-party, used for a method or carried unattributed to any ranking

- **`FeiZhuLulu/real-api-pricing`** (MIT), `data/conventions.json` — the audited standard traffic
  mix (97% cache read / 2.5% fresh input / 0.5% output), revised 2026-09-23 after a 14-sample
  audit. Used as a **method input** to the $/M computations in section 1 of the report and in
  [data/method-sensitivity.csv](../data/method-sensitivity.csv); it is not a measurement of any
  workload in this pass. Its 318-row price database was not adopted: adopting it wholesale would
  import three evidence classes (high/medium/low confidence, with 214 official / 75 derived / 29
  sample date kinds) into one table without the grades that distinguish them.
- **`phuryn/experiments`**, `subscription-multipliers/` — metered allowance multipliers, carried in
  [data/subscription-measurements.csv](../data/subscription-measurements.csv) with attribution,
  date, method and uncertainty, and **not ranked** against this pass's published ceilings because
  the two are different evidence classes. The SuperGrok per-call cost was independently re-derived
  from its raw call log as a check on the method.

## Provenance and reproducibility

- Every figure in this pass derives from a page in `sources/`, fetched on 2026-10-02 with the
  per-source log in [data/fetch-log.json](../data/fetch-log.json). The Z.ai overview page's
  SHA-256 is `594793a7...`; two independent fetches of the same URL on the same day produced the
  same digest, so the page is stable across them and any difference between this pass's GLM figures
  and another pass's is a transcription difference rather than a vendor change.
- `tools/parse-opencode-go.py` regenerates [data/opencode-go-grid.csv](../data/opencode-go-grid.csv)
  byte for byte from the archived `opencode-go.html`; CI fails if it stops doing so. The grid is
  therefore recomputable from evidence in the repo rather than citable on trust.
- `tools/validate.py` gates every pass. Its checks and the defects each was added for are listed in
  [../../docs/reviews-2026-10-02.md](../../docs/reviews-2026-10-02.md) review 5.

## Sources explicitly not used

- API relay and reseller marketplaces. Excluded by the policy set in the 2026-09-20 pass: their
  prices are advertisement, their discounts are quota resale, and this pass had no capacity to
  re-verify that universe.
- Any figure about a plan's real metered usage. No plan was subscribed to in this pass, so nothing
  here is a metered result; third-party metered figures are carried separately and not ranked
  against the published ceilings in this pass.
