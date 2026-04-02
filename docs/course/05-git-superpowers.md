# Lesson 05 — Git Superpowers

A modern `.gitconfig`, beautiful diffs, 100+ aliases, a visual TUI, and multi-account support. This lesson covers the git setup that ties it all together.

## Modern .gitconfig

Our git config enables features most developers never turn on. Run `bat ~/.gitconfig` to see the full file — here's what each section does and **why**.

### Init

```ini
[init]
    defaultBranch = main
```

All new repos start with `main` instead of `master`. Matches GitHub/GitLab defaults.

### Core

```ini
[core]
    pager = delta
    autocrlf = input
    excludesFile = ~/.config/git/ignore
```

| Setting | Why |
|---------|-----|
| `pager = delta` | All diff output (diff, log, show) goes through delta for syntax highlighting, side-by-side layout, and line numbers |
| `autocrlf = input` | Converts CRLF → LF on commit. Prevents Windows line endings from leaking into the repo |
| `excludesFile` | Points to a global gitignore so OS junk and editor files are ignored everywhere without per-repo `.gitignore` entries |

### Pull, push, and fetch

```ini
[pull]
    rebase = true

[push]
    default = current
    autoSetupRemote = true
    followTags = true

[fetch]
    prune = true
    pruneTags = true
```

| Setting | What it does | Why it matters |
|---------|-------------|---------------|
| `pull.rebase = true` | `git pull` rebases local commits on top of remote instead of creating a merge commit | Keeps history linear — no "Merge branch 'main' into main" clutter |
| `push.default = current` | `git push` pushes the current branch to a same-named remote branch | Predictable default — no ambiguity about what gets pushed |
| `push.autoSetupRemote = true` | First `git push` auto-creates the upstream tracking branch | No more `git push --set-upstream origin my-branch` |
| `push.followTags = true` | `git push` includes tags that point to pushed commits | Tags don't get left behind |
| `fetch.prune = true` | Auto-deletes local tracking refs when the remote branch is deleted | `git branch -r` stays clean |

### Merges and conflict resolution

```ini
[merge]
    conflictstyle = zdiff3

[rerere]
    enabled = true
```

**`conflictstyle = zdiff3`** — Standard conflicts show two sides (yours vs theirs). zdiff3 shows **three**: yours, the original, and theirs. Seeing what the code looked like *before either side changed it* makes conflicts dramatically easier to resolve:

```
<<<<<<< yours
  return user.fullName();
||||||| original
  return user.name;
======= theirs
  return user.getName();
>>>>>>>
```

**`rerere.enabled`** — "REuse REcorded REsolution." If you resolve a merge conflict, git remembers the resolution. Next time the same conflict appears (common during long-running rebases), it's resolved automatically.

### Rebase

```ini
[rebase]
    autostash = true
    autosquash = true
```

**`autostash`** — You have uncommitted changes and need to rebase? Git automatically stashes them before rebasing and re-applies them after. No more "Cannot rebase: You have unstaged changes" errors.

**`autosquash`** — Commits prefixed with `fixup!` or `squash!` are automatically reordered during interactive rebase. The workflow: make a fix, commit it with `git commit --fixup=<sha>`, then `git rebase -i` handles the rest — the fixup commit is moved next to its target and marked for squashing.

### Smarter diffs

```ini
[diff]
    algorithm = histogram
    colorMoved = default
    renames = copies
```

| Setting | Effect |
|---------|--------|
| `algorithm = histogram` | Produces fewer nonsensical diff hunks on large files — more semantically meaningful changes |
| `colorMoved = default` | Lines that were **moved** (not added/removed) get a distinct color. When you refactor by moving a function to a new file, the diff shows those lines in a different color instead of marking them as "deleted here, added there" — so you can instantly tell a move from new code |
| `renames = copies` | Detects file copies in addition to renames — `git diff` shows "renamed: a.py → b.py" instead of a full delete + add |

### Branch sorting

```ini
[branch]
    sort = -committerdate
```

`git branch` lists branches by most recently committed, not alphabetically. Your active branches appear first.

### Custom aliases

```ini
[alias]
    co = checkout
    br = branch
    ci = commit
    st = status
    undo = reset --soft HEAD~1
    wip = !git add -A && git commit -m 'wip'
    amend = commit --amend --no-edit
    today = log --since=midnight --oneline --no-merges
```

Quick shortcuts beyond the OMZ aliases covered later:

```bash
git undo     # Undo last commit, keep changes staged
git amend    # Add staged changes to last commit (no message edit)
git wip      # Stage everything + commit with message "wip"
git today    # Show your commits from today
```

### Try it

```bash
cd /tmp && mkdir git-demo && cd git-demo && git init
```

> **Docker note:** `git commit` requires an identity. The install script skips the interactive identity prompt in Docker, so you must set one manually:
>
> ```bash
> git config user.name "Test User"
> git config user.email "test@example.com"
> ```

```bash
git config user.name "Test User"
git config user.email "test@example.com"

echo "hello" > file.txt && git add . && git commit -m "first commit"
echo "world" >> file.txt && git add . && git commit -m "second commit"

# Undo the last commit (changes stay staged):
git undo
git status
```

Expected output:

```
On branch main
Changes to be committed:
  (use "git restore --staged <file>..." to unstage)
	modified:   file.txt
```

```bash
# Re-commit, then check today's log:
git commit -m "second commit"
git today
```

Expected output:

```
a1b2c3d second commit
f4e5d6a first commit
```

## delta — Beautiful Diffs

delta is configured as git's pager via `core.pager = delta`. Every `git diff`, `git log -p`, and `git show` runs through it automatically — no flags needed. The key settings from `.gitconfig`:

```ini
[delta]
    navigate = true
    dark = true
    side-by-side = true
    line-numbers = true

[interactive]
    diffFilter = delta --color-only
```

**`side-by-side = true`** means diffs are **already side-by-side by default**. Just run `git diff` and you get a two-column view with syntax highlighting and word-level change detection. There is no `--side-by-side` flag for git — the layout comes entirely from delta's config.

**`navigate = true`** lets you press **n** and **N** to jump between diff sections (files/hunks) when viewing long diffs in the pager.

**`diffFilter = delta --color-only`** applies delta's syntax highlighting to interactive commands like `git add -p`.

### Try it

```bash
cd /tmp/git-demo

# Make a change:
echo "hello universe" > file.txt

# See the diff — delta renders it side-by-side automatically:
git diff
```

Expected output (rendered by delta):

```
─── file.txt ──────────────────────────────────────────────
│ 1 │hello                         │ 1 │hello universe
│ 2 │world                         │   │
```

You'll see: syntax highlighting, line numbers on both sides, and word-level highlighting showing exactly what changed on each line.

```bash
# Commit and view the log with patches:
git add . && git commit -m "update greeting"
git log -p
# Patches are delta-rendered too. Press n/N to jump between files.
# Press q to exit.
```

> **Beware common mistakes:** There is no `git diff --side-by-side` flag — that's a delta config, not a git option. And `git diff -s` is shorthand for `--no-patch`, which produces **no output at all**. You never need either — just run `git diff`.

## OMZ Git Aliases

The Oh My Zsh `git` plugin is loaded via zinit (see `20-plugins.zsh`):

```zsh
zinit snippet OMZP::git
```

This provides **100+ short aliases** for common git commands. You don't need to memorize them all — here are the ones you'll use daily:

| Alias | Expands to | Notes |
|-------|-----------|-------|
| `gst` | `git status` | |
| `ga` | `git add` | `ga .` to stage everything |
| `gc` | `git commit --verbose` | Shows diff in commit message editor |
| `gc!` | `git commit --verbose --amend` | Amend last commit |
| `gco` | `git checkout` | |
| `gcb` | `git checkout -b` | Create and switch to new branch |
| `gd` | `git diff` | Uses delta automatically |
| `gp` | `git push` | |
| `gl` | `git pull` | |
| `glog` | `git log --oneline --decorate --graph` | Visual branch history |
| `grb` | `git rebase` | |
| `gsta` | `git stash push` | |
| `gstp` | `git stash pop` | |

> **Docker note:** `gp` (`git push`) and `gl` (`git pull`) won't work in the Docker playground — there's no remote configured. All other aliases work fine with local repos.

### Try it

```bash
cd /tmp/git-demo

# Check status with the short alias:
gst
```

Expected output:

```
On branch main
nothing to commit, working tree clean
```

```bash
# Make a change, stage, and commit with aliases:
echo "new line" >> file.txt
ga file.txt
gc -m "add new line"

# View the log graphically:
glog
```

Expected output:

```
* a1b2c3d (HEAD -> main) add new line
* d4e5f6a update greeting
* b7c8d9e second commit
* c0d1e2f first commit
```

To see all available aliases, run `alias | rg "^g"`.

## lazygit — Git TUI

lazygit gives you a full visual interface for git. Launch it with `lg` (aliased in `40-aliases.zsh`) in any git repo.

```bash
cd /tmp/git-demo
lg
```

### The interface

lazygit has 5 panels. Press the **number keys** (`1`–`5`) or **`[`/`]`** to switch between them:

| # | Panel | Shows | Key actions |
|---|-------|-------|-------------|
| 1 | **Status** | Current branch, repo info | |
| 2 | **Files** | Changed/staged files | `space` stage/unstage, `a` stage all, `c` commit |
| 3 | **Branches** | Local + remote branches | `space` checkout, `n` new branch |
| 4 | **Commits** | Commit history | `s` squash, `r` reword, `f` fixup, `d` drop |
| 5 | **Stash** | Stashed changes | `space` apply, `g` pop |

Our config (`lazygit/.config/lazygit/config.yml`) sets Nerd Font icons, file icons, and the Catppuccin Macchiato theme. Delta is used as the pager inside lazygit too (`pager: delta --dark --paging=never`).

### Essential workflows

**Stage individual hunks** (partial file staging):
1. Files panel → press **Enter** on a file to see its diff
2. Navigate to a hunk → press **space** to stage just that hunk
3. Press **c** to commit only what you staged

**Interactive rebase:**
1. Commits panel → navigate to a commit → press **e** to start editing
2. Use: **s** = squash, **f** = fixup, **r** = reword, **d** = drop
3. Hunks reorder in real time as you move them

**Resolve merge conflicts:**
1. Files panel shows conflicted files with a `UU` marker
2. Press **Enter** on a conflicted file
3. Choose: pick ours / theirs / both for each conflict section

**Quick shortcuts:**

| Key | Action |
|-----|--------|
| `?` | Full keybinding help |
| `space` | Context-dependent action (stage, checkout, apply) |
| `c` | Commit |
| `p` | Push |
| `P` | Pull |
| `q` | Quit |

> **Docker note:** Push (`p`) and Pull (`P`) require a remote and won't work in the playground. Everything else — staging, committing, branching, rebasing — works locally.

### Try it

```bash
cd /tmp/git-demo

# Create some uncommitted changes:
echo "line A" >> file.txt
echo "new file" > other.txt

# Open lazygit:
lg

# In the Files panel:
#   - You should see file.txt (modified) and other.txt (untracked)
#   - Press space on file.txt to stage it
#   - Press c to commit, type a message, press Enter
#   - other.txt remains unstaged
#   - Press q to quit
```

## Multi-Account Git Setup

The `.gitconfig` uses `includeIf` to automatically switch git identities based on which directory a repo lives in:

```ini
[include]
    path = ~/.gitconfig.local              # fallback identity

[includeIf "gitdir:~/personal/"]
    path = ~/.gitconfig-personal           # repos under ~/personal/

[includeIf "gitdir:~/workplace/"]
    path = ~/.gitconfig-work               # repos under ~/workplace/
```

**How it works:** When you run a git command, git checks the repo's path. If it's under `~/personal/`, the identity from `~/.gitconfig-personal` is used. Under `~/workplace/`, it uses `~/.gitconfig-work`. Everywhere else, the fallback `~/.gitconfig.local` applies.

The identity files are **not tracked in git** (they contain your real name and email). Create them with:

```bash
git config --file ~/.gitconfig.local    user.name "Your Name"
git config --file ~/.gitconfig.local    user.email "you@example.com"

git config --file ~/.gitconfig-personal user.name "Your Name"
git config --file ~/.gitconfig-personal user.email "personal@example.com"

git config --file ~/.gitconfig-work     user.name "Your Name"
git config --file ~/.gitconfig-work     user.email "work@company.com"
```

The install script prompts for these on first run.

### Verify it

```bash
# On your host machine, check which identity a repo uses:
cd ~/personal/some-repo
git config user.email
# → personal@example.com

cd ~/workplace/some-repo
git config user.email
# → work@company.com
```

> **Host only** — This setup is for your host machine. In the Docker playground, git identities aren't configured (the install script skips the interactive prompt). Use `git config user.name` / `git config user.email` per-repo as shown earlier.

## Global Gitignore

A global gitignore prevents OS junk, editor files, and secrets from ever appearing in `git status`:

```bash
bat ~/.config/git/ignore
```

It covers:
- **OS files:** `.DS_Store`, `Thumbs.db`
- **Editor files:** `.idea/`, `.vscode/`, `*.swp`
- **Secrets:** `.env`, `.env.local`, `*.pem`, `*.key`
- **Language artifacts:** `node_modules/`, `__pycache__/`, `venv/`, `target/`, `vendor/`
- **Tools:** `.direnv/`, `*.log`
- **Infra:** `.terraform/`, `*.tfstate`

This is set via `core.excludesFile = ~/.config/git/ignore` in `.gitconfig`, so it applies to every repo without needing per-repo `.gitignore` entries.

## Cheat Sheet

| Task | Command |
|------|---------|
| Status | `gst` |
| Stage files | `ga file.txt` or `ga .` |
| Commit | `gc -m "message"` |
| Amend last commit | `gc!` or `git amend` |
| Undo last commit | `git undo` |
| View diff (side-by-side via delta) | `gd` |
| View log with patches | `git log -p` |
| Visual branch graph | `glog` |
| WIP commit | `git wip` |
| Today's commits | `git today` |
| Open lazygit | `lg` |
| Jump between diff sections | `n` / `N` (in pager) |
| Check active git identity | `git config user.email` |
| All git aliases | `alias \| rg "^g"` |

## Next

[Lesson 06 — Terminal Multiplexing →](06-terminal-multiplexing.md)
