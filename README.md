# 5-Day AI Agents: Intensive Vibe Coding Course (Google × Kaggle)

Self-paced materials for the June 15–19, 2026 course, fetched and organized locally.

- **Learn guide:** https://www.kaggle.com/learn-guide/5-day-agents-vibecoding
- **Course home:** https://www.kaggle.com/competitions/5-day-ai-agents-intensive-vibecoding-course-with-google
- **Capstone (Kaggriculture):** https://www.kaggle.com/competitions/vibecoding-agents-capstone-project — ⚠️ live hackathon, ~5 days left as of 2026-07-02

Hosts for all livestreams: Anant Nawalgaria and Smitha Kolan, on Kaggle's YouTube channel.

## Layout

Each `dayN-*/` folder contains the day's **whitepaper PDF**, offline **codelab HTML copies**, and a `resources.md` with all links (podcast, codelabs, livestream, guests).

| Day | Topic | Folder |
|-----|-------|--------|
| 1 | Introduction to Agents & Vibe Coding | `day1-intro-agents-and-vibe-coding/` |
| 2 | Agent Tools & Interoperability (MCP, A2A, A2UI, AP2/UCP) | `day2-agent-tools-and-interoperability/` |
| 3 | Agent Skills (SKILL.md, progressive disclosure) | `day3-agent-skills/` |
| 4 | Vibe Coding Agent Security & Evaluation | `day4-agent-security-and-evaluation/` |
| 5 | Spec-Driven Production Grade Development | `day5-spec-driven-production/` |
| — | Capstone project | `capstone/` |

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

Each `dayN-*/` folder contains the whitepaper as **PDF** and as **enhanced markdown** (`whitepaper-*.md`) with real headings, a rebuilt table of contents, and every figure/table embedded as a PNG under `assets/`. Codelabs are saved as offline HTML plus readable markdown.

To regenerate a whitepaper markdown (e.g. after a PDF update):

```bash
pip install -r tools/requirements.txt   # markitdown[pdf] + pymupdf
python tools/enhance_whitepaper.py dayN-…/whitepaper-….pdf
```

The script converts with markitdown, strips per-page header/footer noise, promotes headings from the PDF bookmark outline, renders figure/table regions to PNGs, validates any ```mermaid blocks with `mmdc`, and prints a sanity report.

## Key tools used in the course

- **Antigravity 2.0** (IDE + CLI) — Google's agentic coding environment, used throughout
- **Google AI Studio** + **Cloud Run** — build and deploy vibe-coded apps
- **ADK (Agent Development Kit)** + **Agents CLI** — agent construction and lifecycle
- **MCP (Model Context Protocol)** — tool/data interoperability
