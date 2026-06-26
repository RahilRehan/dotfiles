# Power Tools Reference

This environment has modern CLI tools installed. Use them instead of legacy equivalents.

## Quick Reference — Common Tasks

### Find files by name
```bash
fd "pattern"              # FASTEST — find by name pattern
fd . -t f                 # list ALL files recursively
fd . -t d                 # list ALL directories recursively
fd -e ts                  # find all .ts files
fd -e py -e pyi           # find all Python files
```

### Search file contents
```bash
rg "pattern"              # FASTEST — search everywhere
rg "pattern" -t py        # search only Python files
rg "pattern" -l           # list matching filenames only
rg "pattern" -C 3         # show 3 lines of context
rg "pattern" --json       # structured output
```

### List files
```bash
rg --files                # all files (respects .gitignore)
eza -la --git             # detailed listing with git status
eza --tree --level=2      # tree view, 2 levels deep
```

### View file contents
```bash
bat file.py               # syntax-highlighted, with line numbers
bat -p file.py            # plain output (no line numbers/header)
bat -r 10:20 file.py      # show only lines 10-20
```

### Navigate directories
```bash
z project                 # jump to most-visited match (zoxide)
zi                        # interactive directory picker (zoxide)
y                         # visual file browser (yazi), cd on quit
```

### Search interactively
```bash
# ctrl-t                  # fzf: find file (with bat preview)
# alt-c                   # fzf: find directory (with eza tree preview)
# ctrl-r                  # atuin: fuzzy shell history search
```

### Git
```bash
lg                        # lazygit TUI (stage, commit, push, rebase)
git diff                  # diffs render through delta pager automatically
git log -p                # log with diffs — also rendered through delta
```

### Runtime versions
```bash
mise install              # install tools from .mise.toml
mise use node@20          # set node version for current project
mise ls                   # list installed tool versions
```

### Environment variables
```bash
# .envrc files auto-load via direnv on cd
direnv allow              # approve an .envrc after editing
```

### System info
```bash
dust                      # visual disk usage tree (du replacement)
duf                       # disk free overview (df replacement)
btm                       # system monitor with graphs (top replacement)
procs                     # process viewer with tree (ps replacement)
```

### Utilities
```bash
tldr tar                  # quick man page summary (the 20% you need)
sd 'old' 'new' file      # find-and-replace (sed replacement)
glow README.md            # render markdown in terminal
hyperfine 'cmd1' 'cmd2'  # benchmark commands statistically
just                      # run project tasks from justfile
```

### Containers
```bash
lzd                       # lazydocker TUI (containers, images, logs)
k9s                       # Kubernetes TUI (pods, logs, exec)
```

## Banned — Never Use These

| Banned | Use Instead | Why |
|--------|-------------|-----|
| `find` | `fd` | fd is faster, simpler syntax, respects .gitignore |
| `grep` / `grep -r` | `rg` | ripgrep is 10-100x faster, better defaults |
| `tree` | `fd . -t f` or `eza --tree` | tree may not be installed, these are faster |
| `ls -R` | `rg --files` or `fd` | recursive ls is slow and unreadable |
| `cat file \| grep` | `rg pattern file` | single tool, no pipe overhead |
| `nvm` / `pyenv` / `rbenv` | `mise` | mise replaces all version managers |
| `cat` (for viewing) | `bat` | syntax highlighting, line numbers, git changes (`cat` is fine for piping) |
| `cd` (for jumping) | `z` | zoxide learns your frequent directories |
| `du` | `dust` | disk usage with visual tree, sorted by size |
| `df` | `duf` | disk free with colors, grouped by filesystem type |
| `top` / `htop` | `btm` | graphs, filtering, process search |
| `ps` | `procs` | tree view, keyword search, colored |
| `sed` | `sd` | simpler regex syntax, no escaping headaches |
| `man` (for quick ref) | `tldr` | community examples, just the useful parts |
