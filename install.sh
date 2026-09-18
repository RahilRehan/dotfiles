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
    # Only back up paths managed by the small default package set. This lets
    # Stow create links without overwriting an existing personal setup.
    local files=(
        ".zshrc"
        ".gitconfig"
        ".config/zsh"
        ".config/starship.toml"
        ".config/bat"
        ".config/git/ignore"
    )

    for f in "${files[@]}"; do
        if [ -e "$HOME/$f" ] && [ ! -L "$HOME/$f" ]; then
            mkdir -p "$backup_dir/$(dirname "$f")"
            mv "$HOME/$f" "$backup_dir/$f"
            success "Backed up ~/$f"
        fi
    done
}

stow_packages() {
	local packages=(zsh starship git bat mise micro)
	cd "$DOTFILES_DIR"
	for package in "${packages[@]}"; do
		stow --restow --target="$HOME" "$package"
		success "Stowed $package"
	done
}

link_hermes() {
	if [[ -e "$HOME/.hermes" && ! -L "$HOME/.hermes" ]]; then
		warn "Refusing to replace existing real $HOME/.hermes"
		return
	fi
	ln -sfn "$DOTFILES_DIR/hermes/.hermes" "$HOME/.hermes"
	success "Linked native Hermes home"
}

install_hermes() {
	if command -v hermes &>/dev/null; then
		success "Hermes Agent already installed"
		return
	fi
	info "Installing Hermes Agent with the official installer..."
	curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
	success "Hermes Agent installed"
}

install_micro_plugin() {
    if command -v micro &>/dev/null && [ ! -d "$HOME/.config/micro/plug/preview" ]; then
        micro -plugin install preview
        success "Installed Micro preview plugin"
    fi
}

install_ai_config() {
    if command -v jq &>/dev/null; then
        bash "$DOTFILES_DIR/ai/bin/ai-sync"
        success "Linked AI harness configuration"
    else
        warn "jq is unavailable — skipping AI harness configuration"
    fi
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

main() {
    if [[ "$(uname -s)" != "Darwin" ]]; then
        echo "This dotfiles repo supports macOS only." >&2
        exit 1
    fi

    info "macOS ($(uname -m))"

    install_packages
    mkdir -p "$HOME/.config" "$HOME/.local/bin" "$HOME/.local/state/zsh"
    backup_existing
    stow_packages
    link_hermes
    install_hermes
    install_micro_plugin
    install_ai_config
    setup_shell
    setup_git_user

    echo ""
    success "Done! Run: exec zsh"
}

main "$@"
