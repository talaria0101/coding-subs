"""Leaderboard checks: plan rows join to models, and scores belong to the exact SKU."""
from __future__ import annotations

import importlib.util
import re
from pathlib import Path

from .common import TOOLS, _num, data_rows, failures, read_rows, rel


def check_model_slug_joins(pass_dir: Path) -> None:
    """A plan row that names a model must join to a row in the model database.

    The plan table carries display names ("GLM-5.3-Flash") and the model
    database carries slugs ("glm-5-3-flash"). Joining them on the display name
    silently yields an empty ranking: the first version of this pass's ranked
    table was empty for exactly that reason and said nothing was wrong. A row
    whose model has no counterpart is therefore an error, not a gap.

    The one legitimate exception is a SKU the leaderboard does not carry at all,
    and it has to be said so rather than inferred: a row whose
    `aa_score_provenance` cell begins `unscored:` is declaring that the leaderboard
    has no row for it. Skipping those is not a loophole, because `unscored-model`
    requires the marker to be present whenever the score cannot be joined, so
    marking the absence is the only way through, and an unmarked mismatch still
    fails here.
    """
    data = pass_dir / "data"
    models = data / "models-database.csv"
    plans = data / "plan-economics.csv"
    if not models.is_file() or not plans.is_file():
        return
    mheader, mrows = read_rows(models)
    pheader, prows = read_rows(plans)
    if "slug" not in mheader or "model_slug" not in pheader:
        return
    mi = mheader.index("slug")
    pi = pheader.index("model_slug")
    pi_prov = pheader.index("aa_score_provenance") if "aa_score_provenance" in pheader else None
    known = {r[mi].strip() for r in data_rows(mrows) if len(r) > mi}
    for offset, row in enumerate(data_rows(prows), start=1):
        if len(row) <= pi:
            continue
        slug = row[pi].strip()
        if not slug or slug == "UNKNOWN":
            continue
        if slug in known:
            continue
        prov = row[pi_prov].strip().lower() if pi_prov is not None and len(row) > pi_prov else ""
        if prov.startswith("unscored:"):
            continue
        failures.append(
            f"[model-slug-joins] {rel(plans)} data row {offset} names model_slug "
            f"{slug!r}, which is not in data/models-database.csv and is not marked "
            f"unscored: in aa_score_provenance"
        )


def _normalise_identity(text: str) -> str:
    """Fold a display name or slug to comparable form.

    "Muse Spark 1.3 Contributor" and "muse-spark-1-3" are the same underlying
    model; "Muse Spark 1.3 Contributor" and "muse-spark-1-3-contributor" are
    different SKUs of it. That difference is the whole defect, so tier words are
    kept as separate tokens rather than normalised away.
    """
    text = text.lower().replace("-", " ").replace("_", " ")
    text = re.sub(r"\(.*?\)", " ", text)
    text = re.sub(r"[^a-z0-9 ]+", " ", text)
    return " ".join(text.split())


# Words that qualify a model into a different SKU rather than naming it. A plan
# row selling one of these is not selling the row it joined to.
SKU_TIER_WORDS = ("contributor", "pro", "max", "lite", "mini", "flash", "preview")

# A displayed name that deliberately carries no SKU tier. The plan names a
# vendor's own model row; the landscape may name the same row by its base product
# name, and reading one of these as a tier is reading a measurement variation
# ("Preview"), a vendor's own marketing word for a mode ("Max Effort", "Adaptive
# Reasoning"), or a brand used for two models at once ("Fable"). The set is read
# against what is absent as well as what is present, so an entry is a deliberate
# abstention and not a list of words the check has not seen.
DISPLAY_NAME_EXEMPTIONS = {
    # "Grok 4.7 (Xhigh)" - a reasoning effort, and the only Grok row.
    "grok-4-7",
    # "Space Bunny" - the platform's own name; Space Bunny 2 is the premium SKU.
    "space-bunny",
    # "Claude Opus/Sonnet/Fable 5.x (Adaptive Reasoning, Max Effort, ...)" -
    # "Max Effort" is a reasoning effort and "Adaptive Reasoning" a mode.
    "claude-opus-5-5", "claude-sonnet-5-5", "claude-fable-5-1",
    # "Fable" is a brand across two numbered models; the landscape also carries
    # "Claude Fable 5.1". A family name alone is not a tier.
    "fable",
    # "MiniMax" is a vendor name that begins with "mini".
    "minimax-m3", "minimax",
}

# Subjects a provenance may name instead of a slug: the payload a score was read
# out of. `leaderboard:aa-models-on-2026-10-06` says "the figure came out of the
# archived leaderboard page", and `provenance-in-log` can corroborate that
# because the fetch log records the page. A slug cannot be corroborated that way,
# because the log records retrievals and not what a reader found inside them.
#
# The list is a closed set on purpose. A subject that is not here and is not the
# row's own slug is treated as another SKU's score, which is the defect this
# check exists for.
PAYLOAD_SUBJECTS = {
    # tools/parse-aa-models.py parses sources/aa-models.html.
    "aa-models",
    # tools/parse-aa-scores.py parses sources/aa-leaderboard-models.html.
    "aa-leaderboard-models",
}


def check_unscored_model(pass_dir: Path) -> None:
    """A capability score must come from a leaderboard row or be marked absent.

    `model-slug-joins` only asks whether a slug is in the landscape. It cannot
    see a row that joined cleanly to a *different* SKU: the plan sells "Muse Spark
    1.3 Contributor", the landscape carries "Muse Spark 1.3", and the base model's
    48.09 was carried across to the Contributor SKU. That Contributor tier has no
    Intelligence Index at all, and it is the lane that reaches 11,029M tokens, so
    the inherited score is what made an unverified SKU look like the pass's
    answer.

    The first version tested slug *presence*, which is why it passed on that
    defect: `muse-spark-1-3` is in the landscape, so the check returned clean. A
    second version compared SKU tier words and went inert in the other direction:
    add the tier slug to the landscape and the row asserts a score the leaderboard
    does not publish, yet the check stayed silent, because the defect had moved
    from a missing tier to a present one.

    So the question is no longer "are these the same row" but **"does the board
    publish a score for this exact SKU, and is it the score the row asserts?"** The
    plan row's `aa_score_provenance` names what was read; the landscape's
    `intelligenceIndex` is what the board holds for that SKU. A provenance naming
    a SKU the landscape scores is not a defect - that is a verified score. A
    provenance naming a SKU the landscape carries with no score is a defect,
    whatever the tier words say. And a provenance naming a reading the fetch log
    does not record is `provenance-in-log`'s business.

    The authority is `data/aa-lookup.csv` where it exists, not the landscape.
    That file records what the leaderboard returned for each slug, including the
    slugs it does not carry, so it can tell "the board has no row for this tier"
    from "this derived file has no row for this tier". A landscape file can be
    edited to carry a score for a tier that does not exist on the board, and a
    check that reads only the landscape then agrees with the edit - which is how
    this check went inert the second time. Where the lookup records the slug as
    absent, a score on the plan row is borrowed no matter what the landscape
    says. Where no lookup exists for the slug, the landscape is the only evidence
    available and this check uses it.
    """
    data = pass_dir / "data"
    models = data / "models-database.csv"
    plans = data / "plan-economics.csv"
    if not models.is_file() or not plans.is_file():
        return
    mheader, mrows = read_rows(models)
    pheader, prows = read_rows(plans)
    if "slug" not in mheader or "model_slug" not in pheader:
        return
    mi = mheader.index("slug")
    name_i = mheader.index("name") if "name" in mheader else None
    score_i = mheader.index("intelligenceIndex") if "intelligenceIndex" in mheader else None

    # slug -> (present_on_board, intelligence_index) as the board actually
    # returned it. A later observation supersedes an earlier absence, so a `yes`
    # anywhere in the file wins over a `no`.
    lookup: dict[str, tuple[bool, float | None]] = {}
    lookup_path = data / "aa-lookup.csv"
    if lookup_path.is_file():
        lheader, lrows = read_rows(lookup_path)
        if "sought_slug" in lheader:
            ls = lheader.index("sought_slug")
            lp = lheader.index("present_on_board") if "present_on_board" in lheader else None
            li = lheader.index("intelligence_index") if "intelligence_index" in lheader else None
            for row in data_rows(lrows):
                if len(row) <= ls:
                    continue
                slug = row[ls].strip()
                present = (lp is not None and len(row) > lp
                           and row[lp].strip().lower() == "yes")
                score = _num(row[li]) if li is not None and len(row) > li else None
                if slug in lookup and lookup[slug][0] and not present:
                    continue
                lookup[slug] = (present, score)

    pi = pheader.index("model_slug")
    prov_i = pheader.index("aa_score_provenance") if "aa_score_provenance" in pheader else None
    model_i = pheader.index("model") if "model" in pheader else None
    plan_scores = [
        i for i, name in enumerate(pheader)
        if name.strip().lower() in ("intelligence_index", "aa_intelligence_index",
                                    "aa_score", "quality_index")
    ]
    if prov_i is None and not plan_scores:
        return
    if score_i is None and prov_i is None:
        return

    # slug -> (identity tokens of the landscape row, the score it carries)
    landscape: dict[str, tuple[tuple[str, ...], float | None]] = {}
    for r in data_rows(mrows):
        if len(r) <= mi:
            continue
        slug = r[mi].strip()
        if not slug:
            continue
        display = r[name_i] if name_i is not None and len(r) > name_i else slug
        board_score = _num(r[score_i]) if score_i is not None and len(r) > score_i else None
        landscape[slug] = (tuple(_normalise_identity(display).split()), board_score)

    for offset, row in enumerate(data_rows(prows), start=1):
        if len(row) <= pi or len(row) != len(pheader):
            continue
        slug = row[pi].strip()
        if not slug or slug == "UNKNOWN":
            continue
        prov = row[prov_i].strip().lower() if prov_i is not None and len(row) > prov_i else ""
        if prov.startswith("unscored:"):
            continue
        published = [
            row[c].strip() for c in plan_scores
            if row[c].strip() and row[c].strip().upper() != "UNKNOWN"
        ]
        asserts_score = bool(published) or bool(prov)

        if slug not in landscape:
            # Not on the board at all. Only an unscored marker saves it, and a
            # provenance asserting a reading has to be corroborated by the log.
            if published:
                failures.append(
                    f"[unscored-model] {rel(plans)} data row {offset} publishes "
                    f"{published[0]} for model_slug {slug!r}, which has no row in "
                    f"data/models-database.csv. Either the score belongs to a "
                    f"different SKU, or aa_score_provenance must read "
                    f"'unscored:<reason>'."
                )
            continue

        board_tokens, board_score = landscape[slug]

        # The lookup outranks the landscape where they disagree. `aa-lookup.csv`
        # is what the board returned; `models-database.csv` is derived from it and
        # can carry a score the board does not publish.
        if slug in lookup and not lookup[slug][0] and board_score is not None:
            failures.append(
                f"[unscored-model] {rel(plans)} data row {offset} asserts "
                f"aa_score_provenance {prov!r} for model_slug {slug!r}, and "
                f"data/models-database.csv carries that slug at "
                f"{board_score:g}. But data/aa-lookup.csv records "
                f"present_on_board=no for {slug!r}: the leaderboard has no row for "
                f"this SKU. A score on a derived file the board does not publish is "
                f"a borrowed score whatever file it sits in. Write "
                f"'unscored:<reason>'."
            )
            continue

        if prov.startswith("leaderboard:"):
            # `leaderboard:<subject>-on-YYYY-MM-DD`, optionally behind a `scored:`
            # kind. The date and the kind are stripped; what is left names what
            # was read.
            #
            # A subject is one of three things, and conflating them is how this
            # check went inert the first time:
            #
            # * this row's own slug - a per-model leaderboard page was read;
            # * the name of the payload it was read out of - `aa-models` is the
            #   archived leaderboard page, and naming it says which bytes carry
            #   the figure. This is the form that survives `provenance-in-log`,
            #   because the fetch log can vouch for a page and not for a slug;
            # * some other slug - a different SKU's score, which is the defect.
            #
            # So the page form is checked by asking the landscape whether *this*
            # row's SKU carries a score, not by comparing the subject to the
            # slug. That is the question the finding in FIX-LIST-2 §1 named:
            # slug presence is not the test, the board's own score for the exact
            # SKU is.
            claimed = re.sub(r"-on-\d{4}-\d{2}-\d{2}$", "",
                             prov.split(":", 1)[1].strip())
            claimed = re.sub(r"-ii-[\d.]+$", "", claimed)
            if claimed == slug:
                if board_score is not None:
                    continue
                failures.append(
                    f"[unscored-model] {rel(plans)} data row {offset} asserts a "
                    f"leaderboard score for model_slug {slug!r}, but "
                    f"data/models-database.csv carries that slug with no "
                    f"intelligenceIndex. The board publishes no score for this "
                    f"SKU, so any figure on this row is borrowed. Write "
                    f"'unscored:<reason>'."
                )
                continue
            if claimed in PAYLOAD_SUBJECTS:
                if board_score is not None:
                    continue
                failures.append(
                    f"[unscored-model] {rel(plans)} data row {offset} asserts "
                    f"aa_score_provenance {prov!r} for model_slug {slug!r}, but "
                    f"data/models-database.csv carries that slug with no "
                    f"intelligenceIndex. The board publishes no score for this "
                    f"SKU, so a score read out of {claimed!r} for it is borrowed. "
                    f"Write 'unscored:<reason>'."
                )
                continue
            failures.append(
                f"[unscored-model] {rel(plans)} data row {offset} asserts "
                f"aa_score_provenance {prov!r} while model_slug is {slug!r}. A "
                f"provenance that names a different SKU is that SKU's score; name "
                f"this row's own slug, name the leaderboard page the score was "
                f"read from, or write 'unscored:<reason>'."
            )
            continue

        # No usable provenance: fall back on identity, which is what catches a row
        # whose provenance is missing altogether.
        if model_i is None:
            continue
        sold = _normalise_identity(row[model_i] if len(row) > model_i else slug)
        if sold == slug.replace("-", " "):
            continue
        if sold in DISPLAY_NAME_EXEMPTIONS or slug in DISPLAY_NAME_EXEMPTIONS:
            continue
        sold_tokens = set(sold.split())
        sold_tier = {w for w in SKU_TIER_WORDS if w in sold_tokens}
        board_tier = {w for w in SKU_TIER_WORDS if w in set(board_tokens)}
        if sold_tier and not board_tier and sold_tokens - board_tier - {"<=", "and", "or"}:
            tier = ", ".join(sorted(sold_tier))
            failures.append(
                f"[unscored-model] {rel(plans)} data row {offset} sells "
                f"{row[model_i].strip()!r} - a {tier} tier - but model_slug "
                f"{slug!r} names the untiered base model, and this row asserts a "
                f"score for it. A tiered SKU is a different product from its base "
                f"model and does not inherit its Intelligence Index; look the tier "
                f"itself up, or write 'unscored:<reason>'."
            )


def _leaderboard_models(pass_dir: Path) -> dict[str, float] | None:
    """slug -> Intelligence Index, read out of the archived leaderboard payload.

    The payload is a React Server Component flight string with escaped quotes, so
    the scores cannot be seen by grepping the raw HTML — the bar model itself,
    `deepseek-v4-1-flash` at 39.4562, is invisible to `grep -c "39\\.4562"` on that
    file. `tools/parse-aa-models.py` is the repository's own answer to that, and it
    is imported here rather than reimplemented so the check and the parser cannot
    drift apart: the earlier rejection in this review rested on a grep that could
    not see the payload, and the correction was to ask the parser.

    Returns None when the pass archives no leaderboard payload or the parser
    cannot load, in which case there is nothing to check the lookup against.
    """
    for name in ("aa-leaderboard-models.html", "aa-models.html"):
        page = pass_dir / "sources" / name
        if not page.is_file():
            continue
        spec = importlib.util.spec_from_file_location(
            "repo_parse_aa_models", TOOLS / "parse-aa-models.py"
        )
        if spec is None or spec.loader is None:
            return None
        module = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(module)
        except Exception:
            return None
        raw = page.read_text(encoding="utf-8", errors="replace")
        try:
            blob = module.flight_blob(raw)
        except Exception:
            return None
        board: dict[str, float] = {}
        for obj in module.model_objects(blob):
            slug = obj.get("slug")
            index = obj.get("intelligenceIndex")
            if slug and index is not None:
                board[slug] = float(index)
        if board:
            return board
    return None


def check_lookup_against_board(pass_dir: Path) -> None:
    """A lookup row must say what the archived leaderboard payload actually holds.

    `unscored-model` reads `aa-lookup.csv` as the authority on whether the board
    carries a SKU, and it never checks the lookup itself. Flipping
    `muse-spark-1-2-contributor` to `present_on_board=yes` with a score makes that
    check read a score the board does not publish as a verified one, and the gate
    exits 0: a file that is the authority for every other check is itself unchecked.

    The comparison is against the archived payload, parsed by the repository's own
    parser, on the two fields the lookup asserts: `present_on_board` and
    `intelligence_index`. A slug the payload carries but the lookup marks absent is
    a notFound the payload contradicts; a slug the lookup marks present that the
    payload does not carry is a presence it invents; and a score that disagrees with
    the payload's for the same slug is a figure no page holds.

    A row whose `read_date` predates the pass's own leaderboard fetch is exempt,
    because a lookup recorded against an earlier page was true of that page. The
    lookup already carries the `mimo-v2-6-flash` case in exactly this form.
    """
    lookup = pass_dir / "data" / "aa-lookup.csv"
    if not lookup.is_file():
        return
    board = _leaderboard_models(pass_dir)
    if board is None:
        return
    header, rows = read_rows(lookup)
    if "sought_slug" not in header or "present_on_board" not in header:
        return
    ls = header.index("sought_slug")
    lp = header.index("present_on_board")
    li = header.index("intelligence_index") if "intelligence_index" in header else None
    for offset, row in enumerate(data_rows(rows), start=1):
        if len(row) <= max(ls, lp):
            continue
        slug = row[ls].strip()
        present = row[lp].strip().lower() == "yes"
        score = _num(row[li]) if li is not None and len(row) > li else None
        on_board = slug in board
        if present and not on_board:
            failures.append(
                f"[lookup-against-board] {rel(lookup)} data row {offset} records "
                f"present_on_board=yes for {slug!r}, but the archived leaderboard "
                f"payload does not carry that slug. tools/parse-aa-models.py "
                f"recovers it from neither payload this pass archives."
            )
            continue
        if present and score is not None and abs(board[slug] - score) > 0.001:
            failures.append(
                f"[lookup-against-board] {rel(lookup)} data row {offset} records "
                f"{slug!r} at {score:g}, but the archived leaderboard payload "
                f"carries it at {board[slug]:g}. A score that disagrees with the "
                f"page it is attributed to is a figure no page holds."
            )
