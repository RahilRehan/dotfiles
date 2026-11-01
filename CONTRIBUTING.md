# Maintaining this setup

- Add applications and CLI tools to `Brewfile`.
- Keep Node versions in `home/dot_config/mise/config.toml`; projects may override them.
- Keep portable configuration in `home/`, using chezmoi's file naming.
- Keep custom skills in `skills/<name>/SKILL.md` and install them with skills.sh.
- Pin upstream skills in `skills/upstream.tsv`; review changes before updating revisions.
- Add only useful overrides; leave application state, credentials, and MCP configuration local.
- Run `bash check.sh` after applying changes. The bootstrap currently targets macOS.
- Use `chezmoi diff` before applying; commit only the intended source files.
