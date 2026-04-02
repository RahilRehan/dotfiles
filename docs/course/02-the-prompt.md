<!-- docs/course/02-the-prompt.md -->

# Lesson 02 — The Prompt

## What Is Starship?

Starship is a cross-shell prompt written in Rust. Instead of a static `$` or `%`,
it renders contextual segments — git branch, file status, language versions,
command duration — and stays fast (sub-10 ms render time). It works with zsh,
bash, fish, and others from a single TOML config.

```bash
starship --version
```

The config lives at `~/.config/starship.toml`. Changes take effect on the next
prompt render — no restart needed.

## What the Prompt Shows

A fully-loaded prompt looks like this:

```
~/code/my-project 󰘬 main ?2 !1 +15 -3 via  v20.10.0 took 3s
❯                                                             14:32
```

The first line shows context. The second line is the input line — `❯` on the
left, a 24-hour clock on the right.

### Segments

| Segment | Example | Meaning | Color |
|---------|---------|---------|-------|
| Directory | `~/code/my-project` | Current path, truncated to 3 levels | bold blue |
| Git branch | `󰘬 main` | Current branch | bold mauve |
| Git status | `?2 !1` | Working tree file states (see table below) | bold peach |
| Git metrics | `+15 -3` | Lines added / deleted in the diff | green / red |
| Language | ` v20.10.0` | Runtime version (only in relevant projects) | varies |
| Duration | `took 3s` | Last command's wall time (only if > 2 s) | yellow |
| Prompt char | `❯` | Where you type | **mauve** = success, **red** = error |
| Time | `14:32` | 24-hour clock (right side) | dimmed |

### Git status symbols

Git status counts **files** — how many are in each state:

| Symbol | Meaning | Example |
|--------|---------|---------|
| `?N` | Untracked — new files git doesn't track yet | `?2` = 2 new files |
| `!N` | Modified — changed but not staged | `!1` = 1 modified file |
| `+N` | Staged — added to the next commit | `+3` = 3 staged files |
| `✘N` | Deleted | `✘1` = 1 deleted file |
| `*N` | Stashed | `*1` = 1 stash entry |
| `=N` | Conflicted — merge conflict | `=2` = 2 conflicted files |
| `⇡N` | Commits ahead of remote | `⇡3` = 3 unpushed commits |
| `⇣N` | Commits behind remote | `⇣1` = 1 commit to pull |
| `⇕⇡M⇣N` | Diverged — ahead and behind | `⇕⇡2⇣1` = diverged |

## Try It

```bash
cd /tmp && mkdir prompt-lab && cd prompt-lab
git init
git config user.name "Test" && git config user.email "test@test.com"
```

The prompt now shows the branch:

```
/tmp/prompt-lab 󰘬 main
❯
```

### 1. Create an untracked file

```bash
touch hello.txt
```

```
/tmp/prompt-lab 󰘬 main ?1
❯
```

`?1` — one untracked file. Git sees it but isn't tracking it yet.

### 2. Stage the file

```bash
git add hello.txt
```

```
/tmp/prompt-lab 󰘬 main +1
❯
```

`+1` — one file staged for commit. The `?` became `+`.

### 3. Commit

```bash
git commit -m "first"
```

```
/tmp/prompt-lab 󰘬 main
❯
```

Clean — no status symbols. Everything is committed.

### 4. Modify a tracked file

```bash
echo "hello world" >> hello.txt
```

```
/tmp/prompt-lab 󰘬 main !1 +1
❯
```

Two things appeared:

- `!1` (peach) — git status: 1 modified file
- `+1` (green) — git metrics: 1 line added in the diff

### 5. Command duration

```bash
sleep 3
```

```
/tmp/prompt-lab 󰘬 main !1 +1 took 3s
❯
```

The `took 3s` segment only appears when a command exceeds 2 seconds.

### 6. Error indicator

```bash
false
```

```
/tmp/prompt-lab 󰘬 main !1 +1
❯
```

The `❯` turns **red** because `false` exited with a non-zero status. Run any
successful command and it returns to **mauve**.

### Cleanup

```bash
cd /tmp && rm -rf prompt-lab
```

## Git Metrics

Git metrics is a separate module from git status. It counts **lines**, not files
— a mini `diff --stat` rendered inline.

- `+15` (green) — 15 lines added across all changed files
- `-3` (red) — 3 lines deleted

It only appears when there are uncommitted changes.

> **Why both?** Git status tells you *how many files* changed. Git metrics tells
> you *how much code* changed. Seeing `!1 +200 -150` instantly communicates a
> large refactor in a single file — very different from `!1 +1`.

The relevant config:

```toml
[git_metrics]
disabled = false
```

## Right-Side Time

The right side of the prompt shows a 24-hour clock:

```
❯                                                             14:32
```

This is configured by:

```toml
right_format = """$time"""

[time]
disabled = false
style = "dimmed text"
time_format = "%H:%M"
```

Change `time_format` to `"%I:%M %p"` for 12-hour format (e.g., `2:32 PM`).

## Catppuccin Macchiato

The prompt uses the **Catppuccin Macchiato** color palette. Every tool in this
repo — starship, bat, delta, fzf, lazygit, yazi — shares the same palette for
visual consistency.

The palette is defined at the bottom of `starship.toml`:

```bash
tail -30 ~/.config/starship.toml
```

Key colors used in the prompt:

| Name | Hex | Used for |
|------|-----|----------|
| blue | `#8aadf4` | Directories |
| mauve | `#c6a0f6` | Git branch, prompt char (success) |
| peach | `#f5a97f` | Git status |
| red | `#ed8796` | Prompt char (error), line deletions |
| green | `#a6da95` | Line additions (git metrics) |
| text | `#cad3f5` | Time display |

## Customization

Changes to `~/.config/starship.toml` take effect on the next prompt — no restart
needed. Common tweaks:

- **Reorder segments:** edit the `format` string to rearrange `$directory`,
  `$git_branch`, etc.
- **Add languages:** add modules like `$python`, `$rust`, `$golang` to `format`
  (they auto-detect by project files)
- **Longer paths:** increase `truncation_length` in `[directory]` (default is 3)
- **12-hour clock:** change `time_format` to `"%I:%M %p"` in `[time]`
- **Cloud context:** uncomment `[aws]` or `[kubernetes]` in the config to show
  the active account/cluster

## Next

[Lesson 03 — File Operations →](03-file-operations.md)
