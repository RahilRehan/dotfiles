# Linux-specific config (Homebrew init moved to 00-env.zsh for correct load order)

alias ports="ss -tlnp"                     # show listening ports

# Clipboard compatibility — so macOS pbcopy/pbpaste commands work on Linux
if command -v xclip &>/dev/null; then
    alias pbcopy="xclip -selection clipboard"
    alias pbpaste="xclip -selection clipboard -o"
elif command -v xsel &>/dev/null; then
    alias pbcopy="xsel --clipboard --input"
    alias pbpaste="xsel --clipboard --output"
elif command -v wl-copy &>/dev/null; then
    alias pbcopy="wl-copy"
    alias pbpaste="wl-paste"
fi

# open alias — xdg-open is the Linux equivalent of macOS open
command -v xdg-open &>/dev/null && alias open="xdg-open"
