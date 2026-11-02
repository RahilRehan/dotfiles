# Personal T3 Code setup

T3 Code is the default surface for Codex, Claude Code, and Cursor.
Record choices here as the setup review progresses. Device preferences must be
checked on each client. Chezmoi merges the selected server defaults into
`~/.t3/userdata/settings.json`; the device preferences below are a setup checklist.
Accounts, provider paths, secrets, and project overrides remain local.

## Confirmed choices

Verified in the Mac desktop app during the 2026-11-01/02 setup review:

- Appearance: retain the existing Iris theme in dark mode and its customization.
- Chat → Follow-up behavior: **Steer**.
- Chat → Send shortcut: **Enter**; **Shift+Enter** inserts a new line.
- Typography: retain **SF Pro, 16 px** for the interface and **Menlo, 13 px**
  for code and the terminal.
- Sidebar: retain the current inbox with the **Working section enabled**.
- Notifications: retain **system alerts with sound** and **in-app toasts off**.
- Appearance → Render math: **on**.
- Appearance → Word wrap: **on** for code blocks, diffs, and file previews.
- Keyboard shortcuts: retain the built-in bindings.
- Labs → Context window indicator (legacy): **on**.
- Labs → Plan mode (legacy): **on**, restoring Build/Plan and **Shift+Tab**.
- Diffs: retain **Stacked** layout, show whitespace-only edits
  (**Hide whitespace changes off**), and retain manual panel opening
  (**Proactive panels off**).
- Browser: ordinary chat and terminal links open in **T3 Code**. Retain
  **automatic floating previews** and the existing **Default** browser profile.
- Mac environment defaults, across projects unless overridden:
  - New-thread model: **Codex GPT-6.1 Sol**, **High** reasoning.
  - Fallback for new threads when Codex is out of usage:
    **Claude Code Sonnet 5.5**, **High** reasoning, **Fast mode off**.
  - New-thread permissions: retain **Full access**.
  - Auto-settle inactive threads after **7 days**.
  - **Keep threads with a PR** enabled; merge/close settlement still applies.
  - **Resume after usage limits** enabled at the reported reset time.
  - New coding threads start in a **New worktree**.
  - **Automatically pull** enabled for eligible clean default-branch checkouts.
  - Default pull request merge method: **Squash and merge**.
  - Source control writing style: **Conventional Commits**. Existing repository
    change-request templates remain enabled.
  - Background activity: **Performance**.
  - **Continue threads after restarts** remains enabled.
  - Browser artifact retention: **30 days**.
  - Rotated log retention: **14 days**; current logs are retained.

Wrapping, math rendering, settlement, and usage-limit resumption were updated
and verified. Other confirmed preferences already matched the requested values.

## Worktree cleanup

On the Mac environment, **Delete merged worktrees** is enabled with
**Keep worktrees with local changes → Any local files**. This protects edits,
untracked files, and ignored local files such as `.env`, except `node_modules`,
which can be recreated. Inactivity, settlement, unchanged-worktree, and
thread-deletion cleanup remain disabled. Thread settlement alone leaves the
working folder in place.

Before enabling cleanup, all five existing T3 worktrees were inspected for
local changes and branch pull requests. None had a branch pull request, so none
qualified for merged-only cleanup. All five remained afterward. The desktop UI
and saved server settings confirmed the new-worktree default, merged-only
cleanup, and local-file protection.

## Retention verification

The retention controls initially enable an 8-day period. Before setting the
requested 30/14-day periods, six older files were temporarily safeguarded outside
the cleanup directories. After both periods were saved and checked, every file
was restored and its SHA-256 verified. The temporary safeguard was removed.

## Telemetry

T3 product telemetry and connection tracing are opted out with
`T3CODE_TELEMETRY_ENABLED=false`. Chezmoi manages the shell export in
`home/dot_config/zsh/env.zsh` for desktop launches and updates only this variable
in `~/.t3/service.env`, preserving other service variables. Service variables
and credentials are not copied into the repository.

The opt-out takes effect when the service and desktop app next start. Restart
activation is pending; the active setup session has not been interrupted.
After this review, restart the service with `t3 service restart`, then fully
quit and reopen the desktop app. This controls T3 reporting, independently of
provider telemetry settings.

## Reproducing server defaults

`home/dot_t3/private_userdata/modify_private_settings.json` uses jq to merge only the
agreed server defaults and keeps T3's data directory private. It preserves other settings and contains no local
account data. `chezmoi apply` reapplies this baseline; change the source here
when making a lasting change to a managed preference. Project overrides still
take precedence. Authenticate the named Codex and Claude providers separately
on another machine.

The installed T3 build exposes the fallback model but no fallback effort picker.
Its saved model selection therefore explicitly records `effort: high` and
`fastMode: false`. Actual usage-limit failover has not been forced for testing.
The merge was checked with fresh and existing settings, including preservation
of provider configuration and project overrides, invalid-input rejection, and
idempotence. Chezmoi verification and the full dotfiles checks passed.

## Harness startup verification

Fresh, read-only Claude and Cursor CLI sessions quoted the shared Personal
defaults and the exact `fzf --filter` command without making any tool calls.
Codex also received the shared file directly in the active T3 session.

The installed Cursor CLI resolves `.cursor/rules` through workspace ancestors.
The successful Cursor probe ran under `~/personal`, matching the current project
layout and T3 scratch folders under the home directory. A first probe in the
system temporary directory outside home did not inherit this rule. Projects
outside home need a project-level link to the same shared file or another
verified global-rule mechanism for that Cursor version.

## Remaining setup and verification

- Finish the reproducible settings record and review pending dotfiles changes.
- Activate and verify the telemetry opt-out after restarting T3.

## Deferred work

- Repository-specific project actions, setup scripts, and overrides.
- Other machines and remote access configuration.
- Useful scheduled workflows once the daily setup is established.

Personal agent behavior customization is tracked separately in [the backlog](backlog.md).
