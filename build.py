#!/usr/bin/env python3
"""Build the Mono themes in one hue.

    python3 build.py                                    # gray, black and white
    python3 build.py --hue 250                          # blue
    python3 build.py --hue 250 --chroma 0.6 --tint 0    # weaker blue on pure black and white
    python3 build.py --image wallpaper.jpg              # all three numbers from an image

The themes are always called mono-dark and mono-light, so a rebuild with other
colours replaces the installed ones without any change to the configuration.
A theme is set by three numbers:

    hue     OKLCH hue in degrees
    chroma  colour strength; 0 is gray, 1 the default, 2 the strongest
    tint    paper lift; 0 keeps the paper pure black or white, 1 the default

Every colour keeps the WCAG contrast against its paper that it has in the gray
theme. A tinted paper scales all log-contrasts by one factor, so the steps
between colours stay even. Hue and chroma come on top, with the chroma held
inside the sRGB gamut.

Only the Python standard library is needed, except for --image, which reads
the image with Pillow.
"""

import argparse
import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TEMPLATES = ROOT / "templates"

TOKENS = ["paper", "bg1", "bg2", "bg3", "bg4", "rule", "faint", "muted", "soft", "text", "ink"]

# The gray theme. Dark grays are spaced evenly in OKLab lightness; each light
# gray has the contrast against white that its dark one has against black.
GRAY = {
    "dark": ["#000000", "#121212", "#1c1c1c", "#282828", "#373737", "#484848",
             "#5d5d5d", "#838383", "#ababab", "#d4d4d4", "#ffffff"],
    "light": ["#ffffff", "#f2f2f2", "#e8e8e8", "#d9d9d9", "#c4c4c4", "#acacac",
              "#909090", "#686868", "#484848", "#2b2b2b", "#000000"],
}

# OKLCH chroma per token at chroma = 1. Literals (soft) and the selection
# (bg4) carry the hue; body text stays close to neutral for long reading.
CHROMA = [0.018, 0.024, 0.028, 0.036, 0.055, 0.040, 0.045, 0.050, 0.090, 0.014, 0.006]

GAMUT_FRACTION = 0.9                          # keep clear of the sRGB edge
PAPER_LIFT = {"dark": 0.18, "light": -0.025}  # OKLab L shift of the paper at tint = 1
INK_HEADROOM = 0.06                           # contrast given up at tint = 1 so ink can carry hue

COLOURFUL = 0.02          # image pixels below this chroma carry no hue
CHROMA_REFERENCE = 0.075  # mean chroma of an image that gives chroma = 1

# Colours beyond the tokens are a gray of the gray theme plus the token whose
# chroma they take. A bare token name stands for that token.
ANSI = {
    "dark": ["bg4", ("#8c8c8c", "muted"), "ink", ("#e8e8e8", "text"), "soft",
             ("#bebebe", "soft"), ("#989898", "soft"), "text",
             "muted", ("#bebebe", "soft"), "soft", "ink", "soft", "ink", "ink", "ink"],
    "light": ["text", ("#606060", "muted"), "ink", ("#1c1c1c", "text"), "soft",
              ("#3b3b3b", "soft"), ("#565656", "soft"), "faint",
              "muted", ("#3b3b3b", "soft"), "soft", "ink", "soft", "ink", "ink", "rule"],
}

# Claude Code keys that are not tokens: (dark gray, light gray, chroma from).
# Added lines take the selection's colour, removed lines stay near the paper.
CLAUDE_CODE = {
    "diffAdded": ("#2e2e2e", "#d0d0d0", "bg4"),
    "diffAddedWord": ("#404040", "#b7b7b7", "bg4"),
    "diffAddedDimmed": ("#1f1f1f", "#e4e4e4", "bg4"),
    "diffRemoved": ("#161616", "#eeeeee", "paper"),
    "diffRemovedWord": ("#242424", "#dedede", "paper"),
    "diffRemovedDimmed": ("#0f0f0f", "#f4f4f4", "paper"),
    "blue_FOR_SUBAGENTS_ONLY": ("#ebebeb", "#191919", "soft"),
    "green_FOR_SUBAGENTS_ONLY": ("#d7d7d7", "#292929", "soft"),
    "yellow_FOR_SUBAGENTS_ONLY": ("#c4c4c4", "#363636", "soft"),
    "purple_FOR_SUBAGENTS_ONLY": ("#b1b1b1", "#444444", "soft"),
    "orange_FOR_SUBAGENTS_ONLY": ("#9e9e9e", "#525252", "soft"),
    "pink_FOR_SUBAGENTS_ONLY": ("#8c8c8c", "#606060", "soft"),
    "cyan_FOR_SUBAGENTS_ONLY": ("#7a7a7a", "#717171", "soft"),
    "rainbow_red": ("#9e9e9e", "#525252", "soft"),
    "rainbow_red_shimmer": ("#c4c4c4", "#363636", "soft"),
    "rainbow_orange": ("#aeaeae", "#464646", "soft"),
    "rainbow_yellow": ("#bebebe", "#3b3b3b", "soft"),
    "rainbow_yellow_shimmer": ("#e4e4e4", "#1f1f1f", "soft"),
    "rainbow_green": ("#cecece", "#303030", "soft"),
    "rainbow_green_shimmer": ("#f5f5f5", "#0e0e0e", "soft"),
    "rainbow_blue": ("#dedede", "#242424", "soft"),
    "rainbow_indigo": ("#eeeeee", "#161616", "soft"),
}

# Template, then output path relative to the build directory.
OUTPUTS = [
    ("ghostty", "ghostty/{name}"),
    ("helix.toml", "helix/{name}.toml"),
    ("yazi.toml", "yazi/{name}.yazi/flavor.toml"),
    ("tmtheme.xml", "yazi/{name}.yazi/tmtheme.xml"),
    ("gitui.ron", "gitui/{name}.ron"),
    ("tmtheme.xml", "gitui/{name}.tmTheme"),
    ("claude-code.json", "claude-code/{name}.json"),
]


# Colour maths ---------------------------------------------------------------

def srgb_to_linear(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def linear_to_srgb(c):
    return 12.92 * c if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055


def hex_to_linear(x):
    return tuple(srgb_to_linear(int(x[i:i + 2], 16) / 255) for i in (1, 3, 5))


def linear_to_hex(rgb):
    return "#" + "".join(f"{round(min(max(linear_to_srgb(max(c, 0.0)), 0.0), 1.0) * 255):02x}" for c in rgb)


def oklab(rgb):
    r, g, b = rgb
    l = (0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b) ** (1 / 3)
    m = (0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b) ** (1 / 3)
    s = (0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b) ** (1 / 3)
    return (
        0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s,
        1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s,
        0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s,
    )


def oklch_to_linear(L, C, h):
    a = C * math.cos(math.radians(h))
    b = C * math.sin(math.radians(h))
    l = (L + 0.3963377774 * a + 0.2158037573 * b) ** 3
    m = (L - 0.1055613458 * a - 0.0638541728 * b) ** 3
    s = (L - 0.0894841775 * a - 1.2914855480 * b) ** 3
    return (
        +4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s,
        -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s,
        -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s,
    )


def luminance(rgb):
    r, g, b = rgb
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(y1, y2):
    return (max(y1, y2) + 0.05) / (min(y1, y2) + 0.05)


def max_chroma(L, h):
    lo, hi = 0.0, 0.4
    for _ in range(28):
        mid = (lo + hi) / 2
        if all(-1e-7 <= c <= 1 + 1e-7 for c in oklch_to_linear(L, mid, h)):
            lo = mid
        else:
            hi = mid
    return lo


def colour(L, C, h):
    """Linear sRGB at (L, C, h), with C pulled inside the gamut."""
    return oklch_to_linear(L, min(C, GAMUT_FRACTION * max_chroma(L, h)), h)


def solve(y, C, h):
    """Colour of chroma C and hue h whose luminance is y."""
    lo, hi = 0.0, 1.0
    for _ in range(36):
        mid = (lo + hi) / 2
        if luminance(colour(mid, C, h)) < y:
            lo = mid
        else:
            hi = mid
    return colour((lo + hi) / 2, C, h)


# Palette --------------------------------------------------------------------

class Palette:
    """One variant ("dark" or "light") of a theme."""

    def __init__(self, mode, hue, chroma, tint):
        self.dark = mode == "dark"
        self.hue = hue
        gray = [hex_to_linear(x) for x in GRAY[mode]]
        gray_y = [luminance(c) for c in gray]
        target = [c * chroma for c in CHROMA]
        if not self.dark:
            # Dark inks on light paper look more saturated at equal chroma, so
            # foreground tokens keep the dark variant's ratio of chroma to lightness.
            dark_L = [oklab(hex_to_linear(x))[0] for x in GRAY["dark"]]
            light_L = [oklab(c)[0] for c in gray]
            target = [c * min(1.0, l / d) if d > 0 else c for c, l, d in zip(target, light_L, dark_L)]
        self.chroma = dict(zip(TOKENS, target))

        paper = colour(oklab(gray[0])[0] + tint * PAPER_LIFT[mode], self.chroma["paper"], hue)
        self.gray_paper = gray_y[0]
        self.paper = luminance(paper)
        reach = (1.05 / (self.paper + 0.05) if self.dark else (self.paper + 0.05) / 0.05) * (1 - tint * INK_HEADROOM)
        self.scale = math.log(reach) / math.log(contrast(gray_y[-1], gray_y[0]))

        self.tokens = {"paper": linear_to_hex(paper)}
        for token, x in zip(TOKENS[1:], GRAY[mode][1:]):
            self.tokens[token] = self.shade(x, self.chroma[token])

    def shade(self, gray, chroma):
        """The colour of this chroma that stands to the paper as the gray does in the gray theme."""
        k = contrast(luminance(hex_to_linear(gray)), self.gray_paper) ** self.scale
        y = k * (self.paper + 0.05) - 0.05 if self.dark else (self.paper + 0.05) / k - 0.05
        return linear_to_hex(solve(y, chroma, self.hue))

    def extra(self, spec):
        if isinstance(spec, str):
            return self.tokens[spec]
        gray, token = spec
        return self.shade(gray, self.chroma[token])

    def cube(self, index):
        """Slot 16-255 of the xterm palette: the colour of equal lightness, the more chromatic the more colourful."""
        if index < 232:
            levels = (0, 95, 135, 175, 215, 255)
            i = index - 16
            rgb = [srgb_to_linear(levels[j] / 255) for j in (i // 36, i // 6 % 6, i % 6)]
        else:
            rgb = [srgb_to_linear((8 + 10 * (index - 232)) / 255)] * 3
        L, a, b = oklab(rgb)
        weight = min(1.0, math.hypot(a, b) / 0.16)
        chroma = (1 - weight) * self.chroma["bg1"] + weight * self.chroma["soft"]
        return self.shade(linear_to_hex([L ** 3] * 3), chroma)


# Image ----------------------------------------------------------------------

def load_image(path):
    """The sRGB pixels of an image, scaled down to at most 128 pixels a side."""
    try:
        from PIL import Image
    except ImportError:
        sys.exit("Reading an image needs the Pillow package (https://pypi.org/project/pillow/).")
    try:
        from pillow_heif import register_heif_opener
        register_heif_opener()
        heif = True
    except ImportError:
        heif = False
    try:
        with Image.open(path) as image:
            image.draft("RGB", (256, 256))
            image = image.convert("RGB")
            image.thumbnail((128, 128))
            data = image.tobytes()
    except OSError as error:
        if not heif and path.suffix.lower() in (".heic", ".heif"):
            sys.exit(f"Reading {path.name} needs the pillow-heif package (https://pypi.org/project/pillow-heif/).")
        sys.exit(f"Cannot read {path}: {error}")
    return [tuple(data[i:i + 3]) for i in range(0, len(data), 3)]


def hue_distance(h1, h2):
    return abs((h1 - h2 + 180) % 360 - 180)


def analyse(pixels):
    """Hue, chroma and tint for an image, plus its strongest hues with their share of the colour.

    The hue is the strongest peak of a histogram of the colourful pixels'
    hues, each pixel weighted by its chroma. Averaging all hues instead would
    turn an image of red and blue into magenta. The chroma follows the mean
    chroma of the image, and the tint the lightness of its darkest parts, so
    that an image with deep black shadows keeps the paper black.
    """
    lab = [oklab(tuple(srgb_to_linear(c / 255) for c in p)) for p in pixels]
    colourful = []
    bins = [0.0] * 72
    for _, a, b in lab:
        C = math.hypot(a, b)
        if C >= COLOURFUL:
            h = math.degrees(math.atan2(b, a)) % 360
            colourful.append((C, h, a, b))
            bins[int(h // 5)] += C
    total = sum(bins)

    kernel = (1, 2, 3, 4, 3, 2, 1)
    smooth = [sum(bins[(i + j - 3) % 72] * k for j, k in enumerate(kernel)) for i in range(72)]
    peaks = [i for i in range(72) if smooth[i] > 0 and smooth[i - 1] <= smooth[i] >= smooth[(i + 1) % 72]]
    hues = []
    for i in sorted(peaks, key=lambda i: -smooth[i]):
        centre = i * 5 + 2.5
        if any(hue_distance(centre, h) < 30 for h, _ in hues):
            continue
        # Summing (a, b) averages the hues near the peak, weighted by chroma.
        near = [(C, a, b) for C, h, a, b in colourful if hue_distance(h, centre) <= 15]
        hue = math.degrees(math.atan2(sum(b for _, _, b in near), sum(a for _, a, _ in near))) % 360
        share = sum(C for C, _, _ in near) / total
        if hues and share < 0.02:
            break
        hues.append((hue, share))
        if len(hues) == 3:
            break

    mean_chroma = sum(math.hypot(a, b) for _, a, b in lab) / len(lab)
    shadow = sorted(L for L, _, _ in lab)[len(lab) // 20]
    return {
        "hue": round(hues[0][0]) % 360 if hues else None,
        "chroma": round(min(2.0, mean_chroma / CHROMA_REFERENCE), 2) if hues else 0.0,
        "tint": round(min(1.0, shadow / PAPER_LIFT["dark"]), 2),
        "hues": hues,
    }


# Build ----------------------------------------------------------------------

def values(mode, hue, chroma, tint, command):
    p = Palette(mode, hue, chroma, tint)
    v = dict(p.tokens)
    v |= {f"ansi{i}": p.extra(spec) for i, spec in enumerate(ANSI[mode])}
    v["cube"] = "\n".join(f"palette = {i}={p.cube(i)}" for i in range(16, 256))
    column = 0 if mode == "dark" else 1
    v |= {key: p.extra((spec[column], spec[2])) for key, spec in CLAUDE_CODE.items()}
    v |= {
        "name": f"mono-{mode}",
        "variant": mode,
        "title": f"Mono {mode.title()}",
        "command": command,
    }
    return v


def render(template, v):
    return re.sub(r"\{\{(\w+)\}\}", lambda m: v[m.group(1)], template)


def main():
    parser = argparse.ArgumentParser(description="Build the Mono themes in one hue.")
    parser.add_argument("--hue", type=float, help="OKLCH hue in degrees; leave out for the gray theme")
    parser.add_argument("--chroma", type=float, help="colour strength, 0 to 2 (default 1 with a hue, 0 without)")
    parser.add_argument("--tint", type=float, help="paper lift, 0 to 1.5 (default 1 with a hue, 0 without)")
    parser.add_argument("--image", type=Path, help="take hue, chroma and tint from an image; options above override")
    parser.add_argument("--out", type=Path, default=ROOT / "build", help="output directory (default: build)")
    args = parser.parse_args()

    if args.image is not None:
        found = analyse(load_image(args.image))
        hues = ", ".join(f"{h:.0f} ({share:.0%})" for h, share in found["hues"]) or "none"
        print(f"{args.image.name}: hue {found['hue']}, chroma {found['chroma']:g}, tint {found['tint']:g}"
              f" (strongest hues: {hues})")
        for key in ("hue", "chroma", "tint"):
            if getattr(args, key) is None:
                setattr(args, key, found[key])

    gray = args.hue is None
    hue = 0.0 if gray else args.hue % 360
    chroma = args.chroma if args.chroma is not None else 0.0 if gray else 1.0
    tint = args.tint if args.tint is not None else 0.0 if gray else 1.0
    if gray and chroma > 0:
        parser.error("--chroma needs a --hue")
    if not 0 <= chroma <= 2:
        parser.error("--chroma must be between 0 and 2")
    if not 0 <= tint <= 1.5:
        parser.error("--tint must be between 0 and 1.5")

    command = "python3 build.py"
    if not gray:
        command += f" --hue {hue:g}"
    if chroma != (0.0 if gray else 1.0):
        command += f" --chroma {chroma:g}"
    if tint != (0.0 if gray else 1.0):
        command += f" --tint {tint:g}"

    templates = {t: (TEMPLATES / t).read_text() for t, _ in OUTPUTS}
    for mode in ("dark", "light"):
        v = values(mode, hue, chroma, tint, command)
        for template, path in OUTPUTS:
            target = args.out / path.format(name=v["name"])
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(render(templates[template], v))

    print(f"mono-dark and mono-light (hue {hue:g}, chroma {chroma:g}, tint {tint:g}) written to {args.out}")


if __name__ == "__main__":
    sys.exit(main())
