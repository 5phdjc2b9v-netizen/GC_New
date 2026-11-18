#!/usr/bin/env python3
"""Create optimized catalog covers from the actual first page of the publisher PDF."""
from pathlib import Path
import fitz
from PIL import Image
from io import BytesIO

ROOT = Path(__file__).resolve().parents[1]
ITEMS = [
    ("assets/catalogs/pdfs/teneues-fruehjahr-2027.pdf",
     "assets/images/catalogs/teneues-fruehjahr-2027.webp"),
    ("assets/catalogs/pdfs/gestalten-fruehjahr-2027.pdf",
     "assets/images/catalogs/gestalten-fruehjahr-2027.webp"),
]

def create_cover(pdf_rel: str, image_rel: str) -> None:
    pdf = ROOT / pdf_rel
    dest = ROOT / image_rel
    if not pdf.is_file():
        raise FileNotFoundError(f"Missing source PDF: {pdf_rel}")
    with fitz.open(pdf) as doc:
        if not doc.page_count:
            raise ValueError(f"No pages in {pdf_rel}")
        page = doc[0]
        # Keep the actual first PDF page, without adding fictional book mockups.
        scale = min(1300 / page.rect.width, 1600 / page.rect.height)
        pix = page.get_pixmap(matrix=fitz.Matrix(scale, scale), alpha=False)
        image = Image.open(BytesIO(pix.tobytes("png"))).convert("RGB")
        dest.parent.mkdir(parents=True, exist_ok=True)
        image.save(dest, "WEBP", quality=86, method=6)
        print(f"{pdf_rel}: {doc.page_count} pages; cover {image.size}; {dest.stat().st_size} bytes")

if __name__ == "__main__":
    for source, target in ITEMS:
        create_cover(source, target)
