# Lab 2 — Observability: The Vibe Trajectory and the Metrics That Matter (~45 min)

Goal: you cannot operate what you cannot see. Turn your agent's raw
`traces.jsonl` into the four numbers an on-call engineer actually watches —
task success rate, latency percentiles, steps/cost per task, and tool
error rate by tool — and learn the OpenTelemetry GenAI vocabulary the whole
industry now standardizes on.

Prereqs: Lab 1. Work in:

```bash
mkdir -p agent-ops/scratch/lab2 && cd agent-ops/scratch/lab2
cp ../../../harness-eng/workshop/solution/pocket_agent.py .
mkdir data && for f in a b c; do printf "# $f\n" > data/$f.md; done && printf 'x\n' > data/note.txt
```

### Step 1 — Generate a trajectory worth reading
```bash
rm -f traces.jsonl
python3 pocket_agent.py "List the data directory, then read data/a.md, then finish telling me how many .md files exist."
cat traces.jsonl
```

CHECK: `traces.jsonl` has several lines, each a JSON object with `step`,
`action`, `ok`, `latency_s`. Name the sequence of actions you see.
Concept: this is the **Vibe Trajectory** (Day 4) — the ordered record of
think→tool→observe steps. It is the raw material of every agent metric,
and the thing that makes non-determinism debuggable.

### Step 2 — Map your fields onto the OTel GenAI standard
Look at your trace fields and state, for each, the OpenTelemetry GenAI
attribute it corresponds to (coach has the key):
- your `action` (a tool call) → `gen_ai.tool.name`
- your `args` → `gen_ai.tool.call.arguments`
- your `latency_s` → `gen_ai.client.operation.duration`
- a whole run → a span named by `gen_ai.conversation.id`

CHECK: you produced the four mappings and can say why a shared schema
matters (any backend — Langfuse, Phoenix, Cloud Trace — reads it).
Concept: telemetry is only useful if it's *standard*; the OTel GenAI
semantic conventions are the vendor-neutral schema agents are converging
on (Day 4's `agent.session` / `agent.think` / `agent.tool` spans are the
same idea).

### Step 3 — Build the metrics reducer
Write `agg.py` that reads `traces.jsonl` and prints, per run
(a run = the sequence from step 1 up to the next `finish`):
steps, total latency, whether it ended in `finish` (success) or
`max steps` (fail), and any non-`ok` actions grouped by action name.

```bash
# generate a few varied runs first
for t in "count .md files in data, finish with the number" \
         "read data/b.md and finish with its first line" \
         "delete data/a.md then finish"; do
  python3 pocket_agent.py "$t"; done
python3 agg.py traces.jsonl
```

CHECK: `agg.py` prints one row per run plus totals: success rate,
p50/p95 latency, mean steps/run, and a tool-error tally.
Concept: metrics are a *reduction* over traces — the dashboard is just
this table refreshed. (You just built the core of Lab 5's eval runner.)

Reference (for your coach, or for you after an honest attempt):
`agent-ops/labs/solution/agg.py` — a tested implementation of exactly this.

Troubleshoot: split runs on `action == "finish"` OR a `parse_error` streak
ending in max-steps; if unsure where a run ends, print raw lines first.

### Step 4 — Cost per successful task
Add one derived metric to `agg.py`: **cost per successful task** =
total steps across ALL runs ÷ number of successful runs. Compare it to
steps per run.

CHECK: the two numbers differ, and you can explain why cost-per-success is
the more honest operating number.
Concept: failed runs still burn tokens; dividing by *successes* prices the
retries and dead-ends in. This is the number that catches a **Denial of
Wallet** loop that a "steps per run" average would hide.

### Step 5 — Tail-based sampling decision
You can't store every trace at scale. State a rule for which traces to
KEEP at 100% and which to sample at (say) 1%, based on your `agg.py`
output fields.

CHECK: a rule that keeps errors / high-step / abandoned runs and samples
routine successes.
Concept: **dynamic tail-based sampling** (Day 4) — spend your storage on
the long tail where the failures live, not the boring successes. Online
evaluation "biases toward high-cost sessions and sessions the user
abandoned" for the same reason.

## Recap

### P2-R1
Q: Why is "cost per successful task" a better operating metric than "average tokens per run"?
Key:
- Average-per-run hides failed/looping runs that consumed tokens but delivered nothing
- Dividing total cost by *successes* prices retries and dead-ends in — and surfaces a runaway loop (Denial of Wallet) that a per-run average smooths over

### P2-R2
Q: What does tail-based sampling keep vs. drop, and why is that the right bias for agent observability?
Key:
- Keep 100% of error / excessive-step / abandoned traces; sample routine successes at a low rate
- Failures and their causes live in the tail; storing every success is expensive and low-information

## Theory

The Day 4 whitepaper makes observability "a strict security requirement,
not just uptime/latency" — an HTTP 200 can mask a hallucination loop, and
Denial-of-Wallet attacks are invisible to classic dashboards. Its span
taxonomy (`agent.session` / `agent.think` / `agent.tool`) is the same
structure the OpenTelemetry GenAI semantic conventions standardize as
`gen_ai.*` attributes, which is why your homegrown `traces.jsonl` maps
cleanly onto what Langfuse, Arize Phoenix, and Google Cloud Trace ingest.
The metrics you reduced to — success rate, latency percentiles, steps and
cost per task, tool error rate by tool — are exactly the agent SLIs
practitioners converge on, because per-step health can look green while the
*task* fails. Deep dives: links.md → OpenTelemetry GenAI semantic
conventions; links.md → "What is Agent Observability" (SLI formulas);
links.md → arXiv 2411.05285 (AgentOps: what to trace across the lifecycle);
Day-4 whitepaper "Observability: Auditing the Agent's Mind".
