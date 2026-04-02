# Lesson 07 — File Manager (yazi)

## Launch

There are two ways to open yazi:

```bash
y                             # wrapper function (cd on quit)
yazi                          # raw yazi (no cd on quit)
```

**Always use `y`.** When you quit yazi, the `y` wrapper changes your shell's working directory to wherever you last navigated. Raw `yazi` doesn't — you'll be right where you started. We'll explain the mechanics later in this lesson.

## The Interface

yazi uses **Miller columns** — three panels that give you context at every level:

```
┌─────────────┬───────────────────┬──────────────────────┐
│ Parent dir  │ Current dir       │ Preview              │
│             │                   │                      │
│ bat/        │ > 00-env.zsh   4K │ # Environment vars   │
│ claude/     │   10-options.zsh  │ # set before zsh     │
│ docs/       │   20-plugins.zsh  │ # reads its configs  │
│ git/        │   30-completions… │ ...                  │
│ > zsh/      │   40-aliases.zsh  │                      │
│ yazi/       │   50-functions…   │                      │
│             │   60-tools.zsh    │                      │
└─────────────┴───────────────────┴──────────────────────┘
```

**Left column** — the parent directory. `zsh/` is highlighted because that's where we are.
**Center column** — the current directory's contents with the cursor on `00-env.zsh`.
**Right column** — a live preview of whatever is selected: syntax-highlighted code for text files, a listing for directories, even images in terminals that support it (thanks to `allow-passthrough on` in our tmux config).

Two things to notice that come from our config:

- **File sizes are shown** next to each entry — `linemode = "size"` in our `yazi.toml`.
- **Dotfiles are visible by default** — `show_hidden = true`. Press `.` to toggle them off, but in a dotfiles repo you'll want them visible.

## Navigation

yazi uses vim-style keys:

```
h               go to parent directory (left)
l               enter directory / open file (right)
j               move down
k               move up

g g             jump to first item
G               jump to last item
/               search by filename (fuzzy)

~               go to home directory
.               toggle hidden files (already shown by default)
```

### Exercise: Navigate the Dotfiles

```bash
y ~/dotfiles
```

**Step 1** — You see the dotfiles repo in the center column. Press `j`/`k` until `zsh/` is highlighted, then press `l` to enter it.

**Step 2** — Enter `.config/` (`l`), then `zsh/` (`l` again). You should now see the modular zsh config files:

```
┌─────────────┬───────────────────┬──────────────────────┐
│ .config/    │ > 00-env.zsh      │ # Environment vars   │
│             │   10-options.zsh  │ # ...                │
│ > zsh/      │   20-keybindings… │                      │
│             │   20-plugins.zsh  │                      │
│             │   30-completions… │                      │
│             │   40-aliases.zsh  │                      │
│             │   50-functions…   │                      │
│             │   60-tools.zsh    │                      │
│             │   70-platform.zsh │                      │
└─────────────┴───────────────────┴──────────────────────┘
```

**Step 3** — Press `j` to move down to `40-aliases.zsh`. The right column updates to show a syntax-highlighted preview of the alias file.

**Step 4** — Press `h` three times to go back to the repo root.

**Step 5** — Press `q` to quit. Now check your shell:

```bash
pwd
```

Expected output:

```
/root/dotfiles
```

Because you used `y`, your shell followed you. If you'd used `yazi`, `pwd` would still show wherever you launched from.

## File Operations

### Selecting

Select files first, then act on them:

```
space           toggle selection on current file
V               visual mode (select a range with j/k)
```

Operations work on selected files, or the current file if nothing is selected.

### Keys

```
y               yank (copy) — stages files for pasting
x               cut — stages files for moving
p               paste — copies or moves yanked/cut files to current directory
d               trash (recoverable — moves to system trash)
D               permanent delete (gone forever, confirms first)
r               rename
a               create new file
A               create new directory
```

> **Watch out:** many file managers use `c` for copy and `d` for delete. yazi follows vim conventions — `y` (yank) for copy. And `d` only moves to **trash** (recoverable). You need `D` (shift-d) for permanent deletion.

### Exercise: Copy, Trash, Rename

Set up a scratch directory:

```bash
mkdir -p /tmp/yazi-practice && cd /tmp/yazi-practice
echo "alpha" > a.txt
echo "bravo" > b.txt
echo "charlie" > c.txt
y .
```

Inside yazi:

**Step 1 — Copy a file:** highlight `a.txt`, press `y` (yank). Press `A`, type `backup`, press Enter to create a directory. Press `l` to enter `backup/`. Press `p` to paste. You see `a.txt` appear in the `backup/` directory.

**Step 2 — Trash a file:** press `h` to go back to the parent. Highlight `b.txt`, press `d`. Confirm with `y`. The file disappears from the listing — it's in the system trash, not gone permanently.

**Step 3 — Rename a file:** highlight `c.txt`, press `r`. The filename becomes editable. Change it to `charlie.txt`, press Enter.

**Step 4** — Press `q` to quit. Verify from the shell:

```bash
ls
```

Expected output:

```
a.txt  backup  charlie.txt
```

```bash
ls backup/
```

Expected output:

```
a.txt
```

`b.txt` is gone from the listing (trashed). `c.txt` is now `charlie.txt`. And `a.txt` was copied (not moved) into `backup/`.

## Tabs

yazi supports tabs for working in multiple directories at once:

```
t               new tab (opens current directory)
1-9             switch to tab by number
[               previous tab
]               next tab
ctrl-c          close current tab
```

## The `y` Wrapper Explained

The difference in action:

```bash
# Without the wrapper:
pwd                           # /home/user
yazi                          # navigate to /etc/nginx, press q
pwd                           # /home/user — didn't change!

# With the wrapper:
pwd                           # /home/user
y                             # navigate to /etc/nginx, press q
pwd                           # /etc/nginx — shell followed you
```

The `y` function is defined in `60-tools.zsh`. It tells yazi to write its last directory to a temp file on quit. After yazi exits, the wrapper reads that file and `cd`s your shell there:

```bash
function y() {
    local tmp
    tmp="$(mktemp -t "yazi-cwd.XXXXXX")"
    yazi "$@" --cwd-file="$tmp"
    if cwd="$(command cat -- "$tmp")" && [ -n "$cwd" ] && [ "$cwd" != "$PWD" ]; then
        builtin cd -- "$cwd"
    fi
    rm -f -- "$tmp"
}
```

This turns yazi from "a file manager you look at" into "a file manager you navigate with." Always use `y`, not `yazi`.

## Config Notes

Our yazi config (`yazi/.config/yazi/yazi.toml`) is minimal — two overrides from defaults:

| Setting | Value | What it does |
|---------|-------|-------------|
| `show_hidden` | `true` | Dotfiles visible by default (toggle with `.`) |
| `linemode` | `"size"` | Shows file sizes next to filenames |

The Catppuccin Macchiato theme is installed as a flavor in `yazi/.config/yazi/flavors/`, giving yazi the same color scheme as the rest of our tools.

## Next

[Lesson 08 — Dev Environment →](08-dev-environment.md)
