"""The registry of checks, one entry per registered check.

This table is the authority on what the gate checks. `gate-count-claims` holds
every document's stated count against `len(CHECKS)`, and
tests/test_gate_structure.py holds this table against the runner's PIPELINE and
the plant manifest, so a check added in one place and not the others fails.
"""
from __future__ import annotations


# name -> (what it enforces, what defect it was added for)
CHECKS: dict[str, str] = {
    "layout": "every pass has data/, references/, sources/ and a README",
    "gate-count-claims": "a document claiming a number of checks that disagrees with CHECKS",
    "field-count": "7 malformed CSV rows shipped past a green run across two passes",
    "field-columns": "an arity-preserving column shift puts every value in the wrong column",
    "cost-arithmetic": "a price, a token count and a $/M must describe one quantity",
    "cost-identity": "a row's token count must be the division the row states it performed",
    "evidence-label": "a number without a source is not evidence",
    "evidence-vocabulary": "an evidence class outside the set the root README declares",
    "no-future-pass": "a pass directory cannot be dated after the machine's clock",
    "fetch-log-corroborates": "every archived source needs a log entry and every logged hash must be the hash of the bytes",
    "report-matches-data": "row counts, cited paths and fetch tallies the report quotes must match the CSVs and the log",
    "model-slug-joins": "a plan row naming a model must join to a model in the landscape",
    "ladder-price-on-page": "a ladder price must appear in the page it cites",
    "quoted-money-on-page": "a figure quoted in references/*.md must be on the page it cites",
    "unit-scale": "25.81 yi (10^8) was read as 25.81 billion and reached a headline verdict",
    "unscored-model": "a score inherited from a different SKU ranks as a real capability score",
    "lookup-against-board": "a lookup row must say what the archived leaderboard payload actually holds",
    "provenance-in-log": "a provenance string asserting a dated lookup no fetch log entry records",
    "shared-cap": "a per-model ceiling was published without saying the ceilings share a pool",
    "mix-declared": "a derived $/M or tokens/month figure whose row omits its traffic mix",
}
