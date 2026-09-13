# XDG Base Directories — keeps $HOME clean.
# Tools that respect XDG put configs in ~/.config/, data in ~/.local/share/,
# cache in ~/.cache/, state (history, logs) in ~/.local/state/.
export XDG_CONFIG_HOME="${XDG_CONFIG_HOME:-$HOME/.config}"
export XDG_DATA_HOME="${XDG_DATA_HOME:-$HOME/.local/share}"
export XDG_CACHE_HOME="${XDG_CACHE_HOME:-$HOME/.cache}"
export XDG_STATE_HOME="${XDG_STATE_HOME:-$HOME/.local/state}"

# Optional AI / MCP secrets — never commit this file
[[ -f "$XDG_CONFIG_HOME/ai/secrets.env" ]] && source "$XDG_CONFIG_HOME/ai/secrets.env"

# Default editor — fallback chain for portability
if command -v cursor &>/dev/null; then
    export EDITOR="cursor --wait"
elif command -v nvim &>/dev/null; then
    export EDITOR="nvim"
else
    export EDITOR="vim"
fi
export VISUAL="$EDITOR"
export PAGER="less"
export LANG="en_US.UTF-8"
export LC_ALL="en_US.UTF-8"

# Homebrew — must be early so brew-installed tools are on PATH for 60-tools.zsh.
# Apple Silicon: /opt/homebrew, Intel: /usr/local
if [ -f /opt/homebrew/bin/brew ]; then
    eval "$(/opt/homebrew/bin/brew shellenv)"
elif [ -f /usr/local/bin/brew ]; then
    eval "$(/usr/local/bin/brew shellenv)"
fi

# typeset -U = deduplicate. Sourcing .zshrc 10 times won't add 10 duplicate entries.
typeset -U path
path=(
    $HOME/.local/bin    # user scripts, pip --user installs
    $HOME/.cargo/bin    # rust/cargo binaries
    $path
)
