# Hermes Agent

This is the Hermes dotfiles package. It mirrors the native Hermes home at
`~/.hermes` while keeping runtime data in this repository directory and out of
Git. The complete directory is linked atomically because Hermes writes state
across several sibling directories.

Tracked files are the editable configuration and personal-agent sources:

- `.hermes/config.yaml`
- `.hermes/SOUL.md`
- `.hermes/cron/jobs.json`
- `.hermes/news/`
- `.hermes/skills/`
- `.hermes/docs/`

Credentials, OAuth state, sessions, memories, databases, logs, caches, and
other runtime files are intentionally ignored by `.hermes/.gitignore`.

Install the native runtime using the official Hermes installer, then run
`make hermes` from the dotfiles repository to link this package into `~/.hermes`.
