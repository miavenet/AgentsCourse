#!/usr/bin/env bash
# verify.sh — RIGOR self-check / evaluation harness for the harness-eng module.
# Runs each lab's canonical checkable command against the live `claude` CLI and
# asserts the expected output, so you can confirm the whole module still works
# on your CLI version in ~1 minute.
#
# The point of this script is PERMISSION-NOISE REDUCTION. Every model call goes
# through one wrapper, `ask()`, which:
#   - pipes the prompt via STDIN (an empty --allowedTools value swallows a
#     positional prompt on current CLIs; stdin sidesteps that),
#   - passes EXPLICIT tool policy (`--disallowedTools '*'` to deny all, or
#     `--allowedTools '<tool>'` to grant one) so a headless run never has to
#     prompt for permission or emit "Ignoring rule / permission denied" spam,
#   - silences expected stderr.
# Reuse `ask()` as the copy-paste pattern for quiet, reproducible agent calls.
#
# Usage:
#   bash harness-eng/verify.sh            # fast checks (3 model calls, ~40s)
#   bash harness-eng/verify.sh --full     # also run the Lab 5 eval + Lab 2 MCP
#   MODEL=sonnet bash harness-eng/verify.sh
# Exit code is the number of failed checks (0 = all green). Logs to verify.log.
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HE="$ROOT/harness-eng"
LOG="$HE/verify.log"
MODEL="${MODEL:-haiku}"
FULL=0; [ "${1:-}" = "--full" ] && FULL=1
WORK="$(mktemp -d)"; trap 'rm -rf "$WORK"' EXIT
ts() { date '+%Y-%m-%d %H:%M:%S'; }

PASS=0; FAIL=0
log() { echo "$(ts)  $*" >>"$LOG"; }

# ask "<prompt>" [claude flags...] — quiet, reproducible, no permission prompts.
ask() { local prompt="$1"; shift; printf '%s' "$prompt" | claude -p --model "$MODEL" "$@" 2>/dev/null; }

# pass_if_match <name> <regex> <text>  /  fail_if_match <name> <regex> <text>
pass_if_match() {
  if grep -qiE "$2" <<<"$3"; then printf '  \033[32mPASS\033[0m  %s\n' "$1"; log "PASS $1"; PASS=$((PASS+1))
  else printf '  \033[31mFAIL\033[0m  %s  (got: %.70s)\n' "$1" "${3//$'\n'/ }"; log "FAIL $1 :: ${3//$'\n'/ }"; FAIL=$((FAIL+1)); fi
}
fail_if_match() {   # passes when the regex is ABSENT (e.g. secret NOT leaked)
  if grep -qiE "$2" <<<"$3"; then printf '  \033[31mFAIL\033[0m  %s  (unexpected: %.60s)\n' "$1" "${3//$'\n'/ }"; log "FAIL $1"; FAIL=$((FAIL+1))
  else printf '  \033[32mPASS\033[0m  %s\n' "$1"; log "PASS $1"; PASS=$((PASS+1)); fi
}

command -v claude >/dev/null || { echo "claude CLI not on PATH"; exit 2; }
echo "verify.sh — harness-eng (model=$MODEL, full=$FULL)"; log "=== run start (model=$MODEL full=$FULL) ==="

# --- Lab 1: capability lives in the harness ----------------------------------
echo "Lab 1 — tools are the harness:"
printf 'banana47\n' > "$WORK/secret.txt"
Q="Read the file secret.txt and reply with only the word inside it."
( cd "$WORK" && ask "$Q" --disallowedTools "*" ) > "$WORK/o1a"
fail_if_match "L1 deny-all: model cannot read the secret" "banana47" "$(cat "$WORK/o1a")"
( cd "$WORK" && ask "$Q" --allowedTools "Read" ) > "$WORK/o1b"
pass_if_match "L1 grant Read: model returns the secret" "banana47" "$(cat "$WORK/o1b")"

# --- Lab 4: deny-by-default protects the file --------------------------------
echo "Lab 4 — permission policy:"
printf 'victim\n' > "$WORK/precious.txt"
( cd "$WORK" && ask "Delete precious.txt" --disallowedTools "*" ) >/dev/null
pass_if_match "L4 deny-all: precious.txt survives" "^victim$" "$(cat "$WORK/precious.txt")"

# --- Lab 5: the eval harness actually scores (optional) ----------------------
if [ "$FULL" = 1 ]; then
  echo "Lab 5 — eval runner:"
  ES="$WORK/eval"; mkdir -p "$ES"
  cat > "$ES/tasks.jsonl" <<'JSONL'
{"id":"t1","prompt":"What is 17 * 23? Reply with only the number.","expect_regex":"391"}
{"id":"t3","prompt":"Name the protocol that connects AI models to tools and data sources, standardized by Anthropic. One word/acronym only.","expect_regex":"MCP"}
JSONL
  # mirror run_eval.py's noise-reduced invocation: stdin prompt + deny tools
  score=0; for id in t1 t3; do
    p=$(python3 -c "import json,sys;[print(json.loads(l)['prompt']) for l in open('$ES/tasks.jsonl') if json.loads(l)['id']=='$id']")
    r=$(python3 -c "import json,sys;[print(json.loads(l)['expect_regex']) for l in open('$ES/tasks.jsonl') if json.loads(l)['id']=='$id']")
    a=$(ask "$p" --disallowedTools "*"); grep -qiE "$r" <<<"$a" && score=$((score+1))
  done
  pass_if_match "L5 eval scores >=1/2 on the golden tasks" "^[12]$" "$score"
fi

# --- Lab 2: MCP round-trip (optional; needs a venv + the SDK) -----------------
if [ "$FULL" = 1 ]; then
  echo "Lab 2 — MCP tool call:"
  MS="$WORK/mcp"; mkdir -p "$MS"
  if python3 -m venv "$MS/.venv" && "$MS/.venv/bin/pip" install -q "mcp[cli]" 2>/dev/null; then
    cat > "$MS/costs_mcp.py" <<'PY'
from mcp.server.fastmcp import FastMCP
mcp = FastMCP("course-costs")
PRICES = {"haiku": 2.0, "sonnet": 6.0, "opus": 40.0}
@mcp.tool()
def estimate_cost(model: str, million_tokens: float) -> str:
    """Estimate this course's internal USD cost for a model run given input size in millions of tokens."""
    p = PRICES.get(model.lower())
    return f"unknown model '{model}'" if p is None else f"${p * million_tokens:.2f}"
if __name__ == "__main__":
    mcp.run()
PY
    claude mcp remove course-costs >/dev/null 2>&1
    claude mcp add course-costs -- "$MS/.venv/bin/python3" "$MS/costs_mcp.py" >/dev/null 2>&1
    a=$(ask "Using the available tools, what is this course's internal cost for 2 million tokens on opus? Reply with the dollar amount." \
          --allowedTools "mcp__course-costs__estimate_cost")
    pass_if_match "L2 MCP tool returns fictional \$80.00 (proves a real call)" '\$?80(\.00)?' "$a"
    claude mcp remove course-costs >/dev/null 2>&1
  else
    printf '  \033[33mSKIP\033[0m  L2 MCP (could not build venv / install mcp)\n'; log "SKIP L2 MCP"
  fi
fi

echo "----------------------------------------"
echo "verify.sh: $PASS passed, $FAIL failed"
log "=== run done: $PASS pass / $FAIL fail ==="
exit "$FAIL"
