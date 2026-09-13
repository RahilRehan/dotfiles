# Agent setup

This directory is intentionally empty by default. It contains the source of
truth for optional skills and MCP servers used by the agents you actually run.

## Skills

Put a skill source under `ai/skills/<name>/SKILL.md`, then install it with the
skills CLI for the agents you use:

```bash
zsh -ic 'npx skills add ./ai/skills/<name> -g -a cursor -a claude-code -a codex -y'
```

The CLI stores the canonical installed copy under `~/.agents/skills/` and may
link it into an agent-specific directory. The repository remains the editable
source; reinstall after changing a skill. Built-in Codex skills under
`~/.codex/skills/.system/` are managed by Codex and do not belong here.

## MCP servers

Edit only [`mcp/servers.json`](mcp/servers.json), then run:

```bash
make ai-sync
```

The script generates Cursor and Claude JSON files and a marked managed block in
`~/.codex/config.toml`. An empty `servers` object is valid and intentionally
removes the old managed servers. Codex's own `node_repl`, computer-use, and
plugin settings remain outside that block.

Secrets belong in `~/.config/ai/secrets.env`, which is not tracked. Do not put
API keys in this repository or in generated MCP files.

## Supported agents

The managed targets are Cursor, Claude Code, and Codex. Pi is no longer part of
this setup. To add another harness later, add one generator adapter and one
explicit target; do not duplicate server definitions by hand.

The dotfiles installer installs these harnesses through Homebrew and runs
`make ai-sync`. Cursor and Claude Code receive symlinks to the generated JSON;
Codex keeps its existing configuration and receives only the marked MCP block.
