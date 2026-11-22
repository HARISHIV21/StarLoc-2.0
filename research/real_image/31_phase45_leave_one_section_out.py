import csv
import json
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation

BASE = Path("research/real_image")
RESULTS = BASE / "results/ASK033"
INPUT = RESULTS / "phase37_validation/phase37_all_matches.csv"
OUT = RESULTS / "phase45_leave_r2c2_out"
OUT.mkdir(parents=True, exist_ok=True)

WIDTH, HEIGHT = 1920, 1440

OFFSETS = {
    "R1C2": (640, 0),
    "R2C1": (0, 480),
    "R3C1": (0, 960),
    "R3C2": (640, 960),
    "R2C2": (640, 480),
}

if not INPUT.exists():
    raise FileNotFoundError(INPUT)

with INPUT.open(newline="") as f:
    rows = list(csv.DictReader(f))

pixels, sky_vectors, sections = [], [], []

for row in rows:
    section = row["section"]
    if section not in OFFSETS:
        continue

    ox, oy = OFFSETS[section]
    x = float(row["candidate_x_local"]) + ox
    y = float(row["candidate_y_local"]) + oy

    ra = np.deg2rad(float(row["hip_ra_deg"]))
    dec = np.deg2rad(float(row["hip_dec_deg"]))

    vector = [
        np.cos(dec) * np.cos(ra),
        np.cos(dec) * np.sin(ra),
        np.sin(dec),
    ]

    pixels.append([x, y])
    sky_vectors.append(vector)
    sections.append(section)

pixels = np.asarray(pixels, dtype=float)
sky_vectors = np.asarray(sky_vectors, dtype=float)
sections = np.asarray(sections)

order = np.arange(len(pixels))
original_train = order[order % 5 != 0]
original_test = order[order % 5 == 0]

# Entire R2C2 section is excluded from fitting.
train_idx = original_train[sections[original_train] != "R2C2"]
r2c2_idx = np.where(sections == "R2C2")[0]
other_test_idx = original_test[sections[original_test] != "R2C2"]
other_train_idx = train_idx.copy()

if len(r2c2_idx) != 51:
    raise RuntimeError(f"Expected 51 R2C2 matches, found {len(r2c2_idx)}")

if len(train_idx) < 100:
    raise RuntimeError(f"Unexpectedly small training set: {len(train_idx)}")

# Reproduce Phase 38 initialisation and model exactly.
mean_vector = np.mean(sky_vectors[train_idx], axis=0)
mean_vector /= np.linalg.norm(mean_vector)

initial_rotation, _ = Rotation.align_vectors(
    [np.array([0.0, 0.0, 1.0])],
    [mean_vector],
)

initial = np.array([
    *initial_rotation.as_rotvec(),
    WIDTH / 2,
    HEIGHT / 2,
    np.log(700.0),
    0.0,
    0.0,
])

lower = np.array([
    -np.inf, -np.inf, -np.inf,
    0, 0, np.log(100.0),
    -1.0, -1.0,
])

upper = np.array([
    np.inf, np.inf, np.inf,
    WIDTH, HEIGHT, np.log(3000.0),
    1.0, 1.0,
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
    error[z <= 0] = 1e4
    return error.ravel()

def metrics(parameters, indices):
    predicted, z = project(parameters, sky_vectors[indices])
    error_vectors = predicted - pixels[indices]
    errors = np.linalg.norm(error_vectors, axis=1)

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
        "median_error_px": float(np.median(errors)),
        "mean_error_px": float(np.mean(errors)),
        "rmse_px": float(np.sqrt(np.mean(errors**2))),
        "p90_error_px": float(np.percentile(errors, 90)),
        "max_error_px": float(np.max(errors)),
        "over_2px": int(np.sum(errors > 2)),
        "over_3px": int(np.sum(errors > 3)),
        "over_5px": int(np.sum(errors > 5)),
        "over_10px": int(np.sum(errors > 10)),
    }, predicted, error_vectors, errors

print("=" * 70)
print("STARLOC 2.0 — PHASE 45")
print("LEAVE-R2C2-OUT GLOBAL CALIBRATION")
print("=" * 70)

print("Total correspondences:", len(pixels))
print("Training sections:", sorted(set(sections[train_idx])))
print("Training points:", len(train_idx))
print("R2C2 withheld points:", len(r2c2_idx))
print("Other held-out test points:", len(other_test_idx))

print("\nFitting global model without R2C2...")

fit = least_squares(
    residual,
    initial,
    args=(train_idx,),
    bounds=(lower, upper),
    loss="soft_l1",
    f_scale=2.5,
    max_nfev=5000,
    verbose=0,
)

if not fit.success:
    raise RuntimeError("Phase 45 optimizer failed: " + fit.message)

parameters = fit.x

print("Optimizer:", fit.message)

# Evaluate withheld R2C2, training sections, and original held-out points.
r2_metrics, r2_pred, r2_vectors, r2_errors = metrics(
    parameters, r2c2_idx
)
train_metrics, train_pred, train_vectors, train_errors = metrics(
    parameters, train_idx
)
other_test_metrics, other_test_pred, other_test_vectors, other_test_errors = metrics(
    parameters, other_test_idx
)

# Per-section evaluation.
section_results = {}
all_section_records = []

for section in sorted(set(sections)):
    indices = np.where(sections == section)[0]
    result, predicted, vectors, errors = metrics(parameters, indices)
    section_results[section] = result

    for idx, pred, vector, error in zip(
        indices, predicted, vectors, errors
    ):
        all_section_records.append({
            "index": int(idx),
            "section": str(sections[idx]),
            "global_x": float(pixels[idx, 0]),
            "global_y": float(pixels[idx, 1]),
            "predicted_x": float(pred[0]),
            "predicted_y": float(pred[1]),
            "dx": float(vector[0]),
            "dy": float(vector[1]),
            "residual_px": float(error),
            "dataset": (
                "withheld_R2C2" if sections[idx] == "R2C2"
                else "training_section"
            ),
        })

# Save all point-level residuals.
csv_path = OUT / "phase45_leave_r2c2_out_residuals.csv"

with csv_path.open("w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=list(all_section_records[0]))
    writer.writeheader()
    writer.writerows(all_section_records)

rotation = Rotation.from_rotvec(parameters[:3])
optical_axis = rotation.inv().apply([0, 0, 1])

axis_ra = float(
    np.rad2deg(np.arctan2(optical_axis[1], optical_axis[0])) % 360
)
axis_dec = float(
    np.rad2deg(np.arcsin(optical_axis[2]))
)

camera_parameters = {
    "optical_centre_x_px": float(parameters[3]),
    "optical_centre_y_px": float(parameters[4]),
    "focal_scale_px_per_rad": float(np.exp(parameters[5])),
    "radial_k1": float(parameters[6]),
    "radial_k2": float(parameters[7]),
    "optical_axis_ra_deg": axis_ra,
    "optical_axis_dec_deg": axis_dec,
    "rotation_matrix_world_to_camera": rotation.as_matrix().tolist(),
}

report = {
    "phase": 45,
    "title": "Leave-R2C2-out global fisheye calibration",
    "model": "Equidistant fisheye with k1 and k2 radial terms",
    "total_correspondences": int(len(pixels)),
    "training_count": int(len(train_idx)),
    "withheld_r2c2_count": int(len(r2c2_idx)),
    "other_held_out_test_count": int(len(other_test_idx)),
    "training_sections": sorted(set(sections[train_idx])),
    "withheld_section": "R2C2",
    "optimizer_success": bool(fit.success),
    "optimizer_message": fit.message,
    "camera_parameters": camera_parameters,
    "training_metrics": train_metrics,
    "withheld_r2c2_metrics": r2_metrics,
    "other_original_test_metrics": other_test_metrics,
    "per_section_metrics": section_results,
    "interpretation_limits": [
        "R2C2 is completely withheld from parameter fitting.",
        "The 51 R2C2 points are evaluated using a model trained on four other sections.",
        "The correspondences still inherit uncertainty from local plate-solving and catalogue matching.",
        "This is a cross-section consistency test, not an independent camera ground-truth measurement.",
    ],
}

report_path = BASE / "phase45_leave_r2c2_out_report.json"
with report_path.open("w") as f:
    json.dump(report, f, indent=2)

# Plot residual map.
fig, ax = plt.subplots(figsize=(10, 7))

for section in sorted(set(sections)):
    subset = [
        r for r in all_section_records if r["section"] == section
    ]
    x = [r["global_x"] for r in subset]
    y = [r["global_y"] for r in subset]
    e = [r["residual_px"] for r in subset]

    marker = "x" if section == "R2C2" else "o"
    size = 48 if section == "R2C2" else 25

    sc = ax.scatter(
        x, y, c=e, marker=marker, s=size, label=section
    )

ax.set_xlim(0, WIDTH)
ax.set_ylim(HEIGHT, 0)
ax.set_aspect("equal")
ax.set_xlabel("Global image X (pixels)")
ax.set_ylabel("Global image Y (pixels)")
ax.set_title("Phase 45 — calibration trained without R2C2")
ax.legend()
fig.colorbar(sc, ax=ax, label="Residual (pixels)")
fig.tight_layout()
fig.savefig(OUT / "phase45_leave_r2c2_out_residual_map.png", dpi=180)
plt.close(fig)

# Plot residual distribution by section.
fig, ax = plt.subplots(figsize=(9, 6))
labels = sorted(section_results)
values = [
    [
        r["residual_px"]
        for r in all_section_records
        if r["section"] == section
    ]
    for section in labels
]

ax.boxplot(values, tick_labels=labels, showfliers=True)
ax.set_ylabel("Residual magnitude (pixels)")
ax.set_title("Phase 45 — per-section residual distribution")
ax.grid(True, axis="y", alpha=0.25)
fig.tight_layout()
fig.savefig(OUT / "phase45_section_boxplot.png", dpi=180)
plt.close(fig)

print("\n" + "=" * 70)
print("PHASE 45 RESULTS")
print("=" * 70)

print("\nWITHHELD R2C2 — NEVER USED FOR FITTING")
for key, value in r2_metrics.items():
    print(f"  {key}: {value}")

print("\nOTHER SECTIONS — TRAINING DATA")
for key, value in train_metrics.items():
    print(f"  {key}: {value}")

print("\nOTHER ORIGINAL HELD-OUT TEST POINTS")
for key, value in other_test_metrics.items():
    print(f"  {key}: {value}")

print("\nPER-SECTION RESULTS")
for section, result in section_results.items():
    print(
        f"  {section}: n={result['count']}, "
        f"median={result['median_error_px']:.3f}px, "
        f"RMSE={result['rmse_px']:.3f}px, "
        f"max={result['max_error_px']:.3f}px"
    )

print("\nCAMERA PARAMETERS")
for key, value in camera_parameters.items():
    if key != "rotation_matrix_world_to_camera":
        print(f"  {key}: {value}")

print("\nOUTPUTS")
print("Report:", report_path)
print("Residual CSV:", csv_path)
print("Residual map:", OUT / "phase45_leave_r2c2_out_residual_map.png")
print("Section boxplot:", OUT / "phase45_section_boxplot.png")

print("\nPHASE 45 COMPLETED SUCCESSFULLY")
