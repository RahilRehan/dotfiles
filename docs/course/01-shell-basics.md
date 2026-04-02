<!-- docs/course/01-shell-basics.md -->

# Lesson 01 — Shell Basics

This lesson covers the shell infrastructure from the ground up: how fast it starts, what options shape daily work, how plugins load without slowing you down, and the utilities that tie it all together.

## Shell Startup

A sluggish shell is a constant tax on your workflow. Every new tab, every `exec zsh`, every tmux split — you feel it. Measure yours:

```bash
time zsh -ic exit
```

Expected output (in this Docker container):

```
zsh -ic exit  0.05s user 0.03s system 95% cpu 0.082 total
```

The number that matters is **total** time (~80ms here). Here's how to interpret it:

| Time | Rating | Typical setup |
|------|--------|---------------|
| < 50ms | Excellent | Minimal config or fully async loading |
| 50–150ms | Great | **This config** with zinit turbo mode |
| 150–300ms | Acceptable | Many plugins loading synchronously |
| 300–500ms | Slow | Oh My Zsh with many plugins enabled |
| > 500ms | Investigate | Something is blocking startup — profile it |

### Deep-dive profiling

If startup feels slow, the built-in profiler shows exactly where time goes. The `.zshrc` has hooks for this:

```bash
# In .zshrc — these two lines bracket all config loading:
[[ -n "$ZSH_PROFILE" ]] && zmodload zsh/zprof   # top of file
[[ -n "$ZSH_PROFILE" ]] && zprof                 # bottom of file
```

Set the variable and reload:

```bash
ZSH_PROFILE=1 exec zsh
```

This reloads the shell with `zprof` enabled. It prints a function-by-function timing breakdown — look for anything over 10ms. Common offenders: `compinit` (completion init), `nvm` (Node version manager), and synchronous plugin loading.

> **Exercise:** Run the profiler now. What's the slowest function? Is anything over 10ms?

## Shell Options (`10-options.zsh`)

Zsh has hundreds of options. This config enables the ones that meaningfully improve daily work. Each section below includes exercises so you can see the behavior firsthand.

### History

```bash
# SHARE_HISTORY: all terminal tabs share one history in real time.
# Open two terminals side by side and try this.
```

**Exercise — shared history across sessions:**

```bash
# Terminal 1:
echo "hello from terminal 1"

# Terminal 2 (immediately after):
history | tail -1
```

Expected output in Terminal 2:

```
  123  echo "hello from terminal 1"
```

The command appears instantly — no need to close/reopen the shell. `SHARE_HISTORY` implies `INC_APPEND_HISTORY`, so every command is written to `$HISTFILE` immediately and read by all sessions.

**Exercise — stealth mode with `HIST_IGNORE_SPACE`:**

```bash
# Prefix with a space to keep it out of history:
 export SECRET_KEY=abc123
history | tail -3
```

The `export` line won't appear — the leading space told zsh to skip it.

**Exercise — safe history expansion with `HIST_VERIFY`:**

```bash
echo hello
!!
```

Expected behavior:

```
$ echo hello
hello
$ !!
$ echo hello      ← loaded into edit buffer, NOT executed yet
```

Without `HIST_VERIFY`, `!!` would execute `echo hello` immediately. With it, zsh loads the expanded command into your prompt so you can inspect or edit it first. Press Enter to execute.

### Navigation

**Exercise — `AUTO_CD`:**

```bash
/tmp
pwd
```

```
/tmp
```

No `cd` needed — just type a directory path.

**Exercise — `AUTO_PUSHD` and the directory stack:**

```bash
cd /etc
cd /var
cd /tmp
dirs -v
```

```
0	/tmp
1	/var
2	/etc
3	~
```

Every `cd` pushes the old directory onto a stack. Jump to any entry by index:

```bash
cd ~2
pwd
```

```
/etc
```

### Globbing

**Exercise — `GLOB_DOTS`:**

```bash
cd /tmp && mkdir glob-test && cd glob-test
touch .hidden visible
echo *
```

```
.hidden visible
```

Without `GLOB_DOTS`, `echo *` would only show `visible`. Dotfiles are normally invisible to globs — this option includes them.

### Corrections

**Exercise — `CORRECT`:**

```bash
gti status
```

```
zsh: correct 'gti' to 'git' [nyae]?
```

| Key | Action |
|-----|--------|
| `y` | Accept the correction |
| `n` | Run the original command as-is |
| `a` | Abort — don't run anything |
| `e` | Edit the command line |

### Safety

**Exercise — `PIPE_FAIL`:**

```bash
false | true
echo $?
```

```
1
```

Without `PIPE_FAIL`, this returns `0` — hiding the fact that `false` failed. With it, the pipeline's exit code reflects the **first** failure, not just the last command. This catches silent failures in scripts like:

```bash
curl https://example.com/data | jq '.results'
# If curl fails, PIPE_FAIL ensures $? is non-zero even though jq "succeeds"
```

## XDG Base Directories (`00-env.zsh`)

Without XDG, every tool dumps dotfiles in `$HOME`. The XDG Base Directory spec gives tools standard locations so your home stays clean:

```bash
echo $XDG_CONFIG_HOME   # configuration files
echo $XDG_DATA_HOME     # persistent data
echo $XDG_CACHE_HOME    # disposable cache
echo $XDG_STATE_HOME    # state (history, logs)
```

```
/home/testuser/.config
/home/testuser/.local/share
/home/testuser/.cache
/home/testuser/.local/state
```

History uses XDG too — no more `~/.zsh_history` cluttering your home:

```bash
echo $HISTFILE
```

```
/home/testuser/.local/state/zsh/history
```

### Homebrew init

`00-env.zsh` also initializes Homebrew early — before anything else. This is deliberate: tools installed by Homebrew (starship, fzf, bat, eza, fd, etc.) must be on `$PATH` before `60-tools.zsh` tries to run their init hooks. If Homebrew weren't initialized here, `command -v starship` would fail in `60-tools.zsh` and the prompt would never set up.

The config detects all possible Homebrew install locations:

| Path | Platform |
|------|----------|
| `/opt/homebrew` | macOS (Apple Silicon) |
| `/usr/local` | macOS (Intel) |
| `/home/linuxbrew/.linuxbrew` | Linux (system-wide) |
| `$HOME/.linuxbrew` | Linux (user-local) |

```bash
# From 00-env.zsh:
if [ -f /opt/homebrew/bin/brew ]; then
    eval "$(/opt/homebrew/bin/brew shellenv)"
elif [ -f /usr/local/bin/brew ]; then
    eval "$(/usr/local/bin/brew shellenv)"
# ... linux paths ...
fi
```

`brew shellenv` exports `PATH`, `MANPATH`, and `INFOPATH`. The `eval` runs it inline so those variables are set for the current session.

> The Docker container doesn't use Homebrew — tools are installed via `apt`. The Homebrew block silently skips when none of these paths exist.

## The Plugin System (`20-plugins.zsh`)

### Why zinit over Oh My Zsh?

Oh My Zsh (OMZ) is the most popular zsh framework, but it loads everything **synchronously** — your prompt doesn't appear until all plugins finish initializing. With 10+ plugins, that means 300–500ms of staring at a blank terminal.

zinit replaces this with **turbo mode**: plugins load *after* the prompt renders, in the background. You see your prompt in ~50ms; plugins finish loading a moment later. You also get **cherry-pick** capability — grab individual OMZ plugins (like its git aliases) without loading the entire framework.

### Turbo mode

Every core plugin uses this pattern:

```
zinit wait lucid for <plugin>
```

| Flag | Purpose |
|------|---------|
| `wait` | Defer loading until after the prompt appears (async) |
| `lucid` | Suppress "Loaded plugin-name" messages |

The shell is fully usable the instant the prompt appears. Plugins finish loading ~100ms later — by the time your fingers reach the keyboard, everything is ready.

### The four core plugins

**Syntax highlighting** (`fast-syntax-highlighting`) — colors commands as you type. Valid commands turn green; typos turn red. You catch mistakes before pressing Enter.

```bash
echo hello       # "echo" appears green — valid command
asdfnotreal      # appears red — not found
```

**Autosuggestions** (`zsh-autosuggestions`) — ghost text from your history appears as you type. Press `→` (right arrow) to accept the full suggestion:

```bash
# Type "ech" — you'll see a dim "o hello" suggested from history.
# Press → to accept, or keep typing to ignore.
```

**History substring search** (`zsh-history-substring-search`) — type part of a command, then press `↑`/`↓` to cycle through only matching history entries:

```bash
# Type "git" then press ↑ — cycles through only commands containing "git",
# not your entire history. Much faster than ctrl-r for recent commands.
```

**Extra completions** (`zsh-completions`) — community-maintained tab completions for 200+ tools (docker, terraform, cargo, kubectl, etc.). Without this, many tools have no tab completion at all.

### Cherry-picked OMZ plugins

Instead of loading the entire OMZ framework, zinit grabs individual snippets:

**git** (`OMZP::git`) — adds 100+ git aliases. Some highlights:

| Alias | Expands to |
|-------|-----------|
| `ga` | `git add` |
| `gc` | `git commit -v` |
| `gco` | `git checkout` |
| `gd` | `git diff` |
| `gp` | `git push` |
| `gl` | `git pull` |
| `gst` | `git status` |
| `glog` | `git log --oneline --decorate --graph` |

**Exercise — try the git aliases:**

```bash
cd /tmp && mkdir alias-test && cd alias-test && git init
gst
```

```
On branch main

No commits yet

nothing to commit (create a copy to track)
```

**sudo** (`OMZP::sudo`) — press `Esc Esc` (Escape twice) to prepend `sudo` to the current or previous command. Faster than reaching for the Home key:

```bash
# Type: apt update
# Press Esc Esc → line becomes: sudo apt update
```

### Completion initialization

At the bottom of `20-plugins.zsh`, this line ties the completion system together:

```
zinit wait lucid atinit"zicompinit; zicdreplay" for zdharma-continuum/null
```

This does two things after all turbo-mode plugins finish loading:

1. **`zicompinit`** — calls `compinit`, zsh's completion initialization. This scans all completion functions and builds the completion database. It's deferred here (instead of running at startup) so it doesn't block the prompt.
2. **`zicdreplay`** — replays any `compdef` calls that plugins made during turbo loading. Because plugins loaded asynchronously, their completion registrations were queued — `zicdreplay` applies them all at once.

The `zdharma-continuum/null` is a no-op plugin used purely as a vehicle for the `atinit` hook.

## Completions (`30-completions.zsh`)

The completion system makes Tab significantly more powerful. All configuration uses `zstyle`, zsh's styling engine for the completion system:

```bash
# Case-insensitive: "doc<Tab>" matches "Documents"
ls /etc/hos         # press Tab → completes to /etc/hosts or /etc/hostname

# Menu selection: when there are multiple matches, arrow keys to navigate
ls /etc/            # press Tab → navigable menu of completions
```

Key `zstyle` settings configured:

| Feature | `zstyle` pattern | What it does |
|---------|-----------------|-------------|
| Case-insensitive | `matcher-list 'm:{a-zA-Z}={A-Za-z}'` | `doc` + Tab matches `Documents` |
| Menu selection | `menu select` | Arrow keys navigate the completion list |
| LS_COLORS | `list-colors "${(s.:.)LS_COLORS}"` | Files colored by type (dirs blue, executables green) |
| Group headers | `format '%F{yellow}-- %d --%f'` | Completions grouped by type with yellow headers |
| "No matches" | `format '%F{red}-- no matches --%f'` | Red message instead of silent failure |
| Caching | `use-cache on` | Completions cached in `$XDG_CACHE_HOME/zsh/zcompcache` |

Caching is especially important for slow completions — tools like `docker` and `kubectl` generate completions dynamically, and caching avoids regenerating them every time.

## Helper Functions (`50-functions.zsh`)

### `mkcd` — create and enter a directory

```bash
mkcd /tmp/my-new-project
pwd
```

```
/tmp/my-new-project
```

Equivalent to `mkdir -p dir && cd dir`, but saves typing and handles errors.

### `extract` — decompress any archive format

Handles `.tar.gz`, `.tar.bz2`, `.tar.xz`, `.tar.zst`, `.zip`, `.7z`, `.rar`, `.xz`, `.zst`, and more. It inspects the extension and picks the right tool — no need to remember `tar xjf` vs `tar xzf` vs `tar xJf`:

```bash
extract archive.tar.gz
```

### `killport` — kill a process by port number

> **Host only:** `killport` uses `lsof`, which is not installed in the Docker playground. Works on macOS and most Linux desktops.

```bash
killport 3000
```

```
Sent SIGTERM to 12345 on port 3000
```

Sends `SIGTERM` first; if the process survives after 1 second, follows up with `SIGKILL`. Useful when a dev server won't let go of a port.

### `serve` — instant HTTP file server

> **Host only:** `serve` uses `python3 -m http.server`, which is not installed in the Docker playground. Works on any system with Python 3.

```bash
serve 3000    # serves current directory on http://localhost:3000
```

Defaults to port 8000 if no argument given.

## The EDITOR Fallback Chain (`00-env.zsh`)

Many tools — `git commit`, `crontab -e`, `kubectl edit` — open `$EDITOR`. The config sets it with a portability chain that picks the first available editor:

```
cursor --wait  →  nvim  →  vim
```

```bash
# From 00-env.zsh:
if command -v cursor &>/dev/null; then
    export EDITOR="cursor --wait"
elif command -v nvim &>/dev/null; then
    export EDITOR="nvim"
else
    export EDITOR="vim"
fi
export VISUAL="$EDITOR"
```

The `--wait` flag on Cursor makes the command **block** until you close the file — without it, `git commit` would immediately see an empty message and abort. On a dev machine with Cursor installed, you edit commit messages in a full GUI editor. On a server with only `vim`, it still works.

```bash
echo $EDITOR
```

In this Docker container (Cursor and Neovim aren't installed):

```
vim
```

`$VISUAL` is set to the same value. Historically `VISUAL` was for full-screen editors and `EDITOR` for line editors — most modern tools check both, so setting them identically avoids surprises.

## Next

[Lesson 02 — The Prompt →](02-the-prompt.md)
