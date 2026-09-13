# Your terminal toolkit

This setup is deliberately small. Learn one tool when a real task calls for it;
you do not need to memorise the list. The four commands worth learning first
are `rg`, `fd`, `z`, and `git diff`.

| Tool | Use it when | First thing to try |
|---|---|---|
| `rg` | You know text inside a file but not its location. | `rg "TODO"` |
| `fd` | You know a file name or extension. | `fd package.json` |
| `fzf` | You have a long list and want to pick one item. | Press `Ctrl-T` to insert a file path. |
| zoxide | You often visit the same directories. | `z dotfiles` |
| `bat` | You want to read a source or config file comfortably. | `bat ~/.zshrc` |
| `git` + delta | You need to see or record code changes. | `git diff` |
| lazygit | You want to stage, commit, or inspect Git visually. | `lg` |
| mise | A project needs a particular runtime version. | `mise install` in that project. |
| `uv` | A Python project needs a virtual environment or dependencies. | `uv init` in a new Python project. |
| direnv | A project has approved environment variables in `.envrc`. | `direnv allow` after reviewing it. |
| Starship | You want a prompt that shows directory and Git state. | It runs automatically. |

## The tools, in plain language

### `rg`: find text inside files

Use `rg` when you remember *what a file says*, not its name. It searches the
current directory recursively and skips ignored files such as `node_modules`.

```bash
rg "createUser"             # Where is this function mentioned?
rg "TODO" src               # Which TODOs are in src/?
rg -n "DATABASE_URL"        # Include line numbers explicitly
```

You need it because reading one likely file at a time is slow when you are
working in an unfamiliar project. Use ordinary `grep` when a tutorial gives
you an exact `grep` command; there is no need to translate it.

### `fd`: find files by name

Use `fd` when you know the file name, extension, or directory name.

```bash
fd package.json              # Find files named package.json
fd -e ts                     # Find TypeScript files
fd '^test'                   # Find names starting with test
```

The distinction is simple: **`fd` finds file names; `rg` finds file contents.**

### `fzf`: choose from a long list

`fzf` is an interactive filter. In this setup, `Ctrl-T` opens a file picker
while you are typing a command, so you can select a path instead of typing it.

```bash
bat <Ctrl-T>                 # Pick a file to read
git checkout <Ctrl-T>        # Usually not useful: Ctrl-T chooses files, not branches
fd -e md | fzf | xargs bat   # Pick one Markdown file from a list
```

You need it when typing or scanning a long path is annoying. You do not need
to build elaborate pipelines around it yet; `Ctrl-T` is enough to start.

### zoxide (`z`): return to places you visit

Use normal `cd` for a new directory. After you have visited a directory a few
times, use `z` with part of its name to return to it.

```bash
cd ~/personal/dotfiles       # Visit it normally once or twice
z dotfiles                   # Return from anywhere later
z personal                   # Pick the best matching familiar directory
```

It saves typing without replacing how directories work. If it picks the wrong
place, use a more specific phrase or ordinary `cd`.

### `bat`: read a file comfortably

`bat` is a viewer with syntax colouring and line numbers. It does not replace
`cat`; use `cat` in scripts and simple pipelines as usual.

```bash
bat README.md
bat -r 20:60 zsh/.config/zsh/60-tools.zsh
```

### Git, delta, and lazygit

Git records changes. `git diff` answers “what have I changed but not committed?”
Delta makes that output easier to read. LazyGit is optional visual navigation
for the same Git operations.

```bash
git status                   # What changed?
git diff                     # What are those changes exactly?
git add path/to/file         # Stage one change
git commit -m "Describe it" # Record it
lg                           # Open the visual Git interface when helpful
```

Start with `git status` and `git diff`. Open `lg` only when you want to stage
individual hunks, browse history, or resolve a merge visually.

### mise, `uv`, and direnv: project setup, not daily commands

Mise provides the runtime version a project asks for; it replaces separately
installed version managers such as `nvm` and `pyenv`. `uv` creates Python
environments and installs Python project dependencies. Direnv loads environment
variables only after you approve a project’s `.envrc` file.

```bash
mise install                 # Install versions declared by this project
mise current                 # See the versions active here
uv init                      # Start a new Python project
uv add requests               # Add a project dependency
uv run pytest                 # Run a command in the project environment
direnv allow                 # Approve a reviewed .envrc once
```

You only need these when a project contains a mise file or `.envrc`. Never run
`direnv allow` before reading the `.envrc`, because it can run shell commands.

### Starship, Stow, and `jq`

Starship is the prompt; you do not operate it. Stow links this repository’s
files into your home directory; use `make stow` only after editing a config.
`jq` formats and queries JSON and is installed because it is a small, common
helper, not because you need to learn it immediately.

## A daily loop

1. `z project-name` to move to a familiar project. Use ordinary `cd` for a new one.
2. `rg "some text"` to search content; `fd name` to search file names.
3. Press `Ctrl-T` when a command needs a file path.
4. Run `git diff`, then `lg` if you want a visual Git interface.

## Tools deliberately left out of the default install

Install these only after you can name the problem they solve:

| Tool | Install when |
|---|---|
| `tmux` | You need persistent remote sessions or terminal panes beyond your terminal app. |
| `yazi` | You routinely manage files from the terminal and prefer a full-screen file manager. |
| `atuin` | Built-in shell history and `Ctrl-R` no longer find commands well enough. |
| `k9s`, `lazydocker` | You operate Kubernetes or Docker frequently. |
| `dust`, `duf`, `procs`, `bottom` | The standard `du`, `df`, `ps`, or Activity Monitor no longer answer the question quickly. |

For an optional tool, install it with Homebrew, try it for two weeks, and add it
to `Brewfile` only if it becomes a habit.
