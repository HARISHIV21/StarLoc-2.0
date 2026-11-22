import csv
import json
from pathlib import Path

import cv2
import numpy as np
from scipy.spatial import cKDTree
from scipy.optimize import differential_evolution
from scipy.spatial.transform import Rotation

ROOT = Path("research/real_image/results/ASK033")
IMAGE = Path("research/real_image/data/network/ASK033/ASK033_live_original.jpg")

def load_csv(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))

detections = load_csv(ROOT / "refined_candidates.csv")
catalogue = load_csv(ROOT / "ASK033_visible_hipparcos_catalogue.csv")

pixels = np.array([[float(r["x"]), float(r["y"])] for r in detections])
az = np.deg2rad(np.array([float(r["azimuth_deg"]) for r in catalogue]))
alt = np.deg2rad(np.array([float(r["altitude_deg"]) for r in catalogue]))
mag = np.array([float(r["magnitude"]) for r in catalogue])
hip = np.array([str(r["hip_id"]) for r in catalogue])

# Use brighter stars first to reduce confusion from faint detections.
keep = mag <= 4.8
az, alt, mag, hip = az[keep], alt[keep], mag[keep], hip[keep]

image = cv2.imread(str(IMAGE))
if image is None:
    raise RuntimeError("ASK033 original image not found")
height, width = image.shape[:2]
cx, cy = width / 2.0, height / 2.0

# Local horizontal coordinates:
# x = East, y = North, z = Up.
world = np.column_stack((
    np.cos(alt) * np.sin(az),
    np.cos(alt) * np.cos(az),
    np.sin(alt)
))

detection_tree = cKDTree(pixels)

def project(params):
    rotvec = np.asarray(params[:3], dtype=float)
    focal = float(params[3])

    rotation = Rotation.from_rotvec(rotvec).as_matrix()
    camera = world @ rotation.T

    z = np.clip(camera[:, 2], -1.0, 1.0)
    theta = np.arccos(z)
    radial = np.hypot(camera[:, 0], camera[:, 1])

    safe = np.maximum(radial, 1e-12)
    x = cx + focal * theta * camera[:, 0] / safe
    y = cy - focal * theta * camera[:, 1] / safe

    return np.column_stack((x, y)), camera[:, 2]

def objective(params):
    projected, front = project(params)

    valid = (
        (front > 0.0) &
        (projected[:, 0] >= 0) & (projected[:, 0] < width) &
        (projected[:, 1] >= 0) & (projected[:, 1] < height)
    )

    points = projected[valid]
    if len(points) < 20:
        return 1e6

    distances, _ = detection_tree.query(points, k=1)

    # Robust loss limits the effect of false detections and masked stars.
    clipped = np.minimum(distances, 15.0)
    close_count = int(np.sum(distances < 6.0))

    # Reward genuine concentration of catalogue projections near detections.
    return float(np.mean(clipped ** 2) - 0.025 * close_count)

print("\nSTARLOC 2.0 — PHASE 22")
print("=" * 58)
print("Image detections:", len(pixels))
print("Bright catalogue stars:", len(world))
print("Searching full 3D orientation and focal scale...")
print("This optimization may take a few minutes.")

result = differential_evolution(
    objective,
    bounds=[
        (-np.pi, np.pi),
        (-np.pi, np.pi),
        (-np.pi, np.pi),
        (350.0, 650.0)
    ],
    strategy="best1bin",
    maxiter=180,
    popsize=12,
    tol=0.002,
    mutation=(0.5, 1.0),
    recombination=0.7,
    polish=True,
    seed=42,
    workers=1,
    updating="immediate"
)

params = result.x
projected, front = project(params)

valid = (
    (front > 0.0) &
    (projected[:, 0] >= 0) & (projected[:, 0] < width) &
    (projected[:, 1] >= 0) & (projected[:, 1] < height)
)

valid_indices = np.flatnonzero(valid)
tree = cKDTree(projected[valid])
distances, nearest = tree.query(pixels, k=1)

# Build unique candidate-to-catalogue matches.
pairs = []
for i, distance in enumerate(distances):
    if distance <= 6.0:
        j = valid_indices[nearest[i]]
        pairs.append({
            "detection_index": i,
            "hip_id": hip[j],
            "magnitude": float(mag[j]),
            "pixel_x": float(pixels[i, 0]),
            "pixel_y": float(pixels[i, 1]),
            "catalogue_projected_x": float(projected[j, 0]),
            "catalogue_projected_y": float(projected[j, 1]),
            "residual_px": float(distance)
        })

unique = {}
for pair in pairs:
    key = pair["hip_id"]
    if key not in unique or pair["residual_px"] < unique[key]["residual_px"]:
        unique[key] = pair

matches = sorted(unique.values(), key=lambda r: r["residual_px"])
residuals = np.array([m["residual_px"] for m in matches])

with open(ROOT / "phase22_full_orientation_matches.csv", "w", newline="") as f:
    fields = list(matches[0].keys()) if matches else [
        "detection_index", "hip_id", "magnitude",
        "pixel_x", "pixel_y", "catalogue_projected_x",
        "catalogue_projected_y", "residual_px"
    ]
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerows(matches)

rotation = Rotation.from_rotvec(params[:3])
matrix = rotation.as_matrix()

report = {
    "phase": 22,
    "model": "Equidistant fisheye with full 3D camera rotation",
    "optical_centre_fixed_px": [cx, cy],
    "rotation_vector_rad": params[:3].tolist(),
    "rotation_matrix_world_to_camera": matrix.tolist(),
    "focal_scale_px_per_rad": float(params[3]),
    "catalogue_stars_tested": len(world),
    "image_candidates": len(pixels),
    "unique_provisional_matches_within_6px": len(matches),
    "median_residual_px": float(np.median(residuals)) if len(residuals) else None,
    "mean_residual_px": float(np.mean(residuals)) if len(residuals) else None,
    "optimizer_objective": float(result.fun),
    "optimizer_success": bool(result.success),
    "optimizer_message": str(result.message),
    "warning": "Exploratory fit only. Optical centre, lens distortion, masks and correspondence reliability still require validation."
}

(ROOT / "phase22_full_orientation_report.json").write_text(
    json.dumps(report, indent=2)
)

print("\nRESULT")
print("Optimizer success:", result.success)
print("Focal scale:", round(float(params[3]), 3), "px/rad")
print("Unique provisional matches:", len(matches))
if len(residuals):
    print("Median residual:", round(float(np.median(residuals)), 3), "px")
    print("Mean residual:", round(float(np.mean(residuals)), 3), "px")

print("\nSaved:")
print((ROOT / "phase22_full_orientation_matches.csv").resolve())
print((ROOT / "phase22_full_orientation_report.json").resolve())
print("\nPHASE 22 COMPLETE")
