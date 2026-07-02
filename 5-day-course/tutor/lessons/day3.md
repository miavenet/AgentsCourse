# Day 3 — Agent Skills

Whitepaper: `5-day-course/day3-agent-skills/whitepaper-agent-skills.md`
Figures: `5-day-course/day3-agent-skills/assets/whitepaper-agent-skills/`

## Concept cards

### D3-C1: What a Skill is, and why now
Summary: An Agent Skill is a folder with a SKILL.md file plus optional
scripts/, references/, and assets/ directories — packaged procedural
knowledge an agent loads on demand. The paper credits their fast adoption
to four friction points they solve: context rot from overstuffed system
prompts, the lack of procedural memory ("how", not just "what"),
multi-agent system overload, and portability across vendors (any agent
with filesystem access can use them).
Source: "1. Introduction"
Elaborate: Which of the four friction points have you personally hit when prompting agents?

### D3-C2: Skill anatomy & progressive disclosure
Summary: SKILL.md starts with metadata (name + description) that is the
only thing the model sees during routing; full instructions, scripts, and
references load only when the skill triggers. This progressive disclosure
keeps the standing prompt tiny while letting one general agent flex into
hundreds of specialist roles — the metadata acts as a thin routing layer.
Figure: assets/whitepaper-agent-skills/figure-2.png
Source: "2. What is an Agent Skill — Skill Anatomy & Progressive Disclosure"
Elaborate: How is progressive disclosure like a book's table of contents?

### D3-C3: Skills as procedural memory
Summary: LLM systems had analogs for episodic memory (what happened —
conversation history) and semantic memory (facts — retrieval/weights), but
not procedural memory (how to do things step by step). Skills are the first
credible procedural-memory primitive: repeatable know-how stored outside
the model, versionable and shareable like code.
Source: "1. Introduction" (friction point 2)
Elaborate: Map the three memory types onto components of an agent system you use.

### D3-C4: Two authoring paths
Summary: Path A translates what you already know — turn an existing runbook
or expert workflow into SKILL.md. Path B crystallizes what the agent just
did — after a successful session, have the agent write the reusable skill
from its own trajectory. B turns one-off wins into permanent capability.
Figure: assets/whitepaper-agent-skills/figure-9.png
Source: "Path A / Path B", "2. What is an Agent Skill"
Elaborate: Name one workflow of yours ripe for Path A and one recent agent success ripe for Path B.

### D3-C5: Evaluating skills — the trigger is the first gate
Summary: A skill that never fires can't help; one that fires too broadly
pollutes context. Vercel's production data showed a 56% non-invocation rate
for skills expected to trigger, and a badly designed skill scored *below*
the no-skill baseline (58% vs 63%) — a poor skill subtracts capability. To
hit ~90% trigger accuracy, the description must pass four checks: testable
specificity (write 3 positive + 3 negative triggers), clarity vs adjacent
skills, execution fidelity (describe real performance), and rephrasing
stability.
Figure: assets/whitepaper-agent-skills/table-1.png
Source: "4. Evaluating Skills — The trigger is the first gate"
Elaborate: Why can a skill score worse than having no skill at all?

### D3-C6: Context rot and token economics
Summary: As prompt size grows, accuracy on a fixed task degrades well
before the context window is full — context rot. Skills fight it
economically: a fifty-skill library costs almost nothing at rest (only
metadata is loaded) versus one giant prompt that pays full token cost on
every request and degrades performance. Co-loading many skills at once
recreates the problem (isolation is a trap in evaluation too).
Figure: assets/whitepaper-agent-skills/figure-7.png
Source: "5. From Prototype to Production — context overflow / token budget"
Elaborate: Connect context rot to why this tutor limits new concepts per session.

### D3-C7: Composing skills at scale
Summary: Beyond single skills: DAG orchestration routes execution through
skill graphs; capability profiles package environment-specific skill sets;
a canonical taxonomy organizes hundreds of skills; and governance ladders
(read → draft → act) classify how much autonomy each skill capability
gets. Meta-skills that improve skills exist but need evaluation gating —
the agent can propose changes, evals decide if they land.
Figure: assets/whitepaper-agent-skills/figure-10.png
Source: "6. Meta-Skills", "7. Composing and Packaging Skills"
Elaborate: Why gate a meta-skill's self-improvements behind evals rather than trust them?

## Question cards

### D3-Q1 (tests D3-C1)
Q: What is an Agent Skill structurally, and what are the four friction points the paper says Skills solve?
Hint: A folder with a special file; then think prompts, memory types, multi-agent, vendors.
Key:
- A folder with SKILL.md (plus optional scripts/, references/, assets/)
- Context rot from overstuffed prompts; missing procedural memory; multi-agent complexity; portability across agents/vendors

### D3-Q2 (tests D3-C2)
Q: During routing, what does the model see of a skill, and what is this design pattern called?
Hint: Two metadata fields.
Key:
- Only the metadata (name + description); full instructions load on demand
- Progressive disclosure

### D3-Q3 (tests D3-C3)
Q: Name the three memory types discussed and which one Skills provide.
Hint: What happened / facts / how-to.
Key:
- Episodic (what happened), semantic (facts), procedural (how to do things)
- Skills are the procedural-memory primitive

### D3-Q4 (tests D3-C4)
Q: Describe authoring Paths A and B for creating a skill.
Hint: One starts from your head, one from the agent's history.
Key:
- Path A: translate existing human know-how (runbooks, workflows) into a skill
- Path B: crystallize a successful agent trajectory into a reusable skill

### D3-Q5 (tests D3-C5)
Q: What did Vercel's production analysis reveal about skill triggering and skill quality?
Hint: Two numbers about firing, one comparison about quality.
Key:
- 56% non-invocation rate for skills expected to trigger
- A poorly designed skill scored below the no-skill baseline (58% vs 63%) — bad skills subtract capability
Stretch: Your new skill isn't firing. Walk through the four description checks and give a concrete fix for each.
StretchKey:
- Testable specificity: write 3 positive and 3 negative trigger examples and test them
- Clarity: rewrite so it can't be confused with adjacent skills
- Execution fidelity: describe what the skill actually does, not aspirations
- Rephrasing stability: test that differently-worded user intents still route to it

### D3-Q6 (tests D3-C5)
Q: The paper says global conventions belong in always-loaded docs (like AGENTS.md), not in skills. What evidence backs this, and what are skills best reserved for?
Hint: A 100% number vs a 53% number.
Key:
- A passive AGENTS.md conventions index hit a 100% pass rate vs a 53% baseline in the same Vercel study
- Skills are best for narrow, action-specific workflows; global context stays passive and always accessible

### D3-Q7 (tests D3-C6)
Q: What is context rot, and how does a skill library beat one big prompt economically?
Hint: Degradation before the limit; cost at rest.
Key:
- Accuracy degrades as prompt size grows, long before the context window is full
- A skill library loads only metadata at rest, paying tokens only for the skill in use; a big prompt pays full cost (and degrades) on every request

### D3-Q8 (tests D3-C7)
Q: What does the read/draft/act governance ladder classify, and why do meta-skills need evaluation gating?
Hint: Autonomy levels; who approves self-changes.
Key:
- It classifies skill capabilities by autonomy level and required review (reading data vs drafting outputs vs acting on the world)
- Meta-skills may propose changes to skills, but evals decide whether changes land — otherwise self-modification can silently degrade behavior
Stretch: Design the governance for a "refund-processing" skill family at a retailer: place look-up, draft-response, and issue-refund on the ladder with review requirements.
StretchKey:
- Look-up = read (autonomous); draft-response = draft (human sends/approves); issue-refund = act (human approval or strict limits + audit)
- Higher rungs get stricter review and logging

### D3-INT (Integrate)
Q: Design a skill for this course: "quiz-me-on-whitepapers". Specify its SKILL.md metadata (name + trigger description passing the four checks), its folder contents, and how progressive disclosure keeps it cheap.
Key:
- Sensible name + description with specific positive/negative triggers (e.g. fires on "quiz me", not on "summarize")
- Folder: SKILL.md instructions plus references/ pointing at the lesson/whitepaper files
- Only metadata sits in context until a quiz is requested; question banks load on demand

## Go deeper (external, free)

- Anthropic engineering: "Equipping agents for the real world with Agent Skills" — https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills
- Agent Skills docs (Claude platform) — https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview
- Anthropic's public skills repo (read real SKILL.md files) — https://github.com/anthropics/skills
- Anthropic's free Agent Skills course — https://anthropic.skilljar.com/introduction-to-agent-skills
