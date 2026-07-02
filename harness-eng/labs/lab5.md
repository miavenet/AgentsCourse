# Lab 5 — Evals: The Steering Wheel of the Harness (~45 min)

Goal: build a miniature but real evaluation harness — task set, automated
grading, JSONL trace log — and use it to *measure* whether a harness change
helps. After this lab, "it seems better" stops being an acceptable sentence.

Prereqs: Labs 1–4. Work in `harness-eng/scratch/lab5/`:

```bash
mkdir -p harness-eng/scratch/lab5 && cd harness-eng/scratch/lab5
```

### Step 1 — Define the task set
Create `tasks.jsonl` — five tasks with machine-checkable expectations:

```jsonl
{"id": "t1", "prompt": "What is 17 * 23? Reply with only the number.", "expect_regex": "^\\s*391\\s*$"}
{"id": "t2", "prompt": "Reverse the string 'harness'. Reply with only the result.", "expect_regex": "^\\s*ssenrah\\s*$"}
{"id": "t3", "prompt": "Name the protocol that connects AI models to tools and data sources, standardized by Anthropic. One word/acronym only.", "expect_regex": "MCP"}
{"id": "t4", "prompt": "If a task takes 3 agents and each needs 4 tool integrations without a shared protocol, how many integrations total? Only the number.", "expect_regex": "^\\s*12\\s*$"}
{"id": "t5", "prompt": "Give the Gherkin keyword that states the precondition of a scenario. One word only.", "expect_regex": "(?i)given"}
```

CHECK: `wc -l tasks.jsonl` → 5.
Concept: an eval starts from tasks with verifiable expectations — write the
check before you care about the score.

### Step 2 — Write the runner
Create `run_eval.py`:

```python
#!/usr/bin/env python3
"""Tiny eval harness: runs tasks through `claude -p`, grades, logs traces."""
import json, re, subprocess, sys, time

MODEL = sys.argv[1] if len(sys.argv) > 1 else "haiku"
EXTRA = sys.argv[2:]          # optional extra claude flags (the "harness change")

results = []
with open("tasks.jsonl") as f, open("traces.jsonl", "a") as log:
    for line in f:
        task = json.loads(line)
        t0 = time.time()
        proc = subprocess.run(
            ["claude", "-p", "--model", MODEL, "--allowedTools", "", *EXTRA,
             task["prompt"]],
            capture_output=True, text=True, timeout=120)
        answer = proc.stdout.strip()
        ok = bool(re.search(task["expect_regex"], answer))
        trace = {"task": task["id"], "model": MODEL, "extra": EXTRA,
                 "answer": answer[:200], "pass": ok,
                 "latency_s": round(time.time() - t0, 1)}
        log.write(json.dumps(trace) + "\n")
        results.append(ok)
        print(f"{task['id']}: {'PASS' if ok else 'FAIL'}  ({answer[:60]!r})")

print(f"\nscore: {sum(results)}/{len(results)}")
```

CHECK: `python3 run_eval.py haiku` runs all 5 tasks and prints a score.
Record the score.
Concept: eval = tasks + runner + grader + traces. Yours is 40 lines and
already produces evidence.

### Step 3 — Read your traces
```bash
python3 -c "
import json
for l in open('traces.jsonl'):
    t = json.loads(l)
    print(t['task'], t['pass'], t['latency_s'], 's')"
```

CHECK: one line per run with pass/latency — your observability layer.
Concept: traces are the raw material of both evaluation and debugging; no
traces, no evidence (Day 4: observability is the prerequisite).

### Step 4 — Make a harness change and MEASURE it
Hypothesis: a system-prompt nudge improves format compliance. Run the same
eval with a harness delta — the model is unchanged:

```bash
python3 run_eval.py haiku --append-system-prompt \
  "Answer with the minimal exact string requested. No preamble, no punctuation, no explanation."
```

CHECK: you have two scores for the same model. State: did the change help,
hurt, or do nothing — and on which tasks?
Concept: this is harness engineering's core loop — change one layer,
re-measure, keep or revert. Feelings don't survive contact with a task set.

### Step 5 — Find the flaky task
Run the winning configuration twice more. Compare per-task results across
runs.

CHECK: you can name which task (if any) flips between runs.
Concept: non-determinism means an eval is a distribution, not a number —
production harnesses run N trials and track rates.

### Step 6 — When exact checks run out
One of your five checks is a regex on a factual answer (t3). Say to your
coach: for a task like "summarize this whitepaper section", what replaces
the regex, and what new risk does that grader introduce?

CHECK: you name LLM-as-judge (or rubric-based model grading) AND one of its
risks (judge shares generator blind spots, drift, gameability, cost).
Concept: graders form a ladder — exact checks → rubrics → model judges →
humans — matched to how open-ended the task is.

## Recap

### L5-R1
Q: Name the four components every eval harness needs, however small.
Key:
- Task set with expectations, a runner, a grader/check, and trace logging

### L5-R2
Q: Why must a harness change (like your Step-4 system prompt) be judged across multiple runs and tasks rather than one glance?
Key:
- Agent output is non-deterministic — single runs are samples; an eval is a distribution (rates over a task set)
- Per-task breakdown shows *where* a change helps or hurts, not just whether

## Theory

The Day-4 whitepaper's evaluation half argues the unit under test is a
trajectory, not a function: decide what to evaluate (output quality, tool
trajectory, safety, cost/latency), pick methods per dimension (exact checks
where possible, LLM-as-judge for open-ended quality, humans for high
stakes), and run continuously — evals are the harness's steering wheel, not
its MOT test. The surveys in `resources/papers/` (arXiv 2503.16416,
2507.21504) map this space academically: capability vs behavior evals,
benchmark contamination, and trajectory-aware grading. Your 40-line runner
is the smallest honest member of that family.
Deep dives: Day-4 whitepaper "Evaluation: Orchestrating Quality";
resources/papers/ surveys; awesome-evals list (links.md).
