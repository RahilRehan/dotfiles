# Shell integrations for the core tools. Each remains optional, so a shell
# still opens if a tool is missing.

# --- zoxide (smart cd) ---
# Learns your most-visited directories. "z proj" jumps to ~/code/my-project.
# Use "z" instead of "cd". "zi" opens an interactive picker.
if command -v zoxide &>/dev/null; then
    eval "$(zoxide init zsh)"
fi

# --- fzf (fuzzy finder) ---
# ctrl-t = find file, alt-c = find directory, ctrl-r = history
# Uses fd as backend (fast, respects .gitignore) and bat for previews.
if command -v fzf &>/dev/null; then
    if fzf --zsh &>/dev/null; then
        source <(fzf --zsh)
    elif [[ -f /usr/share/doc/fzf/examples/key-bindings.zsh ]]; then
        source /usr/share/doc/fzf/examples/key-bindings.zsh
        source /usr/share/doc/fzf/examples/completion.zsh
    elif [[ -f "${XDG_DATA_HOME:-$HOME/.local/share}/fzf/shell/key-bindings.zsh" ]]; then
        source "${XDG_DATA_HOME:-$HOME/.local/share}/fzf/shell/key-bindings.zsh"
        source "${XDG_DATA_HOME:-$HOME/.local/share}/fzf/shell/completion.zsh"
    elif [[ -f /usr/share/fzf/key-bindings.zsh ]]; then
        source /usr/share/fzf/key-bindings.zsh
        source /usr/share/fzf/completion.zsh
    fi

    # Keep Tab as normal zsh completion. fzf remains available through
    # Ctrl-T, Alt-C, and Ctrl-R without replacing the standard completion menu.
    bindkey '^I' expand-or-complete

    # Use fd instead of find (faster, respects .gitignore)
    if command -v fd &>/dev/null; then
        export FZF_DEFAULT_COMMAND="fd --type f --hidden --follow --exclude .git"
        export FZF_CTRL_T_COMMAND="$FZF_DEFAULT_COMMAND"
        export FZF_ALT_C_COMMAND="fd --type d --hidden --follow --exclude .git"
    fi

    # Preview files with bat. Ctrl-/ toggles the preview.
    export FZF_DEFAULT_OPTS="
        --height=60%
        --layout=reverse
        --border=rounded
        --info=inline-right
        --bind='ctrl-/:toggle-preview'
        --color=bg+:#363a4f,bg:#24273a,spinner:#f4dbd6,hl:#ed8796
        --color=fg:#cad3f5,header:#ed8796,info:#c6a0f6,pointer:#f4dbd6
        --color=marker:#b7bdf8,fg+:#cad3f5,prompt:#c6a0f6,hl+:#ed8796
        --color=selected-bg:#494d64
    "
    export FZF_CTRL_T_OPTS="--preview 'bat --color=always --line-range :300 {} 2>/dev/null || cat {}'"
    export FZF_ALT_C_OPTS="--preview 'ls -la {}'"
fi

# --- mise (polyglot runtime manager) ---
# Replaces nvm, pyenv, rbenv, etc. Reads .mise.toml per project to activate
# the right Node, Python, Go, etc. versions automatically on cd.
if command -v mise &>/dev/null; then
    eval "$(mise activate zsh)"
fi

# --- direnv (per-directory env vars) ---
# Reads .envrc files to auto-load env vars (DATABASE_URL, AWS_PROFILE, etc.)
# when you cd into a project, and unloads them when you leave.
if command -v direnv &>/dev/null; then
    eval "$(direnv hook zsh)"
fi

# --- Starship prompt (must be last — it wraps the prompt) ---
# Replaces Powerlevel10k. Cross-shell (zsh/bash/fish), Rust-based.
# Config lives in ~/.config/starship.toml
if command -v starship &>/dev/null; then
    eval "$(starship init zsh)"
fi
