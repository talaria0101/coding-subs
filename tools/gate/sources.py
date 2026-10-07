"""Money checks against archived pages: a price or a quotation must be in the bytes it cites."""
from __future__ import annotations

import re
from pathlib import Path

from .common import data_rows, failures, read_rows, rel


def check_ladder_prices_on_page(pass_dir: Path) -> None:
    """A ladder price must appear in the bytes of the page it cites.

    The plan ladder records, per row, which archived page the figure was read
    from. Verifying each price against that page found four of thirty rows whose
    cited page does not contain the price: Z.ai's overview page publishes only
    "starting at just 18 USD", so the Pro and Max prices attributed to it came
    from an earlier pass. A price with the wrong provenance is worse than a
    missing one, because it looks sourced.

    A page that publishes no dollar figure at all cannot be checked against a
    dollar figure, and pretending otherwise produces a check that passes for the
    wrong reason. `Kilo Individual` is the live case: its row records a price of
    0, `kilo-home.html` carries three bare `0`s and no price at all, and the check
    reported success because the digit matched. A price of exactly zero is
    reported as FREE-ON-PAGE instead, which is a claim about the page rather than
    about a digit appearing somewhere in it.
    """
    ladder = pass_dir / "data" / "plan-ladder.csv"
    sources = pass_dir / "sources"
    if not ladder.is_file() or not sources.is_dir():
        return
    header, rows = read_rows(ladder)
    if "vendor_source" not in header or "price_value" not in header:
        return
    src_i, price_i = header.index("vendor_source"), header.index("price_value")
    ext_i = header.index("extraction") if "extraction" in header else None
    plan_i = header.index("plan") if "plan" in header else None

    money_on_page: dict[str, set[str]] = {}
    for path in sorted(p for p in sources.iterdir() if p.is_file()):
        text = path.read_text(encoding="utf-8", errors="replace")
        # Normalise thousands separators and the ".00" a page may or may not
        # print, so $1,200 and 1200 and 1200.00 compare equal. Three forms are
        # collected because a vendor writes its price three ways: "$18" in prose,
        # "18 USD" in a sentence, and "price":18 in a JSON-LD Offer block.
        # Checking only the first reports correct rows as missing, which is a
        # false positive that trains a reader to ignore the check.
        found = set()

        def add(token: str) -> None:
            token = token.replace(",", "").strip()
            if token:
                found.add(token.rstrip("0").rstrip(".") if "." in token else token)

        for token in re.findall(r"\$\s?([\d,]+(?:\.\d+)?)", text):
            add(token)
        for token in re.findall(r"(\d+(?:\.\d+)?)\s*(?:USD|dollars)\b", text):
            add(token)
        for token in re.findall(r'"price"\s*:\s*"?([\d.]+)"?', text):
            add(token)
        money_on_page[path.name] = found

    for offset, row in enumerate(data_rows(rows), start=1):
        if len(row) <= max(src_i, price_i):
            continue
        page, price = row[src_i].strip(), row[price_i].strip()
        if not price or price == "UNKNOWN" or not page:
            continue
        if ext_i is not None and len(row) > ext_i and row[ext_i].strip() in (
            "NOT-ON-PAGE", "NOT-PUBLISHED", "CARRIED-FORWARD", "FREE-ON-PAGE",
        ):
            continue
        plan = row[plan_i].strip() if plan_i is not None and len(row) > plan_i else "the plan"
        # Normalise the same way `add` does: strip a trailing ".00", not every
        # trailing zero. `rstrip("0")` on "10" yields "1", which reports a price
        # the page plainly contains as missing.
        norm = price.replace(",", "").strip()
        if "." in norm:
            norm = norm.rstrip("0").rstrip(".")
        if norm == "0":
            failures.append(
                f"[ladder-price-on-page] {rel(ladder)} data row {offset}: the row prices "
                f"{plan!r} at 0 and attributes it to sources/{page}. A zero cannot be "
                f"found or missed on a page - it is present everywhere a bare digit "
                f"appears. Mark the row FREE-ON-PAGE if the plan is free, or "
                f"NOT-PUBLISHED if the page states no price, so the cell records which."
            )
            continue
        if norm not in money_on_page.get(page, set()):
            failures.append(
                f"[ladder-price-on-page] {rel(ladder)} data row {offset}: {price} is attributed to "
                f"sources/{page}, which does not contain that figure. Re-read the page, or mark the "
                f"row NOT-ON-PAGE / CARRIED-FORWARD."
            )


# --- a 2026-10-06 check ----------------------------------------------------
#
# `quoted-money-on-page` was written after a specific defect reached a published
# verdict, and it is demonstrated twice in docs/reviews-2026-10-06.md: once
# against a planted defect, once against the corrected data. A check that has
# only been seen failing is indistinguishable from a check that cannot pass.


def _money_on_page(text: str) -> set[str]:
    """Every money figure a page carries, normalised for comparison.

    A vendor writes the same price several ways: "$18" in prose, "18 USD" in a
    sentence, and `"price":18` in a JSON-LD Offer block, and a price of $10 may
    be printed as 10, 10.0 or 10.00. Checking only the first form reports correct
    figures as missing, which is a false positive that trains a reader to ignore
    the check, so all three forms are collected and normalised the same way.
    """
    found: set[str] = set()

    def add(token: str) -> None:
        token = token.replace(",", "").strip()
        if token:
            found.add(token.rstrip("0").rstrip(".") if "." in token else token)

    for token in re.findall(r"\$\s?([\d,]+(?:\.\d+)?)", text):
        add(token)
    for token in re.findall(r"(\d+(?:\.\d+)?)\s*(?:USD|dollars)\b", text):
        add(token)
    for token in re.findall(r'"price"\s*:\s*"?([\d.]+)"?', text):
        add(token)
    return found


def _normalise_money(value: str) -> str:
    norm = value.replace(",", "").strip()
    return norm.rstrip("0").rstrip(".") if "." in norm else norm


# An entry whose dollar figures are the superseded ones being *recorded*. A
# correction is documented, not deleted, and a blanket "the entry carries a
# CORRECTED marker, stop checking" turns one recorded figure into an exemption for
# the rest of the entry. Only the lines that record the superseded quotation are
# exempt, and only while the recording is open.
CORRECTED_OPEN = re.compile(r"\*\*CORRECTED\s+\d{4}-\d{2}-\d{2}")
CORRECTED_CLOSE = re.compile(r"\*\*[A-Z][^*]{2,60}\*\*")


def check_quoted_money_on_page(pass_dir: Path) -> None:
    """A money figure quoted in references/*.md must be on the page it cites.

    `ladder-price-on-page` above does this for the plan-ladder CSV, and it found
    four rows whose cited page did not contain the price. It returns early unless
    `data/plan-ladder.csv` exists, and only the 2026-10-02 pass has one, so the
    check never touched the pass that needed it.

    The defect this was written for is worse than a missing price. 2026-10-06's
    references file quoted the DeepSeek price table as "off-peak $0.007 cache
    hit / $0.22 input miss / $0.66 output; peak $0.014 / $0.44 / $1.32". Four of
    those six figures are not on the page, and they propagated into a blended
    rate, two cost-per-10B figures, two multipliers and the relay ratio. A
    fabricated quotation is indistinguishable from a real one in the file it sits
    in, so the only defence is comparing the quoted figure against the archived
    bytes.

    Two properties of the scoping were wrong in the first version.

    * **Attribution.** An entry carries its money figures on the lines below the
      line that names its archived page - that is how a transcription block is
      written - so the page is attributed to the whole entry, from its `**[Rn]**`
      marker to the next marker or the next heading. Any other form attaches the
      page to every figure in the file, including the figures of an entry that
      names no page at all: the two community meters, quoted from an archived feed
      that carries no dollar figures, were being checked against a vendor's
      pricing page, and would have been reported as fabricated quotations.
    * **Correction scope.** A dated `**CORRECTED …**` marker exempts the lines
      that record the superseded quotation and nothing else. Exempting the rest of
      the entry made a corrected entry uncheckable, which is the one entry class
      whose whole purpose is to be corrected.
    """
    references = pass_dir / "references"
    sources = pass_dir / "sources"
    if not references.is_dir() or not sources.is_dir():
        return

    pages: dict[str, set[str]] = {}
    for path in sorted(p for p in sources.iterdir() if p.is_file()):
        pages[path.name] = _money_on_page(
            path.read_text(encoding="utf-8", errors="replace")
        )

    # A money figure derived by dividing two published numbers is not on the
    # page and is not expected to be; a per-1M rate blended from a table, or a
    # per-token rate restated per 1M, is the same. Those are checked by
    # arithmetic elsewhere, not here.
    #
    # Narrowed 2026-10-07. This used to skip any line containing `per 1m`, `/m`,
    # `blended`, `per mtok`, `per month x` or `x 4.33`. Those are six loose
    # keywords and they were an escape hatch: a fabricated figure written as
    # "billed $0.007 per 1M cache hits" carried `per 1m` and passed silently,
    # because a keyword anywhere on the line silenced every figure on it. The
    # keywords that survive are the ones that *show the arithmetic* rather than
    # name a unit - a blend, a per-token restatement, a spelled-out division.
    # A unit label on its own ("per 1M", "$/M", "blended $/Mtok") no longer
    # exempts anything, so a figure that merely sits next to one is checked
    # against the page like any other.
    #
    # The test is applied to the figure's whole sentence, not to the physical
    # line. Wrapped prose splits a derivation across lines - "blends to
    # $0.00966 per 1M and the peak / tariff to $0.01932 per 1M" - and a
    # line-local test would check the continuation and reject a correct figure.
    derived_markers = (
        "blends to", "blended to", "blend of", "which blends",
        "per token", "times 1m", "x 1m", "÷ 1m",
    )

    def derived_sentence(text: str, start: int) -> str:
        """The sentence holding the character at `start`, so a wrapped
        derivation is judged as one sentence rather than as several lines.

        A period only ends a sentence when it is a real terminator: not the
        dot in a decimal (`0.00966`), not the dot in an abbreviation
        (`i.e.`, `e.g.`, `etc.`, `vs.`), and not one inside a filename.
        Without that, "1.6e-08 per token, i.e. $0.80 / $3.20 per 1M" was cut
        after "i." and the derivation that introduces it was lost.
        """
        def is_break(pos: int) -> bool:
            if text[pos] != ".":
                return False
            before = text[max(0, pos - 4):pos].lower()
            if before.endswith(("e.g", "i.e", "etc", "vs", "cf")):
                return False
            if pos + 1 < len(text) and text[pos + 1].isdigit():
                return False  # a decimal, not a terminator
            return pos + 1 >= len(text) or text[pos + 1].isspace()

        left = max((p for p in range(start - 1, -1, -1) if is_break(p)), default=-1)
        right = next((p for p in range(start, len(text)) if is_break(p)), None)
        if right is None:
            right = min(len(text), start + 200)
        return text[left + 1:right]

    for path in sorted(references.glob("*.md")):
        text = path.read_text(encoding="utf-8", errors="replace")
        # Split the file into entries. An entry runs from its `**[Rn]` marker to
        # the next marker or the next heading, whichever comes first, so an entry
        # cannot inherit the page of a heading it sits under.
        for part in re.split(r"(?m)^(?=\*\*\[R\d+\])", text):
            body = part.split("\n\n")[0]
            named = re.search(r"\(\.\./sources/([^)]+)\)", body)
            if not named:
                continue
            page = named.group(1)
            on_page = pages.get(page)
            if on_page is None:
                continue
            first_line = part.splitlines()[0] if part.splitlines() else ""
            recording = False
            cursor = 0
            for offset, line in enumerate(part.splitlines(), start=1):
                line_at = cursor
                cursor += len(line) + 1
                if not line.strip():
                    recording = False
                    continue
                if CORRECTED_OPEN.search(line):
                    recording = True
                    continue
                if recording:
                    if not CORRECTED_CLOSE.search(line):
                        # Still inside the recording: the superseded figure.
                        continue
                    recording = False
                for match in re.finditer(r"\$\s?(\d[\d,]*\.?\d*)", line):
                    token = match.group(1)
                    if _normalise_money(token) in on_page:
                        continue
                    sentence = derived_sentence(part, line_at + match.start())
                    if any(marker in sentence.lower() for marker in derived_markers):
                        continue
                    failures.append(
                        f"[quoted-money-on-page] {rel(path)} entry "
                        f"{first_line[:60]!r} quotes ${token}, which is not on "
                        f"sources/{page}, the page this entry cites. A quotation that is "
                        f"not in the source is not evidence; re-read the page, show the "
                        f"derivation that produces the figure, or put the superseded figure "
                        f"inside a dated CORRECTED recording."
                    )
