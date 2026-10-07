"""Arithmetic checks: one quantity stated in several units or several rows must agree."""
from __future__ import annotations

import re
from pathlib import Path

from .common import ARITHMETIC_TOLERANCE, CJK_SCALE, _num, data_rows, failures, read_rows, rel


def _role_candidates(index: dict[str, int], role: str) -> list[str]:
    """Columns that play a role, most specific first.

    Columns are resolved by role rather than by an exact-name allow-list because
    an allow-list cannot see the pass that introduces a new column name, and the
    consequence is silent blindness: `cost-arithmetic` matched a fixed list of
    token-column names, none of which the 2026-10-06 pass uses, so the check had
    never once examined a row of the newest pass. A pass that cannot be seen is
    not a pass that is clean.
    """
    if role == "price":
        return [n for n in ("plan_price_usd_month", "price_usd_month", "price") if n in index]
    if role == "per_m":
        return [n for n in ("usd_per_mtok", "usd_per_m_tokens") if n in index]
    if role == "tokens_m":
        names = [n for n in index if TOKEN_COLUMN_PATTERN.match(n)]
        # `_measured` is a user meter and `tokens_m_at_ceiling` is the ceiling a
        # yield was derived from, so both are excluded from this role: a plan
        # price divided by a metered reading is not the plan's $/M.
        names = [
            n for n in names
            if not n.endswith(DIFFERENT_QUANTITY_SUFFIX) and n != "tokens_m_at_ceiling"
        ]
        return sorted(names)
    return []


def _resolve(index: dict[str, int], probe: list[str], role: str, want_number) -> str | None:
    """First candidate for `role` whose value in the first data row is a number."""
    for name in _role_candidates(index, role):
        if index[name] < len(probe) and want_number(probe[index[name]]):
            return name
    return None


def _wants_number(value: str) -> bool:
    number = _num(value)
    return number is not None and number > 0


def check_cost_arithmetic(pass_dir: Path) -> None:
    """price, tokens and $/M must agree. A row that fails is not publishable.

    The three cells have to be the same quantity in three units. A per-M rate is
    only meaningful when it is the same quantity as the token count it came from,
    so the ceiling a yield was derived from is excluded from the token role rather
    than compared against the advertised figure on the same row.

    Columns are resolved by role and the resolved columns are recorded, because
    an exact-name allow-list cannot see a pass that renames a column, and a check
    that cannot see a pass reports it as clean. Resolving by role made this check
    read the 2026-10-06 pass for the first time and immediately find a row there
    it had never looked at.
    """
    data = pass_dir / "data"
    if not data.is_dir():
        return
    for path in sorted(data.glob("*.csv")):
        header, rows = read_rows(path)
        if not header:
            continue
        index = {name.strip().lower(): i for i, name in enumerate(header)}
        live = data_rows(rows)
        if not live:
            continue
        price_col = _resolve(index, live[0], "price", _wants_number)
        per_col = _resolve(index, live[0], "per_m", _wants_number)
        tok_col = _resolve(index, live[0], "tokens_m", _wants_number)
        if not (price_col and tok_col and per_col):
            continue
        for offset, row in enumerate(live, start=1):
            if len(row) <= max(index[c] for c in (price_col, tok_col, per_col)):
                continue
            price = _num(row[index[price_col]])
            tokens = _num(row[index[tok_col]])
            per_m = _num(row[index[per_col]])
            if not price or not tokens or not per_m or price <= 0 or tokens <= 0 or per_m <= 0:
                continue
            # A `*_m` column is already in millions, so price / tokens is $/M.
            expected = price / tokens
            ratio = expected / per_m
            if abs(ratio - 1.0) > ARITHMETIC_TOLERANCE:
                failures.append(
                    f"[cost-arithmetic] {rel(path)} data row {offset}: "
                    f"{price_col}={price:g} / {tok_col}={tokens:g}M tokens = "
                    f"${expected:.4f}/M but the row's {per_col} reads "
                    f"${row[index[per_col]].strip()}/M "
                    f"({per_m / expected:.2f}x off). price, tokens and $/M are the "
                    f"same quantity in three units; the per-model rate is on the same row."
                )


def _identity_fields(index: dict[str, int]) -> dict[str, int] | None:
    """The columns that together name one plan x model x mix x measurement.

    A file that does not carry all of them is skipped: a file without a mix has
    nothing to declare, and a file without a plan has no per-plan price to
    divide.
    """
    names = {
        "plan": next((index[n] for n in ("plan", "provider_plan", "plan_name")
                      if n in index), None),
        "model": next((index[n] for n in ("model", "model_sold", "sku")
                       if n in index), None),
        "mix": next((index[n] for n in ("traffic_mix", "mix", "traffic_mix_used",
                                        "mix_used", "assumed_mix")
                     if n in index), None),
        "ceiling": next((index[n] for n in ("tokens_m_advertised", "tokens_m_converted",
                                            "monthly_tokens_m", "tokens_m",
                                            "plan_monthly_tokens")
                         if n in index), None),
        "pool": next((index[n] for n in ("monthly_pool_usd", "monthly_ceiling_usd",
                                         "per_model_cap_usd", "plan_ceiling_usd")
                      if n in index), None),
        "rate": next((index[n] for n in ("blended_usd_per_mtok", "usd_per_mtok",
                                          "usd_per_m_tokens",
                                          "effective_usd_per_mtok_own_meter",
                                          "conversion_usd_per_mtok")
                      if n in index), None),
    }
    if any(v is None for v in names.values()):
        return None
    return names


def check_cost_identity(pass_dir: Path) -> None:
    """The row must be the division it says it is: ceiling / rate = tokens.

    `cost-arithmetic` holds the three columns that state one quantity in three
    units - plan price, monthly tokens, cost per million - against each other. It
    cannot see a second quantity on the same row, and the newest pass has one: a
    model price per million from which a token yield is derived, sitting beside a
    per-model dollar ceiling. The Go Plus row of 2026-10-06 derived its token
    count from a $120 figure while its per-M rate came from a different one; the
    three columns `cost-arithmetic` reads were internally consistent and the row
    was wrong anyway.

    Two relationships are checked, and they are different relationships. Rows
    describing the same plan x model x mix in one token column must imply one
    dollar figure, tokens x rate, because tokens = dollars / rate: a second
    reading of one quantity can change the rate and the count only in inverse
    proportion. And a row that states both a dollar ceiling and a rate must
    satisfy ceiling / rate = tokens, which is the division the row claims to
    have performed.

    What is deliberately **not** checked is plan price / tokens against the
    model's own `blended_usd_per_mtok`. Those are different quantities - what the
    subscriber pays for the whole plan against what the vendor charges an API
    customer for the model - and their ratio is the plan's whole economics.
    Treating them as two estimates of one number was an over-reach in the first
    version of this check and it rejected 28 correct rows. `cost-arithmetic`
    already holds the former against `usd_per_mtok`.

    Its limit is stated here because it has been hit. **An arity-preserving column
    shift moves the values under the column names without changing either, and
    every arithmetic check reads by name.** A surplus comma in one cell plus a
    removed empty cell elsewhere leaves this file arity-correct with `rankable`
    holding what used to be the evidence class and `evidence_class` holding a URL;
    no amount of arithmetic on the row detects it, because every number in the row
    is still exactly what its new name says it is. `field-columns` is the check
    that sees it, and it is the reason both run.
    """
    data = pass_dir / "data"
    if not data.is_dir():
        return
    for path in sorted(data.glob("*.csv")):
        header, rows = read_rows(path)
        if not header:
            continue
        index = {name.strip().lower(): i for i, name in enumerate(header)}
        cols = _identity_fields(index)
        if cols is None:
            continue
        plan_i, model_i, mix_i = cols["plan"], cols["model"], cols["mix"]
        ceil_i, pool_i, rate_i = cols["ceiling"], cols["pool"], cols["rate"]
        ceil_name = header[ceil_i]
        rate_name = header[rate_i]
        pool_name = header[pool_i]
        both_caps = "per_model_cap_usd" in index and "monthly_pool_usd" in index

        groups: dict[tuple, list[tuple[int, float, float, bool]]] = {}
        for offset, row in enumerate(data_rows(rows), start=1):
            if len(row) != len(header):
                continue
            tokens = _num(row[ceil_i])
            rate = _num(row[rate_i])
            if not tokens or not rate or tokens <= 0 or rate <= 0:
                continue
            # The group is plan x model x mix within this file's token column.
            # The column is fixed per file, so it is not part of the key; keying
            # on the token *value* put every row with a different count in its own
            # group, and the comparison below could then only ever see 1.00x.
            key = tuple(row[i].strip().lower() for i in (plan_i, model_i, mix_i))
            has_pool = _num(row[pool_i]) is not None
            groups.setdefault(key, []).append((offset, tokens, rate, has_pool))
        for (plan, model, mix), members in groups.items():
            if len(members) < 2:
                continue
            first_offset, first_tokens, first_rate, first_pool = members[0]
            for offset, tokens, rate, has_pool in members[1:]:
                # tokens = dollars / rate, so tokens x rate is the dollar figure
                # each row was divided from. Two readings of one quantity share
                # it; a rate change that is not matched by an inverse change in
                # tokens means the rows were divided from different dollar figures.
                first_dollars = first_tokens * first_rate
                dollars = tokens * rate
                if abs(dollars - first_dollars) / max(dollars, first_dollars) <= ARITHMETIC_TOLERANCE:
                    continue
                if has_pool and first_pool:
                    pool_said = f"both carry a dollar ceiling in {pool_name}"
                elif has_pool or first_pool:
                    pool_said = f"only one of them carries a dollar ceiling in {pool_name}"
                else:
                    pool_said = f"neither carries a dollar ceiling in {pool_name}"
                failures.append(
                    f"[cost-identity] {rel(path)} data row {offset} and data row "
                    f"{first_offset} both describe plan {plan!r}, model {model!r} "
                    f"under mix {mix!r} ({pool_said}), but {ceil_name} differs by "
                    f"{tokens / first_tokens:.2f}x and {rate_name} by "
                    f"{rate / first_rate:.2f}x, so {ceil_name} x {rate_name} is "
                    f"${first_dollars:,.2f} on one row and ${dollars:,.2f} on the other. "
                    f"Two readings of one quantity divide the same dollar figure: one "
                    f"of them is counting a different one."
                )

        for offset, row in enumerate(data_rows(rows), start=1):
            if len(row) != len(header):
                continue
            tokens = _num(row[ceil_i])
            rate = _num(row[rate_i])
            if not tokens or not rate or tokens <= 0 or rate <= 0:
                continue
            if both_caps:
                pool = _num(row[index["monthly_pool_usd"]]) or 0.0
                cap = _num(row[index["per_model_cap_usd"]]) or 0.0
                effective = min(v for v in (pool, cap) if v > 0) if (pool or cap) else 0.0
            else:
                effective = _num(row[pool_i]) or 0.0
            if effective <= 0:
                continue
            expected = effective / rate
            if abs(expected - tokens) / expected > ARITHMETIC_TOLERANCE:
                failures.append(
                    f"[cost-identity] {rel(path)} data row {offset}: "
                    f"{pool_name}={row[pool_i].strip()} / {rate_name}="
                    f"{row[rate_i].strip()} = {expected:,.0f}M, but {ceil_name} reads "
                    f"{row[ceil_i].strip()}. The row states the division it performed "
                    f"and it does not produce the count on the same row."
                )


# A token column's own unit, so a value can be checked against its header rather
# than against a guess. `tokens` with no suffix is taken as raw tokens, which is
# the one convention that makes the stored-row comparison meaningful.
TOKEN_COLUMN_UNITS = {
    "monthly_tokens": 1,
    "monthly_tokens_m": 1e6,
    "tokens_m_advertised": 1e6,
    "tokens_m_converted": 1e6,
    "tokens": 1,
    "tokens_m": 1e6,
    "tokens_m_at_ceiling": 1e6,
    "plan_monthly_tokens": 1,
    "monthly_yi": 1e8,
    "monthly_yi_value": 1e8,
}

# Any token-bearing column is matched against this list, and one that is not on
# it is refused rather than skipped. The first version compared only enumerated
# pairs, which meant (a) a file with a single token column could not be checked at
# all - the common case, and the shape the yi defect had - and (b) a column called
# `monthly_tokens_b` carrying an 11.029-vs-11029 error passed silently, because
# the check had never heard of it. An unknown unit column is a column whose
# header makes no promise about scale, and that is the ambiguity this check
# exists to resolve rather than pass over.
TOKEN_COLUMN_PATTERN = re.compile(r"^(monthly_|plan_monthly_)?tokens|token_|_(tokens|token)$|tokens_")

# Columns that state the SAME quantity under different units, compared by default.
# Only column pairs listed here are checked against each other, because "any two
# token columns must agree" is wrong in general: `tokens_m_advertised` and
# `tokens_m_measured` are two different quantities on purpose (a vendor ceiling
# and a user meter), and treating them as one produced a false positive on
# correct data when this check was first written. A check that is confidently
# wrong is worse than no check.
SAME_QUANTITY_GROUPS = (
    frozenset({"monthly_tokens", "monthly_tokens_m"}),
    frozenset({"monthly_tokens", "tokens_m"}),
    frozenset({"monthly_tokens_m", "tokens_m"}),
    frozenset({"monthly_tokens_m", "tokens_m_at_ceiling"}),
    frozenset({"tokens_m_advertised", "monthly_tokens"}),
    frozenset({"tokens_m_advertised", "monthly_tokens_m"}),
    frozenset({"tokens_m_advertised", "tokens_m"}),
    frozenset({"tokens_m_advertised", "monthly_yi"}),
    frozenset({"tokens_m_converted", "monthly_tokens_m"}),
    frozenset({"monthly_tokens_m", "monthly_yi"}),
    frozenset({"tokens_m", "monthly_yi"}),
    frozenset({"plan_monthly_tokens", "monthly_yi"}),
    frozenset({"monthly_yi", "monthly_yi_value"}),
)

# A column whose name carries this suffix is a deliberately different quantity and
# is excluded from the comparison above. `tokens_m_measured` is one: it is a user
# meter reading, not the vendor ceiling in the adjacent column, and the two are
# expected to disagree by a large factor.
DIFFERENT_QUANTITY_SUFFIX = "_measured"

# A token column carrying a magnitude letter in its own name states that letter's
# power of ten. `monthly_tokens_b` is billions, `monthly_tokens_m` millions,
# `monthly_tokens_k` thousands. This is what makes a single-column file
# checkable: the header itself carries the unit, so a value can be read against
# it without a second column to compare against.
NAME_SUFFIX_UNITS = {"k": 1e3, "m": 1e6, "b": 1e9, "bn": 1e9, "g": 1e9, "t": 1e12}

# Below this, a token count is not a token count, and above this it is larger
# than any monthly allowance published in this market. Both ends are the same
# error: a count that arrived multiplied or divided by a power of ten. The lower
# end was checked and the upper end was not, which is the defect's own direction
# - yi is 10^8, so reading 25.81 yi as 25.81 billion overstates by a factor of
# ten - so a check that only looked for understatement could not see the thing it
# was written for.
#
# The bounds come from this repository's own data rather than from a general
# notion of what a lot of tokens is: the largest monthly allowance any archived
# vendor page in this repository publishes is 22,059M, five orders of magnitude
# below the upper bound.
MIN_PLAUSIBLE_MONTHLY_TOKENS = 1e6
MAX_PLAUSIBLE_MONTHLY_TOKENS = 1e13


def _declared_unit_from_name(name: str) -> float | None:
    """The multiplier a column name's trailing unit letter declares, if any.

    A compound name like `monthly_tokens_m_converted` declares its unit in the
    middle rather than at the end, so the token stem is located first and the
    letter immediately after it is read.
    """
    tail = name.rsplit("_", 1)
    if len(tail) == 2 and tail[1].lower() in NAME_SUFFIX_UNITS:
        return NAME_SUFFIX_UNITS[tail[1].lower()]
    stem = re.search(r"tokens?_([a-z]+)", name)
    if stem:
        return NAME_SUFFIX_UNITS.get(stem.group(1))
    return None


def _parse_token_value(raw: str):
    """A token count as a float, or None. Accepts CJK magnitude suffixes."""
    text = raw.strip().replace(",", "")
    if not text or text.upper() == "UNKNOWN":
        return None
    scale = 1.0
    for suffix, factor in CJK_SCALE.items():
        if text.endswith(suffix):
            scale = factor
            text = text[: -len(suffix)].strip()
            break
    try:
        return float(text) * scale
    except ValueError:
        return None


def _check_single_token_column(path: Path, offset: int, name: str, raw: str,
                               unit: float | None) -> None:
    """A lone token column is checked against the unit its own header declares.

    The pair comparison below needs two columns to exist, so a file with one token
    column was unchecked - and one token column is the common case, and the shape
    the yi defect actually had. The column's own unit is applied first, so
    `tokens_m_at_ceiling=1697` is 1.697 billion tokens and is not an error, while
    a `monthly_tokens_m_converted` cell reading 0.453 is 453,000 tokens and is.

    A value whose magnitude cannot be a monthly allowance is a count that arrived
    divided or multiplied by a power of ten. In this market a monthly allowance
    runs from ~34M (Kimi K3 at a $15 cap) to ~22,059M, so neither end of the
    plausible band is near.
    """
    value = _parse_token_value(raw)
    if value is None:
        return
    if unit is None:
        failures.append(
            f"[unit-scale] {rel(path)} data row {offset}: column {name!r} holds a "
            f"token count but its header declares no unit, so {raw.strip()} cannot "
            f"be read against anything. Name the unit in the column "
            f"(tokens_m, monthly_tokens, monthly_tokens_b) or give it a companion "
            f"column in a stated unit."
        )
        return
    tokens = value * unit
    if 0 < tokens < MIN_PLAUSIBLE_MONTHLY_TOKENS:
        failures.append(
            f"[unit-scale] {rel(path)} data row {offset}: {name}={raw.strip()} is "
            f"{tokens:,.0f} tokens in that column's unit. No monthly token "
            f"allowance in this market is below "
            f"{MIN_PLAUSIBLE_MONTHLY_TOKENS:,.0f}, so this is a magnitude error "
            f"rather than a small figure. A count that arrived divided by a power "
            f"of ten on the way in produces exactly this."
        )
    elif tokens > MAX_PLAUSIBLE_MONTHLY_TOKENS:
        failures.append(
            f"[unit-scale] {rel(path)} data row {offset}: {name}={raw.strip()} is "
            f"{tokens:,.0f} tokens in that column's unit. No monthly token allowance "
            f"published in this market is above {MAX_PLAUSIBLE_MONTHLY_TOKENS:,.0f}, "
            f"so this is a magnitude error rather than a large figure - and "
            f"overstatement is the direction the original defect went in, because a "
            f"CJK magnitude suffix is 10^8 and 25.81 of them is 2,581,000,000, not "
            f"25.81 billion. A count that arrived multiplied rather than divided by "
            f"a power of ten produces exactly this."
        )


def check_unit_scale(pass_dir: Path) -> None:
    """Two columns stating one quantity must agree once each is read in its unit.

    A source row stored `monthly_tokens: 2581000000` and, alongside it, a
    human-readable `25.81` under a `monthly_yi` header. yi is 10^8, so those two
    cells agree and describe 2.58 billion. Reading the second cell as 25.81 billion
    is a 10x error; it survived a reconciler and flipped a HIT only when a second
    reconciler re-checked the arithmetic against the stored row. This check is
    that re-check made structural.

    Only column pairs listed in SAME_QUANTITY_GROUPS are compared. The first
    version compared every token column against every other and reported the
    correct `tokens_m_advertised=6211` / `tokens_m_measured=2900` row as a 2.1x
    magnitude error, because those two columns are deliberately different
    quantities: one is a vendor ceiling and the other a user meter. A check that
    is confidently wrong is worse than no check.

    That restraint then over-corrected: pair comparison alone cannot fire on a
    file with a single token column, which is the common case and the shape the yi
    defect actually had, and it silently passed a `monthly_tokens_b` column
    carrying an 11.029-vs-11029 error because the column was not on the list. So
    every token-bearing column is now also checked on its own against the unit
    its header declares and against what a monthly allowance can physically be -
    at both ends, because the original defect was an overstatement.
    """
    data = pass_dir / "data"
    if not data.is_dir():
        return
    for path in sorted(data.glob("*.csv")):
        header, rows = read_rows(path)
        if not header:
            continue
        index = {name.strip().lower(): i for i, name in enumerate(header)}
        present_names = {
            name for name in index
            if name in TOKEN_COLUMN_UNITS and not name.endswith(DIFFERENT_QUANTITY_SUFFIX)
        }
        # Every column that looks like a token count, whether or not the check has
        # seen it before. An unrecognised unit column is the case the old
        # enumerated-pairs version could not reach, so a column whose name
        # declares a magnitude letter gets that letter as its unit.
        token_like = {}
        for name in index:
            if name in present_names or name.endswith(DIFFERENT_QUANTITY_SUFFIX):
                continue
            if not TOKEN_COLUMN_PATTERN.match(name):
                continue
            token_like[name] = _declared_unit_from_name(name)
        pairs = [
            (a, b) for group in SAME_QUANTITY_GROUPS
            for a, b in [sorted(group)]
            if a in present_names and b in present_names
        ]
        for offset, row in enumerate(data_rows(rows), start=1):
            if len(row) != len(header):
                continue
            for name in sorted(present_names):
                if len(row) <= index[name]:
                    continue
                _check_single_token_column(
                    path, offset, name, row[index[name]], TOKEN_COLUMN_UNITS[name]
                )
            for name, unit in sorted(token_like.items()):
                if len(row) <= index[name]:
                    continue
                _check_single_token_column(path, offset, name, row[index[name]], unit)
            for a_name, b_name in pairs:
                a_raw = _parse_token_value(row[index[a_name]])
                b_raw = _parse_token_value(row[index[b_name]])
                if a_raw is None or b_raw is None:
                    continue
                # Each cell as written, then as tokens under its own column unit.
                a_tok = a_raw * TOKEN_COLUMN_UNITS[a_name]
                b_tok = b_raw * TOKEN_COLUMN_UNITS[b_name]
                if not a_tok or not b_tok:
                    continue
                ratio = max(a_tok, b_tok) / min(a_tok, b_tok)
                # One quantity in two units, so anything past 2x is a unit or
                # magnitude disagreement rather than rounding.
                if ratio > 2.0:
                    failures.append(
                        f"[unit-scale] {rel(path)} data row {offset}: {a_name}='{row[index[a_name]].strip()}' "
                        f"is {a_tok:,.0f} tokens and {b_name}='{row[index[b_name]].strip()}' is "
                        f"{b_tok:,.0f} tokens. Both columns state the same quantity and they "
                        f"differ by {ratio:.1f}x. A CJK magnitude suffix (wan/yi/zhao, "
                        f"10^4/10^8/10^12) copied instead of converted produces exactly this."
                    )
