# Lab 1 — An Agent Is a Service: SLOs for a Non-Deterministic System (~40 min)

Goal: feel the difference between "my agent script works" and "my agent
service is healthy" — measure run-to-run variance with your own hands,
then write the first two production artifacts every agent needs: an SLO
and a health check.

Prereqs: the harness-eng module (or at least its reference agent at
`harness-eng/workshop/solution/pocket_agent.py`). Work in a scratch dir:

```bash
mkdir -p agent-ops/scratch/lab1 && cd agent-ops/scratch/lab1
cp ../../../harness-eng/workshop/solution/pocket_agent.py .
mkdir data && printf '# alpha\n' > data/alpha.md && printf '# beta\n' > data/beta.md && printf '# gamma\n' > data/gamma.md && printf 'txt\n' > data/misc.txt
```

### Step 1 — The same task, five times
```bash
for i in 1 2 3 4 5; do
  /usr/bin/time -p python3 pocket_agent.py \
    "How many .md files are in the data directory? Finish with just the number." \
    2>&1 | grep -E '^(3|real|\(stopped)' ; echo ---
done
```

CHECK: you have five outcomes; report how many gave the right answer (3)
and the fastest and slowest wall-clock time. They will NOT be identical.
Concept: an agent in production is a distribution, not a function — same
input, different trajectories, different latency, sometimes different
answers. Everything in this module follows from that fact.

### Step 2 — Turn the runs into metrics
From your five runs, compute by hand and state to the coach:
- task success rate (right answers / 5)
- p50 and worst-case latency (middle and max of your five times)
- steps per task (count lines per run in `traces.jsonl` — `wc -l` it and
  divide; the file accumulated all five runs)

CHECK: three numbers stated, derivation explained in one line each.
Concept: the unit of measurement is the *task*, not the request — success
rate, latency percentiles, and steps/cost per task are the core agent
metrics (they become dashboards in Lab 2).

### Step 3 — Write your first SLO
Write (in a file `SLO.md`) one availability-style objective and one
quality objective for this agent, using your measured numbers as the
baseline, e.g. "≥80% of count-tasks return the correct number" /
"p95 task latency ≤ N s". Then answer: why is "100% correct" a WRONG
objective here?

CHECK: two objectives with thresholds justified by Step-2 data, plus the
100% answer (non-determinism makes perfection unpriceable; an SLO buys an
error budget you can spend on change).
Concept: SLOs, not unit tests, are how you hold a stochastic system to a
standard — "tests catch deterministic regressions; evaluation catches
behavioural drift" (Day 5 whitepaper).

### Step 4 — A health check that tells the truth
A production endpoint must know it is broken before its users do. Write
`healthz.sh` that exits 0 only if ALL hold, printing one line per check:
- `claude` CLI is on PATH (`command -v claude`)
- the model answers a trivial ping within 60s
  (`claude -p --model haiku "reply with exactly: pong"` contains `pong`)
- `data/` exists and is readable

```bash
bash healthz.sh; echo "exit=$?"
```

CHECK: exit=0 now; then `mv data data_x`, rerun (nonzero + a truthful
message), and `mv data_x data` back.
Concept: liveness ("process up") vs readiness ("dependencies answer") —
an agent's readiness includes its model, its tools, and its config.

### Step 5 — Kill switch
Add one more check to `healthz.sh`: if a file named `KILL` exists, exit 1
with `disabled by operator`. Create `KILL`, show the failure, remove it.

CHECK: the switch works both ways.
Concept: the fastest incident mitigation is the one you built before the
incident — every autonomous system ships with an off switch (Day 4 calls
the automated version a stateful circuit breaker).

## Recap

### P1-R1
Q: Your teammate says "the agent passed all its tests, ship it." Using this lab's vocabulary, what is missing before that claim means anything in production?
Key:
- Tests are single deterministic runs; the agent is a distribution — need measured success rate / latency percentiles over repeated tasks (an SLO with an error budget)
- Plus a health/readiness check and an off switch for when the distribution shifts in prod

### P1-R2
Q: Name the three core per-task metrics from Step 2 and why "per task" rather than "per request/step" is the right unit.
Key:
- Task success rate, latency percentiles (p50/p95), steps (≈ cost) per task
- The user's intent is a task; a run may take many steps/requests — per-step metrics can look healthy while the task fails (HTTP 200 can mask a hallucination loop)

## Theory

The Day 4 whitepaper's evaluation half is built on exactly this lab's
premise: vibe-coded agents are non-deterministic and iterative, so quality
is "scored judgments and tolerance bands," measured on dimensions like
intent satisfaction, cost and efficiency, and trajectory quality — not
binary asserts. Its security half supplies the off-switch language:
observability is a security requirement because an agent can be "up" by
every infrastructure signal while burning money in a loop (Denial of
Wallet) — which is why your health check probes the model and config, not
just the process. Google's SRE tradition gives the SLO/error-budget frame:
you cannot spend on change (new prompts, new models) without a budget of
allowed failure. Deep dives: Day-4 whitepaper "What to Evaluate" (seven
dimensions); links.md → Google SRE book (SLOs); links.md → OpenAI
"A practical guide to building agents".
