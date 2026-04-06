# Modern Developer Dotfiles

> A curated dev environment with **30+ modern CLI tools**, managed with GNU Stow. Built for macOS, testable on Linux via Docker.

**What makes this different?** Most dotfiles repos are config dumps. This one is a **learning resource** — every tool is explained, every config is commented, and there's a [hands-on course](#course) to learn it all in a Docker playground.

## Quick Start

```bash
# Clone and install everything
git clone https://github.com/RahilRehan/dotfiles.git ~/dotfiles
cd ~/dotfiles && bash install.sh

# Or test it first in Docker (no risk to your machine)
make test
```

The install script detects your OS, installs packages, symlinks configs with Stow, sets zsh as default shell, and sets up git user info.

---

## The Toolbox

Every tool here replaces something old and slow with something modern and fast. If you're still using `grep`, `find`, `cat`, `ls`, and `top` — you're leaving speed on the table.

### Shell & Prompt

| Tool | Replaces | Why |
|------|----------|-----|
| [**Starship**](https://starship.rs/) | Powerlevel10k | Cross-shell prompt written in Rust. Works in zsh, bash, fish — same config everywhere. Shows git branch, status, language versions, and execution time. |

### File Operations

| Tool | Replaces | Why |
|------|----------|-----|
| [**bat**](https://github.com/sharkdp/bat) | `cat` | Syntax highlighting, line numbers, git diff markers. Pipe-friendly — falls back to plain text when piped. |
| [**eza**](https://github.com/eza-community/eza) | `ls` | File-type icons, git status per file, tree view. One command (`eza --tree`) replaces `ls -la` + `tree`. |
| [**fd**](https://github.com/sharkdp/fd) | `find` | 5-10x faster, sane syntax (`fd "*.py"` vs `find . -name "*.py"`), respects `.gitignore` by default. |
| [**ripgrep**](https://github.com/BurntSushi/ripgrep) (`rg`) | `grep` | 10-100x faster, searches recursively by default, respects `.gitignore`, better regex. |
| [**sd**](https://github.com/chmln/sd) | `sed` | Find-and-replace with intuitive syntax. `sd 'before' 'after' file` — no escaping nightmares. |
| [**yazi**](https://github.com/sxyazi/yazi) | Finder / `ranger` | Terminal file manager in Rust. Miller columns, vim keys, image previews, bulk operations. `y` wrapper function `cd`s to where you navigated on quit. |

### Search & Navigation

| Tool | Replaces | Why |
|------|----------|-----|
| [**fzf**](https://github.com/junegunn/fzf) | manual piping | Universal fuzzy finder. `ctrl-t` finds files (with bat preview), `alt-c` finds directories (with tree preview), pipes into anything. |
| [**zoxide**](https://github.com/ajeetdsouza/zoxide) | `cd` | Learns your directories. `z proj` jumps to `~/code/my-project` from anywhere. `zi` opens an interactive picker. |
| [**atuin**](https://github.com/atuinsh/atuin) | `ctrl-r` / `history` | Shell history in SQLite. Fuzzy search across sessions with context (directory, exit code, duration). Optional cross-machine sync. |

### Git

| Tool | Replaces | Why |
|------|----------|-----|
| [**delta**](https://github.com/dandavison/delta) | `diff` | Syntax-highlighted diffs with line numbers, side-by-side mode, and word-level change detection. Auto-configured as git's pager. |
| [**lazygit**](https://github.com/jesseduffield/lazygit) | `git add -p` / `git rebase -i` | Full git TUI. Stage individual hunks, interactive rebase, resolve conflicts, cherry-pick — all with single keystrokes. |

### Terminal & Multiplexer

| Tool | Replaces | Why |
|------|----------|-----|
| [**tmux**](https://github.com/tmux/tmux) | multiple terminal windows | Split panes, named sessions that survive SSH disconnects, vim-style navigation. Catppuccin-themed status bar at top. |
| [**iTerm2**](https://iterm2.com/) | Terminal.app | macOS terminal with Natural Text Editing, keyboard text selection, split panes, true color. Catppuccin Macchiato theme via Dynamic Profile. |

### Dev Environment

| Tool | Replaces | Why |
|------|----------|-----|
| [**mise**](https://mise.jdx.dev/) | nvm, pyenv, rbenv, goenv | One tool manages all runtimes. Drop `.mise.toml` in a project to pin Node, Python, Go versions. Team gets same versions automatically. |
| [**direnv**](https://direnv.net/) | manual `export` | Auto-loads `.envrc` when you `cd` into a project (`DATABASE_URL`, `AWS_PROFILE`, etc.). Unloads on leave. |

### System Monitoring

| Tool | Replaces | Why |
|------|----------|-----|
| [**dust**](https://github.com/bootandy/dust) | `du` | Visual disk usage tree sorted by size. Instantly see what's eating your disk. |
| [**duf**](https://github.com/muesli/duf) | `df` | Disk free with color, grouped by filesystem type. |
| [**bottom**](https://github.com/ClementTsang/bottom) (`btm`) | `top` / `htop` | System monitor with CPU/memory/network graphs, process filtering, and cross-platform support. |
| [**procs**](https://github.com/dalance/procs) | `ps` | Process viewer with tree view, keyword search, and colored output. |

### Container & Kubernetes TUIs

| Tool | Replaces | Why |
|------|----------|-----|
| [**lazydocker**](https://github.com/jesseduffield/lazydocker) | `docker ps` / `docker logs` | TUI for Docker. See containers, images, volumes, logs — all in one view. |
| [**k9s**](https://github.com/derailed/k9s) | `kubectl` | TUI for Kubernetes. Navigate pods, view logs, exec into containers, manage resources — without memorizing kubectl flags. |

### Utilities

| Tool | Replaces | Why |
|------|----------|-----|
| [**tldr**](https://tldr.sh/) | `man` | Community-maintained cheat sheets. Shows the 20% of a command you actually use, with real examples. |
| [**just**](https://github.com/casey/just) | `make` (for tasks) | Command runner without Makefile baggage. Define project tasks in a `justfile` with simple syntax. |
| [**glow**](https://github.com/charmbracelet/glow) | reading raw markdown | Renders markdown beautifully in the terminal. Great for READMEs and docs. |
| [**hyperfine**](https://github.com/sharkdp/hyperfine) | `time` | Statistical benchmarking. Compare commands with warmup runs, confidence intervals, and export to JSON/CSV. |


---

## Structure

Each top-level directory is a [GNU Stow](https://www.gnu.org/software/stow/) package — a mirror of `$HOME` that gets symlinked in place.

```
dotfiles/
├── zsh/                          # Shell
│   ├── .zshrc                    #   Thin loader
│   └── .config/zsh/
│       ├── 00-env.zsh            #   XDG dirs, PATH, editor, Homebrew
│       ├── 10-options.zsh        #   History, navigation, completion
│       ├── 20-keybindings.zsh    #   Word style, Option+Arrow navigation
│       ├── 20-plugins.zsh        #   zinit plugin manager + completions
│       ├── 30-completions.zsh    #   Completion styles (menu, colors, cache)
│       ├── 40-aliases.zsh        #   Modern tool aliases (eza, bat, dust, etc.)
│       ├── 50-functions.zsh      #   mkcd, extract, killport, serve
│       ├── 60-tools.zsh          #   Tool hooks (zoxide, atuin, fzf, mise, direnv, yazi, starship)
│       ├── 70-platform.zsh       #   OS dispatch
│       └── platform/
│           ├── macos.zsh         #   flush-dns, macOS aliases
│           └── linux.zsh         #   clipboard compat (pbcopy/pbpaste), xdg-open
├── starship/.config/             # Starship prompt (Catppuccin Macchiato)
├── git/
│   ├── .gitconfig                # Modern git config (delta, rebase, autostash)
│   └── .config/git/ignore        # Global gitignore
├── bat/.config/bat/              # bat config (Catppuccin theme)
├── atuin/.config/atuin/          # atuin config (fuzzy, no sync)
├── tmux/.config/tmux/            # tmux config (ctrl-a, vim nav, Catppuccin)
├── iterm2/                       # iTerm2 Dynamic Profile (Catppuccin, macOS only)
├── lazygit/.config/lazygit/      # lazygit config (delta pager, Catppuccin)
├── yazi/.config/yazi/            # yazi config + Catppuccin flavor
├── mise/.config/mise/            # Global runtimes (node lts, python 3.12)
├── docs/prompts/                 # Reusable agent instructions + command reference
├── Brewfile                      # macOS packages
├── Makefile                      # make install, make test, make stow
├── install.sh                    # Cross-platform bootstrap
├── Dockerfile                    # Ubuntu test container
└── docs/course/                  # Hands-on tutorial for every tool
```

## Theme

Everything uses **Catppuccin Macchiato** — a consistent dark theme across all tools:

Starship prompt, tmux status bar, fzf picker, bat syntax highlighting, lazygit UI, yazi file manager, iTerm2 terminal.

## Platform Support

| | macOS (primary) | Linux (Docker / EC2) |
|---|---|---|
| Package install | Homebrew (`Brewfile`) | `apt-get` + GitHub releases |
| Shell | zsh (default) | zsh (set by `install.sh`) |
| Terminal | iTerm2 (Dynamic Profile) | N/A (SSH) |
| Stow packages | All | All except `iterm2` |

## Key Bindings

### Shell (zsh)

| Key | Action |
|-----|--------|
| `ctrl-t` | fzf: find file (with bat preview) |
| `alt-c` | fzf: find directory (with tree preview) |
| `ctrl-r` | atuin: fuzzy shell history search |
| `z <query>` | zoxide: jump to directory |
| `y` | yazi: file manager (cd on quit) |
| `lg` | lazygit |
| `lzd` | lazydocker |

### tmux (prefix = `ctrl-a`)

| Key | Action |
|-----|--------|
| `prefix + \|` | Split vertically |
| `prefix + -` | Split horizontally |
| `prefix + h/j/k/l` | Navigate panes (vim-style) |
| `prefix + H/J/K/L` | Resize panes |
| `prefix + c` | New window |
| `prefix + r` | Reload config |
| `prefix + [` | Enter copy mode (vim keys) |

---

## Course

**New to these tools?** There's a hands-on course in [`docs/course/`](docs/course/) that teaches every tool from scratch using Docker as a safe playground.

```bash
# Start the playground
docker build -t dotfiles-test . && docker run -it dotfiles-test

# Then follow the lessons in docs/course/
```

| Lesson | What you'll learn |
|--------|-------------------|
| [00 - Getting Started](docs/course/00-getting-started.md) | Docker playground setup, how stow works |
| [01 - Shell Basics](docs/course/01-shell-basics.md) | Modular zsh config, zinit plugins, shell options |
| [02 - The Prompt](docs/course/02-the-prompt.md) | Starship configuration, git status, Catppuccin theming |
| [03 - File Operations](docs/course/03-file-operations.md) | bat, eza, fd, ripgrep, sd — replacing the classics |
| [04 - Search & Navigation](docs/course/04-search-and-navigation.md) | fzf, zoxide, atuin — find anything instantly |
| [05 - Git Superpowers](docs/course/05-git-superpowers.md) | Modern .gitconfig, delta diffs, lazygit workflows |
| [06 - Terminal Multiplexing](docs/course/06-terminal-multiplexing.md) | tmux sessions, panes, splits, copy mode |
| [07 - File Manager](docs/course/07-file-manager.md) | yazi navigation, previews, bulk operations |
| [08 - Dev Environment](docs/course/08-dev-environment.md) | mise for runtimes, direnv for env vars |
| [09 - System & Containers](docs/course/09-system-and-containers.md) | dust, duf, btm, procs, lazydocker, k9s |
| [10 - Putting It Together](docs/course/10-putting-it-together.md) | Real workflows combining multiple tools |

---

## Adding a New Tool

1. Create `toolname/.config/toolname/config` in the dotfiles repo
2. Run `stow toolname` to symlink it to `$HOME`
3. Add to `Brewfile` (macOS) and `Dockerfile` (Ubuntu) if needed
4. Add shell integration to `zsh/.config/zsh/60-tools.zsh` if needed
5. Add alias to `zsh/.config/zsh/40-aliases.zsh` if helpful

## Personal Config

**Git identity** uses directory-based auto-switching (none of these files are tracked):

| File | Used for |
|------|----------|
| `~/.gitconfig.local` | Fallback identity (repos outside personal/ and workplace/) |
| `~/.gitconfig-personal` | Repos under `~/personal/` |
| `~/.gitconfig-work` | Repos under `~/workplace/` |

The install script prompts for these on first run. To add or change later:

```bash
git config --file ~/.gitconfig-personal user.name "Your Name"
git config --file ~/.gitconfig-personal user.email "personal@example.com"
git config --file ~/.gitconfig-work     user.name "Your Name"
git config --file ~/.gitconfig-work     user.email "work@example.com"
```

Git picks the right identity automatically — no manual switching. Verify with `git config user.email` inside any repo.

Machine-specific shell config goes in `~/.config/zsh/local.zsh` (gitignored).

## License

MIT
