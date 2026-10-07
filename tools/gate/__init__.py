"""The data-integrity gate, split by responsibility.

`tools/validate.py` is the command line and documents what the gate is for.
The modules here hold the checks, grouped by what they read:

    common      shared helpers, constants and the one `failures` list
    registry    CHECKS, the single table of registered checks
    structure   layout, field-count, field-columns
    arithmetic  cost-arithmetic, cost-identity, unit-scale
    evidence    evidence-label, evidence-vocabulary
    provenance  no-future-pass, fetch-log-corroborates, provenance-in-log
    sources     ladder-price-on-page, quoted-money-on-page
    models      model-slug-joins, unscored-model, lookup-against-board
    plans       shared-cap, mix-declared
    report      gate-count-claims, report-matches-data
    runner      PIPELINE (run order), validate(), main()
"""
