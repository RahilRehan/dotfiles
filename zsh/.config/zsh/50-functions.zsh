mkcd() {
    [ -z "$1" ] && { echo "Usage: mkcd <directory>" >&2; return 1; }
    mkdir -p "$1" && cd "$1"
}

extract() {
    if [ ! -f "$1" ]; then
        echo "'$1' is not a valid file" >&2
        return 1
    fi
    case "$1" in
        *.tar.bz2|*.tbz2)  tar xjf "$1" ;;
        *.tar.gz|*.tgz)    tar xzf "$1" ;;
        *.tar.xz)          tar xJf "$1" ;;
        *.tar.zst)         tar --zstd -xf "$1" ;;
        *.tar)             tar xf "$1"  ;;
        *.bz2)             bunzip2 "$1" ;;
        *.gz)              gunzip "$1"  ;;
        *.zip)             unzip "$1"   ;;
        *.Z)               uncompress "$1" ;;
        *.7z)              7z x "$1"    ;;
        *.rar)             unrar x "$1" ;;
        *.xz)              unxz "$1"    ;;
        *.zst)             unzstd "$1"  ;;
        *)                 echo "'$1' cannot be extracted" >&2; return 1 ;;
    esac
}

# Usage: killport 3000
killport() {
    local pid
    pid=$(lsof -ti :"$1" 2>/dev/null)
    if [ -n "$pid" ]; then
        kill "$pid" && echo "Sent SIGTERM to $pid on port $1"
        sleep 1
        kill -0 "$pid" 2>/dev/null && kill -9 "$pid" && echo "Sent SIGKILL to $pid"
    else
        echo "No process on port $1"
    fi
}

# Usage: serve 3000
serve() {
    local port="${1:-8000}"
    echo "Serving on http://localhost:$port"
    python3 -m http.server "$port"
}
