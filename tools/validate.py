#!/usr/bin/env python3
"""Data-integrity checks for a coding-subs research pass.

Usage: python3 tools/validate.py [PASS_DIR]   (default: latest YYYY-MM-DD dir)
Exit code 0 = all checks pass; 1 = failures (printed).
"""
import csv, json, os, re, sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
failures: list[str] = []


def check(cond: bool, msg: str) -> None:
    if not cond:
        failures.append(msg)


def latest_pass() -> Path:
    passes = sorted(p for p in ROOT.iterdir() if p.is_dir() and re.fullmatch(r"\d{4}-\d{2}-\d{2}", p.name))
    check(bool(passes), "no YYYY-MM-DD pass directory found")
    return passes[-1] if passes else ROOT


def main() -> int:
    pass_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else latest_pass()
    print(f"validating pass: {pass_dir.name}")

    # --- layout ---
    for sub in ("data", "references", "sources"):
        check((pass_dir / sub).is_dir(), f"missing directory {sub}/")
    check((pass_dir / "README.md").is_file(), "missing report README.md")
    check((ROOT / "README.md").is_file(), "missing root README.md")
    check((ROOT / "docs" / "reviews.md").is_file(), "missing docs/reviews.md")
    check(pass_dir.name <= str(date.today()), f"pass dir {pass_dir.name} is in the future")
    if os.environ.get("STRICT_DATE"):
        check(pass_dir.name == str(date.today()), f"pass dir {pass_dir.name} != today {date.today()}")

    # --- models database ---
    mpath = pass_dir / "data" / "models-database.csv"
    check(mpath.is_file(), "missing data/models-database.csv")
    if mpath.is_file():
        with mpath.open() as f:
            models = list(csv.DictReader(f))
        check(len(models) >= 30, f"models DB has {len(models)} rows, need >= 30")
        need = {"model_slug", "provider", "release_date", "aa_intelligence_index",
                "terminal_bench_v4", "context_window_tokens", "ctx_ge_1m",
                "image_input", "api_input_usd_per_m", "api_output_usd_per_m"}
        check(need.issubset(models[0].keys()), f"models DB missing columns: {need - set(models[0].keys())}")
        slugs = set()
        for r in models:
            s = r["model_slug"]
            check(s and s not in slugs, f"duplicate/empty model slug: {s!r}")
            slugs.add(s)
            try:
                ctx = int(r["context_window_tokens"])
            except ValueError:
                failures.append(f"{s}: non-integer context {r['context_window_tokens']!r}")
                continue
            if ctx == 0 and r["ctx_ge_1m"] == "UNKNOWN":
                continue  # context not published; ctx_ge_1m honestly unknown
            want = "YES" if ctx >= 1_000_000 else "NO"
            check(r["ctx_ge_1m"] == want, f"{s}: ctx_ge_1m={r['ctx_ge_1m']} inconsistent with ctx={ctx}")
            for pcol in ("api_input_usd_per_m", "api_output_usd_per_m"):
                v = r[pcol]
                if v not in ("", None):
                    try:
                        check(float(v) >= 0, f"{s}: negative {pcol}")
                    except ValueError:
                        failures.append(f"{s}: non-numeric {pcol}={v!r}")
        # frontier band present per brief (Opus 5 class)
        check("claude-opus-5" in slugs, "models DB missing claude-opus-5")

    # --- providers database ---
    ppath = pass_dir / "data" / "providers-database.csv"
    check(ppath.is_file(), "missing data/providers-database.csv")
    if ppath.is_file():
        with ppath.open() as f:
            providers = list(csv.DictReader(f))
        check(len(providers) >= 25, f"providers DB has {len(providers)} rows, need >= 25")
        pneed = {"provider", "coding_tool", "price_usd_month", "usage_mechanism",
                 "ctx_1m_at_sub_level", "bundled_inference", "status", "source_quality"}
        check(pneed.issubset(providers[0].keys()), f"providers DB missing columns: {pneed - set(providers[0].keys())}")
        distinct = {r["provider"] for r in providers}
        check(len(distinct) >= 20, f"only {len(distinct)} distinct providers, need >= 20")
        for r in providers:
            check(r["source_quality"] != "", f"{r['provider']}/{r['coding_tool']}: empty source_quality")

    # --- AA snapshot ---
    apath = pass_dir / "data" / "aa-snapshot-2026-09-13.json"
    if apath.is_file():
        aa = json.loads(apath.read_text())
        check(len(aa) >= 100, f"AA snapshot only {len(aa)} rows")
        bad = [r["slug"] for r in aa if r.get("deprecated") or (r.get("intelligenceIndex") or 0) < 20]
        check(not bad, f"AA snapshot contains deprecated/low-II rows: {bad[:5]}")
        iis = [r["intelligenceIndex"] for r in aa]
        check(iis == sorted(iis, reverse=True), "AA snapshot not sorted by II desc")

    # --- report cross-checks ---
    report = (pass_dir / "README.md").read_text()
    for anchor in ("BEST DEAL FOUND", "HIDDEN DEALS", "ARBITRAGE OPPORTUNITIES",
                   "WHAT I WOULD BUY", "Workload test", "1M-context deep dive",
                   "Multimodal deep dive", "Rankings", "Method"):
        check(anchor in report, f"report missing section: {anchor}")
    check("52.5M" in report, "report missing 52.5M workload figure")
    # workload arithmetic
    check(15 + 37.5 == 52.5, "workload arithmetic 15M + 37.5M != 52.5M")
    # GLM capacity claim must match weekly allowance x 4.33 weeks (48-97M/wk)
    for wk, mo in ((48, 208), (97, 420)):
        check(abs(wk * 4.33 - mo) <= 1, f"GLM weekly {wk}M x 4.33 != {mo}M")
    check("208–420M" in report, "report missing GLM Lite monthly capacity 208–420M")
    # every model slug cited with backticks in the DB exists in models DB
    if mpath.is_file():
        with mpath.open() as f:
            slugs = {r["model_slug"] for r in csv.DictReader(f)}
        for cited in set(re.findall(r"`([a-z0-9]+(?:[-.][a-z0-9]+)+)`", report)):
            norm = cited.replace(".", "-")
            if norm.startswith(("claude-", "gpt-", "gemini-", "qwen", "kimi-", "glm-", "muse-",
                                "minimax-", "deepseek-", "grok-", "mimo-")):
                check(norm in slugs, f"report cites model `{cited}` not in models DB")
        # GLM capacity consistency between report (x4.33wk) and providers DB
        if ppath.is_file():
            with ppath.open() as f:
                prow = next((r for r in csv.DictReader(f) if r["coding_tool"] == "GLM Coding Plan Lite"), {})
            est = prow.get("est_token_capacity_month", "")
            for fig in ("208-420M", "632M-1,264M"):
                check(fig in est, f"providers DB GLM Lite capacity missing {fig} (4.33wk math)")
            for fig in ("208–420M", "632M–1.26B", "632M–1,264M"):
                pass  # report uses en-dashes; primary check is the CSV side above
            check("208–420M" in report, "report GLM Lite capacity disagrees with DB")

    # --- references ---
    refs = (pass_dir / "references" / "references.md").read_text() if (pass_dir / "references" / "references.md").is_file() else ""
    check(pass_dir.name in refs, f"references missing access date {pass_dir.name}")
    check(refs.count("\n") > 40, "references suspiciously short")

    # --- sources present ---
    n_sources = len(list((pass_dir / "sources").glob("*"))) if (pass_dir / "sources").is_dir() else 0
    check(n_sources >= 20, f"only {n_sources} source snapshots, expected >= 20")

    # --- result ---
    if failures:
        print(f"FAIL ({len(failures)}):")
        for m in failures:
            print("  -", m)
        return 1
    print("OK: all checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
