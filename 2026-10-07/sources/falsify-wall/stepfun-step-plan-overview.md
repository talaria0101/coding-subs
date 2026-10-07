> ## Documentation Index
> Fetch the complete documentation index at: https://platform.stepfun.ai/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# Step Plan Overview

Related resources: [Step Code authentication](/docs/en/step-code/configuration/models) · [Pay-as-you-go pricing and rate limits](/docs/en/guides/pricing/details).

Step Plan is a subscription service from the StepFun API Platform that lets you use StepFun models at a subscription price in mainstream coding tools and agent platforms such as OpenClaw, Claude Code, Trae, and Cursor. After subscribing, you connect with a valid Step API Key and receive a unified model usage allowance every month.

<Note>
  Step Plan has moved to **Credit-based monthly allowance** billing: your allowance is issued in Credits each month and can be spent flexibly within the month. If you subscribed to the earlier request-based plan, see the [Step Plan upgrade notice](/docs/en/step-plan/upgrade-notice) for what changed and how to upgrade.
</Note>

## Key features

* **One billing unit for everything**: usage across all models is measured in Credits, so there is no need to track separate prices per model.
* **Fast model experience by default**: every tier provides the same high-speed model performance, with no extra charge for speed.
* **Monthly allowance, flexible spending**: Credits are issued once per month and can be spent at any time within the month, with no time-window or request-frequency limits.
* **Top up when you run out**: if you use up your monthly allowance, you can purchase booster packs instead of waiting for the next month.
* **Available across platforms**: no platform restrictions. One subscription covers mainstream coding and agent toolchains.
* **Multiple model families**: covers text, reasoning, speech, and smart routing models, with more on the way.

## Billing

Step Plan uses **Credits** as its unified billing unit. When you call any model, the usage is converted into Credits and deducted from your current month's allowance.

Credits convert to payment at approximately **\$1 ≈ 7M Credits** (7 million Credits correspond to about \$1 of model usage). What differs between tiers is the number of Credits issued each month.

After you subscribe, the full month's Credits are issued to your monthly allowance at once. They can be spent at any time within the month, are cleared at the end of the month, and do not roll over to the next cycle.

### Deduction order

When your account holds both monthly-allowance Credits and booster-pack Credits, usage is deducted from whichever expires first. Monthly-allowance Credits expire when the month's allowance is cleared; booster-pack Credits expire on their own 30-day expiration dates.

## Plan tiers

Step Plan offers four tiers. They differ in the monthly Credit allowance and price; all tiers provide the same high-speed model performance.

| Plan | Best for | Monthly Credits | Monthly | Quarterly | Yearly |
| - | - | - | - | - | - |
| **Flash Mini** | Getting started with AI | 400M | \$6.99 | \$18.99 | \$69.99 |
| **Flash Plus** | Daily productivity | 1,600M | \$9.99 | \$26.99 | \$95.99 |
| **Flash Pro** | Heavy AI use | 8,000M | \$29 | \$79 | \$289 |
| **Flash Max** | Professional workloads | 40,000M | \$99 | \$269 | \$989 |

Quarterly and yearly plans are paid once for the full period, but Credits are still issued month by month (quarterly = monthly Credits × 3 months, yearly = monthly Credits × 12 months). "M" stands for million Credits.

Every tier includes: access to all flagship models and smart routing, coverage of multiple MCP tools, and multi-device login. Flash Plus and above also include priority API rates and priority technical support.

## Booster packs

When your monthly allowance runs out, you can purchase booster packs to add Credits without waiting for the next month's issuance. Booster packs are available only to active Step Plan subscribers, run on their own separate 30-day cycles, and are independent of your subscription's expiration date.

| Booster pack | Price | Credits |
| - | - | - |
| Small | \$6.99 | 400M |
| Large | \$9.99 | 1,600M |

## Supported models

Step Plan currently supports the following models, covering text, reasoning, speech, and smart routing. For each model's capabilities and parameters, see the [model capability overview](/docs/en/guides/models/overview).

* [`step-5-preview`](/docs/en/guides/models/step-5-preview): flagship model for agentic work
* [`step-3.7-flash`](/docs/en/guides/models/step-3.7-flash): high-speed multimodal reasoning model
* [`step-3.5-flash`](/docs/en/guides/models/step-3.5-flash): high-speed model for agent and coding tasks
* `step-3.5-flash-2603`: a version optimized for high-frequency agent scenarios
* [`stepaudio-2.5-tts`](/docs/en/guides/models/stepaudio-2.5-tts): next-generation contextual TTS model
* [`stepaudio-2.5-asr`](/docs/en/guides/models/stepaudio-2.5-asr): next-generation automatic speech recognition model
* `step-router-v1`: smart routing model that dispatches requests by task complexity

More StepFun flagship models will be added over time.

## Getting connected

After you have a valid Step API Key, choose the Step Plan configuration URL for your tool:

* **Claude Code / Anthropic SDK:** `https://api.stepfun.ai/step_plan`
* **OpenAI SDK Chat Completions calls:** `https://api.stepfun.ai/step_plan/v1`

These are client configuration URLs (Base URL), not the full HTTP request URLs. See the [Messages API](/docs/en/api-reference/chat/messages-create) and the matching API reference for full request URLs. For Claude Code setup, see the [Claude Code integration guide](/docs/en/step-plan/integrations/claude-code). For other tools, follow the tool-specific [integration guide](/docs/en/step-plan/quick-start).

The Step Plan channel consumes subscription Credits. The standard API channel has a separate quota. Requests sent to the standard API address enter the standard API channel; whether they succeed depends on that channel's permissions and account status. A successful call does not mean Step Plan Credits were consumed.

## Frequently asked questions

<AccordionGroup>
  <Accordion title="How is Step Plan different from calling the API directly?">
    Step Plan is a subscription: its monthly Credit allowance provides more usage than pay-as-you-go at the same spend, and Credits are issued monthly and can be spent at any time within the month, which makes costs easier to control. The two use different Base URLs and do not affect each other.
  </Accordion>

  <Accordion title="How are Credits billed?">
    Credits are Step Plan's unified billing unit; each model's usage is converted into Credits and deducted. Credits convert at approximately \$1 ≈ 7M Credits. After you subscribe, the full month's Credits are issued at once, to be spent within the month and cleared at month end.
  </Accordion>

  <Accordion title="Do unused monthly Credits roll over to the next month?">
    No. Monthly-allowance Credits are cleared at the end of the month and do not carry over to the next cycle. Booster packs run on their own separate 30-day cycles and expire on their own dates.
  </Accordion>

  <Accordion title="What happens when I use up this month's Credits?">
    You can purchase booster packs to add Credits (Small at \$6.99 / 400M, Large at \$9.99 / 1600M, each on its own 30-day cycle), or wait for the next month's allowance to be issued.
  </Accordion>

  <Accordion title="Is Step Plan subject to tiered rate limits (RPM / TPM)?">
    No. Step Plan is not subject to the platform's [tiered rate limits](/docs/en/guides/pricing/details#tiered-rate-limits) based on cumulative top-up amounts. Your usage is governed by the monthly Credit allowance of your subscribed tier.
  </Accordion>

  <Accordion title="What is the relationship between Step Plan and my account balance?">
    They are two separate systems. Usage within Step Plan draws on the subscription's own Credit allowance and does not deduct from your account balance. You can, however, use your account balance (top-up funds) to pay for a Step Plan subscription.
  </Accordion>

  <Accordion title="Which payment methods are supported?">
    Subscriptions can be paid through Stripe, or redeemed using your account balance (top-up funds).
  </Accordion>

  <Accordion title="Can I cancel my subscription?">
    Yes, at any time. Fees already paid are not refunded, and service continues until the end of the current billing cycle.
  </Accordion>

  <Accordion title="Which Base URL does Step Plan use?">
    Choose by tool: Claude Code / Anthropic SDK uses `https://api.stepfun.ai/step_plan`; OpenAI SDK Chat Completions calls use `https://api.stepfun.ai/step_plan/v1`. In Claude Code, do not paste the full `/v1/messages` request URL into the Base URL. See the [Claude Code integration guide](/docs/en/step-plan/integrations/claude-code) and the [Messages API](/docs/en/api-reference/chat/messages-create).
  </Accordion>

  <Accordion title="What should I do if a third-party tool throws errors?">
    First confirm the Base URL for that tool, your current model permissions, and your Step Plan subscription and Credit status. If you previously connected another provider, check old URL, model, or key settings, then fully restart the client. If it still fails, share the client version, error message, time of the issue, and a request ID if you have one. Do not send the full API Key.
  </Accordion>

  <Accordion title="Will more models be added in the future?">
    Yes. Step Plan will gradually expand to more existing and future StepFun flagship models.
  </Accordion>
</AccordionGroup>


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.