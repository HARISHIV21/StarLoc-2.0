from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urljoin
import re
import json

OUT = Path("research/real_image/data/network/ASK033")
PAGE_FILE = OUT / "camera_page.html"
BASE = "https://allskykamera.space/kamera.php?k=ASK033&lang=en"

if not PAGE_FILE.exists():
    raise SystemExit("Saved camera page not found: " + str(PAGE_FILE))

html = PAGE_FILE.read_text(encoding="utf-8", errors="replace")

class Parser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.items = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        for key in ("src", "href", "data-src", "data-original", "content"):
            value = attrs.get(key)
            if value:
                self.items.append({
                    "tag": tag,
                    "attribute": key,
                    "url": urljoin(BASE, value)
                })

parser = Parser()
parser.feed(html)

metadata = {
    "camera_id": "ASK033",
    "location": "Miesenbach, Austria",
    "latitude": 47.834,
    "longitude": 16.005,
    "timezone": "Europe/Vienna",
    "source_page": BASE
}

patterns = {
    "camera_name": r"Camera name:\s*([^<\n]+)",
    "camera_id": r"Camera ID:\s*(ASK\d+)",
    "latitude": r"Latitude:\s*(-?\d+(?:\.\d+)?)",
    "longitude": r"Longitude:\s*(-?\d+(?:\.\d+)?)",
    "timezone": r"Timezone:\s*([^<\n]+)",
    "local_time": r"Local time\s*([^<\n]+)"
}

for key, pattern in patterns.items():
    match = re.search(pattern, html, re.IGNORECASE)
    if match:
        metadata[key] = match.group(1).strip()

image_items = []
for item in parser.items:
    url = item["url"]
    if re.search(r"\.(jpg|jpeg|png|webp)(?:[?#]|$)", url, re.I):
        image_items.append(item)

unique = []
seen = set()
for item in image_items:
    if item["url"] not in seen:
        unique.append(item)
        seen.add(item["url"])

# Preserve archive and camera-related links as well.
related = [
    item for item in parser.items
    if re.search(r"archive|image|keogram|startrail|kamera|video", item["url"], re.I)
]

(OUT / "camera_metadata.json").write_text(
    json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8"
)
(OUT / "discovered_image_urls.json").write_text(
    json.dumps(unique, indent=2, ensure_ascii=False), encoding="utf-8"
)
(OUT / "discovered_related_urls.json").write_text(
    json.dumps(related, indent=2, ensure_ascii=False), encoding="utf-8"
)

print("\nSTARLOC 2.0 — ASK033 PAGE INSPECTION")
print("=" * 55)
print("\nCAMERA METADATA")
print(json.dumps(metadata, indent=2, ensure_ascii=False))

print("\nIMAGE URLS FOUND:", len(unique))
for item in unique[:40]:
    print(item["url"])

print("\nARCHIVE / RELATED LINKS:", len(related))
for item in related[:50]:
    print(item["url"])

print("\nSaved inspection results to:", OUT.resolve())
print("INSPECTION COMPLETE")
