# macOS-specific aliases (Homebrew init in 00-env.zsh)
alias flush-dns="sudo dscacheutil -flushcache; sudo killall -HUP mDNSResponder"
alias cleanup="find . -type f -name '*.DS_Store' -ls -delete"
alias ports="lsof -i -P -n | grep LISTEN"
