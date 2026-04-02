# --- History ---
HISTSIZE=100000                     # lines kept in memory per session
SAVEHIST=100000                     # lines persisted to disk
HISTFILE="${XDG_STATE_HOME:-$HOME/.local/state}/zsh/history"
mkdir -p "$(dirname "$HISTFILE")" 2>/dev/null

setopt EXTENDED_HISTORY             # save timestamp + duration with each entry
setopt HIST_EXPIRE_DUPS_FIRST      # when trimming, remove dupes before unique entries
setopt HIST_FIND_NO_DUPS           # ctrl-r skips duplicates
setopt HIST_IGNORE_ALL_DUPS        # if you run the same command, older entry is removed
setopt HIST_IGNORE_SPACE           # prefix with space = not saved (stealth mode for secrets)
setopt HIST_REDUCE_BLANKS          # strip extra whitespace before saving
setopt SHARE_HISTORY               # all terminals share one history in real time (implies INC_APPEND_HISTORY)

# --- Directory navigation ---
setopt AUTO_CD                     # type a directory name to cd into it: "/tmp" instead of "cd /tmp"
setopt AUTO_PUSHD                  # every cd pushes old dir onto a stack (popd to go back, dirs -v to see stack)
setopt PUSHD_IGNORE_DUPS           # don't push duplicate dirs onto the stack
setopt PUSHD_SILENT                # don't print the stack after every pushd/popd

# --- General ---
setopt CORRECT                     # suggest corrections for typos: "gti" → "did you mean git?"
setopt INTERACTIVE_COMMENTS        # allow # comments in interactive shell (useful for pasting scripts)
setopt NO_BEEP                     # no terminal bell
setopt COMPLETE_IN_WORD            # tab-complete even when cursor is mid-word
setopt ALWAYS_TO_END               # after completion, move cursor to end of word
setopt GLOB_DOTS                   # include hidden files (dotfiles) in glob patterns: * matches .env, .git, etc.
setopt HIST_VERIFY                 # don't execute history expansion immediately — load into edit buffer first
setopt PIPE_FAIL                   # pipeline exit status = rightmost failed command, not last command
