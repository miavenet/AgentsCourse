# Agents in Production — Hands-On Module

A practice-first course on the discipline of *running* agents, not just
building them: **deploy, observe, gate, safeguard, and operate** a
non-deterministic system in production. Five labs where you break and build
real ops layers with your own hands, capped by a workshop that wraps your
harness-eng Pocket-Agent into a full agent-as-a-service — health checks,
guardrails, eval-gated deploys, canary rollback, metrics, and an incident
drill. Theory never comes first; it's one layer down, on demand.

Driveable by any Claude model, including Haiku: the coach protocol
(`COACH.md`) pre-scripts every step, check, and grading rule.

Built for max learning per hour: short resumable sessions, retrieval-graded
recaps, spaced re-asks of your misses, and nothing padded.

## Launch

```bash
cd ~/courses/GoogKaggleAiAgent
claude --model haiku
> /agentops            # resumes wherever you left off
```

Prereq: the `harness-eng` module (its Pocket-Agent is the thing you put
into production here). If you skipped it, run `/harness` first — or at least
confirm `harness-eng/workshop/solution/pocket_agent.py` exists.

## The path (~4–5 hours total, spread over days)

| Stage | You build / break | Production layer |
|-------|-------------------|------------------|
| Lab 1 (~40 min) | Measure run-to-run variance; write an SLO + health check + kill switch | reliability baseline |
| Lab 2 (~45 min) | A metrics reducer over your traces; map to OTel GenAI | observability |
| Lab 3 (~50 min) | Versioned prompts; an eval gate; a canary with rollback | CI/CD & rollout |
| Lab 4 (~55 min) | Red-team via indirect injection; build layered guardrails | safeguards & security |
| Lab 5 (~45 min) | Three incident drills; a one-page runbook | day-2 ops & IR |
| Workshop (~2–3 h) | **Agent-as-a-Service**: HTTP + health + guards + gate + canary + drill | all of them, shipped |

Labs are sequential — each artifact or lesson feeds a later one, and the
workshop assembles all of them. Each lab ends with retrieval-graded recap
questions and a `## Theory` section for the strong-theory layer.

## Theory on demand

- `resources/FURTHER-READING.md` — the curated best-of-best shelf
  (Anthropic, Google ADK, Willison, Hamel, OWASP, OTel) — read this if you
  read nothing else.
- `resources/links.md` — per-lab pointer map the coach draws from.
- `resources/papers/` — five open-access PDFs: *Measuring Agents in
  Production* (2512.04123), *AgentOps* (2411.05285), *CaMeL* (2503.18813),
  *Design Patterns for Securing LLM Agents* (2506.08837), *AgentDojo* (2406.13352).
- Origin texts: the Day-4 whitepaper (security & evaluation) and Day-5
  whitepaper (spec-driven production) in the sibling `dayN-*/` folders.

## Working space

Labs write into `agent-ops/scratch/` (gitignored). Progress lives in
`agent-ops/progress.md` — commit it to track the journey. The workshop
reference solution is in `workshop/solution/` (`agent_service.py`,
`metrics.py`, `gate.py`, `canary.py`) — it's the coach's answer key;
opening it before workshop M6 is spoiling yourself.
