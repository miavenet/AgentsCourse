#!/usr/bin/env bash
# verify.sh — RIGOR self-check / evaluation harness for the agent-ops module.
# Exercises the workshop's own machinery (the reference solution) against the
# live `claude` CLI and asserts the expected behavior, so you can confirm the
# module still works on your CLI version.
#
# Fast mode is deterministic + one model smoke (~30s): script syntax, the
# metrics.py SLO exit-code gate, and a pocket-agent arithmetic call.
# --full adds the model-heavy pipeline: eval gate rejects a regression, canary
# rolls back, and the HTTP service's health + kill switch.
#
# Usage:
#   bash agent-ops/verify.sh            # fast checks
#   bash agent-ops/verify.sh --full     # + gate/canary/service (many model calls, ~4min)
# Exit code = number of failed checks (0 = all green). Logs to verify.log.
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
AO="$ROOT/agent-ops"
SOL="$AO/workshop/solution"
POCKET="$ROOT/harness-eng/workshop/solution/pocket_agent.py"
LOG="$AO/verify.log"
MODEL="${MODEL:-haiku}"
FULL=0; [ "${1:-}" = "--full" ] && FULL=1
WORK="$(mktemp -d)"; trap 'rm -rf "$WORK"' EXIT
ts() { date '+%Y-%m-%d %H:%M:%S'; }
PASS=0; FAIL=0
log() { echo "$(ts)  $*" >>"$LOG"; }
ok()  { printf '  \033[32mPASS\033[0m  %s\n' "$1"; log "PASS $1"; PASS=$((PASS+1)); }
no()  { printf '  \033[31mFAIL\033[0m  %s  (%.70s)\n' "$1" "${2//$'\n'/ }"; log "FAIL $1 :: ${2//$'\n'/ }"; FAIL=$((FAIL+1)); }
skip(){ printf '  \033[33mSKIP\033[0m  %s\n' "$1"; log "SKIP $1"; }
match(){ grep -qiE "$2" <<<"$3" && ok "$1" || no "$1" "$3"; }

command -v claude >/dev/null || { echo "claude CLI not on PATH"; exit 2; }
[ -f "$POCKET" ] || { echo "pocket_agent.py missing — run the harness-eng workshop first"; exit 2; }
echo "verify.sh — agent-ops (model=$MODEL, full=$FULL)"; log "=== run start (model=$MODEL full=$FULL) ==="

# Stage a scratch workshop identical to the labs' setup.
cp "$POCKET" "$SOL"/{agent_service.py,metrics.py,gate.py,canary.py} "$WORK"/
mkdir -p "$WORK/prompts" "$WORK/data"
printf 'Be concise; result is one factual sentence.\n' > "$WORK/prompts/v1.txt"
printf 'Always express any number in the result as an English word, never a digit.\n' > "$WORK/prompts/v2.txt"
printf 'Be concise and precise; result is one factual sentence.\n' > "$WORK/prompts/v3.txt"
printf 'harness\n' > "$WORK/data/topic.txt"
for f in a b c; do printf '# %s\n' "$f" > "$WORK/data/$f.md"; done
printf 'v1\n' > "$WORK/active_version"

# --- Deterministic: syntax of every reference script -------------------------
echo "solution scripts:"
synbad=""
for f in agent_service.py metrics.py gate.py canary.py; do
  python3 -c "import ast; ast.parse(open('$WORK/$f').read())" 2>/dev/null || synbad="$synbad $f"
done
[ -z "$synbad" ] && ok "all four solution scripts parse" || no "solution scripts parse" "$synbad"

# --- Deterministic: metrics.py SLO exit code (the alerting mechanism) ---------
echo "metrics SLO gate:"
mklog(){ : > "$WORK/service_log.jsonl"; local v; for v in "$@"; do echo "$v" >> "$WORK/service_log.jsonl"; done; }
mklog '{"version":"v1","ok":false,"latency_s":1.0,"flags":[]}' \
      '{"version":"v1","ok":false,"latency_s":1.0,"flags":[]}' \
      '{"version":"v1","ok":false,"latency_s":1.0,"flags":[]}'
( cd "$WORK" && python3 metrics.py service_log.jsonl --slo-errors 0.2 >/dev/null 2>&1 ); \
  [ $? -eq 1 ] && ok "metrics exits 1 on SLO breach (100% errors)" || no "metrics SLO breach" "expected exit 1"
mklog '{"version":"v1","ok":true,"latency_s":1.0,"flags":[]}' \
      '{"version":"v1","ok":true,"latency_s":1.0,"flags":[]}'
( cd "$WORK" && python3 metrics.py service_log.jsonl --slo-errors 0.2 >/dev/null 2>&1 ); \
  [ $? -eq 0 ] && ok "metrics exits 0 when within SLO (0% errors)" || no "metrics within SLO" "expected exit 0"
rm -f "$WORK/service_log.jsonl"

# --- One model smoke: pocket-agent answers arithmetic ------------------------
echo "pocket-agent smoke:"
a=$( cd "$WORK" && python3 pocket_agent.py "What is 3 plus 4? Finish with just the number." 2>/dev/null )
match "pocket-agent returns 7" '\b7\b' "$a"
rm -f "$WORK/traces.jsonl"

if [ "$FULL" = 1 ]; then
  # --- Eval gate blocks a regression -----------------------------------------
  echo "eval gate:"
  ( cd "$WORK" && python3 gate.py v1 --baseline >/dev/null 2>&1 )
  g=$( cd "$WORK" && python3 gate.py v2 2>&1 ); grc=$?
  if [ $grc -ne 0 ] && [ "$(cat "$WORK/active_version")" = "v1" ]; then
    ok "gate FAILS the numbers-as-words v2 and keeps active_version=v1"
  else
    no "gate blocks v2 regression" "exit=$grc active=$(cat "$WORK/active_version") :: $g"
  fi

  # --- Canary rolls back a bad candidate -------------------------------------
  echo "canary rollback:"
  printf 'v1\n' > "$WORK/active_version"
  c=$( cd "$WORK" && python3 canary.py v2 --requests 4 --share 2 2>&1 )
  if grep -qi "ROLLBACK" <<<"$c" && [ "$(cat "$WORK/active_version")" = "v1" ]; then
    ok "canary rolls back v2 and keeps active_version=v1"
  else
    no "canary rollback" "active=$(cat "$WORK/active_version") :: $c"
  fi

  # --- Service health + kill switch ------------------------------------------
  echo "service health/kill:"
  ( cd "$WORK" && PORT=8077 python3 agent_service.py >/dev/null 2>&1 & echo $! > "$WORK/svc.pid" )
  sleep 2
  h=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8077/healthz 2>/dev/null)
  touch "$WORK/KILL"
  hk=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8077/healthz 2>/dev/null)
  rm -f "$WORK/KILL"
  kill "$(cat "$WORK/svc.pid")" 2>/dev/null
  if [ "$h" = "200" ] && [ "$hk" = "503" ]; then
    ok "healthz 200 when live, 503 with kill switch engaged"
  else
    no "service health/kill" "live=$h killed=$hk (expected 200 then 503)"
  fi
fi

echo "----------------------------------------"
echo "verify.sh: $PASS passed, $FAIL failed"
log "=== run done: $PASS pass / $FAIL fail ==="
exit "$FAIL"
