# Lesson 10 — Putting It Together

Real workflows that combine multiple tools. This is where the toolbox pays off.

Every workflow in this lesson uses the **dotfiles repo itself** as the sample project — it's already at `~/dotfiles` after install. No setup required.

## Workflow 1: Explore This Codebase

You just cloned a repo you've never seen. Understand it in 60 seconds.

```bash
cd ~/dotfiles

# 1. Project structure at a glance:
eza --tree --level=2
```

Expected output (abbreviated):

```
dotfiles
├── Brewfile
├── Makefile
├── bat
│   └── .config
├── git
│   ├── .config
│   └── .gitconfig
├── starship
│   └── .config
├── tmux
│   └── .config
├── zsh
│   ├── .config
│   └── .zshrc
├── docs
│   └── course
...
```

```bash
# 2. What kinds of files exist?
fd . -t f | head -20

# 3. Find config files — every tool stores its config as a dotfile:
fd "config" -t f
# Expected output:
# atuin/.config/atuin/config.toml
# bat/.config/bat/config
# lazygit/.config/lazygit/config.yml
# mise/.config/mise/config.toml
# starship/.config/starship.toml
# tmux/.config/tmux/tmux.conf
# yazi/.config/yazi/yazi.toml

# 4. What themes are configured? Search across ALL config files at once:
rg "catppuccin" -l
# Expected output — every tool shares the same theme:
# bat/.config/bat/config
# lazygit/.config/lazygit/config.yml
# starship/.config/starship.toml
# yazi/.config/yazi/flavors/catppuccin-macchiato.yazi/flavor.toml

# 5. Read the shell modules in load order:
ls ~/.config/zsh/
# 00-env.zsh  10-options.zsh  20-plugins.zsh  30-completions.zsh
# 40-aliases.zsh  50-functions.zsh  60-tools.zsh  70-platform.zsh

# 6. Browse visually — preview files as you navigate:
y                             # yazi — arrow keys to browse, q to quit
```

**What you practiced:** `eza --tree` for structure, `fd` for finding files by name, `rg -l` for finding files by content, `ls` for ordered listings, `yazi` for visual exploration.

## Workflow 2: Fix a Bug

Someone reports that an alias is wrong. Find it, understand the history, fix it, and commit — all from the terminal.

```bash
# Set up a test repo to practice the full flow:
cd /tmp && mkdir bugfix-demo && cd bugfix-demo && git init
cat > aliases.sh << 'EOF'
alias gs="git status"
alias gc="git commit"
alias gp="git psuh"
EOF
git add . && git commit -m "add aliases"
```

Now find and fix the typo:

```bash
# 1. Search for the bug — we know "push" is misspelled somewhere:
rg "psuh"
# Expected output:
# aliases.sh:3:alias gp="git psuh"

# 2. See context around the match:
rg "psuh" -C 2
# Expected output:
# aliases.sh-1-alias gs="git status"
# aliases.sh-2-alias gc="git commit"
# aliases.sh:3:alias gp="git psuh"

# 3. Check git blame — when was this introduced?
git log -p -S "psuh"
# Shows the commit that added the typo, with delta-rendered diff

# 4. Fix it (edit the file however you prefer, then use lazygit):
lg
# In lazygit:
#   Files panel shows aliases.sh as modified
#   Press Enter on the file to see the diff
#   Press space to stage
#   Press c to commit, type "fix: correct git push alias typo", Enter
```

Verify the fix:

```bash
rg "psuh"                     # no results — bug is gone
git log --oneline -2
# Expected output:
# a1b2c3d fix: correct git push alias typo
# d4e5f6a add aliases
```

**What you practiced:** `rg` to locate a bug, `rg -C` for context, `git log -p -S` to find when it was introduced, `lg` (lazygit) to stage and commit.

## Workflow 3: tmux Dev Session

Build a multi-pane workspace for exploring the dotfiles repo.

```bash
# 1. Create a named session:
tmux new -s dotfiles

# 2. Left pane — browse the repo:
cd ~/dotfiles

# 3. Split vertically (prefix |):
# ctrl-a |

# 4. Right pane — run searches:
cd ~/dotfiles

# 5. Split the right pane horizontally (prefix -):
# ctrl-a -

# 6. Bottom-right pane — watch a file:
cd ~/dotfiles
bat zsh/.config/zsh/40-aliases.zsh
```

Your layout should look like this:

```
┌─────────────────────┬─────────────────────┐
│                     │                     │
│   Browse / edit     │   rg searches       │
│   (yazi or bat)     │                     │
│                     ├─────────────────────┤
│                     │                     │
│                     │   file viewer       │
│                     │   (bat output)      │
└─────────────────────┴─────────────────────┘
```

```bash
# Navigate between panes:
# ctrl-a h/j/k/l     (vim-style movement)

# Try this workflow:
# Left pane:         y                    (browse with yazi)
# Top-right pane:    rg "alias" -l        (find all files with aliases)
# Bottom-right pane: bat zsh/.config/zsh/40-aliases.zsh

# Detach (session keeps running):
# ctrl-a d

# List sessions:
tmux ls
# Expected output:
# dotfiles: 1 windows (created Thu Apr  2 10:00:00 2026)

# Reattach — everything is exactly where you left it:
tmux a -t dotfiles
```

**What you practiced:** tmux sessions, splits (`|` and `-`), pane navigation (`h/j/k/l`), detach/reattach.

## Workflow 4: Deep Search

Combine `rg`, `fd`, and `fzf` to answer real questions about a codebase.

```bash
cd ~/dotfiles

# Question: "What environment variables does this repo set?"
rg "export " zsh/.config/zsh/ -n
# Shows every export with file and line number

# Question: "Which tools does the install script configure?"
rg "stow " install.sh
# Shows every stow command — one per tool package

# Question: "Find all TODO/FIXME comments across the entire repo:"
rg "TODO|FIXME|HACK" --glob '!node_modules'
```

> **Regex note:** ripgrep uses standard regex. Alternation is a bare pipe — `rg "TODO|FIXME"`. Do **not** escape the pipe with a backslash (`\|`), which is BRE/grep syntax and will silently match the wrong thing in rg.

```bash
# Real-world example — find entry points across a polyglot codebase:
rg "func main|def main|export default"
# Correct: bare pipes for alternation.
# Wrong:   rg "func main\|def main\|export default"  ← backslash-pipe is NOT rg syntax

# Question: "What file types exist in this repo?"
fd . -t f | rg '\.([^.]+)$' -o | sort | uniq -c | sort -rn
# Expected output (approximate):
#   15 .md
#   10 .zsh
#    8 .toml
#    3 .yml
#    ...

# Question: "Find recently modified shell files:"
fd -e zsh --changed-within 7d

# Interactive search — pick a file with preview, then read it:
fd -e zsh | fzf --preview 'bat --color=always {}'
# Type to filter, arrow keys to navigate, Enter to select
# The selected path is printed to stdout

# Pipe the selection into bat to read it:
fd -e zsh | fzf --preview 'bat --color=always {}' | xargs bat
```

### Old Way vs New Way

```bash
# OLD: Find Python files excluding vendor, search for TODO, with context:
find . -name "*.py" -not -path "*/vendor/*" -exec grep -n "TODO" {} +

# NEW: Same thing, readable and fast:
rg "TODO" -t py --glob '!vendor' -C 2

# OLD: Find files larger than 1MB:
find . -type f -size +1M

# NEW:
fd . -t f --size +1m
```

**What you practiced:** `rg` with alternation (`|`), file type filters (`-t`), glob exclusions, `fd` with size/time filters, `fzf` with preview for interactive selection.

## Workflow 5: System Monitoring & Cleanup

### Disk Cleanup

Find and reclaim wasted disk space.

```bash
# 1. See what's using space in your home directory:
dust ~ -d 1

# 2. Drill into the biggest offender:
dust ~/Library -d 2

# 3. Find node_modules graveyards:
fd node_modules -t d --size +100m ~/code

# 4. Clean them:
fd node_modules -t d ~/code --exec rm -rf

# 5. Check overall disk free space:
duf --only local

# 6. Monitor system impact during heavy operations:
btm
```

**What you practiced:** `dust` for directory sizes, `fd --exec` for bulk operations, `duf` for disk overview, `btm` for system monitoring.

### Benchmark Old vs New

Prove to yourself that the modern tools are faster.

```bash
# How much faster is fd than find?
hyperfine "find . -type f -name '*.zsh'" "fd -e zsh" --warmup 3

# Expected output (results vary by machine):
# Benchmark 1: find . -type f -name '*.zsh'
#   Time (mean ± σ):     112.3 ms ±   5.1 ms
# Benchmark 2: fd -e zsh
#   Time (mean ± σ):       4.2 ms ±   0.8 ms
# Summary
#   fd -e zsh ran 26.74 ± 5.42 times faster than find . -type f -name '*.zsh'

# How much faster is rg than grep?
hyperfine "grep -r 'alias' --include='*.zsh' ." "rg 'alias' -t zsh" --warmup 3
```

**What you practiced:** `hyperfine` for benchmarking, comparing legacy tools to modern replacements with real data.

## What's Next

You've completed the course. Here's how to make it yours:

**Customize your prompt.** Open `starship/.config/starship.toml` and tweak colors, segments, or icons. Try changing the color palette or adding a segment for your language of choice. See the [Starship docs](https://starship.rs/config/) for every option.

**Add your own aliases.** Edit `zsh/.config/zsh/40-aliases.zsh`. Good candidates: project directories you `cd` to daily, long commands you run repeatedly, typos you always make.

**Create shell functions.** For anything more complex than an alias, add functions to `zsh/.config/zsh/50-functions.zsh`. Functions can take arguments, use conditionals, and call other commands.

**Add new tools.** Found a CLI tool you like? Add it to the `Brewfile`, create a config directory (`toolname/.config/toolname/config`), and run `stow toolname`. The pattern is always the same.

**Fork and diverge.** This repo is a starting point. Delete tools you don't use, change keybindings that don't feel right, swap themes. The best dotfiles are the ones you've made your own.
