#!/usr/bin/env bash
set -euo pipefail

DOTFILES_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ "$(uname -s)" != Darwin ]]; then
    echo "This bootstrap currently supports macOS." >&2
    exit 1
fi

if ! command -v brew >/dev/null; then
    echo "Install Homebrew from https://brew.sh, then rerun this script." >&2
    exit 1
fi

# Install missing packages without upgrading tools in active sessions.
brew bundle install --no-upgrade --file="$DOTFILES_DIR/Brewfile"
eval "$(brew shellenv)"

# Remember this checkout so future 'chezmoi apply' needs no extra flags.
chezmoi init --source="$DOTFILES_DIR"
chezmoi apply
# Never inherit the runtime requirements of the caller's current project.
(
    cd "$HOME"
    mise install
    mise reshim
)

bash "$DOTFILES_DIR/skills/install.sh"

echo "Setup complete. Open a new terminal."
echo "Run 'bash check.sh' to verify; set Git identities as described in README.md."
