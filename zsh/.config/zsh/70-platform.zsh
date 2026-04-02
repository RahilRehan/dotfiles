# Load OS-specific config. Same dotfiles repo, different behavior per platform.
# macOS: brew shellenv, flush-dns, cleanup aliases
# Linux: clipboard compatibility (pbcopy/pbpaste), open alias

ZSH_CONFIG="${XDG_CONFIG_HOME:-$HOME/.config}/zsh"

case "$(uname -s)" in
    Darwin) [ -f "$ZSH_CONFIG/platform/macos.zsh" ] && source "$ZSH_CONFIG/platform/macos.zsh" ;;
    Linux)  [ -f "$ZSH_CONFIG/platform/linux.zsh" ]  && source "$ZSH_CONFIG/platform/linux.zsh" ;;
esac
