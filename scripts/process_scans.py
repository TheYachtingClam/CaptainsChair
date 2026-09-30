#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["opencv-python-headless>=4.10", "numpy>=2.0", "pillow>=11.0"]
# ///
"""Turn raw card scans into web-ready card images.

Reads   resources/scans/cards/**/*.{jpg,jpeg,png,webp,tif,tiff}   any folder layout, any depth
Writes  server/content/images/<same folders>/<card_id>.webp
        server/content/images/manifest.json

Organise the scans however you like, for example:
  resources/scans/cards/cargo/...
  resources/scans/cards/captains/soval/...
The processed images use the same folders, so server/content/images/captains/soval/2SOV01.webp.

Each output file is named by the card id printed on the card, for example 2GEO01.
Card ids must be unique across all folders. A raw scan gets its card id from, in order:
  1. a mapping.csv in the same folder as the scan, with columns  file,card_id[,rotate]
     rotate is 0, 90, 180 or 270 degrees clockwise, applied after cropping.
  2. the raw file name, if it starts with a card id, for example "2GEO01.jpg" or "2GEO01 front.jpg".
Scans with no card id are skipped and listed at the end.

For each scan the script finds the card's outline, straightens it with a perspective
warp, and resizes it to 630 x 880 pixels (portrait) or 880 x 630 (landscape).
Use --no-detect to skip outline detection and only resize the whole photo.

A full run (no folders given) also cleans up: images whose scan was deleted or renamed are
removed, and an image moves when its scan moves to another folder.

Usage:
  scripts/process_scans.py                          process every folder
  scripts/process_scans.py captains/soval cargo     process only these folders (and their subfolders)
  scripts/process_scans.py --force                  redo images that are already up to date
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SCANS_DIR = ROOT / "resources" / "scans" / "cards"
OUT_DIR = ROOT / "server" / "content" / "images"
MANIFEST = OUT_DIR / "manifest.json"

CARD_SHORT, CARD_LONG = 630, 880  # 63 x 88 mm card ratio
WEBP_QUALITY = 82
RAW_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff"}
# Printed ids look like 2GEO01, 2LOC05, SD09. Card backs and other special images
# may use lower-case ids such as back-standard.
PRINTED_ID_RE = re.compile(r"^([0-9]?[A-Z]{2,5}[0-9]{2,3})(?=$|[ _.-])")
SPECIAL_ID_RE = re.compile(r"^[a-z][a-z0-9]*(-[a-z0-9]+)+$")  # whole name, e.g. back-standard


def load_mapping(set_dir: Path) -> dict[str, tuple[str, int]]:
    path = set_dir / "mapping.csv"
    if not path.exists():
        return {}
    mapping: dict[str, tuple[str, int]] = {}
    with path.open(newline="") as f:
        for row in csv.DictReader(f):
            name = (row.get("file") or "").strip()
            card_id = (row.get("card_id") or "").strip()
            if name and card_id:
                mapping[name] = (card_id, int((row.get("rotate") or "0").strip() or 0))
    return mapping


def card_id_for(raw: Path, mapping: dict[str, tuple[str, int]]) -> tuple[str, int] | None:
    if raw.name in mapping:
        return mapping[raw.name]
    match = PRINTED_ID_RE.match(raw.stem)
    if match:
        return match.group(1), 0
    return (raw.stem, 0) if SPECIAL_ID_RE.match(raw.stem) else None


def order_corners(pts: np.ndarray) -> np.ndarray:
    """Top-left, top-right, bottom-right, bottom-left."""
    pts = pts.reshape(4, 2).astype("float32")
    s = pts.sum(axis=1)
    d = np.diff(pts, axis=1).ravel()
    return np.array([pts[s.argmin()], pts[d.argmin()], pts[s.argmax()], pts[d.argmax()]], dtype="float32")


def find_card(image: np.ndarray) -> np.ndarray | None:
    """Return the four corners of the largest card-shaped outline, or None."""
    h, w = image.shape[:2]
    scale = 1000 / max(h, w)
    small = cv2.resize(image, (int(w * scale), int(h * scale))) if scale < 1 else image
    scale = min(scale, 1.0)
    gray = cv2.GaussianBlur(cv2.cvtColor(small, cv2.COLOR_BGR2GRAY), (5, 5), 0)
    edges = cv2.dilate(cv2.Canny(gray, 40, 120), np.ones((3, 3), np.uint8), iterations=1)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    area_min = 0.05 * small.shape[0] * small.shape[1]
    for contour in sorted(contours, key=cv2.contourArea, reverse=True)[:5]:
        if cv2.contourArea(contour) < area_min:
            break
        approx = cv2.approxPolyDP(contour, 0.02 * cv2.arcLength(contour, True), True)
        if len(approx) == 4:
            return order_corners(approx) / scale
        # Rounded card corners often give more than 4 points; fall back to the min-area box.
        box = cv2.boxPoints(cv2.minAreaRect(contour))
        return order_corners(box) / scale
    return None


EDGE_INSET = 0.004  # outline detection overshoots the card edge slightly; pull corners in


def straighten(image: np.ndarray, corners: np.ndarray) -> np.ndarray:
    center = corners.mean(axis=0)
    corners = (corners + (center - corners) * EDGE_INSET * 2).astype("float32")
    tl, tr, br, bl = corners
    width = max(np.linalg.norm(tr - tl), np.linalg.norm(br - bl))
    height = max(np.linalg.norm(bl - tl), np.linalg.norm(br - tr))
    out_w, out_h = (CARD_SHORT, CARD_LONG) if height >= width else (CARD_LONG, CARD_SHORT)
    target = np.array([[0, 0], [out_w - 1, 0], [out_w - 1, out_h - 1], [0, out_h - 1]], dtype="float32")
    matrix = cv2.getPerspectiveTransform(corners, target)
    return cv2.warpPerspective(image, matrix, (out_w, out_h), flags=cv2.INTER_AREA)


def fit(image: np.ndarray) -> np.ndarray:
    h, w = image.shape[:2]
    size = (CARD_SHORT, CARD_LONG) if h >= w else (CARD_LONG, CARD_SHORT)
    return cv2.resize(image, size, interpolation=cv2.INTER_AREA)


def rotate(image: np.ndarray, degrees: int) -> np.ndarray:
    codes = {90: cv2.ROTATE_90_CLOCKWISE, 180: cv2.ROTATE_180, 270: cv2.ROTATE_90_COUNTERCLOCKWISE}
    return cv2.rotate(image, codes[degrees]) if degrees in codes else image


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def find_scans() -> list[Path]:
    """Every raw scan under SCANS_DIR, at any depth, skipping hidden files and folders."""
    if not SCANS_DIR.exists():
        return []
    return sorted(
        p for p in SCANS_DIR.rglob("*")
        if p.is_file()
        and p.suffix.lower() in RAW_SUFFIXES
        and not any(part.startswith(".") for part in p.relative_to(SCANS_DIR).parts)
    )


def remove_output(file: str) -> None:
    path = OUT_DIR / file
    if path.is_file():
        path.unlink()


def remove_empty_dirs(root: Path) -> None:
    for d in sorted((p for p in root.rglob("*") if p.is_dir()), key=lambda p: len(p.parts), reverse=True):
        if not any(d.iterdir()):
            d.rmdir()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("folders", nargs="*", help="folders under resources/scans/cards to process (default: all)")
    parser.add_argument("--force", action="store_true", help="reprocess images that are already up to date")
    parser.add_argument("--no-detect", action="store_true", help="skip outline detection; only resize")
    args = parser.parse_args()

    manifest: dict = json.loads(MANIFEST.read_text()) if MANIFEST.exists() else {"cards": {}}
    cards: dict[str, dict] = manifest.setdefault("cards", {})

    filters: list[Path] = []
    for folder in args.folders:
        path = (SCANS_DIR / folder).resolve()
        if not path.is_dir() or SCANS_DIR.resolve() not in (path, *path.parents):
            print(f"No such folder under {SCANS_DIR.relative_to(ROOT)}: {folder}", file=sys.stderr)
            return 1
        filters.append(path)

    # Resolve every scan's card id first, across all folders, so duplicates are caught
    # even when only some folders are being processed.
    mappings: dict[Path, dict[str, tuple[str, int]]] = {}
    by_id: dict[str, tuple[Path, int]] = {}
    skipped: list[str] = []
    duplicates: list[str] = []
    for raw in find_scans():
        mapping = mappings.setdefault(raw.parent, load_mapping(raw.parent))
        found = card_id_for(raw, mapping)
        if found is None:
            skipped.append(str(raw.relative_to(ROOT)))
            continue
        card_id, degrees = found
        if card_id in by_id:
            duplicates.append(f"  {card_id}: {by_id[card_id][0].relative_to(ROOT)} and {raw.relative_to(ROOT)}")
            continue
        by_id[card_id] = (raw, degrees)
    if duplicates:
        print("Each card id may appear only once. Duplicates:\n" + "\n".join(duplicates), file=sys.stderr)
        return 1

    undetected: list[str] = []
    written = unchanged = moved = 0

    for card_id, (raw, degrees) in sorted(by_id.items(), key=lambda kv: kv[1][0]):
        if filters and not any(f == raw.resolve().parent or f in raw.resolve().parents for f in filters):
            continue
        folder = raw.parent.relative_to(SCANS_DIR)
        file = (folder / f"{card_id}.webp").as_posix()
        out = OUT_DIR / file
        source_hash = file_hash(raw)
        settings_key = f"{degrees}:{args.no_detect}"
        entry = cards.get(card_id)

        if entry and entry.get("file") != file:
            # The scan moved to another folder. If it is otherwise unchanged, move its image;
            # otherwise drop the old image and regenerate below.
            old = OUT_DIR / entry["file"]
            if (not args.force and old.is_file() and entry.get("source_sha256") == source_hash
                    and entry.get("settings") == settings_key):
                out.parent.mkdir(parents=True, exist_ok=True)
                old.replace(out)
                entry.update(folder=folder.as_posix() if folder.parts else "", file=file,
                             source=str(raw.relative_to(ROOT)))
                moved += 1
                print(f"moved {old.relative_to(ROOT)} -> {out.relative_to(ROOT)}")
                continue
            remove_output(entry["file"])

        if (not args.force and out.exists() and entry and entry.get("file") == file
                and entry.get("source_sha256") == source_hash and entry.get("settings") == settings_key):
            unchanged += 1
            continue

        image = cv2.imread(str(raw), cv2.IMREAD_COLOR)
        if image is None:
            print(f"Cannot read {raw}", file=sys.stderr)
            return 1
        corners = None if args.no_detect else find_card(image)
        if corners is None and not args.no_detect:
            undetected.append(str(raw.relative_to(ROOT)))
        card = straighten(image, corners) if corners is not None else fit(image)
        card = rotate(card, degrees)

        out.parent.mkdir(parents=True, exist_ok=True)
        Image.fromarray(cv2.cvtColor(card, cv2.COLOR_BGR2RGB)).save(out, "WEBP", quality=WEBP_QUALITY, method=6)
        cards[card_id] = {
            "folder": folder.as_posix() if folder.parts else "",
            "file": file,
            "version": file_hash(out)[:12],
            "source": str(raw.relative_to(ROOT)),
            "source_sha256": source_hash,
            "settings": settings_key,
        }
        written += 1
        print(f"{raw.relative_to(ROOT)} -> {out.relative_to(ROOT)}")

    removed: list[str] = []
    if not filters:
        # Full run: forget images whose scan is gone, and delete any stray output files.
        for card_id in sorted(set(cards) - set(by_id)):
            remove_output(cards.pop(card_id)["file"])
            removed.append(card_id)
        known = {entry["file"] for entry in cards.values()}
        if OUT_DIR.exists():
            for stray in OUT_DIR.rglob("*.webp"):
                if stray.relative_to(OUT_DIR).as_posix() not in known:
                    stray.unlink()
                    removed.append(str(stray.relative_to(ROOT)))
            remove_empty_dirs(OUT_DIR)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps({"cards": dict(sorted(cards.items()))}, indent=2) + "\n")

    print(f"\nWrote {written} image(s), {moved} moved to a new folder; {unchanged} already up to date.")
    if removed:
        print("\nRemoved images with no matching scan:")
        print("\n".join(f"  {r}" for r in removed))
    if undetected:
        print("\nNo card outline found; the whole photo was resized instead. Check these:")
        print("\n".join(f"  {p}" for p in undetected))
    if skipped:
        print("\nSkipped, because no card id was found in mapping.csv or the file name:")
        print("\n".join(f"  {p}" for p in skipped))
    return 0


if __name__ == "__main__":
    sys.exit(main())
