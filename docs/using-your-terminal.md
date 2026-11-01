# Terminal toolkit

| Tool | Purpose | Example |
|---|---|---|
| `rg` | Search file contents | `rg -n 'createUser' src` |
| `fd` | Find file names | `fd -e ts` |
| `fzf` | Filter a list or pick a file | `Ctrl-T` for files, `Ctrl-R` for history |
| zoxide | Return to a visited directory | `z dotfiles` |
| `bat` | Read files with line numbers | `bat --paging=never README.md` |
| Git + delta | Review and record changes | `git diff`, `git add -p` |
| mise | Select a project's runtime | `mise install`, `mise current` |
| `uv` | Run Python tools and projects | `uv run pytest` |
| direnv | Load a project's environment | Read `.envrc`, then `direnv allow` |
| Micro | Edit a file in the terminal | `micro README.md` |

Standard commands such as `cat`, `ls`, and `rm` retain their normal meanings.
Starship renders the prompt automatically; shell suggestions and highlighting
load from Homebrew. Machine-specific settings belong in
`~/.config/zsh/local.zsh`.

Use `chezmoi edit ~/.zshrc`, `chezmoi diff`, and `chezmoi apply` to change the
shell setup. The source files live under `home/` in this repository.

For unattended commands, avoid interactive pickers: use `fd` directly or
`fzf --filter=pattern`, `zoxide query name`, and `bat --paging=never`.
Review `.envrc` before authorizing it: direnv files execute shell commands.
Harness-specific skills and MCP connections are outside this dotfiles setup.
