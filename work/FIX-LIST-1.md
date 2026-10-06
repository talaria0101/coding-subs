# Fix list — round 1

Three adversarial reviews ran against branch `pass-2026-10-06` @ `b14c893`. Every finding below was
independently confirmed against the repo's own archived bytes by me before dispatching you.
Fix all of them. Do not leave a finding unaddressed without a written reason why not.

Read `docs/reviews-2026-10-06.md` first — it is your own file and you will be adding to it.
The repo's rules: `python3 tools/validate.py --all` must exit 0. Every number needs a fetched URL,
an access date, a verbatim quote and an evidence class. `UNKNOWN` is a valid answer; never estimate.

---

## A. Fabricated source quotation — fix this first

**`2026-10-06/references/references.md` R5 misquotes the DeepSeek price table.** It states off-peak
"$0.007 cache hit / $0.22 input miss / $0.66 output" and peak "$0.014 / $0.44 / $1.32". The page
(archived at `sources/deepseek-pricing.html`, sha256 `210f1022…`, and byte-identical live today)
actually publishes:

```
1M INPUT TOKENS (CACHE HIT)   OFF-PEAK $0.003  $0.022   PEAK $0.006  $0.044
1M INPUT TOKENS (CACHE MISS)  OFF-PEAK $0.15   $0.66    PEAK $0.3    $1.32
1M OUTPUT TOKENS              OFF-PEAK $0.6    $1.98    PEAK $1.2    $3.96
```

$0.007, $0.22, $0.014 and $0.44 are not on the page. Fix the quotation, then fix every number
derived from it: the $0.01559/M official blended rate, "$155.90 for 10B" and its 15.6x, the peak
$0.03118/M / $311.80 / 31.2x, and Fenno's 3.30x ratio. The correct official off-peak blended rate is
**$0.00966/M** — the value the pass already uses correctly in `plan-economics.csv`. The corrected
multiples are 9.7x (not 15.6x) and 19.3x (not 31.2x), and Fenno's true ratio is **5.33x** (0.05152 /
0.00966). Check every downstream consequence, including the README's "9.7x–15.6x" range.

**Then fix the structural cause:** `check_ladder_prices_on_page` is exactly the right check and
already exists in `validate.py`, but it returns early unless `data/plan-ladder.csv` exists, and only
`2026-10-02` has one — so the check is not wired to the pass that needed it. Extend it (or add a
sibling check) so a money figure quoted in `references/*.md` is verified against the archived source
it cites, in every pass. That is worth more than the patch.

## B. An arity-preserving column shift in the relay table

**`2026-10-06/data/relay-providers.csv:16` (PPToken)** is missing the empty `ratio_to_official` cell
and its `notes` field contains an unquoted comma. Two errors that cancel in arity, so `field-count`
passes and `validate.py --all` exits 0 — while every value from index 10 onward sits in the wrong
column: `ratio_to_official='no'`, `rankable='No public rate card…'`,
`measured_exclusion_reason='THIRD-PARTY'`, `evidence_class='https://api.pptoken.cc'`,
`source_url='2026-10-06'`, `read_date='Self-serve purchase page exists…'`.

Quote the notes field, restoring the empty cell. `docs/reviews-2026-10-06.md:293-298` claims
"field-count fired on one row… with a missing empty cell" as a FIXED defect — it is not fixed, only
hidden. Correct that claim. **Then harden `field-count`**: a row whose field count is right but whose
*values* contradict their header names (a URL in an evidence-class column, a date in a source column)
must also fail. An arity-preserving shift defeats the current check entirely.

## C. The shared-pool exhibit contradicts its own cited page

`2026-10-06/README.md` and `docs/reviews-2026-10-06.md` present as "the cleanest evidence available
and it is first-party" that *Go Plus raises the price 4x while the DeepSeek per-model cap rises only
2x ($60 → $60 against a $120 pool)*.

The archived page says otherwise — `sources/opencode-go.md:178` is `$60` under Go and **line 223 is
`$120` under Go Plus**. The published monthly limit doubles cleanly. There is no separate pool figure
anywhere on the page. So the "$60 against a $120 pool" is an assumption, and it is the assumption
carrying the conclusion. Under the additive reading the cap also doubles, so both readings predict
the same table and this row is not decisive evidence.

Restate it accurately: the published per-model limit for DeepSeek doubles ($60 → $120) while the
price quadruples, so $/M worsens 2x under either reading; whether $120 is a pool the other models
divide or an independent per-model budget is the open question. Demote it from "decisive
first-party evidence" to "consistent with, not decisive".

**And fix the row that encodes it:** `2026-10-06/data/plan-economics.csv:17` states
`monthly_pool_usd=120, per_model_cap_usd=60` yet `tokens_m_advertised=12423`, and
12423 × 0.00966 = **$120.00** — the full pool, ignoring the cap on the same row. Under the pass's own
`min()` model the value is **6,211**. The row's own notes cell says "the per-model cap is $60 on a
$120 pool, so min() takes the $60", which its number contradicts. Decide the row correctly against
the corrected reading above and make the prose and the number agree.

## D. Four new checks that do not fire on the defects they were written for

Each was demonstrated only by a plant that does not match the real failure shape. Test each against
the real shape, fix it, and re-demonstrate.

- **`unscored-model` (`validate.py:524`)** tests whether the *slug* is absent from
  `models-database.csv`. The actual 2026-10-02 defect was a plan row selling the **Contributor** SKU
  whose `model_slug` pointed at the **base** model — which IS in the database, so the check passes
  (exit 0, verified). The check must compare the plan row's displayed model/SKU identity against the
  landscape row's identity, not just slug presence.
- **`unit-scale` (`validate.py:464`)** only compares enumerated *pairs* of token columns, so it
  cannot fire when the file has one token column — which is the common case and the real 亿 shape.
  It also passes a `monthly_tokens_b` column it does not know about carrying an 11.029-vs-11029
  (1000x) error. Make it catch a single-column magnitude error and any unit column outside its list.
- **`mix-declared` (`validate.py:672-686`)** is satisfied by the substring "cache", "mix" or "%"
  appearing *anywhere* in the notes. A row reading "Vendor caches nothing beyond the discounted tier"
  passes. Require the `traffic_mix` column to be present and non-empty; nothing else should count.
- **`shared-cap` (`validate.py:636`)** short-circuits on the bare token "pool" appearing in free-text
  notes, so a row whose `cap_model` literally reads `PER-MODEL` passes if its notes mention "pool".
  `cap_model` must be authoritative; drop the bare "pool" fallback.

Every one must refuse a realistic wrong dataset AND accept correct input, with both commands and
exit codes in the review file.

## E. Unscored-SKU count is wrong, and two SKUs were never looked up

`README.md:68-71` says the *only two* prices at or below $0.0028/M are the two models the leaderboard
does not carry. The archived grid has **four**: Muse Spark 1.3 Contributor ($0.002), **Muse Spark 1.2
Contributor ($0.002)**, MiMo-V2.6-Flash ($0.0028), **MiMo-V2.5 ($0.0028)**. Neither
`muse-spark-1-2-contributor` nor `mimo-v2-5` was looked up. The stronger claim (all four cheapest
lanes are unscored) happens to be true, so the conclusion survives — but the stated evidence is
false. Fix the count, list all four, look up the two missing SKUs, and note that two were missed,
which weakens rather than strengthens the claim that the absence is structural.

`Muse Spark 1.2 Contributor` is material: same price, same $60 cap, same 11,029M yield. The claim
"the only lane above 10,000M" is false on the pass's own archived page.

## F. `plan-economics.csv:17` also omits a $0 lane

`LongCat 2.5 Preview Free` is priced Free/Free/Free with an unlimited limited-time ceiling. It does
not clear the bar, so the negative result stands — but a lane with a **$0** ceiling must be addressed
in a structural negative-result argument. Add it, state why it fails, and fix
`plan-economics.csv:8`'s "the only lane in the market above 10,000M".

## G. Overstated completeness and an unattested headline

- **`README.md:128`** claims "**Every** plan × model where a first-party ceiling and a leaderboard
  score both exist". Twelve CSV rows satisfy that predicate; six are shown. Either add the rows or
  state the filter. The omitted set includes the market's second-largest qualifying lane.
- **`README.md:42-48` / §0**: the 5,000M wall is a 100%-cache upper bound, but no plan produces
  100% cache reads, and the pass's own audited mix (97%) gives 1,838M for the same SKU. State both
  bounds in §0 where the headline lives, not only in §1.
- **`README.md:32`** asserts "Confidence: HIGH on every price and cap" unqualified. Given A and the
  Fenno finding below, that is not supportable. Restate it.
- **`README.md:62` / `:256`** says the gate enforces "eight things"; `validate.py` registers 13
  checks. Make the prose match the code.
- **`plan-economics.csv:10`** stores `tokens_m_measured=2900`; `pool-meter-reports.csv:11` and
  `README.md:25` say 2,899. Pick one and derive the other.

## H. Unsourced figure and a wrong line citation

- **`relay-providers.csv:15`** marks Fenno's ceiling `yes - 100B tokens/day claimed` as first-party.
  The cited source (`sources/fenno-models.json`, verified) contains no such figure, and `fenno.ai`
  fetched live has zero hits for `100B`/`Billion`/`亿`. Either find a real source or downgrade it to
  THIRD-PARTY/UNKNOWN with the claim attributed.
- **`account.go:1695`** is the wrong line for the TLS-fingerprint gating; the function is
  `IsTLSFingerprintEnabled()` at `account.go:2422`. Fix the citation; the substance is correct.
- **`docs/reviews-2026-10-06.md`** attributes the 45.3x multiplier to a file that does not contain
  it (`adopted.csv` has zero hits for 45.3; it appears in `claude-adoption-round10-2026-09-25.json` as
  a token count, and $9,060 appears nowhere). Re-attribute or drop.

## I. Evidence class one notch too strong

`plan-economics.csv:18-19` (Z.ai Lite rows) carry `FIRST-PARTY-COMPUTED` on the blended $/M column.
The archived page publishes no $/Mtok, and one identical value `0.03530` is printed for two models
whose real ratios differ 3x (`18/1264 = 0.01424`, `18/420 = 0.04286`). Reclassify per the repo's own
ladder and fix the value.

## J. Residual assertions of the retracted figure

`docs/reviews-2026-10-06.md:24` claims both 2026-10-02 documents carry a superseding note. True for
§7, **false for §1–§4**. `2026-10-02/README.md` still asserts at line 422 ("Published results are
SuperGrok 190x ±21"), at 447-448 ("its headline 190x…"), and at lines 29/30/47/64/364/394 prints
**`Muse Spark 1.3` at II 48.09 / $0.0009/M** in its ranked table — the base model's name on a row that
now carries the Contributor SKU in the CSV, and the base model's inherited score. That is the same
inheritance error this pass exists to fix, uncorrected in prose. Mark the 190x occurrences at every
site and correct the prose to the Contributor SKU's unscored status. Also `2026-09-20/README.md:64`
still asserts the superseded "up to ~$60/mo of list-value usage" unmarked, and the `~6× face` row it
marks SUPERSEDED was never 6× — the sum of all 37 per-model ceilings is $1,335 against a $10 plan.

## K. Structure and editorial fixes

- **The relay standard has no home in the report.** `2026-09-20/README.md:290` points the reader to
  "`../2026-10-06/README.md` **§7**" for the relay measurement standard. §7 is "What would falsify
  this pass". Add a section carrying the standard and the four verdicts, and fix the pointer.
  `relay-providers.csv:18` leaves `rankable` blank for Sub2api, so "0 of 4 are rankable" counts a
  blank verdict.
- **`method-notes.md:4`** contains the self-referential process narration "No host details, no session
  history." Delete it.
- **`docs/reviews-2026-10-06.md` §5.5** is host/environment-specific throughout — "on this host",
  `/tmp/` paths, "Windows will hit it and conclude CI is broken". The finding is sound and worth
  keeping, but reframe it as a portability caveat on the gate and make the command transcripts
  re-runnable on any platform.
- **`data/fetch-log.json`** is presented as the complete retrieval record, but `method-notes.md`
  reports three `r.jina.ai` measurements with no log entry and no archived artefact. Either log them
  or mark them explicitly as unlogged demonstrations. Also `method-notes.md:65` cites a tracker count
  ("3,571 open issues") that appears nowhere else — GitHub's `open_issues_count` includes pull
  requests, so verify and state the real issue count.
- **`2026-10-06/README.md:8`** lists five databases; `data/` also holds `models-database.csv`.

## L. The CI step that is red — verify the diagnosis, do not trust it

`docs/reviews-2026-10-06.md:326-344` attributes the `parse-opencode-go.py` byte-diff failure to a
Windows `\r\r\n` artefact and states the three reproducibility checks pass on Linux. They do not: the
committed `2026-10-02/data/opencode-go-grid.csv` is LF and the regenerated one is CRLF, so `diff -u`
fails on `ubuntu-latest` too. Re-verify, correct the attribution, and make the gate deterministic on
both platforms — either normalise line endings in the parser's output or make CI compare
content-normalised. Record which.

## M. A snapshot that went stale in one day

`aa-lookup.csv:13` records `mimo-v2-6-flash` as `present_on_board=no` / `notFound`. That was correct
on 2026-10-06. Today the live board carries it at **II 37.8844** — below the 39.4562 bar, so the
conclusion is unaffected, but the row is stale. Record the later observation with its date rather than
editing the dated pass silently.

Related: the repo's parser recovers 0 models from `/leaderboards/models` because it requires
`{"id":UUID,"slug":...}` while that page ships `{"slug":...}`. The claim "the live board carries 24
models" (asserted in 4 CSV cells) is a parser artefact of the `/models` page — the leaderboard payload
carries 681. Either fix the parser or correct the claim to say which page it counts.

---

## Requirements

1. `python3 tools/validate.py --all` exits 0. Paste the output.
2. Every fix above is either made or answered in writing with a reason.
3. Every new/strengthened check demonstrates both a refusal and an acceptance with command output in
   `docs/reviews-2026-10-06.md`, following the existing review-file conventions.
4. Corrections are **supersessions with dates**, never silent edits. The repo documents what is true
   on a date.
5. No narrative history, no host details, no session/agent references, no phase numbering.
6. Do not weaken an existing check to make a finding go away. If a check cannot be made to fire
   correctly, remove it and record why — a check that passes on everything is worse than none.
7. Commit on the same branch. Do not push, do not open a PR.

When done, report: the commit hash, `validate.py --all` output, a numbered list of each finding with
FIXED / PARTIAL / REJECTED and the file:line of the change, and anything you could not complete.
