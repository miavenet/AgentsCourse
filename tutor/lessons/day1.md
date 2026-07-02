# Day 1 — Introduction to Agents & Vibe Coding

Whitepaper: `day1-intro-agents-and-vibe-coding/whitepaper-the-new-sdlc-with-vibe-coding.md`
Figures: `day1-intro-agents-and-vibe-coding/assets/whitepaper-the-new-sdlc-with-vibe-coding/`

## Concept cards

### D1-C1: From syntax to intent
Summary: Software development is shifting from writing syntax to expressing
intent: the developer states *what* to build, the AI handles *how*. The
paper reports that as of early 2026, 85% of professional developers use AI
coding agents, 51% daily, and roughly 41% of new code is AI-generated. The
progression ran autocomplete → inline suggestions → chat → autonomous
agents that plan multi-file changes, run tests, and open PRs.
Figure: assets/whitepaper-the-new-sdlc-with-vibe-coding/figure-1.png
Source: "The shift from syntax to intent"
Elaborate: What part of your own coding time is already intent-expression rather than syntax-writing?

### D1-C2: The agent loop
Summary: An AI agent is a model in a loop: perceive the environment, plan,
act through tools, observe the result, and iterate until the goal or a stop
condition is reached. What separates an agent from a chatbot is this loop
plus tool access — the ability to affect the world and react to feedback.
Figure: assets/whitepaper-the-new-sdlc-with-vibe-coding/figure-2.png
Source: "AI Agents: A Quick Refresher"
Elaborate: Which step of the loop do you think fails most often in practice, and why?

### D1-C3: The vibe coding ↔ agentic engineering spectrum
Summary: Vibe coding is fast, conversational, low-ceremony building where
you accept AI output largely on trust — ideal for prototypes. Agentic
engineering is the disciplined end of the same spectrum: explicit
constraints, evaluation, and review around autonomous execution — required
for production. They are not rivals; teams slide along the spectrum per
task, and the danger is using vibe-coding trust levels for
production-grade stakes.
Figure: assets/whitepaper-the-new-sdlc-with-vibe-coding/figure-3.png
Source: "What is vibe coding? — The spectrum: vibe coding to agentic engineering"
Elaborate: Name one task from your week that belongs at each end of the spectrum.

### D1-C4: Context engineering
Summary: The real durable skill is context engineering: deciding what the
model sees — requirements, code, conventions, examples, tool outputs — and
when. Static context (project docs, style guides) sets standing knowledge;
dynamic context (retrieved files, test results) is assembled per task. Bad
context, not a bad model, is behind most bad output.
Figure: assets/whitepaper-the-new-sdlc-with-vibe-coding/figure-4.png
Source: "Context engineering: the real skill"
Elaborate: Why would adding *more* context sometimes make output worse?

### D1-C5: The new SDLC and the factory model
Summary: AI compresses every SDLC phase, collapsing the
requirements→design→implement→test→deploy pipeline into short cycles. In
the factory model, the developer stops hand-crafting the product and
instead designs the system that produces it: agents write the code, tests
verify it, and the human designs the machinery of evaluation, constraints,
and context around them.
Figure: assets/whitepaper-the-new-sdlc-with-vibe-coding/figure-6.png
Source: "The new software development life cycle — The factory model"
Elaborate: In a factory model, what artifact becomes more valuable than the code itself?

### D1-C6: Harness engineering
Summary: An agent = model + harness. The harness is everything around the
model: tools, permissions, context sources, evaluation gates, and feedback
loops. Harness engineering maps onto the SDLC — configure the harness
(requirements/architecture), run it (implementation), close the feedback
loop (testing), observe it (review/deploy/maintain). A weak model in a
strong harness often beats the reverse.
Figure: assets/whitepaper-the-new-sdlc-with-vibe-coding/figure-7.png
Source: "Harness Engineering: What surrounds the model"
Elaborate: What harness elements does your current dev setup already have?

### D1-C7: Conductor, orchestrator, and the 80% problem
Summary: Two working modes: the conductor directs one agent hands-on in
real time; the orchestrator delegates to multiple agents asynchronously
and reviews results. The 80% problem: agents get you 80% of the way
fast, but the last 20% — edge cases, integration, polish — still demands
human judgment, and underestimating it is where vibe-coded projects stall.
Figure: assets/whitepaper-the-new-sdlc-with-vibe-coding/figure-8.png
Source: "The developer's evolving role: conductors and orchestrators"
Elaborate: Which mode matches how you currently use AI tools, and what would moving one step toward the other look like?

### D1-C8: The economics — CapEx vs OpEx
Summary: Pure vibe coding is low CapEx / high OpEx: nearly free to start,
but unreviewed AI code accumulates hidden debt you pay during maintenance.
Agentic engineering is high CapEx / low OpEx: building evals, specs, and
harnesses costs upfront but makes every later change cheap. Choose by how
long the code must live.
Figure: assets/whitepaper-the-new-sdlc-with-vibe-coding/figure-9.png
Source: "The Economics of AI Development"
Elaborate: Apply this to the capstone project: which investments are worth the CapEx?

## Question cards

### D1-Q1 (tests D1-C1)
Q: What does "the shift from syntax to intent" mean, and roughly how widespread is AI-assisted coding according to the paper?
Hint: Think about what the human supplies vs what the machine supplies, plus the three adoption statistics.
Key:
- Developers express what to build (intent); the AI produces the implementation (syntax)
- Adoption is mainstream: ~85% of professional developers use AI coding agents (about half daily), and ~41% of new code is AI-generated
Stretch: The paper says this shift collapses "friction of translation" in programming. Trace the three translation steps that existed before and state which ones the AI absorbs.
StretchKey:
- Old steps: understand the problem in human terms → design an abstract solution → render it in machine syntax
- AI absorbs the rendering (syntax) step and much of the solution-design step; the human keeps problem understanding, architecture, and judgment

### D1-Q2 (tests D1-C2)
Q: Name the stages of the agent loop and state what separates an agent from a chatbot.
Hint: Five verbs, then think "tools".
Key:
- Perceive → plan → act → observe → iterate
- An agent has tool access and loops on feedback until a goal is met; a chatbot only responds

### D1-Q3 (tests D1-C3)
Q: Give two defining traits of vibe coding and two of agentic engineering, and say when each is appropriate.
Hint: Trust level and ceremony level.
Key:
- Vibe coding: conversational/low-ceremony, output accepted largely on trust — right for prototypes and throwaway tools
- Agentic engineering: explicit constraints, evaluation and review around autonomy — required when code must live in production

### D1-Q4 (tests D1-C4)
Q: What is context engineering, and what is the difference between static and dynamic context?
Hint: What the model sees, and when it's assembled.
Key:
- Deciding what information the model sees and when (requirements, code, conventions, tool output)
- Static context = standing knowledge (docs, style guides); dynamic context = assembled per task (retrieved files, test results)
Stretch: A teammate's agent writes code that compiles but violates your team's conventions. Diagnose this as a context-engineering failure and propose the fix.
StretchKey:
- The conventions were missing from static context (not a model failure)
- Fix: encode conventions in standing project context (e.g. a conventions doc / AGENTS.md-style file) so every task sees them

### D1-Q5 (tests D1-C5)
Q: In the factory model, what does the developer build, and what verifies the output?
Hint: Not the product itself.
Key:
- The developer designs the system that produces software: context, constraints, and evaluation harnesses for agents
- Automated tests/evals verify the agent-produced code

### D1-Q6 (tests D1-C6)
Q: An agent equals a model plus what? List three things that component contains.
Hint: It's everything wrapped around the model.
Key:
- The harness
- Any three of: tools, permissions, context sources, evaluation gates, feedback loops

### D1-Q7 (tests D1-C7)
Q: Contrast the conductor and orchestrator modes, and state the 80% problem in one sentence.
Hint: Sync vs async; then think about the last mile.
Key:
- Conductor: hands-on, real-time direction of one agent; orchestrator: async delegation to multiple agents with review
- 80% problem: agents deliver the first 80% quickly, but the final 20% (edge cases, integration, polish) still needs human judgment

### D1-Q8 (tests D1-C8)
Q: Explain vibe coding's "hidden debt" using the CapEx/OpEx framing.
Hint: Cheap now, expensive when?
Key:
- Vibe coding is low CapEx (cheap to start) but high OpEx: unreviewed AI code accrues debt paid during maintenance
- Agentic engineering inverts this: upfront investment in evals/specs/harnesses makes later change cheap
Stretch: Your team vibe-coded an internal tool that unexpectedly became business-critical. Using the economics framing, what migration would you propose?
StretchKey:
- Pay the CapEx retroactively: add specs/tests/evals and review gates around the existing code (move it toward agentic engineering)
- Justification: the code now has a long expected lifetime, so OpEx dominates

### D1-INT (Integrate)
Q: You must ship a demo in 3 days and then maintain it for a year. Using at least three Day-1 concepts, describe your plan.
Key:
- Uses vibe coding for the 3-day demo (spectrum: low stakes, speed)
- Plans the transition: harness/evals/specs before long-term maintenance (factory model, economics)
- Names the human's role in the last 20% (80% problem) or context engineering for the handoff

## Go deeper (external, free)

- Google Agent Development Kit docs & quickstart — https://google.github.io/adk-docs/
- Anthropic, "Building effective agents" (agent-loop patterns) — https://www.anthropic.com/research/building-effective-agents
- Addy Osmani's companion essay to this whitepaper — https://addyosmani.com/blog/new-sdlc-vibe-coding/
