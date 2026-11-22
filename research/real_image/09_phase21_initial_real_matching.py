import csv
import json
import math
from pathlib import Path

import cv2
import numpy as np
from scipy.spatial import cKDTree
from scipy.optimize import minimize

ROOT = Path("research/real_image/results/ASK033")
IMAGE = Path("research/real_image/data/network/ASK033/ASK033_live_original.jpg")
CANDIDATES = ROOT / "refined_candidates.csv"
CATALOGUE = ROOT / "ASK033_visible_hipparcos_catalogue.csv"
OUT = ROOT

def read_csv(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        raise RuntimeError("Empty CSV: " + str(path))
    return rows

def find_key(row, names):
    lower = {k.lower(): k for k in row}
    for name in names:
        if name.lower() in lower:
            return lower[name.lower()]
    raise KeyError(
        "Could not find any of " + str(names) +
        " in columns " + str(list(row.keys()))
    )

detections = read_csv(CANDIDATES)
catalogue = read_csv(CATALOGUE)

print("Candidate columns:", list(detections[0].keys()))
print("Catalogue columns:", list(catalogue[0].keys()))

dx = find_key(detections[0], ["x", "centroid_x", "x_px", "cx"])
dy = find_key(detections[0], ["y", "centroid_y", "y_px", "cy"])

azk = find_key(catalogue[0], ["azimuth_deg", "az_deg", "azimuth"])
altk = find_key(catalogue[0], ["altitude_deg", "alt_deg", "altitude"])
hipk = find_key(catalogue[0], ["hip_id", "hip_number", "hip"])
magk = find_key(catalogue[0], ["magnitude", "vmag", "mag"])

pixels = np.array([
    [float(r[dx]), float(r[dy])] for r in detections
], dtype=float)

az = np.array([float(r[azk]) for r in catalogue])
alt = np.array([float(r[altk]) for r in catalogue])
mag = np.array([float(r[magk]) for r in catalogue])
hip = np.array([str(r[hipk]) for r in catalogue])

image = cv2.imread(str(IMAGE))
if image is None:
    raise RuntimeError("Original ASK033 image not found")
h, w = image.shape[:2]

# Use the image centre as a provisional optical centre.
cx0, cy0 = w / 2.0, h / 2.0

# Keep brighter catalogue stars for the first identification pass.
# This reduces confusion from the very large number of faint stars.
bright = mag <= 4.8
az, alt, mag, hip = az[bright], alt[bright], mag[bright], hip[bright]

# Zenith-centred equidistant projection:
# radial distance = focal_scale * zenith_distance_in_radians.
zenith_distance = np.deg2rad(90.0 - alt)
az_rad = np.deg2rad(az)

def project(roll_deg, focal):
    angle = az_rad + np.deg2rad(roll_deg)
    radius = focal * zenith_distance
    x = cx0 + radius * np.sin(angle)
    y = cy0 - radius * np.cos(angle)
    return np.column_stack((x, y))

# Restrict the initial search to plausible full-sky fisheye scales.
# Search roll globally; optimize roll and focal from nearest neighbours.
def score(params):
    roll, focal = params
    if focal < 300 or focal > 650:
        return 1e6
    projected = project(roll, focal)
    inside = (
        (projected[:, 0] >= 0) & (projected[:, 0] < w) &
        (projected[:, 1] >= 0) & (projected[:, 1] < h)
    )
    projected = projected[inside]
    if len(projected) < 10:
        return 1e6
    tree = cKDTree(projected)
    distances, _ = tree.query(pixels, k=1)
    # Robust truncated loss prevents false detections dominating.
    return float(np.mean(np.minimum(distances, 18.0) ** 2))

best = None
for roll in range(0, 360, 5):
    result = minimize(
        score,
        x0=[float(roll), 458.0],
        method="Nelder-Mead",
        options={"maxiter": 120, "xatol": 0.02, "fatol": 0.001}
    )
    if best is None or result.fun < best.fun:
        best = result

roll, focal = float(best.x[0] % 360), float(best.x[1])
projected_all = project(roll, focal)

inside = (
    (projected_all[:, 0] >= 0) & (projected_all[:, 0] < w) &
    (projected_all[:, 1] >= 0) & (projected_all[:, 1] < h)
)
projected = projected_all[inside]
catalogue_indices = np.flatnonzero(inside)
tree = cKDTree(projected)

distances, nearest = tree.query(pixels, k=1)
# Keep only close provisional correspondences.
threshold_px = 8.0
matches = []

for i, distance in enumerate(distances):
    if distance <= threshold_px:
        j = catalogue_indices[nearest[i]]
        matches.append({
            "detection_index": i,
            "hip_id": hip[j],
            "catalogue_magnitude": float(mag[j]),
            "pixel_x": float(pixels[i, 0]),
            "pixel_y": float(pixels[i, 1]),
            "projected_x": float(projected_all[j, 0]),
            "projected_y": float(projected_all[j, 1]),
            "residual_px": float(distance)
        })

# Enforce one-to-one catalogue assignment: retain the closest detection
# for each HIP identifier.
unique = {}
for match in matches:
    key = match["hip_id"]
    if key not in unique or match["residual_px"] < unique[key]["residual_px"]:
        unique[key] = match
matches = sorted(unique.values(), key=lambda r: r["residual_px"])

match_path = OUT / "phase21_provisional_matches.csv"
with open(match_path, "w", newline="", encoding="utf-8") as f:
    fields = [
        "detection_index", "hip_id", "catalogue_magnitude",
        "pixel_x", "pixel_y", "projected_x", "projected_y",
        "residual_px"
    ]
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerows(matches)

residuals = np.array([m["residual_px"] for m in matches])
report = {
    "phase": 21,
    "image": str(IMAGE),
    "image_width": w,
    "image_height": h,
    "candidate_count": len(pixels),
    "catalogue_count_after_magnitude_filter": len(az),
    "projection": "Provisional zenith-centred equidistant fisheye",
    "assumed_optical_centre_px": [cx0, cy0],
    "estimated_roll_deg": roll,
    "estimated_focal_scale_px_per_rad": focal,
    "estimated_full_fov_deg": math.degrees(min(w, h) / (2.0 * focal) * 2.0),
    "matching_threshold_px": threshold_px,
    "provisional_unique_matches": len(matches),
    "median_residual_px": float(np.median(residuals)) if len(residuals) else None,
    "mean_residual_px": float(np.mean(residuals)) if len(residuals) else None,
    "warning": (
        "Exploratory correspondences only. Optical centre, camera tilt, "
        "distortion, masks and false matches have not yet been independently solved."
    )
}

(OUT / "phase21_matching_report.json").write_text(
    json.dumps(report, indent=2)
)

print("\nSTARLOC 2.0 — PHASE 21")
print("=" * 58)
print("Image size:", w, "x", h)
print("Image candidates:", len(pixels))
print("Bright catalogue stars tested:", len(az))
print("Estimated roll:", round(roll, 4), "deg")
print("Estimated focal scale:", round(focal, 4), "px/rad")
print("Provisional unique matches:", len(matches))
if len(residuals):
    print("Median residual:", round(float(np.median(residuals)), 3), "px")
    print("Mean residual:", round(float(np.mean(residuals)), 3), "px")
print("\nSaved:")
print(match_path.resolve())
print((OUT / "phase21_matching_report.json").resolve())
print("\nPHASE 21 COMPLETE — EXPLORATORY MATCHING")
