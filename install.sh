#!/usr/bin/env bash
set -euo pipefail

DOTFILES_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

info()    { echo -e "\033[0;34m::\033[0m $1"; }
success() { echo -e "\033[0;32mok\033[0m $1"; }
warn()    { echo -e "\033[1;33m!!\033[0m $1"; }

install_packages() {
    if ! command -v brew &>/dev/null; then
        info "Installing Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        eval "$(/opt/homebrew/bin/brew shellenv 2>/dev/null || /usr/local/bin/brew shellenv 2>/dev/null)"
    fi
    brew bundle --file="$DOTFILES_DIR/Brewfile"
    success "Packages installed"
}

backup_existing() {
    local backup_dir="$HOME/.dotfiles_backup/$(date +%Y%m%d_%H%M%S)"
    local files=(".zshrc" ".gitconfig" ".tmux.conf")

    for f in "${files[@]}"; do
        if [ -e "$HOME/$f" ] && [ ! -L "$HOME/$f" ]; then
            mkdir -p "$backup_dir/$(dirname "$f")"
            mv "$HOME/$f" "$backup_dir/$f"
            success "Backed up ~/$f"
        fi
    done
}

stow_packages() {
    cd "$DOTFILES_DIR"
    for dir in */; do
        dir="${dir%/}"
        [[ "$dir" == .git || "$dir" == docs || "$dir" == iterm2 || "$dir" == ai ]] && continue
        stow --restow --target="$HOME" "$dir"
        success "Stowed $dir"
    done
}

setup_shell() {
    local zsh_path
    zsh_path="$(command -v zsh)"

    if ! grep -qF "$zsh_path" /etc/shells 2>/dev/null; then
        echo "$zsh_path" | sudo tee -a /etc/shells >/dev/null
    fi

    if [[ "${SHELL:-}" != */zsh ]]; then
        sudo chsh -s "$zsh_path" "$(whoami)" 2>/dev/null || true
    fi
    success "Shell set to zsh"
}

# Prompt for git identity files if they don't exist.
# .gitconfig uses includeIf to auto-switch identity by directory:
#   ~/personal/  → ~/.gitconfig-personal
#   ~/workplace/ → ~/.gitconfig-work
#   fallback     → ~/.gitconfig.local
setup_git_user() {
    if [ ! -t 0 ]; then
        warn "Non-interactive — run install.sh interactively to set git identities"
        return
    fi

    _setup_git_identity "$HOME/.gitconfig.local"       "default (fallback)"
    _setup_git_identity "$HOME/.gitconfig-personal"    "personal (~/personal/ repos)"
    _setup_git_identity "$HOME/.gitconfig-work"        "work (~/workplace/ repos)"
}

_setup_git_identity() {
    local file="$1" label="$2"

    if [ -f "$file" ]; then
        success "Git $label identity exists ($file)"
        return
    fi

    info "Setting up git $label identity (stored in $file, not in the repo)"
    read -rp "  Name: " git_name
    read -rp "  Email: " git_email

    git config --file "$file" user.name "$git_name"
    git config --file "$file" user.email "$git_email"
    success "Git $label identity saved to $file"
}

setup_iterm2() {
    local target_dir="$HOME/Library/Application Support/iTerm2/DynamicProfiles"
    local target="$target_dir/dotfiles.json"
    if [ -L "$target" ] || [ -f "$target" ]; then
        success "iTerm2 profile already linked"
        return
    fi
    mkdir -p "$target_dir"
    ln -s "$DOTFILES_DIR/iterm2/profile.json" "$target"
    success "iTerm2 profile linked"
    warn "Open iTerm2 → Settings → Profiles → Keys → Presets → Natural Text Editing"
}

setup_ai() {
    bash "$DOTFILES_DIR/ai/bin/ai-sync"

    local rel
    for rel in .cursor/mcp.json .claude/mcp.json .pi/agent/mcp.json; do
        if [[ -f "$HOME/$rel" && ! -L "$HOME/$rel" ]]; then
            rm "$HOME/$rel"
            success "Replaced ~/$rel with stowed config"
        fi
    done

    cd "$DOTFILES_DIR" && stow --restow --target="$HOME" ai
    success "AI MCP synced"
}

main() {
    if [[ "$(uname -s)" != "Darwin" ]]; then
        echo "This dotfiles repo supports macOS only." >&2
        exit 1
    fi

    info "macOS ($(uname -m))"

    install_packages
    mkdir -p "$HOME/.config" "$HOME/.local/bin" "$HOME/.local/state/zsh"
    backup_existing
    setup_ai
    stow_packages
    setup_shell
    setup_git_user
    setup_iterm2

    echo ""
    success "Done! Run: exec zsh"
}

main "$@"
