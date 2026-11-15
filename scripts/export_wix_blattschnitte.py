#!/usr/bin/env python3
"""Archive public Blattschnitt PDFs linked on GeoCenter's legacy Wix pages.
No automatic publication: results require a copyright/content review.
"""
import csv
import hashlib
import os
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

PAGES = ["https://www.geocenter.de/blattschnitte", "https://www.geocenter.de/programm"]
OUT = Path("blattschnitte-export")
OUT.mkdir(exist_ok=True)
session = requests.Session()
session.headers.update({"User-Agent": "GeoCenter-Blattschnitt-Migration/1.0"})
entries = {}

for page in PAGES:
    try:
        response = session.get(page, timeout=40)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        for a in soup.select("a[href]"):
            href = urljoin(page, a["href"])
            name = a.get_text(" ", strip=True)
            if ".pdf" not in urlparse(href).path.lower():
                continue
            if href not in entries:
                entries[href] = {"title": name, "source": page}
    except requests.RequestException as exc:
        print(f"PAGE ERROR {page}: {exc}")

with (OUT / "links.csv").open("w", newline="", encoding="utf-8-sig") as fh:
    writer = csv.writer(fh)
    writer.writerow(["Titel", "Quelle", "Original-URL", "Typ", "Dateiname", "Status"])
    for url, item in entries.items():
        host = urlparse(url).hostname or ""
        is_wix = host in ("www.geocenter.de", "geocenter.de", "static.wixstatic.com")
        filename = ""
        status = "Externer Link - nicht heruntergeladen"
        if is_wix:
            filename = hashlib.sha256(url.encode()).hexdigest()[:16] + ".pdf"
            path = OUT / filename
            try:
                with session.get(url, timeout=90, stream=True) as r:
                    r.raise_for_status()
                    if "pdf" not in r.headers.get("Content-Type", "").lower() and not urlparse(url).path.lower().endswith(".pdf"):
                        raise ValueError("Unexpected content type")
                    total = 0
                    with path.open("wb") as f:
                        for block in r.iter_content(1024 * 128):
                            total += len(block)
                            if total > 50 * 1024 * 1024:
                                raise ValueError("File larger than 50 MB")
                            f.write(block)
                if path.open("rb").read(5) != b"%PDF-":
                    raise ValueError("Not a valid PDF header")
                status = "PDF archiviert"
            except (requests.RequestException, OSError, ValueError) as exc:
                path.unlink(missing_ok=True)
                status = f"Fehler: {str(exc)[:150]}"
        writer.writerow([item["title"], item["source"], url, "Wix" if is_wix else "Extern", filename, status])
print(f"Extracted {len(entries)} unique PDF URLs")
