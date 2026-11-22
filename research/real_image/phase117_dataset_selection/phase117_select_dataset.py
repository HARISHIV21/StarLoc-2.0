from pathlib import Path
from astropy.table import Table
import urllib.request
import json

OUT = Path("research/real_image/phase117_dataset_selection")
OUT.mkdir(parents=True, exist_ok=True)

url = "https://www.igapsimages.org/data/images/igaps-images.fits.gz"
metadata_file = OUT / "igaps-images.fits.gz"

if not metadata_file.exists():
    print("Downloading IGAPS observation metadata...")
    request = urllib.request.Request(
        url, headers={"User-Agent": "StarLoc2.0 research project"}
    )
    with urllib.request.urlopen(request, timeout=180) as response:
        metadata_file.write_bytes(response.read())

print("Reading metadata table...")
table = Table.read(metadata_file)

print("\nAvailable metadata columns:")
print(", ".join(table.colnames))

def value(row, key, default=None):
    if key not in table.colnames:
        return default
    item = row[key]
    if getattr(item, "mask", False):
        return default
    return item.item() if hasattr(item, "item") else item

def text(row, key):
    v = value(row, key, "")
    return str(v).strip()

candidates = []

for row in table:
    band = text(row, "band").lower()
    grade = text(row, "qcgrade").upper()
    calibrated = value(row, "2020", value(row, "calibrated", False))
    seeing = value(row, "seeing")
    exposure = value(row, "exptime")
    depth = value(row, "depth")
    url_value = text(row, "url")

    if band not in ("r", "i", "g"):
        continue
    if grade not in ("A++", "A+", "A"):
        continue
    if seeing is None or not (0 < float(seeing) <= 1.8):
        continue
    if exposure is None or not (5 <= float(exposure) <= 120):
        continue
    if not url_value:
        continue

    candidates.append({
        "run": int(value(row, "run")),
        "ccd": int(value(row, "ccd")),
        "band": band,
        "grade": grade,
        "ra_deg": float(value(row, "ra")),
        "dec_deg": float(value(row, "dec")),
        "utc_start": text(row, "utstart"),
        "exposure_s": float(exposure),
        "seeing_arcsec": float(seeing),
        "depth_mag": float(depth) if depth is not None else None,
        "url": url_value,
        "calibrated_flag": str(calibrated),
        "fieldid": text(row, "fieldid"),
    })

candidates.sort(
    key=lambda x: (
        {"A++": 0, "A+": 1, "A": 2}[x["grade"]],
        x["seeing_arcsec"],
        -(x["depth_mag"] or 0),
    )
)

# Keep a manageable shortlist, with different sky fields where possible.
shortlist = []
seen_fields = set()
for item in candidates:
    field = item["fieldid"] or f'{item["ra_deg"]:.3f}_{item["dec_deg"]:.3f}'
    if field in seen_fields:
        continue
    shortlist.append(item)
    seen_fields.add(field)
    if len(shortlist) == 20:
        break

report = {
    "source": "IGAPS / Isaac Newton Telescope Wide Field Camera",
    "metadata_url": url,
    "metadata_rows": len(table),
    "filtered_candidate_count": len(candidates),
    "shortlist": shortlist,
    "selection_note": (
        "Pipeline-reduced survey images with pre-existing astrometric WCS. "
        "StarLoc must perform its own detection, catalogue matching and "
        "calibration. Existing WCS is reserved for independent comparison."
    ),
}

(OUT / "phase117_candidate_shortlist.json").write_text(
    json.dumps(report, indent=2), encoding="utf-8"
)

print(f"\nTotal metadata rows: {len(table)}")
print(f"High-quality candidates: {len(candidates)}")
print("\nTOP 20 CANDIDATES")
print("-" * 110)

for i, item in enumerate(shortlist, 1):
    print(
        f'{i:02d}. Run {item["run"]}-{item["ccd"]} | '
        f'{item["band"]}-band | {item["grade"]} | '
        f'seeing {item["seeing_arcsec"]:.2f}" | '
        f'exposure {item["exposure_s"]:.1f}s | '
        f'RA {item["ra_deg"]:.5f} Dec {item["dec_deg"]:.5f} | '
        f'UTC {item["utc_start"]}'
    )
    print(f'    {item["url"]}')

print("\nSaved:")
print(OUT / "phase117_candidate_shortlist.json")
print("\nNo image has been selected or downloaded yet.")
