#!/usr/bin/env python3
"""Probe OpenCode Zen: what an unauthenticated caller actually gets.

The repo's headline claim about this market is that only one endpoint answers
without a key. That claim was made by a prior pass and is re-tested here from
scratch, because it is the only live measurement in the repo and a reader has no
way to check it except by re-running this.

Three things are measured, separately, because they fail differently:
  1. reach      -- does /models answer with no credential?
  2. completion -- does a minimal chat completion answer with no credential?
  3. honesty    -- for anything that answers, is the reported token usage
                   consistent with the prompt that was sent?

(3) is the part a reader cannot check from a price table, and the part that
decides whether the reported usage can be used to budget a context window.
"""
import json
import statistics
import sys
import time
import urllib.error
import urllib.request

BASE = "https://opencode.ai/zen/v1"
UA = "Mozilla/5.0 (X11; Linux x86_64) coding-subs-probe/1.0"


def call(url: str, payload: dict | None = None, timeout: int = 60) -> dict:
    """One request, no Authorization header of any kind, by construction."""
    data = json.dumps(payload).encode() if payload is not None else None
    headers = {"User-Agent": UA, "Accept": "application/json"}
    if data is not None:
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(url, data=data, headers=headers)
    started = time.time()
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read()
            status = response.status
    except urllib.error.HTTPError as exc:
        body = exc.read()
        status = exc.code
    except Exception as exc:  # noqa: BLE001
        return {"status": None, "ms": int((time.time() - started) * 1000),
                "error": f"{type(exc).__name__}: {exc}"[:160], "json": None}
    parsed = None
    try:
        parsed = json.loads(body)
    except Exception:  # noqa: BLE001
        parsed = None
    return {"status": status, "ms": int((time.time() - started) * 1000),
            "bytes": len(body), "error": None, "json": parsed,
            "text": body[:400].decode("utf-8", "replace")}


def main() -> int:
    out_path = sys.argv[1] if len(sys.argv) > 1 else "opencode-zen-probe.json"
    result = {
        "probe": "OpenCode Zen anonymous access",
        "auth_header_sent": False,
        "base": BASE,
        "steps": {},
    }

    # 1. reach
    models = call(f"{BASE}/models")
    ids = []
    if models.get("json"):
        data = models["json"].get("data") or models["json"].get("models") or []
        ids = [m.get("id") for m in data if isinstance(m, dict) and m.get("id")]
    result["steps"]["models"] = {
        "status": models.get("status"),
        "ms": models.get("ms"),
        "bytes": models.get("bytes"),
        "model_count": len(ids),
        "error": models.get("error"),
    }
    result["model_ids"] = sorted(ids)

    free_ids = [i for i in ids if "free" in i.lower()]

    # 2. completion, three rounds, on every free-listed model
    probes = []
    for model in free_ids:
        runs = []
        for _ in range(3):
            r = call(f"{BASE}/chat/completions", {
                "model": model, "max_tokens": 10,
                "messages": [{"role": "user", "content": "Reply with the single word: ok"}],
            })
            entry = {"status": r.get("status"), "ms": r.get("ms"), "error": r.get("error")}
            body = r.get("json") or {}
            usage = body.get("usage") or {}
            choice = ((body.get("choices") or [{}])[0].get("message") or {})
            entry["content"] = (choice.get("content") or "")[:60]
            entry["prompt_tokens"] = usage.get("prompt_tokens")
            entry["completion_tokens"] = usage.get("completion_tokens")
            entry["total_tokens"] = usage.get("total_tokens")
            if not entry["content"]:
                entry["error_text"] = (r.get("text") or "")[:200]
            runs.append(entry)
            time.sleep(0.4)
        statuses = [x["status"] for x in runs]
        probes.append({
            "model": model,
            "runs": runs,
            "verdict": ("ANON_OK" if all(s == 200 for s in statuses)
                        else "AUTH_REQUIRED" if all(s in (401, 403) for s in statuses)
                        else f"HTTP_{statuses}"),
        })

    result["free_model_probes"] = probes
    anon_ok = [p["model"] for p in probes if p["verdict"] == "ANON_OK"]
    result["summary"] = {
        "models_reachable": models.get("status") == 200,
        "model_count": len(ids),
        "free_listed_models": len(free_ids),
        "free_models_answering_anonymously": len(anon_ok),
        "which": anon_ok,
    }

    # 3. honesty: does reported prompt_tokens track the prompt that was sent?
    honesty = []
    for size, filler in ((200, 0), (8_000, 7_800), (40_000, 39_800), (120_000, 119_800)):
        needle = "NEEDLE-9f3a2b-CONSTANT-7c1d"
        prompt = filler * "x" if filler else ""
        prompt = (
            f"Read this and reply with only the marker.\n{needle}\n"
            + ("filler text. " * (filler // 13 if filler else 0))
        )
        r = call(f"{BASE}/chat/completions", {
            "model": "space-bunny-free", "max_tokens": 16,
            "messages": [{"role": "user", "content": prompt}],
        })
        body = r.get("json") or {}
        usage = body.get("usage") or {}
        content = (((body.get("choices") or [{}])[0].get("message") or {}).get("content") or "")
        # A rough token estimate for ASCII prose: ~4 chars per token.
        honesty.append({
            "prompt_chars_sent": len(prompt),
            "status": r.get("status"),
            "prompt_tokens_reported": usage.get("prompt_tokens"),
            "completion_tokens_reported": usage.get("completion_tokens"),
            "content_len": len(content),
            "needle_echoed": needle in content,
            "content": content[:120],
        })
        time.sleep(0.6)
    result["steps"]["usage_honesty"] = honesty

    with open(out_path, "w") as handle:
        json.dump(result, handle, indent=2)

    print(f"models endpoint: HTTP {result['steps']['models']['status']}, "
          f"{len(ids)} models, {len(free_ids)} with 'free' in the id")
    print(f"free-listed models answering with no credential: {len(anon_ok)} -> {anon_ok}")
    print(f"{len(free_ids) - len(anon_ok)} of the free-listed models are not anonymously usable\n")
    print("Reported usage vs prompt actually sent:")
    print(f"{'chars sent':>12}{'status':>8}{'prompt_tokens':>16}{'content len':>13}{'needle':>8}")
    for h in honesty:
        print(f"{h['prompt_chars_sent']:>12,}{str(h['status']):>8}"
              f"{str(h['prompt_tokens_reported']):>16}{h['content_len']:>13}"
              f"{str(h['needle_echoed']):>8}")
    print(f"\nwritten to {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
