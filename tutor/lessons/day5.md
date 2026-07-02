# Day 5 — Spec-Driven Production Grade Development

Whitepaper: `day5-spec-driven-production/whitepaper-spec-driven-production-grade-development.md`
Figures: `day5-spec-driven-production/assets/whitepaper-spec-driven-production-grade-development/`

## Concept cards

### D5-C1: Spec-Driven Development — code as disposable
Summary: SDD inverts the traditional hierarchy: the specification, not the
code, is the source of truth. Because AI can regenerate implementation
cheaply, code becomes disposable while behavior specs are durable assets.
Since implementation is no longer the bottleneck, effort shifts to writing
precise, testable descriptions of intended behavior that agents build
against and are verified against.
Source: "Spec-Driven Development (SDD)"
Elaborate: If code is disposable, what changes about how you'd review a pull request?

### D5-C2: Good specifications and BDD/Gherkin
Summary: A good spec is unambiguous, testable, and behavior-focused —
what the system does, not how. Behavior-Driven Development formats like
Gherkin (Given / When / Then scenarios) work well because they're readable
by humans, executable as tests, and precise enough to constrain an agent.
The spec doubles as the acceptance test suite.
Source: "A good specification — Which format to use? — Behavior Driven"
Elaborate: Write a one-line Given/When/Then for this tutor's grading behavior.

### D5-C3: Where instructions live
Summary: Agent instructions are layered by scope: project-level standing
instructions (conventions, architecture — e.g. AGENTS.md-style files),
feature-level specs, and task-level prompts. Different use cases get
different prompts — a spike, a refactor, and a production feature should
not share the same instruction set. Keeping instructions in versioned files
makes agent behavior reproducible and reviewable.
Source: "Where do the instructions live? — Different Prompts for Different Use Cases"
Elaborate: What's in your global CLAUDE.md, and does it match this layering?

### D5-C4: MCP for production — one integration, every framework
Summary: Production teams wrap internal systems as MCP servers once, and
every agent framework in the company can use them. Day 5 covers the
producer side (building an MCP server: tools, schemas, transport) versus
Day 2's consumer side — making MCP the integration seam between vibe-coded
agents and enterprise systems.
Source: "MCP: One Integration, Every Framework"
Elaborate: Which internal system at your work would you wrap as an MCP server first, and why?

### D5-C5: Zero-trust development — the safety net
Summary: Assume any generated code may be wrong or unsafe until proven
otherwise. The net has six strands: guardrails (hard limits on agent
actions), sandboxing (isolated execution), human-in-the-loop (approval for
consequential steps), AI-generated test coverage (agents write and run
tests against the spec), continuous evaluation, and a policy server — a
hybrid decision point that programmatically allows, denies, or escalates
agent actions against org policy.
Source: "Zero-Trust Development: Building the Safety Net"
Elaborate: Which strand does your current workflow lack most?

### D5-C6: Team culture — reviews and sustainability
Summary: When agents produce most code, review culture shifts: automated
code-review agents handle the volume first (style, bugs, spec conformance),
humans review what machines can't judge — intent, architecture, risk.
Sustainability means keeping the system healthy long-term: specs
maintained, evals trusted, and humans still able to understand the system
they operate.
Figure: assets/whitepaper-spec-driven-production-grade-development/figure-1.png
Source: "Team Culture & Process Evolution"
Elaborate: What skill should a junior engineer build first in this world?

## Question cards

### D5-Q1 (tests D5-C1)
Q: In SDD, what is the source of truth, and what economic change makes that inversion sensible?
Hint: What got cheap?
Key:
- The specification is the source of truth; code is treated as disposable/regenerable
- AI made implementation cheap, so durable value moves to precise behavior descriptions

### D5-Q2 (tests D5-C2)
Q: What three properties make a spec "good", and why does Gherkin suit agent-driven development?
Hint: Ambiguity, verification, focus; then who/what can read Gherkin.
Key:
- Unambiguous, testable, behavior-focused (what, not how)
- Gherkin (Given/When/Then) is human-readable, machine-executable as tests, and precise enough to constrain an agent
Stretch: Turn this requirement into two Gherkin scenarios: "users can export their data, but exports are rate-limited to one per hour."
StretchKey:
- A happy-path scenario (Given a user with no recent export, When they request one, Then it succeeds)
- A limit scenario (Given a user who exported <1h ago, When they request again, Then it's rejected with an explanatory error)

### D5-Q3 (tests D5-C3)
Q: Describe the three layers of where agent instructions live and why versioning them matters.
Hint: Project / feature / task.
Key:
- Project-level standing conventions (e.g. AGENTS.md), feature-level specs, task-level prompts
- Versioned instruction files make agent behavior reproducible and reviewable like code

### D5-Q4 (tests D5-C4)
Q: How do Day 2 and Day 5 differ in their treatment of MCP?
Hint: Consumer vs producer.
Key:
- Day 2: consuming existing MCP servers (discovery, configuration, connection)
- Day 5: building your own MCP server so one integration serves every agent framework in the org

### D5-Q5 (tests D5-C5)
Q: Name at least four strands of the zero-trust development safety net.
Hint: Limits, isolation, humans, tests, evals, policy.
Key:
- Any four of: guardrails, sandboxing, human-in-the-loop, AI-generated test coverage, continuous evaluation, policy server

### D5-Q6 (tests D5-C5)
Q: What does a policy server do in an agentic pipeline?
Hint: It sits between agent intent and execution.
Key:
- A decision point that checks agent actions against organizational policy and programmatically allows, denies, or escalates them
Stretch: An agent wants to run a database migration in production at 2am. Trace the request through the full zero-trust net.
StretchKey:
- Guardrails/policy server evaluate the action class (prod + destructive → escalate, not allow)
- Human-in-the-loop approval required; execution in a controlled window; sandbox/staging validation and tests/evals referenced before approval; everything traced

### D5-Q7 (tests D5-C6)
Q: In an AI-heavy team, what do automated review agents check, and what remains for human reviewers?
Hint: Volume vs judgment.
Key:
- Agents: style, bugs, spec conformance at volume
- Humans: intent, architecture, and risk — what machines can't judge

### D5-INT (Integrate — capstone-ready)
Q: Lay out the full production path for your capstone agent using Day-5 concepts: from spec to deployed, governed system. Name at least five elements.
Key:
- Gherkin/behavior spec as source of truth; layered instructions (project conventions + feature spec)
- Agent implements against the spec; AI-generated tests verify it
- Zero-trust execution: sandbox, guardrails, policy server, human approval for high-stakes steps
- Deployment with observability/evals; automated review agents + human architecture review

## Go deeper (external, free)

- GitHub Spec Kit (hands-on SDD toolkit) — https://github.com/github/spec-kit — quickstart: https://github.github.com/spec-kit/quickstart.html
- The Spec Kit methodology essay — https://github.com/github/spec-kit/blob/main/spec-driven.md
- Microsoft Learn: Spec-Driven Development with Spec Kit — https://learn.microsoft.com/en-us/training/modules/spec-driven-development-github-spec-kit-greenfield-intro/
- MCP server-building guide (producer side) — https://modelcontextprotocol.io/docs/getting-started/intro
