#!/usr/bin/env python3
"""Optimize eight oversized GeoCenter site images into WebP and update asset links."""
from pathlib import Path
from PIL import Image, ImageOps
ROOT = Path(__file__).resolve().parent.parent
ASSETS = [
  "assets/images/trade/boutique-coffee-table.jpg",
  "assets/images/coffee/rolex-2026.png",
  "assets/images/coffee/pop.png",
  "assets/images/catalogs/naturzeit-2026.png",
  "assets/images/catalogs/gestalten-herbst-2026.png",
  "assets/images/catalogs/biber-butzemann-2026.png",
  "assets/images/catalogs/kleine-gestalten-herbst-2026.png",
  "assets/images/about/frankfurt-book-fair-exterior.jpg",
]
changes = {}
for src_rel in ASSETS:
    src = ROOT / src_rel
    if not src.is_file():
        raise FileNotFoundError(src_rel)
    dst = src.with_suffix(".webp")
    with Image.open(src) as loaded:
        img = ImageOps.exif_transpose(loaded)
        if max(img.size) > 2600:
            img.thumbnail((2600, 2600), Image.Resampling.LANCZOS)
        if "A" in img.getbands() or "transparency" in img.info:
            img = img.convert("RGBA")
        else:
            img = img.convert("RGB")
        img.save(dst, "WEBP", quality=84, method=6)
    before = src.stat().st_size
    after = dst.stat().st_size
    if after >= before:
        dst.unlink()
        print(f"Keeping original; not smaller: {src_rel} ({before} -> {after})")
    else:
        changes[src_rel] = dst.relative_to(ROOT).as_posix()
        print(f"Optimized {src_rel}: {before} -> {after} bytes")
if not changes:
    print("No images improved.")
else:
    updated_files = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in {".html", ".css", ".js"}:
            continue
        if ".git" in path.parts or "node_modules" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        new_text = text
        for src_rel, dst_rel in changes.items():
            new_text = new_text.replace(src_rel, dst_rel)
        if new_text != text:
            path.write_text(new_text, encoding="utf-8")
            updated_files.append(str(path.relative_to(ROOT)))
    print("Updated references in", len(updated_files), "files")
