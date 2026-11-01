#!/usr/bin/env bash
set -euo pipefail
SKILLS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Use the global mise runtime, regardless of the caller's project directory.
cd "$HOME"
export DISABLE_TELEMETRY=1
run_skills() { mise exec -- npx --yes skills@1.7.0 "$@" </dev/null; }

run_skills add "$SKILLS_DIR" --skill terminal-toolkit \
    --global --agent codex claude-code cursor --yes

# Keep retained third-party skills pinned, with provenance owned by skills.sh.
while IFS=$'\t' read -r name source; do
    [[ -z "$name" || "$name" == \#* ]] && continue
    run_skills add "$source" --skill "$name" \
        --global --agent codex claude-code cursor --yes
done < "$SKILLS_DIR/upstream.tsv"
