#!/usr/bin/env python3
"""Mirror public GeoCenter Blattschnitt PDFs from the legacy Wix site.

The generated PDFs and manifest are written into the relaunch site so the new
website no longer depends on Wix for these downloads.
"""
import csv
import json
import re
import shutil
import unicodedata
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

PAGES = ["https://www.geocenter.de/blattschnitte", "https://www.geocenter.de/programm"]
DOWNLOAD_ROOT = Path("assets/downloads/blattschnitte")
DATA_ROOT = Path("assets/data")
EXPORT_ROOT = Path("blattschnitte-export")
WORLD_PREFIXES = (
    "Australien ", "Himalaya ", "Indien ", "Karakoram ", "Marokko ",
    "Nepal ", "Neuseeland ", "Welt "
)

session = requests.Session()
session.headers.update({"User-Agent": "GeoCenter-Blattschnitt-Migration/2.0"})


def slugify(value: str) -> str:
    value = unicodedata.normalize("NFKD", value)
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    value = value.lower().replace("ß", "ss")
    value = re.sub(r"[^a-z0-9]+", "-", value).strip("-")
    return value[:120] or "blattschnitt"


def category_for(title: str) -> str:
    clean = " ".join(title.split())
    if clean.startswith("Deutschland "):
        return "Deutschland"
    if clean.startswith(WORLD_PREFIXES):
        return "Welt"
    return "Europa"


if DOWNLOAD_ROOT.exists():
    shutil.rmtree(DOWNLOAD_ROOT)
DOWNLOAD_ROOT.mkdir(parents=True, exist_ok=True)
DATA_ROOT.mkdir(parents=True, exist_ok=True)
EXPORT_ROOT.mkdir(exist_ok=True)

entries = {}
for page in PAGES:
    response = session.get(page, timeout=40)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    for a in soup.select("a[href]"):
        href = urljoin(page, a["href"])
        title = " ".join(a.get_text(" ", strip=True).split())
        if ".pdf" not in urlparse(href).path.lower() or not title:
            continue
        entries.setdefault(href, {"title": title, "source": page})

manifest = []
rows = []
used_paths = set()

for url, item in entries.items():
    host = (urlparse(url).hostname or "").lower()
    is_wix = host in {"www.geocenter.de", "geocenter.de", "static.wixstatic.com"}
    status = "Externer Link - nicht gespiegelt"
    local_href = ""
    local_name = ""

    if is_wix:
        category = category_for(item["title"])
        folder = DOWNLOAD_ROOT / {"Deutschland": "deutschland", "Europa": "europa", "Welt": "welt"}[category]
        folder.mkdir(parents=True, exist_ok=True)

        base = slugify(item["title"])
        candidate = folder / f"{base}.pdf"
        suffix = 2
        while candidate.as_posix() in used_paths:
            candidate = folder / f"{base}-{suffix}.pdf"
            suffix += 1
        used_paths.add(candidate.as_posix())

        try:
            with session.get(url, timeout=90, stream=True) as response:
                response.raise_for_status()
                total = 0
                with candidate.open("wb") as fh:
                    for block in response.iter_content(1024 * 128):
                        if not block:
                            continue
                        total += len(block)
                        if total > 50 * 1024 * 1024:
                            raise ValueError("File larger than 50 MB")
                        fh.write(block)
            if candidate.open("rb").read(5) != b"%PDF-":
                raise ValueError("Not a valid PDF header")
            status = "PDF gespiegelt"
            local_name = candidate.name
            local_href = "./" + candidate.as_posix()
            manifest.append({
                "title": item["title"],
                "category": category,
                "href": local_href,
                "source": item["source"],
                "original_url": url,
            })
        except (requests.RequestException, OSError, ValueError) as exc:
            candidate.unlink(missing_ok=True)
            status = f"Fehler: {str(exc)[:150]}"

    rows.append([
        item["title"], item["source"], url,
        "Wix" if is_wix else "Extern", local_name, status
    ])

manifest.sort(key=lambda x: ({"Deutschland": 0, "Europa": 1, "Welt": 2}[x["category"]], x["title"].lower()))
(DATA_ROOT / "blattschnitte.json").write_text(
    json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
)

with (EXPORT_ROOT / "links.csv").open("w", newline="", encoding="utf-8-sig") as fh:
    writer = csv.writer(fh)
    writer.writerow(["Titel", "Quelle", "Original-URL", "Typ", "Dateiname", "Status"])
    writer.writerows(rows)

print(f"Found {len(entries)} PDF links; mirrored {len(manifest)} Wix PDFs")
