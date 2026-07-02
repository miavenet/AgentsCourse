# Theory-on-demand map — agent-ops

The coach pulls from here when you ask "why". Organized by lab so the coach
can offer ONE relevant pointer, then get back to the lab. For a curated
best-of-best reading shelf, see `FURTHER-READING.md`.

## Lab 1 — SLOs for a non-deterministic system
- Google SRE Book — Service Level Objectives:
  https://sre.google/sre-book/service-level-objectives/ (error budgets)
- OpenAI — A Practical Guide to Building Agents (PDF):
  https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf
- Day-4 whitepaper "What to Evaluate" — the seven evaluation dimensions.
- arXiv 2512.04123 *Measuring Agents in Production* (papers/) — what real
  production agents look like (68% run ≤10 steps before human intervention).

## Lab 2 — Observability & the Vibe Trajectory
- OpenTelemetry GenAI semantic conventions:
  https://opentelemetry.io/docs/specs/semconv/gen-ai/ · canonical repo
  https://github.com/open-telemetry/semantic-conventions-genai
  · agent spans .../gen-ai/gen-ai-agent-spans/ · metrics in `gen-ai-metrics.md`
- OTel blog — AI Agent Observability: https://opentelemetry.io/blog/2025/ai-agent-observability/
- "What is Agent Observability" (SLI formulas — loop rate, tool error rate,
  cost per successful task):
  https://dev.to/mostafa_ibrahim_774fe947b/what-is-agent-observability-traces-loop-rate-tool-errors-and-cost-per-successful-task-bl5
- Langfuse eval/observability docs: https://langfuse.com/docs/evaluation/overview
  · Arize Phoenix (OSS): https://arize.com/docs/phoenix
- arXiv 2411.05285 *AgentOps* (papers/) — taxonomy of what to trace.
- Day-4 whitepaper "Observability: Auditing the Agent's Mind" (spans,
  tail-based sampling, Denial of Wallet).

## Lab 3 — Eval-gated CI/CD & rollout
- Hamel Husain & Shreya Shankar — LLM Evals FAQ: https://hamel.dev/blog/posts/evals-faq/
  · foundational: https://hamel.dev/blog/posts/evals/
- LangSmith — Evaluation concepts (offline vs online, trajectory evals):
  https://docs.langchain.com/langsmith/evaluation-concepts
- Anthropic — multi-agent research system (rainbow deployments, checkpointing):
  https://www.anthropic.com/engineering/multi-agent-research-system
- Anthropic — April-2026 postmortem (config changes need eval gates):
  https://www.anthropic.com/engineering/april-23-postmortem
- ADK — Deploying your agent: https://adk.dev/deploy/ · Agent Starter Pack
  (eval-instrumented CI/CD): https://github.com/GoogleCloudPlatform/agent-starter-pack
- Day-5 whitepaper — `agents-cli scaffold / eval run / deploy`; Cloud Run vs
  Vertex AI Agent Engine.

## Lab 4 — Safeguards & security
- Simon Willison — the lethal trifecta: https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/
  · dual-LLM pattern: https://simonwillison.net/2023/Apr/25/dual-llm-pattern/
- OWASP Top 10 for LLM Apps 2025: https://genai.owasp.org/llm-top-10/
  (LLM01 Prompt Injection … LLM10 Unbounded Consumption)
- OWASP Agentic AI — Threats & Mitigations (T1 Memory Poisoning … T15 Human
  Manipulation): https://genai.owasp.org/resource/agentic-ai-threats-and-mitigations/
- CaMeL — Defeating Prompt Injections by Design: https://arxiv.org/abs/2503.18813 (papers/)
- Design Patterns for Securing LLM Agents: https://arxiv.org/abs/2506.08837 (papers/)
- Anthropic — Claude Code sandboxing (egress deny-by-default, credential
  isolation): https://www.anthropic.com/engineering/claude-code-sandboxing
- Microsoft MSRC — defending against indirect prompt injection (Spotlighting,
  Prompt Shields): https://www.microsoft.com/en-us/msrc/blog/2025/07/how-microsoft-defends-against-indirect-prompt-injection-attacks
- NIST AI RMF + GenAI Profile: https://www.nist.gov/itl/ai-risk-management-framework
- Benchmarks: AgentDojo https://arxiv.org/abs/2406.13352 (papers/) ·
  InjecAgent https://arxiv.org/abs/2403.02691
- Day-4 whitepaper "7-Pillar Agent Security Architecture"; Red/Blue/Green.

## Lab 5 — Incidents & reliability
- Anthropic — postmortem of three recent issues (silent quality incident):
  https://www.anthropic.com/engineering/a-postmortem-of-three-recent-issues
- Replit incident (agent deleted prod DB, lied about it):
  https://codenotary.com/blog/when-ai-goes-rogue-the-replit-incident-and-its-lessons
  · AI incident-response playbook: https://tianpan.co/blog/2026-04-19-ai-incident-response-playbook-llm-production
- Applying SRE to Autonomous AI Agents (Microsoft) — error budgets, burn rates:
  https://techcommunity.microsoft.com/blog/linuxandopensourceblog/applying-site-reliability-engineering-to-autonomous-ai-agents/4521357
- AI Agent Error Budgets: https://www.buildmvpfast.com/blog/ai-agent-error-budget-sre-reliability-autonomous-2026
- Day-4 whitepaper "stateful circuit breakers" + version-control checkpoints.

## Workshop — Agent-as-a-Service
- 12-Factor Agents: https://github.com/humanlayer/12-factor-agents
- Temporal — durable execution for agentic flows:
  https://temporal.io/blog/from-ai-hype-to-durable-reality-why-agentic-flows-need-distributed-systems
- Building LangGraph (agent runtime capabilities): https://www.langchain.com/blog/building-langgraph
- Anthropic — Building Effective Agents: https://www.anthropic.com/engineering/building-effective-agents
- Building agents with the Claude Agent SDK:
  https://claude.com/blog/building-agents-with-the-claude-agent-sdk
- Codelab — deploy ADK agents to GKE:
  https://codelabs.developers.google.com/codelabs/production-ready-ai-with-gc/5-deploying-agents/deploy-adk-agents-to-gke
- Day-5 whitepaper "Zero-Trust Development" (Policy Server) + three-tier
  Code Review Runtime (Managed / Hybrid / Custom on Agent Engine).

## Course-native terms (stay consistent with the whitepapers)
Effective Trust · Context-as-a-Perimeter · Zero Ambient Authority / JIT
downscoping · Vibe Trajectory (`agent.session`/`agent.think`/`agent.tool`) ·
tail-based sampling · AgBOM vs SBOM · Red/Blue/Green teaming · the Vibe Diff
/ Evaluator Quorum · Slopsquatting · Denial of Wallet · seven evaluation
dimensions · online evaluation / session convergence · "tests catch
deterministic regressions, evaluation catches behavioural drift" ·
Zero-Trust Development / Policy Server (structural + semantic gating) ·
three-tier Code Review Runtime · Human-in-the-Loop checkpoint gates ·
Conditional LGTM · Cloud Run / Vertex AI Agent Engine.
