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

## Third-party, used only for a method rather than a number

- **`FeiZhuLulu/real-api-pricing`** (MIT), `data/conventions.json` — the audited standard traffic
  mix (97% cache read / 2.5% fresh input / 0.5% output) and its evidence grades. The mix is an
  **input to this pass's method**, quoted as a convention, not a measurement of my own workload. The
  upstream issue #2 pointed at this repo; see [docs/reviews-2026-10-02.md](../../docs/reviews-2026-10-02.md)
  for what was and was not taken from it.
- **`phuryn/experiments`**, `subscription-multipliers/` — metered allowance multipliers. Not
  adopted as numbers in this pass; the reasoning for that is in the review.

## Cross-checks against the fork

The Z.ai overview page fetched here has SHA-256 `594793a7...`, identical to the entry the fork
recorded in its own `2026-10-03/data/fetch-log.json` for the same URL. Two independent fetches
agree the page is unchanged, so any difference between this pass and the fork's 10-02 figures on
GLM is a transcription difference, not a vendor change.

## Sources explicitly not used

- API relay and reseller marketplaces. Excluded by the policy set in the 2026-09-20 pass: their
  prices are advertisement, their discounts are quota resale, and this pass had no capacity to
  re-verify that universe.
- Any figure about a plan's real usage. No plan was subscribed to in this pass, so nothing here is
  a metered result.
