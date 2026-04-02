# Thin loader — sources numbered config files from ~/.config/zsh/
# Profile startup: ZSH_PROFILE=1 exec zsh, then check output.
[[ -n "$ZSH_PROFILE" ]] && zmodload zsh/zprof

ZSH_CONFIG="${XDG_CONFIG_HOME:-$HOME/.config}/zsh"

# (N) = nullglob — if no files match, don't error
for conf in "$ZSH_CONFIG"/[0-9]*.zsh(N); do
    source "$conf"
done

# Machine-specific overrides (API keys, work stuff). Gitignored.
[ -f "$ZSH_CONFIG/local.zsh" ] && source "$ZSH_CONFIG/local.zsh"

[[ -n "$ZSH_PROFILE" ]] && zprof
