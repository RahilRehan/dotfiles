# Lesson 04 — Search & Navigation

Three tools that change how you move around your filesystem and recall past commands. Each one replaces a built-in with something dramatically better.

## fzf — Fuzzy Finder

fzf takes any list of items, lets you type to fuzzy-filter, and outputs your selection. On its own it's a simple filter — but wired into your shell, it becomes a file picker, directory jumper, and history browser.

### How it's configured

Three things make fzf powerful in this setup:

1. **fd as the backend.** By default fzf uses `find` to list files. We swap that for `fd`, which is faster and respects `.gitignore`. Three environment variables control this:

```bash
# From 60-tools.zsh:
export FZF_DEFAULT_COMMAND="fd --type f --hidden --follow --exclude .git"
export FZF_CTRL_T_COMMAND="$FZF_DEFAULT_COMMAND"       # file picker uses fd
export FZF_ALT_C_COMMAND="fd --type d --hidden --follow --exclude .git"  # directory picker uses fd
```

`FZF_DEFAULT_COMMAND` controls what fzf lists when you pipe nothing into it (bare `fzf` in the terminal). `FZF_CTRL_T_COMMAND` and `FZF_ALT_C_COMMAND` control the Ctrl-T file picker and Alt-C directory picker respectively. All three use `fd` with `--hidden` (include dotfiles) and `--exclude .git` (skip the `.git` directory).

2. **Catppuccin Macchiato colors.** fzf picks up the same palette as starship, bat, delta, and lazygit — so the finder blends visually with everything else. The colors are set via `FZF_DEFAULT_OPTS` in `60-tools.zsh`:

```bash
export FZF_DEFAULT_OPTS="
    --height=60%
    --layout=reverse
    --border=rounded
    --info=inline-right
    --bind='ctrl-/:toggle-preview'
    --color=bg+:#363a4f,bg:#24273a,spinner:#f4dbd6,hl:#ed8796
    --color=fg:#cad3f5,header:#ed8796,info:#c6a0f6,pointer:#f4dbd6
    --color=marker:#b7bdf8,fg+:#cad3f5,prompt:#c6a0f6,hl+:#ed8796
    --color=selected-bg:#494d64
"
```

Every `--color` value is a hex code from the Catppuccin Macchiato palette. `bg` is the base background, `fg` is the text, `hl` is the matched characters (red/mauve), `pointer` is the selection arrow, and so on. Because every tool uses Catppuccin, the fzf popup looks like a native part of the terminal.

3. **Previews.** Ctrl-T shows a **bat** preview of the selected file's contents. Alt-C shows an **eza tree** preview of the directory. Both are toggled with **Ctrl-/**.

### Ctrl-T — Find and insert a file path

Press **Ctrl-T** at any point on the command line. A file picker appears with a **bat preview** on the right. Type to filter, arrow keys to navigate, Enter to select. The selected path is inserted at your cursor.

```bash
# Example: open a file in vim without knowing its exact path
vim [press Ctrl-T, type "starship", select the match, press Enter]
# → vim /home/testuser/.config/starship.toml
```

The preview shows syntax-highlighted file contents via bat. Toggle it with **Ctrl-/**.

### Alt-C — Find and cd into a directory

Press **Alt-C** anywhere. A directory picker appears with an **eza tree preview**. Select a directory and your shell `cd`s into it instantly.

```bash
# Example: jump into a deeply nested config directory
[press Alt-C, type "zsh", select .config/zsh, press Enter]
pwd
# → /home/testuser/.config/zsh
```

> **Note:** Alt-C sends an escape sequence that some terminals and multiplexers intercept. If it doesn't work inside tmux, a nested terminal, or your specific terminal emulator, check that your terminal is sending the correct Alt/Meta key (Ghostty and iTerm2 both have an "Option as Meta" setting). As a fallback, you can always use `cd **[Tab]` which triggers fzf's tab completion for directories, or `zi` from zoxide (covered below).

### Ctrl-R — History search (handed off to atuin)

In most fzf setups, Ctrl-R provides fuzzy history search. In this setup, **atuin handles Ctrl-R** instead (see below) — it offers richer context like directory, exit code, and duration for each command.

If atuin were not installed, fzf would provide its own fuzzy history picker.

### Piping into fzf

fzf's real power shows when you pipe any list into it:

```bash
# Pick a Python file to edit:
fd -e py | fzf --preview 'bat --color=always {}' | xargs vim
```

```bash
# Pick a git branch to checkout:
git branch | fzf | xargs git checkout
```

```bash
# Browse and preview toml config files:
fd -e toml ~/dotfiles | fzf --preview 'bat --color=always --line-range :50 {}'
```

```bash
# Pick a process to kill:
ps aux | fzf | awk '{print $2}' | xargs kill
```

```bash
# Browse and preview markdown course files:
fd -e md ~/dotfiles/docs | fzf --preview 'bat --color=always --line-range :50 {}'
```

The pattern is always the same: **generate a list → pipe into fzf → do something with the selection**. Any command that outputs lines can be an fzf source.

### Try it

```bash
# 1. Press Ctrl-T, type "toml", select a file — its path appears on your command line.
#    Press Enter (or Ctrl-C to cancel).

# 2. Press Alt-C, type "zsh", select a directory — you cd into it.
pwd
# → /home/testuser/.config/zsh (or whichever you chose)

# 3. Pipe a file list into fzf and preview:
fd -e zsh ~/dotfiles | fzf --preview 'bat --color=always {}'
# Arrow through files — the preview updates in real time.
# Press Ctrl-/ to toggle the preview panel.
```

---

## zoxide — Smart `cd`

zoxide replaces `cd` with a command that learns where you go. After a few visits, you can jump to any directory with a fragment of its name.

### How frecency works

zoxide ranks directories by **frecency** — a blend of **frequency** (how often) and **recency** (how recently). A directory you visit ten times a day scores far higher than one you visited once last month. Scores decay over time, so stale directories naturally drop off.

### Try it

```bash
# Build up some history by visiting a few directories:
cd /etc
cd /var/log
cd /home/testuser/dotfiles
cd /tmp
```

Now jump with partial names:

```bash
z etc
pwd
```

Expected output:

```
/etc
```

```bash
z log
pwd
```

Expected output:

```
/var/log
```

```bash
# Multiple words narrow the match:
z dot
pwd
```

Expected output:

```
/home/testuser/dotfiles
```

```bash
# Interactive mode — opens fzf with all learned directories:
zi
# Type to filter, arrow to select, Enter to jump.
```

```bash
# Check what zoxide has learned:
zoxide query -ls
```

Expected output (after the visits above):

```
  10.0 /etc
  10.0 /home/testuser/dotfiles
  10.0 /tmp
  10.0 /var/log
```

Scores increase as you revisit directories. Over time your most-used paths bubble to the top.

---

## atuin — Shell History in SQLite

The default shell history is a flat text file with no context. atuin replaces it with a **SQLite database** that records the command, timestamp, duration, exit code, and working directory for every command you run.

### How it's configured

```bash
# From 60-tools.zsh:
eval "$(atuin init zsh --disable-up-arrow)"
```

The `--disable-up-arrow` flag is important: it keeps the **Up arrow** bound to normal line-by-line history navigation (via the zsh-history-substring-search plugin), while **Ctrl-R** opens atuin's full-screen search. Without this flag, atuin would hijack Up arrow too, which feels disorienting if you're used to pressing Up for the last command.

In practice:
- **Up arrow** → scroll through recent commands one-by-one (normal shell behavior)
- **Ctrl-R** → open atuin's full-screen fuzzy search with all the context columns

### Try it

```bash
# Run a few commands to populate history:
echo "hello from atuin"
ls -la /tmp
sleep 1
false   # intentional failure (exit code 1)

# Now press Ctrl-R:
# A full-screen picker appears showing every command with context.
# Each row shows: timestamp · duration · exit code · directory · command
```

Expected display (compact style):

```
 2026-04-02 12:01:00  0.001s  1    /home/testuser    false
 2026-04-02 12:00:59  1.003s  0    /home/testuser    sleep 1
 2026-04-02 12:00:58  0.002s  0    /home/testuser    ls -la /tmp
 2026-04-02 12:00:57  0.001s  0    /home/testuser    echo "hello from atuin"
```

Type to fuzzy-filter across all fields. Press Enter to execute, or Tab to insert the command for editing.

```bash
# Search with filters from the command line:
atuin search --exit 0              # only successful commands
atuin search --cwd /tmp            # only commands run in /tmp
atuin search --after "1 hour ago"  # recent commands

# View usage statistics:
atuin stats
```

### Why atuin over default Ctrl-R?

| Feature | Default Ctrl-R | atuin |
|---------|---------------|-------|
| Search mode | Substring | Fuzzy (typos OK) |
| Context | None | Directory, exit code, duration, timestamp |
| Scope | Current session | All sessions, all terminals |
| Storage | Flat text file | SQLite database |
| Sync | No | Optional (encrypted, across machines) |
| Up arrow | Same as Ctrl-R | Separate — normal history navigation preserved |

### Configuration highlights

From `~/.config/atuin/config.toml`:

| Setting | Value | Why |
|---------|-------|-----|
| `style` | `"compact"` | Shows more results per screen than the default `"auto"` layout |
| `auto_sync` | `false` | History stays local — no cloud sync (privacy first) |
| `sync_address` | `""` | No sync server configured |
| `filter_mode_shell_up_key_binding` | `"directory"` | When atuin does handle Up arrow, it filters to commands run in the **current directory** — though we disable atuin's Up arrow binding, this still affects `atuin search` scoping |
| `history_filter` | patterns for secrets | Prevents recording commands containing `AWS_SECRET`, `TOKEN`, `PASSWORD`, `KEY`, `SECRET`, or `curl` with auth headers |

---

## Cheat Sheet

| Action | Shortcut / Command |
|--------|-------------------|
| Find a file by name | **Ctrl-T** (fzf + fd + bat preview) |
| Jump to a directory | **Alt-C** (fzf + fd + eza preview) |
| Search command history | **Ctrl-R** (atuin full-screen) |
| Previous command | **Up arrow** (line-by-line, filtered by current input) |
| Jump to a visited directory | `z <fragment>` (zoxide) |
| Interactive directory jump | `zi` (zoxide + fzf) |
| Toggle fzf preview | **Ctrl-/** |

## Next

[Lesson 05 — Git Superpowers →](05-git-superpowers.md)
