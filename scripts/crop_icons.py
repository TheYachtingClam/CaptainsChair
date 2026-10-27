#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["pillow>=11.0", "numpy>=2.0"]
# ///
"""Crop the game's icons from the rulebook's icon reference (page 36) into client/public/icons/<name>.webp.

The client draws them in place of "[Action]", "[Dilithium]" and the other bracketed icon names in card text and the
tutorial coach (client/src/components/Icons.tsx). The page is a photo on light paper: the background is the
near-white area connected to the crop's edges, and becomes transparent. Re-run after changing a box.

Usage: scripts/crop_icons.py
"""

from collections import deque
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
PAGE = ROOT / "resources/scans/to_boldly_go/manual/page-036.jpg"
OUT = ROOT / "client/public/icons"
HEIGHT = 96

# name: (left, top, right, bottom) in the full-size page's pixels.
BOXES = {
    "action": (1450, 1635, 1560, 1760),
    "away-team": (1445, 1840, 1570, 1960),
    "dilithium": (1440, 2450, 1575, 2585),
    "latinum": (1440, 2635, 1575, 2768),
    "glory": (1440, 2815, 1575, 2940),
    "research": (830, 2460, 940, 2575),
    "influence": (1130, 1280, 1280, 1395),
    "military": (1140, 2015, 1260, 2135),
}


def transparent_background(rgb: np.ndarray, tolerance: int = 38) -> np.ndarray:
    """An alpha channel: 0 for the light background reachable from the edges, 255 for the icon."""
    h, w, _ = rgb.shape
    light = rgb.astype(int).min(axis=2) > 255 - tolerance - 40
    seen = np.zeros((h, w), bool)
    queue = deque((y, x) for y in range(h) for x in (0, w - 1)) + deque((y, x) for x in range(w) for y in (0, h - 1))
    while queue:
        y, x = queue.popleft()
        if seen[y, x] or not light[y, x]:
            continue
        seen[y, x] = True
        for ny, nx in ((y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)):
            if 0 <= ny < h and 0 <= nx < w and not seen[ny, nx]:
                queue.append((ny, nx))
    return np.where(seen, 0, 255).astype(np.uint8)


def main() -> None:
    page = Image.open(PAGE).convert("RGB")
    OUT.mkdir(parents=True, exist_ok=True)
    for name, box in BOXES.items():
        rgb = np.array(page.crop(box))
        alpha = transparent_background(rgb)
        icon = Image.fromarray(np.dstack([rgb, alpha]), "RGBA")
        icon = icon.crop(icon.getbbox())
        icon = icon.resize((round(icon.width * HEIGHT / icon.height), HEIGHT), Image.LANCZOS)
        icon.save(OUT / f"{name}.webp", quality=90)
        print(f"{name}: {icon.width}x{icon.height}")


if __name__ == "__main__":
    main()
