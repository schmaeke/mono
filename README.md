# Mono

A monochromatic theme for Ghostty, foot, Helix, Yazi, gitui, zathura, mako, bottom, aerc, GTK, Qt and Claude Code, in a dark
and a light variant. Every color is a
shade of one hue that you choose, so colors differ only in lightness and chroma. Without a hue, Mono is black and white:
eleven grays, bold and italic.

## Build

```sh
python3 build.py --hue 250
```

This writes `mono-dark` and `mono-light` for all these applications, plus a palette file for scripts and the Linux
console colors, to `build/`. The themes always have these names, so a rebuild with other colors replaces the installed
ones and your configuration stays as it is. Apart from `--image`, the script needs only the Python standard library.

| Option     | Default      | Meaning                                                                       |
| ---------- | ------------ | ----------------------------------------------------------------------------- |
| `--hue`    | none, gray   | OKLCH hue in degrees                                                          |
| `--chroma` | 1            | Color strength, from 0 (gray) to 2                                            |
| `--tint`   | 1            | Paper lift, from 0 (pure black or white) to 1.5                               |
| `--image`  | none         | Take hue, chroma and tint from an image (see below)                           |
| `--out`    | `build`      | Output directory                                                              |

Without `--hue`, the script builds the gray theme, with chroma and tint 0. `--tint` also works without a hue and gives
a dark gray or off-white paper.

Some hues to start from: red 25, amber 70, olive 105, green 145, teal 190, blue 250, violet 290, rose 340. Yellow hues
turn olive in the light variant, because sRGB has no dark, saturated yellow.

### From a wallpaper

```sh
python3 build.py --image ~/Pictures/wallpaper.jpg
```

`--image` takes all three numbers from an image and prints them, together with the image's strongest hues:

- The hue is the strongest peak among the hues of the image's colorful pixels, each weighted by its chroma. An image of
  red and blue gives red or blue, whichever covers more, and never the magenta between them.
- The chroma follows the image's mean chroma: a gray photo gives 0, a hazy landscape about 0.3, a vivid graphic up to 2.
- The tint follows the lightness of the darkest 5 % of the image, up to 1. An image with deep black shadows keeps the
  paper black.

Options given next to `--image` override what it finds: `--image wallpaper.jpg --hue 30` keeps the image's chroma and
tint. The `Built with` line in each theme file records the numbers, not the image, so the build can be repeated without
it.

Reading the image needs the [Pillow](https://pypi.org/project/pillow/) package. It reads JPEG, PNG, WebP, TIFF and most
other formats; HEIC images, which macOS uses for its wallpapers, also need
[pillow-heif](https://pypi.org/project/pillow-heif/). Everything else needs only the standard library. To keep both out
of the system Python, install them into a virtual environment in the repository, which `install.sh` then uses:

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
./install.sh --image ~/Pictures/wallpaper.heic
```

## Palette

The palette is built in OKLCH. Each token keeps the WCAG contrast against its paper that it has in the gray theme, so
legibility does not depend on the hue. Hue and chroma come on top, with chroma held within 90 % of the sRGB gamut.

The gray theme sets the contrasts. Its dark grays are spaced evenly in OKLab lightness, and each light gray has the same
contrast against white as its dark counterpart has against black, so both variants read the same.

| Token   | Dark      | Light     | Contrast | Chroma | Role                                         |
| ------- | --------- | --------- | -------: | -----: | -------------------------------------------- |
| `paper` | `#000000` | `#ffffff` |      1.0 |  0.018 | Background                                   |
| `bg1`   | `#121212` | `#f2f2f2` |      1.1 |  0.024 | Cursor line, status line, ruler              |
| `bg2`   | `#1c1c1c` | `#e8e8e8` |      1.2 |  0.028 | Popups, menus, your messages in Claude Code  |
| `bg3`   | `#282828` | `#d9d9d9` |      1.4 |  0.036 | Secondary selection, focused picker row      |
| `bg4`   | `#373737` | `#c4c4c4` |      1.8 |  0.055 | Primary selection, selected menu item        |
| `rule`  | `#484848` | `#acacac` |      2.3 |  0.040 | Borders and dividers                         |
| `faint` | `#5d5d5d` | `#909090` |      3.2 |  0.045 | Line numbers, inlay hints                    |
| `muted` | `#838383` | `#686868` |      5.5 |  0.050 | Comments, punctuation, inactive text         |
| `soft`  | `#ababab` | `#484848` |      9.1 |  0.090 | Strings, numbers, constants                  |
| `text`  | `#d4d4d4` | `#2b2b2b` |     14.2 |  0.014 | Body text                                    |
| `ink`   | `#ffffff` | `#000000` |     21.0 |  0.006 | Keywords (bold), functions, types, cursor    |

Code uses four inks: `ink` for structure and names, `text` for the rest, `soft` for literals and `muted` for comments
and punctuation. Italic marks text that is not code: comments, inlay hints and emphasis in prose.

The chroma column is the OKLCH chroma at `--chroma 1`; the option scales it. Literals and the selection carry the hue,
and body text stays close to neutral for long reading. In the light variant, dark inks on light paper would look more
saturated at the same chroma, so each ink keeps the ratio of chroma to lightness that it has in the dark variant.

`--tint` lifts the paper away from pure black or white so that it can carry the hue too. All contrasts then shrink by one
factor in log scale, so the steps between tokens stay even. At `--tint 1`, `ink` has a contrast of about 18 and `muted`
of about 5.

## Terminal colors

ANSI colors map to palette colors by their usual role, not their hue:

| Color   | Normal                         | Bright                                       |
| ------- | ------------------------------ | -------------------------------------------- |
| red     | dim: removed lines             | light: errors                                |
| green   | `ink`: added lines, success    | `soft`: strings in Claude Code               |
| yellow  | near `ink`: warnings           | `ink`: function names in Claude Code         |
| blue    | `soft`                         | `soft`: numbers in Claude Code               |
| magenta | light                          | `ink`: keywords in Claude Code               |
| cyan    | dim                            | `ink`: types in Claude Code                  |

The light and dim colors that are not tokens take the chroma of `soft`, so colored terminal output shows the hue.

Palette slots 16–255 map each color of the xterm 256-color cube to the palette color of the same lightness. The more
colorful a slot is in xterm, the more chroma it gets, from that of `bg1` up to that of `soft`. Programs that use 256
colors stay in the one hue too.

## Install

```sh
./install.sh --hue 250
```

The script passes its options to `build.py`, builds the themes in a temporary directory and copies them for each
application it finds, and the palette to `~/.config/mono`. It skips the rest and does not change any settings. Without
options it installs the gray theme.

To install by hand, run `build.py` and copy the files from `build/`. To change the colors later, run the script again with
other options; the configuration below stays the same.

**Ghostty**

```sh
cp build/ghostty/* ~/.config/ghostty/themes/
```

```ini
theme = light:mono-light,dark:mono-dark
```

**Helix**

```sh
cp build/helix/* ~/.config/helix/themes/
```

```toml
theme = "mono-dark"
```

The theme leaves the editor background to the terminal, so a transparent terminal stays transparent in Helix. Use it
in a terminal with the matching Mono theme, whose background is the paper color.

**Yazi**

```sh
cp -R build/yazi/* ~/.config/yazi/flavors/
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
cp build/gitui/* ~/.config/gitui/
```

```sh
gitui -t mono-dark.ron
```

gitui has no light and dark switch. Pass the variant with `-t`, or copy it to `~/.config/gitui/theme.ron` to make it the
default. Each theme loads the matching `.tmTheme` for code views and silently falls back to a colored syntax theme when it
is missing.

**Claude Code**

```sh
cp build/claude-code/* ~/.claude/themes/
```

Select the theme with `/theme`, or set `"theme": "custom:mono-dark"` in `~/.claude/settings.json`.

Both Claude Code themes set every one of the 72 color keys. They are built on the `dark-ansi` and `light-ansi` bases,
because Claude Code takes the syntax colors for code blocks and diffs from the terminal's ANSI palette only with those
bases. With any other base it falls back to a fixed color scheme. Code in Claude Code is therefore in the theme's hue
only when the terminal uses the matching Mono palette. Added lines in diffs take the chroma of the selection, and
removed lines stay close to the paper.

**foot**

```sh
cp build/foot/* ~/.config/foot/
```

In `~/.config/foot/foot.ini`, before any `[colors-…]` section of your own:

```ini
[main]
include=~/.config/foot/mono-dark.ini
include=~/.config/foot/mono-light.ini
initial-color-theme=dark
```

Each file holds one section, `[colors-dark]` or `[colors-light]`. foot starts in `initial-color-theme`, and `SIGUSR1`
and `SIGUSR2` switch a running foot to dark or light. Slots 16–255 are the same as in the Ghostty theme.

**zathura**

```sh
cp build/zathura/* ~/.config/zathura/
```

In `~/.config/zathura/zathurarc`:

```
include mono-dark
```

zathura has no light and dark switch. To switch, include a link such as `mono` that points to either file. `Ctrl-r`
recolors the page from `text` on `paper`.

**mako**

```sh
cp build/mako/* ~/.config/mako/
```

At the end of `~/.config/mako/config`:

```ini
include=~/.config/mako/mono-dark
include=~/.config/mako/mono-light
```

The files hold the sections `[mode=dark]` and `[mode=light]`. Select one with `makoctl mode -s dark`.

**GTK 3**

```sh
cp -R build/gtk-3.0/* ~/.local/share/themes/
gsettings set org.gnome.desktop.interface gtk-theme mono-dark
```

`mono-dark` and `mono-light` are GTK 3 themes over adw-gtk3, the GTK 3 port of libadwaita (on Arch the package
`adw-gtk-theme`), which draws every widget and state from libadwaita's named colors. The themes set these colors:
windows and views on the paper, header bars, sidebars and cards on `bg1`, popovers on `bg2`, the accent in `soft` with
the paper on it, and messages on `bg3` in `ink`. Being themes rather than a `gtk.css`, they switch in running programs
when the setting changes.

**GTK 4 and libadwaita**

```sh
cp build/gtk-4.0/* ~/.config/gtk-4.0/
ln -sf mono-dark.css ~/.config/gtk-4.0/gtk.css
```

libadwaita ignores themes but reads `~/.config/gtk-4.0/gtk.css`, which sets the same named colors as the GTK 3 themes.
Programs read it when they start.

**Qt**

```sh
cp build/qt6ct/* ~/.config/qt6ct/colors/
```

In `~/.config/qt6ct/qt6ct.conf`, with `QT_QPA_PLATFORMTHEME=qt6ct` in the environment:

```ini
[Appearance]
style=Fusion
custom_palette=true
color_scheme_path=/home/you/.config/qt6ct/colors/mono-dark.conf
```

The color scheme sets all 22 roles of Qt's palette for the active, inactive and disabled state, from the same tokens as
the GTK themes. Qt programs read it when they start.

**bottom**

```sh
cp build/bottom/* ~/.config/bottom/
ln -sf mono-dark.toml ~/.config/bottom/bottom.toml
```

bottom reads a single config file, so link it to the variant, or copy the `[styles]` tables into your own: borders in
`rule`, the selected widget in `soft`, the selected row in `bg4`, and graph lines told apart by lightness. No background
color is set, so the terminal's shows through.

**aerc**

```sh
mkdir -p ~/.config/aerc/stylesets
cp build/aerc/* ~/.config/aerc/stylesets/
```

Set `styleset-name=mono-dark` (or `mono-light`) under `[ui]` in `aerc.conf`. The styleset is flat like the Yazi flavor:
no background colors, the selection underlined in `ink`, unread mail in `ink` and bold, read mail `muted`, flagged and
marked mail `soft`. Its `[viewer]` section colors mail through aerc's `colorize` filter: links and quotes in `soft`,
deeper quotes fading to `faint`.

**Palette for scripts**

`build/palette/mono-dark` and `mono-light` hold the eleven tokens as `name=rrggbb` lines without `#`, for programs
without a theme of their own: source them in a shell script, or read the lines. `install.sh` copies them to
`~/.config/mono/`. For example, for a launcher:

```sh
. ~/.config/mono/mono-dark
wmenu -N "$paper" -n "$soft" -S "$bg3" -s "$ink"
```

**Linux console**

`build/console/mono-dark` and `mono-light` hold the 16 console colors as `#rrggbb` lines, in the format of
`setvtrgb`. Color 0 is the paper, since the console draws its background in color 0; the others are the terminal
colors. `install.sh` copies them to `~/.config/mono/console/`. To set them until the next boot:

```sh
sudo setvtrgb ~/.config/mono/console/mono-dark
```

To set them from the start of the boot, pass them as the kernel parameters `vt.default_red`, `vt.default_grn` and
`vt.default_blu`, each a list of the 16 values in decimal.

## Templates

Each application has a template in `templates/`. `{{token}}` stands for a color as `#rrggbb`, `{{token|bare}}` for
`rrggbb` and `{{token|rgb}}` for `r,g,b`. Besides the tokens there are `ansi0` to `ansi15`, `cube` and `cube_foot` (slots
16–255 for Ghostty and foot), the Claude Code keys, and `name`, `variant`, `dark_suffix` (`-dark` or nothing), `title`
and `command`. A new application needs a template and a line in `OUTPUTS` in `build.py`.

## License

Mono is MIT licensed. See [`LICENSE`](LICENSE).
