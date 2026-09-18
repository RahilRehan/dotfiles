---
name: personal-recall
description: Capture, retrieve, and repeatedly resurface Rahil's personal memories, experiences, people details, ideas, and media using adaptive recall.
license: MIT
metadata:
  hermes:
    tags: [Personal-Agent, Memory, Recall, Life]
    related_skills: [spaced-repetition, growth-insights, daily-guide]
---

# Personal Recall

Help Rahil retain meaningful parts of his life, not only academic material.
Capture durable memories, retrieve them accurately, and resurface them through
repeated active recall. Seeing something once never counts as retained.

This skill owns personal memories. It does not own DSA, system design,
communication exercises, deadlines, financial records, news, or the general
Hermes conversation history.

## Sources of truth

- Machine-readable state:
  ~/.hermes/state/life/memories.json
- Deterministic helper:
  ~/.hermes/skills/personal-recall/scripts/life_state.py
- Obsidian: optional detailed reflections or long-form notes.
- Hermes memory: only compact durable preferences and profile facts, not the
  complete personal-event history.

Do not duplicate every memory into Obsidian. Create or link an Obsidian note
only when the memory deserves human-readable detail.

## What belongs here

Examples include movies and shows, books and articles, trips, places, events,
important conversations, people details, decisions and their reasoning,
startup ideas, lessons from mistakes, and meaningful experiences.

Temporary chatter does not belong here. Credentials, authentication secrets,
private keys, full payment-card data, and similarly dangerous secrets must
never be stored. For sensitive personal or household information, capture only
when Rahil clearly asks to remember, log, or track it.

## Capture contract

Persist a memory when:

- Rahil explicitly says remember, save, log, track, or equivalent;
- he answers a capture question in a personal-recall thread; or
- the message unmistakably describes something he wants the life agent to
  retain.

If intent is uncertain, ask one short question before writing. Do not claim a
memory was stored until the helper completed and the record was read back.

Capture the smallest useful record:

- kind;
- title;
- date the event occurred;
- Rahil's own summary or interpretation;
- optional details, people, tags, source-note path, and importance.

Use the event date supplied by Rahil. Resolve relative dates using
Asia/Kolkata and the actual current date. Do not silently invent a date.

Run:

    python3 ~/.hermes/skills/personal-recall/scripts/life_state.py \
      capture-memory --kind KIND --title TITLE --occurred-on YYYY-MM-DD \
      --summary SUMMARY

The helper merges the same kind, title, and event date instead of producing a
duplicate. A repeated activity on a different date remains a separate memory.

## Retrieval contract

Search structured state before relying on general chat history. For a query:

    python3 ~/.hermes/skills/personal-recall/scripts/life_state.py \
      search-memories QUERY

Answer with the remembered date, Rahil's own recollection, and the Obsidian
source path when one exists. Separate stored facts from any external
information. Never replace Rahil's memory with a web synopsis.

If no matching record exists, say so plainly. Do not fabricate a memory from a
likely event or similarly named item.

## Repeated recall

Every new memory starts with a first recall due the following day. Due memories
are selected with:

    python3 ~/.hermes/skills/personal-recall/scripts/life_state.py \
      due-memories --date YYYY-MM-DD --limit 3

Ask before revealing the stored answer. Vary the retrieval cue over time:

- identify the item from the date or context;
- state the central idea or event;
- recall two supporting details;
- explain why it mattered;
- connect it to another experience or decision.

Use only cues supported by the stored record. Do not turn personal recall into
trivia about details Rahil never recorded.

Accept these explicit ratings:

- forgot;
- partial;
- remembered;
- effortless.

They reuse the shared spaced-repetition interval algorithm internally:
forgot maps to again, partial to hard, remembered to good, and effortless to
easy. Forgotten items return quickly; successful items move toward long-term
maintenance. Important memories remain available even after repeated success.

After Rahil answers, treat the answer as coaching content until he gives or
confirms a rating. Then run:

    python3 ~/.hermes/skills/personal-recall/scripts/life_state.py \
      review-memory ITEM_ID RATING --date YYYY-MM-DD --answer ANSWER

Read the record back before reporting the next recall date.

## Proactive limits

- Select at most three due personal memories in one day initially.
- Prefer high-importance memories, then forgotten memories, then the oldest
  due date.
- Do not send one independent notification per memory.
- Do not repeat a memory before it is due merely to fill a message.
- A missed item remains due; it is not marked remembered.
- Scheduling belongs to the life-agent coordinator and is added only after a
  manual Slack test passes.

## Slack interaction

Keep the first recall prompt compact:

    🧠 *PERSONAL RECALL* · DD Mon YYYY
    🔁 *DUE* · [memory type and cue]
    > [one retrieval question without the answer]

    Reply naturally, then add:
    rating: forgot|partial|remembered|effortless

After the reply, briefly show what was remembered correctly, fill only the
important missing detail, and report the exact next recall date after verified
persistence.

## Test boundary

Before scheduling:

1. Capture one real memory from Slack.
2. Retrieve it by title and by a detail.
3. Capture it again and verify that it updates rather than duplicates.
4. Review it with forgot and verify a near due date.
5. Review it successfully and verify a longer interval.
6. Restart Hermes and retrieve the same record.
7. Reject an ambiguous capture without changing state.
