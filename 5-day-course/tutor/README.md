# Interactive Course Tutor

A study system for the 5-Day AI Agents Vibe Coding course, built on the
cognitive science of durable learning. It is designed to be **driven by any
Claude model, including Haiku**: all judgment calls are pre-made, every
question ships with its own grading key, and the session flow is a strict
state machine.

## Files

| File | Purpose |
|------|---------|
| `TUTOR.md` | The tutor protocol — load this to run a session |
| `PRINCIPLES.md` | The neuroscience behind the design (read once as a human) |
| `lessons/day1.md` … `day5.md` | Concept cards + question cards with grading keys |
| `progress.md` | Your spaced-repetition state (the tutor updates it) |

## Launch

**In Claude Code (recommended — the tutor reads/updates `progress.md` itself):**

```bash
cd ~/courses/GoogKaggleAiAgent
claude --model haiku        # Haiku is enough — the protocol pre-makes all judgment calls
> /tutor                    # default session
> /tutor quick              # 10-min spaced review only
> /tutor exam               # 12-question mixed mock exam
```

The `/tutor` command lives in `.claude/commands/tutor.md`; it loads the
protocol, gets today's date itself, and picks up where your progress file
left off.

**In any chat app:** paste the contents of `TUTOR.md`, then the lesson file
for the day you're on, then your current `progress.md`, and say
"Run my session. Today is \<date\>." At the end, copy the updated PROGRESS
block it prints back into `progress.md` yourself.

## Session types

- `session` (default, ~30–45 min) — spaced review of due cards, then new
  concepts for the current day, then a retrieval quiz.
- `quick` (~10 min) — spaced review of due cards only. Good for off-days.
- `exam` (~30 min) — 12 mixed questions across all days you've studied.
  Run once after finishing Day 5, and again a week later.

## How it adapts to you

All adaptivity is rule-based so any model can drive it:

- **Placement** — your first session asks one experience question and sets
  your starting difficulty (`core` or `stretch`).
- **Difficulty tracking** — three straight correct answers switch you to
  stretch (application-level) variants; a miss drops you back to core.
- **Re-teaching** — two consecutive misses trigger a re-presentation of the
  concept summary and a hint on the next question.
- **Blind-spot detection** — tag answers `(sure)` or `(unsure)`; confident
  misses get flagged (the hypercorrection effect makes these the most
  fixable errors) and resurface the next day.
- **Spacing** — every card carries its own review date; strong cards drift
  out to 21-day intervals, weak ones return tomorrow.

Each lesson also ends with **Go deeper** links — vetted, free external
tutorials (official MCP/A2A/ADK docs, Anthropic's skills course, OWASP,
GitHub Spec Kit) for topics you want beyond the whitepapers.

## Quality bar

Held to the repo's `RIGOR.md` rubric. Every card's facts and citations were
checked against the source whitepapers: the statistics (Day 1: 85% use AI
agents / 51% daily / 41% of new code; Day 3: 56% non-invocation, 58% vs 63%
stripped-skill-vs-none, 100% vs 53% for a passive conventions index), every
`Figure:`/`Table:` caption, and every `Source:` section heading resolve to
the actual whitepaper. External "Go deeper" links are checked live (200) and
point at canonical URLs. This is repeatable: `bash 5-day-course/tutor/verify.sh`
re-greps every cited statistic, figure caption, and section heading against
the whitepapers (add `--links` to also curl the Go-deeper URLs). Run it after
any whitepaper is re-fetched or re-enhanced.

## The one rule the human must follow

**Answer from memory before looking anything up.** The struggle to retrieve
is the event that strengthens memory — reading the answer first cancels the
benefit (see `PRINCIPLES.md`). Wrong answers cost nothing; the tutor corrects
them immediately, which is when your brain is most ready to encode the fix.

Track your journey: commit `progress.md` after each session —
`git add 5-day-course/tutor/progress.md && git commit -m "study session $(date +%F)"`.
