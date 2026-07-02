# Harness Engineering — Curated Resources

The theory layer for the labs. Everything here is free. Items marked
**[local]** are in this repo.

## Primary texts

- **[local]** Day-1 whitepaper, "Harness Engineering: What surrounds the model" —
  `5-day-course/day1-intro-agents-and-vibe-coding/whitepaper-the-new-sdlc-with-vibe-coding.md`
  (the section this whole module grew from; figures 6–7 show harness anatomy)
- Anthropic — *Building effective agents*:
  https://www.anthropic.com/engineering/building-effective-agents
  (workflow vs agent patterns; when NOT to build an agent)
- Anthropic — *Effective context engineering for AI agents*:
  https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
  (attention budget, curation, compaction — the theory behind Lab 3)
- Anthropic — *Writing tools for agents*:
  https://www.anthropic.com/engineering/writing-tools-for-agents
  (tool ergonomics — the theory behind Lab 2)
- Anthropic — *How we built our multi-agent research system*:
  https://www.anthropic.com/engineering/multi-agent-research-system
  (orchestration + eval lessons from a production harness)
- Claude Cookbook — context engineering recipes (memory, compaction, tool clearing):
  https://platform.claude.com/cookbook/tool-use-context-engineering-context-engineering-tools

## Whitepapers / papers **[local]** in `resources/papers/`

- *A Survey on Evaluation of LLM-based Agents* (arXiv 2503.16416) —
  taxonomy of what/how to evaluate; backs Lab 5
- *Evaluation and Benchmarking of LLM Agents: A Survey* (arXiv 2507.21504)
- *A Survey of Vibe Coding with Large Language Models* (arXiv 2510.12399)

## Talks & transcripts

- Andrej Karpathy — *From Vibe Coding to Agentic Engineering* (Sequoia AI
  Ascent 2026): https://www.youtube.com/watch?v=96jN2OCOfLs
  (why the discipline is coordinating fallible agents while preserving quality)
- **[local]** Course Day-1 livestream transcript —
  `resources/transcripts/day1-livestream.txt`
- **[local]** Course Day-1 podcast transcript —
  `resources/transcripts/day1-podcast.txt`

## Reference docs (for during the labs)

- Claude Code docs (hooks, settings, MCP, headless mode):
  https://docs.claude.com/en/docs/claude-code/overview
- MCP official docs: https://modelcontextprotocol.io/docs/getting-started/intro
- Google ADK docs (another production harness to compare against):
  https://adk.dev/ (formerly google.github.io/adk-docs)

## Curated lists (rabbit holes, post-course)

- awesome-harness-engineering: https://github.com/ai-boost/awesome-harness-engineering
- awesome-evals: https://github.com/benchflow-ai/awesome-evals
