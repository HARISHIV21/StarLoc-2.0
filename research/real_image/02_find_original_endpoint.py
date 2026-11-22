from pathlib import Path
from urllib.parse import urljoin
import re
import json

OUT = Path("research/real_image/data/network/ASK033")
html = (OUT / "camera_page.html").read_text(
    encoding="utf-8", errors="replace"
)

patterns = [
    r"""https?://[^"'<> ]+""",
    r"""(?:src|href|data-src|data-image|data-url)\s*=\s*["']([^"']+)""",
    r"""imageProxy\.php[^"'<> ]*""",
    r"""(?:image\.jpg|last\.jpg|latest\.jpg|archive\.php)[^"'<> ]*""",
    r"""(?:liveImage|live_image|cameraImage|archive|imageProxy)[^;\n]{0,220}""",
]

found = []
for pattern in patterns:
    for match in re.finditer(pattern, html, re.IGNORECASE):
        value = match.group(1) if match.lastindex else match.group(0)
        value = value.replace("&amp;", "&")
        full = urljoin(
            "https://allskykamera.space/kamera.php?k=ASK033&lang=en",
            value
        )
        if full not in found:
            found.append(full)

print("\nSTARLOC — ORIGINAL IMAGE ENDPOINT SEARCH")
print("=" * 60)

for value in found:
    if re.search(
        r"imageProxy|image\.jpg|last\.jpg|latest\.jpg|archive|\.jpe?g|\.png",
        value,
        re.IGNORECASE
    ):
        print(value)

print("\nRELEVANT HTML CONTEXT")
for term in ("imageProxy", "image.jpg", "last.jpg", "archive", "live image"):
    positions = [m.start() for m in re.finditer(term, html, re.IGNORECASE)]
    print("\n---", term, "matches:", len(positions), "---")
    for pos in positions[:4]:
        print(html[max(0, pos-250):min(len(html), pos+500)])
        print()

(OUT / "endpoint_candidates.json").write_text(
    json.dumps(found, indent=2), encoding="utf-8"
)
print("\nSaved endpoint candidates.")
