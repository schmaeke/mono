#!/bin/sh
# Install the Mono themes for every supported application found on this machine.
set -eu

src=$(cd "$(dirname "$0")" && pwd)
config=${XDG_CONFIG_HOME:-$HOME/.config}

install_theme() { # name, target directory, files...
    name=$1 dir=$2
    shift 2
    mkdir -p "$dir"
    cp "$@" "$dir"
    echo "$name: installed to $dir"
}

if command -v ghostty >/dev/null 2>&1 || [ -d /Applications/Ghostty.app ]; then
    install_theme Ghostty "$config/ghostty/themes" "$src"/ghostty/mono-dark "$src"/ghostty/mono-light
else
    echo "Ghostty: not found, skipped"
fi

if command -v hx >/dev/null 2>&1 || command -v helix >/dev/null 2>&1; then
    install_theme Helix "$config/helix/themes" "$src"/helix/mono-dark.toml "$src"/helix/mono-light.toml
else
    echo "Helix: not found, skipped"
fi

if command -v claude >/dev/null 2>&1; then
    install_theme "Claude Code" "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/themes" \
        "$src"/claude-code/mono-dark.json "$src"/claude-code/mono-light.json
else
    echo "Claude Code: not found, skipped"
fi
