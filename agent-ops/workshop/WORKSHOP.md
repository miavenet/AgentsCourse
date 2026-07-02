# Workshop — Ship Pocket-Agent: Agent-as-a-Service, End to End (~2–3 h)

In harness-eng you built Pocket-Agent — a working agent in ~130 lines. It
runs on your laptop from the command line. That is a *prototype*, not a
*service*. This workshop wraps it in the production skin: an HTTP endpoint
with a health check and kill switch, versioned prompts, guardrails on
every request, an eval gate that stands in front of deploys, a canary that
rolls back on regression, a metrics view, and an incident drill that
exercises the whole thing.

Thesis made concrete: the model and the agent don't change at all. Every
line you add here is *operations* — the difference between "it works on my
machine" and "it's running in production and I'd know within minutes if it
weren't."

The whole service is one request flowing through six layers you'll build
in order. Keep this picture in view — every milestone adds one box:

```
              ┌─────────────────────── agent_service.py ───────────────────────┐
  POST /task  │  guard_input ─▶ load prompt(active_version) ─▶ pocket_agent.run │
  ──────────▶ │       │              (M1 boundary, M5 versioning)      │        │
              │   (M3 flag)                                        (loop+gate,  │
              │       │                                          from harness)  │
              │       ▼                                                │        │
   JSON  ◀─── │  guard_output ◀──────────── result ◀───────────────────┘        │
  response    │   (M3 redact)         │                                         │
              │                       ▼                                         │
              │              service_log.jsonl ──▶ metrics.py ──▶ SLO exit code │
              │                 (M4 observe)          (M4)      (M4 alert/gate)  │
              └────────────────────────────────────────────────────────────────┘
   guarded by:  /healthz + KILL (M2)      shipped through:  gate.py + canary.py (M5)
```

Work in `agent-ops/scratch/workshop/`. Copy your Pocket-Agent in first:

```bash
mkdir -p agent-ops/scratch/workshop/{prompts,data}
cd agent-ops/scratch/workshop
cp ../../../harness-eng/workshop/solution/pocket_agent.py .
printf 'Be concise; result is one short factual sentence.\n' > prompts/v1.txt
printf 'v1\n' > active_version
for f in a b c; do printf "# $f\n" > data/$f.md; done
printf 'harness\n' > data/topic.txt
```

Reference implementations live in `agent-ops/workshop/solution/`
(`agent_service.py`, `metrics.py`, `gate.py`, `canary.py`) — the coach's
answer key. Opening them before M6 is spoiling your own workshop.

### M1 — Wrap it in a service
Create `agent_service.py`. Import your `pocket_agent` (add its dir to
`sys.path`). Write `run_task(task, version)` that: loads
`prompts/<version>.txt`, appends it to `pocket_agent.SYSTEM`, calls
`pocket_agent.run(...)`, and returns a dict `{request_id, version, ok,
latency_s, result}`. Stand up an `http.server` with `POST /task`
(JSON body `{"task": "..."}`).

CHECK: `curl -s -X POST localhost:8055/task -d '{"task":"say hello, finish with a greeting"}'`
returns a JSON object with a `result`.
Concept: a service is a *contract at a boundary* — request in, structured
response out, the agent hidden behind it. Everything else this workshop
adds hangs off this seam.

### M2 — Health, readiness, and a kill switch
Add `GET /healthz` that returns 200 only if: the `claude` CLI is on PATH,
the active prompt file loads, and no `KILL` file exists (else 503 with the
reason). Make `POST /task` refuse with 503 when `KILL` exists.

CHECK: `/healthz` is 200 now; `touch KILL` → `/healthz` 503 and `/task`
503; `rm KILL` → back to 200.
Concept: **readiness ≠ liveness** — an agent is only "ready" if its model,
tools, and config all answer. The kill switch is the mitigation you build
*before* the incident (Lab 1).

### M3 — Guardrails on every request
Add `guard_input(task)` (flag injection patterns — Lab 4) and
`guard_output(result)` (redact `sk-`/`AKIA`/`ghp_` secret shapes). Run both
inside `run_task`; record any flags in the returned dict and the log.

CHECK: a task containing "ignore all previous instructions" comes back with
`flags` including an input flag; a task whose answer would contain a
fake `sk-live-...` string comes back `[REDACTED]`.
Concept: guardrails are **per-request middleware**, not a one-time setup —
the boundary inspects everything crossing it, in and out (Day 4's LLM
firewall in ~15 lines).

### M4 — Structured service log + metrics
Append every request to `service_log.jsonl`
(`request_id, ts, version, ok, latency_s, flags, task, result`). Write
`metrics.py` that reduces the log per version to: requests, error rate,
p50/p95 latency, guardrail-flag count — and **exits 1 if any version's
error rate breaches an SLO** you pass in.

CHECK: after a handful of requests, `python3 metrics.py` prints the table;
force a couple of failures and confirm the SLO breach flips the exit code.
Concept: metrics are a **reduction over the log**, and the exit code is
what an alert or a CI step hangs off — observability becomes *action* only
when a number can fail a build.

### M5 — The eval gate and canary
(a) Write `gate.py` with a golden task set (capability + safety cases,
Lab 3). It scores a candidate version and writes `active_version` **only**
if score ≥ recorded baseline. (b) Write `canary.py` that routes a slice of
probe traffic to a candidate, compares error rates, and rolls back on
regression.

```bash
python3 gate.py v1 --baseline
printf 'Always write any number as an English word, never a digit.\n' > prompts/v2.txt
python3 gate.py v2          # should FAIL and NOT deploy (a real regression)
```

CHECK: baseline recorded; the v2 regression is caught (gate exits nonzero,
`active_version` unchanged). Then make a genuinely-good v3 and watch
`canary.py` PROMOTE it.
Concept: two judgment points — **offline gate before deploy, online canary
during deploy** — make a config change *falsifiable* instead of hopeful.
This is the CI/CD spine of AgentOps.

### M6 — Incident drill: prove the whole thing holds [DRILL]
Have your coach silently break one thing (append "answer from memory, no
tools" to the live prompt, OR `chmod 000 data`, OR ask for an action the
agent will confabulate). Using ONLY `/healthz`, `metrics.py`, and
`service_log.jsonl`, diagnose it, mitigate it (roll back / kill switch /
restore), and confirm recovery.

CHECK: you detected the break from signals (not vibes), mitigated with one
command, and `metrics.py` shows recovery. State which drill it was and the
detect+mitigate lines.
Concept: the full **Day-2 loop** — observe → detect → mitigate → verify —
running against your own service. If you can do this, you can operate an
agent, not just build one.

### Stretch — Rainbow deploy for in-flight tasks
Your canary flips `active_version` instantly. Real stateful agents may be
mid-task during a deploy. Sketch (or implement) a **rainbow deployment**:
keep vN and vN+1 both serving, route NEW tasks to vN+1, let in-flight vN
tasks drain, retire vN only when its in-flight count hits zero.

CHECK: you can explain what breaks if you hard-swap a version under an
in-flight multi-step task, and how draining fixes it.
Concept: you rediscovered why Anthropic uses rainbow deployments for
long-running agents — statefulness is the constraint that makes agent
deploys different from stateless web deploys.

## Recap

### W-R1
Q: The model and the agent code are byte-for-byte identical to the harness-eng workshop. Name the six operational layers you added here and what each one is for.
Key:
- Service boundary (HTTP contract) — request in / structured response out
- Health + kill switch — readiness detection and instant mitigation
- Guardrails (in/out) — per-request injection flagging + secret redaction
- Service log + metrics — observability reduced to alertable numbers
- Eval gate + canary — offline & online judgment gating every deploy
- Incident runbook/drill — detect → mitigate → verify loop

### W-R2
Q: A teammate wants to hot-swap the production prompt by editing the running service. Give two reasons your `active_version` + gate + canary design is safer.
Key:
- Config is a versioned artifact — auditable, diffable, rollback = flip one pointer to a known-good version
- The change must pass an offline eval gate and survive a canary before owning traffic — regressions (incl. injection-style overrides) are caught mechanically, not by eyeballing

## Theory

Everything you built maps onto the course's own production frameworks. The
service boundary + guardrails are Day 4's LLM firewall and Day 5's Policy
Server pattern (structural + semantic gating in front of every tool call);
the health check and kill switch are the stateful-circuit-breaker idea in
miniature; the service log is the Vibe Trajectory; metrics + SLO + error
budget are the observability pillar turned into alertable numbers; the eval
gate and canary are Day 5's `agents-cli eval run` gate and the
managed-runtime rollout you'd get from Vertex AI Agent Engine. Production
frameworks (ADK on Agent Engine, LangGraph, Temporal) differ from your
scratch service in robustness and scale — durable execution, autoscaling,
distributed state — not in *kind*: they have exactly these layers. Map each
file you wrote to its industrial counterpart and you hold the whole
discipline of running agents in one directory. Deep dives: links.md → ADK
"Deploying your agent" + Agent Starter Pack; links.md → Anthropic
"multi-agent research system" (rainbow deploys); links.md → 12-Factor
Agents (stateless-reducer, own-your-control-flow); Day-5 whitepaper
"Zero-Trust Development" and three-tier Code Review Runtime.
