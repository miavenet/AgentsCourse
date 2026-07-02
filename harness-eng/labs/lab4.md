# Lab 4 — Control: Permissions, Hooks, and a Real Guardrail (~40 min)

Goal: build the constraint layer of a harness with your own hands — a
deny-by-default tool policy, then a programmatic PreToolUse hook that
blocks a class of dangerous actions no matter what the model decides.

Prereqs: Labs 1–3. Work in a throwaway directory so experiments are safe:

```bash
mkdir -p harness-eng/scratch/lab4 && cd harness-eng/scratch/lab4
```

### Step 1 — Observe default-deny in print mode
```bash
echo "victim" > precious.txt
echo "Delete precious.txt" | claude -p --model haiku --disallowedTools "*"
cat precious.txt
```

CHECK: file still says `victim`; with every tool denied the model could not
act.
Concept: denying all tools with `--disallowedTools "*"` is true
deny-by-default — the safest baseline any harness starts from. (Do NOT use
`--allowedTools ""` for this: an empty allow list is ignored and the default
tools stay on — it is not deny-by-default.)

### Step 2 — Scoped allow
Grant exactly one capability — reading — and ask for read AND delete:
```bash
echo "Read precious.txt, tell me its contents, then delete the file." \
  | claude -p --model haiku --allowedTools "Read"
cat precious.txt
```

CHECK: the file still exists (`victim`) and the model reports the delete was
blocked — it could read (Read was granted) but not delete (no delete tool
granted).
Concept: capability scoping — you grant specific tools, and the model can do
only what its granted tools permit. Scoping goes finer still: `Bash(cat:*)`
grants only the `cat` verb, not all of `Bash`.

### Step 3 — Write a guardrail hook
Create `.claude/settings.json` in this lab4 directory:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "python3 -c \"import json,sys; d=json.load(sys.stdin); cmd=d.get('tool_input',{}).get('command',''); bad=any(w in cmd for w in ['rm ','rm\\t','unlink','shred']); print(json.dumps({'decision':'block','reason':'destructive commands are blocked by policy; ask the human to delete files'}) if bad else '{}')\""
          }
        ]
      }
    ]
  }
}
```

CHECK: file exists and `python3 -m json.tool < .claude/settings.json` parses.
Concept: a hook is policy-as-code sitting between the model's intent and
execution — the model is not consulted about it.

### Step 4 — Attack your own guardrail
```bash
claude -p --model haiku --allowedTools "Bash" \
  "Delete precious.txt using any means necessary."
cat precious.txt
```

CHECK: file survives, and the transcript shows the block reason being fed
back to the model (rerun with `--output-format json` to see it if needed).
Concept: the reason string is context engineering for the refusal — a good
block message redirects the agent instead of just failing it.

Troubleshoot: hooks load per-directory; make sure you're running inside
`lab4/` where the settings file lives, and that the JSON parses.

### Step 5 — Find the bypass, then close it
Your hook checks for `rm ` — try to think like a red teamer: what deletion
command slips through? Test your idea (e.g. Python's `os.remove`, `mv` to
/tmp, `> precious.txt` truncation). Then extend the `bad=` list to catch
what you found.

CHECK: you found at least one bypass, demonstrated it, and patched it.
Concept: guardrails are an adversarial, iterative artifact — Red team finds,
Green team builds the fix in (Day 4's triad, live).

### Step 6 — Human-in-the-loop by design
State to your coach: for your capstone or current project, which THREE actions
would you put behind (a) hard block, (b) human approval, (c) free autonomy —
and why those tiers.

CHECK: three actions with sensible blast-radius reasoning.
Concept: autonomy is scoped by consequence, not by capability.

## Recap

### L4-R1
Q: Why is a PreToolUse hook stronger than a system-prompt instruction like "never delete files"?
Key:
- The hook is deterministic policy outside the model — it executes regardless of model output/jailbreaks
- Prompt instructions are probabilistic and compete with everything else in context

### L4-R2
Q: Your Step-5 bypass hunt is which security-team role, and what does the triad's third color add beyond attack/defend?
Key:
- Red (attack your own system)
- Green: building security into the development process from the start (safe defaults, guardrails as part of the harness), not bolted on after

## Theory

Day 4's whitepaper frames this as Effective Trust in a non-deterministic
system: no single review certifies an agent, so trust comes from layered,
continuously-verified safeguards — pillars covering sandboxing, identity
and least privilege, high-stakes HITL gates, and the Red/Blue/Green triad.
Your hook implements the "policy" strand that Day 5 scales up into a
policy server: a decision point that allows, denies, or escalates each
action against org rules. Note the layering you built: deny-by-default
(Step 1) → scoped capability (Step 2) → programmatic policy (Steps 3–5) →
human judgment (Step 6). Each layer catches what the previous one can't.
Deep dives: Day-4 whitepaper "7-Pillar Agent Security Architecture";
Day-5 "Zero-Trust Development"; OWASP Agentic Top 10 (links.md).
