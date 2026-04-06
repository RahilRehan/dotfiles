<!-- docs/course/00-getting-started.md -->

# Lesson 00 — Getting Started

## The Docker Playground

Every lesson uses a Docker container so you can experiment freely without affecting your machine. Think of it as a disposable Linux VM that boots in seconds.

```bash
# Build the playground (first time takes ~2 min, cached after)
docker build -t dotfiles-test .

# Enter the playground
docker run -it --rm dotfiles-test
```

Breaking down that `docker run` command:

| Flag | Purpose |
|------|---------|
| `-it` | **Interactive** + **TTY** — gives you a shell you can type into |
| `--rm` | **Remove on exit** — deletes the container (filesystem, processes, everything) the moment you type `exit`. Without this flag, stopped containers accumulate on disk. You'd need `docker container prune` to clean them up. This is what makes the playground truly disposable — every `docker run` gives you a clean slate. |
| `dotfiles-test` | The image name from the `docker build` step |

You're now inside an Ubuntu container (user `testuser`) with all the tools installed and configs symlinked. Everything you do is throwaway — type `exit` and it's gone.

> **Tip:** Keep this lesson open in one terminal and the container in another.

---

## How Stow Works

GNU Stow creates symlinks from the dotfiles repo into your home directory. You version-control your configs in one place; tools find them where they expect.

Each top-level folder in `~/dotfiles/` is a **package**. The directory structure inside each package mirrors `$HOME`:

```
dotfiles/
├── git/.gitconfig                 →  ~/.gitconfig
├── starship/.config/starship.toml →  ~/.config/starship.toml
├── bat/.config/bat/config         →  ~/.config/bat/config
└── zsh/
    ├── .zshrc                     →  ~/.zshrc
    └── .config/zsh/               →  ~/.config/zsh/
```

Stow figures out targets by mapping each package's internal paths relative to the target directory (your home). The `install.sh` script runs `stow --restow --target="$HOME" <package>` for each directory.

### Verify it's working

```bash
ls -la ~/.config/starship.toml
```

Expected output:

```
lrwxrwxrwx 1 testuser testuser 47 ... /home/testuser/.config/starship.toml -> ../dotfiles/starship/.config/starship.toml
```

The `->` confirms it's a symlink pointing back into the repo. Edit the file in the repo and every tool sees the change immediately — no copying, no reloading.

### Exercise: unstow and restow

Let's remove a package and bring it back to see stow in action. Follow every step and compare your output.

**Step 1 — see what packages are stowed:**

```bash
ls ~/dotfiles/
```

Expected output:

```
Brewfile  Makefile  atuin  git       lazygit  starship  yazi
CONTRIBUTING.md  README.md  bat    docs   install.sh  mise     tmux      zsh
```

Each directory (except `docs`) is a stow package.

**Step 2 — check that the bat config symlink exists:**

```bash
ls -la ~/.config/bat/config
```

Expected output:

```
lrwxrwxrwx 1 testuser testuser 42 ... /home/testuser/.config/bat/config -> ../../dotfiles/bat/.config/bat/config
```

The config is a symlink into the repo. `bat` (a syntax-highlighted `cat` replacement — we'll cover it in [Lesson 03](03-file-operations.md)) reads its config from here.

**Step 3 — unstow the bat package:**

```bash
cd ~/dotfiles && stow -D bat
```

No output means success. The `-D` (delete) flag tells stow to remove symlinks it previously created for that package.

**Step 4 — confirm the config is gone:**

```bash
ls ~/.config/bat/config
```

Expected output:

```
ls: cannot access '/home/testuser/.config/bat/config': No such file or directory
```

The symlink is removed. The actual config file still lives safely in `~/dotfiles/bat/.config/bat/config` — stow never deletes real files, only the symlinks it created.

**Step 5 — re-stow it:**

```bash
stow bat
```

No output means success. Stow recreated the symlink.

**Step 6 — verify it's back:**

```bash
ls -la ~/.config/bat/config
```

Expected output:

```
lrwxrwxrwx 1 testuser testuser 42 ... /home/testuser/.config/bat/config -> ../../dotfiles/bat/.config/bat/config
```

The config reappears instantly — stow recreated the symlink. No files were copied or deleted.

> **Key insight:** `stow -D` only removes symlinks stow created — it never deletes real files. And `stow` (restow) is idempotent — running it twice changes nothing.

---

## The Modular Shell

Your entire shell configuration loads through one tiny file. Let's look at it:

```bash
cat ~/.zshrc
```

> `cat` prints the file contents. We'll cover `bat` (a syntax-highlighted replacement) in [Lesson 03](03-file-operations.md).

Expected output:

```
# Thin loader — sources numbered config files from ~/.config/zsh/
# Profile startup: ZSH_PROFILE=1 exec zsh, then check output.
[[ -n "$ZSH_PROFILE" ]] && zmodload zsh/zprof

ZSH_CONFIG="${XDG_CONFIG_HOME:-$HOME/.config}/zsh"

# (N) = nullglob — if no files match, don't error
for conf in "$ZSH_CONFIG"/[0-9]*.zsh(N); do
    source "$conf"
done

# Machine-specific overrides (API keys, work stuff). Gitignored.
[ -f "$ZSH_CONFIG/local.zsh" ] && source "$ZSH_CONFIG/local.zsh"

[[ -n "$ZSH_PROFILE" ]] && zprof
```

That's the entire `.zshrc` — just a loop. It sources every file in `~/.config/zsh/` whose name starts with a digit, in lexicographic order. The `(N)` is a zsh glob qualifier called "nullglob" — if no files match, the loop quietly does nothing instead of erroring.

### The numbered loading order

```bash
ls ~/.config/zsh/[0-9]*.zsh
```

Expected output:

```
00-env.zsh    20-plugins.zsh     40-aliases.zsh    60-tools.zsh
10-options.zsh  30-completions.zsh  50-functions.zsh  70-platform.zsh
```

The numbering is deliberate — it's the same pattern used by systemd units and database migrations. Zsh sources these in lexicographic order, so `00` runs first and `70` runs last. Each file can depend on everything before it.

Here's every file, what it does, and why it must load in that position:

| File | Purpose | Why this position |
|------|---------|-------------------|
| `00-env.zsh` | Sets `$PATH`, XDG base directories (`$XDG_CONFIG_HOME`, etc.), `$EDITOR`, and initializes Homebrew | **Must be first.** Nearly everything else depends on `$PATH` being correct. `60-tools.zsh` runs `starship init zsh` — if Homebrew hasn't added its prefix to `$PATH` yet, the shell can't find the `starship` binary. XDG vars are also used by `10-options.zsh` (for `$HISTFILE`) and `30-completions.zsh` (for cache paths). |
| `10-options.zsh` | Shell behavior (`setopt` flags) and history settings | **After env, before plugins.** History settings like `SHARE_HISTORY` and `HISTFILE` depend on `$XDG_STATE_HOME` from `00`. Must be set before plugins load so that plugins inherit the correct shell behavior. |
| `20-plugins.zsh` | zinit plugin manager: syntax highlighting, autosuggestions, `zsh-completions`, history-substring-search, OMZ snippets | **After options, before completions.** Plugins need `$PATH` to clone from GitHub. The `zsh-completions` plugin registers completion definitions that `30-completions.zsh` will style — if completions loaded first, there'd be nothing to style. |
| `30-completions.zsh` | Completion styling: case-insensitive matching, menu selection, colors, caching | **After plugins.** `zstyle` rules configure how completions look and behave, but `20-plugins.zsh` must have loaded `zsh-completions` first so the completion definitions exist. |
| `40-aliases.zsh` | Aliases: `ls`→`eza`, `cat`→`bat`, safety nets (`rm -i`), shortcuts (`lg`, `c`, `reload`) | **After completions, before functions.** Aliases may reference tools whose paths were set in `00`. Placed after completions so that completion definitions apply to the original commands, not the aliases. |
| `50-functions.zsh` | Shell functions: `mkcd`, `extract`, `killport`, `serve` | **Standalone utilities.** These don't depend on much, but placing them after aliases keeps the file focused. Functions are more complex than aliases and deserve their own file. |
| `60-tools.zsh` | Tool initialization hooks: `zoxide init`, `atuin init`, `fzf --zsh`, `mise activate`, `direnv hook`, yazi wrapper, `starship init` | **Near the end.** Every `eval "$(tool init zsh)"` call needs the tool on `$PATH` (from `00`). Starship specifically must be last among tools because it wraps the prompt — anything that modifies the prompt after starship would be overwritten. |
| `70-platform.zsh` | macOS vs. Linux-specific overrides: clipboard aliases, DNS flush, platform utilities | **Last.** Platform-specific config may override anything set by earlier files. On macOS it might tweak aliases; on Linux it adds `pbcopy`/`pbpaste` compatibility wrappers. |

### Why gaps between the numbers?

The 10-unit spacing is intentional — it leaves room for future files without renaming anything. For example, this repo has a `20-keybindings.zsh` file that configures word-navigation keys (Option+Left/Right). It could be inserted between `10-options.zsh` and `20-plugins.zsh` by naming it `15-keybindings.zsh` — no existing files need to change.

The convention:

| Gap | Example use |
|-----|-------------|
| `05-*` | Early PATH additions before Homebrew |
| `15-*` | Keybindings, input settings |
| `25-*` | Extra plugin config after zinit loads |
| `35-*` | Completion overrides for specific tools |
| `45-*` | Context-specific aliases (work, project) |
| `55-*` | Heavier utility functions |
| `65-*` | Late-loading tool hooks |
| `75-*` | Final overrides, debugging |

You'll never use most of these. The point is that you *can* — the system scales without renumbering.

### The `local.zsh` escape hatch

After all numbered files are sourced, `.zshrc` checks for one more file:

```bash
[ -f "$ZSH_CONFIG/local.zsh" ] && source "$ZSH_CONFIG/local.zsh"
```

This file is **gitignored** (the `.gitignore` contains `*.local`), so it never gets committed. Use it for anything machine-specific:

- **API keys and tokens:** `export OPENAI_API_KEY="sk-..."`
- **Work aliases:** `alias vpn="sudo openconnect ..."`
- **Local PATH additions:** `path+=(/opt/custom-tool/bin)`
- **Overrides:** change an alias or variable from the shared config without editing tracked files

Because `local.zsh` loads *after* everything else, it can override any setting from the numbered files. This is the escape hatch that lets you share one repo across machines while keeping secrets and personal tweaks out of version control.

---

## Next

[Lesson 01 — Shell Basics →](01-shell-basics.md)
