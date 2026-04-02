# Lesson 09 — System & Containers

> **Host only — nothing in this lesson works inside the Docker playground.** Every tool here is installed via Homebrew and talks directly to macOS hardware, filesystems, or a running Docker daemon — none of which exist inside the container. Read along to learn what each tool does, then install them on your host:
>
> ```bash
> brew bundle --file=~/dotfiles/Brewfile
> ```

Unix ships utilities like `du`, `df`, and `ps` that haven't changed their output format in decades. A new generation of tools rewrites them with color, bar charts, and interactivity — while keeping the same core purpose. Your dotfiles wire many of these as drop-in aliases so you get the better version without changing habits.

## Aliases You Already Have

Your `40-aliases.zsh` quietly upgrades three everyday commands:

```bash
alias du="dust"       # visual disk usage
alias df="duf"        # disk free overview
alias ps="procs"      # process viewer
```

Type `du` on your host and you're running `dust`. Type `ps` and you're running `procs`. Same muscle memory, dramatically better output. Two TUI launchers are also defined:

```bash
alias lzd="lazydocker"   # Docker TUI
alias lg="lazygit"       # Git TUI (lesson 05)
```

## System Monitoring

### dust — see where disk space went

`du` prints a wall of numbers with no visual hierarchy. dust draws a horizontal bar chart so the biggest directory jumps out immediately.

```bash
dust                      # current directory
dust -d 1 ~/code          # one level deep inside ~/code
dust ~/Library/Caches     # specific path
```

**Try this:** Run `dust ~/code -d 1` and compare to `du -sh ~/code/*`. Same information — dust makes the answer obvious at a glance.

### duf — see how full your disks are

`df -h` shows cryptic device paths and no visual indicator. duf groups filesystems by type and adds colored usage bars.

```bash
duf                       # all mounted filesystems
duf --only local          # skip network and special mounts
duf --json | jq '.[0]'   # machine-readable output
```

**Try this:** Run `duf` and look at the USE% column for your main disk. If it's above 80 %, run `dust / -d 2` to find out what's eating space.

### btm — real-time system dashboard

`top` is hard to read and impossible to navigate. btm (bottom) puts CPU, memory, network, disk I/O, and processes into one interactive dashboard with graphs.

```bash
btm                       # launch the dashboard
btm --basic               # simplified layout, more space
btm --battery             # add battery widget (laptops)
```

Inside btm: `Tab`/`Shift-Tab` switch widgets, `/` filters processes, `dd` kills the selected process, `q` quits.

**Try this:** Run `btm`, then in another terminal run `yes > /dev/null &` to peg one CPU core. Watch the CPU graph spike, find the `yes` process, hit `dd` to kill it, then `q` to quit.

### procs — readable process list

`ps aux` dumps dense columns of text. procs adds color-coding by CPU/memory usage and a tree view showing parent-child relationships.

```bash
ps                        # all processes (alias runs procs)
procs node                # filter to processes matching "node"
procs --tree              # parent-child tree view
```

**Try this:** Run `procs --tree` and find your terminal's process chain. You'll see something like `zsh → procs` — it makes relationships obvious in a way `ps aux | grep` never does.

## Container TUIs

### lazydocker (alias: `lzd`)

lazydocker is a terminal UI for Docker — containers, images, volumes, and logs in one interactive dashboard. It replaces the cycle of `docker ps`, `docker logs`, `docker stop`, `docker rm`.

```bash
lzd                       # launch (alias defined in 40-aliases.zsh)
```

| Key | Action |
|-----|--------|
| `[` / `]` | Switch panels (containers, images, volumes) |
| `Enter` | View logs or details |
| `d` | Remove selected item |
| `s` / `r` | Stop / restart container |
| `x` | Context menu for current item |

**Try this:** On your host, start a throwaway container (`docker run -d --name dottest alpine sleep 3600`), then run `lzd`. Navigate to it, press `Enter` for logs, then `d` to remove it — all without typing a single `docker` command.

### k9s — Kubernetes TUI

k9s does for Kubernetes what lazydocker does for Docker. If you work with clusters, it replaces repetitive `kubectl` commands with a navigable dashboard.

```bash
k9s                       # connect to current kubectl context
k9s --context staging     # specific context
k9s -n my-namespace       # jump to a namespace
```

| Key | Action |
|-----|--------|
| `:` | Command mode — type a resource: `pods`, `deploy`, `svc` |
| `/` | Filter the current view |
| `l` | View logs |
| `s` | Shell into a pod |
| `ctrl-d` | Delete resource |

## Utilities

### tldr — the man page cheat sheet

Man pages are comprehensive but overwhelming — `man tar` is 20+ pages. tldr gives you the three commands you actually need.

```bash
tldr tar                  # essentials for tar
tldr curl                 # essentials for curl
tldr --update             # refresh the local cache
```

**Try this:** Run `tldr fd` and compare it to `man fd`. The tldr page gives you practical examples you can copy-paste immediately.

### sd — find-and-replace without the backslash soup

sd replaces `sed` for text substitution. It uses modern regex syntax so you don't have to escape everything.

```bash
sd "oldFunc" "newFunc" src/api.ts             # in-place replacement
echo "2024-01-15" | sd "(\d{4})-(\d{2})-(\d{2})" '$3/$2/$1'
# Output: 15/01/2024

fd -e ts --exec sd "oldFunc" "newFunc"        # project-wide replace
```

**Try this:** Create a temp file with `echo "Hello World" > /tmp/test.txt`, then run `sd "World" "Terminal" /tmp/test.txt` and cat the file to confirm. Compare that to the `sed -i '' 's/World/Terminal/' /tmp/test.txt` you'd otherwise write.

### glow — render Markdown in the terminal

Renders markdown with colors, headings, and code blocks — useful for reading READMEs without leaving the terminal.

```bash
glow README.md            # render a file
glow -p README.md         # scrollable pager mode
glow .                    # browse all markdown in a directory
```

**Try this:** Run `glow -p ~/dotfiles/README.md` to read the dotfiles docs with full formatting rendered inline.

### hyperfine — benchmark any command

Takes the guesswork out of "which is faster?" by running multiple iterations, computing statistics, and handling warmup runs.

```bash
hyperfine "fd -e py"                                  # benchmark one command
hyperfine "find . -name '*.py'" "fd -e py" --warmup 3 # compare two
hyperfine "rg pattern" "grep -r pattern" --export-markdown bench.md
```

**Try this:** Run `hyperfine "find . -type f -name '*.zsh'" "fd -e zsh" --warmup 3` in your dotfiles directory. The summary line shows exactly how many times faster `fd` is — typically 5–50x.

### just — a modern command runner

`just` is a simpler alternative to `make` for running project tasks. No tabs-vs-spaces landmines, better argument handling, and a built-in `--list` to show available recipes.

```bash
just                      # list available recipes (default)
just dev                  # run a recipe
just deploy production    # pass arguments
```

A minimal `justfile`:

```just
default:
    @just --list

dev:
    npm run dev

test *args:
    npm run test {{args}}

deploy env="staging":
    ./scripts/deploy.sh {{env}}
```

**Try this:** Create a `justfile` in a project you work on daily. Replace whatever npm/make/bash scripts you currently use. After a week, run `just` with no arguments — the self-documenting list is the killer feature.

## Next

[Lesson 10 — Putting It Together →](10-putting-it-together.md)
