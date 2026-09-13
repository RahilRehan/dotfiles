# --- Navigation ---
alias ..="cd .."
alias ...="cd ../.."
alias ....="cd ../../.."

# Keep standard commands standard. Use `bat`, `rg`, and `fd` explicitly while
# learning them; that makes their behaviour easier to remember.
alias ll="ls -lAFh"
alias la="ls -A"

# Git shortcut
command -v lazygit &>/dev/null    && alias lg="lazygit"

# --- Shortcuts ---
alias c="clear"
alias reload="exec zsh"
alias path='print -l ${(s/:/)PATH}'
