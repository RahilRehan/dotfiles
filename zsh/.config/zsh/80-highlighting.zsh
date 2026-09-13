# Syntax highlighting must load after completion and other ZLE widgets.
if command -v brew &>/dev/null; then
    zsh_highlighting="$(brew --prefix zsh-syntax-highlighting 2>/dev/null)/share/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh"
    [[ -r "$zsh_highlighting" ]] && source "$zsh_highlighting"
    unset zsh_highlighting
fi
