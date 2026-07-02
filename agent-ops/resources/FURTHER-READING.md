# Further Reading — best-of-the-best only

A deliberately short shelf. Each item earned its place by being the single
best public source on its topic — not a survey of everything, the few
things worth your scarce hours. Read top-down; stop when you've got what
you came for.

## If you read only three things

1. **Anthropic — Building Effective Agents** (Dec 2024)
   https://www.anthropic.com/engineering/building-effective-agents
   The vocabulary the whole field now shares: workflows vs. agents, the
   composable patterns, and "invest in the agent-computer interface." Start here.

2. **Simon Willison — The lethal trifecta for AI agents** (Jun 2025)
   https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/
   The one-page mental model that will stop you shipping an exfiltration
   bug: private data + untrusted content + external comms = danger. If you
   remember one security idea, this is it.

3. **Anthropic — Demystifying evals for AI agents** (Jan 2026)
   https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents
   Task / trial / grader / trajectory, and which eval belongs at which
   lifecycle stage. The clearest thinking on how to *know* your agent works.

## Deploy & operate

- **ADK — Deploying your agent** — https://adk.dev/deploy/ — the canonical
  Agent Engine vs. Cloud Run vs. GKE decision matrix; `adk deploy` in one line.
- **Vertex AI Agent Engine overview** —
  https://docs.cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/overview
  — managed runtime with Sessions + Memory Bank + Evaluation as first-class services.
- **Anthropic — How we built our multi-agent research system** (Jun 2025) —
  https://www.anthropic.com/engineering/multi-agent-research-system — the
  best public writeup on **rainbow deployments** and checkpointing for
  stateful, long-running agents.
- **12-Factor Agents** — https://github.com/humanlayer/12-factor-agents —
  the community architecture checklist; factors 5/6/8/12 = the resumable-
  service design. (Talk: https://www.youtube.com/watch?v=8kMaTybvDUw)
- **Building LangGraph: an agent runtime from first principles** (Sep 2025) —
  https://www.langchain.com/blog/building-langgraph — the six capabilities a
  real agent runtime must provide (checkpointing, HITL interrupt/resume, queues…).

## Evals & CI/CD

- **Hamel Husain & Shreya Shankar — LLM Evals FAQ** (updated Jan 2026) —
  https://hamel.dev/blog/posts/evals-faq/ — the most practical guidance on
  eval-gated CI and LLM-as-judge calibration. Pair with the foundational
  https://hamel.dev/blog/posts/evals/ and https://hamel.dev/blog/posts/llm-judge/.
- **Google — Agent Starter Pack** — https://github.com/GoogleCloudPlatform/agent-starter-pack
  — official, open, end-to-end eval-instrumented CI/CD for agents on GCP.
  (Maintenance mode; successor is `agents-cli`, the Day-5 tool — still the best reference.)
- **OpenAI — Eval-Driven System Design cookbook** —
  https://developers.openai.com/cookbook/examples/partners/eval_driven_system_design/receipt_inspection
  — a full worked prototype→production example with cost trade-offs.

## Observability & Day-2 ops

- **OpenTelemetry GenAI semantic conventions** —
  https://opentelemetry.io/docs/specs/semconv/gen-ai/ (canonical repo:
  https://github.com/open-telemetry/semantic-conventions-genai) — the
  vendor-neutral `gen_ai.*` schema everything converges on.
- **Langfuse — Evaluation docs** — https://langfuse.com/docs/evaluation/overview
  — the best self-hostable traces + online-evals + dashboards, with real
  conceptual docs (not marketing). Arize **Phoenix** is the OSS alternative:
  https://arize.com/docs/phoenix.
- **Applying SRE to Autonomous AI Agents (Microsoft)** —
  https://techcommunity.microsoft.com/blog/linuxandopensourceblog/applying-site-reliability-engineering-to-autonomous-ai-agents/4521357
  — error budgets, burn-rate alerts, and tiered response for agents.

## Incidents worth internalizing

- **Anthropic — A postmortem of three recent issues** (Sep 2025) —
  https://www.anthropic.com/engineering/a-postmortem-of-three-recent-issues
  — quality degraded while "all classic dashboards stayed green." The
  canonical silent-quality-incident story. (Follow-up on config compounding:
  https://www.anthropic.com/engineering/april-23-postmortem.)
- **The Replit agent database-deletion incident** (Jul 2025) —
  https://codenotary.com/blog/when-ai-goes-rogue-the-replit-incident-and-its-lessons
  — the defining "agent went rogue and lied about it" case. Every guardrail
  lesson in Lab 4/5 traces back to this.

## Security defenses (beyond the trifecta)

- **CaMeL — Defeating Prompt Injections by Design** — https://arxiv.org/abs/2503.18813
  — the strongest "defense by design, not detection" result (in papers/).
- **Design Patterns for Securing LLM Agents against Prompt Injections** —
  https://arxiv.org/abs/2506.08837 — six named, reusable defense patterns (in papers/).
- **Anthropic — Claude Code sandboxing** (Oct 2025) —
  https://www.anthropic.com/engineering/claude-code-sandboxing (OSS:
  https://github.com/anthropic-experimental/sandbox-runtime) — production
  filesystem + network + credential isolation you can actually run.
- **OWASP** — Top 10 for LLM Apps 2025 (https://genai.owasp.org/llm-top-10/)
  and Agentic AI Threats & Mitigations
  (https://genai.owasp.org/resource/agentic-ai-threats-and-mitigations/) —
  the shared threat vocabularies. Skim once; keep as reference.

## Papers on the shelf (`papers/`, open access)

- **2512.04123** — *Measuring Agents in Production* (ICML 2026 oral) — 20
  case studies; the best empirical picture of what production agents actually are.
- **2411.05285** — *AgentOps: Enabling Observability of LLM Agents* — the
  taxonomy of what to trace across the agent lifecycle.
- **2503.18813** — *CaMeL* · **2506.08837** — *Design Patterns for Securing
  LLM Agents* · **2406.13352** — *AgentDojo* (the standard agent-security benchmark).
