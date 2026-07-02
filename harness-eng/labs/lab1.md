# Lab 1 — Dissect a Production Harness (~30 min)

Goal: you already own a production-grade agent harness — Claude Code. Take
it apart and identify every harness component from the outside, so the
formula **Agent = Model + Harness** stops being a slogan.

Prereqs: `claude` CLI installed and logged in. Work anywhere; steps are
read-only.

### Step 1 — Same model, no harness
Run the model with the harness bypassed as far as possible — a single
print-mode call with no tools:

```bash
claude -p --model haiku --allowedTools "" \
  "List the files in the current directory."
```

CHECK: the reply does NOT contain a real file listing — the model either
refuses, asks for information, or hallucinates. It cannot act.
Concept: a model without tools can only talk; capability lives in the harness.

### Step 2 — Same model, with harness
```bash
claude -p --model haiku --allowedTools "Bash(ls:*)" \
  "List the files in the current directory."
```

CHECK: the reply reflects the actual directory contents.
Concept: one flag changed — the tool surface — and the same model became an
agent. The delta was 100% harness.

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
