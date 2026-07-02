#!/usr/bin/env python3
"""agg.py — reference answer for Lab 2. Reduce a pocket-agent traces.jsonl
into per-run metrics and the fleet-level numbers an on-call engineer
watches. A "run" is the steps from step==1 up to (and including) a finish;
step resets to 1 each run, so a new step==1 starts a new run.

    python3 agg.py traces.jsonl
"""
import json
import sys
from collections import Counter


def pctl(xs, p):
    xs = sorted(xs)
    return xs[min(len(xs) - 1, int(p / 100 * len(xs)))] if xs else 0.0


def load_runs(path):
    runs, cur = [], []
    for line in open(path):
        rec = json.loads(line)
        if rec["step"] == 1 and cur:      # new run begins
            runs.append(cur)
            cur = []
        cur.append(rec)
    if cur:
        runs.append(cur)
    return runs


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "traces.jsonl"
    runs = load_runs(path)
    tool_errors = Counter()
    latencies, total_steps, successes = [], 0, 0
    print(f"{'run':>4}{'steps':>7}{'lat_s':>8}{'outcome':>10}")
    for i, run in enumerate(runs, 1):
        steps = len(run)
        lat = round(sum(r.get("latency_s", 0) for r in run), 1)
        ok = any(r["action"] == "finish" for r in run)
        for r in run:
            if not r.get("ok", True):
                tool_errors[r["action"]] += 1
        total_steps += steps
        successes += ok
        latencies.append(lat)
        print(f"{i:>4}{steps:>7}{lat:>8}{'finish' if ok else 'FAILED':>10}")
    n = len(runs) or 1
    print("-" * 29)
    print(f"runs={len(runs)}  success_rate={successes/n:.0%}  "
          f"mean_steps={total_steps/n:.1f}")
    print(f"latency p50={pctl(latencies,50)}s  p95={pctl(latencies,95)}s")
    print(f"cost_per_success={total_steps/successes:.1f} steps"
          if successes else "cost_per_success=inf (no successful runs)")
    if tool_errors:
        print("tool errors by action: " +
              ", ".join(f"{a}={c}" for a, c in tool_errors.most_common()))
