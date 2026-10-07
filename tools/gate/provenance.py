"""Retrieval checks: the pass date, the fetch log's hashes, and dated provenance strings."""
from __future__ import annotations

import hashlib
import json
import re
from datetime import date
from pathlib import Path

from .common import check, data_rows, failures, read_rows, rel


def _path_inside_pass(pass_dir: Path, saved: str) -> str | None:
    """`saved_as` as a POSIX path inside `pass_dir`, or None if it names none.

    Three spellings are in use and all three are read: relative to the
    repository root with either separator (`2026-10-06\\sources\\x.md`,
    `2026-10-06/sources/x.md`), and relative to the pass (`sources/x.md`). A path
    that climbs out with `..`, or is absolute, names no file inside the pass.
    """
    parts = [p for p in saved.replace(chr(92), "/").split("/") if p not in ("", ".")]
    if not parts or ".." in parts or saved.startswith(("/", chr(92))) or ":" in parts[0]:
        return None
    if parts[0] == pass_dir.name:
        parts = parts[1:]
    if not parts or parts[0] not in ("sources", "raw"):
        return None
    return "/".join(parts)


def _saved_as_candidates(pass_dir: Path, saved: str) -> list[Path]:
    """Where the file a log entry names may be, most specific first.

    The full path inside the pass comes first, so a source archived in a
    subdirectory of sources/ is found where the log says it is. The basename
    fallbacks are what every earlier log relies on: `saved_as` was written with
    Windows separators, and the 2026-10-02 log pointed it at `raw/`, the
    gitignored working directory the fetch was written to rather than the
    archive. Resolving by basename inside this pass removes the separator
    convention from the question and makes such an entry find the page it
    archived.
    """
    candidates = []
    inside = _path_inside_pass(pass_dir, saved)
    if inside is not None:
        candidates.append(pass_dir.joinpath(*inside.split("/")))
    basename = saved.replace(chr(92), "/").split("/")[-1]
    candidates += [pass_dir / "sources" / basename,
                   pass_dir / "raw" / basename,
                   pass_dir / basename]
    return candidates


def check_dates(pass_dir: Path) -> None:
    today = str(date.today())
    check(pass_dir.name <= today, f"[no-future-pass] {pass_dir.name} is after the machine date {today}")
    log = pass_dir / "data" / "fetch-log.json"
    if pass_dir.name == today and not log.is_file():
        check(
            False,
            f"[fetch-log-corroborates] pass is dated today ({today}) but "
            f"{rel(log)} is absent, so the date cannot be checked",
        )
    if not log.is_file():
        return
    try:
        entries = json.loads(log.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        failures.append(f"[fetch-log-corroborates] {rel(log)} is not valid JSON: {exc}")
        return
    if not isinstance(entries, list) or not entries:
        failures.append(f"[fetch-log-corroborates] {rel(log)} has no entries")
        return
    for entry in entries:
        if not all(k in entry for k in ("url", "http", "sha256")):
            failures.append(
                f"[fetch-log-corroborates] an entry in {rel(log)} is missing "
                f"url/http/sha256, so it cannot be checked against a source"
            )
            return
    sources = pass_dir / "sources"
    if not sources.is_dir():
        return

    # The hash is the point of the log. A recorded SHA-256 that is never
    # recomputed is a string, and a string can be edited without trace; this
    # recomputes every recorded hash against the bytes actually archived.
    #
    # Two forms are compared, because git can change a file's bytes without
    # anyone editing it. With no `.gitattributes` in this repository, a client
    # configured with `core.autocrlf=true` rewrites every LF in a text file to
    # CRLF on checkout, so an archived page's committed bytes are CRLF while the
    # hash recorded at fetch time was taken over LF. Seventeen of the 2026-10-02
    # pass's twenty archived sources are in exactly that state, and every figure
    # read out of them was unverifiable without this second form. A page with no
    # CR byte in it is unaffected, so the normalisation is a fallback rather than
    # a blanket exemption: a mismatch that survives it is a real mismatch.
    crlf = bytes((13, 10))
    lf = bytes((10,))
    for entry in entries:
        saved = entry.get("saved_as")
        if not saved:
            continue
        recorded = str(entry["sha256"]).lower()
        candidates = _saved_as_candidates(pass_dir, str(saved))
        archived = next((p for p in candidates if p.is_file()), None)
        if archived is None:
            failures.append(
                f"[fetch-log-corroborates] {rel(log)} records {entry.get('url')!r} "
                f"archived as {saved!r}, but no such file exists. The log claims a "
                f"retrieval whose bytes are not in the repository."
            )
            continue
        raw = archived.read_bytes()
        unix_form = raw.replace(crlf, lf)
        as_committed = hashlib.sha256(raw).hexdigest()
        lf_normalised = hashlib.sha256(unix_form).hexdigest()
        if as_committed == recorded:
            form, on_disk = "as committed", len(raw)
        elif lf_normalised == recorded:
            form, on_disk = "LF-normalised", len(unix_form)
        else:
            failures.append(
                f"[fetch-log-corroborates] {rel(archived)} does not hash to the sha256 "
                f"recorded for {entry.get('url')!r}, in either form: recorded "
                f"{recorded}, the committed bytes hash to {as_committed}, and their LF "
                f"normalisation to {lf_normalised}. Either the source moved or the bytes "
                f"were edited after the fetch, and every figure read out of them is now "
                f"unanchored."
            )
            continue
        size = entry.get("bytes")
        if isinstance(size, int) and on_disk != size:
            failures.append(
                f"[fetch-log-corroborates] {rel(archived)} is {on_disk} bytes "
                f"{form}; {rel(log)} recorded {size} for {entry.get('url')!r}."
            )

    # And the other direction: an archived source no log entry accounts for is a
    # page a reader is invited to trust with no record of where it came from.
    # A top-level source is matched by basename, which is how every log before
    # 2026-10-07 can be read; a source in a subdirectory of sources/ is matched
    # by its path inside the pass, because two subdirectories can hold files of
    # one name.
    logged_names = set()
    logged_paths = set()
    for e in entries:
        saved = str(e.get("saved_as") or "")
        if not saved:
            continue
        logged_names.add(saved.replace(chr(92), "/").split("/")[-1])
        inside = _path_inside_pass(pass_dir, saved)
        if inside is not None:
            logged_paths.add(inside)
    for path in sorted(p for p in sources.rglob("*") if p.is_file()):
        inside = path.relative_to(pass_dir).as_posix()
        top_level = path.parent == sources
        if (top_level and path.name in logged_names) or inside in logged_paths:
            continue
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        failures.append(
            f"[fetch-log-corroborates] {rel(path)} "
            f"({path.stat().st_size:,} bytes, sha256 {digest[:16]}...) has no entry "
            f"in {rel(log)}. Every archived source records the retrieval that "
            f"produced it: URL, HTTP status, byte count and hash. Add the entry, or "
            f"delete the file and cite nothing to it."
        )


# The kinds a provenance may put in front of its subject. `scored:` says the
# subject carries a figure and `leaderboard:` says what was read, so the two
# compose as `scored:leaderboard:<page>-on-YYYY-MM-DD`. Only the outer kind is
# optional, and `unscored:` is handled where it appears because it asserts no
# reading at all.
PROVENANCE_KINDS = {
    "scored",
    "leaderboard",
}


def check_provenance_in_log(pass_dir: Path) -> None:
    """A provenance string may not assert a dated reading the log does not record.

    The defect this was written for is in the pass it ships with. Repairing a
    fabricated quotation required writing down where the corrected figure came
    from, and the provenance cell added to settle it asserted a leaderboard lookup
    at a score and on a date that no fetch log entry records. It was fabricated in
    exactly the same way as the quotation it was written to fix: by asserting a
    retrieval that had not happened.

    The rule is narrow on purpose. A provenance string may claim a dated reading
    only if a log entry exists that puts the subject on the record with a read
    date on or before the date claimed. Nothing here decides whether the reading
    should have happened; it decides only that the repository's own record of
    retrievals has to contain it.

    A provenance string is `kind:subject-on-YYYY-MM-DD`, or one of two things
    that assert no retrieval:

    * `unscored:<reason>` - the leaderboard has no row for this SKU. Validated by
      `unscored-model`, which requires the marker to be the only way past a row
      whose score cannot be joined, so it cannot be used to smuggle a borrowed
      score past anything.
    * `UNKNOWN` - nothing is claimed. Accepted as an answer, never as evidence.

    `subject` names what was read: a URL path, an archived file, or a slug. It has
    to match a retrieval the log records.
    """
    log_path = pass_dir / "data" / "fetch-log.json"
    data = pass_dir / "data"
    if not data.is_dir():
        return
    date_re = re.compile(r"(\d{4}-\d{2}-\d{2})")
    reads: list[tuple[str, str]] = []
    if log_path.is_file():
        try:
            entries = json.loads(log_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            entries = []
        for entry in entries if isinstance(entries, list) else []:
            url = str(entry.get("url") or "")
            when = str(entry.get("read_date") or pass_dir.name)
            saved = str(entry.get("saved_as") or "")
            if url:
                # The archived page's own name is part of the provenance of a
                # reading taken out of it: the leaderboard payload is archived as
                # `aa-models.html`, so a score read out of it is corroborated by
                # the file the bytes came from.
                reads.append((url + " " + saved.replace(chr(92), "/"), when))
    for path in sorted(data.glob("*.csv")):
        header, rows = read_rows(path)
        if not header:
            continue
        for column in ("aa_score_provenance", "score_provenance", "provenance"):
            if column not in header:
                continue
            i = header.index(column)
            for offset, row in enumerate(data_rows(rows), start=1):
                if len(row) <= i:
                    continue
                value = row[i].strip()
                if not value or value.upper() == "UNKNOWN":
                    continue
                kind, _, rest = value.partition(":")
                if not rest:
                    failures.append(
                        f"[provenance-in-log] {rel(path)} data row {offset}: "
                        f"{column}={value!r} does not say what kind of reading it "
                        f"records. The form is 'kind:subject-on-YYYY-MM-DD', or "
                        f"'unscored:<reason>' when there is no score."
                    )
                    continue
                if kind.strip().lower().startswith("unscored"):
                    continue
                # A provenance may name a second kind: `scored:leaderboard:<page>`.
                # The kinds are the vocabulary; the subject is what is left, and it
                # keeps its own `leaderboard:` prefix, so it can contain a colon.
                rest = rest.strip()
                prefix, _, remainder = rest.partition(":")
                if prefix.strip().lower() in PROVENANCE_KINDS and remainder.strip():
                    rest = remainder.strip()
                # `kind:subject-on-YYYY-MM-DD`. The date is the last one, so it
                # is stripped from the right.
                subject = rest
                claimed = None
                for match in date_re.finditer(subject):
                    claimed = match
                if claimed and not subject[claimed.end():].strip():
                    subject = subject[: claimed.start()].strip().rstrip("-")
                    if subject.endswith("-on"):
                        subject = subject[:-3]
                if not claimed or not subject:
                    failures.append(
                        f"[provenance-in-log] {rel(path)} data row {offset}: "
                        f"{column}={value!r} asserts a reading without saying when it "
                        f"was taken. An undated provenance cannot be checked against a "
                        f"fetch log and is not one."
                    )
                    continue
                when = claimed.group(1)

                def records(entry: str, read_on: str) -> bool:
                    """Does this logged retrieval put the subject on the record?

                    Two ways. The subject appears in the URL, which is the case for
                    a per-model page. Or the subject appears in the name of the
                    archived file the bytes were saved to, which is the case for a
                    payload the reader extracted the figure from.

                    The second rule is why the subject of a leaderboard score is
                    the archived page's name rather than the slug: the slug is the
                    row's `model_slug`, and the page is what the log can vouch for.
                    """
                    if read_on > when:
                        return False
                    lowered = entry.lower()
                    if subject in lowered or subject in lowered.replace("/", "-"):
                        return True
                    return False

                if any(records(entry, read_on) for entry, read_on in reads):
                    continue
                where = rel(log_path) if log_path.is_file() else "the fetch log"
                failures.append(
                    f"[provenance-in-log] {rel(path)} data row {offset}: "
                    f"{column}={value!r} asserts that {subject!r} was read on or before "
                    f"{when}, and {where} records no such retrieval. A provenance string "
                    f"that names a reading the repository does not record is an "
                    f"assertion, not a provenance. Add the fetch, or write "
                    f"'unscored:<reason>'."
                )
