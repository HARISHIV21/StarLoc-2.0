from pathlib import Path
import csv
import json
import numpy as np

from astropy.io import fits
from astropy.wcs import WCS
from astropy.coordinates import SkyCoord
from astropy import units as u
from scipy.optimize import linear_sum_assignment

BASE = Path("research/real_image")
RESULTS = BASE / "results/ASK033"

WCS_FILE = RESULTS / "custom_plate_solutions/R2C2_custom.wcs"
XYLS_FILE = RESULTS / "custom_source_catalogues/R2C2_custom.xyls"
CATALOGUE = Path("research/data/catalogue/hipparcos_positions_2026.csv")

print("=" * 65)
print("STARLOC 2.0 — PHASE 34")
print("ONE-TO-ONE HIPPARCOS VALIDATION")
print("=" * 65)

with fits.open(WCS_FILE) as hdul:
    wcs = WCS(hdul[0].header).celestial

with fits.open(XYLS_FILE) as hdul:
    data = hdul[1].data
    x = np.asarray(data["X"], dtype=float)
    y = np.asarray(data["Y"], dtype=float)

ra, dec = wcs.all_pix2world(x, y, 1)
image_sky = SkyCoord(ra=ra*u.deg, dec=dec*u.deg, frame="icrs")

with CATALOGUE.open(newline="") as f:
    reader = csv.DictReader(f)
    rows = list(reader)
    columns = reader.fieldnames

def col(options):
    lookup = {c.lower(): c for c in columns}
    for option in options:
        if option.lower() in lookup:
            return lookup[option.lower()]
    return None

ra_col = col(["ra_2026_deg", "ra_deg", "ra"])
dec_col = col(["dec_2026_deg", "dec_deg", "dec"])
hip_col = col(["hip_number", "hip", "hip_id"])
mag_col = col(["vmag", "magnitude", "mag"])

if not ra_col or not dec_col:
    raise RuntimeError("Hipparcos RA/Dec columns not found")

valid_rows, cat_ra, cat_dec = [], [], []

for row in rows:
    try:
        r, d = float(row[ra_col]), float(row[dec_col])
        if np.isfinite(r) and np.isfinite(d):
            valid_rows.append(row)
            cat_ra.append(r)
            cat_dec.append(d)
    except (ValueError, TypeError):
        continue

catalogue_sky = SkyCoord(
    ra=np.asarray(cat_ra)*u.deg,
    dec=np.asarray(cat_dec)*u.deg,
    frame="icrs"
)

# Full angular separation matrix: image detections x Hipparcos stars.
print("\nCalculating angular separation matrix...")
separation = image_sky[:, None].separation(catalogue_sky[None, :])
sep_arcmin = separation.to_value(u.arcmin)

nearest = np.min(sep_arcmin, axis=1)
thresholds = [2, 5, 10, 20]
summary = {}

for threshold in thresholds:
    n_image, n_catalogue = sep_arcmin.shape

    # Dummy columns allow image detections to remain unmatched.
    unmatched_cost = threshold
    invalid_cost = threshold + 100000.0

    real_cost = np.where(
        sep_arcmin <= threshold,
        sep_arcmin,
        invalid_cost
    )
    dummy_cost = np.full((n_image, n_image), unmatched_cost)
    cost = np.hstack([real_cost, dummy_cost])

    image_indices, assigned_indices = linear_sum_assignment(cost)

    accepted = []
    for i, j in zip(image_indices, assigned_indices):
        if j < n_catalogue and sep_arcmin[i, j] <= threshold:
            accepted.append((int(i), int(j), float(sep_arcmin[i, j])))

    residuals = [item[2] for item in accepted]
    summary[str(threshold)] = {
        "unique_matches": len(accepted),
        "unmatched_image_sources": n_image - len(accepted),
        "median_separation_arcmin": (
            float(np.median(residuals)) if residuals else None
        ),
        "mean_separation_arcmin": (
            float(np.mean(residuals)) if residuals else None
        ),
        "maximum_separation_arcmin": (
            float(np.max(residuals)) if residuals else None
        ),
        "matches": accepted
    }

    print(
        f"\nThreshold {threshold:>2} arcmin:",
        len(accepted), "unique matches;",
        n_image - len(accepted), "unmatched"
    )

    if residuals:
        print(
            "  Median:", round(float(np.median(residuals)), 3),
            "arcmin | Mean:", round(float(np.mean(residuals)), 3),
            "arcmin"
        )

# Save the strictest useful assignment (10 arcmin) for inspection.
selected = summary["10"]["matches"]
output_rows = []

for image_i, catalogue_i, sep in selected:
    star = valid_rows[catalogue_i]
    output_rows.append({
        "source_number": image_i + 1,
        "x_pixel": float(x[image_i]),
        "y_pixel": float(y[image_i]),
        "wcs_ra_deg": float(ra[image_i]),
        "wcs_dec_deg": float(dec[image_i]),
        "hip_id": star.get(hip_col, "") if hip_col else "",
        "catalogue_ra_deg": float(cat_ra[catalogue_i]),
        "catalogue_dec_deg": float(cat_dec[catalogue_i]),
        "magnitude": star.get(mag_col, "") if mag_col else "",
        "separation_arcmin": sep,
        "separation_pixels": sep / (251.247 / 60.0)
    })

csv_path = RESULTS / "phase34_unique_hipparcos_matches.csv"
if output_rows:
    with csv_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(output_rows[0].keys()))
        writer.writeheader()
        writer.writerows(output_rows)

report = {
    "phase": 34,
    "section": "R2C2",
    "method": "Hungarian one-to-one assignment with angular gates",
    "image_sources": int(len(x)),
    "hipparcos_catalogue_rows": int(len(valid_rows)),
    "plate_scale_arcsec_per_pixel": 251.247,
    "nearest_neighbour_median_arcmin": float(np.median(nearest)),
    "nearest_neighbour_mean_arcmin": float(np.mean(nearest)),
    "threshold_results": {
        key: {k: v for k, v in value.items() if k != "matches"}
        for key, value in summary.items()
    },
    "unique_matches_at_10_arcmin": len(selected),
    "matches_csv": str(csv_path)
}

report_path = BASE / "phase34_one_to_one_validation.json"
report_path.write_text(json.dumps(report, indent=2))

print("\nSaved:", csv_path)
print("Saved:", report_path)
print("\nPHASE 34 COMPLETE")
