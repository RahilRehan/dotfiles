#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

bash -n install.sh
bash -n check.sh
bash -n skills/install.sh
sh -n home/dot_t3/modify_private_service.env
sh -n home/dot_t3/private_userdata/modify_private_settings.json
for file in home/dot_zshrc home/dot_zprofile home/dot_config/zsh/*.zsh; do
    zsh -n "$file"
done
ruby -c Brewfile
git diff --check

brew bundle check --no-upgrade --file=Brewfile
chezmoi --source="$PWD" verify

# Homebrew receipts can survive an app being deleted in Finder.
casks="$(brew bundle list --cask --file=Brewfile)"
# Cask tokens contain no spaces; intentionally split the newline-separated list.
app_paths="$(brew info --json=v2 --cask $casks | jq -r '.casks[].artifacts[] | select(.app) | .target // ("/Applications/" + .app[0])')"
while IFS= read -r app_path; do
    [[ -d "$app_path" ]] || { echo "Missing application: $app_path" >&2; exit 1; }
done <<< "$app_paths"

# Start with no inherited PATH additions, then check the global runtime.
node_path="$(env -i PATH=/usr/bin:/bin:/usr/sbin:/sbin /bin/zsh -lc 'cd "$HOME" && node -p process.execPath')"
case "$node_path" in
    "${XDG_DATA_HOME:-$HOME/.local/share}"/mise/installs/node/*/bin/node) ;;
    *) echo "Node did not resolve through mise: $node_path" >&2; exit 1 ;;
esac

for tool in jq fzf fd rg bat zoxide direnv uv mise starship micro git gh codex claude cursor-agent; do
    command -v "$tool" >/dev/null
done
bat --paging=never --color=never README.md >/dev/null

# Check only the managed service variable; never source or dump service secrets.
rg -q '^T3CODE_TELEMETRY_ENABLED=false$' "$HOME/.t3/service.env"
telemetry="$(env -i PATH=/usr/bin:/bin:/usr/sbin:/sbin /bin/zsh -lc 'print -r -- "$T3CODE_TELEMETRY_ENABLED"')"
[[ "$telemetry" == false ]] || { echo "T3 telemetry opt-out missing from shell startup" >&2; exit 1; }

# All personal harness instructions resolve to one managed file.
instructions="$HOME/.config/agents/AGENTS.md"
cmp home/dot_config/agents/AGENTS.md "$instructions"
for target in "$HOME/.codex/AGENTS.md" "$HOME/.claude/CLAUDE.md" "$HOME/.cursor/rules/defaults.mdc"; do
    [[ -L "$target" && "$(readlink "$target")" == "$instructions" ]] || {
        echo "Incorrect shared instruction link: $target" >&2; exit 1;
    }
    cmp "$instructions" "$target"
done
[[ ! -s "$HOME/.codex/AGENTS.override.md" ]] || {
    echo "AGENTS.override.md shadows the shared Codex defaults" >&2; exit 1;
}

# Codex and Cursor use the shared directory; Claude Code uses its skills.sh link.
for source in skills/*/SKILL.md; do
    [[ -f "$source" ]] || continue
    name="$(basename "$(dirname "$source")")"
    for root in "$HOME/.agents/skills" "$HOME/.claude/skills"; do
        cmp "$source" "$root/$name/SKILL.md"
    done
done
while IFS=$'\t' read -r name source selection; do
    [[ -z "$name" || "$name" == \#* ]] && continue
    for root in "$HOME/.agents/skills" "$HOME/.claude/skills"; do
        [[ -f "$root/$name/SKILL.md" ]] || { echo "Missing skill: $name in $root" >&2; exit 1; }
    done
done < skills/upstream.tsv
node tests/terminal-toolkit.mjs
echo "Checks passed: packages, app files, configuration, mise Node, tools, shared instructions, and skills for Codex/Claude/Cursor."
