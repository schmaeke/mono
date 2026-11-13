#!/bin/sh
# Build the Mono themes and install them for every supported application found on this machine.
# Options are passed to build.py, e.g. ./install.sh --hue 250
set -eu

src=$(cd "$(dirname "$0")" && pwd)
config=${XDG_CONFIG_HOME:-$HOME/.config}

out=$(mktemp -d)
trap 'rm -rf "$out"' EXIT
python3 "$src/build.py" --out "$out" "$@"

install_theme() { # name, target directory, files or directories...
    name=$1 dir=$2
    shift 2
    mkdir -p "$dir"
    cp -R "$@" "$dir"
    echo "$name: installed to $dir"
}

if command -v ghostty >/dev/null 2>&1 || [ -d /Applications/Ghostty.app ]; then
    install_theme Ghostty "$config/ghostty/themes" "$out"/ghostty/*
else
    echo "Ghostty: not found, skipped"
fi

if command -v hx >/dev/null 2>&1 || command -v helix >/dev/null 2>&1; then
    install_theme Helix "$config/helix/themes" "$out"/helix/*
else
    echo "Helix: not found, skipped"
fi

if command -v yazi >/dev/null 2>&1; then
    install_theme Yazi "${YAZI_CONFIG_HOME:-$config/yazi}/flavors" "$out"/yazi/*
else
    echo "Yazi: not found, skipped"
fi

if command -v gitui >/dev/null 2>&1; then
    # gitui reads ~/.config on macOS whatever XDG_CONFIG_HOME says.
    if [ "$(uname)" = Darwin ]; then gitui_config=$HOME/.config/gitui; else gitui_config=$config/gitui; fi
    install_theme gitui "$gitui_config" "$out"/gitui/*
else
    echo "gitui: not found, skipped"
fi

if command -v claude >/dev/null 2>&1; then
    install_theme "Claude Code" "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/themes" "$out"/claude-code/*
else
    echo "Claude Code: not found, skipped"
fi
