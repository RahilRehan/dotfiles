# Personal dotfiles

Homebrew installs applications and CLI tools, mise supplies Node, and chezmoi
manages configuration. Custom skills live in `skills/` and are installed with
the skills.sh CLI. No Stow, Makefile, or MCP registry.

## Set up a Mac

Install Apple's Command Line Tools and [Homebrew](https://brew.sh), then:

```sh
git clone https://github.com/RahilRehan/dotfiles.git ~/personal/dotfiles
cd ~/personal/dotfiles
bash install.sh
```

The bootstrap installs missing packages without upgrading existing ones, applies
the configuration, installs mise's Node LTS, and installs the selected skills
for Codex, Claude Code, and Cursor. It does not uninstall other
software, change your login shell, or manage application accounts. macOS already
uses zsh by default. Sign in to the harnesses separately.

## What belongs where

| Source | Owns |
|---|---|
| `Brewfile` | CLI tools, plain Micro, Codex, Claude Code, Cursor, T3 Nightly, and the selected Mac apps |
| `home/` | Zsh, Git, Starship, bat, mise, shared harness instructions, and selected T3 server defaults |
| `home/dot_config/mise/config.toml` | Global Node LTS; project mise files can override it |
| `skills/` | Custom skill sources and pinned upstream skill installation |
| Local files | Git identities, machine overrides, credentials, sessions, and application data |

Homebrew's rolling releases and `node = "lts"` reproduce the selected tools and
configuration, not exact historical versions. Pin Node in a project's mise file
when the project needs an exact version.

Login shells put mise's shims on PATH so harness commands can find Node without
loading interactive shell widgets. Interactive shells also enable fzf, zoxide,
direnv, autosuggestions, highlighting, and the Starship prompt.

## Daily maintenance

```sh
chezmoi edit ~/.zshrc         # Edit the source of a managed file
chezmoi diff                 # Review pending configuration changes
chezmoi apply                # Apply source changes to this machine
brew bundle --no-upgrade --file=Brewfile
mise install
bash skills/install.sh       # Reinstall skills after editing their source
bash check.sh
```

Run these from the checkout. Commit and push source changes normally. On another
configured machine, `chezmoi update` pulls and applies committed configuration;
rerun `bash install.sh` there when package or runtime requirements change.
The bootstrap is currently tested on macOS; Linux/WSL installation comes later.

## Local settings

Chezmoi disables T3 product telemetry and connection tracing in shell startup
and merges the opt-out into `~/.t3/service.env` without tracking its other
variables. Restart T3's service and desktop app after first applying this change.

Put machine-specific shell settings in `~/.config/zsh/local.zsh`. It is never
managed by chezmoi. Login-only settings can go in `profile.local.zsh` in that
same directory. MCP connections remain outside this repository.

## Shared harness instructions

The broader T3 Code configuration review is recorded in
[Personal T3 Code setup](docs/t3-setup.md).
Its selected server defaults are merged by chezmoi into T3's settings file,
preserving local provider/account configuration. Device appearance and chat
preferences remain a checklist in that guide.

Edit `home/dot_config/agents/AGENTS.md`, then run `chezmoi apply`. This is the
single source of personal defaults. Chezmoi installs it at
`~/.config/agents/AGENTS.md` and creates these symlinks:

- `~/.codex/AGENTS.md`
- `~/.claude/CLAUDE.md`
- `~/.cursor/rules/defaults.mdc`

The `alwaysApply: true` frontmatter enables Cursor's local user rule; Claude
Code and Codex consume the same file as Markdown. The actual instructions are
in the file, so routine terminal commands need no skill discovery or file read
by the model. Keep detailed procedures in skills and repository-specific
instructions in the repository. A nonempty `~/.codex/AGENTS.override.md` replaces
the global Codex file; `check.sh` flags it.

Start fresh harness sessions after changing defaults. These files configure
local sessions on each bootstrapped machine; they are not Cursor account or
cloud synchronization.

`bash check.sh` checks the link targets and shared contents. Confirm actual
loading in a fresh session by asking the harness to summarize its terminal
defaults without using tools. For Claude Code, `/memory` also lists loaded files;
for Cursor, check Customize → Rules. Shell checks alone do not prove that a
particular harness version has injected the instructions into model context.
Fresh Claude and Cursor CLI probes passed without tool calls during this setup.
The installed Cursor CLI inherits the home rule for projects beneath the home
directory; an outside-home project needs its own link to the shared rule.

## Skills

`skills/terminal-toolkit/SKILL.md` teaches noninteractive file search, bounded
file reading, project lookup, and authorized direnv execution. Edit its source
here, then rerun `bash skills/install.sh`; skills.sh owns the installed copies
and harness links. There is no separate custom synchronization layer.
Codex and local Cursor sessions discover the shared `~/.agents/skills` copy;
skills.sh links Claude Code to it. These are local installs, not Cursor cloud sync.

`skills/upstream.tsv` records the retained Archify Review, Excalidraw Diagram
Generator, and Remove Deadcode skills at verified Git revisions. It also records
the complete pstack bundle, with `poteto-mode` as
the bundle's presence check. No pstack plugin or always-on mode is required.
The installer uses skills CLI 1.7.0 through mise's Node and npm's download cache. To update a
retained skill, review a new upstream revision and change its URL in that file.
It installs only the three named harness targets and does not enable MCPs.

`bash check.sh` verifies installed skill contents and runs isolated toolkit
checks, including filenames with spaces/leading dashes, ignored files, and
direnv authorization. Its temporary zoxide and direnv data are removed afterward.

Git uses three optional, untracked identity files:

| File | Applies to |
|---|---|
| `~/.gitconfig.local` | Fallback |
| `~/.gitconfig-personal` | Repositories under `~/personal/` |
| `~/.gitconfig-work` | Repositories under `~/workplace/` |

Create the files you need with:

```sh
git config --file ~/.gitconfig-personal user.name 'Your Name'
git config --file ~/.gitconfig-personal user.email 'you@example.com'
```

See [the terminal toolkit](docs/using-your-terminal.md) for tool usage.
