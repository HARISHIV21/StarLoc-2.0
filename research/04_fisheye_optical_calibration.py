import csv
import json
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "research" / "data" / "synthetic"
RESULTS = ROOT / "research" / "results"
RESULTS.mkdir(parents=True, exist_ok=True)

# Load synthetic celestial catalogue.
with (DATA / "synthetic_star_catalogue.csv").open() as f:
    catalogue = list(csv.DictReader(f))

# Load detected image positions.
with (RESULTS / "optimized_detections.csv").open() as f:
    detections = list(csv.DictReader(f))

detected_xy = np.array([
    [float(row["x_pixel"]), float(row["y_pixel"])]
    for row in detections
])

# Associate each catalogue star with its nearest detected centroid.
# This uses known synthetic correspondences for controlled validation.
pairs = []
used_detections = set()

for row in catalogue:
    ra = np.radians(float(row["ra_deg"]))
    dec = np.radians(float(row["dec_deg"]))

    celestial = np.array([
        np.cos(dec) * np.cos(ra),
        np.cos(dec) * np.sin(ra),
        np.sin(dec)
    ])

    expected_xy = np.array([
        float(row["x_pixel"]),
        float(row["y_pixel"])
    ])

    distances = np.linalg.norm(detected_xy - expected_xy, axis=1)
    order = np.argsort(distances)

    for detection_index in order:
        if distances[detection_index] <= 5.0:
            if int(detection_index) not in used_detections:
                used_detections.add(int(detection_index))
                observed_xy = detected_xy[detection_index]
                pairs.append((celestial, observed_xy, row))
                break

if len(pairs) < 10:
    raise RuntimeError("Not enough matched stars for calibration.")

celestial_vectors = np.array([p[0] for p in pairs])
observed_pixels = np.array([p[1] for p in pairs])

# Deterministic train/test split.
rng = np.random.default_rng(2026)
indices = rng.permutation(len(pairs))
split = max(1, int(0.8 * len(indices)))

train_indices = indices[:split]
test_indices = indices[split:]

train_celestial = celestial_vectors[train_indices]
train_pixels = observed_pixels[train_indices]
test_celestial = celestial_vectors[test_indices]
test_pixels = observed_pixels[test_indices]

IMAGE_CENTER = 512.0

def predict_pixels(parameters, celestial):
    rotation_vector = parameters[:3]
    cx, cy = parameters[3:5]
    focal_length = np.exp(parameters[5])

    rotation = Rotation.from_rotvec(rotation_vector).as_matrix()

    # Celestial directions transformed into camera coordinates.
    camera = (rotation.T @ celestial.T).T

    z = np.clip(camera[:, 2], -1.0, 1.0)
    theta = np.arccos(z)
    sin_theta = np.sin(theta)

    scale = np.ones_like(theta)
    valid = np.abs(sin_theta) > 1e-10
    scale[valid] = theta[valid] / sin_theta[valid]

    u = cx + focal_length * scale * camera[:, 0]
    v = cy - focal_length * scale * camera[:, 1]

    return np.column_stack((u, v))


def residuals(parameters, celestial, observed):
    predicted = predict_pixels(parameters, celestial)
    return (predicted - observed).ravel()


# Initial estimate:
# image centre = image midpoint; focal length approximately 318 px.
initial = np.array([
    0.0, 0.0, 0.0,
    IMAGE_CENTER,
    IMAGE_CENTER,
    np.log(318.3)
])

lower = [
    -np.pi, -np.pi, -np.pi,
    400.0, 400.0,
    np.log(100.0)
]

upper = [
    np.pi, np.pi, np.pi,
    624.0, 624.0,
    np.log(600.0)
]

fit = least_squares(
    residuals,
    initial,
    args=(train_celestial, train_pixels),
    bounds=(lower, upper),
    loss="soft_l1",
    f_scale=1.0,
    max_nfev=5000
)

if not fit.success:
    raise RuntimeError(f"Calibration failed: {fit.message}")

parameters = fit.x

train_predictions = predict_pixels(parameters, train_celestial)
test_predictions = predict_pixels(parameters, test_celestial)

train_errors = np.linalg.norm(
    train_predictions - train_pixels, axis=1
)

test_errors = np.linalg.norm(
    test_predictions - test_pixels, axis=1
)

rotation_matrix = Rotation.from_rotvec(
    parameters[:3]
).as_matrix()

cx, cy = parameters[3:5]
focal_length = float(np.exp(parameters[5]))
estimated_fov = 2.0 * (500.0 / focal_length) * (180.0 / np.pi)

summary = {
    "project": "StarLoc 2.0",
    "dataset": "synthetic",
    "projection_model": "equidistant_fisheye",
    "matched_stars": int(len(pairs)),
    "training_stars": int(len(train_indices)),
    "testing_stars": int(len(test_indices)),
    "estimated_optical_center_pixels": {
        "cx": float(cx),
        "cy": float(cy)
    },
    "estimated_focal_scale_pixels": focal_length,
    "estimated_fov_from_image_radius_deg": float(estimated_fov),
    "estimated_camera_to_celestial_rotation_matrix": rotation_matrix.tolist(),
    "training_error_pixels": {
        "mean": float(np.mean(train_errors)),
        "median": float(np.median(train_errors)),
        "maximum": float(np.max(train_errors)),
        "rmse": float(np.sqrt(np.mean(train_errors**2)))
    },
    "testing_error_pixels": {
        "mean": float(np.mean(test_errors)) if len(test_errors) else None,
        "median": float(np.median(test_errors)) if len(test_errors) else None,
        "maximum": float(np.max(test_errors)) if len(test_errors) else None,
        "rmse": float(np.sqrt(np.mean(test_errors**2))) if len(test_errors) else None
    },
    "note": (
        "Synthetic validation only. This does not establish "
        "calibration performance on real AllSkyKamera images."
    )
}

with (RESULTS / "fisheye_calibration.json").open("w") as f:
    json.dump(summary, f, indent=4)

# Save per-star residuals.
with (RESULTS / "calibration_residuals.csv").open("w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["dataset", "star_index", "pixel_error"])

    for i, error in enumerate(train_errors):
        writer.writerow(["training", i + 1, f"{error:.6f}"])

    for i, error in enumerate(test_errors):
        writer.writerow(["testing", i + 1, f"{error:.6f}"])

# Diagnostic plot.
fig, ax = plt.subplots(figsize=(9, 6))

ax.hist(train_errors, bins=15, alpha=0.65, label="Training")
if len(test_errors):
    ax.hist(test_errors, bins=15, alpha=0.65, label="Testing")

ax.set_title("Fisheye Calibration — Reprojection Error")
ax.set_xlabel("Pixel error")
ax.set_ylabel("Number of stars")
ax.legend()
ax.grid(alpha=0.2)

fig.tight_layout()
fig.savefig(RESULTS / "calibration_error_distribution.png", dpi=160)
plt.close(fig)

print("\nSTARLOC 2.0 — FISHEYE OPTICAL CALIBRATION")
print("------------------------------------------")
print("Matched stars:", len(pairs))
print("Training stars:", len(train_indices))
print("Testing stars:", len(test_indices))
print("\nEstimated optical parameters:")
print(f"Optical centre X: {cx:.4f} pixels")
print(f"Optical centre Y: {cy:.4f} pixels")
print(f"Focal scale:      {focal_length:.4f} pixels")
print(f"Estimated FOV:    {estimated_fov:.4f} degrees")

print("\nTraining reprojection error:")
print(f"Mean:   {np.mean(train_errors):.4f} pixels")
print(f"RMSE:   {np.sqrt(np.mean(train_errors**2)):.4f} pixels")
print(f"Maximum:{np.max(train_errors):.4f} pixels")

if len(test_errors):
    print("\nIndependent testing reprojection error:")
    print(f"Mean:   {np.mean(test_errors):.4f} pixels")
    print(f"RMSE:   {np.sqrt(np.mean(test_errors**2)):.4f} pixels")
    print(f"Maximum:{np.max(test_errors):.4f} pixels")

print("\nSaved:")
print(RESULTS / "fisheye_calibration.json")
print(RESULTS / "calibration_residuals.csv")
print(RESULTS / "calibration_error_distribution.png")
print("\nOPTICAL CALIBRATION COMPLETE")
