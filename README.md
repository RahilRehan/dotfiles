# Personal dotfiles

A small macOS terminal setup managed with GNU Stow. It is designed around a
simple loop: move to a project, find code, inspect changes, and run the right
project tools.

Start with [the terminal toolkit](docs/using-your-terminal.md). It explains
what every default tool does and when it is worth using. [Application policy](docs/applications.md)
explains what belongs in Homebrew and what should stay vendor-managed.

## Install

```bash
git clone https://github.com/RahilRehan/dotfiles.git ~/personal/dotfiles
cd ~/personal/dotfiles
bash install.sh
```

The installer installs the small default Brewfile, links the tracked configs,
installs Micro's preview plugin and the Codex, Claude Code, and Cursor
harnesses, including Cursor's separate terminal agent, links their shared AI
configuration, sets zsh as the login shell, and asks for Git identities when
required.

## Default tools

| Purpose | Tool |
|---|---|
| Search text and file names | `rg`, `fd`, `fzf` |
| Return to familiar directories | zoxide (`z`) |
| Read files | `bat` |
| Review and manage Git changes | Git, delta, lazygit (`lg`) |
| Use project-specific runtimes and environment variables | mise, uv, direnv |
| Show directory and Git state | Starship |

These tools are deliberately explicit: standard commands such as `cat`, `ls`,
`rm`, and `ps` keep their normal behaviour.

## Structure

Each top-level config directory is a Stow package that mirrors `$HOME`.

```
zsh/       shell options, completions, aliases, and tool hooks
starship/  prompt
git/       Git defaults and global ignore file
bat/       readable file output theme
mise/      project runtime defaults (currently Node LTS)
micro/     Micro editor settings and preview plugin repository
ai/        optional skills and MCP source files
```

Add an optional tool back only after it solves a repeated problem for you.

## Git identity

Git chooses identities by repository location. These untracked files hold the
personal details:

| File | Used for |
|---|---|
| `~/.gitconfig.local` | Repositories outside the folders below |
| `~/.gitconfig-personal` | Repositories under `~/personal/` |
| `~/.gitconfig-work` | Repositories under `~/workplace/` |

## Maintenance

Use `make lint` after editing shell files. Use `make stow` to refresh links.
The Brewfile is a list of tools you actively want on every new machine, not a
wish list.

## Linux migration

The tracked Stow packages are the portable core of this setup. The current
`install.sh` and `Brewfile` target macOS; a future VPS setup should keep the
same `zsh`, `starship`, `git`, `bat`, `mise`, and `micro` packages while using
the VPS distribution's package manager and Docker Engine instead of macOS
casks and Docker Desktop.
