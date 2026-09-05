"""Run with python3 check_palette.py; checks opaque theme text pairs."""

from pathlib import Path
import re
import tomllib


def luminance(color):
    rgb = [int(color[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    linear = [v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in rgb]
    return sum(v * weight for v, weight in zip(linear, (0.2126, 0.7152, 0.0722)))


def contrast(a, b):
    low, high = sorted((luminance(a), luminance(b)))
    return (high + 0.05) / (low + 0.05)


if __name__ == "__main__":
    assert contrast("#000000", "#ffffff") == 21
    colors = tomllib.loads(Path(__file__).with_name("colors.toml").read_text())
    assert colors.pop("mode") == "dark"
    assert all(re.fullmatch(r"#[0-9a-f]{6}", value) for value in colors.values())
    text_keys = [key for key in colors if "background" not in key and not key.startswith("selection")]
    pairs = [(key, "background") for key in text_keys]
    pairs += [("foreground", "lighter_background"), ("muted", "lighter_background")]
    pairs += [("selection_foreground", "selection_background")]
    for front, back in pairs:
        ratio = contrast(colors[front], colors[back])
        assert ratio >= 4.5, f"{front} on {back}: {ratio:.2f}:1"
    print(f"PASS: {len(pairs)} text pairs >= 4.5:1")
    for key in ("foreground", "muted", "red", "accent"):
        print(f"{key}: {contrast(colors[key], colors['background']):.2f}:1")
