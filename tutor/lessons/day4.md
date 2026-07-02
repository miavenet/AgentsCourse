# Day 4 — Vibe Coding Agent Security and Evaluation

Whitepaper: `day4-agent-security-and-evaluation/whitepaper-vibe-coding-agent-security-and-evaluation.md`
Figures: `day4-agent-security-and-evaluation/assets/whitepaper-vibe-coding-agent-security-and-evaluation/`

## Concept cards

### D4-C1: Effective Trust in non-deterministic systems
Summary: Traditional security assumes deterministic code you can audit
once. Agentic workflows are non-deterministic — the same prompt can produce
different code paths — so trust must be established continuously, not at a
single review gate. The paper's frame is "Effective Trust": layered,
verifiable safeguards around the agent (its 7-pillar security architecture)
rather than faith in any single check.
Figure: assets/whitepaper-vibe-coding-agent-security-and-evaluation/figure-1.png
Source: "Security: The Evolution to Secure Agentic Development — The 7-Pillar Agent Security Architecture"
Elaborate: Why can't a one-time code review establish trust in an agent the way it can for a library?

### D4-C2: Ephemeral sandboxing and supply-chain defense
Summary: Agents should execute in ephemeral sandboxes — isolated,
short-lived environments torn down after the task, so a compromised or
misbehaving run can't persist state or reach production. The supply chain
needs defense against "slopsquatting": attackers register package names
that LLMs plausibly hallucinate, so an agent that installs a hallucinated
dependency imports attacker code. Countermeasures: lockfiles/allowlists,
registry verification, and never auto-installing unverified packages.
Source: "Sandboxes and Supply Chain Defence (Pillars 1 & 4)"
Elaborate: How does slopsquatting differ from classic typosquatting?

### D4-C3: Identity, trust, and high-stakes actions
Summary: Agents need their own identity and least-privilege credentials —
not the developer's full permissions. High-stakes actions (payments,
deletions, production deploys) get human-in-the-loop approval gates: the
agent pauses, a human reviews with enough context to judge, then execution
resumes. Autonomy is scoped by blast radius.
Source: "Identity, Trust & High-Stakes Actions (Pillar 5)"
Elaborate: Which actions in your own projects would you put behind an approval gate?

### D4-C4: Red, Blue, and Green teaming
Summary: An active security triad for agentic systems: Red team attacks
(prompt injection, jailbreaks, tool abuse), Blue team defends and monitors,
and Green — the addition for the AI era — builds security in from the
start, designing safe defaults and guardrails into the agent development
process itself rather than bolting them on.
Source: "Red, Blue, and Green Security Teaming (Pillar 6)"
Elaborate: Why does agentic AI need a standing "builder" security function rather than periodic pen tests alone?

### D4-C5: Observability — auditing the agent's mind
Summary: You can't secure or evaluate what you can't see. Trajectory-level
observability records the agent's full decision path — prompts, plans, tool
calls, outputs — typically via OpenTelemetry-style tracing. This enables
auditing why an agent acted, evaluating trajectories against expectations,
and detecting drift or attacks in production. Observability is the
prerequisite for evaluation.
Source: "Observability: Auditing the Agent's Mind (Pillars 6 & 7)"
Elaborate: What's the minimum you'd need to log to answer "why did the agent delete that file?"

### D4-C6: Evaluating vibe coding agents
Summary: Evaluation differs from classic software testing: outputs are
non-deterministic, quality is multi-dimensional, and the unit under test is
a trajectory, not a function. The framework: decide *what* to evaluate
(final output quality, tool-call trajectory, safety, cost/latency), then
*how* — exact checks where possible, LLM-as-judge for open-ended quality,
human review for high stakes — and run evals continuously, not once.
Figure: assets/whitepaper-vibe-coding-agent-security-and-evaluation/figure-3.png
Source: "Evaluation: Orchestrating Quality in Intent-Driven Agentic Systems"
Elaborate: Why is "the tests pass" insufficient evidence that an agent-built feature is good?

## Question cards

### D4-Q1 (tests D4-C1)
Q: Why does agentic development break the traditional audit-once security model, and what replaces it?
Hint: Determinism, then continuity.
Key:
- Agent behavior is non-deterministic — the same input can produce different actions, so a single review can't certify future behavior
- Continuous, layered safeguards ("Effective Trust", the 7-pillar architecture) replace one-time gates

### D4-Q2 (tests D4-C2)
Q: What is slopsquatting and what makes agents especially vulnerable to it?
Hint: Hallucinated names, registered by whom?
Key:
- Attackers pre-register package names LLMs plausibly hallucinate
- Agents that auto-install suggested dependencies import the attacker's code without a human checking the name
Stretch: Design a three-layer defense for an agent that manages Python dependencies.
StretchKey:
- Any three of: allowlist/lockfile of approved packages; verify against the real registry (existence, age, downloads, maintainer); sandbox installs before promotion; human approval for new dependencies

### D4-Q3 (tests D4-C2)
Q: What properties make a sandbox "ephemeral," and what attack class does that neutralize?
Hint: Lifetime and isolation.
Key:
- Isolated from production and torn down after each task (no persistent state)
- Neutralizes persistence: a compromised run can't retain footholds or leak into later runs/production

### D4-Q4 (tests D4-C3)
Q: How should an agent's identity and permissions be set up, and how are high-stakes actions handled?
Hint: Whose credentials? And when does a human enter?
Key:
- Its own identity with least-privilege credentials, not the developer's
- High-stakes actions pause for human-in-the-loop approval before execution resumes

### D4-Q5 (tests D4-C4)
Q: Name the three security teams in the triad and each one's role.
Hint: Attack, defend, build.
Key:
- Red: attacks the system (prompt injection, tool abuse)
- Blue: defends and monitors
- Green: builds security in from the start (safe defaults, guardrails in the dev process)

### D4-Q6 (tests D4-C5)
Q: What does trajectory-level observability capture, and why is it called the prerequisite for evaluation?
Hint: More than logs of outputs.
Key:
- The agent's full decision path: prompts, plans, tool calls, and outputs (OpenTelemetry-style traces)
- You can only evaluate or audit agent behavior you recorded — without traces there is nothing to judge trajectories against

### D4-Q7 (tests D4-C6)
Q: List three distinct dimensions to evaluate in a vibe-coding agent, and match each with an evaluation method.
Hint: What it made, how it got there, what it cost.
Key:
- Any three dimensions: final output quality, tool-call trajectory, safety/security, cost/latency
- Sensible method pairing, e.g. exact/automated checks for deterministic properties, LLM-as-judge for open-ended quality, human review for high stakes
Stretch: Your agent's eval suite is all LLM-as-judge. Give two failure modes of that setup and the fix.
StretchKey:
- Failure modes (any two): judge shares the generator's blind spots; judges drift/are inconsistent; expensive at scale; gameable phrasing
- Fix: mix methods — exact checks where possible, calibrate judges against human labels, human review for high stakes

### D4-INT (Integrate)
Q: For the capstone farming agent, propose a minimal security-and-evaluation plan using at least four Day-4 concepts.
Key:
- Sandbox the agent's execution; least-privilege identity for any external calls
- Guard dependencies (slopsquatting awareness) if it installs anything
- Trace its decisions (observability) and evaluate trajectories, not just final score
- Human-in-the-loop or hard limits on any high-stakes/irreversible action

## Go deeper (external, free)

- OWASP Top 10 for LLM Applications — https://genai.owasp.org/llm-top-10/
- OWASP Top 10 for Agentic Applications (2026) — https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/
- Google's Secure AI Framework (SAIF) — https://saif.google/
