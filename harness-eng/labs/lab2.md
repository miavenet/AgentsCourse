# Lab 2 — Tools: Build, Plug In, and Break an MCP Server (~40 min)

Goal: build your own MCP server in ~25 lines of Python, plug it into the
Claude Code harness, and then prove experimentally that the *description*
of a tool changes agent behavior as much as its implementation.

Prereqs: Lab 1 done. Python 3.10+. Work in `harness-eng/scratch/` (create it;
it is gitignored-friendly working space).

### Step 1 — Write the server
Create `harness-eng/scratch/costs_mcp.py`:

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("course-costs")

# Fictional internal rates (NOT public pricing) — chosen so the correct
# answer can ONLY come from calling this tool, never the model's memory.
PRICES = {"haiku": 2.0, "sonnet": 6.0, "opus": 40.0}

@mcp.tool()
def estimate_cost(model: str, million_tokens: float) -> str:
    """Estimate this course's internal USD cost for a model run given input size in millions of tokens."""
    p = PRICES.get(model.lower())
    if p is None:
        return f"unknown model '{model}'; known: {', '.join(PRICES)}"
    return f"${p * million_tokens:.2f}"

if __name__ == "__main__":
    mcp.run()
```

Install the SDK in a venv and smoke-test the import (a venv, not
`pip install --user`: a Homebrew/system Python refuses global installs with
"externally-managed-environment" — PEP 668):
```bash
cd harness-eng/scratch
python3 -m venv .venv && source .venv/bin/activate
pip install "mcp[cli]"
python3 -c "import mcp; print('sdk ok')"
```
Keep this venv active for the rest of the lab (the server runs in it). To
leave it later: `deactivate`.

CHECK: `sdk ok`.
Concept: an MCP server is just a process that describes and serves tools —
20 lines is a real one.

### Step 2 — Plug it into the harness
```bash
cd harness-eng/scratch
# point it at the VENV's python so the server can import mcp:
claude mcp add course-costs -- "$(pwd)/.venv/bin/python3" "$(pwd)/costs_mcp.py"
claude mcp list
```

CHECK: `course-costs` appears in the list (and `claude mcp get course-costs`
shows it Connected — if it shows failed, the interpreter path is wrong).
Concept: discovery→configuration→connection (Day 2's consumer flow) — you
just did all three from the producer side.

### Step 3 — Watch the agent choose your tool
The tool is named `mcp__<server>__<tool>` — here
`mcp__course-costs__estimate_cost`. Grant it, and ask for a number the
model can't know without it:
```bash
echo "Using the available tools, what is this course's internal cost for 2 million tokens on opus? Reply with the dollar amount." \
  | claude -p --model haiku --allowedTools "mcp__course-costs__estimate_cost"
```

CHECK: the answer is **$80.00** — a figure the model cannot produce from
memory (the rates are fictional), which proves it called `estimate_cost`.
Confirm with `--output-format json`: `num_turns` > 1 means a tool
round-trip happened.
Concept: the model discovered and selected your tool purely from its
machine-readable self-description — and only a granted tool can fire.

### Step 4 — Sabotage the description (not the code)
Edit ONLY the docstring in `costs_mcp.py` to something misleadingly vague:
`"""Internal accounting helper."""` — leave the code identical. Restart the
server so the new description loads (`claude mcp remove course-costs` then
re-add it as in Step 2), then run Step 3's command **three times** and
record the answers.

CHECK: you ran it ≥3× and can state how the behavior *distribution* shifted
versus Step 3 — more hedging, wrong numbers, or refusals mixed in. (You will
often STILL see `$80.00`: a single granted tool whose *name* already says
`estimate_cost` is an easy target, so the model leans on the name. The
docstring's pull is real but partial when the name and grant already point
the way — which is exactly why it matters most when many tools compete.)
Concept: the description IS the interface — names, docstrings, arg docs, and
error text are the only things the model reads to route, and they're
engineering surface, not documentation. And because the effect is
probabilistic, you measure it over runs (Lab 5), never from one glance.

### Step 5 — Repair and harden
Restore the good docstring, re-add the server. The error path already
returns a helpful string (`unknown model 'gemini'; known: haiku, sonnet,
opus`) — first see it deterministically, then watch the agent read it:

```bash
# deterministic: the exact string the model will receive
python3 -c "import costs_mcp; print(costs_mcp.estimate_cost('gemini', 1))"
# live: force the call so the error path fires, and see the agent obey it
echo "Call the estimate_cost tool for model 'gemini' with million_tokens 1, and report exactly what it returns." \
  | claude -p --model haiku --allowedTools "mcp__course-costs__estimate_cost"
```

CHECK: the direct call prints `unknown model 'gemini'; known: haiku,
sonnet, opus`, and the agent relays that message and tells you which models
ARE valid — it read your error as an instruction instead of crashing.
Concept: agents read error messages as instructions. Write errors for the
model (say what to do next), not for a stack trace. (Note we had to *tell*
the model to call the tool — for an out-of-domain model like "gemini" it
otherwise answers from its own priors; forcing the call is what exercises
the error path.)

### Step 6 — Clean up
```bash
claude mcp remove course-costs
```
CHECK: `claude mcp list` no longer shows it.
Concept: tool surface should be curated per project — every registered tool
costs context tokens and adds a routing decision.

## Recap

### L2-R1
Q: You changed only a docstring — not a line of code — and the behavior distribution shifted. Explain why, in harness terms.
Key:
- The model selects and drives tools from their machine-readable descriptions (name, docstring, arg docs — that's all it sees at routing time)
- Tool descriptions are part of the context/interface layer of the harness, so they are engineering surface, not documentation (and the effect is probabilistic — measured over runs, strongest when tools compete)

### L2-R2
Q: Give two properties of a well-engineered agent tool besides "the code works".
Key:
- Any two of: unambiguous purpose vs neighboring tools; description written for model routing; error messages that tell the model what to do next; token-efficient output

## Theory

Anthropic's *Writing tools for agents* argues the most common failure mode
is a bloated or ambiguous tool set: if a human can't say which tool applies,
the model can't either. Tools compete for the model's attention budget, so
fewer, sharper tools beat many overlapping ones; outputs should be concise
because they land in the context window. The MCP architecture (Day 2
whitepaper, "The Vibe Coder's View of MCP") splits the N×M integration
problem into N+M by making every tool self-describing — which is exactly why
the docstring, not the code, controlled behavior in Step 4.
Deep dives: `resources/links.md` → Writing tools for agents; Day 2
whitepaper; MCP docs.
