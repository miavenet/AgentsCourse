#!/usr/bin/env python3
"""Aggregate service_log.jsonl into the metrics that matter for an agent
service, per prompt version. Exits 1 if any version breaches the SLO —
that exit code is what an alert (or a canary) hangs off.

    python3 metrics.py [service_log.jsonl] [--slo-errors 0.2]
"""
import argparse
import json
import sys
from collections import defaultdict


def pctl(xs, p):
    xs = sorted(xs)
    return xs[min(len(xs) - 1, int(p / 100 * len(xs)))] if xs else 0.0


def summarize(path: str) -> dict:
    by_ver = defaultdict(list)
    for line in open(path):
        rec = json.loads(line)
        by_ver[rec["version"]].append(rec)
    out = {}
    for ver, recs in sorted(by_ver.items()):
        lats = [r["latency_s"] for r in recs]
        out[ver] = {
            "requests": len(recs),
            "error_rate": round(sum(not r["ok"] for r in recs) / len(recs), 2),
            "p50_s": pctl(lats, 50),
            "p95_s": pctl(lats, 95),
            "guardrail_flags": sum(len(r.get("flags", [])) for r in recs),
        }
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("log", nargs="?", default="service_log.jsonl")
    ap.add_argument("--slo-errors", type=float, default=0.2)
    a = ap.parse_args()
    stats = summarize(a.log)
    print(f"{'ver':6}{'reqs':>6}{'err%':>7}{'p50s':>7}{'p95s':>7}{'flags':>7}")
    breach = False
    for ver, s in stats.items():
        print(f"{ver:6}{s['requests']:>6}{s['error_rate']:>7.0%}"
              f"{s['p50_s']:>7.1f}{s['p95_s']:>7.1f}{s['guardrail_flags']:>7}")
        if s["error_rate"] > a.slo_errors:
            breach = True
            print(f"  ALERT: {ver} error rate {s['error_rate']:.0%} "
                  f"exceeds SLO {a.slo_errors:.0%}")
    sys.exit(1 if breach else 0)
