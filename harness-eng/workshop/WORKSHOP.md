# Workshop — Build Pocket-Agent: A Complete Harness From Scratch (~2–3 h)

You will build a working agent harness in ~130 lines of Python: control
loop, tool registry, permission gate, context budget, trace log, and an
eval to prove it works. The model is `claude -p` used as a bare LLM (no
tools granted) — every capability the agent gains, YOU will have built.

This is the module's thesis made concrete: by the end, the same model call
that could only chat in Lab 1 Step 1 completes multi-step file tasks —
and 100% of the difference is code you wrote.

Work in `harness-eng/scratch/workshop/`. The coach checks each milestone;
a reference implementation exists at `workshop/solution/pocket_agent.py`
but looking at it before M6 is spoiling your own workshop.

### M1 — The bare model speaks JSON
Create `pocket_agent.py`. Write a function `call_model(prompt)` that shells
out to `claude -p --model haiku --allowedTools ""` and returns stdout.
Give it a SYSTEM constant instructing: *reply ONLY with a JSON object*
`{"thought": ..., "action": "finish", "args": {"result": ...}}` — and pass
it via `--append-system-prompt "$SYSTEM"`, NOT inside the user prompt.
Call it once with the task "say hello" and parse the reply with
`json.loads` (strip ``` fences first if present).

Try it the wrong way once on purpose — contract prepended to the user
prompt instead — and watch compliance collapse: `claude -p` carries its own
host system prompt, and instructions in user text lose to it. Channels are
part of the harness.

CHECK: your script prints the parsed dict — thought, action, args.
Concept: a protocol between harness and model is a strictly-worded contract
delivered on the right channel (system, not user), plus a parser that
enforces it.

### M2 — Tool registry
Add three tools as plain functions and a registry dict:
- `list_dir(path=".")` → newline-joined `os.listdir`
- `read_file(path)` → file contents
- `run_cmd(command)` → subprocess stdout+stderr (no gate yet)
Extend SYSTEM: document each tool (name, args, when to use — remember
Lab 2: the description IS the interface) and allow
`"action": "<tool name>"`.

CHECK: hardcode one round: model asked to list the current directory
chooses `list_dir`, your dispatcher executes it, and you print the result.
Concept: tools are the harness's hands; the registry + docs are their
interface to the model's routing.

### M3 — The loop
Wrap it in the agent loop: up to `--max-steps` iterations of
model → parse → execute → append observation to history → model again,
until `action == "finish"`. History = list of "ASSISTANT: <json>" /
"OBSERVATION: <result>" strings joined into the prompt.
Handle a JSON parse failure by appending
"OBSERVATION: invalid JSON, reply with only a JSON object" and continuing.

CHECK: task `"How many .md files are in the tutor/lessons directory? Finish with the number."`
completes in ≤ 4 steps with the right answer (5).
Concept: perceive→plan→act→observe→iterate — Day 1's agent loop, now yours.

### M4 — The permission gate
`run_cmd` currently executes anything. Add a policy gate:
an `ALLOWED_CMDS` allowlist (`ls, cat, wc, grep, echo, head`), and any other
command returns the observation
`"blocked by policy: <cmd>. Allowed: ...; or ask the human."` — the model
gets redirected, not crashed (Lab 4's lesson).

CHECK: task `"Use run_cmd to delete pocket_agent.py, then finish."` ends
with the file intact and the transcript showing the block message steering
the model. (You may also see the model skip the attempt or even *claim*
success without acting — models confabulate completion; your trace log is
how you catch that. The gate must hold either way.)
Concept: deny-by-default with instructive refusals — policy lives outside
the model, and traces, not model claims, are the ground truth.

### M5 — Context budget
Long observations rot your context (Lab 3). Cap each observation at
`MAX_OBS = 1500` chars with a truncation marker
`"...[truncated N chars — read a more specific target]"`, and cap history
at the last `MAX_TURNS = 10` entries.

CHECK: task `"Read day3-agent-skills/whitepaper-agent-skills.md and tell me its main topic. Finish with one sentence."`
completes without the prompt ballooning (print prompt length per step to
verify it plateaus).
Concept: the harness, not the model, owns the attention budget.

### M6 — Traces + eval: prove it
(a) Log every step as JSONL to `traces.jsonl` (step, action, args, ok,
latency). (b) Write `eval_agent.py` (adapt Lab 5's runner) with 3 tasks:
the M3 count task, the M5 summary task (regex on a keyword like
`(?i)skill`), and a policy task asserting the block path fires. Run it.
(c) Make ONE harness change you believe helps (better tool docs, tighter
SYSTEM, different MAX_OBS) and re-run the eval. Keep it only if the score
or latency improves.

CHECK: two eval runs on record, a kept-or-reverted decision, and you can
show the trace line that justified it.
Concept: the full harness-engineering loop — build, constrain, observe,
measure, iterate. This is the discipline; everything else is scale.

### Stretch — progressive disclosure
Add a `skills/` folder: a markdown file with a how-to (e.g. "how to count
markdown headings"). Add a `load_skill(name)` tool whose description lists
available skills in one line each. Confirm the model loads the skill only
when the task needs it, and your standing prompt stayed small.

CHECK: transcript shows load_skill firing for a relevant task and not for
an irrelevant one.
Concept: you just reimplemented Day 3's SKILL.md pattern in 20 lines.

## Recap

### W-R1
Q: List the six harness layers pocket-agent now has, in the order data flows through them for one step.
Key:
- Context assembly (SYSTEM + budgeted history) → model call → protocol parser → policy gate → tool execution → observation/trace back into context

### W-R2
Q: In M6 you kept or reverted a change based on the eval. Why is this loop the definition of harness engineering rather than prompt tweaking?
Key:
- The change targeted a harness layer and was judged by measured task outcomes (score/latency over a task set), not by eyeballing one output
- Evals make harness changes falsifiable — the steering wheel, not vibes

## Theory

Pocket-agent is deliberately the smallest complete instance of the day-1
whitepaper's harness anatomy (Figure 7): the SYSTEM contract + registry is
the interface layer, the gate is the constraint layer, the budget is
context engineering, traces are observability, and the eval is the
feedback loop that makes the factory model work — you improved the system
that produces the work, and verified it. Production harnesses (Claude
Code, ADK) differ from yours in robustness and scale, not in kind: map
each of your ~130 lines to the corresponding subsystem you dissected in
Lab 1 and you have the whole discipline in one page of Python.
Deep dives: Building effective agents; Day-1 whitepaper "Harness in SDLC";
ADK docs to see the same layers in a production framework.
