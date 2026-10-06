#!/usr/bin/env python3

"""Regenerate the plant fixtures the gate is demonstrated against.



    python3 tools/make-plants.py [OUT_DIR]



Every check in `validate.py` has to be shown refusing a planted defect *and*

accepting correct data. A check that has only been seen failing cannot be

distinguished from a check that cannot pass, and a check that cannot pass is

indistinguishable from one that passes everything.



The fixtures are generated rather than committed as CSVs because each one is a

copy of real repository data with a specific cell changed. Committing the copies

would let them drift from the data they were derived from and a reader could not

tell whether the plant still demonstrates what it claims. The generator names the

pass, the file, the line, the change and the check it is meant to trip, so the

relationship between a plant and the defect it reproduces is legible without

opening either file.



`tests/run-plants.sh` regenerates them into a temporary directory, runs the gate

once per plant, and fails if a plant that is supposed to be refused passes. It

also runs an acceptance case per plant. Run it before committing any change to

`validate.py`.

"""

from __future__ import annotations



import csv

import hashlib

import io

import json

import shutil

import sys

from pathlib import Path



NL = chr(10)
ROOT = Path(__file__).resolve().parent.parent

DEFAULT_OUT = ROOT / "tests" / "plants"





def split_csv(path: Path) -> tuple[list[str], list[str], list[list[str]]]:

    lines = path.read_text(encoding="utf-8").splitlines()

    start = 0

    while start < len(lines) and lines[start].lstrip().startswith("#"):

        start += 1

    rows = list(csv.reader(io.StringIO("\n".join(lines[start:]))))

    return lines[:start], lines[start:start + 1], rows[1:]





def write_csv(path: Path, preamble: list[str], body: list[list[str]]) -> None:

    buf = io.StringIO()

    csv.writer(buf, lineterminator="\n").writerows(body)

    path.write_text("\n".join(preamble + [buf.getvalue().rstrip("\n")]) + "\n",

                    encoding="utf-8")





def set_cell(path: Path, row_key: tuple[str, ...], column: str, value: str) -> None:

    """Set one cell on the row whose leading fields equal `row_key`.



    A row is addressed by its leading fields rather than by row number so that a

    plant still means what it says when a data file gains or loses a row.

    """

    preamble, head, rows = split_csv(path)

    header = head[0].split(",")

    index = header.index(column)

    for row in rows:

        if tuple(row[: len(row_key)]) == tuple(row_key):

            while len(row) <= index:

                row.append("")

            row[index] = value

            break

    else:

        raise SystemExit(f"{path}: no row starting with {row_key!r}")

    write_csv(path, preamble, [header] + rows)





# --- each plant: (name, what it reproduces, what it must trip, build) --------





def plant_field_columns(dest: Path) -> str:
    """An arity-preserving column shift, the shape the review describes.

    One cell splits - `reputation_quantified` keeps `'yes - 43'` and the star
    count moves into `delivery_ceiling_documented` - and the `source_url` cell is
    emptied to put the count back. The row keeps 17 fields against a 17-field
    header, so `field-count` passes, and every value from the split onward sits one
    column to the left. `field-columns` refuses it because `evidence_class` ends
    up holding a URL.

    **A limit on reproducing `b14c893` byte for byte, recorded rather than
    hidden.** That row's header had four contiguous empty cells after the
    failure-mode column and no `measured_exclusion_reason`, so the split value
    landed in `rankable` and the removal came from that run of empties. This pass
    has five empties and an extra column, and the surplus comma splits a
    *quoted* cell rather than an empty run, so the file balances by appending the
    compensating empty cell at the end of the row. Same class of defect, same
    refusal, and every value from the split onward lands one column to the left -
    which is the point.
    """
    shutil.copytree(ROOT / "2026-10-06", dest / "2026-10-06", dirs_exist_ok=True)
    relays = dest / "2026-10-06" / "data" / "relay-providers.csv"
    lines = relays.read_text(encoding="utf-8").splitlines()
    sub_i = next(i for i, line in enumerate(lines) if line.startswith("Sub2api"))
    raw = lines[sub_i]
    marker = "yes - 43,351 stars; repo created 2025-12-18"
    assert marker in raw, "the Sub2api reputation cell changed"
    surplus = raw.replace(marker, "yes - 43, 349 stars; repo created 2025-12-18", 1)
    # Empty the source_url cell: one field less, and the columns after the split
    # shift left so `evidence_class` reads the URL that used to be in `source_url`.
    # Empty `measured_exclusion_reason`, the cell the surplus comma would have
    # displaced, so the arity balances and `evidence_class` ends up holding the
    # URL that used to sit in `source_url`.
    surplus = surplus.replace(",,,,", ",,,", 1) + ","
    lines[sub_i] = surplus
    relays.write_text(NL.join(lines) + NL, encoding="utf-8")
    return "field-columns"


def plant_unscored_model(dest: Path) -> str:
    """The tier slug added to the landscape, carrying the base model's score.

    This is the second shape of the inheritance defect. Add
    `muse-spark-1-3-contributor` to `models-database.csv` with the base model's
    48.0923 and the plan row asserts that score for it, and a presence test and a
    tier-word test both pass: the slug is present, and the slug is the row's own.

    What the board publishes is the question, and the answer is recorded rather
    than inferred. The 2026-10-06 and 2026-10-07 lookups both returned **notFound**
    for this SKU (`data/aa-lookup.csv`, [R21]), so the score the row asserts is the
    base model's and the correct cell says `unscored:`.

    The provenance here names `aa-models` - the archived leaderboard page, which
    `data/fetch-log.json` records - rather than the tier slug, so
    `provenance-in-log` stays silent and the finding lands where it belongs. With
    a slug-shaped subject the same plant trips two checks, and the second one
    masks whether `unscored-model` did any work: the whole point of this plant is
    that the landscape now carries the tier with a score, so nothing else should
    object.
    """
    shutil.copytree(ROOT / "2026-10-06", dest / "2026-10-06", dirs_exist_ok=True)
    models = dest / "2026-10-06" / "data" / "models-database.csv"
    preamble, head, rows = split_csv(models)
    base = next(r for r in rows if r[0] == "muse-spark-1-3")
    template = list(base)
    template[0] = "muse-spark-1-3-contributor"
    template[1] = "Muse Spark 1.3 Contributor"
    rows.append(template)
    write_csv(models, preamble, [head[0].split(",")] + rows)
    # The plan rows have to assert the score too, or there is nothing to check:
    # a row marked `unscored:` declares the absence deliberately and is correct
    # whatever the landscape carries.
    plans = dest / "2026-10-06" / "data" / "plan-economics.csv"
    for plan in ("OpenCode Go", "OpenCode Go Plus"):
        set_cell(plans, (plan, "OpenCode", "10" if plan == "OpenCode Go" else "40",
                         "Muse Spark 1.3 Contributor"),
                 "aa_score_provenance",
                 "leaderboard:aa-models-on-2026-10-06")
    return "unscored-model"


def plant_scored_no_board_row(dest: Path) -> str:
    """A plan row asserting a leaderboard score the board does not publish.

    The provenance names the page the score was read from rather than a SKU, which
    is how every `leaderboard:` row in this repository reads, and the landscape
    carries the slug with no Intelligence Index - the state of every SKU the
    leaderboard does not list, and the state the 2026-10-06 lookup recorded for
    `muse-spark-1-3-contributor`.
    """
    shutil.copytree(ROOT / "2026-10-06", dest / "2026-10-06", dirs_exist_ok=True)
    models = dest / "2026-10-06" / "data" / "models-database.csv"
    lines = models.read_text(encoding="utf-8").splitlines()
    at = next(i for i, l in enumerate(lines) if l and not l.lstrip().startswith("#"))
    rows = list(csv.reader(io.StringIO(NL.join(lines[at:]))))
    header, body = rows[0], rows[1:]
    score_i = header.index("intelligenceIndex")
    # Append the Contributor as the board does not carry it: a row with the slug,
    # the name, and no Intelligence Index. That is what `notFound` means in
    # `data/aa-lookup.csv`, and it is the state a lookup returns for every SKU
    # this pass found absent.
    blank = ["muse-spark-1-3-contributor", "Muse Spark 1.3 Contributor", "Meta",
             "2026-09-02", ""]
    body.append(blank + [""] * (len(header) - len(blank)))
    buf = io.StringIO()
    writer = csv.writer(buf, lineterminator=NL)
    writer.writerow(header)
    for row in body:
        writer.writerow(row)
    models.write_text(NL.join(lines[:at]) + NL + buf.getvalue(), encoding="utf-8")
    plans = dest / "2026-10-06" / "data" / "plan-economics.csv"
    for plan, price in (("OpenCode Go", "10"), ("OpenCode Go Plus", "40")):
        key = (plan, "OpenCode", price, "Muse Spark 1.3 Contributor")
        set_cell(plans, key, "model_slug", "muse-spark-1-3-contributor")
        set_cell(plans, key, "aa_score_provenance",
                 "leaderboard:muse-spark-1-3-contributor-on-2026-10-06")
    return "unscored-model"


def plant_cost_arithmetic(dest: Path) -> str:

    """A token count and a per-M rate that do not follow from the plan price.

    This is the defect the check is named for: three cells on one row that
    describe one quantity in three units, and one of them does not follow from
    the other two. Only the advertised token count moves, so `price / tokens` no
    longer reproduces the row's own rate.

    An earlier version of this plant shifted the token count *and* the rate
    together by 10x. That row is internally consistent, so `cost-arithmetic`
    correctly stayed silent and the plant demonstrated nothing it was named for;
    it tripped `cost-identity` instead, which is a different defect. A plant has
    to break the thing it claims to break, or it is evidence about the wrong
    check.
    """

    shutil.copytree(ROOT / "2026-10-06", dest / "2026-10-06", dirs_exist_ok=True)

    plans = dest / "2026-10-06" / "data" / "plan-economics.csv"

    set_cell(plans, ("OpenCode Go", "OpenCode", "10", "DeepSeek V4.1 Flash (off-peak)"),

             "tokens_m_advertised", "621")

    return "cost-arithmetic"





def plant_mix_declared(dest: Path) -> str:

    """A derived $/M with the mix column emptied and the notes talking about mix.



    'Vendor caches nothing beyond the discounted tier' satisfies a check that

    looks for the substring "cache" anywhere in the row, and says nothing at all

    about the mix the $/M was computed under.

    """

    shutil.copytree(ROOT / "2026-10-06", dest / "2026-10-06", dirs_exist_ok=True)

    plans = dest / "2026-10-06" / "data" / "plan-economics.csv"

    set_cell(plans, ("OpenCode Go", "OpenCode", "10", "GLM-5.3-Flash"),

             "traffic_mix", "")

    preamble, head, rows = split_csv(plans)

    i = head[0].split(",").index("notes")

    for row in rows:

        if row and row[0] == "OpenCode Go" and row[3] == "GLM-5.3-Flash":

            row[i] = ("MIX ASSUMPTION: the vendor caches nothing beyond the "

                      "discounted tier; see the mix note.")

    write_csv(plans, preamble, [head[0].split(",")] + rows)

    return "mix-declared"





def plant_unit_scale(dest: Path) -> str:

    """The original defect's direction: a count multiplied by a power of ten.



    `tokens_m_advertised` is in millions, so 11,029 reads as 11,029,000,000

    tokens. Copying the cell's digits out of a `yi` note instead of converting

    them produces a count 10^6 too large, which is the direction the check's lower

    bound could not see.

    """

    shutil.copytree(ROOT / "2026-10-06", dest / "2026-10-06", dirs_exist_ok=True)

    plans = dest / "2026-10-06" / "data" / "plan-economics.csv"

    set_cell(plans, ("OpenCode Go", "OpenCode", "10", "Muse Spark 1.3 Contributor"),

             "tokens_m_advertised", "11029000000000")

    return "unit-scale"





def plant_quoted_money(dest: Path) -> str:

    """A fabricated quotation plus a second entry with no page of its own.



    The first entry quotes three figures that are not on the DeepSeek page it

    cites. The second entry quotes one, names no archived page, and must not be

    checked against the first entry's page.

    """

    dest_pass = dest / "2026-10-06"

    (dest_pass / "references").mkdir(parents=True, exist_ok=True)

    (dest_pass / "sources").mkdir(parents=True, exist_ok=True)

    shutil.copy(ROOT / "2026-10-06" / "sources" / "deepseek-pricing.html",

                dest_pass / "sources" / "deepseek-pricing.html")

    (dest_pass / "README.md").write_text("# plant\n", encoding="utf-8")

    (dest_pass / "references" / "references.md").write_text(

        "## plant\n\n"

        "**[R5] DeepSeek - API pricing** - <https://api-docs.deepseek.com/quick_start/pricing>"

        " - accessed 2026-10-06 - HTTP 200 - archived as "

        "[../sources/deepseek-pricing.html](../sources/deepseek-pricing.html).\n\n"

        "> **CORRECTED 2026-10-07.** The superseded quotation below is kept on the record.\n\n"

        "Off-peak $0.007 cache hit / $0.22 input miss / $0.66 output; "

        "peak $0.014 / $0.44 / $1.32.\n\n"

        "**[R6] a second entry naming no archived page**\n\n"

        "A figure quoted from a community post, $0.12345, with no sources/ link here.\n",

        encoding="utf-8")

    return "quoted-money-on-page"





def plant_fetch_log(dest: Path) -> str:

    """A recorded SHA-256 that is not the hash of the archived bytes."""

    shutil.copytree(ROOT / "2026-10-06", dest / "2026-10-06", dirs_exist_ok=True)

    log = dest / "2026-10-06" / "data" / "fetch-log.json"

    text = log.read_text(encoding="utf-8")

    original = "e62561c5c6fb7685fafc8bddc9634bdab3aa37c59944a56da83d103d047f7489"

    assert original in text, "opencode-go.md hash not found in the log"

    log.write_text(text.replace(original, original[:-1] + "0"), encoding="utf-8")

    return "fetch-log-corroborates"





def plant_fetch_log_orphan(dest: Path) -> str:

    """An archived source with no fetch-log entry at all."""

    shutil.copytree(ROOT / "2026-10-06", dest / "2026-10-06", dirs_exist_ok=True)

    log = dest / "2026-10-06" / "data" / "fetch-log.json"

    entries = json.loads(log.read_text(encoding="utf-8"))

    entries = [e for e in entries if "reddit-r-opencode-search.xml" not in str(e.get("saved_as"))]

    log.write_text(json.dumps(entries, indent=2) + "\n", encoding="utf-8")

    return "fetch-log-corroborates"





def plant_evidence_label(dest: Path) -> str:

    """A figure whose source is a note about a source rather than a source."""

    shutil.copytree(ROOT / "2026-10-06", dest / "2026-10-06", dirs_exist_ok=True)

    plans = dest / "2026-10-06" / "data" / "plan-economics.csv"

    set_cell(plans, ("OpenCode Go", "OpenCode", "10", "GLM-5.3-Flash"),

             "source_url", "ask me later")

    return "evidence-label"





def plant_evidence_vocabulary(dest: Path) -> str:

    """`FIRST-PARTY` in the evidence-class column: not one of the declared six."""

    shutil.copytree(ROOT / "2026-10-06", dest / "2026-10-06", dirs_exist_ok=True)

    relays = dest / "2026-10-06" / "data" / "relay-providers.csv"

    set_cell(relays, ("CCTK.AI",), "evidence_class", "FIRST-PARTY")

    return "evidence-vocabulary"





def plant_report_matches_data(dest: Path) -> str:

    """A row count and a path in the prose that the files on disk do not carry."""

    shutil.copytree(ROOT / "2026-10-06", dest / "2026-10-06", dirs_exist_ok=True)

    report = dest / "2026-10-06" / "README.md"

    text = report.read_text(encoding="utf-8")

    marker = "[data/plan-economics.csv](data/plan-economics.csv) (20 plan x model rows)"

    assert marker in text, "the row-count sentence was not found"

    report.write_text(

        text.replace(marker, "[data/plan-economics.csv](data/plan-economics.csv) "

                            "(21 plan x model rows)", 1)

            + "\nSee [data/agents-universe.csv](data/agents-universe.csv) for the roster.\n",

        encoding="utf-8")

    return "report-matches-data"





def plant_ladder_price(dest: Path) -> str:

    """A price of 0 attributed to a page with no price on it."""

    shutil.copytree(ROOT / "2026-10-02", dest / "2026-10-02", dirs_exist_ok=True)

    ladder = dest / "2026-10-02" / "data" / "plan-ladder.csv"

    preamble, head, rows = split_csv(ladder)

    index = head[0].split(",").index("extraction")

    for row in rows:

        if row and row[1] == "Kilo Individual":

            row[index] = "JSONLD"

    write_csv(ladder, preamble, [head[0].split(",")] + rows)

    return "ladder-price-on-page"





def plant_cost_identity(dest: Path) -> str:

    """The Go Plus row: a yield from the pool and a rate from the cap.



    `cost-arithmetic` cannot see this row because its three columns - plan price,

    advertised tokens, cost per million - are internally consistent. The error is

    that the advertised count came from a different dollar figure than the rate.

    """

    shutil.copytree(ROOT / "2026-10-06", dest / "2026-10-06", dirs_exist_ok=True)

    plans = dest / "2026-10-06" / "data" / "plan-economics.csv"

    set_cell(plans, ("OpenCode Go Plus", "OpenCode", "40", "DeepSeek V4.1 Flash (off-peak)"),

             "per_model_cap_usd", "60")

    return "cost-identity"





def plant_shared_cap(dest: Path) -> str:

    """`cap_model` reading PER-MODEL with the notes mentioning a pool."""

    shutil.copytree(ROOT / "2026-10-06", dest / "2026-10-06", dirs_exist_ok=True)

    plans = dest / "2026-10-06" / "data" / "plan-economics.csv"

    set_cell(plans, ("OpenCode Go", "OpenCode", "10", "DeepSeek V4.1 Flash (off-peak)"),

             "cap_model", "PER-MODEL")

    return "shared-cap"





def plant_provenance(dest: Path) -> str:
    """A provenance string asserting a reading the log does not record.

    The claim names the leaderboard page and a date later than any retrieval in
    the pass's log - the exact shape of the defect this check was written for, in
    which repairing a fabricated quotation added a provenance string asserting a
    lookup that had not happened.
    """
    shutil.copytree(ROOT / "2026-10-06", dest / "2026-10-06", dirs_exist_ok=True)
    log = dest / "2026-10-06" / "data" / "fetch-log.json"
    entries = json.loads(log.read_text(encoding="utf-8"))
    for entry in entries:
        entry.pop("read_date", None)
    log.write_text(json.dumps(entries, indent=2) + NL, encoding="utf-8")
    plans = dest / "2026-10-06" / "data" / "plan-economics.csv"
    for plan, price in (("OpenCode Go", "10"), ("OpenCode Go Plus", "40")):
        set_cell(plans, (plan, "OpenCode", price, "DeepSeek V4.1 Flash (off-peak)"),
                 "aa_score_provenance",
                 "leaderboard:deepseek-v4-1-flash-on-2026-10-06")
    return "provenance-in-log"


def plant_field_count(dest: Path) -> str:

    """A surplus unquoted comma: the defect the field-count check was added for."""

    shutil.copytree(ROOT / "2026-10-06", dest / "2026-10-06", dirs_exist_ok=True)

    plans = dest / "2026-10-06" / "data" / "plan-economics.csv"

    text = plans.read_text(encoding="utf-8")

    marker = ("The most expensive model on the plan and the most rationed: a $15 cap "

              "against a $60 pool.")

    assert marker in text, "the Kimi K3 notes cell was not found unquoted"

    plans.write_text(

        text.replace(marker, "The most expensive model, and the most rationed: a $15 cap, "

                             "against a $60 pool.", 1),

        encoding="utf-8")

    return "field-count"





def plant_lookup_against_board(dest: Path) -> str:

    """The lookup claiming a score the archived leaderboard does not hold.

    `unscored-model` treats `aa-lookup.csv` as the authority on whether the board
    carries a SKU and never checks the lookup itself, so an authority nobody
    validates is an authority that can be edited into agreement with a defect.
    This is the direction that matters: the Contributor SKU is marked
    `present_on_board=yes` with the base model's score, and `unscored-model`
    reads that as a verified score and stays silent.
    """

    shutil.copytree(ROOT / "2026-10-06", dest / "2026-10-06", dirs_exist_ok=True)

    set_cell(dest / "2026-10-06" / "data" / "aa-lookup.csv",
             ("muse-spark-1-2-contributor",), "present_on_board", "yes")

    set_cell(dest / "2026-10-06" / "data" / "aa-lookup.csv",
             ("muse-spark-1-2-contributor",), "intelligence_index", "39.5759")

    return "lookup-against-board"


def plant_no_future_pass(dest: Path) -> str:

    """A pass directory dated after the machine's clock.

    `no-future-pass` refuses a pass whose date is in the future, which is how a
    dated supersession or a typo would otherwise pass unexamined. It is the one
    check whose fixture has to be named for the day it runs: the copy below is
    dated a year out, so it trips on any clock this repository will be read on.
    """

    shutil.copytree(ROOT / "2026-10-06", dest / "2099-12-31", dirs_exist_ok=True)

    # The copy's fetch log still points `saved_as` at `2026-10-06`, which is not
    # where the bytes now live, and `provenance-in-log` falls back to the pass
    # directory's name as the read date of every entry that carries none. Under a
    # 2099 directory name that fallback postdates the provenance strings in the
    # data, so `provenance-in-log` would fire alongside the check this plant is
    # named for. Repointing the log at the plant's own directory and stamping the
    # original read date onto each entry leaves the future date as the only
    # defect, which is what the plant is for.
    log = dest / "2099-12-31" / "data" / "fetch-log.json"
    entries = json.loads(log.read_text(encoding="utf-8"))
    for entry in entries:
        entry["saved_as"] = str(entry.get("saved_as") or "").replace(
            "2026-10-06\\\\sources", "2099-12-31\\\\sources")
        entry["read_date"] = "2026-10-06"
    log.write_text(json.dumps(entries, indent=2) + "\n", encoding="utf-8")

    return "no-future-pass"


def plant_layout(dest: Path) -> str:

    """A pass directory with its `references/` removed.

    `layout` is the gate's first check and the one with no plant: every pass in
    the tree has all four directories, so nothing demonstrated it. Deleting
    `references/` is the smallest change that trips it — the check requires
    `data/`, `references/`, `sources/` and a README in each pass directory, and a
    pass without its references cannot be checked for quoted money or ladder
    prices at all.
    """

    shutil.copytree(ROOT / "2026-10-06", dest / "2026-10-06", dirs_exist_ok=True)

    shutil.rmtree(dest / "2026-10-06" / "references")

    return "layout"


def plant_model_slug_joins(dest: Path) -> str:

    """A plan row naming a model the landscape does not carry.

    `model-slug-joins` has no plant for the same reason `layout` did: every
    plan row in the tree joins, so nothing demonstrated it. Changing one
    `model_slug` to a slug that is in neither the landscape nor the lookup
    reproduces the defect it exists for — a plan row whose model cannot be
    joined, which is how a ranked table silently comes out empty.
    """

    shutil.copytree(ROOT / "2026-10-06", dest / "2026-10-06", dirs_exist_ok=True)

    # Addressed by the leading fields that identify the off-peak row. Two rows
    # share this slug, so the plan price is part of the key to land on one.
    set_cell(dest / "2026-10-06" / "data" / "plan-economics.csv",
             ("OpenCode Go", "OpenCode", "10", "DeepSeek V4.1 Flash (off-peak)"),
             "model_slug", "deepseek-v9-9-ultra")

    return "model-slug-joins"


def plant_gate_count(dest: Path) -> str:
    """The root README claiming a number of checks the registry does not hold.

    `gate-count-claims` reads the repository's own README, so the plant carries
    its own copy of it with the number changed and hands the pass directory the
    modified README as its own report.
    """
    shutil.copytree(ROOT / "2026-10-06", dest / "2026-10-06", dirs_exist_ok=True)
    wrong = ROOT.joinpath("README.md").read_text(encoding="utf-8").replace(
        "gates every pass on **twenty checks**",
        "gates every pass on **eleven checks**", 1)
    assert "eleven checks" in wrong, "the root README's check count is not where it was expected"
    (dest / "README.md").write_text(wrong, encoding="utf-8")
    (dest / "2026-10-06" / "README.md").write_text(wrong, encoding="utf-8")
    return "gate-count-claims"


PLANTS = [

    ("field-columns", plant_field_columns,

     "relay-providers.csv Sub2api row, arity preserved, shift on free-text columns"),

    ("field-count", plant_field_count,

     "plan-economics.csv notes cell with a surplus unquoted comma"),

    ("inherited-score", plant_unscored_model,
     "models-database.csv gains the Contributor slug carrying the base model's score"),
    ("scored-no-board-row", plant_scored_no_board_row,
     "plan row names the leaderboard page for a SKU the board does not carry"),

    ("cost-arithmetic", plant_cost_arithmetic,

     "DeepSeek row: advertised tokens cut 10x while the rate is left alone"),

    ("cost-identity", plant_cost_identity,

     "Go Plus row: yield from the $120 pool, per-M rate from the $60 cap"),

    ("mix-declared", plant_mix_declared,

     "GLM row: traffic_mix emptied, notes mention caches"),

    ("unit-scale", plant_unit_scale,

     "tokens_m_advertised = 11029000000000, the original defect's direction"),

    ("quoted-money-on-page", plant_quoted_money,

     "references entry quoting three figures absent from the DeepSeek page"),

    ("fetch-log-hash", plant_fetch_log,

     "fetch-log sha256 flipped by one hex character"),

    ("fetch-log-orphan", plant_fetch_log_orphan,

     "an archived source with no fetch-log entry"),

    ("evidence-label", plant_evidence_label,

     "source_url reading 'ask me later'"),

    ("evidence-vocabulary", plant_evidence_vocabulary,

     "evidence_class reading FIRST-PARTY"),

    ("report-matches-data", plant_report_matches_data,

     "README row count off by one and a CSV path that does not exist"),

    ("ladder-price-on-page", plant_ladder_price,

     "Kilo Individual priced 0 against a page that states no price"),

    ("provenance-in-log", plant_provenance,

     "provenance asserting a lookup dated after every log entry"),

    ("shared-cap", plant_shared_cap,

     "cap_model reading PER-MODEL on a row with a $60 ceiling"),

    ("gate-count", plant_gate_count,

     "root README claiming eleven checks"),

    ("layout", plant_layout,

     "references/ deleted from the pass directory"),

    ("lookup-against-board", plant_lookup_against_board,

     "lookup claims the Contributor SKU is on the board at the base model's score"),

    ("model-slug-joins", plant_model_slug_joins,

     "plan row names a slug in neither the landscape nor the lookup"),

    ("no-future-pass", plant_no_future_pass,

     "pass directory dated after the machine's clock"),

]





def build(out: Path) -> list[tuple[str, str, str]]:

    """Create every plant under `out`. Returns (name, expected check, note)."""

    if out.exists():

        shutil.rmtree(out)

    out.mkdir(parents=True)

    made = []

    for name, builder, note in PLANTS:

        dest = out / name

        dest.mkdir(parents=True)

        expected = builder(dest)

        made.append((name, expected, note))

    return made





def main() -> int:

    out = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_OUT

    made = build(out)

    for name, expected, note in made:

        print(f"{name:22} -> expects [{expected}]   {note}")

    print(f"\n{len(PLANTS)} plants under {rel(out)}/")

    # The manifest is what lets `tests/run-plants.sh` assert that each plant is
    # caught *by the check it is named for* rather than merely by something. The
    # harness used to print the tripped check names without comparing them, so a
    # plant tripped by the wrong check still read as a pass.
    (out / "manifest.json").write_text(
        json.dumps(
            {"plants": [{"name": n, "expects": [e], "note": note} for n, e, note in made]},
            indent=2,
        ) + "\n",
        encoding="utf-8",
    )

    return 0





def rel(path: Path) -> str:

    try:

        return str(path.resolve().relative_to(ROOT))

    except ValueError:

        return str(path)





if __name__ == "__main__":

    sys.exit(main())