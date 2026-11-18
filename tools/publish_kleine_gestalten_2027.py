#!/usr/bin/env python3
"""Publish the supplied Kleine gestalten spring 2027 PDF after it is uploaded to the website branch."""
from pathlib import Path
from io import BytesIO
import re
import fitz
from PIL import Image

root = Path(__file__).resolve().parents[1]
source = root / "assets/catalogs/pdfs/kleine-gestalten-fruehjahr-2027.pdf"
cover = root / "assets/images/catalogs/kleine-gestalten-fruehjahr-2027.webp"
page = root / "programm.html"
if not source.is_file():
    raise SystemExit("Upload assets/catalogs/pdfs/kleine-gestalten-fruehjahr-2027.pdf first")
with fitz.open(source) as pdf:
    if pdf.page_count < 1:
        raise SystemExit("Empty PDF")
    p = pdf[0]
    scale = min(1300 / p.rect.width, 1600 / p.rect.height)
    pix = p.get_pixmap(matrix=fitz.Matrix(scale, scale), alpha=False)
    im = Image.open(BytesIO(pix.tobytes("png"))).convert("RGB")
    cover.parent.mkdir(parents=True, exist_ok=True)
    im.save(cover, "WEBP", quality=84, method=6)
html = page.read_text(encoding="utf-8")
pattern = r'<a class="catalog-card"[^>]*><div class="catalog-cover">(?:(?!</a>).)*?<h3>Kleine gestalten</h3>(?:(?!</a>).)*?</a>'
matches = list(re.finditer(pattern, html, re.DOTALL))
if len(matches) != 1:
    raise SystemExit(f"Expected exactly one Kleine gestalten card, got {len(matches)}")
old = matches[0].group(0)
new = re.sub(r'href="[^"]+"', 'href="./assets/catalogs/pdfs/kleine-gestalten-fruehjahr-2027.pdf"', old, count=1)
new = re.sub(r'src="[^"]+"', 'src="./assets/images/catalogs/kleine-gestalten-fruehjahr-2027.webp"', new, count=1)
new = re.sub(r'alt="[^"]+"', 'alt="Kleine gestalten Verlagskatalog Frühjahr 2027"', new, count=1)
new = new.replace('Verlagskatalog Herbst 2026', 'Verlagskatalog Frühjahr 2027').replace('Katalog ansehen →', 'Katalog Frühjahr 2027 ansehen →')
new = new.replace('href="./assets/catalogs/pdfs/kleine-gestalten-fruehjahr-2027.pdf"', 'href="./assets/catalogs/pdfs/kleine-gestalten-fruehjahr-2027.pdf" target="_blank" rel="noopener"', 1)
page.write_text(html[:matches[0].start()] + new + html[matches[0].end():], encoding="utf-8")
print(f"Updated Kleine gestalten card; {source.stat().st_size} PDF bytes, {cover.stat().st_size} WebP bytes")
