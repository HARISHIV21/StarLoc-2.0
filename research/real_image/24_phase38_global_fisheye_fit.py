import csv
import json
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation, rotation
from scipy.spatial.transform import Rotation as R

BASE = Path("research/real_image")
RESULTS = BASE / "results/ASK033"
INPUT = RESULTS / "phase37_validation/phase37_all_matches.csv"
OUT = RESULTS / "phase38_global_calibration"
OUT.mkdir(parents=True, exist_ok=True)

WIDTH, HEIGHT = 1920, 1440

if not INPUT.exists():
    raise FileNotFoundError(f"Phase 37 matches not found: {INPUT}")

with INPUT.open(newline="") as f:
    rows = list(csv.DictReader(f))

if len(rows) < 30:
    raise RuntimeError(
        f"Insufficient correspondences for global fitting: {len(rows)}"
    )

# Original image tile offsets.
OFFSETS = {
    "R1C2": (640, 0),
    "R2C1": (0, 480),
    "R3C1": (0, 960),
    "R3C2": (640, 960),
    "R2C2": (640, 480),
}

pixels = []
sky_vectors = []
sections = []

for row in rows:
    section = row["section"]
    if section not in OFFSETS:
        continue

    ox, oy = OFFSETS[section]

    # Global image coordinates, zero-based.
    x = float(row["candidate_x_local"]) + ox
    y = float(row["candidate_y_local"]) + oy

    ra = np.deg2rad(float(row["hip_ra_deg"]))
    dec = np.deg2rad(float(row["hip_dec_deg"]))

    # ICRS celestial unit vector.
    vector = [
        np.cos(dec) * np.cos(ra),
        np.cos(dec) * np.sin(ra),
        np.sin(dec)
    ]

    pixels.append([x, y])
    sky_vectors.append(vector)
    sections.append(section)

pixels = np.asarray(pixels, dtype=float)
sky_vectors = np.asarray(sky_vectors, dtype=float)
sections = np.asarray(sections)

# Deterministic split: 80% training, 20% held-out test.
order = np.arange(len(pixels))
train_idx = order[order % 5 != 0]
test_idx = order[order % 5 == 0]

if len(test_idx) < 5:
    raise RuntimeError("Too few independent test correspondences.")

# Initial camera orientation: point optical axis toward mean sky vector.
mean_vector = np.mean(sky_vectors[train_idx], axis=0)
mean_vector /= np.linalg.norm(mean_vector)

target_axis = np.array([0.0, 0.0, 1.0])
initial_rotation, _ = Rotation.align_vectors(
    [target_axis], [mean_vector]
)

initial_rotvec = initial_rotation.as_rotvec()

# Parameters:
# rotation vector (3), cx, cy, log(focal scale), k1, k2.
initial = np.array([
    *initial_rotvec,
    WIDTH / 2,
    HEIGHT / 2,
    np.log(700.0),
    0.0,
    0.0
])

lower = np.array([
    -np.inf, -np.inf, -np.inf,
    0, 0, np.log(100.0),
    -1.0, -1.0
])

upper = np.array([
    np.inf, np.inf, np.inf,
    WIDTH, HEIGHT, np.log(3000.0),
    1.0, 1.0
])

def project(parameters, vectors):
    rot = Rotation.from_rotvec(parameters[:3])
    camera = rot.apply(vectors)

    cx, cy = parameters[3], parameters[4]
    focal = np.exp(parameters[5])
    k1, k2 = parameters[6], parameters[7]

    z = camera[:, 2]
    rho = np.hypot(camera[:, 0], camera[:, 1])

    theta = np.arctan2(rho, z)
    radial = focal * (
        theta + k1 * theta**3 + k2 * theta**5
    )

    safe_rho = np.maximum(rho, 1e-12)
    x = cx + radial * camera[:, 0] / safe_rho
    y = cy + radial * camera[:, 1] / safe_rho

    return np.column_stack((x, y)), z

def residual(parameters, indices):
    predicted, z = project(parameters, sky_vectors[indices])

    error = predicted - pixels[indices]

    # Penalize stars projected behind the camera.
    behind = z <= 0
    if np.any(behind):
        error[behind] = 1e4

    return error.ravel()

print("=" * 68)
print("STARLOC 2.0 — PHASE 38")
print("GLOBAL EQUIDISTANT FISHEYE CALIBRATION")
print("=" * 68)
print("Total correspondences:", len(pixels))
print("Training:", len(train_idx))
print("Held-out test:", len(test_idx))
print("Sections:", sorted(set(sections)))

print("\nFitting global camera model...")

fit = least_squares(
    residual,
    initial,
    args=(train_idx,),
    bounds=(lower, upper),
    loss="soft_l1",
    f_scale=2.5,
    max_nfev=5000,
    verbose=0
)

if not fit.success:
    print("Optimizer message:", fit.message)

parameters = fit.x

def metrics(indices):
    predicted, z = project(parameters, sky_vectors[indices])
    error = np.linalg.norm(predicted - pixels[indices], axis=1)

    visible = z > 0
    inside = (
        visible
        & (predicted[:, 0] >= 0)
        & (predicted[:, 0] < WIDTH)
        & (predicted[:, 1] >= 0)
        & (predicted[:, 1] < HEIGHT)
    )

    return {
        "count": int(len(indices)),
        "front_facing": int(np.sum(visible)),
        "predicted_inside_image": int(np.sum(inside)),
        "median_error_px": float(np.median(error)),
        "mean_error_px": float(np.mean(error)),
        "rmse_px": float(np.sqrt(np.mean(error**2))),
        "p90_error_px": float(np.percentile(error, 90)),
        "max_error_px": float(np.max(error))
    }, predicted, error

train_metrics, train_predicted, train_errors = metrics(train_idx)
test_metrics, test_predicted, test_errors = metrics(test_idx)
all_metrics, all_predicted, all_errors = metrics(order)

cx, cy = parameters[3], parameters[4]
focal = np.exp(parameters[5])
k1, k2 = parameters[6], parameters[7]

rotation_matrix = Rotation.from_rotvec(
    parameters[:3]
).as_matrix()

# Optical-axis direction in celestial coordinates.
optical_axis = Rotation.from_rotvec(
    parameters[:3]
).inv().apply([0, 0, 1])

axis_ra = np.rad2deg(
    np.arctan2(optical_axis[1], optical_axis[0])
) % 360

axis_dec = np.rad2deg(
    np.arcsin(optical_axis[2])
)

# Save per-correspondence residuals.
match_output = OUT / "phase38_global_fit_residuals.csv"

with match_output.open("w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow([
        "section", "global_x", "global_y",
        "predicted_x", "predicted_y",
        "residual_px", "dataset"
    ])

    for idx, pred, error in zip(
        train_idx, train_predicted, train_errors
    ):
        writer.writerow([
            sections[idx], pixels[idx, 0], pixels[idx, 1],
            pred[0], pred[1], error, "train"
        ])

    for idx, pred, error in zip(
        test_idx, test_predicted, test_errors
    ):
        writer.writerow([
            sections[idx], pixels[idx, 0], pixels[idx, 1],
            pred[0], pred[1], error, "test"
        ])

# Residual plot.
fig, ax = plt.subplots(figsize=(10, 7))
ax.scatter(
    pixels[train_idx, 0],
    pixels[train_idx, 1],
    c=train_errors,
    s=28,
    label="Training residual"
)
ax.scatter(
    pixels[test_idx, 0],
    pixels[test_idx, 1],
    c=test_errors,
    marker="x",
    s=45,
    label="Held-out test residual"
)
ax.set_xlim(0, WIDTH)
ax.set_ylim(HEIGHT, 0)
ax.set_aspect("equal")
ax.set_xlabel("Image X (pixels)")
ax.set_ylabel("Image Y (pixels)")
ax.set_title("Global fisheye calibration — pixel residuals")
ax.legend()
fig.colorbar(ax.collections[0], ax=ax, label="Residual (pixels)")
fig.tight_layout()
fig.savefig(OUT / "phase38_residual_map.png", dpi=160)
plt.close(fig)

report = {
    "phase": 38,
    "model": "Equidistant fisheye with k1 and k2 radial terms",
    "input": str(INPUT),
    "image_dimensions": [WIDTH, HEIGHT],
    "correspondences": int(len(pixels)),
    "training_correspondences": int(len(train_idx)),
    "test_correspondences": int(len(test_idx)),
    "sections": sorted(set(sections)),
    "optimizer_success": bool(fit.success),
    "optimizer_message": str(fit.message),
    "parameters": {
        "optical_centre_x_px": float(cx),
        "optical_centre_y_px": float(cy),
        "focal_scale_px_per_rad": float(focal),
        "radial_k1": float(k1),
        "radial_k2": float(k2),
        "optical_axis_ra_deg": float(axis_ra),
        "optical_axis_dec_deg": float(axis_dec),
        "rotation_matrix_world_to_camera": rotation_matrix.tolist()
    },
    "training_metrics": train_metrics,
    "held_out_test_metrics": test_metrics,
    "all_data_metrics": all_metrics,
    "interpretation": (
        "Exploratory global fisheye fit. The held-out test residuals "
        "must be assessed before accepting this as a camera calibration. "
        "Input correspondences inherit local WCS matching uncertainty."
    )
}

report_path = BASE / "phase38_global_calibration_report.json"
report_path.write_text(json.dumps(report, indent=2))

print("\n" + "=" * 68)
print("PHASE 38 RESULTS")
print("=" * 68)
print("Optimizer success:", fit.success)
print(f"Optical centre: ({cx:.2f}, {cy:.2f}) px")
print(f"Focal scale: {focal:.3f} px/rad")
print(f"Radial k1: {k1:.8f}")
print(f"Radial k2: {k2:.8f}")
print(f"Optical axis RA: {axis_ra:.5f} deg")
print(f"Optical axis Dec: {axis_dec:.5f} deg")

print("\nTRAINING")
for key, value in train_metrics.items():
    print(f"{key}: {value}")

print("\nHELD-OUT TEST")
for key, value in test_metrics.items():
    print(f"{key}: {value}")

print("\nALL CORRESPONDENCES")
for key, value in all_metrics.items():
    print(f"{key}: {value}")

print("\nReport:", report_path)
print("Residual CSV:", match_output)
print("Residual map:", OUT / "phase38_residual_map.png")
print("\nPHASE 38 COMPLETE")
