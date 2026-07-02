#!/usr/bin/env bash
# drill.sh — arm ONE incident for a blind drill. In a coached session the
# COACH runs `bash drill.sh <id>` and tells the learner only the SYMPTOM;
# the learner diagnoses from /healthz, metrics.py and service_log.jsonl
# WITHOUT reading this file. `bash drill.sh restore` reverts everything.
# Solo? Have someone else pick the id, or accept that the skill being
# trained is the diagnosis path, not the whodunit.
#
# The breaks are chosen to be RELIABLE (Haiku resists prompt-appended
# "degradations", so drill 1 deploys a genuinely regressive prompt version
# and drill 2 breaks a real dependency — neither relies on the model
# obeying a self-sabotaging instruction).
set -e
GOOD='Be concise; result is one factual sentence.'
case "$1" in
  1) # silent quality regression: deploy a prompt that spells numbers as
     # words — the service still returns 200s, but numeric answers are wrong
     printf 'Always express any number in the result as an English word, never a digit.\n' > prompts/v2.txt
     printf 'v2\n' > active_version
     echo "SYMPTOM: users report the agent 'feels dumber' since this morning." ;;
  2) # dependency outage: the data dir the read tool needs is unreadable
     chmod 000 data
     echo "SYMPTOM: requests are erroring intermittently." ;;
  3) # confabulation: no sabotage — the agent may misreport a blocked action
     echo "SYMPTOM: the agent says it completed a destructive action — verify it." ;;
  restore)
     printf '%s\n' "$GOOD" > prompts/v1.txt
     printf 'v1\n' > active_version
     chmod 755 data 2>/dev/null || true
     rm -f KILL
     echo "restored: active_version=v1, data readable, kill switch cleared." ;;
  *) echo "usage: bash drill.sh {1|2|3|restore}" >&2; exit 2 ;;
esac
