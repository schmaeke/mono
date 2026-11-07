#!/bin/sh
# Install the Mono themes for every supported application found on this machine.
set -eu

src=$(cd "$(dirname "$0")" && pwd)
config=${XDG_CONFIG_HOME:-$HOME/.config}

install_theme() { # name, target directory, files or directories...
    name=$1 dir=$2
    shift 2
    mkdir -p "$dir"
    cp -RL "$@" "$dir"
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

if command -v yazi >/dev/null 2>&1; then
    install_theme Yazi "${YAZI_CONFIG_HOME:-$config/yazi}/flavors" \
        "$src"/yazi/mono-dark.yazi "$src"/yazi/mono-light.yazi
else
    echo "Yazi: not found, skipped"
fi

if command -v gitui >/dev/null 2>&1; then
    # gitui reads ~/.config on macOS whatever XDG_CONFIG_HOME says.
    if [ "$(uname)" = Darwin ]; then gitui_config=$HOME/.config/gitui; else gitui_config=$config/gitui; fi
    install_theme gitui "$gitui_config" "$src"/gitui/mono-dark.ron "$src"/gitui/mono-light.ron \
        "$src"/gitui/mono-dark.tmTheme "$src"/gitui/mono-light.tmTheme
else
    echo "gitui: not found, skipped"
fi

if command -v claude >/dev/null 2>&1; then
    install_theme "Claude Code" "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/themes" \
        "$src"/claude-code/mono-dark.json "$src"/claude-code/mono-light.json
else
    echo "Claude Code: not found, skipped"
fi
