#!/usr/bin/env python3
"""Mirror verified GeoCenter-hosted 2025 publisher catalog PDFs locally and update cards."""
from pathlib import Path
from io import BytesIO
import re
import urllib.request
import fitz
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ITEMS = [
    {
        "name": "World for Kids", "match": "World for Kids",
        "url": "https://www.geocenter.de/_files/ugd/9fec19_de7deab24b854162b80df539e254a2d3.pdf?index=true",
        "pdf": "assets/catalogs/pdfs/world-for-kids-programm-2025.pdf",
        "cover": "assets/images/catalogs/world-for-kids-programm-2025.webp",
    },
    {
        "name": "Biber & Butzemann", "match": "Biber &amp; Butzemann",
        "url": "https://www.geocenter.de/_files/ugd/9fec19_772e427c76e343ea9e9f939bcc777fd9.pdf?index=true",
        "pdf": "assets/catalogs/pdfs/biber-butzemann-gesamtkatalog-2025.pdf",
        "cover": "assets/images/catalogs/biber-butzemann-gesamtkatalog-2025.webp",
    },
]

def get_file(url):
    request = urllib.request.Request(url, headers={"User-Agent": "GeoCenter website catalog migration/1.0"})
    with urllib.request.urlopen(request, timeout=90) as response:
        data = response.read(35_000_001)
        if len(data) > 35_000_000:
            raise RuntimeError("PDF exceeds 35MB")
        if not data.startswith(b"%PDF"):
            raise RuntimeError("Download is not a PDF")
    return data

def update_card(html, item):
    pattern = r'<a class="catalog-card"[^>]*><div class="catalog-cover">(?:(?!</a>).)*?<span class="catalog-meta-heading">' + re.escape(item["match"]) + r'</span>(?:(?!</a>).)*?</a>'
    matches = list(re.finditer(pattern, html, flags=re.DOTALL))
    if not matches:
        raise RuntimeError(f"No cards found for {item['name']}")
    for match in reversed(matches):
        old = match.group()
        new = re.sub(r'href="[^"]+"', f'href="./{item["pdf"]}"', old, count=1)
        new = re.sub(r'src="[^"]+"', f'src="./{item["cover"]}"', new, count=1)
        new = re.sub(r'alt="[^"]+"', f'alt="{item["name"]} Verlagskatalog 2025"', new, count=1)
        new = re.sub(r'<span class="catalog-label">[^<]*</span>', '<span class="catalog-label">Verlagskatalog 2025</span>', new, count=1)
        new = new.replace('Katalog anfragen →', 'Katalog ansehen →')
        if 'target="_blank"' not in new.split('>',1)[0]:
            new = new.replace('class="catalog-card"', 'class="catalog-card" target="_blank" rel="noopener"',1)
        html = html[:match.start()] + new + html[match.end():]
    return html

def main():
    data = []
    for item in ITEMS:
        content = get_file(item["url"])
        with fitz.open(stream=content, filetype="pdf") as doc:
            if not doc.page_count:
                raise RuntimeError("Empty PDF")
            page = doc[0]
            scale = min(1200 / page.rect.width, 1600 / page.rect.height)
            pix = page.get_pixmap(matrix=fitz.Matrix(scale, scale), alpha=False)
            image = Image.open(BytesIO(pix.tobytes("png"))).convert("RGB")
            cover_target = ROOT / item["cover"]
            cover_target.parent.mkdir(parents=True, exist_ok=True)
            image.save(cover_target, "WEBP", quality=85, method=6)
            print(f"{item['name']}: {doc.page_count} pages, {len(content)} PDF bytes")
        pdf_target = ROOT / item["pdf"]
        pdf_target.parent.mkdir(parents=True, exist_ok=True)
        pdf_target.write_bytes(content)
        data.append(item)
    file = ROOT / "programm.html"
    html = file.read_text(encoding="utf-8")
    for item in data:
        html = update_card(html, item)
    file.write_text(html, encoding="utf-8")

if __name__ == "__main__":
    main()
