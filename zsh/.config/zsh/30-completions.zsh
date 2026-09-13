# Use zsh's built-in completion system. No plugin manager is required.
autoload -Uz compinit
compinit -d "${XDG_CACHE_HOME:-$HOME/.cache}/zsh/zcompdump"

# Case-insensitive matching: "doc<tab>" matches "Documents"
zstyle ':completion:*' matcher-list 'm:{a-zA-Z}={A-Za-z}' 'r:|=*' 'l:|=* r:|=*'

# Arrow-key menu selection instead of cycling through options
zstyle ':completion:*' menu select

# Color completions using LS_COLORS (files get file colors, dirs get dir colors)
zstyle ':completion:*' list-colors "${(s.:.)LS_COLORS}"

# Show . and .. in completions
zstyle ':completion:*' special-dirs true

# Collapse repeated slashes: cd path///to → cd path/to
zstyle ':completion:*' squeeze-slashes true

# Group completions by type with a yellow header
zstyle ':completion:*:descriptions' format '%F{yellow}-- %d --%f'

# Show "no matches" in red instead of silent failure
zstyle ':completion:*:warnings' format '%F{red}-- no matches --%f'

# Group completions (files separate from directories, etc.)
zstyle ':completion:*' group-name ''

# Cache completions for faster repeated use
zstyle ':completion:*' use-cache on
zstyle ':completion:*' cache-path "${XDG_CACHE_HOME:-$HOME/.cache}/zsh/zcompcache"
mkdir -p "${XDG_CACHE_HOME:-$HOME/.cache}/zsh/zcompcache" 2>/dev/null
