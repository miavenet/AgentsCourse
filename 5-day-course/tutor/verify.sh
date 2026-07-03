#!/usr/bin/env bash
# verify.sh — fact-check the tutor lessons against the source whitepapers.
# The tutor is recall-based (no commands to run), so its "CHECK" is that every
# statistic, figure caption, and section heading a lesson card cites still
# resolves to the actual whitepaper. This makes that verification repeatable —
# run it after any whitepaper is re-fetched/re-enhanced.
#
# All checks are deterministic greps (no model calls). Add --links to also curl
# the "Go deeper" URLs (network).
#
# Usage:
#   bash 5-day-course/tutor/verify.sh
#   bash 5-day-course/tutor/verify.sh --links
# Exit code = number of failed checks (0 = all green). Logs to verify.log.
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
C="$ROOT/5-day-course"
LOG="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/verify.log"
LINKS=0; [ "${1:-}" = "--links" ] && LINKS=1
ts() { date '+%Y-%m-%d %H:%M:%S'; }
PASS=0; FAIL=0
D1="$C/day1-intro-agents-and-vibe-coding/whitepaper-the-new-sdlc-with-vibe-coding.md"
D2="$C/day2-agent-tools-and-interoperability/whitepaper-agent-tools-and-interoperability.md"
D3="$C/day3-agent-skills/whitepaper-agent-skills.md"
D4="$C/day4-agent-security-and-evaluation/whitepaper-vibe-coding-agent-security-and-evaluation.md"
D5="$C/day5-spec-driven-production/whitepaper-spec-driven-production-grade-development.md"

# has <file> <regex> <label> — assert the whitepaper contains a match.
has() {
  if [ -f "$1" ] && grep -qiE "$2" "$1"; then
    printf '  \033[32mPASS\033[0m  %s\n' "$3"; echo "$(ts)  PASS  $3" >>"$LOG"; PASS=$((PASS+1))
  else
    printf '  \033[31mFAIL\033[0m  %s\n' "$3"; echo "$(ts)  FAIL  $3" >>"$LOG"; FAIL=$((FAIL+1))
  fi
}

echo "verify.sh — tutor fact-check (links=$LINKS)"; echo "$(ts)  === run start ===" >>"$LOG"

echo "Day 1 — statistics & figures:"
has "$D1" "85%[^.]*developers"                     "D1 stat: 85% of developers"
has "$D1" "51%[^.]*daily"                          "D1 stat: 51% daily"
has "$D1" "41%[^.]*new code"                       "D1 stat: 41% of new code"
has "$D1" "Figure 2:[^*]*Agent Loop"               "D1 fig2 = Agent Loop"
has "$D1" "Figure 4:[^*]*Context Engineering"      "D1 fig4 = Context Engineering"
has "$D1" "Figure 7:[^*]*Harness"                  "D1 fig7 = Harness Anatomy"
has "$D1" "Figure 8:[^*]*Conductor"                "D1 fig8 = Conductor vs Orchestrator"
has "$D1" "Figure 9:[^*]*Economics"                "D1 fig9 = Economics"

echo "Day 2 — figures & headings:"
has "$D2" "Figure 1:[^*]*Ecosystem"                "D2 fig1 = Protocol Ecosystem"
has "$D2" "Figure 2:[^*]*(Onboarding|MCP)"         "D2 fig2 = Onboarding an MCP Server"
has "$D2" "Figure 8:[^*]*(AP2|UCP)"                "D2 fig8 = AP2/UCP"
has "$D2" "Vibe Coder.s View of MCP"               "D2 heading: Vibe Coder's View of MCP"

echo "Day 3 — statistics & figures:"
has "$D3" "56%[^.]*non-invocation|non-invocation[^.]*56%" "D3 stat: 56% non-invocation"
has "$D3" "58%"                                    "D3 stat: 58% (stripped skill)"
has "$D3" "without the skill scored 63%"           "D3 stat: 63% (no-skill baseline)"
has "$D3" "100% pass rate against a 53% baseline"  "D3 stat: 100% vs 53% (AGENTS.md)"
has "$D3" "Figure 7:[^*]*Context rot"              "D3 fig7 = Context rot"
has "$D3" "Figure 2:[^*]*(routing|metadata|gatekeeping)" "D3 fig2 = progressive disclosure"

echo "Day 4 & 5 — figures & headings:"
has "$D4" "Figure 1:[^*]*Secure"                   "D4 fig1 = Secure Vibe Coding Framework"
has "$D4" "7-Pillar Agent Security Architecture"   "D4 heading: 7-Pillar Architecture"
has "$D4" "Red, Blue, and Green"                   "D4 heading: Red/Blue/Green teaming"
has "$D5" "Figure 1:[^*]*Code Review Runtime"      "D5 fig1 = Custom Code Review Runtime"
has "$D5" "Zero-Trust Development"                 "D5 heading: Zero-Trust Development"

if [ "$LINKS" = 1 ]; then
  echo "Go-deeper links (200 expected):"
  command -v curl >/dev/null || { echo "  (curl unavailable)"; }
  while read -r url; do
    [ -z "$url" ] && continue
    code=$(curl -sL -o /dev/null -w "%{http_code}" --max-time 20 "$url" 2>/dev/null)
    lbl="link $url"
    if [ "$code" = "200" ]; then printf '  \033[32mPASS\033[0m  %s\n' "$lbl"; echo "$(ts)  PASS  $lbl" >>"$LOG"; PASS=$((PASS+1))
    else printf '  \033[31mFAIL\033[0m  %s (%s)\n' "$lbl" "$code"; echo "$(ts)  FAIL  $lbl ($code)" >>"$LOG"; FAIL=$((FAIL+1)); fi
  done < <(grep -rhoE 'https?://[^ )]+' "$C"/tutor/lessons/*.md | sed 's/[.,]$//' | sort -u)
fi

echo "----------------------------------------"
echo "verify.sh: $PASS passed, $FAIL failed"
echo "$(ts)  === run done: $PASS pass / $FAIL fail ===" >>"$LOG"
exit "$FAIL"
