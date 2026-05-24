"""
Bench harness for /api/chat (and optionally /api/vapi/chat/completions).

Measures:
  - end-to-end latency (p50/p95/p99 across repeats)
  - tool-selection accuracy vs expected_tool_any_of (substring, case-insensitive)
  - per-tag breakdown

Assumes the dev-bypass auth is active:
  ENVIRONMENT=development, DEV_API_KEY=dev-bypass, DEV_USER_ID=<id>

Usage:
  uv run scripts/bench_chat.py                   # all cases, 1 run each
  uv run scripts/bench_chat.py --n 3             # 3 repeats for stable p95
  uv run scripts/bench_chat.py --filter gmail    # only cases with "gmail" in id or tag
  uv run scripts/bench_chat.py --endpoint vapi   # hit VAPI custom-llm path
  uv run scripts/bench_chat.py --show-response   # print full response bodies
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
from pathlib import Path
from typing import Any
from urllib import request as urlrequest
from urllib.error import HTTPError, URLError

ROOT = Path(__file__).resolve().parent
CASES_FILE = ROOT / "bench_cases.jsonl"
BASE_URL = "http://127.0.0.1:8000"
COOKIE = "api_key=dev-bypass"


def load_cases(filter_str: str | None) -> list[dict[str, Any]]:
    cases = []
    for line in CASES_FILE.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        cases.append(json.loads(line))
    if filter_str:
        f = filter_str.lower()
        cases = [c for c in cases if f in c["id"].lower() or any(f in t.lower() for t in c.get("tags", []))]
    return cases


def build_payload(endpoint: str, prompt: str) -> tuple[str, bytes]:
    if endpoint == "chat":
        url = f"{BASE_URL}/api/chat"
        body = {"messages": [{"role": "user", "content": prompt}]}
    elif endpoint == "vapi":
        url = f"{BASE_URL}/api/vapi/chat/completions"
        body = {
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
        }
    else:
        raise ValueError(f"unknown endpoint: {endpoint}")
    return url, json.dumps(body).encode("utf-8")


def call_once(endpoint: str, prompt: str, timeout: float = 60.0) -> dict[str, Any]:
    url, data = build_payload(endpoint, prompt)
    req = urlrequest.Request(
        url,
        data=data,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "Cookie": COOKIE,
        },
    )
    t0 = time.perf_counter()
    try:
        with urlrequest.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            status = resp.status
    except HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        status = e.code
    except URLError as e:
        body = f"URLError: {e}"
        status = 0
    elapsed = time.perf_counter() - t0
    try:
        parsed = json.loads(body)
    except json.JSONDecodeError:
        parsed = {"_raw": body[:500]}
    return {"elapsed_s": elapsed, "status": status, "body": parsed}


def extract_tool_names(endpoint: str, body: dict[str, Any]) -> list[str]:
    if endpoint == "chat":
        tcs = body.get("tool_calls") or []
        names = []
        for tc in tcs:
            if isinstance(tc, dict):
                n = tc.get("name") or tc.get("function", {}).get("name") or tc.get("tool")
                if n:
                    names.append(n)
            elif isinstance(tc, str):
                names.append(tc)
        return names
    if endpoint == "vapi":
        choices = body.get("choices") or []
        names = []
        for ch in choices:
            msg = ch.get("message", {}) or {}
            for tc in msg.get("tool_calls") or []:
                fn = (tc.get("function") or {}).get("name")
                if fn:
                    names.append(fn)
        return names
    return []


def tool_match(actual: list[str], expected_any: list[str]) -> bool:
    if not expected_any:
        return len(actual) == 0
    if not actual:
        return False
    low = [a.lower() for a in actual]
    return any(any(e.lower() in a for a in low) for e in expected_any)


def pct(vals: list[float], q: float) -> float:
    if not vals:
        return 0.0
    k = int(round((len(vals) - 1) * q))
    return sorted(vals)[k]


def run_bench(cases: list[dict[str, Any]], endpoint: str, n: int, show_response: bool) -> int:
    print(f"\nRunning {len(cases)} cases × {n} repeats against {endpoint} ({BASE_URL})")
    print("=" * 100)

    per_case_rows = []
    tag_stats: dict[str, list[tuple[bool, float]]] = {}

    for case in cases:
        case_id = case["id"]
        prompt = case["prompt"]
        expect = case.get("expect_tool_any_of", [])
        tags = case.get("tags", []) or ["-"]

        latencies = []
        tool_hits = []
        first_body = None
        first_status = None

        for _ in range(n):
            r = call_once(endpoint, prompt)
            latencies.append(r["elapsed_s"])
            first_body = first_body or r["body"]
            first_status = first_status or r["status"]
            names = extract_tool_names(endpoint, r["body"])
            tool_hits.append((names, tool_match(names, expect)))

        p50 = pct(latencies, 0.50)
        p95 = pct(latencies, 0.95)
        passes = sum(1 for _, ok in tool_hits if ok)
        accuracy = passes / len(tool_hits)
        first_actual = tool_hits[0][0]

        pass_mark = "✓" if accuracy == 1.0 else ("~" if accuracy > 0 else "✗")
        expect_fmt = ",".join(expect) if expect else "(no tool)"
        actual_fmt = ",".join(first_actual) if first_actual else "(no tool)"
        print(
            f"  [{pass_mark}] {case_id:14} p50={p50*1000:6.0f}ms p95={p95*1000:6.0f}ms "
            f"status={first_status} acc={passes}/{n}  expect={expect_fmt}  got={actual_fmt}"
        )
        if show_response and first_body:
            snippet = json.dumps(first_body)[:300]
            print(f"       body: {snippet}")

        per_case_rows.append({
            "id": case_id, "tags": tags, "p50_ms": p50 * 1000, "p95_ms": p95 * 1000,
            "status": first_status, "accuracy": accuracy,
            "expected": expect, "actual": first_actual,
        })
        for t in tags:
            tag_stats.setdefault(t, []).append((accuracy == 1.0, p50))

    print("\nSummary")
    print("=" * 100)
    all_lat = [r["p50_ms"] / 1000 for r in per_case_rows]
    print(f"  latency across cases: p50={pct(all_lat, 0.5)*1000:.0f}ms "
          f"p95={pct(all_lat, 0.95)*1000:.0f}ms p99={pct(all_lat, 0.99)*1000:.0f}ms "
          f"max={max(all_lat)*1000:.0f}ms")
    overall_acc = statistics.mean(r["accuracy"] for r in per_case_rows) if per_case_rows else 0
    print(f"  accuracy: {overall_acc*100:.0f}%  "
          f"({sum(1 for r in per_case_rows if r['accuracy'] == 1.0)}/{len(per_case_rows)} fully correct)")

    print("\nBy tag:")
    for tag in sorted(tag_stats):
        rows = tag_stats[tag]
        acc = sum(1 for ok, _ in rows if ok) / len(rows)
        med = statistics.median(lat for _, lat in rows)
        print(f"  {tag:15} n={len(rows):2}  acc={acc*100:3.0f}%  p50={med*1000:5.0f}ms")

    fails = [r for r in per_case_rows if r["accuracy"] < 1.0]
    if fails:
        print("\nFailures:")
        for r in fails:
            print(f"  {r['id']:14} expected={r['expected']} got={r['actual']} "
                  f"({r['accuracy']*100:.0f}% across {n} runs)")
    else:
        print("\nAll cases passed.")

    return 1 if fails else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--endpoint", choices=["chat", "vapi"], default="chat")
    ap.add_argument("--n", type=int, default=1, help="repeats per case for latency stability")
    ap.add_argument("--filter", default=None, help="substring match on case id or tag")
    ap.add_argument("--show-response", action="store_true")
    args = ap.parse_args()

    cases = load_cases(args.filter)
    if not cases:
        print("no cases matched", file=sys.stderr)
        return 2
    return run_bench(cases, args.endpoint, args.n, args.show_response)


if __name__ == "__main__":
    raise SystemExit(main())
