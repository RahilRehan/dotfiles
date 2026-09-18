# Applications policy

Use Homebrew Cask for applications that should be reproducible on a new Mac.
Keep application data, login state, caches, and secrets out of this repository.
The Brewfile records what to install; dotfiles record only portable settings.

## Managed by this repository

These are already declared in `Brewfile`:

| Application | Package | Why |
|---|---|---|
| Codex | `codex` | AI coding harness |
| Claude Code | `claude-code` | AI coding CLI |
| Cursor desktop | `cursor` | Editor and desktop harness |
| Cursor terminal agent | `cursor-cli` | `cursor-agent` command |

Hermes Agent is managed through the official native installer from the
dotfiles workflow (`make hermes-install`), not Homebrew. Its editable settings
and ignored runtime home are managed by the `hermes/` package.

The AI MCP source is [`../ai/mcp/servers.json`](../ai/mcp/servers.json). Run
`make ai-sync` after changing it. The generated Cursor and Claude files are
linked into their home directories; Codex receives a marked block in its
existing config.

## Good Homebrew candidates

Add these to `Brewfile` only when you confirm you use them regularly:

- `docker-desktop` for Docker-based projects.
- `iterm2` for the terminal application.
- `android-studio` for React Native Android development.
- `obsidian`, `google-chrome`, `slack`, or `localsend` if they are part of your
  daily workflow.

Homebrew Cask handles downloading and upgrading these consistently. It does
not manage their account data or application preferences unless those settings
are separately linked into this repository.

## Keep manual or vendor-managed

- Xcode is best installed through the Mac App Store or Apple's developer tools.
- Microsoft Office, Adobe Acrobat, DaVinci Resolve, Blackmagic tools, and
  OneDrive are vendor suites with their own update and licensing workflows.
- Falcon, Qualys, Securden, Self-Service, and other corporate tools should be
  managed by the organisation's installer.
- ChatGPT, Claude desktop, OpenCode desktop, and similar auto-updating apps may
  be installed through their vendors unless you specifically want Homebrew to
  own their update cycle.

Do not put every application in the Brewfile just because a cask exists. Add a
cask when reinstalling it is a repeated need and Homebrew's update behaviour is
acceptable. Keep one source of installation for each app; do not mix a manual
copy and a Homebrew cask for the same application.

## Rebuild workflow

```bash
brew bundle --file=Brewfile
make stow
make ai-sync
make hermes
```

The commands restore packages and links. Sign-ins, project data, extensions,
and caches remain local to each application.
