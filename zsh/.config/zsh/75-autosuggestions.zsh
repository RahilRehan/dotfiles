# Fish-style inline suggestions from history. Must load BEFORE
# 80-highlighting.zsh — zsh-syntax-highlighting has to be the last plugin
# sourced, after every other zle widget is defined.
if command -v brew &>/dev/null; then
    zsh_autosuggestions="$(brew --prefix zsh-autosuggestions 2>/dev/null)/share/zsh-autosuggestions/zsh-autosuggestions.zsh"
    [[ -r "$zsh_autosuggestions" ]] && source "$zsh_autosuggestions"
    unset zsh_autosuggestions
fi
