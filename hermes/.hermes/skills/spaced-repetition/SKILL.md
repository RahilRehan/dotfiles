---
name: spaced-repetition
description: Select, teach, review, and record learning items for DSA, system design, communication, and future personal-learning domains using one shared spaced-repetition ledger.
version: 0.1.0
author: Rahil, Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Learning, Spaced-Repetition, DSA, System-Design, Communication]
    related_skills: [dsa-coach, system-design-coach, communication-coach]
---

# Spaced Repetition

Use one shared review ledger for Rahil's learning domains. This skill owns
selection and review behavior; it does not own curriculum content, Obsidian
notes, credentials, Slack permissions, news consumption, building time, or
scheduling.

Domain coaches own teaching quality: `dsa-coach` teaches DSA, and
`system-design-coach` teaches system design. This skill supplies the shared
selection and retention contract they use.

## Current scope

- DSA questions from the cleaned DSA curriculum.
- System-design topics and design questions, with Hello Interview preceding
  Fanout in the curriculum order.
- Communication items created after an actual exercise, correction, or
  speaking/listening session.

Do not create placeholder communication items or add new domains until a real
learning item exists. The permanent morning schedules are managed outside this
skill. Interactive Slack sessions have the approved `file` and `terminal`
toolsets so they can persist explicit feedback; scheduled jobs do not have
permission to mutate state because `cron_mode` remains `deny`.

## Ledger

The durable machine-readable state is `~/.hermes/state/learning.json` in
Hermes, backed up with the rest of `data/`. Obsidian remains the detailed
human-owned source of notes; the ledger stores only selection and review state.

The shared planning knob is `exploration_level` in the ledger. It controls the
balance between new items and reviews without changing the review algorithm:

- `0.7` initially: favor broad coverage, while reserving about 30% for review;
- `0.5`: balanced learning and review;
- `0.2`: review-heavy maintenance;
- `0.0`: review-only when the backlog is intentionally closed.

When due items exist, reserve at least 25% of the learning session for them.
This minimum prevents exploration from becoming an excuse to skip revision,
while still allowing most of a session to cover new material early on.

This planner owns only the learning blocks. The current four-hour morning
envelope is 20 minutes for news, 25 minutes for communication, 75 minutes
maximum for DSA, 60 minutes for system design, and 60 minutes for building.
News and building must remain separate Daily Guide blocks and must not become
review items.

Planning is time-aware. Use the configured learning block, reserve the review
budget first, and spend the remaining minutes on new items. Current estimates
are 35 minutes for an unknown DSA problem, 20 minutes for a system-design topic, 45
minutes for a design question, 35 minutes for a case study, and 20 minutes for
a communication item. DSA estimates are difficulty-aware when source metadata
exists: Easy `20m`, Medium `35m`, Hard `60m`, and unknown `35m`. When source
difficulty is absent but the problem title is recognizable, the DSA coach may
make a session-local difficulty estimate and use the matching timebox; it must
label that value `estimated` and must not write it back as source metadata.
Use `unknown` only when the title is ambiguous. These are planning estimates,
not performance targets.

The DSA first pass is a five-month, weekly-paced plan for the current 412-item
curriculum: 19 items per week, six study days per week, and a maximum of 75
minutes per day. The weekly target is the commitment; the daily cap is a
guardrail, not a demand to force three identical questions into every session.
The curriculum is frozen during this pass; genuinely new questions go to a
later archive.

Each item separates learning progress from review scheduling. `progress` tracks
attempts, solved count, understood count, recalled count, mastery, and the date
the item first passed. A review rating (`again|hard|good|easy`) controls the next
review interval; an outcome (`attempted|solved|understood|recalled|mastered`)
records what actually happened. Never infer mastery from a rating alone.

Every item has a stable `id`, `domain`, `kind`, `label`, `source`, and review
fields. Curriculum metadata is nested under `metadata`. The curated DSA set
now carries source-backed status, topic, difficulty, and source-list fields;
pattern, importance, and prerequisite fields remain empty until supported by
evidence. System-design metadata currently records normalized curriculum
order. Stable IDs are never regenerated from a rewritten title. Keep the
original curriculum entry available in `source` when practical.

## Ad hoc "what's TODO" queries

When Rahil asks something like "what's TODO for system design" or "what
haven't I started in DSA" outside a formal session, don't just re-read the
Obsidian curriculum note — it lists topic titles but not progress. Query the
ledger directly: filter `items` by `domain` and `progress.attempts == 0 and
not progress.mastered`. Use
`scripts/list_todo.py --state ~/.hermes/state/learning.json --domain
system-design` (works for any domain) instead of hand-rolling a one-off
python -c snippet each time. If the not-started count equals the full domain
count, say so plainly — that means nothing has been logged as attempted yet,
not that the curriculum is unusually large. Offer to either mark historical
progress Rahil already did, or start from curriculum order 0, rather than
dumping the whole list into chat.

## Selection policy

When asked for the next learning session:

1. Select items due on or before the requested date first.
2. Within due items, prefer items with more failed recalls, then older due
   dates.
3. Apply `exploration_level` to reserve part of the bounded session for new
   items; do not turn the whole session into review unless the knob is set to
   review-only or there are no new items.
4. Select new items round-robin across available domains. Within a domain,
   use explicit importance metadata when present, then preserve curriculum
   order. Include DSA, system design, and communication when practiced
   communication items are available.
5. Do not repeat a not-due item merely because it is convenient.
6. Keep the session bounded. Return the selected item IDs and why each was
   selected: `due`, `new`, or `weak-item`.

The high-level learning block should reserve review time rather than dedicate
the entire block to revision. Use the configured 160-minute learning block as
a planning budget with at least 30 minutes for review when reviews are due;
the remaining time is available for new teaching and practice. Report the
planned budget, used minutes, and unused minutes so the Daily Guide can adjust
without pretending that item counts equal effort.

## Review behavior

Use active recall before explanation:

- DSA: ask for approach, invariant, complexity, and optionally code.
- System design: ask for requirements, scale, architecture, tradeoffs, and
  failure modes before teaching.
- Communication: ask Rahil to produce the answer first, then give focused
  feedback and record the exercise.

After Rahil responds, ask separately for a rating (`again`, `hard`, `good`, or
`easy`) and an outcome (`attempted`, `solved`, `understood`, `recalled`, or
`mastered`).
If the response itself clearly shows a failure or successful recall, suggest a
rating but let Rahil override it.

### Slack feedback protocol

Treat a reply in the item's thread as feedback for the item introduced in that
thread. Accept persistence only when Rahil explicitly supplies both fields,
preferably in this compact form:

```text
rating: good
outcome: understood
note: I needed one hint for the invariant.
```

Natural-language answers are coaching content, not a state mutation by
themselves. If the item or either field is ambiguous, ask a clarification
question and do not write anything. For an explicit rating/outcome, invoke the
deterministic helper with the concrete item ID, date, and optional note:

```text
python3 ~/.hermes/skills/spaced-repetition/scripts/review_state.py \
  --state ~/.hermes/state/learning.json rate ITEM_ID RATING \
  --outcome OUTCOME --date YYYY-MM-DD --note "..."
```

Read back the resulting item or summary before telling Rahil that the review
was saved. The helper keeps a bounded review history and the latest coaching
note on the item.

The initial transparent intervals are:

- `again`: 1 day
- `hard`: roughly 1.2× the previous interval, minimum 1 day
- `good`: roughly 2× the previous interval, minimum 3 days
- `easy`: roughly 3× the previous interval, minimum 7 days

Cap intervals at 180 days for now. Record the rating, recall quality, previous
interval, new interval, and timestamps. A missed review is not silently marked
complete; it remains due until reviewed.

## Output contract

For a session, show:

```text
Learning review — DD Mon YYYY, Asia/Kolkata

1. [domain] [new|due|weak-item] Item title
   Recall prompt: ...
   Reply with: rating [again|hard|good|easy] · outcome [attempted|solved|understood|recalled|mastered]

Progress: N completed · M remaining
Next review: DD Mon YYYY
```

After a rating, report the exact next-review date and the item recorded. Do
not report persistence unless the state write was actually completed and
verified.

## Testing boundary

The local planner and proactive delivery have been tested. The Slack write
path is now implemented, but it must be manually exercised with one known
thread before it is considered production-proven. Test locally and then
manually that:

- the JSON ledger validates;
- a new item is selected once;
- due items outrank new items;
- `again` returns the item sooner than `good`;
- the same item is not duplicated;
- state survives a process restart;
- invalid IDs and ratings fail safely without changing the ledger.

Test it with one known item and one explicit rating/outcome, verify the
resulting JSON diff and readback, and reject ambiguous replies. Ordinary vault
and state access is intentional for this personal agent; destructive shell
actions remain governed by manual approval.
