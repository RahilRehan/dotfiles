# --- Navigation ---
alias ..="cd .."
alias ...="cd ../.."
alias ....="cd ../../.."

# --- Listing ---
# If eza is installed, use it (icons, git status, tree view). Otherwise fall back to ls.
if command -v eza &>/dev/null; then
    alias ls="eza --icons --group-directories-first"
    alias ll="eza -la --icons --group-directories-first --git"
    alias la="eza -a --icons --group-directories-first"
    alias lt="eza --tree --level=3 --icons"    # tree view, 3 levels deep
else
    alias ll="ls -lAFh"
    alias la="ls -A"
fi

# --- cat ---
# If bat is installed, use it for cat (syntax highlighting, line numbers).
if command -v bat &>/dev/null; then
    alias cat="bat --paging=never"             # no pager, just print like cat
    alias catp="bat --plain"                   # no line numbers, no header (raw output)
fi

# --- Safety nets — prompt before overwriting ---
alias rm="rm -i"
alias cp="cp -i"
alias mv="mv -i"

# --- TUI shortcuts ---
command -v lazygit &>/dev/null    && alias lg="lazygit"
command -v lazydocker &>/dev/null && alias lzd="lazydocker"

# --- Modern replacements ---
# dust = du, duf = df, btm = top, procs = ps
command -v dust &>/dev/null && alias du="dust"
command -v duf &>/dev/null  && alias df="duf"
command -v procs &>/dev/null && alias ps="procs"

# --- Shortcuts ---
alias c="clear"
alias reload="exec zsh"
alias dotfiles='cd "${DOTFILES_DIR:-$HOME/dotfiles}"'
alias path='print -l ${(s/:/)PATH}'
alias myip="curl -s ifconfig.me"
