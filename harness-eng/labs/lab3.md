# Lab 3 — Context Engineering: Measure It, Don't Believe It (~40 min)

Goal: demonstrate on your own machine that (a) missing context produces
confident wrong answers, (b) drowning context degrades answers, and
(c) a curated context assembler fixes both. You'll build the assembler.

Prereqs: Labs 1–2. Run from the repo root.

### Step 1 — Establish a question with a knowable answer
Pick something answerable only from this repo's materials:

```bash
echo "In the Vercel study cited in the Agent Skills whitepaper, what was the non-invocation rate for skills expected to trigger? One sentence." \
  | claude -p --model haiku --allowedTools ""
```

> Prompt via stdin, `--allowedTools ""` last — an empty tool flag placed
> right before a positional prompt swallows it. Same pattern all lab long.

CHECK: the model either admits it doesn't know or guesses (the true figure,
from `day3-agent-skills/whitepaper-agent-skills.md`, is 56%). Note what it
said.
Concept: no context → the model samples from priors. Confidence is not
evidence.

### Step 2 — Perfect context, tiny prompt
Give it only the relevant section:

```bash
{ echo "Based only on the text below: what was the non-invocation rate? One sentence."; echo; \
  grep -A6 "non-invocation" day3-agent-skills/whitepaper-agent-skills.md; } \
 | claude -p --model haiku --allowedTools ""
```

CHECK: correct answer (56%), grounded in the excerpt.
Concept: retrieval-then-read beats recall. The harness's job is getting the
right 6 lines in front of the model.

### Step 3 — Drown it
Now bury the same fact in noise — feed three whole whitepapers and ask the
same question:

```bash
{ echo "What was the non-invocation rate in the Vercel study? Also list every protocol mentioned. One short paragraph."; echo; \
  cat day1*/whitepaper-*.md day2*/whitepaper-*.md day3*/whitepaper-*.md; } \
 | claude -p --model haiku --allowedTools ""
```

CHECK: observe quality vs Step 2 — slower, and often fuzzier or partially
wrong on one of the two asks. Record what degraded. (If it aces it, note
that too — then compare cost/latency of Step 2 vs Step 3, which is the same
lesson in economic form.)
Concept: context rot — more tokens compete for the same attention budget,
and you pay for all of them.

### Step 4 — Build the assembler
Create `harness-eng/scratch/assemble.sh` — a 15-line curated-context tool:

```bash
#!/bin/bash
# usage: assemble.sh "<search term>" [max_lines] — builds a tight context pack
TERM="$1"; MAX="${2:-40}"
{
  echo "## Context pack for: $TERM"
  grep -rn -B2 -A4 "$TERM" day*/whitepaper-*.md tutor/lessons/*.md 2>/dev/null \
    | head -"$MAX"
} 
```

```bash
chmod +x harness-eng/scratch/assemble.sh
harness-eng/scratch/assemble.sh "non-invocation" | wc -l
```

CHECK: a compact pack (≤ ~44 lines) containing the fact.
Concept: this is dynamic context assembly — the third pillar next to static
context (CLAUDE.md) and tools.

### Step 5 — Assembler + model
```bash
{ echo "Based only on the context pack below: what was the non-invocation rate, and what does it imply for skill design? Two sentences."; echo; \
  harness-eng/scratch/assemble.sh "non-invocation"; } \
 | claude -p --model haiku --allowedTools ""
```

CHECK: correct figure AND a grounded implication, at a fraction of Step 3's
input size.
Concept: curation beats volume. "Informative, yet tight" is the whole game.

### Step 6 — Compare the layers
The four context layers, by lifetime and who fills them:

```
   LIFETIME →   always-on            per-session          per-task            accumulating
              ┌──────────────┐    ┌───────────────┐   ┌──────────────┐    ┌────────────────┐
   context →  │ static:      │    │ session inject:│   │ dynamic:     │    │ working memory:│
              │ CLAUDE.md /  │    │ --append-      │   │ assemble.sh  │    │ message history│
              │ AGENTS.md    │    │ system-prompt  │   │ (retrieval)  │    │ (grows, rots)  │
              └──────────────┘    └───────────────┘   └──────────────┘    └────────────────┘
   fix for →  rules every task    one run's framing   big corpora, load   compaction is the
              needs                                    only what's needed  maintenance job
```

State (to your coach) where each of these lives in the harness: your
`~/.claude/CLAUDE.md`, the assembler script, the `--append-system-prompt`
flag, a conversation's message history.

CHECK: you place them as: static standing context / dynamic per-task
context / per-session static injection / accumulating working memory.
Concept: context engineering = managing all four deliberately.

## Recap

### L3-R1
Q: Define context rot and cite what you observed in Step 3.
Key:
- Quality degrades as prompt size grows, well before the window is full (attention budget is finite)
- Observed: same question answered worse/slower/costlier with 3 whitepapers than with a 6-line excerpt

### L3-R2
Q: Your agent keeps misciting project conventions. Using this lab's layers, name two different context fixes and when each applies.
Key:
- Static fix: put conventions in standing context (CLAUDE.md/AGENTS.md) — for rules that apply to every task
- Dynamic fix: retrieve/assemble the relevant convention section per task — for large corpora where always-loading would rot context

## Theory

Anthropic's *Effective context engineering for AI agents* frames context as
a finite attention budget to be spent, not a bucket to be filled: curate
the smallest set of high-signal tokens that makes the desired behavior
likely. Strategies: retrieval before generation, compaction of history,
few-shot examples chosen as canonical demonstrations, and progressive
disclosure (Day 3's skills) so instructions load only on demand. The Day-1
whitepaper calls context engineering "the real skill" and splits it
static/dynamic — your Step 6 mapping. Figure 4 of the day-1 whitepaper
diagrams it.
Deep dives: `resources/links.md` → Effective context engineering; Claude
Cookbook context recipes; Day-3 whitepaper "context rot" sections.
