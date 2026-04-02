# zinit — fast, flexible zsh plugin manager (replaces Oh My Zsh)
# https://github.com/zdharma-continuum/zinit
#
# Why zinit over OMZ:
#   - Turbo mode: plugins load AFTER prompt appears (async), not before
#   - Cherry-pick: grab individual OMZ plugins without the framework
#   - Shell startup: ~50ms vs ~500ms with OMZ

ZINIT_HOME="${XDG_DATA_HOME:-$HOME/.local/share}/zinit/zinit.git"

# Auto-install zinit on first run
if [ ! -d "$ZINIT_HOME" ]; then
    print -P "%F{blue}:: Installing zinit...%f"
    command mkdir -p "$(dirname "$ZINIT_HOME")"
    command git clone https://github.com/zdharma-continuum/zinit.git "$ZINIT_HOME" 2>/dev/null
fi

if [ ! -f "${ZINIT_HOME}/zinit.zsh" ]; then
    print -P "%F{red}:: zinit not installed and clone failed. Skipping plugins.%f"
    return
fi

source "${ZINIT_HOME}/zinit.zsh"

# --- Core plugins (turbo mode — load async after prompt) ---

# wait"0" = load immediately after prompt renders (lowest delay)
# lucid   = suppress "Loaded X" messages

# Syntax highlighting — colors commands as you type
# green = valid command, red = typo/not found
zinit wait lucid for \
    zdharma-continuum/fast-syntax-highlighting

# Autosuggestions — ghost text from history as you type (accept with →)
zinit wait lucid atload"_zsh_autosuggest_start" for \
    zsh-users/zsh-autosuggestions

# Extra completions — community-maintained completions for 200+ tools
zinit wait lucid blockf atpull"zinit creinstall -q ." for \
    zsh-users/zsh-completions

# History substring search — type partial command, then ↑/↓ to filter history
# Example: type "git" then press ↑ → cycles through only commands starting with "git"
zinit wait lucid atload"
    bindkey '^[[A' history-substring-search-up
    bindkey '^[[B' history-substring-search-down
" for zsh-users/zsh-history-substring-search

# --- Cherry-picked OMZ plugins (just the useful snippets, not the framework) ---

# git: adds 100+ git aliases (ga, gc, gco, gd, gp, gl, etc.)
zinit snippet OMZP::git

# sudo: press ESC ESC to prepend "sudo" to current or last command
zinit snippet OMZP::sudo

# --- Completion system ---
# Must run after all plugins are loaded. zicompinit calls compinit,
# zicdreplay replays any completions deferred by blockf.
zinit wait lucid atinit"zicompinit; zicdreplay" for zdharma-continuum/null
