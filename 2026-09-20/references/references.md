# References — coding-subs research pass 2026-09-20

All first-party sources accessed and snapshotted on **2026-09-20 between 06:47 and 07:30 UTC**
unless noted. Raw snapshots live in [`../sources/`](../sources/). Evidence labels follow the
repo convention: VERIFIED = read from the provider's own current page/docs; THIRD-PARTY =
reputable secondary source; ESTIMATED = derived; UNKNOWN = not published, never guessed.

## Model landscape

1. **Artificial Analysis — models page, embedded leaderboard dataset** (`artificialanalysis.ai/models`,
   JSON-LD `data` block extracted to `../data/aa-leaderboard-2026-09-20.json`): Intelligence Index
   for the top 20 entries as of 2026-09-20. Deltas vs the 2026-09-13 snapshot: Qwen3.8 Max
   40.3 -> 45.42; Step 5 Preview new at 43.73; Inkling new at 24.98; top-5 otherwise within
   noise (Fable 5.1 53.35, GPT-6 Astra 52.67, Opus 5 50.78, Muse Spark 1.3 48.09, GPT-5.6 Sol 46.97).
   Terminal-Bench, context and API-price columns are carried from the 2026-09-13 snapshot
   (`../../2026-09-13/data/aa-snapshot-2026-09-13.json`) and marked `aa_ii_asof` per row.

## Subscription & plan pricing (first-party, all re-verified 2026-09-20)

2. **Z.ai — GLM Coding Plan docs** (`docs.z.ai/devpack/overview.md`, `faq.md`, `teamplan.md`,
   `transition.md`): Lite/Pro/Max 5-hour credits 2,000/12,000/28,000 and weekly 10,000/60,000/140,000;
   official token-allowance tables unchanged (Lite GLM-5.3 @95% cache: 48-97M tokens/week);
   multipliers GLM-5.3 6.9/1.7/24 and Flash 2.3/0.56/8; off-peak 50% credits. Snapshot:
   `zai-glm-coding-plan-overview.md`, `zai-glm-coding-plan-faq.md`, `zai-teamplan.md`.
3. **Z.ai — Legacy Plan Migration Notice** (`docs.z.ai/devpack/transition.md`): current standard
   monthly prices Lite $18 / Pro $72 / Max $160; quarterly $48.60/$194.40/$432; annual
   $172.80/$691.20/$1,536; legacy-migration 50% path ($9/$36/$80 monthly). Snapshot:
   `zai-plan-update-announcement.md`.
4. **Z.ai — GLM-5.3-Flash Usage Campaign** (`docs.z.ai/devpack/notice/event-glm-5.3-flash.md`):
   campaign window Sep 3-20, 2026 (ends the day of this pass); zero-quota Flash via ZCode
   23:00-09:00 SGT, doubled quota in other agents. Snapshot: `zai-glm53-flash-campaign.md`.
5. **OpenAI — Codex pricing docs** (`developers.openai.com/codex/pricing.md`): Free $0 / Go $8 /
   Plus $20 / Pro from $100 (5x) and $200 (20x); GPT-5.5 retires from ChatGPT/Codex Oct 14, 2026;
   per-model local-messages-per-5h table unchanged (Plus: Sol 10-100, Terra 25-200, Luna 250-2,000,
   Astra 5-45); credits table explicit (1 credit = $0.01; GPT-6 Astra 250 credits per 1M input,
   25 cached, 1,250 output). Snapshot: `openai-codex-pricing.md`.
6. **Anthropic — pricing page** (`anthropic.com/pricing`): Pro $20 ($17 annual, $200 upfront);
   Max from $100, 5x/20x; 1M context on all paid plan tiers; usage credits. Snapshot:
   `anthropic-pricing-page.html`.
7. **Anthropic — "How large is the context window on paid Claude plans?"** (support.claude.com
   8606394): Claude Code on Pro/Max/Team/Enterprise exposes 1M for Fable 5.1 / Sonnet 5 / Fable 5 /
   Opus 5 / Opus 4.8/4.7/4.6; Pro users must enable usage credits for 1M. Snapshot:
   `anthropic-context-window-paid-plans.html`.
8. **Claude Code weekly-limit change, Sep 14 2026** (THIRD-PARTY synthesis; Anthropic does not
   publish numeric limits): the 50% promotional level ran May 13 - Sep 13 2026; from Sep 14 the
   permanent level is +25% vs the pre-May baseline, i.e. ~17% below the promo level. Snapshot of
   one analysis: `thirdparty-aicatchup-weekly-limits.html` (published Aug 29, updated Sep 14).
9. **Google — AI plans page** (`gemini.google/subscriptions/`): AI Pro $19.99/mo ("4x higher usage"
   vs free); AI Ultra starting $99.99 (5x) with $199.99 (20x) tier; AI Plus available in 160+
   countries; student promo (Plus free for a year). Snapshot: `google-ai-subscriptions.html`.
10. **Google Antigravity 2.0 — plans & models docs** (`antigravity.google/docs/plans/`, `/docs/models/`):
    baseline quota (Gemini 3.1 Pro + 3.8/3.7/3.6 Flash core; unlimited tab completions); free tier =
    "meaningful quota, refreshed weekly"; Claude Sonnet 4.6 & Opus 4.6 (thinking) + gpt-oss-120b on
    free/AI Plus/Pro; third-party models on Ultra; AI-credit overage at consumption pricing; UI
    rebrand "Antigravity 2.0" with AGY CLI. Snapshots: `antigravity-plans-doc.html`,
    `antigravity-models-doc.html` (gzip-decoded).
11. **Google — Gemini API pricing** (`ai.google.dev/gemini-api/docs/pricing`): Gemini 3.8 Flash
    intro $0.75/$3.75 per 1M through Dec 31 2026, then $1.50/$7.50; Batch 50% off. Snapshot:
    `gemini-api-pricing.html`.
12. **MiniMax — Token Plan docs** (`platform.minimax.io/docs/token-plan/intro.md` +
    `guides/pricing-token-plan.md`): Plus $22 / Max $55 / Ultra $132; 5-hour + weekly windows;
    3-4/4-5/6-7 parallel agents; credits 1,000 = $1. Snapshots: `minimax-token-plan-intro.md`,
    `minimax-token-plan-pricing.md`.
13. **Kimi (Moonshot) — Membership Benefits** (`kimi.com/code/docs/en/kimi-code/membership.html`):
    NEW plans launched; "pricing unchanged"; weekly quota window REMOVED for new members (5h rolling
    only); Kimi Code from Plus; K3 access from Plus; K3 1M context from Pro; legacy members keep
    legacy rules. Snapshot: `kimi-membership-doc.html`.
14. **Kimi Help Center — membership overview** (`kimi.com/en/help/membership/membership-overview`):
    legacy CN tiers Andante ¥49 / Moderato ¥99 / Allegretto ¥199 / Allegro ¥699 per month (CNY,
    VERIFIED). Snapshot: `kimi-help-membership-overview.html`. International USD list prices
    ($19/$39/$99/$199) remain THIRD-PARTY (ki-ai.chat snapshot `thirdparty-kiaichat-membership.html`).
15. **GitHub Copilot — plans doc** (`docs.github.com/en/copilot/get-started/plans`): Pro $10
    (1,000 base + 500 flex), Pro+ $39 (3,900 + 3,100), Max $100 (10,000 + 10,000), Business $19,
    Enterprise $39. Snapshot: `github-copilot-plans.html`.
16. **Meta — Muse Code subscriptions doc** (`dev.meta.ai/docs/muse-code/subscriptions.md`):
    Everyday (10-50 prompts/5h), High (5x), Power (20x); multimodal uploads; prices still shown only
    at onboarding. Snapshot: `meta-muse-subscriptions.md`.
17. **Alibaba Cloud Model Studio — Coding plan overview** (doc updated Sep 11 2026): Pro $50/month;
    up to 6,000 requests/5h, 45,000/week, 90,000/month; supported models qwen3-coder-next,
    qwen3-coder-plus, glm-4.7; Lite retired Mar 20 2026; slots restocked daily 00:00 UTC+8.
    Snapshot: `alibaba-coding-plan-doc.html`.
18. **ByteDance Trae — pricing** (`trae.ai/pricing`): Free $0 (Auto only) / Pro $20 / Pro+ $60 /
    Ultra $200 — Lite $3 and Pro $10 are gone. Snapshot: `trae-pricing.html`.
19. **AWS Kiro — pricing** (`kiro.dev/pricing/`): Free 50 credits; Pro $20 = 1,000 credits;
    Pro+ $40 = 2,000; Pro Max $100 = 5,000; Power $200 = 10,000; add-on credits $0.04; free tier
    gets Claude Sonnet 4.5 + open-weight models. Snapshot: `kiro-pricing.html`.
20. **Cognition Devin — pricing** (`devin.ai/pricing`): Free $0 / Pro $20 / Max $200 (NEW "Max" tag);
    Teams $80 + $40 per full dev seat; SWE-2 model announced. Snapshot: `devin-pricing.html`.
21. **Command Code — pricing page** (`commandcode.ai/pricing`): Go $1 / GOAT $10 / Pro $20 /
    Max 10x $100 / Max 20x $200; credits $10/$70/$80/$150/$300; API plan $15/mo, zero-markup PAYG,
    top-ups roll over; Teams $40; up to 1M context; per-model allowances on GOAT. Snapshot:
    `commandcode-pricing.html` (+ the Nemo-010 fork's independent snapshot of the same page:
    `commandcode-pricing-fork-snapshot.txt`).
22. **Factory — pricing** (`factory.ai/pricing`): Droid Pro $20 / Plus $100 (~5x) / Max $200 (~10x);
    Droid Computers on Plus+. Snapshot: `factory-pricing.html`.
23. **Replit — pricing** (`replit.com/pricing`): Core $20 ($18 annual); Pro $100 ($90 annual) with
    $100 model credit and 10 parallel agents. Snapshot: `replit-pricing.html`.
24. **Augment — pricing** (`augmentcode.com/pricing`): product rebranded Cosmos; STANDARD $20/mo
    flat per team, up to 50 seats, $20 usage included. Snapshot: `augment-pricing.html`.
25. **Cerebras — Code page** (`cerebras.ai/code`): Pro $50 (24M tokens/day) and Max $200
    (120M tokens/day) both still marked "sold out"; model GLM-4.7. Snapshot:
    `cerebras-code-pricing.html`.
26. **Cursor — pricing** (`cursor.com/pricing`): public page shows Individual $20 and Teams $40
    only; Pro+/Ultra prices sit behind a JS tab (THIRD-PARTY for $60/$200, unchanged vs 09-13).
    Snapshot: `cursor-pricing.html`.
27. **Mistral — pricing** (`mistral.ai/pricing`): Le Chat Pro $14.99 with full Vibe access, fair
    use; $10/mo API credits. Snapshot: `mistral-lechat-pricing.html`.
28. **Zed — pricing** (`zed.dev/pricing`): Pro $10/mo, $5 of tokens included, hosted usage billed at
    API list +10%; Personal free with BYOK. Snapshot: `zed-pricing.html`.
29. **Warp — pricing** (`warp.dev/pricing`): Free $0; Build "pay as you go, starting at $20/mo"
    ($18 annual); Max "starting at $200/mo" ($180 annual). Snapshot: `warp-pricing.html`.
30. **OpenCode Zen** (`opencode.ai/zen/`): $20 top-ups (+$1.23 card fee), per-request pricing,
    "zero markups", auto-top-up at $5. Snapshot: `opencode-zen.html`.

## FX and registries

31. **FX**: open.er-api.com USD base rates, updated 2026-09-20T00:02:31Z: 1 USD = 6.7184 CNY =
    7.8453 HKD = 31.8367 TWD. Snapshot: `fx-cny-usd.txt`. Conversions in
    `../data/currency-normalization.csv` are ESTIMATED (rounding + daily FX drift).
32. **models.dev registry API** (`models.dev/api.json`, fetched 2026-09-20): 222 providers /
    7,869 models. Snapshot: `modelsdev-api.json`. Provider-level cost table:
    `../data/modelsdev-providers.csv` (adopted from the Nemo-010 fork, see Provenance).

## Relay/reseller market (advisory only — excluded from rankings)

33. **Wei-Shaw/sub2api README** (live at commit `fbb9006adef8`, pushed 2026-09-20T06:57Z): sponsor
    table with affiliate links (`?aff=SUB2API`); ToS warning; sponsor copy quoted in
    `../data/relay-market-flags.csv`. Snapshot: `sub2api-readme-today.md`.
34. **Nemo-010/coding-subs fork, pass 2026-09-20** (THIRD-PARTY): rate-card snapshots and tracker
    findings for the relay market (CodexEverywhere pool instability, PPToken/PP.dog ad arithmetic,
    CCTK Claude-group 2.1x, jiangzhi issue refs #6871/#7202/#6957, reverse-proxy reachability probe).
    Used only as corroborating evidence in the advisory; its rankings were NOT adopted.

## Method lineage

35. **This repo's 2026-09-13 pass** (`../../2026-09-13/`): models-database columns, provider
    database columns, workload definition (52.5M tokens/month), and evidence-label conventions
    carried forward; 44 provider rows re-verified or updated individually.
36. **Category enumeration method**: adopted from the Nemo-010 fork's PROVIDER-BY-PROVIDER pass —
    enumerate the coding-agent category and check each member, rather than string-searching
    sources; its `agents-universe.csv` is carried forward in `../data/` with two new rows.
