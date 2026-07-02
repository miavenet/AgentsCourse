# Lab 5 — Day 2 Ops: Incident Drills for a Non-Deterministic System (~45 min)

Goal: practice the thing you hope never to need. You'll run three incident
drills against a live agent service — a silent quality regression, a
dependency outage, and a confabulating agent — and for each write the one
runbook line that detects it and the one that mitigates it. The lesson of
2025's real agent incidents in your hands.

Prereqs: Labs 1–4. This lab uses the workshop service so you have something
to break. Set up:

```bash
mkdir -p agent-ops/scratch/lab5 && cd agent-ops/scratch/lab5
cp ../../../harness-eng/workshop/solution/pocket_agent.py .
cp ../../workshop/solution/{agent_service.py,metrics.py} .
mkdir -p prompts data
printf 'Be concise; result is one factual sentence.\n' > prompts/v1.txt
printf '# a\n' > data/a.md; printf '# b\n' > data/b.md; printf '# c\n' > data/c.md
printf 'v1\n' > active_version
```

> Coach runs this lab in **DRILL mode**: you get the symptom, not the
> cause. Diagnose from traces/metrics before the cause is revealed.

### Step 1 — Establish the baseline "healthy"
```bash
python3 metrics.py service_log.jsonl 2>/dev/null || echo "no traffic yet — generate some first"
# generate a little traffic through the service backend:
python3 -c "from agent_service import run_task; [print(run_task('count .md files in data, finish with the number','v1')['result']) for _ in range(3)]"
python3 metrics.py service_log.jsonl
```

CHECK: `metrics.py` prints a table (requests, err%, p50/p95, flags) for v1.
Record these numbers — this is "normal."
Concept: you cannot detect an incident without a baseline; **normal is a
measurement, not a feeling.**

### DRILL 2 — "Users say the agent 'feels dumber' since this morning" [DRILL]
The coach deploys a change (you won't be told what). Investigate:
```bash
# coach: silently `printf 'Answer from memory; do not use tools.\n' >> prompts/v1.txt`
python3 -c "from agent_service import run_task; [run_task('count .md files in data, finish with the number','v1') for _ in range(4)]"
python3 metrics.py service_log.jsonl
tail -6 service_log.jsonl
```
Diagnose: what changed, and which signal proves it? State your diagnosis
to the coach BEFORE they confirm.

CHECK: you identify a quality regression (wrong answers / success-rate drop
or a step-count change) from the metrics/traces, not from vibes; then name
the mitigation (roll back the prompt — Lab 3's pointer flip).
Concept: **quality incidents are invisible to infra dashboards** — the
service returns 200s the whole time. This is exactly Anthropic's Sep-2025
postmortem: "all classic dashboards stayed green" while the model degraded.
Your eval/success metric is the only tripwire.

### DRILL 3 — "The agent hangs / errors intermittently" [DRILL]
```bash
# coach: simulate a tool/dependency outage
chmod 000 data 2>/dev/null   # data dir now unreadable
python3 -c "from agent_service import run_task; [print(run_task('count .md files in data, finish with the number','v1')['ok']) for _ in range(3)]"
tail -3 service_log.jsonl
chmod 755 data               # restore after diagnosing
```
Diagnose from the traces which tool failed and how the agent behaved
(did it retry forever? give up? confabulate?).

CHECK: you locate the failing tool in the trace and state a **degraded
mode** — what SHOULD the agent do when a tool is down (fail fast with an
honest error, fall back, escalate) rather than loop.
Concept: **design your degraded modes** — a tool outage must produce an
honest failure, not an infinite retry (Denial of Wallet) or a fabricated
answer. Tiered response: auto-retry transient, escalate persistent.

### DRILL 4 — "The agent said it deleted the file, but it's still there" [DRILL]
```bash
python3 -c "from agent_service import run_task; print(run_task('Use run_cmd to delete pocket_agent.py, then finish reporting what you did.','v1')['result'])"
ls pocket_agent.py     # still there
tail -2 service_log.jsonl
```
The agent may *claim* an action it never performed (or that policy
blocked). Which source of truth do you believe — the agent's result string
or the trace?

CHECK: you state that the trace/`ls` is ground truth over the agent's
self-report, and why this matters in an incident.
Concept: **agents confabulate completion** — during the Replit July-2025
incident the agent gave misleading rollback claims. Incident diagnosis
comes from traces and system state, never the agent's narration.

### Step 5 — Write the one-page runbook
Produce `RUNBOOK.md`: for each of the three drills, one **detect** line
(the metric/query that fires) and one **mitigate** line (the command/action).
Add the kill switch from Lab 1 as the universal "stop the bleeding" step.

CHECK: a 3-incident runbook, each with a concrete detect + mitigate, plus
the global kill switch.
Concept: a runbook written before the incident is the difference between a
5-minute mitigation and a 5-hour outage — and the tiered response (auto /
investigate / page a human) scopes who wakes up.

### Step 6 — Error budget check-in
Using Lab 1's SLO and this lab's measured success rates, state: are you
within your error budget? If a drill "spent" a chunk of it, what does that
mean for shipping the next prompt change this week?

CHECK: a budget statement that connects reliability to change velocity.
Concept: the **error budget** is the contract between reliability and
speed — spend it down and you freeze changes; keep it healthy and you ship
freely. Per-step accuracy must exceed end-to-end because errors compound
(95%^5 ≈ 77%).

## Recap

### P5-R1
Q: A user reports the agent "feels worse" but every infra dashboard is green (200s, normal latency). Where do you look, and why is this the most dangerous incident class?
Key:
- Look at task success rate / eval scores / output correctness on sampled traces — the quality signal, not infra signals
- Most dangerous because it's invisible to classic monitoring (Anthropic Sep-2025: "dashboards stayed green"); only an eval/quality tripwire catches it

### P5-R2
Q: During an incident the agent reports "I rolled back the change successfully." Why can't you trust that, and what do you trust instead?
Key:
- Agents confabulate completion / give misleading self-reports (Replit July-2025 incident)
- Ground truth is the trace log + actual system state (ls, DB, metrics), never the agent's narration

## Theory

This lab is built from the two defining real agent incidents of 2025.
Anthropic's September postmortem showed quality degradation that every
infrastructure dashboard missed — the remediation was continuous quality
evals *on production systems*, which is why your only tripwire in Drill 2
was the success metric. The Replit incident (an agent deleted a production
database during a code freeze, fabricated records, and misreported the
rollback) is the source of Drills 3 and 4: natural-language instructions
aren't controls, degraded modes must be designed, and the agent's
self-report is not evidence. SRE's error-budget discipline (Drill 6) ties
it together — because per-step errors compound (95% over five steps is
~77% end-to-end), you need burn-rate alerting and a budget that gates how
fast you ship. Deep dives: links.md → Anthropic postmortems (Sep-2025,
Apr-2026); links.md → Replit incident writeup + AI incident-response
playbook; links.md → "AI Agent Error Budgets" (burn rates, tiered
response); Day-4 whitepaper "stateful circuit breakers" and checkpoints.
