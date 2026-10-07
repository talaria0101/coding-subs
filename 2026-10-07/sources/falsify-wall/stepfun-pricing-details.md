> ## Documentation Index
> Fetch the complete documentation index at: https://platform.stepfun.ai/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# Pricing and Rate Limits

## Pricing Details

### Pricing for Multimodal Reasoning Models

| Model | Billing unit | Input (cache miss) | Input (cache hit) | Output |
| :- | :- | :- | :- | :- |
| `step-5-preview` | 1M tokens | \$1.00 | \$0.05 | \$2.70 |
| `step-3.7-flash` | 1M tokens | \$0.20 | \$0.04 | \$1.15 |

For `step-5-preview`, the cache-miss input price includes writing new content to the cache. Output tokens include both the model's reasoning process and final answer. See [Prompt caching](/docs/en/guides/developer/prompt-cache) for details.

### Pricing for Reasoning Models

| Model | Billing unit | Input (cache miss) | Input (cache hit) | Output |
| :- | :- | :- | :- | :- |
| `step-3.5-flash` | 1M tokens | \$0.10 | \$0.02 | \$0.30 |
| `step-3.5-flash-2603` | 1M tokens | \$0.10 | \$0.02 | \$0.30 |

### Pricing for Vision Models

| Model | Billing unit | Input (cache miss) | Input (cache hit) | Output |
| :- | :- | :- | :- | :- |
| `step-1o-turbo-vision` | 1M tokens | \$0.36 | \$0.07 | \$1.15 |

Image input is counted and billed as tokens, just like text input. By default, each image uses 169 input tokens; with `detail` enabled, the token count is calculated from the image size.

### Pricing for Speech Models

#### Billed by token

| Model | Billing unit | Input (cache miss) | Input (cache hit) | Output | Current status |
| :- | :- | :- | :- | :- | :- |
| `stepaudio-3-realtime-preview` | — | — | — | — | Free (limited time) |
| `stepaudio-3-chat-preview` | — | — | — | — | Free (limited time) |
| `stepaudio-2.5-realtime` | 1M tokens | \$1.50 | \$0.30 | \$10.00 | Usage-based |
| `stepaudio-2.5-chat` | 1M tokens | \$1.50 | \$0.30 | \$3.50 | Usage-based |
| `step-1o-audio` | 1M tokens | \$3.57 | \$0.71 | \$8.57 | Usage-based |
| `step-audio-2` | 1M tokens | \$1.43 | \$0.29 | \$10.00 | Usage-based |
| `step-audio-r1.5` | 1M tokens | \$1.43 | \$0.29 | \$15.00 | Usage-based |

#### Billed by characters or audio duration

##### Text-to-speech

| Model | Model type | Unit price |
| :- | :- | :- |
| `stepaudio-3-tts` | Text-to-speech model | \$0.36 / 10,000 characters |
| `stepaudio-2.5-tts` | Context-aware text-to-speech model | \$0.85 / 10,000 characters |
| `step-tts-2` | Next-generation text-to-speech model | \$0.40 / 10,000 characters |
| `step-tts-mini` | Text-to-speech model | \$0.13 / 10,000 characters |
| `stepaudio-3-tts` / `stepaudio-2.5-tts` / `step-tts-2` / `step-tts-mini` | Voice cloning model | \$1.50 / voice; trial calls are charged only for synthesis, and a successful production clone is charged immediately |

##### Audio generation and music generation

| Model | Model type | Unit price |
| :- | :- | :- |
| `stepaudio-3-gen-preview` | Unified audio generation model | Free (limited time) |
| `stepaudio-3-music-preview` | Music generation model | Free (limited time) |

##### Speech recognition

| Model | Model type | Unit price |
| :- | :- | :- |
| `stepaudio-3-asr-max` | Speech recognition model | \$0.40 / hour |
| `stepaudio-2.5-asr` | Speech recognition model | \$0.022 / hour |
| `stepaudio-2.5-asr-stream` | Streaming speech recognition model | \$0.18 / hour |
| `stepaudio-2-asr-pro` | Speech recognition model | \$0.29 / hour |
| `step-asr` | Speech recognition model | \$0.13 / hour |
| `step-asr-1.1` | Speech recognition model | \$0.31 / hour |
| `step-asr-1.1-stream` | Streaming speech recognition model | \$0.37 / hour |

For character-based billing, one Chinese character counts as one character, two English letters count as one character, and two punctuation marks count as one character.

### Pricing for Image Generation and Editing

<Note>
  `step-2x-large` and `step-image-edit-2` will be retired on October 10, 2026. The text-to-image, image-to-image, and image editing APIs will stop serving requests on that date. See the [image model retirement notice](/docs/en/guides/image-offline-notice).
</Note>

| Model | Billing unit (per image) |
| :- | :- |
| `step-2x-large` | \$0.02 |
| `step-image-edit-2` | \$0.003 |

Image generation is billed by the number of images generated. The default is one image per request.

`step-2x-large` has not been free since June 12, 2026 and is billed at \$0.02 per image.

### Pricing for Value-Added Capabilities

| Capability | Billing unit |
| :- | :- |
| Internet search | \$0.006 / call |
| Image search | \$0.02 / call |
| File storage | \$0.08 / GB / day |

Value-added capabilities are billed by actual usage.

## Tiered Rate Limits

Pay-as-you-go calls to the standard Open Platform API are rate limited by tier according to the cumulative top-up amount on your account. Only cash top-ups count toward that amount; vouchers do not. [Step Plan](/docs/en/step-plan/overview) usage is governed by the monthly Credit allowance of your subscribed tier rather than by cumulative top-up. When resources reach capacity, we may temporarily adjust the limits for each tier.

### Individual Accounts

Individual accounts must complete identity verification first. Tiers are assigned by cumulative top-up amount:

| User tier | Cumulative top-up amount | Concurrency | RPM | TPM |
| :-: | :- | :- | :- | :- |
| V0 | Under \$15 | 5 | 100 | 500,000 |
| V1 | $15 to $69 | 20 | 400 | 2,000,000 |
| V2 | $70 to $299 | 30 | 600 | 3,000,000 |
| V3 | $300 to $1,499 | 40 | 800 | 4,000,000 |
| V4 | \$1,500 and above | 130 | 2,600 | 13,000,000 |

### Enterprise Accounts

For the rate limit tiers available to verified enterprise accounts, contact your sales representative. Prepaid funds added to an Open Platform account count toward the cumulative top-up amount and are eligible for invoicing through the Open Platform. Postpaid billing is not tied to the cumulative top-up amount and is not invoiced through the Open Platform.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.