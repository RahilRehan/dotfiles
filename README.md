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
| `home/` | Zsh, Git, Starship, bat, and mise configuration |
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

Put machine-specific shell settings in `~/.config/zsh/local.zsh`. It is never
managed by chezmoi. Login-only settings can go in `profile.local.zsh` in that
same directory. MCP connections remain outside this repository.

## Skills

`skills/terminal-toolkit/SKILL.md` teaches noninteractive file search, bounded
file reading, project lookup, and authorized direnv execution. Edit its source
here, then rerun `bash skills/install.sh`; skills.sh owns the installed copies
and harness links. There is no separate custom synchronization layer.
Codex and local Cursor sessions discover the shared `~/.agents/skills` copy;
skills.sh links Claude Code to it. These are local installs, not Cursor cloud sync.

`skills/upstream.tsv` records the retained Archify Review, Excalidraw Diagram
Generator, and Remove Deadcode skills at verified Git revisions. The installer
uses skills CLI 1.7.0 through mise's Node and npm's download cache. To update a
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
