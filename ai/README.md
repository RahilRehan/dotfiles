# AI Tools

Config for **Cursor**, **Claude Code**, **Codex**, and **Pi**.

| What | Tool |
|------|------|
| **Skills** | [`npx skills`](https://skills.sh/docs) |
| **MCP servers** | `mcp/servers.json` + `make ai-sync` |

Default agents for this setup: **cursor**, **claude-code**, **codex**, **pi**.

```bash
make -C ~/personal/dotfiles ai-sync   # MCP only
npx skills ls -g                      # list installed skills
```

---

## Structure

```
ai/
├── skills/                   # Optional custom skill sources
├── skills-lock.json          # Optional — commit to restore on new machines
├── mcp/servers.json          # MCP definitions + per-tool routing
├── bin/ai-sync               # Generate MCP configs
├── .cursor/mcp.json          # Generated → stowed to ~/.cursor/
├── .claude/mcp.json          # Generated → stowed to ~/.claude/
├── .pi/agent/mcp.json        # Generated → stowed to ~/.pi/agent/
└── .config/ai/
    └── secrets.env.example
```

Codex MCP is written to a managed block in `~/.codex/config.toml`.

---

## Skills

All skills are managed with the [skills.sh](https://skills.sh/docs) CLI. Full reference: `npx skills --help`.

### Local skills

`ai/skills/` is where **your** skills live in dotfiles. Community skills from [skills.sh](https://skills.sh) install straight from GitHub — local skills you author yourself go here.

```
ai/skills/
└── python-senior-dev/
    ├── SKILL.md              # required
    ├── tdd-workflow.md       # optional references
    └── ...
```

**Create a new skill:**

```bash
cd ~/personal/dotfiles/ai
npx skills init my-skill       # creates skills/my-skill/SKILL.md (or run from skills/)
# edit skills/my-skill/SKILL.md
```

**Install to all four agents** (run from `ai/` or use absolute path):

```bash
cd ~/personal/dotfiles/ai

# All skills in ai/skills/
npx skills add ./skills -g \
  -a cursor -a claude-code -a codex -a pi -y

# Or a single skill
npx skills add ./skills/python-senior-dev -g \
  -a cursor -a claude-code -a codex -a pi -y
```

This copies into `~/.agents/skills/<name>/` and symlinks each agent dir to that canonical copy. The dotfiles repo stays the source of truth — re-run `npx skills add` after you edit a local skill.

**Update a local skill after editing:**

```bash
npx skills remove python-senior-dev -g -y
npx skills add ./skills/python-senior-dev -g \
  -a cursor -a claude-code -a codex -a pi -y
```

`npx skills update` does not track local paths — only GitHub-installed skills.

**List what's installed:**

```bash
npx skills ls -g
```

### Community skills (skills.sh)

```bash
# Browse a repo without installing
npx skills add vercel-labs/agent-skills --list

# One skill, all four agents, global
npx skills add vercel-labs/agent-skills \
  -g -s frontend-design \
  -a cursor -a claude-code -a codex -a pi \
  -y

# Search skills.sh
npx skills find typescript

# All skills, all agents
npx skills add vercel-labs/agent-skills -g --all
```

### List, update, remove

```bash
npx skills ls -g
npx skills check               # GitHub skills only; skips local paths
npx skills update -g           # GitHub skills only
npx skills remove my-skill -g -y
```

### Restore on a new machine

Local skills travel with dotfiles — reinstall after clone:

```bash
cd ~/personal/dotfiles/ai
npx skills add ./skills -g -a cursor -a claude-code -a codex -a pi -y
```

Community skills: commit `skills-lock.json`, then:

```bash
cd ~/personal/dotfiles/ai
npx skills experimental_install -y
```

### Where skills land

Canonical copy in `~/.agents/skills/<name>/`, with symlinks to each agent ([docs](https://vercel-labs-skills.mintlify.app/guides/installation-methods)):

| Agent | Global path |
|-------|-------------|
| Cursor | `~/.cursor/skills/<name>` |
| Claude Code | `~/.claude/skills/<name>` |
| Codex | `~/.agents/skills/<name>` |
| Pi | `~/.pi/agent/skills/<name>` |

### Migrating old symlinks

If skills were symlinked directly to `ai/skills/` (old `ai-sync` behavior), remove stale links and reinstall:

```bash
rm ~/.cursor/skills/<name> ~/.claude/skills/<name> \
   ~/.agents/skills/<name> ~/.pi/agent/skills/<name>

npx skills add ~/personal/dotfiles/ai/skills -g \
  -a cursor -a claude-code -a codex -a pi -y
```

### Flags & env

| Flag | Purpose |
|------|---------|
| `-g` | Global install (`~/.agents/skills/`) |
| `-a <agent>` | Target agent (`cursor`, `claude-code`, `codex`, `pi`, or `*`) |
| `-s <skill>` | Pick skills by name |
| `-y` | Skip prompts |
| `--copy` | Copy files instead of symlinking |
| `--all` | All skills + all agents |

`DISABLE_TELEMETRY=1` — opt out of [skills.sh](https://skills.sh/docs) telemetry.

---

## MCP servers

Edit `mcp/servers.json`, then `make ai-sync`.

| `tools` value | Written to |
|---------------|------------|
| `cursor` | `~/.cursor/mcp.json` |
| `claude` | `~/.claude/mcp.json` |
| `pi` | `~/.pi/agent/mcp.json` |
| `codex` | `~/.codex/config.toml` |

Secrets: `cp .config/ai/secrets.env.example ~/.config/ai/secrets.env`

---

## Plugins

Installed per tool — not managed here. See [skills.sh](https://skills.sh/docs) for skills; use Claude `/plugin`, Codex `/plugins`, or Pi `/claude:plugin` for full plugin bundles.

**Requires:** `jq` (MCP sync). Pi MCP needs `pi-mcp-adapter` in `~/.pi/agent/settings.json`.
