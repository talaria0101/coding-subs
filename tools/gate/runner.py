"""The order checks run in, and the command line that runs them.

PIPELINE pairs each check function with the CHECKS keys its messages carry. The
order is the order failures are printed in, so it is part of the gate's output
and is kept as it was when the gate was one file. Most functions emit one key;
`check_dates` emits two, because the pass date and the fetch log it corroborates
against are read in one place.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Callable

from .arithmetic import check_cost_arithmetic, check_cost_identity, check_unit_scale
from .common import failures, latest, passes
from .evidence import check_evidence_labels, check_evidence_vocabulary
from .models import check_lookup_against_board, check_model_slug_joins, check_unscored_model
from .plans import check_mix_declared, check_shared_cap
from .provenance import check_dates, check_provenance_in_log
from .report import check_gate_count_claims, check_report_matches_data
from .sources import check_ladder_prices_on_page, check_quoted_money_on_page
from .structure import check_column_values, check_field_counts, check_layout

PIPELINE: tuple[tuple[Callable[[Path], None], tuple[str, ...]], ...] = (
    (check_layout, ("layout",)),
    (check_gate_count_claims, ("gate-count-claims",)),
    (check_dates, ("no-future-pass", "fetch-log-corroborates")),
    (check_field_counts, ("field-count",)),
    (check_column_values, ("field-columns",)),
    (check_cost_arithmetic, ("cost-arithmetic",)),
    (check_cost_identity, ("cost-identity",)),
    (check_evidence_labels, ("evidence-label",)),
    (check_evidence_vocabulary, ("evidence-vocabulary",)),
    (check_report_matches_data, ("report-matches-data",)),
    (check_model_slug_joins, ("model-slug-joins",)),
    (check_ladder_prices_on_page, ("ladder-price-on-page",)),
    (check_quoted_money_on_page, ("quoted-money-on-page",)),
    (check_unit_scale, ("unit-scale",)),
    (check_unscored_model, ("unscored-model",)),
    (check_lookup_against_board, ("lookup-against-board",)),
    (check_provenance_in_log, ("provenance-in-log",)),
    (check_shared_cap, ("shared-cap",)),
    (check_mix_declared, ("mix-declared",)),
)


def validate(pass_dir: Path) -> None:
    for run, _names in PIPELINE:
        run(pass_dir)


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if "--all" in args:
        targets = passes()
        if not targets:
            print("no pass directories found")
            return 1
    elif args:
        targets = [Path(a) for a in args]
    else:
        targets = [latest()]

    for pass_dir in targets:
        before = len(failures)
        validate(pass_dir)
        added = len(failures) - before
        print(f"{pass_dir.name}: {'OK' if not added else f'{added} failure(s)'}")

    if failures:
        print(f"\nFAIL ({len(failures)}):")
        for message in failures:
            print("  -", message)
        return 1
    print("\nOK: all checks passed")
    return 0
