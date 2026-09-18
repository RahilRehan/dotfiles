# Personal agent roadmap

## Vision

Build a proactive personal guide for Rahil: an assistant that teaches,
retrieves, revises, reminds, motivates, and proposes the next useful action
across learning, health, money, maintenance, content, career, and startup work.

The system should be proactive in recommendations but confirmation-based for
external actions. It should not publish, move money, alter important records, or
make commitments silently.

## Source-of-truth design

- Obsidian is the detailed, human-owned life knowledge base.
- Hermes memory stores compact durable preferences, goals, and profile facts.
- Hermes skills store repeatable procedures and coaching workflows.
- Hermes cron delivers routines and reminders.
- Slack is the conversational and notification interface.
- Each domain gets a small, explicit data structure rather than one giant note.

## Anti-duplication and retention architecture

Proactive behavior needs a shared ledger, not separate skills independently
remembering what they suggested. Every lesson, news item, recommendation,
exercise, reminder, and content idea should have a stable record with:

- canonical ID or source URL
- domain and topic
- first seen, last shown, and last acted-on timestamps
- status: new, active, completed, rejected, deferred, or archived
- review metadata where relevant: difficulty, recall quality, and next review date

Rules:

- News deduplicates by canonical post/article URL, post ID, and normalized topic;
  repeat only for a material update or an explicit request.
- Learning repeats because review is due, not because the same item is convenient.
  Failed recall shortens the interval; successful recall lengthens it.
- Recommendations are not repeated until their cooldown expires, their status
  changes, or new evidence makes them relevant.
- Daily guidance reads the ledger and selects a small number of due or high-value
  actions across domains; domain skills do not independently spam Slack.
- Every proactive message should state whether it is new, due for review, or a
  follow-up.

## Daily learning allocation

Rahil prefers touching the important domains every day, with adaptive depth
rather than a rigid rotation. The daily guide should therefore produce:

- communication every day, usually a short writing or speaking exercise;
- DSA every day, ranging from an easy problem, a partial attempt, a review, or
  a harder problem depending on time and recent performance;
- system design every day, ranging from one concept review to a deeper design
  exercise;
- any additional domain only when it is due, urgent, or fits the available
  time.

Use a focus/maintenance pattern. One domain gets the main block, while the
others receive small meaningful touches. Balance difficulty across the day:

- hard DSA → system design review or one small concept;
- medium DSA → system design explanation or short tradeoff exercise;
- easy DSA → deeper system design topic;
- deep system design → easy DSA or DSA review.

The initial review planner uses one `exploration_level` knob: `0.7` favors new
material while reserving review time, and lower values progressively shift the
session toward maintenance. Due reviews always receive at least 25% of the
session when any are available; `0.0` is review-only.

Reviews due today take priority over new material. The guide should assume a
bounded default session, ask for a shorter or longer version only when needed,
and allow Rahil to reply with available time or energy. It should report what
was completed, what was intentionally shortened, and what is next due rather
than treating every domain as an all-or-nothing task.

### DSA first-pass strategy

The current 412-item DSA curriculum is a five-month first pass beginning
2026-09-14 and targeting 2027-02-14. The commitment is 19 items per week over
six study days, not a rigid number of questions every day. DSA is capped at 75
minutes per day so startup building and other life goals remain the priority.

Each item is handled as deliberate practice: active recall first, a progressive
hint ladder, an explanation of the invariant and complexity, then implementation
and requirement-driven tests where useful. Easy, medium, hard, and unknown
items use different planning estimates. Review scheduling is separate from
learning progress: attempts, solved, understood, recalled, and mastered are
tracked independently. The curriculum is frozen during the first pass; new
questions are collected for a later archive.

## Skill and integration architecture

Use one focused skill per meaningful domain or repeatable workflow. Skills
contain behavior, teaching style, prioritization, output formats, and safety
rules. They should not contain credentials or become the database.

Connectors and MCP servers provide access to external systems. Keep them
separate from skills and expose the smallest read-only surface first.

Planned skills:

- `obsidian-research` — search and teach from the read-only vault with note-path citations.
- `x-news-digest` — monitor X lists and produce India-focused news and content ideas.
- `spaced-repetition` — shared selection, review, and persistence across
  learning domains; it is infrastructure, not a teaching mega-skill.
- `dsa-coach` — problem-solving instruction, hints, code review, and tests.
- `system-design-coach` — concept teaching, design practice, and interview simulation.
- `communication-coach` — proactive spoken, written, listening, vocabulary, grammar, and public-speaking coaching.
- `coding-coach` — keep Rahil close to code, design reasoning, and requirement-driven testing while using coding agents.
- `agent-control` — later, safely route approved development tasks to Codex, Claude, Cursor, or a project tool.
- `personal-recall` — record and retrieve movies, books, events, and experiences.
- `growth-insights` — deliver sourced book ideas, practical applications, and
  repeated recall without motivational spam.
- `wellbeing-coach` — motivation and sustainable exercise accountability.
- `finance-coach` — financial education, summaries, and manually confirmed records.
- `life-admin` — car service, insurance, renewals, and household reminders.
- `content-coach` — turn notes and research into Instagram, YouTube, and X drafts.
- `startup-coach` — evaluate opportunities, evidence, experiments, and next actions.
- `daily-guide` — a thin coordinator that selects a few actions from the domain skills.

Do not build all of these up front. Start each as a manual workflow, add its
data structure, test it, and only then schedule it or connect an external API.
Financial connectors and any action that can move money or publish externally
must remain read-only or confirmation-gated until separately audited.

## Build order

### 0. Foundation and vault access

- [x] Mount the complete personal Obsidian vault at `/opt/obsidian` and expose
      it through Hermes' native file tools.
- [x] Configure `OBSIDIAN_VAULT_PATH` so skills use one concrete container path.
- [x] Permit ordinary read/search/create/append/targeted-edit operations; keep
      delete, rename, move, and arbitrary shell actions confirmation-gated.
- [ ] Test note search, note retrieval, note creation, append, and source-path
      citations from Slack.
- [x] Require read-back after every note write and report the exact path changed.

### 1. Daily personal briefing

- [x] Daily 06:30 IST companies X-news digest is scheduled.
- [ ] Add a short personal agenda section without changing the news routine.
- [ ] Include due reviews, communication, DSA, system design, reminders, one
      health action, and one optional content/startup action using adaptive
      depth rather than independent full-sized tasks.
- [ ] Test that the briefing is useful rather than an overwhelming task list.

### 1.5. Shared progress and retention ledger

- [x] Define the smallest durable record format for lessons, recommendations,
      news items, reminders, and content ideas.
- [x] Store machine-readable review state in the backed-up Hermes `data/`
      directory, separate from Obsidian prose notes.
- [x] Keep detailed human-readable learning notes in Obsidian only when useful;
      do not make Obsidian and the ledger competing sources of truth.
- [x] Add stable IDs, statuses, timestamps, cooldowns, and review dates.
- [ ] Test that an already-completed recommendation is not repeated.
- [ ] Test that a deliberately failed learning item returns when due.
- [ ] Test that a new update to an old news topic is treated as new evidence.
- [x] Verify that the temporary multi-channel delivery test does not mutate the
      ledger or memory when no inbound write path is available.
- [x] Implement the explicit inbound Slack-to-ledger write path for ratings and
      outcomes, with deterministic helper invocation and read-back verification.
- [ ] Manually test one known item in one Slack thread and reject ambiguous
      replies.
- [x] Add a shared daily execution ledger for planned/completed/skipped/
      shortened blocks and energy state.

### 2. Learning and retention engine

- [x] Create initial learning records for DSA and system-design items, with
      communication items added after real practice.
- [x] Implement one shared review engine for DSA, system design, and future
      communication items rather than one scheduler per skill.
- [x] Start with DSA and system design.
- [x] Use active recall first: ask Rahil to solve or explain before teaching.
- [x] Schedule spaced reviews based on difficulty and recall quality.
- [x] Add explicit curriculum metadata fields and a conservative curriculum-
      order fallback when source metadata is not yet available.
- [x] Replace the original 782-item DSA curriculum with the curated tracking
      union: 314 historical notes plus 98 missing NeetCode/LeetCode core items.
- [x] Add source-backed topic, difficulty, and source-list metadata to the
      curated DSA tracking set without guessing from slugs.
- [x] Configure a five-month, weekly-paced DSA first pass with a 75-minute
      daily cap and difficulty-aware time estimates.
- [x] Separate DSA progress outcomes from spaced-repetition ratings.
- [ ] Complete DSA pattern, importance, and prerequisite metadata from
      Obsidian/source evidence.
- [ ] Track repeated mistakes and create targeted revision sessions.
- [ ] Test one daily problem and one review session before broadening scope.

### 2.5. Communication coach

- [x] Capture Rahil's baseline, goals, correction preference, and real practice
      contexts in `SOUL.md` and memory.
- [x] Create `communication-coach` with Slack/Open Whisper speaking practice,
      ChatGPT Voice roleplay prompts, writing, word rescue, listening, review,
      broad daily curiosity topics, and compact practice records.
- [x] Define confidence, recurring-error, and spaced-review fields without
      turning feedback into grades.
- [x] Add broad curiosity topics and reading-comprehension practice so the
      coach is not limited to Amazon and technology.
- [x] Schedule the daily communication notification in `#communication` after
      testing its delivery.
- [ ] Run the first manual Slack speaking exercise and verify the retry loop.
- [ ] Test the ChatGPT Voice prompt and paste back its handoff.
- [ ] Run and verify the first writing exercise and a non-technical curiosity
      topic.
- [ ] Verify persistence and non-repetition from a real Slack reply.

### 2.6. Daily Guide and morning block

- [x] Define a four-hour morning block: 20 minutes of news, 25 minutes of
      communication, 75 minutes of DSA, 60 minutes of system design, and 1
      hour of building.
- [x] Create a local Daily Guide coordinator that assembles the blocks without
      duplicating domain skills.
- [x] Reserve communication every day, with one primary mode and a short
      vocabulary/retrieval warm-up in the Daily Guide plan.
- [x] Include DSA and system design every day, with new material and due
      reviews selected by spaced repetition and taught by their domain coaches
      in the local plan.
- [x] Design the Daily Guide as a compact, channel-aware dashboard with one
      clear start action and explicit completion controls.
- [x] Define a Slack-native mrkdwn format that preserves information while
      improving hierarchy, retrieval cues, and focus.
- [x] Schedule separate morning deliveries for news, communication, DSA,
      system design, and building in their chosen channels.
- [ ] Include small daily health, finance, life-admin, or motivation actions;
      do not turn them into long reports.
- [ ] Decide later whether a single Daily Guide summary is better than the
      current separate-channel delivery; do not change this during testing.
- [x] Test scheduled delivery manually in Slack before enabling the permanent
      morning schedules.

### 3. Personal recall

- [x] Add a lightweight media/experience log for movies, books, and events.
- [ ] Support questions such as “What did I watch yesterday?” and “What was it
      about?” with dates and note links.
- [ ] Test recall after a restart and after several unrelated conversations.

### 3.5. Book insights and motivation

- [x] Create a sourced growth-insight skill with one practical application per
      insight.
- [x] Reuse the spaced-repetition interval engine for insight recall and
      personal-memory resurfacing.
- [x] Add deterministic deduplication, due selection, application status, and
      verified state writes under the native `~/.hermes/state/life/` path.
- [ ] Add the first real book insight from Rahil's Obsidian notes or a source
      he provides.
- [ ] Test selection, delivery, response persistence, rejection, and restart
      survival from Slack.
- [ ] Schedule one combined Growth & Recall message only after manual tests
      pass.

### 4. Health and motivation

- [ ] Track simple exercise intentions and completions, not sensitive medical
      diagnoses.
- [ ] Provide small next actions and weekly progress reflection.
- [ ] Use supportive accountability without guilt or shame.
- [ ] Test a low-friction daily check-in before adding detailed metrics.

### 5. Finance and vehicle administration

- [ ] Define a private finance-note structure and decide what Hermes may read.
- [ ] Start with education, summaries, budgets, and manually entered records.
- [ ] Add car service, insurance, pollution certificate, and renewal dates.
- [ ] Create reminder jobs with explicit confirmation for record changes.
- [ ] Do not connect bank accounts or enable financial transactions in the first version.

### 6. Content and startup coach

- [ ] Turn X/news and Obsidian notes into India-focused tech content ideas.
- [ ] Draft Instagram, YouTube, and X posts in Rahil's voice.
- [ ] Maintain a content backlog, status, and next publishing action.
- [ ] Maintain a startup opportunity backlog linked to real problems and evidence.
- [ ] Keep publishing manual until drafting quality and approval flow are proven.

### 7. Coding and agent-engineering coach

- [ ] Interview Rahil for coding standards, preferred languages, frameworks,
      testing expectations, and review boundaries.
- [ ] Start with code-reading and requirement-to-test exercises from selected
      Obsidian notes or a safe project.
- [ ] Review agent-generated changes for design, clarity, failure modes, and
      meaningful requirement coverage.
- [ ] Keep implementation and publishing actions confirmation-gated.
- [ ] Explore Slack control only after read-only project status and review flows
      are reliable; do not begin with arbitrary remote command execution.

## Feature test loop

For every feature:

1. Define the data shape and success criteria.
2. Create the smallest skill or routine.
3. Test manually in Slack.
4. Verify persistence after restart.
5. Test an incorrect, missing, or unauthorized input.
6. Schedule it only after the manual test passes.
7. Record the result here before adding the next feature.

## Current status

- Hermes runs with one durable `data/` directory.
- Slack has the approved personal-assistant toolset, including file and
  terminal access; manual approvals remain enabled for destructive shell work
  and cron jobs remain unable to mutate state.
- `x-news-digest` is active and scheduled daily at 06:30 IST.
- Obsidian vault has been inspected and reorganized into Learning categories.
- `communication-coach` is implemented and its scheduled delivery is active;
  the real exercise/retry and persistence tests remain.
- `dsa-coach` and `system-design-coach` are implemented as domain teaching
  skills using the shared spaced-repetition ledger; their scheduled deliveries
  are active, while real coaching and persistence tests remain.
- The selection schema now distinguishes source-backed metadata from
  unclassified DSA records; unknown records safely follow curriculum order
  until an evidence-based enrichment pass is completed.
- The DSA planner now uses a five-month first pass (19 items/week across six
  study days), a 75-minute daily cap, difficulty-aware estimates, progressive
  hints, and separate learning outcomes from review ratings.
- The backed-up spaced-repetition ledger and offline review utility now contain
  702 DSA/system-design items: 412 curated DSA tracking items and 290 system-
  design items. The four-hour envelope is modeled as 20 minutes news, 25
  minutes communication, 75 minutes DSA, 60 minutes system design, and 60
  minutes building; review notifications are
  delivered. Explicit Slack ratings/outcomes now have a deterministic write
  path; the manual end-to-end proof is the remaining test.
- A separate backed-up daily execution ledger now records what was planned and
  what actually happened without duplicating learning progress.
- `personal-recall` and `growth-insights` now share a deterministic life-state
  helper that reuses the existing interval engine; no proactive schedule has
  been created until their Slack feedback loop is tested.
- A local Daily Guide coordinator now assembles that envelope; Slack delivery
  has been tested through temporary channel deliveries and the permanent
  channel schedules are active.
- The next milestone is the genuine coaching loop: answer in the same Slack
  thread, send an explicit rating/outcome, and verify one exact ledger diff;
  then exercise a real Obsidian read and a deliberately approved write from
  Slack.
