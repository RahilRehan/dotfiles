# Word style: treat only whitespace as word boundaries so Option+Arrow
# jumps over paths and dotted.names as a single word (like a text editor).

autoload -U select-word-style
select-word-style bash

# Option+Left/Right for word navigation (works across terminals)
bindkey '^[[1;3D' backward-word    # Option+Left
bindkey '^[[1;3C' forward-word     # Option+Right
