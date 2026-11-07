#!/usr/bin/env python3
"""Rebuild the favicon set and Open Graph image from the existing NGX logos.

Masters, left unchanged:
  images/logo-mark.png
  images/logo-dark-blue.png

Outputs committed for GitHub Pages (no build on the host):
  favicon.ico
  favicon-16x16.png
  favicon-32x32.png
  apple-touch-icon.png
  images/og-image.png
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
YELLOW = (253, 228, 40)


def flatten(image: Image.Image, size: tuple[int, int] | None = None) -> Image.Image:
    image = image.convert("RGBA")
    if size is not None:
        image = image.resize(size, Image.Resampling.LANCZOS)
    background = image.getpixel((0, 0))
    plate = Image.new("RGB", image.size, background[:3])
    plate.paste(image, mask=image.split()[-1])
    return plate


def main() -> None:
    mark = Image.open(ROOT / "images/logo-mark.png")
    for size, name in (
        (16, "favicon-16x16.png"),
        (32, "favicon-32x32.png"),
        (180, "apple-touch-icon.png"),
    ):
        icon = flatten(mark, (size, size))
        icon.save(ROOT / name, optimize=True)
        print(name, icon.size)

    flatten(mark, (48, 48)).save(
        ROOT / "favicon.ico",
        format="ICO",
        sizes=[(16, 16), (32, 32), (48, 48)],
    )
    print("favicon.ico")

    word = Image.open(ROOT / "images/logo-dark-blue.png").convert("RGB")
    plate = word.getpixel((2, 2))
    canvas = Image.new("RGB", (1200, 630), plate)
    scale = 780 / word.width
    resized = word.resize((780, round(word.height * scale)), Image.Resampling.LANCZOS)
    x = (canvas.width - resized.width) // 2
    y = (canvas.height - resized.height) // 2 - 8
    canvas.paste(resized, (x, y))
    bar = Image.new("RGB", (canvas.width, 12), YELLOW)
    canvas.paste(bar, (0, canvas.height - bar.height))
    destination = ROOT / "images/og-image.png"
    canvas.save(destination, optimize=True)
    print(destination.name, canvas.size, destination.stat().st_size)


if __name__ == "__main__":
    main()
