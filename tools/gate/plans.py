"""Declaration checks on derived plan figures: a ceiling states its pool, a $/M its mix."""
from __future__ import annotations

from pathlib import Path

from .common import _num, data_rows, failures, read_rows, rel


def check_shared_cap(pass_dir: Path) -> None:
    """A per-model dollar ceiling must say whether it is independent or pooled.

    OpenCode Go publishes a $60 monthly limit per model and says "Each model's
    monthly limit below determines how its usage counts toward those allowances",
    which reads as independent budgets. Several open issues report the opposite:
    models blocked at $0 recorded spend, one at $4.38 total account spend against
    a $60 pool. An independent-per-model table and a shared-pool table produce the
    same headline number for a single model and differ by the number of models a
    buyer uses, so a row publishing the ceiling without recording which it is
    cannot be planned against.

    The pool model may be declared in either `cap_model` (the 2026-10-06 column)
    or `meter_basis` (the 2026-10-02 column), and a ceiling may be published in
    `monthly_ceiling_usd`, `per_model_cap_usd` or `monthly_pool_usd`. A file that
    carries none of them has nothing to check and is skipped rather than guessed
    at.

    `cap_model` / `meter_basis` is **authoritative**. The first version also
    accepted the bare token "pool" appearing anywhere in the free-text notes,
    which lets a row whose `cap_model` literally reads `PER-MODEL` pass as long as
    some sentence in its notes happens to mention a pool. The notes are where the
    reading is argued; the column is where it is declared, and a check that reads
    the argument instead of the declaration is checking prose.
    """
    plans = pass_dir / "data" / "plan-economics.csv"
    if not plans.is_file():
        return
    header, rows = read_rows(plans)
    if not header:
        return
    cap_cols = [c for c in ("monthly_ceiling_usd", "per_model_cap_usd", "monthly_pool_usd")
                if c in header]
    model_cols = [c for c in ("cap_model", "meter_basis") if c in header]
    if not cap_cols or not model_cols:
        return
    cap_idx = [header.index(c) for c in cap_cols]
    model_idx = [header.index(c) for c in model_cols]
    for offset, row in enumerate(data_rows(rows), start=1):
        if len(row) != len(header):
            continue
        ceilings = [(row[i] or "").strip() for i in cap_idx]
        if not any(c and _num(c) is not None for c in ceilings):
            continue
        declared = " ".join((row[i] or "") for i in model_idx).lower()
        if not declared.strip():
            failures.append(
                f"[shared-cap] {rel(plans)} data row {offset} publishes a dollar "
                f"ceiling but its {'/'.join(model_cols)} cell is empty. A per-model "
                f"ceiling means nothing without saying whether it is independent or "
                f"drawn against a shared monthly pool, because the two differ by the "
                f"number of models a buyer uses in the month."
            )
            continue
        if any(token in declared for token in ("pool", "shared", "additive")):
            continue
        shown = next(c for c in ceilings if c and _num(c) is not None)
        failures.append(
            f"[shared-cap] {rel(plans)} data row {offset}: ceiling ${shown} is "
            f"published with {'/'.join(model_cols)}={row[model_idx[0]].strip()!r} and "
            f"nothing recording whether it is independent or drawn against a shared "
            f"monthly pool. State it in the cap_model column, not in the notes: a "
            f"pooled cap changes the plan's yield by the number of models a buyer "
            f"uses in the month, and that column is what a reader reads."
        )


def check_mix_declared(pass_dir: Path) -> None:
    """A derived $/M or tokens/month row must state the traffic mix behind it.

    A $/M figure is a division and its divisor is a traffic mix. The same plan on
    the same page yields figures 5.3x to 29.0x apart depending on the mix, and
    the 2026-10-02 pass exists because a $/M was published without one and a
    second was published to contradict it. A row carrying a derived price or a
    derived monthly token count without recording the mix it was computed under has
    published an assumption as a result.

    Two changes. The mix must be in a **column**, and that column must be
    non-empty: the first version accepted the substring "cache", "mix" or "%"
    anywhere in the notes, which satisfies a row whose notes read "Vendor caches
    nothing beyond the discounted tier" - a sentence that says nothing about the
    mix the row's $/M was computed under. And a file with no mix column at all has
    declared no mix anywhere, so the check now says so rather than skipping it,
    which is what left the newest pass unchecked: it published twenty derived $/M
    figures and the check demanded nothing of them.
    """
    data = pass_dir / "data"
    if not data.is_dir():
        return
    for path in sorted(data.glob("*.csv")):
        header, rows = read_rows(path)
        if not header:
            continue
        index = {name.strip().lower(): i for i, name in enumerate(header)}
        derived = [c for c in ("usd_per_mtok", "monthly_tokens_m", "tokens_m",
                               "tokens_m_at_ceiling", "blended_usd_per_mtok")
                   if c in index]
        if not derived:
            continue
        # A dedicated mix column, if the file has one. `cache` alone is not a mix
        # column: `cached_read_per_m` is a price, and a file whose only
        # "cache"-ish column is a price has declared no mix.
        mix_cols = [
            c for c in index
            if c in ("traffic_mix", "mix", "traffic_mix_used", "mix_used",
                     "assumed_mix")
        ]
        for offset, row in enumerate(data_rows(rows), start=1):
            if len(row) != len(header):
                continue
            values = [row[index[c]] for c in derived
                      if _num(row[index[c]]) is not None and _num(row[index[c]]) > 0]
            if not values:
                continue
            if not mix_cols:
                failures.append(
                    f"[mix-declared] {rel(path)} data row {offset} carries a derived "
                    f"$/M or tokens/month figure ({'/'.join(derived)}) and this file has "
                    f"no traffic-mix column. A $/M is a division and the mix is its "
                    f"divisor; add a traffic_mix column and state it per row, or mark "
                    f"the figure UNKNOWN."
                )
                continue
            if any(row[index[c]].strip() for c in mix_cols):
                continue
            failures.append(
                f"[mix-declared] {rel(path)} data row {offset} carries a "
                f"derived $/M or tokens/month figure but its "
                f"{'/'.join(sorted(mix_cols))} cell is empty. The mix is the "
                f"divisor of every figure in this row; state it there."
            )
