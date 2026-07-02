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
cp ../../workshop/solution/{agent_service.py,metrics.py,drill.sh} .
mkdir -p prompts data
printf 'Be concise; result is one factual sentence.\n' > prompts/v1.txt
printf 'harness\n' > data/topic.txt
printf 'v1\n' > active_version
```

> This lab runs in **DRILL mode**. Your coach arms one incident with
> `bash drill.sh <id>` and tells you only the SYMPTOM — you do NOT read
> `drill.sh`. Diagnose from `/healthz`, `metrics.py`, and
> `service_log.jsonl`, state your diagnosis, THEN the coach reveals the
> cause. (Solo: run the drill without re-reading it; the skill trained is
> the diagnosis path, not the whodunit.) Every probe below hits the LIVE
> version via `active_version()` — real traffic goes to whatever is
> deployed, so a drill that flips the pointer takes effect.

### Step 1 — Establish the baseline "healthy"
```bash
# arithmetic is a reliable probe (Haiku is flaky at counting files but
# solid at 3+4); a healthy agent answers "7" every time.
python3 -c "from agent_service import run_task, active_version as v; [print(run_task('What is 3 plus 4? Finish with just the number.', v())['result']) for _ in range(3)]"
python3 metrics.py service_log.jsonl
```

CHECK: all three runs return `7`; `metrics.py` prints a table (requests,
err%, p50/p95, flags) with ~0% errors. Record these numbers — this is
"normal."
Concept: you cannot detect an incident without a baseline; **normal is a
measurement, not a feeling.**

### DRILL 2 — coach: `bash drill.sh 1` [DRILL]
Coach states the symptom only. Investigate the live service:
```bash
python3 -c "from agent_service import run_task, active_version as v; [run_task('What is 3 plus 4? Finish with just the number.', v()) for _ in range(4)]"
python3 metrics.py service_log.jsonl
tail -6 service_log.jsonl
```
Diagnose: what changed, and which signal proves it? State your diagnosis
BEFORE the coach confirms.

CHECK: here is the trap — `metrics.py` still shows **~0% errors** (the
service returns 200s and finishes every task), yet the answers now read
`seven` instead of `7`. You catch it only by comparing OUTPUTS to the
baseline (an online eval), not by reading the infra table; then you
localize it (`cat active_version` shows `v2`; diff the prompt) and mitigate
with `bash drill.sh restore` (roll the pointer back to v1 — Lab 3).
Concept: **quality incidents are invisible to infra dashboards** — this is
exactly Anthropic's Sep-2025 postmortem, "all classic dashboards stayed
green" while quality degraded. Only an eval/quality tripwire (not err% or
latency) catches a formatting/quality regression. This is why Lab 3's gate
exists.

### DRILL 3 — coach: `bash drill.sh 2` [DRILL]
```bash
python3 -c "from agent_service import run_task, active_version as v; [print(run_task('Read data/topic.txt and finish with the single word it contains.', v())['ok']) for _ in range(3)]"
tail -3 service_log.jsonl
```
Look at BOTH levels: the request-level `ok` in `service_log.jsonl` and the
step-level tool result in `traces.jsonl`. Mitigate with `bash drill.sh restore`.

CHECK: the signal lives at the STEP level, not the request level — the
`read_file` step shows a tool error in `traces.jsonl`, but the request may
still come back `ok=true` because the agent finishes by honestly reporting
"cannot read data/topic.txt: no read permission." Recognize that this
graceful degradation is the GOOD behavior; state what a BAD degraded mode
would look like (infinite retry burning tokens, or fabricating a word).
Concept: **request-level metrics can hide tool-level failures** — a healthy
err% doesn't mean healthy tools. And a good degraded mode is an honest,
finishing failure, not an infinite retry (Denial of Wallet) or a fabricated
answer. Tiered response: auto-retry transient, escalate persistent.

### DRILL 4 — coach: `bash drill.sh 3` [DRILL]
Create a decoy so no real artifact is at risk, then issue a destructive task:
```bash
printf 'delete me\n' > decoy.txt
python3 -c "from agent_service import run_task, active_version as v; print(run_task('Use run_cmd to delete decoy.txt, then finish reporting what you did.', v())['result'])"
ls decoy.txt           # still there — the policy gate held
tail -2 service_log.jsonl
```
The agent's result string is a *claim* about what happened — here it will
usually honestly report the block ("cannot delete… run_cmd only allows…"),
but it might instead claim success it never achieved. Either way: which
source of truth do you believe — the agent's narration, or `ls` + the trace?

CHECK: you verify against ground truth (`ls decoy.txt` shows the file
survived; the trace shows the `run_cmd` was blocked) REGARDLESS of what the
result string says, and explain why an incident responder never takes the
agent's word.
Concept: **the agent's self-report is not evidence** — it may be honest, or
it may confabulate completion (the Replit July-2025 incident gave misleading
rollback claims). Incident diagnosis comes from traces and system state,
never the agent's narration.

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
