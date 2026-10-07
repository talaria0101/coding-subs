#!/usr/bin/env python3
"""Merge fetch logs into one, re-pointing every archived file at its new home.

    python3 tools/merge-fetch-logs.py LOG [LOG ...] --map OLD_PREFIX=NEW_PREFIX
                                      [--map ...] (--out MERGED | --dry-run)
                                      [--copy-sources DEST_DIR]

Each LOG is a JSON list of attempt records as `tools/fetch-source.py --append`
writes them. The records are concatenated in argument order, and every record
that names an archived file in `saved_as` is checked and rewritten:

* **Where the file is.** An absolute `saved_as` is used as written. A relative
  one is resolved against the directory of the log that holds it, then against
  the working directory. Either separator is accepted.
* **Where it goes.** `--map OLD_PREFIX=NEW_PREFIX` rewrites the resolved path.
  OLD_PREFIX is a directory, made absolute against the working directory, and
  matches whole path components; the longest matching prefix wins. NEW_PREFIX
  must be a relative path, and the rewritten `saved_as` is always a POSIX
  relative path such as `2026-10-07/sources/x.html`. A file no map covers is an
  error, because a merged log pointing into a scratch directory names bytes the
  repository will not hold.
* **That the bytes are the bytes.** The SHA-256 is recomputed from the file and
  compared with the recorded one, and the byte count likewise. A mismatch is an
  error: a log that vouches for bytes it does not describe is worse than none.
* **That nothing is overwritten.** Two records that map to one destination with
  different bytes are a collision, and so is a destination already holding
  different bytes under `--copy-sources`. Both sides are listed. Identical bytes
  at one destination are not a collision.

`--copy-sources DEST_DIR` copies each file to DEST_DIR joined with its rewritten
`saved_as`, so DEST_DIR is the directory those paths are relative to, normally
the repository root. A file already there with identical bytes is verified and
left alone. `--dry-run` runs every check and prints what would be written and
copied, and writes nothing.

Nothing is written or copied unless every check passes. The exit code is 0 on
success, 1 when any record fails a check, and 2 on a usage error.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path, PurePosixPath


@dataclass
class Placement:
    """Where one archived file comes from and where it is going."""

    source: Path
    destination: str
    sha256: str
    origin: str


def _posix_abs(path: str | Path) -> str:
    return Path(os.path.abspath(path)).as_posix()


def parse_map(value: str) -> tuple[str, str]:
    if "=" not in value:
        raise argparse.ArgumentTypeError(f"--map {value!r} is not OLD_PREFIX=NEW_PREFIX")
    old, new = value.split("=", 1)
    if not old or not new:
        raise argparse.ArgumentTypeError(f"--map {value!r} has an empty side")
    new_posix = new.replace("\\", "/").rstrip("/")
    pure = PurePosixPath(new_posix)
    if pure.is_absolute() or ".." in pure.parts or (pure.parts and ":" in pure.parts[0]):
        raise argparse.ArgumentTypeError(
            f"--map {value!r}: NEW_PREFIX must be a relative path without '..'"
        )
    return _posix_abs(old).rstrip("/"), str(pure)


def resolve_saved_as(saved: str, log_dir: Path) -> list[Path]:
    """Candidate locations of the file a record names, in the order tried."""
    text = saved.replace("\\", "/")
    path = Path(text)
    if path.is_absolute():
        return [path]
    return [log_dir / path, Path.cwd() / path]


def apply_map(source: Path, maps: list[tuple[str, str]]) -> str | None:
    absolute = _posix_abs(source)
    best = None
    for old, new in maps:
        if absolute == old or absolute.startswith(old + "/"):
            if best is None or len(old) > len(best[0]):
                best = (old, new)
    if best is None:
        return None
    rest = absolute[len(best[0]):].lstrip("/")
    return f"{best[1]}/{rest}" if rest else best[1]


def merge(logs: list[Path], maps: list[tuple[str, str]],
          copy_root: Path | None) -> tuple[list[dict], list[Placement], list[str], list[str]]:
    """Merge the logs. Returns (records, placements, errors, notes); writes nothing."""
    merged: list[dict] = []
    errors: list[str] = []
    notes: list[str] = []
    placed: dict[str, Placement] = {}

    for log in logs:
        try:
            entries = json.loads(log.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{log}: cannot be read as JSON: {exc}")
            continue
        if not isinstance(entries, list):
            errors.append(f"{log}: is not a JSON list of attempt records")
            continue
        for index, entry in enumerate(entries):
            origin = f"{log} record {index}"
            if not isinstance(entry, dict):
                errors.append(f"{origin}: is not a JSON object")
                continue
            record = dict(entry)
            merged.append(record)
            saved = record.get("saved_as")
            if not saved:
                continue
            candidates = resolve_saved_as(str(saved), log.parent)
            source = next((c for c in candidates if c.is_file()), None)
            if source is None:
                tried = ", ".join(str(c) for c in candidates)
                errors.append(f"{origin}: saved_as {saved!r} names no file (tried {tried})")
                continue
            destination = apply_map(source, maps)
            if destination is None:
                errors.append(
                    f"{origin}: {_posix_abs(source)} is under no --map OLD_PREFIX, so its "
                    f"saved_as cannot be rewritten"
                )
                continue
            raw = source.read_bytes()
            digest = hashlib.sha256(raw).hexdigest()
            recorded = str(record.get("sha256") or "").lower()
            if digest != recorded:
                lf = hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()
                hint = " (it matches the LF-normalised bytes)" if lf == recorded else ""
                errors.append(
                    f"{origin}: {source} hashes to {digest}, the log records "
                    f"{recorded or 'no sha256'}{hint}"
                )
                continue
            size = record.get("bytes")
            if isinstance(size, int) and size != len(raw):
                errors.append(
                    f"{origin}: {source} is {len(raw)} bytes, the log records {size}"
                )
                continue
            here = Placement(source, destination, digest, origin)
            earlier = placed.get(destination)
            if earlier is not None and earlier.sha256 != digest:
                errors.append(
                    f"collision at {destination}: {earlier.source} ({earlier.origin}, "
                    f"sha256 {earlier.sha256[:16]}) and {source} ({origin}, sha256 "
                    f"{digest[:16]}) hold different bytes"
                )
                continue
            if earlier is None:
                placed[destination] = here
                if copy_root is not None:
                    target = copy_root / destination
                    if target.exists():
                        existing = hashlib.sha256(target.read_bytes()).hexdigest() \
                            if target.is_file() else None
                        if existing != digest:
                            errors.append(
                                f"collision at {target}: it already holds different "
                                f"bytes (sha256 {(existing or 'not a file')[:16]}) from "
                                f"{source} ({origin}, sha256 {digest[:16]})"
                            )
                            continue
                        notes.append(f"verified {target} (identical bytes)")
            elif earlier.source != source:
                notes.append(
                    f"{destination}: {earlier.source} and {source} hold identical bytes"
                )
            record["saved_as"] = destination
    return merged, list(placed.values()), errors, notes


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("logs", nargs="+", type=Path, metavar="LOG")
    parser.add_argument("--map", dest="maps", action="append", type=parse_map,
                        required=True, metavar="OLD_PREFIX=NEW_PREFIX")
    parser.add_argument("--out", type=Path, help="where to write the merged log")
    parser.add_argument("--copy-sources", type=Path, metavar="DEST_DIR",
                        help="copy each file to DEST_DIR/<rewritten saved_as>")
    parser.add_argument("--dry-run", action="store_true",
                        help="check and report, write and copy nothing")
    args = parser.parse_args(argv)
    if not args.dry_run and args.out is None:
        parser.error("--out is required unless --dry-run is given")

    copy_root = args.copy_sources
    merged, placements, errors, notes = merge(args.logs, args.maps, copy_root)

    saved = sum(1 for r in merged if r.get("saved_as"))
    print(f"{len(merged)} records from {len(args.logs)} log(s); {saved} name an "
          f"archived file; {len(placements)} distinct destination(s)")
    for note in notes:
        print(f"  note: {note}")
    if errors:
        print(f"\nREFUSED ({len(errors)}): nothing written, nothing copied", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1

    if args.dry_run:
        for placement in placements:
            action = "copy" if copy_root is not None else "map"
            print(f"  would {action} {placement.source} -> {placement.destination}")
        if args.out is not None:
            print(f"  would write {len(merged)} records to {args.out}")
        print("dry run: nothing written")
        return 0

    if copy_root is not None:
        for placement in placements:
            target = copy_root / placement.destination
            if target.is_file():
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(placement.source, target)
            if hashlib.sha256(target.read_bytes()).hexdigest() != placement.sha256:
                print(f"copy of {placement.source} to {target} does not hash to "
                      f"{placement.sha256}", file=sys.stderr)
                return 1
            print(f"  copied {placement.source} -> {target}")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(merged, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(merged)} records to {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
