"""Shared state and helpers for every check in the gate.

`failures` is the one list every check appends to. It is a single module-level
object so that the runner can count what each pass added by length, exactly as
the gate did when it was one file.
"""
from __future__ import annotations

import csv
import re
from pathlib import Path

TOOLS = Path(__file__).resolve().parent.parent
ROOT = TOOLS.parent


failures: list[str] = []


# How far two figures derived from the same inputs may differ before they are
# treated as different quantities rather than as rounding. Every figure this
# repo publishes is rounded to four decimal places on a rate or to the nearest
# whole token-million, so five per cent is generous and one per cent would
# reject correct data.
ARITHMETIC_TOLERANCE = 0.05

# CJK magnitude suffixes and the power of ten each stands for. A note carrying
# one of these has to be converted against the stored row, never copied: yi is
# 10^8, so 25.81 yi is 2,581,000,000 and not 25.81 billion.
CJK_SCALE = {"万": 1e4, "萬": 1e4, "亿": 1e8, "億": 1e8, "兆": 1e12}

NUM_WORDS = {
    "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
    "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12,
    "thirteen": 13, "fourteen": 14, "fifteen": 15, "sixteen": 16,
    "seventeen": 17, "eighteen": 18, "nineteen": 19, "twenty": 20,
}

_UNIT_WORDS = {w: n for w, n in NUM_WORDS.items() if n < 20}
_TENS_WORDS = {
    "twenty": 20, "thirty": 30, "forty": 40, "fifty": 50,
    "sixty": 60, "seventy": 70, "eighty": 80, "ninety": 90,
}


def number_from_words(text: str) -> int | None:
    """An integer written in digits or in English words from zero to ninety-nine.

    Accepts "ten", "twenty", "twenty-one", "twenty one" and "21". Anything else,
    including "umpteen", "a hundred" or "twenty-ten", is None: the caller decides
    whether an unreadable number is an error, and in a count claim it is.
    """
    raw = text.strip().lower()
    if raw.isdigit():
        return int(raw)
    parts = [p for p in re.split(r"[-\s]+", raw) if p]
    if len(parts) == 1:
        word = parts[0]
        if word in _UNIT_WORDS:
            return _UNIT_WORDS[word]
        if word in _TENS_WORDS:
            return _TENS_WORDS[word]
        return None
    if len(parts) == 2 and parts[0] in _TENS_WORDS:
        unit = _UNIT_WORDS.get(parts[1])
        if unit is not None and 1 <= unit <= 9:
            return _TENS_WORDS[parts[0]] + unit
    return None


# The closed evidence vocabulary, exactly as the root README declares it. A class
# outside this set is a class no reader of that table can interpret, which is why
# it is refused rather than merely noted.
EVIDENCE_CLASSES = frozenset({
    "FIRST-PARTY-COMPUTED",
    "FIRST-PARTY-PRICE-ONLY",
    "MEASURED",
    "DOCUMENTED",
    "THIRD-PARTY",
    "UNKNOWN",
})

# A word that records a figure this pass could not re-verify from the sources it
# archived. It is not evidence, which is the point of it, so it is not in
# EVIDENCE_CLASSES and the vocabulary check reports it separately.
CARRY_MARKER = "CARRIED-FORWARD"


def check(cond: bool, msg: str) -> None:
    if not cond:
        failures.append(msg)


def passes() -> list[Path]:
    return sorted(p for p in ROOT.iterdir() if p.is_dir() and re.fullmatch(r"\d{4}-\d{2}-\d{2}", p.name))


def latest() -> Path:
    found = passes()
    check(bool(found), "no YYYY-MM-DD pass directory found")
    return found[-1] if found else ROOT


def rel(path: Path) -> str:
    """Path relative to the repo root, whether or not ROOT is a prefix of it.

    A pass directory can be passed in as a relative path, and `relative_to`
    raises rather than degrading. Reporting a bare path is better than a
    traceback in a gate that is supposed to be readable.
    """
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def read_rows(path: Path) -> tuple[list[str], list[list[str]]]:
    """Rows of a CSV, skipping a leading prose preamble whose header starts '#'."""
    raw = path.read_text(encoding="utf-8", errors="replace").splitlines()
    start = 0
    while start < len(raw) and raw[start].lstrip().startswith("#"):
        start += 1
    if start >= len(raw):
        return [], []
    rows = list(csv.reader(raw[start:]))
    return (rows[0] if rows else []), rows[1:]


def data_rows(rows: list[list[str]]) -> list[list[str]]:
    """Data rows only: a blank line, or a line holding one empty field, is not a row."""
    return [r for r in rows if r and not (len(r) == 1 and not r[0].strip())]


def _num(value):
    """A numeric cell, or None.

    Accepts thousands separators, a currency symbol, a trailing CJK magnitude
    suffix and the English number words that appear in prose. A cell that is not
    a number is UNKNOWN rather than zero, so a row that reads FREE is not
    silently treated as a row worth nothing.
    """
    if value is None:
        return None
    text = str(value).strip().replace(",", "").replace("$", "").replace("%", "")
    if not text or text.upper() in ("UNKNOWN", "N/A", "NA", "-"):
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
        pass
    lowered = text.lower()
    if lowered in NUM_WORDS:
        return float(NUM_WORDS[lowered]) * scale
    return None


def _row_contract(path: Path) -> list[str]:
    """What a CSV's own `#` preamble says its rows are.

    Some of this repository's databases are *derived* artefacts, regenerable from
    a named archived source: the model landscapes come out of a leaderboard page,
    the price grids out of the vendor pages they quote. Those files legitimately
    carry no per-row source column, because their provenance is the file. The
    rest are tables of observation, and every row of those has to say where its
    numbers came from.

    The distinction is read from the preamble the file already carries rather
    than hard-coded by filename, so a new derived file declares itself and a new
    table of observation gets no free pass. A file whose preamble says nothing is
    treated as a table of observation, which is the stricter reading.
    """
    found = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.lstrip().startswith("#"):
            break
        low = line.lower()
        if ("regenerat" in low or "reproduce" in low or "comes out of" in low
                or "extracted" in low or "derived" in low or "byte for byte" in low
                or "payload" in low):
            found.append(line)
    return found
