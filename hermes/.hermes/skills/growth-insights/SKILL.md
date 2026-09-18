---
name: growth-insights
description: Deliver sourced, personalized book insights and turn them into small actions and spaced recall for Rahil's personal growth.
license: MIT
metadata:
  hermes:
    tags: [Personal-Agent, Books, Motivation, Growth]
    related_skills: [personal-recall, spaced-repetition, daily-guide]
---

# Growth Insights

Give Rahil one useful, sourced idea from a book or his notes and help him apply
and retain it. The purpose is practical personal growth, not motivational quote
spam or shallow daily book summaries.

This skill owns book-derived insights and their application state. It does not
own the personal-memory log, general learning curricula, health tracking,
finance, or life-admin reminders.

## Sources and grounding

Use sources in this order:

1. Rahil's Obsidian highlights and book notes.
2. Books he says he is reading or has completed.
3. Books he explicitly adds to a queue.
4. A deliberately curated personal-growth reading list.
5. Reliable web material when research is explicitly needed.

Every persisted insight must name its source and source type. Include an
Obsidian path, chapter, or page when available. Treat page numbers and
quotations as unknown unless directly present in the source. Prefer concise
paraphrases; do not invent quotations or claim to have read unavailable book
content.

Machine-readable state:

    ~/.hermes/state/life/insights.json

Deterministic helper:

    ~/.hermes/skills/personal-recall/scripts/life_state.py

Long book notes remain in Obsidian. The state file stores only selection,
application, repetition, and source metadata.

## Insight record

Store:

- book;
- one atomic idea;
- why it matters specifically to Rahil;
- one small application;
- source and source type;
- optional note path, chapter, or page;
- shown history, application status, rating, and next review date.

An insight should be small enough to recall in one sentence. Split unrelated
ideas into separate records.

Add or update an insight with:

    python3 ~/.hermes/skills/personal-recall/scripts/life_state.py \
      add-insight --book BOOK --idea IDEA --source SOURCE \
      --source-type obsidian --why-for-rahil WHY --application ACTION

The helper deduplicates by normalized book and idea.

## Selection

Choose with:

    python3 ~/.hermes/skills/personal-recall/scripts/life_state.py \
      next-insights --date YYYY-MM-DD --limit 1

Due insights outrank new insights. Never select a not-due active insight merely
because it is convenient. Never select rejected or archived insights.

Mark an insight shown only after it was actually delivered:

    python3 ~/.hermes/skills/personal-recall/scripts/life_state.py \
      show-insight ITEM_ID --date YYYY-MM-DD

This schedules the first retrieval after three days, preventing the same idea
from appearing again immediately.

## Daily experience

Use this compact format:

    📚 *GROWTH INSIGHT* · DD Mon YYYY
    *Book:* [title]
    *Insight:* [one-sentence paraphrase]
    *Why it matters to you:* [specific connection]
    *Apply today:* [one action requiring roughly 5–15 minutes]
    > *Recall:* [one question Rahil can answer later]
    *Source:* [book, chapter/page, or Obsidian path]

Do not send a full book summary each day. A weekly synthesis may later connect
several applied insights, but it is outside the first version.

Motivation must be tied to Rahil's real goals, current obstacles, and evidence
of progress. Avoid guilt, exaggerated praise, poster language, and claims that
one insight will transform his life.

## Response and retention

After Rahil tries or discusses an idea, accept:

- recall rating: forgot, partial, remembered, or effortless;
- application status: not-started, planned, tried, applied, or rejected;
- an optional short note about what happened.

Persist with:

    python3 ~/.hermes/skills/personal-recall/scripts/life_state.py \
      review-insight ITEM_ID RATING --date YYYY-MM-DD \
      --application-status STATUS --note NOTE

The rating uses the same adaptive interval engine as personal recall and the
existing learning system. Rejected insights stop resurfacing. Applied insights
continue at longer maintenance intervals when retaining them remains useful.

Do not infer application from agreement or enthusiasm. Only update application
status from an explicit response, and report persistence only after read-back.

## Proactive limits

- At most one growth insight per day.
- One idea, one application, one recall question.
- Do not create an independent cron during implementation.
- Later, the life-agent coordinator may combine one insight with the personal
  recall queue in one message.
- If no grounded insight is available, say so instead of inventing one.

## Test boundary

Before scheduling:

1. Add one insight from an actual Obsidian note or user-provided source.
2. Select it as new and mark it shown.
3. Verify it cannot be selected again before its due date.
4. Review it and verify the interval changes.
5. Add the same idea again and verify it updates rather than duplicates.
6. Reject an insight and verify it no longer appears.
7. Restart Hermes and confirm the state remains readable.
