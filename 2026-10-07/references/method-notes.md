# Method notes - 2026-10-07

What worked and what failed in retrieval this pass. Counts refer to [../data/fetch-log.json](../data/fetch-log.json).

## What worked

- **Code read at a pinned commit.** OpenCode's quota logic and R20's tables were fetched from
  `raw.githubusercontent.com/<owner>/<repo>/<full SHA>/<path>`, not from a branch. A line number cited
  against a SHA stays true after the branch moves; a line number cited against `main` does not. The
  commit SHA is in every URL, so the log records the exact revision with no separate step.
- **The GitHub REST API instead of issue HTML.** Issue JSON carries `created_at`, `state`, `labels` and
  the opening body in a few kilobytes, which is what an issue-citation audit needs. It showed that none
  of the 13 Sub2api issues cited by the 2026-10-06 pass carries a label.
- **Markdown routes of documentation sites** (`docs.z.ai/*.md`, `opencode.ai/docs/go.md`,
  `openrouter.ai/docs/api_reference/limits.md`, StepFun's `*.md`). Small, line-citable, and free of
  rendering noise.
- **Parsing the leaderboard payload rather than grepping it.** `tools/parse-aa-models.py` recovers each
  model object, including `isReasoning` and `contextWindowTokens`, which answered the context and
  reasoning-mode half of the Ling identity question without archiving the 4 MB per-model page.
- **Visible-text comparison for drift.** Two of the four drifted pages (Command Code GOAT, xAI) changed
  bytes on re-fetch. Comparing the text an HTML parser keeps after dropping script, style, svg and head
  separates a content change (three new strings on GOAT) from page-build noise (none on xAI). A changed
  SHA-256 alone says only that the bytes moved.
- **PDF text.** The NVIDIA trial terms were checked by extracting the archived PDF with `pypdf`, installed
  into a throwaway environment with `uv run --with pypdf`; the machine had no `pip` and no `pdftotext`.

## What failed or needs care

- **r.jina.ai is intermittent.** 8 of the 14 failure records in the log are r.jina.ai 403s. The same
  Volcengine URL returned 403 and later 200 through the same route, so a jina 403 is not a property of
  the target page. Where the jina rendering is the archived copy (Volcengine, Xiaomi, Kimi), the bytes
  are the proxy's text, not the vendor's, and the CSVs say so.
- **User-agent effects.** An earlier worker probed six user agents against the four drift pages (its log
  is not archived here): Command Code returned HTTP 403 (Cloudflare error 1010) to Python's default
  urllib agent and the same body to the other five; no page served different prices to different
  agents. `tools/fetch-source.py` sends one fixed agent, so a 403 from a default-agent client is not
  evidence that a page is unreachable.
- **Logged-in surfaces.** Z.ai's live checkout price, Gemini's per-project rate limits and every relay's
  subscription price sit behind a login. None was attempted; each is `UNKNOWN`.
- **Per-model pages that do not exist.** Artificial Analysis returns 404 for both Contributor slugs. A 404
  is recorded as a failure with its byte count and hash, and it is evidence only of that URL.
- **Search engines.** Google returned an access screen and Bing returned unrelated results to an earlier
  worker; neither is cited as evidence of anything.

## Bounding the archive

The seven research logs held far more than this pass cites. Each log was filtered to the files a
published claim rests on, plus the failure records the pass cites, then merged with
`tools/merge-fetch-logs.py`, one `--map` per topic into `sources/<topic>/` and one file-level map that
puts the leaderboard payload at the top of `sources/` for the gate. Result: 87 records, 73 archived files,
9,266,537 bytes. Pages read but not archived are listed at the end of
[references.md](references.md); no figure from them is published as verified.
