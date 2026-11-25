#!/usr/bin/env python3
"""Render the first page of the Kleine gestalten 2027 catalog as its web cover."""
from pathlib import Path
from io import BytesIO
import fitz
from PIL import Image

root = Path(__file__).resolve().parents[1]
source = root / "assets/catalogs/pdfs/kleine-gestalten-fruehjahr-2027.pdf"
cover = root / "assets/images/catalogs/kleine-gestalten-fruehjahr-2027.webp"
if not source.is_file():
    raise SystemExit("Missing Kleine gestalten source PDF")
with fitz.open(source) as pdf:
    if not pdf.page_count:
        raise SystemExit("Empty PDF")
    page = pdf[0]
    scale = min(1300 / page.rect.width, 1600 / page.rect.height)
    pix = page.get_pixmap(matrix=fitz.Matrix(scale, scale), alpha=False)
    image = Image.open(BytesIO(pix.tobytes("png"))).convert("RGB")
    cover.parent.mkdir(parents=True, exist_ok=True)
    image.save(cover, "WEBP", quality=85, method=6)
    print(f"Generated {cover}: {cover.stat().st_size} bytes")
