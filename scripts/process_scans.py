#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["opencv-python-headless>=4.10", "numpy>=2.0", "pillow>=11.0", "pypdfium2>=4.30"]
# ///
"""Turn raw scans into the web images the server serves.

Reads   resources/scans/<set>/<kind>/**/*.{jpg,jpeg,png,webp,tif,tiff,pdf}
Writes  server/content/images/<set>/<kind>/<same folders>/<id>.webp
        server/content/images/manifest.json

<set> is the product, e.g. to_boldly_go, second_contact or promo2. <kind> is the folder below it,
and sets how images are sized:
  cards/     forced to exact card proportions, 630 x 880 (or 880 x 630 for landscape cards)
  boards/    crew boards; the scan's own proportions are kept, 1800 px on the long side
  command/   the Bot's Automated Command cards; own proportions kept, 1400 px on the long side
  manual/, solo/   rulebook scans; never processed
Any other kind folder keeps its proportions at 1200 px on the long side.
Below the kind folder, organise scans however you like, at any depth.

Every image needs an id, unique across all folders. It comes from, in order:
  1. a mapping.csv in the same folder as the scan, with columns  file,id[,rotate]
     For a PDF page, write the file as  name.pdf#2  (pages count from 1).
     rotate is 0, 90, 180 or 270 degrees clockwise.
  2. the file name, if it starts with a printed card id, such as "2GEO01.jpg" or "2GEO01 front.jpg",
     or if the whole name is a lower-case hyphenated id, such as "cb-soval-basic.jpg".
  3. for a PDF page with no mapping: the PDF's name plus the page number, such as cc-soval-p2.
Scans with no id are skipped and listed at the end.

Scans are expected to be cropped to the item already, as flatbed or app scans are.
For photos that still show the table around the item, add --detect: the script then finds
the item's outline and straightens it. Do not use --detect on cropped scans; it can lock onto
the artwork inside a card and crop to that.

A full run (no folders given) also cleans up: images whose scan was deleted or renamed are
removed, and an image moves when its scan moves to another folder.

Usage:
  scripts/process_scans.py                               process everything
  scripts/process_scans.py to_boldly_go/cards second_contact    process only these folders
  scripts/process_scans.py --force                       redo images that are already up to date
  scripts/process_scans.py to_boldly_go/cards/photos --detect   straighten uncropped photos
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np
import pypdfium2 as pdfium
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SCANS_DIR = ROOT / "resources" / "scans"
OUT_DIR = ROOT / "server" / "content" / "images"
MANIFEST = OUT_DIR / "manifest.json"

WEBP_QUALITY = 82
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff"}
PRINTED_ID_RE = re.compile(r"^([0-9]?[A-Z]{2,5}[0-9]{2,3}[AB]?)(?=$|[ _.-])")  # A/B: sides of a double-sided card
SPECIAL_ID_RE = re.compile(r"^[a-z][a-z0-9]*(-[a-z0-9]+)+$")  # whole name, e.g. cb-soval-basic


@dataclass(frozen=True)
class Profile:
    long_side: int
    card_shape: bool  # force exact 63:88 proportions


PROFILES = {
    "cards": Profile(long_side=880, card_shape=True),
    "boards": Profile(long_side=1800, card_shape=False),
    "command": Profile(long_side=1400, card_shape=False),
}
DEFAULT_PROFILE = Profile(long_side=1200, card_shape=False)
SKIP_KINDS = {"manual", "solo"}  # rulebook scans, read by people only
CARD_RATIO = 63 / 88


@dataclass(frozen=True)
class Source:
    """One image to produce: an image file, or one page of a PDF."""

    path: Path
    page: int | None = None  # 1-based PDF page

    @property
    def label(self) -> str:
        rel = self.path.relative_to(ROOT)
        return f"{rel}#{self.page}" if self.page else str(rel)

    @property
    def mapping_key(self) -> str:
        return f"{self.path.name}#{self.page}" if self.page else self.path.name

    @property
    def kind(self) -> str:
        return self.path.relative_to(SCANS_DIR).parts[1]

    @property
    def folder(self) -> Path:
        return self.path.parent.relative_to(SCANS_DIR)


# ---------------------------------------------------------------- finding scans and ids


def find_sources() -> list[Source]:
    if not SCANS_DIR.exists():
        return []
    sources: list[Source] = []
    for p in sorted(SCANS_DIR.rglob("*")):
        rel = p.relative_to(SCANS_DIR)
        if not p.is_file() or len(rel.parts) < 3 or any(part.startswith(".") for part in rel.parts):
            continue
        if rel.parts[1] in SKIP_KINDS:
            continue
        suffix = p.suffix.lower()
        if suffix in IMAGE_SUFFIXES:
            sources.append(Source(p))
        elif suffix == ".pdf":
            pdf = pdfium.PdfDocument(p)
            sources.extend(Source(p, page) for page in range(1, len(pdf) + 1))
            pdf.close()
    return sources


def load_mapping(folder: Path) -> dict[str, tuple[str, int]]:
    path = folder / "mapping.csv"
    if not path.exists():
        return {}
    mapping: dict[str, tuple[str, int]] = {}
    with path.open(newline="") as f:
        for row in csv.DictReader(f):
            name = (row.get("file") or "").strip()
            image_id = (row.get("id") or row.get("card_id") or "").strip()
            if name and image_id:
                mapping[name] = (image_id, int((row.get("rotate") or "0").strip() or 0))
    return mapping


def id_for(source: Source, mapping: dict[str, tuple[str, int]]) -> tuple[str, int] | None:
    if source.mapping_key in mapping:
        return mapping[source.mapping_key]
    stem = source.path.stem
    match = PRINTED_ID_RE.match(stem)
    if match and not source.page:
        return match.group(1), 0
    if SPECIAL_ID_RE.match(stem):
        return (f"{stem}-p{source.page}" if source.page else stem), 0
    return None


# ---------------------------------------------------------------- image processing


def load(source: Source, profile: Profile) -> np.ndarray | None:
    if source.page is None:
        return cv2.imread(str(source.path), cv2.IMREAD_COLOR)
    pdf = pdfium.PdfDocument(source.path)
    page = pdf[source.page - 1]
    width, height = page.get_size()
    # Render at twice the target size, then scale down for a sharp result.
    pil = page.render(scale=2 * profile.long_side / max(width, height)).to_pil().convert("RGB")
    pdf.close()
    return cv2.cvtColor(np.asarray(pil), cv2.COLOR_RGB2BGR)


def order_corners(pts: np.ndarray) -> np.ndarray:
    """Top-left, top-right, bottom-right, bottom-left."""
    pts = pts.reshape(4, 2).astype("float32")
    s = pts.sum(axis=1)
    d = np.diff(pts, axis=1).ravel()
    return np.array([pts[s.argmin()], pts[d.argmin()], pts[s.argmax()], pts[d.argmax()]], dtype="float32")


def find_outline(image: np.ndarray) -> np.ndarray | None:
    """Four corners of the largest rectangular outline in a photo, or None."""
    h, w = image.shape[:2]
    scale = min(1.0, 1000 / max(h, w))
    small = cv2.resize(image, (int(w * scale), int(h * scale))) if scale < 1 else image
    gray = cv2.GaussianBlur(cv2.cvtColor(small, cv2.COLOR_BGR2GRAY), (5, 5), 0)
    edges = cv2.dilate(cv2.Canny(gray, 40, 120), np.ones((3, 3), np.uint8), iterations=1)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    area_min = 0.05 * small.shape[0] * small.shape[1]
    for contour in sorted(contours, key=cv2.contourArea, reverse=True)[:5]:
        if cv2.contourArea(contour) < area_min:
            break
        approx = cv2.approxPolyDP(contour, 0.02 * cv2.arcLength(contour, True), True)
        corners = approx if len(approx) == 4 else cv2.boxPoints(cv2.minAreaRect(contour))
        return order_corners(corners) / scale
    return None


EDGE_INSET = 0.004  # outline detection overshoots the edge slightly; pull corners in


def straighten(image: np.ndarray, corners: np.ndarray) -> np.ndarray:
    center = corners.mean(axis=0)
    corners = (corners + (center - corners) * EDGE_INSET * 2).astype("float32")
    tl, tr, br, bl = corners
    width = int(max(np.linalg.norm(tr - tl), np.linalg.norm(br - bl)))
    height = int(max(np.linalg.norm(bl - tl), np.linalg.norm(br - tr)))
    target = np.array([[0, 0], [width - 1, 0], [width - 1, height - 1], [0, height - 1]], dtype="float32")
    return cv2.warpPerspective(image, cv2.getPerspectiveTransform(corners, target), (width, height))


def resize(image: np.ndarray, profile: Profile) -> np.ndarray:
    h, w = image.shape[:2]
    if profile.card_shape:
        short = round(profile.long_side * CARD_RATIO)
        size = (short, profile.long_side) if h >= w else (profile.long_side, short)
    else:
        scale = profile.long_side / max(h, w)
        size = (round(w * scale), round(h * scale))
    return cv2.resize(image, size, interpolation=cv2.INTER_AREA)


def rotate(image: np.ndarray, degrees: int) -> np.ndarray:
    codes = {90: cv2.ROTATE_90_CLOCKWISE, 180: cv2.ROTATE_180, 270: cv2.ROTATE_90_COUNTERCLOCKWISE}
    return cv2.rotate(image, codes[degrees]) if degrees in codes else image


# ---------------------------------------------------------------- bookkeeping


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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
    parser.add_argument("folders", nargs="*", help="folders under resources/scans to process, e.g. to_boldly_go/cards (default: all)")
    parser.add_argument("--force", action="store_true", help="reprocess images that are already up to date")
    parser.add_argument("--detect", action="store_true", help="find and straighten the item in uncropped photos")
    args = parser.parse_args()

    manifest: dict = json.loads(MANIFEST.read_text()) if MANIFEST.exists() else {}
    images: dict[str, dict] = manifest.get("images", {})

    filters: list[Path] = []
    for folder in args.folders:
        path = (SCANS_DIR / folder).resolve()
        if not path.is_dir() or SCANS_DIR.resolve() not in path.parents:
            print(f"No such folder under {SCANS_DIR.relative_to(ROOT)}: {folder}", file=sys.stderr)
            return 1
        filters.append(path)

    # Resolve every id first, across all folders, so duplicates are always caught.
    mappings: dict[Path, dict[str, tuple[str, int]]] = {}
    by_id: dict[str, tuple[Source, int]] = {}
    skipped: list[str] = []
    duplicates: list[str] = []
    for source in find_sources():
        mapping = mappings.setdefault(source.path.parent, load_mapping(source.path.parent))
        found = id_for(source, mapping)
        if found is None:
            skipped.append(source.label)
            continue
        image_id, degrees = found
        if image_id in by_id:
            duplicates.append(f"  {image_id}: {by_id[image_id][0].label} and {source.label}")
            continue
        by_id[image_id] = (source, degrees)
    if duplicates:
        print("Each id may appear only once. Duplicates:\n" + "\n".join(duplicates), file=sys.stderr)
        return 1

    written = unchanged = moved = 0
    hashes: dict[Path, str] = {}

    for image_id, (source, degrees) in sorted(by_id.items(), key=lambda kv: kv[1][0].label):
        resolved = source.path.resolve()
        if filters and not any(f in resolved.parents for f in filters):
            continue
        profile = PROFILES.get(source.kind, DEFAULT_PROFILE)
        file = (source.folder / f"{image_id}.webp").as_posix()
        out = OUT_DIR / file
        source_hash = hashes.setdefault(source.path, file_hash(source.path))
        settings = f"v2:{profile}:{degrees}:{args.detect}:{source.page}"
        entry = images.get(image_id)

        if entry and entry.get("file") != file:
            # The scan moved folder. If nothing else changed, move its image; otherwise regenerate.
            old = OUT_DIR / entry["file"]
            if (not args.force and old.is_file() and entry.get("source_sha256") == source_hash
                    and entry.get("settings") == settings):
                out.parent.mkdir(parents=True, exist_ok=True)
                old.replace(out)
                entry.update(file=file, source=source.label)
                moved += 1
                print(f"moved {old.relative_to(ROOT)} -> {out.relative_to(ROOT)}")
                continue
            remove_output(entry["file"])

        if (not args.force and out.exists() and entry and entry.get("file") == file
                and entry.get("source_sha256") == source_hash and entry.get("settings") == settings):
            unchanged += 1
            continue

        image = load(source, profile)
        if image is None:
            print(f"Cannot read {source.label}", file=sys.stderr)
            return 1
        if args.detect:
            corners = find_outline(image)
            if corners is None:
                print(f"  no outline found in {source.label}; using the whole image")
            else:
                image = straighten(image, corners)
        image = resize(rotate(image, degrees), profile)

        out.parent.mkdir(parents=True, exist_ok=True)
        Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB)).save(out, "WEBP", quality=WEBP_QUALITY, method=6)
        images[image_id] = {
            "kind": source.kind,
            "file": file,
            "width": image.shape[1],
            "height": image.shape[0],
            "version": file_hash(out)[:12],
            "source": source.label,
            "source_sha256": source_hash,
            "settings": settings,
        }
        written += 1
        print(f"{source.label} -> {out.relative_to(ROOT)}")

    removed: list[str] = []
    if not filters:
        # Full run: forget images whose scan is gone, and delete stray output files.
        for image_id in sorted(set(images) - set(by_id)):
            remove_output(images.pop(image_id)["file"])
            removed.append(image_id)
        known = {entry["file"] for entry in images.values()}
        if OUT_DIR.exists():
            for stray in OUT_DIR.rglob("*.webp"):
                if stray.relative_to(OUT_DIR).as_posix() not in known:
                    stray.unlink()
                    removed.append(str(stray.relative_to(ROOT)))
            remove_empty_dirs(OUT_DIR)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps({"images": dict(sorted(images.items()))}, indent=2) + "\n")

    print(f"\nWrote {written} image(s), moved {moved}; {unchanged} already up to date.")
    if removed:
        print(f"\nRemoved {len(removed)} image(s) with no matching scan.")
    if skipped:
        print("\nSkipped, because no id was found in mapping.csv or the file name:")
        print("\n".join(f"  {p}" for p in skipped))
    return 0


if __name__ == "__main__":
    sys.exit(main())
