# Audit record — round 2 defect list for the 2026-10-06 pass

> **This is a published audit record, not a set of instructions.** It is the defect list that four
> adversarial reviews produced against `pass-2026-10-06` @ `530e370`, kept so a reader can see what
> that round was asked to find and check each finding against what was done. The findings and their
> dispositions — including the rejections and the evidence each rejection rests on — are written up
> in [`docs/reviews-2026-10-06.md`](../docs/reviews-2026-10-06.md), which is the record of what
> happened. The imperative phrasing below is preserved because it is what the list said at the time.

Four adversarial reviewers ran against HEAD `530e370`. Findings below are real and reproducible.
Each was fixed; any rejected was recorded **with its evidence** in
`docs/reviews-2026-10-06.md`, which recorded none before this round — itself a finding.

Non-negotiables: `python3 tools/validate.py --all` exits 0; never weaken a check to make a finding
go away (if a check cannot fire correctly, remove it and record why); every number carries a URL, an
access date, a verbatim quote and an evidence class; corrections are dated supersessions, never
silent edits; no narrative history, host details, session/agent references or process narration.

---

## 1. Six checks still do not fire on the defect they were written for

Each has a confirmed reproduction. **Reproduce each failure yourself first**, then fix, then
re-demonstrate both the refusal and the acceptance in `docs/reviews-2026-10-06.md`.

- **`field-columns` (`validate.py:162-167`)** type-checks only four column names, so a shift landing
  entirely on free-text columns passes. Restoring the Sub2api row exactly as `b14c893` shipped it puts
  `'yes - 43'` in `reputation_quantified`, `'349 stars; repo created 2025-12-18'` in
  `delivery_ceiling_documented` — and `R19` cites 43,349 stars, so the corruption reaches prose.
  Broaden the type inference, and **fix the star count wherever it was corrupted**.
- **`unscored-model` (`validate.py:942`)** fires only when `sold_tier and not board_tier`. Add the tier
  slug to `models-database.csv` carrying the *base* model's score and the check is inert — the exact
  inheritance defect. Compare the row's `aa_score_provenance` against the landscape's own
  `intelligenceIndex`, not slug presence.
- **`mix-declared` (`validate.py:1068`)** accepts any non-empty string; its own docstring's example
  passes. Require the `traffic_mix` column present and non-empty, and reject prose that merely
  mentions cache/mix/%.
- **`cost-arithmetic` (`validate.py:238`)** resolves the token column from a fixed name list and is
  therefore **blind to the 2026-10-06 pass entirely** (it uses `tokens_m_advertised`). Make it resolve
  columns by role, so it covers every pass.
- **`unit-scale` (`validate.py:719`)** tests only `0 < tokens < MIN_PLAUSIBLE_MONTHLY_TOKENS`, so an
  *upward* magnitude error (亿 read as billion, the original defect's direction) passes.
- **`quoted-money-on-page` (`validate.py:561-564`)** sets a flag when a `**CORRECTED <date>**` marker
  appears anywhere in an entry and then stops checking the rest of that entry — so a corrected entry
  becomes uncheckable. Also: it misses every money figure whose entry line carries no `../sources/`
  link, and mis-attributes the ones it does catch. Fix the scoping and the attribution.

## 2. Two more checks do less than the docs claim

- **`fetch-log-corroborates` (`validate.py:307`)** verifies only that `url`/`http`/`sha256` *keys*
  exist. It hashes nothing. Meanwhile `2026-10-06/sources/reddit-r-opencode-search.xml` (73kB) has
  **no fetch-log entry at all**, and deleting the whole log still passes the gate. Make the check
  actually recompute each recorded SHA-256 against the archived file and fail on a mismatch or a
  missing entry for a cited source.
- **`evidence-label` (`validate.py:279`)** accepts any `source_url` as evidence; `report-matches-data`
  (`validate.py:327`) matches only one syntactic form; `ladder-price-on-page` silently skips
  `Kilo Individual` because the page contains many other `0`s. Tighten or scope each honestly, and
  make the docstrings match the behaviour.
- Enforce the repo's declared **evidence-class vocabulary**
  (`FIRST-PARTY-COMPUTED | FIRST-PARTY-PRICE-ONLY | MEASURED | DOCUMENTED | THIRD-PARTY | UNKNOWN`).
  Five rows currently use classes outside it.

## 3. A fabricated provenance string was added in the fix round

`2026-10-06/data/plan-economics.csv:9` carries an `aa_score_provenance` value asserting a leaderboard
lookup that did not happen on that date. This is the same class of defect as the fabricated quotation
you just fixed, introduced while fixing it. Remove it, and add a check that a provenance string
cannot assert a dated measurement absent from `fetch-log.json`.

## 4. Numbers that do not reproduce

Recompute each from the archived bytes and correct:

- **`plan-economics.csv:17`** (the Go Plus row) is self-inconsistent in `usd_per_mtok`, and the README
  exhibit that matches it is wrong. Decide it against the corrected reading and make prose and number
  agree.
- **`blended_usd_per_mtok` for GPT 6 Luna** is not the blend of its own price row.
- **`pool-meter-reports.csv:15`** is off by one token-million.
- **"the $1,335 across 37 ceilings"** is wrong: 38 ceilings, $1,365. Correct it wherever it appears.
- **A model above the capability bar is recorded as `notFound`.** One AA lookup row carries a score of
  **39.5759**, above the pass's own 39.4562 bar, yet is marked absent from the board. The `notFound`
  claim for `muse-spark-1-2-contributor` is genuinely correct — keep it — but the above-bar row must
  be resolved, not left contradictory.
- **"every multiplier in this market is below 2x"** contradicts the pass's own measurement table.
- **The headline count "14" qualifying rows is not derivable** from the data (the count is 15 or 12
  depending on the filter). Publish the filter and the count together so they reconcile.
- **§3's row count is wrong**: 14 rows qualify, not 13, and the "eight omitted" is seven.

## 5. The negative result overstates itself in its own headline

**Two of the four "lanes [that] clear 10,000M" do not clear 10,000M.** Fix the headline so it states
only what the table supports. The conclusion (no plan clears the bar at ≤$10 on a *verified* model)
still stands on the unscored-SKU argument — say that plainly instead of padding the count.

Check the whole pass for the same overstatement after fixing: the §0 headline, §1's wall, §5's mix
table and the ranked field.

## 6. Corrections still incomplete across earlier passes

- **`2026-09-20/README.md` carries the "II 48.09" claim at five sites with no superseding marker.**
- **`2026-10-02/README.md`**: confirm every residual assertion of the retracted 190x and of
  Muse Spark 1.3's inherited score is marked, in every file.
- `2026-10-06/README.md:191` and `docs/reviews-2026-10-06.md` cite CSV paths that do not exist
  (`agents-universe.csv`, `providers-database.csv` in the wrong pass). Fix every path.
- Root `README.md:12` says 7 malformed rows across three files; `validate.py:14-16` says four files,
  38 rows. Reconcile.

## 7. Docs that describe code that does not do what they say

- **`tools/validate.py` docstring describes six checks; fifteen are registered.** Update it, and make
  the count self-consistent with the `CHECKS` dict.
- **`parse-aa-scores.py`** does not do what its docstring says on the very page that motivated it
  (it returns 0 where the docstring says non-zero). Fix behaviour or docstring; they must agree.
- **`fetch-community.py`** returns success for a query that was never executed in `--mode new`. It
  must refuse, not succeed.
- **`parse-opencode-go.py:61`** defaults to `raw/opencode-go.html`, a path that does not exist here,
  and `.gitignore` hides `research-raw/`. Make the default correct or require an explicit argument.
- **`CheckUsageLimits`** is cited as the pre-request middleware, but `grep -rn` finds only its own
  definition — it is dead code. The real path is `ValidateAndCheckLimits`
  (`subscription_service.go:1005`) called from `api_key_auth.go:239,247`. Fix the citation.

## 8. Review-file and method-note hygiene

- **`docs/reviews-2026-10-06.md` demonstrates nine checks against `_plants/` paths that were never
  committed** (lines 677, 738, 773, 785, 801, 812, 827, 839 and others). A reader cannot re-run them.
  Either commit the plant fixtures under a reproducible path with a script that creates them, or
  inline the exact commands and mutations so they can be re-created.
- **`method-notes.md:19-23` publishes undated measurements against an undated surface.** Date them and
  mark which are reproducible.
- **Record the one finding you reject, with evidence.** A review file that records no rejection reads
  as unreviewed.
- One commit message claims a CI check is green while §5.5 of the review says it cannot run on this
  platform. Make the commit-message claim and the review agree.

---

## Requirements

1. `python3 tools/validate.py --all` exits 0; paste the output.
2. Each finding above is FIXED or REJECTED-with-evidence, numbered, with file:line.
3. Each strengthened check demonstrates a refusal **and** an acceptance with commands and exit codes.
4. The plant fixtures used for demonstrations are committed and reproducible by a reader.
5. Commit on `pass-2026-10-06`. Do not push. Do not open a PR.

Report: commit hash; `validate.py --all` output; numbered findings with status and file:line;
anything not completed with the reason.
