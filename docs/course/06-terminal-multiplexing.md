# Lesson 06 — Terminal Multiplexing

## Why tmux?

Every developer eventually needs more than one terminal. Maybe you're editing code, running tests, and tailing logs — all at the same time. You could open multiple terminal windows, but what happens when you accidentally close one? Or SSH into a server and your connection drops?

tmux solves both problems:

- **Split one terminal** into multiple panes and windows
- **Persist sessions** that survive disconnects, terminal crashes, and logouts

You start tmux once and live inside it. Everything you do is preserved — close your laptop, reopen it, reattach, and pick up exactly where you left off.

## The Mental Model

Before touching any keybindings, understand how tmux organizes things. There are three layers, and they nest like this:

```
Session          (a project workspace — e.g. "dotfiles", "webapp")
├── Window       (a full-screen tab — e.g. "editor", "tests")
│   ├── Pane     (a split within the window)
│   └── Pane
├── Window
│   └── Pane
└── Window
    ├── Pane
    ├── Pane
    └── Pane
```

| Layer   | Analogy              | Key idea                                      |
|---------|----------------------|-----------------------------------------------|
| Session | A project workspace  | Top-level container. Persists in the background. |
| Window  | A browser tab        | Fills the whole screen. Belongs to one session. |
| Pane    | A split view         | A subdivision of a window. Each runs its own shell. |

A **session** contains one or more **windows**. Each **window** fills the screen and contains one or more **panes**. Think of it as: sessions are projects, windows are tabs, panes are split views within a tab.

This hierarchy is the single most important thing to internalize. Every tmux command operates on one of these three layers.

## The Prefix Key

Our prefix key is **`ctrl-a`** (not the default `ctrl-b`). It's a one-handed reach and a classic GNU Screen binding.

**How it works:** every tmux shortcut is a two-step sequence, not a chord.

1. Press `ctrl-a` (hold ctrl, tap a)
2. **Release both keys**
3. Press the next key

For example, to split vertically: press `ctrl-a`, let go, then press `|`. You are *not* holding ctrl-a while pressing the next key. Get this wrong and nothing will happen — it's the most common beginner mistake.

Throughout this lesson, `ctrl-a X` means "prefix, release, then X".

## Starting tmux

```bash
tmux new -s dotfiles
```

You're now inside a tmux session named "dotfiles". Notice the **status bar at the top of the screen** — most tmux configs put it at the bottom, but ours puts it at the top. It shows:

```
 dotfiles  1:zsh                                  Thu 02 Apr │ 14:30
```

- **Left:** session name (`dotfiles`)
- **Center:** window list (currently just `1:zsh` — window number 1 running zsh)
- **Right:** date and time

> **Windows are numbered starting at 1**, not 0. This is configured in our `tmux.conf` with `base-index 1`. The number keys on your keyboard map naturally — `ctrl-a 1` goes to the first window.

## Panes (Splits)

Panes split your current window into sections. Each pane runs its own independent shell.

```
ctrl-a |        split vertically (side by side)
ctrl-a -        split horizontally (top and bottom)
```

The bindings are mnemonic — `|` looks like a vertical divider, `-` looks like a horizontal one. New panes open in the same directory as the pane you split from.

Navigate between panes with vim-style keys:

```
ctrl-a h        move left
ctrl-a j        move down
ctrl-a k        move up
ctrl-a l        move right
```

Resize panes with the uppercase versions (these are repeatable — press prefix once, then hold the key):

```
ctrl-a H        resize left
ctrl-a J        resize down
ctrl-a K        resize up
ctrl-a L        resize right
```

Close a pane by exiting its shell:

```
exit            or ctrl-d
```

> **Mouse is enabled.** You can click a pane to focus it, drag borders to resize, and scroll to enter copy mode. The mouse works alongside all the keyboard shortcuts — use whichever feels natural.

### Exercise: Your First Split

```bash
# 1. Start a fresh session:
tmux new -s panes

# 2. Split vertically:
#    Press ctrl-a, release, press |
#    You now see two panes side by side. Your cursor is in the right pane.

# 3. In the right pane, run:
echo "right pane"
```

Expected layout — two panes side by side:

```
 panes  1:zsh
╭──────────────────────┬──────────────────────╮
│ $                    │ $ echo "right pane"  │
│                      │ right pane           │
│                      │ $                    │
│                      │                      │
│                      │                      │
╰──────────────────────┴──────────────────────╯
```

```bash
# 4. Move to the left pane:
#    Press ctrl-a h

# 5. Split the left pane horizontally:
#    Press ctrl-a -
#    The left side is now split top and bottom. Cursor is in the bottom-left.

# 6. Run something in the bottom-left pane:
echo "bottom left"
```

Expected layout — three panes:

```
 panes  1:zsh
╭──────────────────────┬──────────────────────╮
│ $                    │ $ echo "right pane"  │
│                      │ right pane           │
├──────────────────────┤ $                    │
│ $ echo "bottom left" │                      │
│ bottom left          │                      │
│ $                    │                      │
╰──────────────────────┴──────────────────────╯
```

```bash
# 7. Practice navigating: ctrl-a h/j/k/l to move between all three panes.
# 8. Practice resizing: ctrl-a H/J/K/L to make the left column wider or narrower.
# 9. Close the bottom-left pane: type exit (or ctrl-d).
#    You're back to two panes.
```

## Windows (Tabs)

Windows are like browser tabs — each one fills the entire screen and can contain its own arrangement of panes.

```
ctrl-a c        create a new window (inherits current directory)
ctrl-a ,        rename current window (type a name, press Enter)
ctrl-a 1        go to window 1
ctrl-a 2        go to window 2
ctrl-a n        next window
ctrl-a p        previous window
```

The status bar shows all windows. The active window is highlighted in a different color:

```
 dotfiles  1:editor  2:tests  3:logs
```

Remember: windows start at **1**, so `ctrl-a 1` is always your first window.

### Exercise: Create Named Windows

```bash
# Make sure you're in a tmux session, then:

# 1. Rename the current window:
#    Press ctrl-a ,
#    Backspace to clear the default name, type: editor
#    Press Enter

# 2. Create a second window:
#    Press ctrl-a c

# 3. Rename it:
#    Press ctrl-a ,
#    Type: tests
#    Press Enter

# 4. Switch back to window 1:
#    Press ctrl-a 1
```

Expected status bar:

```
 dotfiles  1:editor  2:tests
```

You're now on window 1 (`editor`). Press `ctrl-a 2` to jump to `tests`, `ctrl-a 1` to jump back.

## Sessions

Sessions are the top-level container. Each session is an independent workspace with its own set of windows and panes. Sessions persist in the background — you can detach from one and reattach later, even after closing your terminal.

### Detaching and Reattaching

```
ctrl-a d        detach from current session (session keeps running)
```

From outside tmux (your regular terminal):

```bash
tmux ls                       # list all running sessions
tmux new -s webapp            # create a new session named "webapp"
tmux attach -t dotfiles       # reattach to a session by name
tmux a                        # reattach to the most recent session
tmux kill-session -t webapp   # destroy a session
```

Switch between sessions from inside tmux:

```
ctrl-a (        previous session
ctrl-a )        next session
ctrl-a s        interactive session picker (arrow keys + Enter)
```

### detach-on-destroy

Our config sets `detach-on-destroy off`. This changes what happens when you close the last window in a session:

| | Last window closes |
|---|---|
| **Default tmux** | Detaches you to your regular terminal (you leave tmux) |
| **Our config** | Switches you to another active session (you stay in tmux) |

This means you stay inside tmux as long as any session exists. No surprise exits back to a bare terminal.

### Exercise: Multi-Session Workflow

```bash
# 1. Create two sessions (from outside tmux):
tmux new -s frontend -d       # -d creates the session without attaching
tmux new -s backend -d

# 2. List them:
tmux ls
```

Expected output:

```
backend: 1 windows (created Thu Apr  2 14:30:00 2026)
frontend: 1 windows (created Thu Apr  2 14:30:00 2026)
```

```bash
# 3. Attach to frontend:
tmux a -t frontend

# 4. Switch to backend without detaching:
#    Press ctrl-a )
#    The status bar now shows "backend" on the left.

# 5. Kill the backend session (type inside it):
exit
```

Because `detach-on-destroy` is off, tmux switches you to the `frontend` session instead of kicking you out to a bare terminal. Check the status bar — it says `frontend`.

```bash
# 6. Verify only frontend remains:
#    Press ctrl-a s (session picker)
#    You should see only "frontend" listed. Press Escape to close.
```

## Copy Mode

Copy mode lets you scroll back through output, search, and copy text — all with vim keybindings (our config uses `mode-keys vi`).

Enter copy mode:

```
ctrl-a [        enter copy mode
```

Once in copy mode, the cursor becomes movable. Use:

```
j / k           scroll line by line
ctrl-d / ctrl-u half-page down / up
/pattern        search forward
?pattern        search backward
n / N           next / previous match
```

To select and copy text:

```
v               start selection (like vim visual mode)
y               yank (copy) selection and exit copy mode
ctrl-a ]        paste the last copied text
```

Press `q` or `Escape` to exit copy mode without copying.

> You can also scroll with the mouse wheel — it enters copy mode automatically. Click to exit.

## Config Highlights

Key settings from our `tmux.conf` that affect your daily workflow:

| Setting | What it does |
|---------|-------------|
| `mouse on` | Click panes to focus, drag borders to resize, scroll to enter copy mode |
| `base-index 1` | Windows and panes start at 1, not 0 — maps naturally to keyboard number keys |
| `status-position top` | Status bar at the top of the screen (most configs use bottom) |
| `detach-on-destroy off` | Close last window → switch to another session instead of detaching |
| `allow-passthrough on` | Lets programs send escape sequences through tmux — needed for image previews in yazi (next lesson) |
| `escape-time 0` | No delay after pressing Escape — critical for vim users |
| `set-clipboard on` | Yanked text in copy mode goes to your system clipboard via OSC 52 |
| `renumber-windows on` | Closing window 2 of 3 renumbers window 3 → 2 (no gaps) |

The `allow-passthrough` setting is worth calling out: without it, programs like yazi can't render image previews inside tmux. It passes through the Kitty graphics protocol and sixel escape sequences that terminals use to draw images. You'll see this in action in the next lesson.

### Quick Reload

After editing `tmux.conf`, reload without restarting:

```
ctrl-a r        displays "Config reloaded"
```

## Exercise: Build a Dev Layout

Combine everything you've learned into a realistic workspace:

```bash
# 1. Create a session:
tmux new -s dev

# 2. Rename the window to "code":
#    ctrl-a ,  →  type "code"  →  Enter

# 3. Split vertically (editor left, terminal right):
#    ctrl-a |

# 4. In the right pane, split horizontally (shell top, logs bottom):
#    ctrl-a -

# 5. Navigate to each pane and run something:
#    Left pane (ctrl-a h):        bat ~/.config/tmux/tmux.conf
#    Top-right pane (ctrl-a l):   ls -la
#    Bottom-right pane (ctrl-a j): echo "watching logs..."
```

Expected layout in the "code" window:

```
 dev  1:code
╭──────────────────────────┬──────────────────────╮
│ (bat output of           │ $ ls -la             │
│  tmux.conf, syntax       │ total 42             │
│  highlighted)            │ drwxr-xr-x  ...      │
│                          │ -rw-r--r--  ...      │
│                          ├──────────────────────┤
│                          │ $ echo "watching lo… │
│                          │ watching logs...     │
╰──────────────────────────┴──────────────────────╯
```

```bash
# 6. Create a second window for git:
#    ctrl-a c
#    ctrl-a ,  →  type "git"  →  Enter
#    Run: git status

# 7. Switch between windows:
#    ctrl-a 1 → "code" window (with your three-pane layout)
#    ctrl-a 2 → "git" window
```

Expected status bar:

```
 dev  1:code  2:git
```

```bash
# 8. Detach from this session:
#    ctrl-a d

# 9. Verify it's still running:
tmux ls
```

Expected output:

```
dev: 2 windows (created Thu Apr  2 14:35:00 2026)
```

```bash
# 10. Reattach — everything is exactly as you left it:
tmux a -t dev
```

Your three-pane layout in "code", your "git" window, all the output — still there.

## Next

[Lesson 07 — File Manager →](07-file-manager.md)
