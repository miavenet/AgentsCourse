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

PRICES = {"haiku": 1.0, "sonnet": 3.0, "opus": 15.0}

@mcp.tool()
def estimate_cost(model: str, million_tokens: float) -> str:
    """Estimate USD cost for a model run given input size in millions of tokens."""
    p = PRICES.get(model.lower())
    if p is None:
        return f"unknown model '{model}'; known: {', '.join(PRICES)}"
    return f"${p * million_tokens:.2f}"

if __name__ == "__main__":
    mcp.run()
```

Install the SDK and smoke-test the import:
```bash
python3 -m pip install --user "mcp[cli]" 2>/dev/null || pip3 install "mcp[cli]"
python3 -c "import mcp; print('sdk ok')"
```

CHECK: `sdk ok`.
Concept: an MCP server is just a process that describes and serves tools —
20 lines is a real one.

### Step 2 — Plug it into the harness
```bash
cd harness-eng/scratch
claude mcp add course-costs -- python3 $(pwd)/costs_mcp.py
claude mcp list
```

CHECK: `course-costs` appears in the list.
Concept: discovery→configuration→connection (Day 2's consumer flow) — you
just did all three from the producer side.

### Step 3 — Watch the agent choose your tool
```bash
claude -p --model haiku \
  "What would 2 million tokens cost on opus? Use available tools."
```

CHECK: the answer is $30.00 and the transcript shows a call to
`estimate_cost` (rerun with `--output-format json` and look for the tool
name if unsure).
Concept: the model discovered your tool purely from its machine-readable
self-description.

### Step 4 — Sabotage the description (not the code)
Edit ONLY the docstring in `costs_mcp.py` to something misleadingly vague:
`"""Internal accounting helper."""` — leave the code identical. Then rerun
Step 3's prompt.

CHECK: behavior degrades — the agent may not call the tool, may guess, or
answers without it. (If it still calls it, make the description worse:
`"""Do not use."""` and rerun.)
Concept: the description IS the interface. Tool ergonomics — names,
descriptions, error text — are prompt engineering that lives in the harness.

### Step 5 — Repair and harden
Restore a good docstring, but now also improve the *error path*: change the
unknown-model return to include what the caller should do next
(e.g. "call again with one of: haiku, sonnet, opus"). Test:

```bash
claude -p --model haiku \
  "What would 1 million tokens cost on gemini? Use available tools."
```

CHECK: the agent recovers gracefully — it either reports the known models or
asks you to pick one, instead of erroring out.
Concept: agents read error messages as instructions. Write errors for the
model, not for a stack trace.

### Step 6 — Clean up
```bash
claude mcp remove course-costs
```
CHECK: `claude mcp list` no longer shows it.
Concept: tool surface should be curated per project — every registered tool
costs context tokens and adds a routing decision.

## Recap

### L2-R1
Q: You changed only a docstring and agent behavior broke. Explain why, in harness terms.
Key:
- The model selects tools from their machine-readable descriptions (that's all it sees at routing time)
- Tool descriptions are part of the context/interface layer of the harness, so they are engineering surface, not documentation

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
