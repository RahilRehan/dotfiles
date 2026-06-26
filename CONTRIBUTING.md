# Contributing

Thanks for your interest in improving these dotfiles!

## Adding a New Tool

1. Create its stow package: `toolname/.config/toolname/config`
2. Only override settings that differ from the tool's defaults
3. Add to `Brewfile`
4. Add shell integration to `zsh/.config/zsh/60-tools.zsh` if needed (guard with `command -v`)
5. Add alias to `zsh/.config/zsh/40-aliases.zsh` if helpful
6. Update `README.md` toolbox table and structure diagram

## Principles

- **Minimal overrides only** -- don't restate tool defaults, only configure what you're changing
- **macOS only** -- no Linux/Windows compatibility shims
- **Catppuccin Macchiato** -- all themed tools should use this palette for consistency
- **Install and forget** -- configs should work out of the box with no manual steps

## Submitting Changes

1. Fork the repo and create a branch
2. Test on macOS: `make install` or `make stow`
3. Verify `make lint` passes on any modified shell files
4. Open a PR with a clear description of what changed and why

## Reporting Issues

Open an issue with:
- Your macOS version and architecture (`uname -a`)
- The tool/config that's broken
- Expected vs actual behavior
