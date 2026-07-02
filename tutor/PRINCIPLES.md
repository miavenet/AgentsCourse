# Why This Tutor Works: The Neuroscience of Learning

Read this once as a human. Nothing here is required to run a session — it
explains why the protocol in `TUTOR.md` is shaped the way it is, so you
trust the mechanics enough to follow them on days they feel unpleasant.
(Spoiler: the unpleasant days are the ones doing the most for you.)

## 1. What "learning" physically is

A memory is not a recording; it's a pattern of strengthened connections
between neurons. Three phases matter for study design:

- **Encoding** — while you attend to new material, neurons that fire
  together strengthen their synapses (long-term potentiation). Attention is
  the gate: material you merely see, without processing its meaning, barely
  encodes at all.
- **Consolidation** — over hours and especially during sleep, the
  hippocampus "replays" new patterns to the neocortex, converting fragile
  traces into stable long-term structure. This is why the tutor ends every
  session telling you to come back *another day*: two sessions separated by
  sleep beat one double-length session.
- **Retrieval** — recalling a memory partially re-opens it for modification
  (reconsolidation). Each successful effortful recall re-saves the memory in
  strengthened, updated form. This is the engine the whole tutor runs on.

## 2. The techniques, and where the tutor applies each

### Retrieval practice (the testing effect)
Actively recalling information strengthens memory far more than re-reading
it — in classic experiments (Roediger & Karpicke, 2006), students who
practiced recall retained roughly 50% more a week later than students who
re-studied for the same time. Re-reading feels better and works worse: it
creates fluency ("this looks familiar") that your brain mistakes for
knowledge.
**In the tutor:** everything is a question. You are never shown material
twice; you are asked for it. Rule #2 (never reveal the key before an
attempt) exists because even a failed retrieval attempt potentiates the
correction that follows.

### Spaced repetition
Memories decay along a forgetting curve (Ebbinghaus). Reviewing just before
you'd forget resets the curve with a shallower slope each time — the same
minutes spread over days buy multiples of the retention that massing them
in one sitting does (Cepeda et al., 2006).
**In the tutor:** the Leitner boxes. A card you know moves to longer
intervals (1 → 2 → 7 → 21 days); a card you miss comes back tomorrow. The
intervals deliberately let you *start* forgetting — recall that requires
effort is recall that strengthens.

### Interleaving
Practicing related-but-different topics shuffled together outperforms
studying them in blocks, because your brain must repeatedly *discriminate*
which concept applies — the exact skill exams and real work demand. Blocked
practice feels smoother and produces worse transfer.
**In the tutor:** the review block never asks two cards from the same day
back-to-back when it can avoid it, and exams shuffle all five days.

### Elaborative interrogation & the generation effect
Asking "why is this true?" or "how does this connect to what I know?"
forces deep semantic processing, which creates more retrieval routes.
Producing an answer in your own words (generation) encodes better than
receiving the same words passively.
**In the tutor:** every concept card ends with an `Elaborate:` prompt
before any quizzing, and after every MISS you must restate the correction
in your own words before moving on.

### Desirable difficulties
Conditions that slow you down and induce errors during practice — spacing,
interleaving, testing before you feel ready — improve long-term retention
and transfer (Bjork). The discomfort is the signal that encoding is deep.
**In the tutor:** the adaptive `stretch` mode. Three straight HITs means
the questions have stopped being difficult enough to be useful, so the
tutor escalates to application-level variants. A MISS drops you back —
difficulty stays pinned near the edge of your ability (your zone of
proximal development), where learning is fastest.

### Errorful learning + immediate feedback, and hypercorrection
Guessing wrong and being corrected produces *better* retention than never
guessing — provided feedback is immediate. Strongest of all is the
**hypercorrection effect**: errors made with high confidence, once
corrected, are the least likely to ever be repeated — surprise is a
powerful encoding signal.
**In the tutor:** the optional `(sure)`/`(unsure)` tag on your answers.
A confident miss gets flagged, resurfaces tomorrow regardless of anything
else, and is listed at session close for a same-night re-read. Tag
honestly; the flags are finding miscalibrated beliefs, which are the most
dangerous kind of not-knowing.

### Metacognitive calibration
Learners are systematically overconfident about material that merely feels
familiar. Confidence judgments before feedback train your internal
"do I actually know this?" sensor, which improves how you allocate future
study time.
**In the tutor:** same `(sure)`/`(unsure)` mechanism — over weeks, watch
your flagged-error count fall.

### Dual coding
Verbal and visual information are processed by partly separate systems;
encoding both creates two retrieval paths to the same idea (Paivio).
**In the tutor:** concept cards point at the actual figure PNGs extracted
from the whitepapers (`dayN/assets/…`). Open them — a diagram you've seen
anchors a definition you've read.

### Cognitive load management
Working memory holds only a handful of chunks. Overloading it during
encoding means nothing reaches long-term memory (Sweller).
**In the tutor:** one question at a time, at most 6 new concepts per
session, explanations capped at 4 sentences, and re-teaching (after 2
misses) re-presents the *summary*, not the whole chapter.

### Sleep-dependent consolidation
Hippocampal replay during slow-wave and REM sleep is when the day's
learning is filed into cortex. Two shorter sessions with a night between
them reliably beat one long one.
**In the tutor:** sessions are capped (~6 concepts), and the sign-off
instruction to return on a different day is not a pleasantry — it is the
consolidation step of the algorithm, and you are the one who executes it.

## 3. How a 5-day course becomes a 5-week memory

The course's own structure (one topic per day) blocks nicely for *first
exposure*, but retention comes from what happens after: each day's cards
keep resurfacing at growing intervals while new days are added, so by the
time you take the post-course `exam` session, Day 1 material has been
retrieved on roughly days 1, 2, 4, 11, and 32 — five spaced, interleaved,
effortful retrievals. That schedule, not the first read, is what makes it
stick.

## 4. Open resources on learning science

- The Learning Scientists — free, evidence-based guides to the six core
  study strategies (spacing, retrieval, interleaving, elaboration, dual
  coding, concrete examples): https://www.learningscientists.org/downloadable-materials
- Retrieval Practice (Pooja Agarwal) — practical guides and the research
  behind the testing effect: https://www.retrievalpractice.org/library

## 5. What the human must supply

The protocol automates scheduling, difficulty, and feedback, but three
things only you can do:

1. **Attempt before looking.** Every time.
2. **Sleep between sessions.** The algorithm assumes it.
3. **Tag confidence honestly.** The system finds blind spots only if the
   `(sure)` tag means it.
