# Harness Engineering — Hands-On Module

A practice-first course on the discipline behind **Agent = Model + Harness**:
five labs where you take apart and build real harness layers, capped by a
workshop where you construct a complete agent harness from scratch and
prove it works with your own evals. Theory never comes first — it is
available on demand, one layer down, whenever you ask "why".

Driveable by any Claude model, including Haiku: the coach protocol
(`COACH.md`) pre-scripts every step, check, and grading rule.

## Launch

```bash
cd ~/courses/GoogKaggleAiAgent
claude --model haiku
> /harness            # resumes wherever you left off
```

Or in any chat: paste `COACH.md` + the current lab file + `progress.md`.

## The path (~5 hours total, spread over days)

| Stage | You build / break | Harness layer |
|-------|-------------------|---------------|
| Lab 1 (~30 min) | Dissect Claude Code from the outside | anatomy: all of them |
| Lab 2 (~40 min) | Your own MCP server; sabotage its docstring | tools & interfaces |
| Lab 3 (~40 min) | A context assembler; measure context rot | context engineering |
| Lab 4 (~40 min) | A PreToolUse guardrail; red-team your own hook | permissions & policy |
| Lab 5 (~45 min) | A 40-line eval harness; measure a harness change | evals & observability |
| Workshop (~2–3 h) | **Pocket-Agent**: loop, registry, gate, budget, traces, eval | all of them, from scratch |

Labs are sequential — each one's artifact or lesson is used by a later one.
Each lab ends with recap questions (graded like `5-day-course/tutor/TUTOR.md`) and a
`## Theory` section — the strong-theory layer, with pointers into
`resources/` for depth.

## Theory on demand

- `resources/links.md` — curated map: Anthropic engineering posts (context
  engineering, writing tools, building effective agents), Karpathy's
  agentic-engineering talk, ADK/MCP/Claude Code docs, awesome-lists
- `resources/papers/` — three open-access arXiv surveys (agent evaluation
  ×2, vibe coding)
- `resources/transcripts/` — cleaned transcripts of the course's Day-1
  livestream and podcast (personal study copies)
- The day-1 whitepaper's "Harness Engineering" section is the module's
  origin text: `5-day-course/day1-intro-agents-and-vibe-coding/whitepaper-*.md`

## Quality bar

Held to the repo's `RIGOR.md` rubric (≥95, zero blockers): every command
and CHECK has been run against the live `claude` CLI and the current MCP
SDK. Note one CLI ergonomic the labs rely on — an empty `--allowedTools ""`
placed right before a positional prompt swallows it, so the labs pipe the
prompt via stdin. If you extend a lab, re-run its commands.

## Working space

Labs write into `harness-eng/scratch/` (gitignored). Your progress lives in
`harness-eng/progress.md` — commit it to track the journey. The workshop
reference solution is in `workshop/solution/` — it is the coach's answer
key; opening it before workshop M6 is spoiling yourself.
