---
alwaysApply: true
---

# Personal defaults

Use these defaults across projects, alongside each repository's instructions.

## Terminal

- Search contents with `rg -n -- 'pattern' path`. Find files with `fd` or
  `rg --files`. Start in the active repository; scope hidden-file searches.
- Read bounded excerpts with
  `bat --paging=never --color=never --line-range 20:80 -- file`.
  Adjust the range to the task.
- Use `fzf --filter='query'` for unattended filtering. Exit 1 means no matches;
  inspect ambiguous results before choosing a file to modify.
- Locate known projects with `zoxide query -- project-name`; verify the path
  and set the working directory explicitly for each command.
- Quote paths, use `--` for file operands, and use NUL-delimited filename
  pipelines when passing paths between tools.
- Inspect `.envrc` and the scripts it loads before authorizing direnv. Use
  `direnv exec /absolute/project command` for a trusted environment, setting
  the working directory separately. Do not print secrets or entire environments.
- Use mise's Node runtime and respect project mise configuration. Manage shared
  tools through the dotfiles Brewfile and configuration through chezmoi.

These inline defaults cover routine terminal work. The `terminal-toolkit`
skill contains detailed examples and edge cases for tasks that need them.
