---
name: x-news-digest
description: Search monitored X account lists and produce a concise, source-linked news digest with startup, engineering, and content-creation relevance.
---

# X News Digest

Use this skill when Rahil asks for an X news digest, monitored-account update,
company news, people news, or content ideas based on recent X activity.

## Source lists

The source lists are stored under `~/.hermes/news/x/`:

- `companies.yaml` — the current 23-account company list.
- `people.yaml` — currently empty; tell Rahil to add accounts before searching it.

When using the companies list, use these handles in three batches because
`x_search` accepts at most 10 allowed handles per request:

1. `GoogleAI`, `claudeai`, `GeminiApp`, `grok`, `deepseek_ai`, `MistralAI`,
   `SpaceXAI`, `AnthropicAI`
2. `AIatMeta`, `huggingface`, `GoogleDeepMind`, `OpenAI`, `Apple`,
   `CrowdStrike`, `Microsoft`, `awscloud`
3. `nvidia`, `Cloudflare`, `Google`, `Azure`, `github`, `Tesla`, `Meta`

For a different list, use its handles when available. Never invent accounts.

## Search and selection

Search the requested lookback window, defaulting to the last 24 hours. Run the
account-batch searches in parallel when the runtime supports parallel tool
calls, then merge and deduplicate the results. Ask each search for only the
highest-signal items (normally no more than five per batch). Prefer original
posts over reposts. Treat source claims as claims unless independently verified.

Run each of the three company batches at most once. If an `x_search` call
returns an error or times out, continue with the batches that completed, do not
retry the failed batch, and report the reduced coverage in the final line.

For every selected post, preserve the post's published date and time. Display
it in IST (`Asia/Kolkata`) and include the original X timestamp when available.
Never invent a timestamp: use `time unavailable` if the search result does not
provide one. Label the source as `Original`, `Quote-post`, `Reply`, `Repost`, or
`Secondary summary` so a Grok-generated summary is not mistaken for the account's
own announcement.

For the companies list, keep:

- New product, model, or platform launches
- Major technical announcements
- Important research papers or benchmarks
- Funding, acquisitions, partnerships, or leadership changes
- Pricing, API, policy, or developer-platform changes
- Security incidents or outages
- Regulatory or market news
- Developments likely to affect developers, businesses, or Rahil's work
- Strong technical discussions or meaningful reactions

Ignore routine reposts, generic marketing, ordinary hiring, support replies,
event reminders without new information, duplicate announcements, engagement
bait, vague inspiration, and minor updates without practical impact. Keep hiring
or minor updates only when strategically important.

Rank items by practical importance to Rahil and a technology audience in India:
startup opportunities and real customer problems, low-level engineering,
infrastructure, system design, developer tools, open source, reality-versus-
hype analysis, Instagram content potential, career resilience, India access or
pricing, local hiring and startup implications, and India-relevant regulation.

## Output

Start with this standalone Slack workflow header, then a short divider:

```text
📰 *X NEWS* · DD Mon YYYY · `Asia/Kolkata`
*Window:* [start IST]–[end IST]
────────────────────
```

Return no more than five items in these sections:

1. **Top developments**
2. **Worth watching**
3. **Content ideas for me**

Each selected item should include:

`[01] Headline — Account — DD Mon YYYY, h:mm AM/PM IST — Source type`

- **What happened:** one or two concise sentences
- **Why it matters in India:** practical implication for Indian developers,
  builders, companies, or tech professionals
- **Source:** direct X link
- **Content angle:** a reality-versus-hype or useful explainer angle for an
  Indian technology audience

Clearly separate facts from Hermes's interpretation. Include direct citations
when returned by `x_search`. If no meaningful news was found, say so instead
of filling the digest. Do not post, reply, like, DM, or take any X account action.

Keep the response compact. Do not narrate the three searches or list every
account that was quiet. End with one line: `Coverage: 23 accounts checked ·
window: <start IST>–<end IST> · <number> items selected.`

## Invocation examples

- “Run my companies X news digest for the last 24 hours.”
- “What changed in my companies list this week? Add Instagram ideas.”
- “Run the people digest.”
