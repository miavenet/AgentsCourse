# Lab 1 — Dissect a Production Harness (~30 min)

Goal: you already own a production-grade agent harness — Claude Code. Take
it apart and identify every harness component from the outside, so the
formula **Agent = Model + Harness** stops being a slogan.

Prereqs: `claude` CLI installed and logged in. Work anywhere; steps are
read-only.

### Step 1 — Same model, no tools
Give the model a task whose answer it CANNOT guess — a word only present in
a local file — with every tool denied:

```bash
mkdir -p harness-eng/scratch/lab1 && cd harness-eng/scratch/lab1
echo "banana47" > secret.txt
echo "Read the file secret.txt and reply with only the word inside it." \
  | claude -p --model haiku --disallowedTools "*"
```

> Two harness-ergonomics details we use all lab: the prompt goes in via
> **stdin** (an `--allowedTools`/`--disallowedTools` value placed right
> before a positional prompt can swallow it), and we deny tools with
> `--disallowedTools "*"`, NOT `--allowedTools ""` — an empty allow list is
> ignored and the default read tools stay on, so `""` does not give you a
> tool-less model.

CHECK: the reply is NOT `banana47` — the model emits an unexecuted tool-call
or guesses a random word. With every tool denied it cannot read the file.
Concept: a model with no tools can only talk (and guess); capability lives
in the harness.

### Step 2 — Same model, one tool
```bash
echo "Read the file secret.txt and reply with only the word inside it." \
  | claude -p --model haiku --allowedTools "Read"
```

CHECK: the reply is `banana47` — the real file contents.
Concept: one flag changed — a single tool granted — and the same model can
now act on the world. The delta was 100% harness.

### Step 3 — Inventory the tool surface
```bash
claude -p --model haiku --output-format json \
  "Say only the word: ready" | python3 -m json.tool | head -30
```
Then look at what the harness reports about the run (cost, duration,
turns, session id).

CHECK: you can point at fields the *harness* produced that the *model*
never saw (e.g. cost accounting, session identity).
Concept: the harness wraps every call with plumbing — identity, accounting,
transcripts — invisible to the model but essential to operating it.

### Step 4 — Find the permission layer
```bash
cat ~/.claude/settings.json 2>/dev/null | head -40
ls .claude/ 2>/dev/null && cat .claude/settings.local.json 2>/dev/null | head -40
```

CHECK: you found at least one `permissions`/`allow`/`deny`-style structure
(or confirmed the files exist but are empty — also a finding).
Concept: permissions are declarative harness config, not model behavior —
they hold even if the model "wants" otherwise.

### Step 5 — Find the context layer
```bash
ls ~/.claude/CLAUDE.md 2>/dev/null; ls CLAUDE.md AGENTS.md 2>/dev/null
```
Open whichever exists and skim it.

CHECK: you can say which scope each file applies to (global vs project).
Concept: standing instructions are static context, injected by the harness
every session — the model never "remembers" them; it re-reads them.

### Step 6 — Map it
Without looking at the day-1 whitepaper, draw (text sketch is fine) the
harness anatomy you just observed: model in the middle, then label the
layers you found in steps 1–5.

CHECK: your sketch names at least four distinct layers (tools, permissions,
static context, accounting/observability — session/loop control also
counts).
Concept: this diagram *is* Figure 7 of the day-1 whitepaper — you just
derived it empirically. Compare:
`day1-intro-agents-and-vibe-coding/assets/whitepaper-the-new-sdlc-with-vibe-coding/figure-7.png`

## Recap

### L1-R1
Q: In Steps 1–2 the model was identical. State precisely what changed and what that implies about where agent capability lives.
Key:
- Only the allowed tool surface changed (harness config)
- Capability (and safety) are properties of the harness at least as much as the model

### L1-R2
Q: Name the four harness layers you located in this lab and one artifact/file/flag that evidences each.
Key:
- Tools (--allowedTools), permissions (settings.json allow/deny), static context (CLAUDE.md/AGENTS.md), observability/accounting (JSON result fields: cost, turns, session)

## Theory

The harness anatomy you derived in Step 6 (compare your sketch — this is
Figure 7 in text form):

```
                         ┌──────────────── HARNESS ────────────────┐
   standing context ────▶│  static context (CLAUDE.md / AGENTS.md)  │
   (Step 5)              │              │                          │
   tools (Step 1–2) ────▶│         ┌────▼────┐   permissions ◀──── Step 4
                         │  tools ─▶│  MODEL  │◀─ (settings.json    │
   per-task context ────▶│         └────┬────┘   allow/deny)       │
                         │              │                          │
                         │   loop / session control  ── observability & │
                         │   (perceive→act→observe)     accounting (Step 3:│
                         │              │               cost, turns, id)   │
                         └──────────────▼──────────────────────────┘
                                   actions / output
```
Agent = Model + Harness: the model is one box; everything else is the
harness you just inventoried.

The day-1 whitepaper defines the harness as everything surrounding the
model: tools, permissions, context sources, evaluation gates, feedback
loops ("Harness Engineering: What surrounds the model"). The practical
consequence you just demonstrated is the industry finding that swapping
the harness moves benchmark scores far more than swapping the model —
capability is co-produced. Anthropic's *Building effective agents* defines
an agent as "an LLM autonomously using tools in a loop", which makes the
loop-and-tools wrapper — not the weights — the unit you engineer.
Deep dives: `resources/links.md` → Building effective agents; day-1
whitepaper sections "Harness Engineering" and "The factory model".
