from pathlib import Path
import csv
import json
import warnings
import numpy as np
import cv2

from astropy.io import fits
from astropy.wcs import WCS
from astropy.coordinates import SkyCoord
from astropy import units as u
from astropy.wcs import FITSFixedWarning
from astropy.wcs.wcs import NoConvergence
from scipy.optimize import linear_sum_assignment

warnings.simplefilter("ignore", FITSFixedWarning)

BASE = Path("research/real_image")
RESULTS = BASE / "results/ASK033"

IMAGE = RESULTS / "ASK033_section_R2C2.jpg"
WCS_FILE = RESULTS / "custom_plate_solutions/R2C2_custom.wcs"
XYLS_FILE = RESULTS / "custom_source_catalogues/R2C2_custom.xyls"
CATALOGUE = Path("research/data/catalogue/hipparcos_positions_2026.csv")

print("=" * 65)
print("STARLOC 2.0 — PHASE 35 CORRECTED")
print("VISUAL WCS AND PIXEL-SPACE VALIDATION")
print("=" * 65)

for p in [IMAGE, WCS_FILE, XYLS_FILE, CATALOGUE]:
    if not p.exists():
        raise FileNotFoundError(p)

image = cv2.imread(str(IMAGE))
if image is None:
    raise RuntimeError("Could not load R2C2 image")

height, width = image.shape[:2]

with fits.open(WCS_FILE) as hdul:
    wcs = WCS(hdul[0].header).celestial

with fits.open(XYLS_FILE) as hdul:
    sources = hdul[1].data
    x_detected = np.asarray(sources["X"], dtype=float)
    y_detected = np.asarray(sources["Y"], dtype=float)

with CATALOGUE.open(newline="") as f:
    catalogue = list(csv.DictReader(f))

hip_ids, ra_all, dec_all, mags_all = [], [], [], []

for row in catalogue:
    try:
        ra = float(row["ra_2026_deg"])
        dec = float(row["dec_2026_deg"])
        mag = float(row["vmag"])
        if np.isfinite(ra) and np.isfinite(dec):
            hip_ids.append(row["hip_number"])
            ra_all.append(ra)
            dec_all.append(dec)
            mags_all.append(mag)
    except (ValueError, TypeError, KeyError):
        continue

ra_all = np.asarray(ra_all)
dec_all = np.asarray(dec_all)
mags_all = np.asarray(mags_all)

# First restrict stars to the neighbourhood of the WCS field centre.
centre = SkyCoord(
    ra=float(wcs.wcs.crval[0]) * u.deg,
    dec=float(wcs.wcs.crval[1]) * u.deg,
    frame="icrs"
)
all_sky = SkyCoord(
    ra=ra_all * u.deg,
    dec=dec_all * u.deg,
    frame="icrs"
)

angular_distance = centre.separation(all_sky).deg
nearby = angular_distance <= 30.0

ra_near = ra_all[nearby]
dec_near = dec_all[nearby]
mag_near = mags_all[nearby]
hip_near = np.asarray(hip_ids)[nearby]

print("\nHipparcos catalogue rows:", len(ra_all))
print("Stars within 30 degrees of field centre:", len(ra_near))

# Project stars individually so one divergent point cannot abort the run.
projected = []

for i, (ra, dec) in enumerate(zip(ra_near, dec_near)):
    try:
        px, py = wcs.all_world2pix(float(ra), float(dec), 1)
        px, py = float(px), float(py)

        if (
            np.isfinite(px) and np.isfinite(py)
            and 1 <= px <= width
            and 1 <= py <= height
        ):
            projected.append((i, px, py))
    except (NoConvergence, ValueError, RuntimeError):
        continue

if not projected:
    raise RuntimeError("No catalogue stars projected inside R2C2")

cat_indices = np.array([p[0] for p in projected], dtype=int)
px = np.array([p[1] for p in projected])
py = np.array([p[2] for p in projected])

print("Successfully projected inside image:", len(px))
print("Detected image candidates:", len(x_detected))

# One-to-one pixel-space assignment.
distance = np.sqrt(
    (px[:, None] - x_detected[None, :]) ** 2
    + (py[:, None] - y_detected[None, :]) ** 2
)

thresholds = [1.0, 2.0, 3.0, 5.0]
summary = {}
assignments = {}

for threshold in thresholds:
    n_cat, n_det = distance.shape

    cost = np.hstack([
        np.where(distance <= threshold, distance, threshold + 1e6),
        np.full((n_cat, n_cat), threshold)
    ])

    rows, cols = linear_sum_assignment(cost)
    accepted = []

    for i, j in zip(rows, cols):
        if j < n_det and distance[i, j] <= threshold:
            accepted.append((int(i), int(j), float(distance[i, j])))

    residuals = [m[2] for m in accepted]
    assignments[threshold] = accepted

    summary[str(threshold)] = {
        "unique_matches": len(accepted),
        "median_pixel_residual": (
            float(np.median(residuals)) if residuals else None
        ),
        "mean_pixel_residual": (
            float(np.mean(residuals)) if residuals else None
        ),
        "maximum_pixel_residual": (
            float(np.max(residuals)) if residuals else None
        )
    }

    print(
        f"\nWithin {threshold:.1f} pixels:",
        len(accepted), "unique matches"
    )
    if residuals:
        print(
            "Median:", round(float(np.median(residuals)), 3),
            "px | Mean:", round(float(np.mean(residuals)), 3), "px"
        )

# Build visual overlay using the 3-pixel matching threshold.
accepted = assignments[3.0]
overlay = image.copy()

# Blue: detected candidates.
for x, y in zip(x_detected, y_detected):
    cv2.circle(
        overlay, (int(round(x - 1)), int(round(y - 1))),
        3, (255, 100, 0), 1
    )

# Green: projected Hipparcos stars.
for x, y in zip(px, py):
    cv2.circle(
        overlay, (int(round(x - 1)), int(round(y - 1))),
        4, (0, 220, 0), 1
    )

match_rows = []

# Yellow lines: unique catalogue-to-image correspondences.
for cat_i, det_i, residual in accepted:
    cx, cy = int(round(px[cat_i] - 1)), int(round(py[cat_i] - 1))
    dx = int(round(x_detected[det_i] - 1))
    dy = int(round(y_detected[det_i] - 1))

    cv2.line(overlay, (cx, cy), (dx, dy), (0, 255, 255), 1)

    original_index = cat_indices[cat_i]

    match_rows.append({
        "hip_id": str(hip_near[original_index]),
        "magnitude": float(mag_near[original_index]),
        "catalogue_x": float(px[cat_i]),
        "catalogue_y": float(py[cat_i]),
        "detected_x": float(x_detected[det_i]),
        "detected_y": float(y_detected[det_i]),
        "pixel_residual": float(residual)
    })

overlay_path = RESULTS / "phase35_wcs_match_overlay.jpg"
cv2.imwrite(str(overlay_path), overlay)

match_csv = RESULTS / "phase35_pixel_matches.csv"
if match_rows:
    with match_csv.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(match_rows[0].keys()))
        writer.writeheader()
        writer.writerows(match_rows)

report = {
    "phase": 35,
    "section": "R2C2",
    "image_dimensions": [width, height],
    "detected_candidates": int(len(x_detected)),
    "catalogue_rows": int(len(ra_all)),
    "catalogue_stars_near_field": int(len(ra_near)),
    "catalogue_stars_projected_inside": int(len(px)),
    "pixel_space_one_to_one_matches": summary,
    "visual_match_threshold_pixels": 3.0,
    "visual_match_count": len(accepted),
    "overlay": str(overlay_path),
    "match_csv": str(match_csv),
    "interpretation": (
        "Pixel-space correspondence diagnostic; "
        "not a final optical distortion calibration."
    )
}

report_path = BASE / "phase35_visual_wcs_validation.json"
report_path.write_text(json.dumps(report, indent=2))

print("\nOVERLAY:", overlay_path)
print("MATCH CSV:", match_csv)
print("REPORT:", report_path)
print("\nPHASE 35 CORRECTED COMPLETE")
