# macOS-specific aliases (Homebrew init moved to 00-env.zsh for correct load order)
alias flush-dns="sudo dscacheutil -flushcache; sudo killall -HUP mDNSResponder"
alias cleanup="find . -type f -name '*.DS_Store' -ls -delete"
alias ports="lsof -i -P -n | grep LISTEN"
