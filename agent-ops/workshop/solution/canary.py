#!/usr/bin/env python3
"""Canary rollout — send a slice of live traffic to a candidate version,
score its OUTPUT QUALITY (not just "did it return"), and roll back
automatically on regression. The gate (gate.py) is offline judgment before
deploy; the canary is online judgment during deploy — you need both, and a
canary only catches regressions its probe traffic actually exercises.

    python3 canary.py v2 --requests 6 --share 3   # every 3rd request -> v2
"""
import argparse
import re
import sys
from pathlib import Path

from agent_service import run_task, active_version

# A quality probe, not a liveness probe: a good canary asserts the answer is
# RIGHT, because a bad prompt usually still "finishes" — it just finishes
# wrong. Arithmetic is a reliable probe (Haiku is flaky at counting files);
# it still catches a numbers-as-words regression ("seven" != "7").
PROBE = "What is 3 plus 4? Finish with just the number."
EXPECT = re.compile(r"\b7\b")
ROLLBACK_MARGIN = 0.34   # candidate fail-rate may exceed stable's by at most this


def fail_rate(records):
    # a request "fails" if it errored OR returned a wrong answer
    bad = sum(not r["ok"] or not EXPECT.search(r["result"]) for r in records)
    return bad / len(records) if records else 0.0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("candidate")
    ap.add_argument("--requests", type=int, default=6)
    ap.add_argument("--share", type=int, default=3, help="every Nth request -> candidate")
    a = ap.parse_args()
    stable = active_version()
    if stable == a.candidate:
        sys.exit(f"candidate {a.candidate} is already the active version")
    routed = {stable: [], a.candidate: []}
    for i in range(1, a.requests + 1):
        ver = a.candidate if i % a.share == 0 else stable
        rec = run_task(PROBE, ver, max_steps=4)
        ok = rec["ok"] and bool(EXPECT.search(rec["result"]))
        routed[ver].append(rec)
        print(f"req {i}: -> {ver:4} good={ok} ({rec['latency_s']}s)  {rec['result'][:50]!r}")
    f_stable, f_canary = fail_rate(routed[stable]), fail_rate(routed[a.candidate])
    print(f"fail rates: {stable}={f_stable:.0%}  {a.candidate}={f_canary:.0%}")
    if f_canary - f_stable > ROLLBACK_MARGIN:
        Path("active_version").write_text(stable + "\n")
        print(f"ROLLBACK — {a.candidate} regressed; active_version stays {stable}")
        sys.exit(1)
    Path("active_version").write_text(a.candidate + "\n")
    print(f"PROMOTED — active_version -> {a.candidate}")
