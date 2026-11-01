---
name: terminal-toolkit
description: Find and inspect repository files, locate known projects, and run project commands using rg, fd, bat, fzf, zoxide, and direnv. Use for terminal exploration and command preparation, especially unattended agent sessions.
---

# Terminal toolkit

Choose the tool that answers the current question. These tools are available in
the dotfiles setup; using every tool is unnecessary.

| Need | Preferred command |
|---|---|
| Find text or a symbol | `rg -n -- 'pattern' path` |
| Find a file by name | `fd --fixed-strings 'name' path` or `rg --files path` |
| Read a bounded source excerpt | `bat --paging=never --color=never --line-range 20:80 -- file` |
| Narrow an existing candidate list | `fzf --filter='query'` |
| Locate a previously visited project | `zoxide query -- project-name` |
| Run with an already authorized project environment | `direnv exec /absolute/project command args` |

## Unattended operation

- Use `fzf --filter` in agent commands. An interactive picker needs a terminal
  and can hang a background task. Treat no matches (exit 1) as an empty result;
  inspect ambiguous candidates before choosing a target for a write.
- Disable bat's pager and color for captured output. Read the relevant range
  instead of sending a large file through the tool output.
- Prefer an explicit working directory for each command. `z` is an interactive
  shell function; `zoxide query` returns a candidate path, which must exist and
  match the intended project. A directory change in one tool call need not
  persist into the next. Fall back to the known project path if the database
  has no entry.

## Search boundaries and paths

Search the active repository or a named subdirectory first. `rg` and `fd`
normally respect ignore rules. If that omits a relevant dotfile, opt into a
scoped hidden-file search such as `rg --hidden -g '!.git/**' ...`; don't expand
to an entire home directory just because the first search was empty.

Quote paths and use `--` for literal file operands that could start with a
dash. When piping filenames into another command, use NUL delimiters, for
example `fd --type f -e md -0 . docs | xargs -0 bat --paging=never --color=never --`.
Do not evaluate filenames as shell code.

## Project environments

Use `direnv status` to inspect authorization. Before granting trust, read
`.envrc` and the files or scripts it loads. Run `direnv allow` only when project
setup is authorized and the commands are appropriate for the task; don't grant
trust merely to suppress a blocked-environment error. Never dump the complete
environment or print credentials while checking it.

For an approved environment, `direnv exec /absolute/project command` works
without an interactive shell hook. It supplies environment variables; it does
not establish the working directory for the requested command. Set that
directory separately when relative paths matter.

If a tool is missing, use a suitable standard command for the current task and
report the missing dependency when relevant. Change the shared setup through
the dotfiles source rather than adding ad-hoc aliases or installers to a
project.
