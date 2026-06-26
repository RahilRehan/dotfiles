# Lesson 03 — File Operations

Five modern replacements for the commands you use most. Each one is faster, more informative, and already wired into your shell aliases.

## bat — A Better `cat`

`bat` adds syntax highlighting, line numbers, and git-change markers to file output. In this setup it uses the **Catppuccin Macchiato** theme to match every other tool.

Two aliases make it seamless:

| Alias  | Expands to           | Use when…                                                     |
|--------|----------------------|---------------------------------------------------------------|
| `cat`  | `bat --paging=never` | You want syntax highlighting with line numbers                |
| `catp` | `bat --plain`        | You want colors but no line numbers or header (pipe-friendly) |

### Try it

```bash
# Syntax-highlighted output with line numbers and a filename header:
cat ~/.config/starship.toml
```

Expected output (abbreviated):

```
───────┬────────────────────────────────────────
       │ File: ~/.config/starship.toml
───────┼────────────────────────────────────────
   1   │ format = """
   2   │ $directory\
   3   │ $git_branch\
  ...  │ ...
```

```bash
# Show only lines 1–10:
bat -r 1:10 ~/.config/starship.toml

# Plain mode — colors but no chrome (great for piping):
catp ~/.config/zsh/40-aliases.zsh

# Multiple files — bat prints each with a header:
bat ~/.config/zsh/00-env.zsh ~/.config/zsh/10-options.zsh
```

> Because `cat` is aliased to `bat`, every script or habit that uses `cat` now gets syntax highlighting for free. If you ever need the real `cat`, use `command cat`.

## eza — A Better `ls`

`eza` replaces `ls` with icons, color-coded file types, git status, and tree views. Four aliases cover daily use:

| Alias | Expands to                                          | What it adds                                               |
|-------|-----------------------------------------------------|------------------------------------------------------------|
| `ls`  | `eza --icons --group-directories-first`             | Icons, directories sorted to top                           |
| `ll`  | `eza -la --icons --group-directories-first --git`   | Long listing with permissions, sizes, **git status**       |
| `la`  | `eza -a --icons --group-directories-first`          | Hidden files included                                      |
| `lt`  | `eza --tree --level=3 --icons`                      | Tree view, 3 levels deep                                   |

### Why `--group-directories-first`?

Standard `ls` mixes files and directories alphabetically. With this flag, directories always appear at the top, making it easier to scan project structure at a glance.

### Try it

```bash
# Basic listing — notice icons and directory grouping:
ls ~/dotfiles
```

Expected output (abbreviated):

```
 bat
 docs
 git
 tmux
 zsh
 Brewfile
 Makefile
 README.md
```

```bash
# Long listing with git status:
ll ~/dotfiles
```

Expected output (abbreviated):

```
drwxr-xr-x   - you  2 Apr 12:00  bat
drwxr-xr-x   - you  2 Apr 12:00  git
-rw-r--r-- 1.2k you  2 Apr 12:00 N Brewfile
```

The `N` column is git status — `N` means new/untracked, `M` means modified.

```bash
# Tree view of a specific directory:
lt ~/dotfiles/zsh
```

Expected output (abbreviated):

```
zsh
├── .config
│  └── zsh
│     ├── 00-env.zsh
│     ├── 10-options.zsh
│     ├── 20-plugins.zsh
│     ├── 30-completions.zsh
│     ├── 40-aliases.zsh
│     ├── 50-functions.zsh
│     └── 60-tools.zsh
└── .zshrc
```

```bash
# Control tree depth:
eza --tree --level=1 ~/dotfiles   # top level only
eza --tree --level=5 ~/dotfiles   # deep dive
```

## fd — A Better `find`

`fd` is a fast, user-friendly alternative to `find`. It respects `.gitignore` by default, uses regex patterns, and has sensible defaults (no more `-name` and `-type f` boilerplate).

### Try it

```bash
# Find files by name pattern (regex, not glob):
fd config ~/dotfiles
```

Expected output:

```
~/dotfiles/atuin/.config/atuin/config.toml
~/dotfiles/bat/.config/bat/config
~/dotfiles/lazygit/.config/lazygit/config.yml
~/dotfiles/mise/.config/mise/config.toml
```

```bash
# Find by extension:
fd -e toml ~/dotfiles
```

Expected output:

```
~/dotfiles/atuin/.config/atuin/config.toml
~/dotfiles/mise/.config/mise/config.toml
~/dotfiles/starship/.config/starship.toml
~/dotfiles/yazi/.config/yazi/theme.toml
~/dotfiles/yazi/.config/yazi/yazi.toml
```

```bash
# List all directories:
fd . -t d ~/dotfiles/zsh

# Find .zsh files:
fd -e zsh ~/dotfiles/zsh/

# Exclude patterns:
fd -e js --exclude node_modules

# Include gitignored files:
fd -I "*.log"
```

### Execute commands on results

`--exec` runs a command on each match — no `xargs` needed:

```bash
# Count lines in every markdown file:
fd -e md ~/dotfiles/docs --exec wc -l
```

Expected output:

```
  42 ~/dotfiles/docs/course/01-shell-basics.md
  84 ~/dotfiles/docs/course/02-the-prompt.md
 139 ~/dotfiles/docs/course/03-file-operations.md
  ...
```

## ripgrep (rg) — A Better `grep`

`rg` searches file contents recursively, with syntax-aware defaults. It's fast (uses parallelism), respects `.gitignore`, and highlights matches.

### Try it

```bash
# Search for a pattern recursively:
rg "alias" ~/dotfiles/zsh/.config/zsh/40-aliases.zsh
```

Expected output:

```
1:alias ..="cd .."
2:alias ...="cd ../.."
3:alias ....="cd ../../.."
9:    alias ls="eza --icons --group-directories-first"
10:    alias ll="eza -la --icons --group-directories-first --git"
  ...
```

```bash
# Case-insensitive search:
rg -i "catppuccin" ~/dotfiles

# Only show filenames that match:
rg -l "starship" ~/dotfiles

# Context — 3 lines before and after each match:
rg -C 3 "eval" ~/dotfiles/zsh/.config/zsh/60-tools.zsh
```

### File type filtering

ripgrep has built-in type filters (`-t py`, `-t js`, etc.), but **not every extension has a type**. For example, there is no `-t zsh` type. Use `-g` (glob) instead:

```bash
# Built-in types work for common languages:
rg "import" -t py              # Python files only
rg "function" -t js            # JavaScript files only

# For file types rg doesn't know (like .zsh), use -g:
rg "function" -g "*.zsh" ~/dotfiles
```

Expected output (abbreviated):

```
~/dotfiles/zsh/.config/zsh/50-functions.zsh
1:# Utility functions loaded into every shell session.
  ...
```

```bash
# Count matches per file:
rg -c "alias" ~/dotfiles/zsh/.config/zsh/
```

Expected output:

```
~/dotfiles/zsh/.config/zsh/40-aliases.zsh:18
```

```bash
# Preview a replacement (doesn't modify files):
rg "old_name" -r "new_name"

# Combine fd + rg for targeted searches:
fd -e toml ~/dotfiles | xargs rg "catppuccin"
```

## sd — A Better `sed`

`sd` replaces `sed` for find-and-replace. The key advantage: **no escaping gymnastics**. Regex is the default, and capture groups use `$1` instead of `\1`.

```bash
# Simple replacement (modifies file in-place):
echo "hello world" > /tmp/test.txt
sd "world" "universe" /tmp/test.txt
cat /tmp/test.txt
# → hello universe

# Preview without modifying (pipe from stdin):
echo "foo bar baz" | sd "bar" "BAR"
# → foo BAR baz

# Regex with capture groups:
echo "2024-01-15" | sd "(\d{4})-(\d{2})-(\d{2})" '$3/$2/$1'
# → 15/01/2024

# Compare with sed — sd doesn't need bracket escaping:
# sed: sed -i 's/\[/(/g' file
# sd:  sd '\[' '(' file
```

## Hands-On: Putting It Together

These tools compose well. Try this exercise that chains several together.

**Exercise 1 — Find alias definitions across the shell config**

```bash
# Step 1: Find all .zsh files in the config:
fd -e zsh ~/dotfiles/zsh/.config/zsh/
```

Expected output:

```
~/dotfiles/zsh/.config/zsh/00-env.zsh
~/dotfiles/zsh/.config/zsh/10-options.zsh
~/dotfiles/zsh/.config/zsh/20-plugins.zsh
~/dotfiles/zsh/.config/zsh/30-completions.zsh
~/dotfiles/zsh/.config/zsh/40-aliases.zsh
~/dotfiles/zsh/.config/zsh/50-functions.zsh
~/dotfiles/zsh/.config/zsh/60-tools.zsh
~/dotfiles/zsh/.config/zsh/70-platform.zsh
```

```bash
# Step 2: Which of those files contain "alias"?
rg -l "alias" -g "*.zsh" ~/dotfiles/zsh/.config/zsh/
```

Expected output:

```
~/dotfiles/zsh/.config/zsh/40-aliases.zsh
```

```bash
# Step 3: Show alias definitions with syntax highlighting:
rg "^alias" ~/dotfiles/zsh/.config/zsh/40-aliases.zsh | bat -l zsh
```

```bash
# Step 4: How many config files exist across the entire dotfiles repo?
fd -e toml -e yml -e zsh ~/dotfiles | wc -l
```

**Exercise 2 — fd + rg + bat: find, search, display**

Combine all three tools to locate every TOML file mentioning "catppuccin" and display the matches with full syntax highlighting:

```bash
# Find TOML files, search for a theme name, display with bat:
fd -e toml ~/dotfiles --exec rg -l "catppuccin" {} \; | xargs bat
```

Expected output: bat displays each matching TOML file with syntax highlighting. You'll see files like `starship.toml`, `flavor.toml`, and others that reference the Catppuccin theme.

Try adapting the pattern for your own searches:

```bash
# Find all YAML/TOML config files that mention "true":
fd -e toml -e yml ~/dotfiles --exec rg -l "true" {} \; | xargs bat
```

## Cheat Sheet

| Old command                          | New command              | Notes                                 |
|--------------------------------------|--------------------------|---------------------------------------|
| `cat file.py`                        | `cat file.py`            | Aliased to `bat`; syntax highlighting automatic |
| `cat` (pipe-friendly)                | `catp file.py`           | `bat --plain` — colors, no chrome     |
| `ls -la`                             | `ll`                     | Long listing + git status + icons     |
| `ls -a`                              | `la`                     | Hidden files + icons                  |
| `ls -R` / `tree`                     | `lt`                     | Tree view, 3 levels                   |
| `find . -name "*.py"`               | `fd -e py`               | Respects `.gitignore`, faster         |
| `find . -type d`                     | `fd . -t d`              |                                       |
| `grep -r "pattern" .`               | `rg "pattern"`           | Parallel, syntax-aware                |
| `grep -r "pat" --include="*.zsh"`   | `rg "pat" -g "*.zsh"`   | Glob filter (no `-t zsh`)             |
| `sed -i 's/old/new/g' file`         | `sd "old" "new" file`    | No escaping gymnastics                |

## Next

[Lesson 04 — Search & Navigation →](04-search-and-navigation.md)
