import csv
import json
import math
from pathlib import Path

import numpy as np
from astropy.wcs import WCS
from astropy.coordinates import SkyCoord
import astropy.units as u

BASE = Path("research/real_image")
ASK = BASE / "results/ASK033"
OUT = ASK / "phase53_catalogue_revalidation"
OUT.mkdir(parents=True, exist_ok=True)

PHASE49 = ASK / "phase49_cross_section_consistency/phase49_cross_section_point_comparison.csv"
PHASE52 = BASE / "phase52_global_prediction_test_report.json"
WCS_PATH = ASK / "custom_plate_solutions/R2C2_custom.wcs"

print("=" * 76)
print("STARLOC 2.0 — PHASE 53")
print("HIPPARCOS CATALOGUE IDENTITY REVALIDATION")
print("=" * 76)

for p in [PHASE49, PHASE52, WCS_PATH]:
    if not p.exists():
        raise FileNotFoundError(f"Required input missing: {p}")

# ------------------------------------------------------------
# 1. Locate the actual visible Hipparcos catalogue.
# ------------------------------------------------------------
aliases = {
    "hip": {"hip", "hip_id", "hipparcos", "hipparcos_id", "hip_number"},
    "ra": {"ra", "ra_deg", "raj2000", "ra_icrs", "right_ascension"},
    "dec": {"dec", "dec_deg", "dej2000", "dec_icrs", "declination"},
}

catalogue_candidates = []

for path in BASE.rglob("*.csv"):
    try:
        with path.open(newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            if not reader.fieldnames:
                continue
            normalized = {
                str(name).strip().lower().replace(" ", "_"): name
                for name in reader.fieldnames
            }
            found = {}
            for key, names in aliases.items():
                match = next((normalized[n] for n in names if n in normalized), None)
                if match is None:
                    break
                found[key] = match
            if len(found) == 3:
                rows = list(reader)
                if len(rows) >= 100:
                    score = len(rows) + (100000 if "catalog" in path.name.lower() else 0)
                    catalogue_candidates.append((score, path, found, rows))
    except Exception:
        continue

if not catalogue_candidates:
    raise RuntimeError(
        "Could not automatically identify the Hipparcos CSV. "
        "No calibration files were changed."
    )

catalogue_candidates.sort(key=lambda x: x[0], reverse=True)
_, catalogue_path, columns, catalogue_rows = catalogue_candidates[0]

print("\nSelected catalogue:", catalogue_path)
print("Rows:", len(catalogue_rows))
print("Columns:", columns)

hip_ids, ra_values, dec_values = [], [], []
for row in catalogue_rows:
    try:
        hip_ids.append(str(row[columns["hip"]]))
        ra_values.append(float(row[columns["ra"]]))
        dec_values.append(float(row[columns["dec"]]))
    except (ValueError, TypeError):
        continue

catalogue_coords = SkyCoord(
    ra=np.asarray(ra_values) * u.deg,
    dec=np.asarray(dec_values) * u.deg,
    frame="icrs"
)

# ------------------------------------------------------------
# 2. Load source correspondences and global model predictions.
# ------------------------------------------------------------
with PHASE49.open(newline="", encoding="utf-8-sig") as f:
    phase49_rows = list(csv.DictReader(f))

r2c2_rows = [r for r in phase49_rows if r["section"] == "R2C2"]

with PHASE52.open() as f:
    phase52 = json.load(f)

points = phase52["points"]
wcs = WCS(str(WCS_PATH), relax=True)

# R2C2 is the centre tile: its global offset is (640, 480).
OFFSET_X, OFFSET_Y = 640.0, 480.0

records = []

for point in points:
    name = point["id"]
    gx = float(point["candidate_position"]["x"])
    gy = float(point["candidate_position"]["y"])
    px = float(point["global_prediction"]["x"])
    py = float(point["global_prediction"]["y"])

    # Match the Phase 49 record to the detected candidate.
    matches = []
    for row in r2c2_rows:
        distance = math.hypot(
            float(row["global_x"]) - gx,
            float(row["global_y"]) - gy
        )
        matches.append((distance, row))

    candidate_distance, source_row = min(matches, key=lambda x: x[0])
    if candidate_distance > 0.1:
        raise RuntimeError(
            f"{name}: could not match Phase 49 source row "
            f"(nearest distance {candidate_distance:.3f}px)"
        )

    assigned_ra = float(source_row["hip_ra_deg"])
    assigned_dec = float(source_row["hip_dec_deg"])

    # Convert global image coordinates to R2C2 tile coordinates.
    candidate_local = [gx - OFFSET_X, gy - OFFSET_Y]
    prediction_local = [px - OFFSET_X, py - OFFSET_Y]

    # Sky coordinates implied by the local plate solution.
    candidate_sky = wcs.pixel_to_world(
        candidate_local[0], candidate_local[1]
    )
    prediction_sky = wcs.pixel_to_world(
        prediction_local[0], prediction_local[1]
    )

    assigned_sky = SkyCoord(
        ra=assigned_ra * u.deg,
        dec=assigned_dec * u.deg,
        frame="icrs"
    )

    # Find nearest catalogue star at each WCS-implied sky position.
    candidate_idx, candidate_sep, _ = candidate_sky.match_to_catalog_sky(
        catalogue_coords
    )
    prediction_idx, prediction_sep, _ = prediction_sky.match_to_catalog_sky(
        catalogue_coords
    )

    assigned_idx = int(np.argmin(
        assigned_sky.separation(catalogue_coords).to_value(u.arcsec)
    ))
    assigned_catalogue_sep = assigned_sky.separation(
        catalogue_coords[assigned_idx]
    ).arcsec

    # Also find nearest catalogue star to the original detected candidate
    # and to the global-model predicted position.
    records.append({
        "point": name,
        "candidate_global_x": gx,
        "candidate_global_y": gy,
        "global_prediction_x": px,
        "global_prediction_y": py,
        "candidate_to_global_prediction_px": math.hypot(px-gx, py-gy),
        "original_assigned_ra_deg": assigned_ra,
        "original_assigned_dec_deg": assigned_dec,
        "original_assigned_hip_id": hip_ids[assigned_idx],
        "original_assigned_catalogue_separation_arcsec": assigned_catalogue_sep,
        "candidate_wcs_ra_deg": candidate_sky.ra.deg,
        "candidate_wcs_dec_deg": candidate_sky.dec.deg,
        "candidate_nearest_hip_id": hip_ids[int(candidate_idx)],
        "candidate_nearest_hip_separation_arcsec": float(np.asarray(candidate_sep.arcsec).reshape(-1)[0]),
        "prediction_wcs_ra_deg": prediction_sky.ra.deg,
        "prediction_wcs_dec_deg": prediction_sky.dec.deg,
        "prediction_nearest_hip_id": hip_ids[int(prediction_idx)],
        "prediction_nearest_hip_separation_arcsec": float(np.asarray(prediction_sep.arcsec).reshape(-1)[0]),
        "same_nearest_catalogue_id": (
            hip_ids[int(candidate_idx)] == hip_ids[int(prediction_idx)]
        ),
    })

    print(f"\n{name}")
    print(f"  Original assigned HIP: {hip_ids[assigned_idx]}")
    print(f"  Original catalogue coordinate: RA={assigned_ra:.6f}, Dec={assigned_dec:.6f}")
    print(f"  Candidate WCS coordinate: RA={candidate_sky.ra.deg:.6f}, Dec={candidate_sky.dec.deg:.6f}")
    print(f"  Nearest HIP at candidate: {hip_ids[int(candidate_idx)]}")
    print(f"  Candidate-to-catalogue separation: {float(np.asarray(candidate_sep.arcsec).reshape(-1)[0]):.2f} arcsec")
    print(f"  Global-prediction WCS coordinate: RA={prediction_sky.ra.deg:.6f}, Dec={prediction_sky.dec.deg:.6f}")
    print(f"  Nearest HIP at global prediction: {hip_ids[int(prediction_idx)]}")
    print(f"  Prediction-to-catalogue separation: {float(np.asarray(prediction_sep.arcsec).reshape(-1)[0]):.2f} arcsec")
    print(f"  Same nearest HIP at both positions: {hip_ids[int(candidate_idx)] == hip_ids[int(prediction_idx)]}")

# ------------------------------------------------------------
# 3. Save auditable outputs.
# ------------------------------------------------------------
csv_path = OUT / "phase53_catalogue_identity_audit.csv"
with csv_path.open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=list(records[0].keys()))
    writer.writeheader()
    writer.writerows(records)

report = {
    "phase": 53,
    "title": "R2C2 Hipparcos catalogue identity revalidation",
    "catalogue_file": str(catalogue_path),
    "catalogue_rows_loaded": len(hip_ids),
    "wcs_file": str(WCS_PATH),
    "method": (
        "Compare the Hipparcos identities nearest to the detected candidate "
        "and the global-model prediction after mapping both positions through "
        "the R2C2 local WCS."
    ),
    "points": records,
    "limitations": [
        "The local WCS is itself an astrometric solution and is not independent ground truth.",
        "Nearest catalogue identity alone does not prove a star detection.",
        "Catalogue epoch, proper motion, atmospheric refraction and image timestamp "
        "uncertainties may affect angular separations.",
        "This phase does not modify or refit the global fisheye calibration."
    ]
}

json_path = BASE / "phase53_catalogue_identity_revalidation_report.json"
json_path.write_text(json.dumps(report, indent=2))

print("\n" + "=" * 76)
print("PHASE 53 COMPLETED")
print("=" * 76)
print("Catalogue:", catalogue_path)
print("CSV:", csv_path)
print("Report:", json_path)
print("Original calibration files preserved.")
