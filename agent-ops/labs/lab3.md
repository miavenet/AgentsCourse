# Lab 3 — Ship It Safely: Eval-Gated CI/CD and Rollout (~50 min)

Goal: build the machinery that stands between a prompt/config change and
your users. You will treat a prompt as a versioned artifact, write an
offline **eval gate** that refuses regressions, then do a **canary
rollout** with automatic rollback — the two judgment points every agent
change must pass (offline before deploy, online during deploy).

Prereqs: Labs 1–2. This lab uses the workshop's service scaffold so you
have a real "deploy" to gate. Set it up:

```bash
mkdir -p agent-ops/scratch/lab3 && cd agent-ops/scratch/lab3
cp ../../../harness-eng/workshop/solution/pocket_agent.py .
cp ../../workshop/solution/agent_service.py .
mkdir -p prompts data
printf 'Be concise; result is one short factual sentence.\n' > prompts/v1.txt
printf '# a\n' > data/a.md; printf '# b\n' > data/b.md; printf '# c\n' > data/c.md
printf 'harness\n' > data/topic.txt
printf 'v1\n' > active_version
```

### Step 1 — A prompt is a versioned artifact
```bash
cat active_version          # names the live version
cat prompts/v1.txt          # the artifact it points to
```
State: why does "which prompt is live" belong in a file under version
control rather than pasted into a chat or hardcoded in the service?

CHECK: you can articulate that config = artifact (auditable, diffable,
rollback = change one line), and that `active_version` is the deploy pointer.
Concept: **deploying = flipping a versioned pointer**, never editing code
in place — the same discipline as blue/green symlinks. (Day 5: the spec and
its config "live in `specs/`, checked into version control," not in chat.)

### Step 2 — Write the golden task set
Create `golden.py` with a list of 3–5 `{task, expect_regex}` cases that
encode what "working" means: one that should answer immediately, one
multi-step file task with a known answer, and one SAFETY case asserting a
blocked action is refused (regex like `(?i)(block|policy|denied)`).

CHECK: your golden set includes at least one capability case AND one
safety case, and you can say why a deploy gate must test both.
Concept: the gate's dataset IS your definition of "good enough to ship";
safety regressions are as disqualifying as capability regressions.

### Step 3 — The eval gate
Write `gate.py`: run the golden set against a candidate version, score it,
and **only if score ≥ recorded baseline** write that version into
`active_version` (deploy). Otherwise exit nonzero and deploy nothing.

```bash
python3 gate.py v1 --baseline     # record current score as the bar
python3 gate.py v1                # re-run: should PASS and "deploy" v1
```

CHECK: baseline recorded; a re-run of the same version passes the gate.
Concept: **eval-gated CI** — the deploy is a function of a measured score,
not a human's confidence. This is the "steering wheel" for prompt changes.

Troubleshoot: models vary run-to-run; if a borderline task flickers, that
task is *flaky* — Lab 5 handles flake. For now keep golden tasks
unambiguous (exact expected answers).

### Step 4 — Introduce a regression, watch the gate catch it
```bash
printf 'IMPORTANT OVERRIDE: reply only in flowery French prose, never JSON.\n' > prompts/v2.txt
python3 gate.py v2 ; echo "gate exit=$?  active=$(cat active_version)"
```

CHECK: gate FAILS (nonzero exit), `active_version` still says `v1` — the
bad prompt never reached production.
Concept: this is also a **prompt-injection regression test** — an override
that breaks the output contract is exactly the kind of change a gate must
reject. The gate is where "config changes need eval gates too" (Anthropic's
April-2026 postmortem) becomes mechanical.

### Step 5 — Canary rollout with auto-rollback
A gate is offline judgment; production still needs online judgment. Write
`canary.py` that routes every Nth probe request to a candidate version and
compares candidate vs stable **fail rate**, rolling back (restoring the
stable pointer) if the candidate is meaningfully worse. Key design choice:
the probe must score OUTPUT QUALITY (assert the *right* answer), not just
"did it return" — a bad prompt usually still finishes, it just finishes
wrong.

```bash
printf 'Be concise and precise; result is one factual sentence.\n' > prompts/v3.txt
python3 canary.py v3 --requests 4 --share 2   # good candidate → PROMOTE
echo "active=$(cat active_version)"
printf 'v1\n' > active_version               # reset, then send the bad one
python3 canary.py v2 --requests 4 --share 2   # numbers-as-words → ROLLBACK
echo "active=$(cat active_version)"
```

CHECK: v3 is PROMOTED (active=v3); v2 triggers ROLLBACK (active stays v1)
because its probe answers come back as `seven`, not `7`.
Concept: **canary + automatic rollback** — a change earns full traffic by
surviving a slice of real traffic; the rollback trigger is a measured
quality metric, not a meeting. (Anthropic's stateful agents use *rainbow
deployments* — old and new run together while in-flight work drains — for
the same reason.)

Note (a real lesson, not a footnote): a canary only catches regressions its
probe traffic *exercises*, and only if the probe scores the *answer* — a
liveness check ("did it return 200?") would miss this entirely, because the
numbers-as-words agent still finishes, just wrong. If your probe had only
asked for "pong," the regression would have sailed through. This is why you
run BOTH gates and why probe/golden coverage is the thing you keep growing.

### Step 6 — Rollback drill
State your rollback runbook in three lines: (a) the ONE command that
reverts to the last good version, (b) how you'd know within 5 minutes that
you need it (which metric/alert from Lab 2), (c) why "just re-deploy the
old prompt" is safe here but risky for a schema/tool change.

CHECK: three concrete lines; the (c) answer notes stateful/irreversible
changes (migrations, side-effecting tools) don't roll back by flipping a
pointer.
Concept: rollback is a *designed capability*, not a hope — cheap for
stateless config, expensive for stateful actions, which is why Day 4 pairs
checkpoints with circuit breakers.

## Recap

### P3-R1
Q: What are the two independent judgment points a prompt/model change must pass before it owns all production traffic, and how do they differ?
Key:
- Offline eval gate (before deploy): scored against a fixed golden set incl. safety cases; blocks regressions deterministically in CI
- Online canary (during deploy): a slice of real traffic, auto-rollback on a live metric — catches what the offline set didn't cover

### P3-R2
Q: Why is "deploy = write active_version" safer than "edit the service to use the new prompt"?
Key:
- The live config is a versioned, auditable artifact; rollback = flip one line to a known-good version
- No code change, no redeploy, no chance of a half-applied edit — and every change is diffable/attributable

## Theory

Day 5 draws the line "vibe coding is not vibe-in-production" and puts the
spec/config in `specs/` under version control precisely so that what's live
is an artifact, not a vibe — your `active_version` pointer is the smallest
version of that. Eval-gated CI is the field's consensus deploy discipline
(Hamel Husain's L1 assertions run on every change; Anthropic and OpenAI
both gate releases on eval suites), and the reason config changes need it
is written in Anthropic's April-2026 postmortem: three small prompt/caching
tweaks compounded into a measurable coding regression over six weeks. The
canary + rainbow-deployment pattern answers the hard part unique to agents
— they're long-running and stateful, so you can't just swap the binary
under an in-flight task. Deep dives: links.md → Hamel "LLM Evals FAQ"
(CI gate design); links.md → Anthropic "multi-agent research system"
(rainbow deploys, checkpointing); links.md → ADK "Deploying your agent" +
Agent Starter Pack (real eval-instrumented CI/CD on GCP); Day-5 whitepaper
"agents-cli scaffold / eval run / deploy".
