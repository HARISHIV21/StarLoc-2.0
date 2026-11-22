from pathlib import Path
import csv
import json
import numpy as np

from astropy.io import fits
from astropy.wcs import WCS
from astropy.coordinates import SkyCoord
from astropy import units as u

BASE = Path("research/real_image")
RESULTS = BASE / "results/ASK033"
SOLVE = RESULTS / "custom_plate_solutions"
CATALOGUE = Path("research/data/catalogue/hipparcos_positions_2026.csv")

WCS_FILE = SOLVE / "R2C2_custom.wcs"
XYLS_FILE = RESULTS / "custom_source_catalogues/R2C2_custom.xyls"

print("=" * 65)
print("STARLOC 2.0 — PHASE 33")
print("INDEPENDENT HIPPARCOS VALIDATION")
print("=" * 65)

for path in (WCS_FILE, XYLS_FILE, CATALOGUE):
    if not path.exists():
        raise FileNotFoundError(path)

# Read WCS solution.
with fits.open(WCS_FILE) as hdul:
    wcs = WCS(hdul[0].header).celestial

# Read source coordinates from the exact FITS catalogue used in Phase 32.
with fits.open(XYLS_FILE) as hdul:
    sources = hdul[1].data
    x = np.asarray(sources["X"], dtype=float)
    y = np.asarray(sources["Y"], dtype=float)

ra_image, dec_image = wcs.all_pix2world(x, y, 1)

image_coords = SkyCoord(
    ra=ra_image * u.deg,
    dec=dec_image * u.deg,
    frame="icrs"
)

# Load the propagated Hipparcos catalogue.
with CATALOGUE.open(newline="") as f:
    reader = csv.DictReader(f)
    rows = list(reader)
    fields = reader.fieldnames

print("\nHipparcos columns:", fields)

def find_column(names):
    lower = {name.lower(): name for name in fields}
    for name in names:
        if name.lower() in lower:
            return lower[name.lower()]
    return None

ra_col = find_column(["ra_2026_deg", "ra_deg", "ra"])
dec_col = find_column(["dec_2026_deg", "dec_deg", "dec"])
hip_col = find_column(["hip_number", "hip", "hip_id"])
mag_col = find_column(["vmag", "magnitude", "mag"])

if not ra_col or not dec_col:
    raise RuntimeError(
        "Could not identify RA/Dec columns. Found: " + str(fields)
    )

valid_rows = []
cat_ra = []
cat_dec = []

for row in rows:
    try:
        ra = float(row[ra_col])
        dec = float(row[dec_col])
        if np.isfinite(ra) and np.isfinite(dec):
            valid_rows.append(row)
            cat_ra.append(ra)
            cat_dec.append(dec)
    except (ValueError, TypeError, KeyError):
        continue

catalogue_coords = SkyCoord(
    ra=np.asarray(cat_ra) * u.deg,
    dec=np.asarray(cat_dec) * u.deg,
    frame="icrs"
)

indices, separations, _ = image_coords.match_to_catalog_sky(
    catalogue_coords
)

separation_arcmin = separations.arcmin
separation_deg = separations.deg

# Report several thresholds; do not assume every nearest neighbour is real.
thresholds_arcmin = [2, 5, 10, 20, 30]

matches = []
for i, (j, sep) in enumerate(zip(indices, separation_arcmin)):
    row = valid_rows[int(j)]
    matches.append({
        "source_number": i + 1,
        "x_pixel": float(x[i]),
        "y_pixel": float(y[i]),
        "wcs_ra_deg": float(ra_image[i]),
        "wcs_dec_deg": float(dec_image[i]),
        "nearest_hip_id": row.get(hip_col, "") if hip_col else "",
        "catalogue_ra_deg": float(cat_ra[j]),
        "catalogue_dec_deg": float(cat_dec[j]),
        "catalogue_magnitude": row.get(mag_col, "") if mag_col else "",
        "separation_arcmin": float(sep)
    })

match_path = RESULTS / "phase33_hipparcos_crossmatches.csv"
with match_path.open("w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=list(matches[0].keys()))
    writer.writeheader()
    writer.writerows(matches)

report = {
    "phase": 33,
    "section": "R2C2",
    "wcs_file": str(WCS_FILE),
    "hipparcos_catalogue": str(CATALOGUE),
    "image_sources": int(len(x)),
    "catalogue_rows": int(len(valid_rows)),
    "field_centre_ra_deg": float(np.mean(ra_image)),
    "field_centre_dec_deg": float(np.mean(dec_image)),
    "nearest_neighbour_median_arcmin": float(np.median(separation_arcmin)),
    "nearest_neighbour_mean_arcmin": float(np.mean(separation_arcmin)),
    "nearest_neighbour_max_arcmin": float(np.max(separation_arcmin)),
    "matches_within_threshold": {
        str(t): int(np.sum(separation_arcmin <= t))
        for t in thresholds_arcmin
    },
    "interpretation": (
        "Nearest-neighbour catalogue comparison only. "
        "Threshold counts must be assessed before accepting the WCS."
    )
}

report_path = BASE / "phase33_hipparcos_validation.json"
report_path.write_text(json.dumps(report, indent=2))

print("\nVALIDATION RESULTS")
print("Image sources:", len(x))
print("Hipparcos catalogue rows:", len(valid_rows))
print("Median nearest separation:",
      round(float(np.median(separation_arcmin)), 3), "arcmin")
print("Mean nearest separation:",
      round(float(np.mean(separation_arcmin)), 3), "arcmin")
print("Maximum nearest separation:",
      round(float(np.max(separation_arcmin)), 3), "arcmin")

print("\nMATCH COUNTS")
for threshold in thresholds_arcmin:
    print(
        f"Within {threshold:>2} arcmin:",
        int(np.sum(separation_arcmin <= threshold))
    )

print("\nFirst 10 matches")
for item in matches[:10]:
    print(
        item["source_number"],
        "HIP", item["nearest_hip_id"],
        "separation", round(item["separation_arcmin"], 2), "arcmin"
    )

print("\nSaved:", match_path)
print("Saved:", report_path)
print("\nPHASE 33 COMPLETE")
