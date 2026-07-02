# 5-Day AI Agents: Intensive Vibe Coding Course (Google × Kaggle)

Self-paced materials for the June 15–19, 2026 course, fetched and organized locally.

- **Learn guide:** https://www.kaggle.com/learn-guide/5-day-agents-vibecoding
- **Course home:** https://www.kaggle.com/competitions/5-day-ai-agents-intensive-vibecoding-course-with-google
- **Capstone (Kaggriculture):** https://www.kaggle.com/competitions/vibecoding-agents-capstone-project — ⚠️ live hackathon, ~5 days left as of 2026-07-02

Hosts for all livestreams: Anant Nawalgaria and Smitha Kolan, on Kaggle's YouTube channel.

## Repository layout

- **`5-day-course/`** — the course itself: the five `dayN-*/` material folders
  (whitepapers + codelabs), the `capstone/`, the `tutor/` study system, and the
  whitepaper `tools/`.
- **`harness-eng/`** — a separate, self-contained hands-on module (`/harness`).
- **`agent-ops/`** — a separate, self-contained hands-on module (`/agentops`).
- **`RIGOR.md`** — the repo-wide quality rubric; **`scripts/hooks/`** — the
  permission-noise hook; **`.claude/`** — settings + slash commands.

## The 5-day course

Each `5-day-course/dayN-*/` folder contains the day's **whitepaper PDF**, offline **codelab HTML copies**, and a `resources.md` with all links (podcast, codelabs, livestream, guests).

| Day | Topic | Folder |
|-----|-------|--------|
| 1 | Introduction to Agents & Vibe Coding | `5-day-course/day1-intro-agents-and-vibe-coding/` |
| 2 | Agent Tools & Interoperability (MCP, A2A, A2UI, AP2/UCP) | `5-day-course/day2-agent-tools-and-interoperability/` |
| 3 | Agent Skills (SKILL.md, progressive disclosure) | `5-day-course/day3-agent-skills/` |
| 4 | Vibe Coding Agent Security & Evaluation | `5-day-course/day4-agent-security-and-evaluation/` |
| 5 | Spec-Driven Production Grade Development | `5-day-course/day5-spec-driven-production/` |
| — | Capstone project | `5-day-course/capstone/` |

## Study tutor

`5-day-course/tutor/` contains an adaptive, spaced-repetition study system for the whole
course, built on learning-science principles (see `5-day-course/tutor/PRINCIPLES.md`)
and runnable by any Claude model — launch with `/tutor` inside Claude Code
(`claude --model haiku` is sufficient). Progress lives in
`5-day-course/tutor/progress.md`; commit it after each session to track your journey.

## Harness engineering module

`harness-eng/` is a hands-on companion module: five practical labs
(dissect Claude Code, build an MCP server, measure context rot, write
guardrail hooks, build an eval harness) plus a from-scratch agent-harness
workshop. Launch with `/harness`. Theory on demand in
`harness-eng/resources/`.

## Agents-in-production module

`agent-ops/` is the operations companion: five hands-on labs (SLOs for a
non-deterministic system, observability & the Vibe Trajectory, eval-gated
CI/CD with canary rollback, red-team-then-guardrail safeguards, incident
drills) plus a workshop that wraps the `harness-eng` Pocket-Agent into a
full **agent-as-a-service** (HTTP endpoint, health/kill switch, guardrails,
eval gate, canary, metrics, incident drill). Launch with `/agentops`.
Best-of-best reading in `agent-ops/resources/FURTHER-READING.md`.

## Quality bar (RIGOR.md)

`RIGOR.md` is this repo's scoring rubric for every learning artifact
(tutorials, labs, workshops, coach protocols). It encodes the standing
constraint — **maximum durable learning per hour** — into weighted
categories (accuracy, learning-science efficacy, hands-on verifiability,
Haiku-drivability, economy, safety) with hard gates. Modules target
≥95/100 with zero blockers; the load-bearing rule is that every command a
learner runs and every CHECK they're graded on has been executed against
the real tool.

## Reducing permission noise (and self-checking the labs)

The labs run many shell commands (`claude -p` calls, `grep`, `python3`,
`mkdir`, `mcp add/remove` …). To avoid a permission prompt on every one,
`.claude/settings.json` wires a **PreToolUse hook**,
`scripts/hooks/bash_guard.py`, that auto-**allows** provably-safe commands
(read-only, or writes/deletes confined to this repo, `/tmp`, or `/dev/null`),
forces **ask** on anything that mutates outside the repo / can't be bounded /
reads a secret path / `git push`, and **denies** a small catastrophic set
(`rm -rf /`, `mkfs`, `dd of=/dev/…`). It fails open — any parse error passes
through to the normal prompt, so it can't break or silently approve a call.

`harness-eng/verify.sh` is the module's evaluation harness: it runs each
lab's canonical command through one noise-reduced `ask()` wrapper (stdin
prompt + explicit tool policy) and asserts the expected output.
`bash harness-eng/verify.sh` (fast) or `--full` (adds the Lab 5 eval and Lab
2 MCP round-trip); exit code = number of failed checks.

## Recommended daily flow

1. Listen to the summary **podcast** (link in the day's `resources.md`).
2. Read the **whitepaper** (local PDF).
3. Complete the two **codelabs** (offline HTML for reference; do them live at the linked URLs).
4. Optionally watch the recorded **livestream**.

## Quick links

| Day | Podcast | Whitepaper (Kaggle) | Livestream |
|-----|---------|---------------------|------------|
| 1 | [▶︎](https://www.youtube.com/watch?v=cbzmr7vt4XA) | [The New SDLC with Vibe Coding](https://www.kaggle.com/whitepaper-the-new-SDLC-with-vibe-coding) | [▶︎](https://youtube.com/live/7iic3Zj427M) |
| 2 | [▶︎](https://www.youtube.com/watch?v=GjjKXqxFTOY) | [Agent Tools & Interoperability](https://www.kaggle.com/whitepaper-agent-tools-and-interoperability) | [▶︎](https://www.youtube.com/live/PGI_S59EoRA) |
| 3 | [▶︎](https://www.youtube.com/watch?v=uYURYHhpmKc) | [Agent Skills](https://www.kaggle.com/whitepaper-agent-skills) | [▶︎](https://www.youtube.com/live/1T2mxYZkqL0) |
| 4 | [▶︎](https://www.youtube.com/watch?v=Ddz1b8CYPvg) | [Vibe Coding Agent Security and Evaluation](https://www.kaggle.com/whitepaper-vibe-coding-agent-security-and-evaluation) | [▶︎](https://www.youtube.com/live/suWoYLD7uGY) |
| 5 | [▶︎](https://www.youtube.com/watch?v=VSRdL4wlbLY) | [Spec-Driven Production Grade Development](https://www.kaggle.com/whitepaper-spec-driven-production-grade-development-in-the-age-of-vibe-coding) | [▶︎](https://www.youtube.com/live/Y3HfV4IroCU) |

## Local files & tooling

Each `5-day-course/dayN-*/` folder contains the whitepaper as **PDF** and as **enhanced markdown** (`whitepaper-*.md`) with real headings, a rebuilt table of contents, and every figure/table embedded as a PNG under `assets/`. Codelabs are saved as offline HTML plus readable markdown.

To regenerate a whitepaper markdown (e.g. after a PDF update):

```bash
pip install -r 5-day-course/tools/requirements.txt   # markitdown[pdf] + pymupdf
python 5-day-course/tools/enhance_whitepaper.py 5-day-course/dayN-…/whitepaper-….pdf
```

The script converts with markitdown, strips per-page header/footer noise, promotes headings from the PDF bookmark outline, renders figure/table regions to PNGs, validates any ```mermaid blocks with `mmdc`, and prints a sanity report.

## Key tools used in the course

- **Antigravity 2.0** (IDE + CLI) — Google's agentic coding environment, used throughout
- **Google AI Studio** + **Cloud Run** — build and deploy vibe-coded apps
- **ADK (Agent Development Kit)** + **Agents CLI** — agent construction and lifecycle
- **MCP (Model Context Protocol)** — tool/data interoperability
