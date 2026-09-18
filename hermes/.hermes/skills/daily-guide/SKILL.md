---
name: daily-guide
description: Coordinate Rahil's morning across news, learning, building, and future life domains using one bounded plan and shared progress state.
version: 0.1.0
author: Rahil, Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Personal-Agent, Daily-Guide, Planning, Learning]
    related_skills: [spaced-repetition, dsa-coach, system-design-coach, communication-coach, x-news-digest, personal-recall, growth-insights]
---

# Daily Guide

Act as the thin coordinator for Rahil's personal-agent routine. Assemble one
useful morning plan; do not become a separate database or duplicate the
behavior of domain skills.

## Current morning envelope

The current four-hour plan is:

- 20 minutes: India-relevant technology news and content signals, using
  `x-news-digest`;
- 25 minutes: communication practice selected by `communication-coach`;
- 75 minutes maximum: DSA problem-solving selected by `spaced-repetition` and
  taught by `dsa-coach`, paced against a weekly target rather than a rigid
  daily question count;
- 60 minutes: system-design learning selected by `spaced-repetition` and
  taught by `system-design-coach`;
- 60 minutes: building one concrete product, startup, or content outcome.

The schedule is a planning budget, not a demand to work without breaks. If
Rahil reports less time or energy, shorten the plan while preserving due
reviews, the DSA daily cap, and the single highest-value building action.

## Coordination rules

1. Produce one morning message with these blocks. Domain skills must not send
   independent duplicate morning notifications once this guide is active.
2. Ask the news skill for a compact digest; do not let news consume the
   learning or building blocks.
3. Reserve communication time every day. Choose one mode—writing, speaking,
   reading, listening, vocabulary, or roleplay—and keep it to one primary
   exercise plus a short warm-up.
4. Give DSA and system design their own bounded budgets to the
   spaced-repetition planner, then hand each selected item to its domain coach.
   It must reserve review time when items are due and use its
   `exploration_level` knob for the new-versus-review balance. DSA uses a
   weekly target and never exceeds its 75-minute daily cap.
5. Choose exactly one building outcome from a real backlog when available. If
   no building backlog is connected, say that the block needs a project choice;
   do not invent progress or create a large task list.
6. Add health, finance, life-admin, startup, content, or recall sections only
   when their skill and data source are implemented and an item is due or
   clearly useful. Do not fill the plan for symmetry.
7. Read the shared learning ledger for selection and the daily execution state
   for today's progress. Write state only for explicit feedback or explicit
   `done`, `skip`, `shorten`, or `energy` controls. Never claim that a review or
   task was persisted based only on a conversation.

## UX rules

Treat the Daily Guide as a morning dashboard, not a transcript or a dump of
planner internals.

- Make the first screen scannable in a few seconds: date, one-sentence win,
  time map, and a single `Start here` action.
- Use compact sections with consistent labels: `Goal`, `Plan`, `Done when`,
  and `Channel`.
- Group learning work by destination channel. The guide coordinates; the
  domain channel holds the detailed coaching history.
- Show only useful state. Say `No reviews due today` instead of exposing a
  zero-valued review calculation. Show `new`, `due`, or `weak-item` beside
  each learning item.
- Sequence work as `Now`, `Next`, and `If time remains`; do not make five
  equal-looking tasks compete for attention.
- Give every block one concrete completion condition. Do not use motivational
  filler, long explanations, or internal implementation terminology.
- Keep the building block honest. If no backlog is connected, show one clear
  setup decision rather than inventing a project or presenting a list of
  generic tasks.
- End with lightweight response controls such as `done`, `skip`, `shorten`,
  `energy low`, and a rating for completed reviews.

## Slack formatting profile

The current cron and gateway delivery path sends Slack text, so use Slack
`mrkdwn` rather than emitting Block Kit JSON. Slack reliably supports bold,
italics, strikethrough, inline code, block quotes, numbered/bulleted lists,
emoji, links, and channel references. Use channel-link syntax when an ID is
known, for example `<#C0C1JU79PA5|#communication>`.

- Use `*bold*` for section names and the single most important action.
- Use backticks for short controls, statuses, durations, and item IDs.
- Use `>` for the day's win, a warning, or one memory cue.
- Use `•` for supporting details and numbered lists only for an intentional
  sequence.
- Use a consistent emoji plus a text label, such as `🔁 *DUE*` or
  `✨ *NEW*`; never rely on color or emoji alone.
- Separate major sections with a short Unicode rule such as
  `────────────────────`. Do not use Markdown tables, HTML, CSS, task-list
  checkboxes, or fake columns; they do not render reliably in Slack messages.
- Do not imply that buttons, collapsible sections, colored cards, or actual
  Block Kit dividers exist unless the delivery integration explicitly supports
  structured blocks. Until then, use text commands as controls.
- For a standalone building delivery, begin with `🏗️ *BUILDING* · DD Mon
  YYYY · \`Asia/Kolkata\`` and a divider before the outcome. End with one
  explicit instruction to reply in that message's thread. Do not combine a
  building block with news or another workflow.

The stable layout is intentional: repeated landmarks reduce search effort,
while the win statement, one start action, and one memory cue support
orientation and retrieval. Keep the information; change its hierarchy.

## Output contract

Use this production format. Do not include `TEST`, implementation caveats,
planner internals, or apologies in the user-facing message.

```text
☀️ *DAILY GUIDE* · DD Mon YYYY · `Asia/Kolkata`
> *Today's win:* [one sentence describing the meaningful outcome]

*⏱ TIME MAP*
`20m` News → `25m` Communication → `75m` DSA → `60m` System Design → `60m` Building
*Total:* `4h` · *Focus:* [the first meaningful action]

*▶ START HERE* → [first channel or action]

────────────────────
*1 · NEWS* · `20m` · [channel or link]
*Goal:* [one-line outcome]
*Plan:* [digest or one compact action]
*Done when:* [clear completion condition]

────────────────────
*2 · COMMUNICATION* · `25m` · #communication
*Goal:* [one-line communication outcome]
*Plan:* `5m` warm-up → `20m` primary exercise
*Warm-up:* [small retrieval or articulation task]
*Primary:* [exercise with audience, goal, and output]
*Done when:* [observable output]

────────────────────
*3 · DSA PROBLEM-SOLVING* · `75m` · #problem-solving
*Pace:* `N/19` this week · `N` remaining · target `[date]`
*Review:* [No reviews due today | N minutes due]
*New:* `N minutes` · *Buffer:* `N minutes`

`✨ NEW` · [DSA item] · `time`
• *Recall first:* [one prompt before opening notes]
• *Done when:* [attempt, explanation, or test output]

────────────────────
*4 · SYSTEM DESIGN* · `60m` · #system-design
`🔁 DUE` / `✨ NEW` · [system-design item] · `time`
• *Recall first:* [one prompt before opening notes]
• *Done when:* [explanation, design checkpoint, or tradeoff]

*IF TIME REMAINS*
`✨ NEW` · [next item] · `time`

> *Memory cue:* [one short principle to retrieve again later]

────────────────────
*5 · BUILDING* · `60m`
*Goal:* [one concrete deliverable]
*Done when:* [observable output]
If no backlog: `Needs one project choice before this block can be planned.`

────────────────────
*✅ QUICK CONTROLS*
`done [block]` · `skip [item]` · `shorten` · `energy low`
For reviews: `rate [item] [again|hard|good|easy]` plus
`outcome [attempted|solved|understood|recalled|mastered]`

*Next due:* [date/item, or `none yet`]
```

For every learning item, label it `due`, `new`, or `weak-item`. Show the
review budget and used minutes when the planner provides them. At the end,
state what is next due; do not report completion until the user confirms it.

## State and scheduling boundary

The durable review state is `~/.hermes/state/learning.json`. The shared daily
execution state is `~/.hermes/state/daily.json`; it records only planned
blocks, completion status, energy, and short notes. The local planner is
available for offline testing at
`~/.hermes/skills/daily-guide/scripts/daily_plan.py` and the state helper is at
`~/.hermes/skills/daily-guide/scripts/daily_state.py`.

For an explicit daily control, use the deterministic helper and then read back
the day's record:

```text
python3 ~/.hermes/skills/daily-guide/scripts/daily_state.py \
  --state ~/.hermes/state/daily.json complete --date YYYY-MM-DD --block dsa
python3 ~/.hermes/skills/daily-guide/scripts/daily_state.py \
  --state ~/.hermes/state/daily.json show --date YYYY-MM-DD
```

Use `skip`, `shorten`, or `energy low|normal|high` as appropriate. A thread
reply belongs to the block that created it; if a reply does not identify a
block or item clearly, ask before changing state. The learning skill owns
ratings and outcomes; this skill owns daily execution status.

Do not create or modify cron jobs from this skill. The current approved setup
keeps delivery separated by purpose: news to `C0C20J9N604`, communication to
`#communication`, DSA to `#problem-solving`, system design to `#system-design`,
and building to `C0C1FDGBCF9`. Do not collapse these into one message unless
Rahil explicitly chooses that UX after seeing the separate-channel routine in
use.
