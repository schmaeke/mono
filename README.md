# Mono

A black-and-white theme for Ghostty, Helix, Yazi, gitui and Claude Code, in a dark and a light variant. It uses no hue
at all, only eleven grays, bold and italic.

## Palette

The dark grays are spaced evenly in OKLab lightness. Each light gray has the same WCAG contrast against white as its
dark counterpart has against black, so both variants read the same.

| Token   | Dark      | Light     | Contrast | Role                                         |
| ------- | --------- | --------- | -------: | -------------------------------------------- |
| `paper` | `#000000` | `#ffffff` |      1.0 | Background                                   |
| `bg1`   | `#121212` | `#f2f2f2` |      1.1 | Cursor line, status line, ruler              |
| `bg2`   | `#1c1c1c` | `#e8e8e8` |      1.2 | Popups, menus, your messages in Claude Code  |
| `bg3`   | `#282828` | `#d9d9d9` |      1.4 | Secondary selection, focused picker row      |
| `bg4`   | `#373737` | `#c4c4c4` |      1.8 | Primary selection, selected menu item        |
| `rule`  | `#484848` | `#acacac` |      2.3 | Borders and dividers                         |
| `faint` | `#5d5d5d` | `#909090` |      3.2 | Line numbers, inlay hints                    |
| `muted` | `#838383` | `#686868` |      5.5 | Comments, punctuation, inactive text         |
| `soft`  | `#ababab` | `#484848` |      9.1 | Strings, numbers, constants                  |
| `text`  | `#d4d4d4` | `#2b2b2b` |     14.2 | Body text                                    |
| `ink`   | `#ffffff` | `#000000` |     21.0 | Keywords (bold), functions, types, cursor    |

Code uses four inks: `ink` for structure and names, `text` for the rest, `soft` for literals and `muted` for comments
and punctuation. Italic marks text that is not code: comments, inlay hints and emphasis in prose.

## Terminal colors

ANSI colors map to grays by their usual role, not their hue:

| Color   | Normal                         | Bright                                       |
| ------- | ------------------------------ | -------------------------------------------- |
| red     | dim: removed lines             | light: errors                                |
| green   | `ink`: added lines, success    | `soft`: strings in Claude Code               |
| yellow  | near `ink`: warnings           | `ink`: function names in Claude Code         |
| blue    | `soft`                         | `soft`: numbers in Claude Code               |
| magenta | light                          | `ink`: keywords in Claude Code               |
| cyan    | dim                            | `ink`: types in Claude Code                  |

Palette slots 16–255 map each color of the xterm 256-color cube to the gray of the same OKLab lightness. Programs that
use 256 colors are rendered in gray too.

## Install

```sh
./install.sh
```

The script copies the themes for each application it finds and skips the rest. It does not change any settings. To
install by hand, or to activate a theme afterwards:

**Ghostty**

```sh
cp ghostty/mono-dark ghostty/mono-light ~/.config/ghostty/themes/
```

```ini
theme = light:mono-light,dark:mono-dark
```

**Helix**

```sh
cp helix/mono-dark.toml helix/mono-light.toml ~/.config/helix/themes/
```

```toml
theme = "mono-dark"
```

**Yazi**

```sh
cp -R yazi/mono-dark.yazi yazi/mono-light.yazi ~/.config/yazi/flavors/
```

In `~/.config/yazi/theme.toml`:

```toml
[flavor]
dark = "mono-dark"
light = "mono-light"
```

Yazi picks the flavor that matches the terminal's background. Icons have no color of their own and take the color of the
file name: directories in bold `ink`, files in `text`, media and documents in `soft`, archives in `muted`. Code previews
use the flavor's `tmtheme.xml`, which sets code in the same four inks as the Helix theme.

**gitui**

```sh
cp -L gitui/* ~/.config/gitui/
```

```sh
gitui -t mono-dark.ron
```

gitui has no light and dark switch. Pass the variant with `-t`, or copy it to `~/.config/gitui/theme.ron` to make it the
default. Each theme loads the matching `.tmTheme` for code views and silently falls back to a colored syntax theme when it
is missing. In the repository, the `.tmTheme` files are symlinks to the Yazi `tmtheme.xml` files, so `cp -L` copies the
files they point to.

**Claude Code**

```sh
cp claude-code/mono-dark.json claude-code/mono-light.json ~/.claude/themes/
```

Select the theme with `/theme`, or set `"theme": "custom:mono-dark"` in `~/.claude/settings.json`.

Both Claude Code themes set every one of the 72 color keys. They are built on the `dark-ansi` and `light-ansi` bases,
because Claude Code takes the syntax colors for code blocks and diffs from the terminal's ANSI palette only with those
bases. With any other base it falls back to a fixed color scheme. Code in Claude Code is therefore black and white only
when the terminal uses the Mono palette.

## License

Mono is MIT licensed. See [`LICENSE`](LICENSE).
