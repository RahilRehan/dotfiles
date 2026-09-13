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

# Installers sometimes append duplicate or now-unused PATH entries. Keep it
# tidy after loading machine-specific additions.
typeset -U path
path=(${path:#$HOME/.local/share/zinit/polaris/bin})
path=(${path:#$HOME/.codex/packages/standalone/*})
path=(${path:#$HOME/.codex/tmp/*})
path=(${path:#$HOME/.local/share/cursor-agent/*})

[[ -n "$ZSH_PROFILE" ]] && zprof
export ENABLE_PROMPT_CACHING_1H=1
