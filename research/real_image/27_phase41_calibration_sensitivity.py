import csv
import json
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation

BASE = Path("research/real_image")
RESULTS = BASE / "results/ASK033"
PHASE37 = RESULTS / "phase37_validation/phase37_all_matches.csv"
PHASE38 = RESULTS / "phase38_global_calibration/phase38_global_fit_residuals.csv"
ORIGINAL_REPORT = BASE / "phase38_global_calibration_report.json"

OUT = RESULTS / "phase41_sensitivity"
OUT.mkdir(parents=True, exist_ok=True)

WIDTH, HEIGHT = 1920, 1440

OFFSETS = {
    "R1C2": (640, 0),
    "R2C1": (0, 480),
    "R3C1": (0, 960),
    "R3C2": (640, 960),
    "R2C2": (640, 480),
}

def read_csv(path):
    if not path.exists():
        raise FileNotFoundError(path)
    with path.open(newline="") as f:
        return list(csv.DictReader(f))

phase37 = read_csv(PHASE37)
phase38 = read_csv(PHASE38)

with ORIGINAL_REPORT.open() as f:
    original_report = json.load(f)

# Reconstruct the exact Phase 38 correspondence order.
pixels = []
sky_vectors = []
sections = []
keys = []

for row in phase37:
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
    keys.append((section, round(x, 3), round(y, 3)))

pixels = np.asarray(pixels, dtype=float)
sky_vectors = np.asarray(sky_vectors, dtype=float)
sections = np.asarray(sections)

if len(pixels) != 233:
    raise RuntimeError(f"Expected 233 matches, found {len(pixels)}")

# Recover the saved Phase 38 training/test labels by exact rounded coordinates.
saved = {}
for row in phase38:
    key = (
        row["section"],
        round(float(row["global_x"]), 3),
        round(float(row["global_y"]), 3),
    )
    saved[key] = row

if len(saved) != len(phase38):
    raise RuntimeError("Duplicate coordinate keys in Phase 38 residual file.")

datasets = []
for key in keys:
    if key not in saved:
        raise RuntimeError(f"Could not match Phase 37 point to Phase 38: {key}")
    datasets.append(saved[key]["dataset"])

datasets = np.asarray(datasets)
order = np.arange(len(pixels))
train_idx = np.where(datasets == "train")[0]
test_idx = np.where(datasets == "test")[0]

if len(train_idx) != 186 or len(test_idx) != 47:
    raise RuntimeError(
        f"Unexpected split: {len(train_idx)} train, {len(test_idx)} test"
    )

# Reproduce the exact Phase 38 initialization.
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

def fit_model(indices):
    return least_squares(
        residual,
        initial.copy(),
        args=(indices,),
        bounds=(lower, upper),
        loss="soft_l1",
        f_scale=2.5,
        max_nfev=5000,
        verbose=0,
    )

def metrics(parameters, indices):
    predicted, z = project(parameters, sky_vectors[indices])
    errors = np.linalg.norm(predicted - pixels[indices], axis=1)

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
    }, errors

def parameter_summary(parameters):
    rot = Rotation.from_rotvec(parameters[:3])
    axis = rot.inv().apply([0, 0, 1])

    return {
        "optical_centre_x_px": float(parameters[3]),
        "optical_centre_y_px": float(parameters[4]),
        "focal_scale_px_per_rad": float(np.exp(parameters[5])),
        "radial_k1": float(parameters[6]),
        "radial_k2": float(parameters[7]),
        "optical_axis_ra_deg": float(
            np.rad2deg(np.arctan2(axis[1], axis[0])) % 360
        ),
        "optical_axis_dec_deg": float(
            np.rad2deg(np.arcsin(axis[2]))
        ),
        "rotation_matrix_world_to_camera": rot.as_matrix().tolist(),
    }

print("=" * 70)
print("STARLOC 2.0 — PHASE 41")
print("GLOBAL FISHEYE CALIBRATION SENSITIVITY TEST")
print("=" * 70)
print(f"Correspondences: {len(pixels)}")
print(f"Training: {len(train_idx)}")
print(f"Unchanged held-out test: {len(test_idx)}")

# Fit 1: reproduce original Phase 38.
print("\n[1/2] Reproducing original Phase 38 calibration...")
baseline = fit_model(train_idx)

if not baseline.success:
    raise RuntimeError(f"Baseline reproduction failed: {baseline.message}")

baseline_params = parameter_summary(baseline.x)
saved_params = original_report["parameters"]

checks = {
    "centre_x": abs(
        baseline_params["optical_centre_x_px"]
        - saved_params["optical_centre_x_px"]
    ),
    "centre_y": abs(
        baseline_params["optical_centre_y_px"]
        - saved_params["optical_centre_y_px"]
    ),
    "focal": abs(
        baseline_params["focal_scale_px_per_rad"]
        - saved_params["focal_scale_px_per_rad"]
    ),
    "k1": abs(
        baseline_params["radial_k1"] - saved_params["radial_k1"]
    ),
    "k2": abs(
        baseline_params["radial_k2"] - saved_params["radial_k2"]
    ),
}

print("Baseline parameter reproduction differences:")
for name, difference in checks.items():
    print(f"  {name}: {difference:.10f}")

if (
    checks["centre_x"] > 0.05
    or checks["centre_y"] > 0.05
    or checks["focal"] > 0.1
    or checks["k1"] > 1e-4
    or checks["k2"] > 1e-4
):
    raise RuntimeError(
        "Baseline does not reproduce Phase 38 closely. "
        "Sensitivity test stopped to avoid an invalid comparison."
    )

# Identify the four largest training residuals from the saved Phase 38 fit.
train_residuals = np.array([
    float(saved[key]["residual_px"])
    for key in keys
])

training_errors = train_residuals[train_idx]
worst_order = np.argsort(training_errors)[-4:][::-1]
excluded_idx = train_idx[worst_order]

if len(excluded_idx) != 4:
    raise RuntimeError("Could not identify exactly four training outliers.")

print("\nFour training points selected for diagnostic exclusion:")
excluded_rows = []

for idx in excluded_idx:
    key = keys[idx]
    row = saved[key]
    info = {
        "section": sections[idx],
        "global_x": float(pixels[idx, 0]),
        "global_y": float(pixels[idx, 1]),
        "phase38_residual_px": float(row["residual_px"]),
    }
    excluded_rows.append(info)
    print(
        f"  {info['section']} ({info['global_x']:.3f}, "
        f"{info['global_y']:.3f}) — "
        f"{info['phase38_residual_px']:.3f} px"
    )

# Fit 2: exclude only those four training points.
filtered_train_idx = np.array([
    idx for idx in train_idx if idx not in set(excluded_idx)
])

print("\n[2/2] Fitting with four training outliers excluded...")
filtered = fit_model(filtered_train_idx)

if not filtered.success:
    raise RuntimeError(f"Filtered fit failed: {filtered.message}")

# Evaluate both models on exactly the same 47 held-out test points.
baseline_train_metrics, baseline_train_errors = metrics(
    baseline.x, train_idx
)
baseline_test_metrics, baseline_test_errors = metrics(
    baseline.x, test_idx
)

filtered_train_metrics, filtered_train_errors = metrics(
    filtered.x, filtered_train_idx
)
filtered_test_metrics, filtered_test_errors = metrics(
    filtered.x, test_idx
)

baseline_all_metrics, _ = metrics(baseline.x, order)
filtered_all_metrics, _ = metrics(filtered.x, order)

baseline_summary = parameter_summary(baseline.x)
filtered_summary = parameter_summary(filtered.x)

parameter_changes = {}
for key in [
    "optical_centre_x_px",
    "optical_centre_y_px",
    "focal_scale_px_per_rad",
    "radial_k1",
    "radial_k2",
    "optical_axis_ra_deg",
    "optical_axis_dec_deg",
]:
    before = baseline_summary[key]
    after = filtered_summary[key]
    parameter_changes[key] = {
        "phase38_baseline": before,
        "phase41_filtered": after,
        "absolute_change": float(abs(after - before)),
    }

# Save comparison CSV.
comparison_path = OUT / "phase41_residual_comparison.csv"
with comparison_path.open("w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow([
        "section", "global_x", "global_y", "dataset",
        "excluded_from_filtered_training",
        "phase38_baseline_residual_px",
        "phase41_filtered_residual_px",
    ])

    for idx in order:
        b_pred, _ = project(baseline.x, sky_vectors[[idx]])
        f_pred, _ = project(filtered.x, sky_vectors[[idx]])

        b_error = float(np.linalg.norm(b_pred[0] - pixels[idx]))
        f_error = float(np.linalg.norm(f_pred[0] - pixels[idx]))

        writer.writerow([
            sections[idx],
            pixels[idx, 0],
            pixels[idx, 1],
            datasets[idx],
            bool(idx in excluded_idx),
            b_error,
            f_error,
        ])

report = {
    "phase": 41,
    "purpose": "Sensitivity test excluding four largest Phase 38 training residuals",
    "method": "Same equidistant fisheye model, initialization, bounds, loss and unchanged held-out test set",
    "correspondences": int(len(pixels)),
    "baseline_training_count": int(len(train_idx)),
    "filtered_training_count": int(len(filtered_train_idx)),
    "held_out_test_count": int(len(test_idx)),
    "excluded_training_points": excluded_rows,
    "baseline_reproduction": {
        "optimizer_success": bool(baseline.success),
        "optimizer_message": baseline.message,
        "parameter_differences_from_saved_phase38": checks,
    },
    "baseline": {
        "parameters": baseline_summary,
        "training_metrics": baseline_train_metrics,
        "held_out_test_metrics": baseline_test_metrics,
        "all_data_metrics": baseline_all_metrics,
    },
    "filtered": {
        "optimizer_success": bool(filtered.success),
        "optimizer_message": filtered.message,
        "parameters": filtered_summary,
        "training_metrics": filtered_train_metrics,
        "held_out_test_metrics": filtered_test_metrics,
        "all_data_metrics": filtered_all_metrics,
    },
    "parameter_changes": parameter_changes,
    "interpretation_note": (
        "The four excluded points are removed only from training. "
        "All 47 held-out test points remain unchanged. "
        "This is a sensitivity diagnostic, not automatic rejection "
        "of the correspondences or proof of final calibration."
    ),
}

report_path = BASE / "phase41_calibration_sensitivity_report.json"
with report_path.open("w") as f:
    json.dump(report, f, indent=2)

# Comparison plot: unchanged held-out test residuals.
fig, ax = plt.subplots(figsize=(9, 5))
labels = ["Median", "Mean", "RMSE", "P90", "Maximum"]
metric_keys = [
    "median_error_px",
    "mean_error_px",
    "rmse_px",
    "p90_error_px",
    "max_error_px",
]
x = np.arange(len(labels))
width = 0.36

ax.bar(
    x - width / 2,
    [baseline_test_metrics[k] for k in metric_keys],
    width,
    label="Phase 38 baseline",
)
ax.bar(
    x + width / 2,
    [filtered_test_metrics[k] for k in metric_keys],
    width,
    label="Phase 41 filtered",
)

ax.set_xticks(x)
ax.set_xticklabels(labels)
ax.set_ylabel("Pixel error")
ax.set_title("Held-out test comparison — same 47 points")
ax.legend()
fig.tight_layout()
fig.savefig(OUT / "phase41_test_comparison.png", dpi=160)
plt.close(fig)

# Plot parameter changes.
fig, ax = plt.subplots(figsize=(9, 5))
names = [
    "Centre X",
    "Centre Y",
    "Focal scale",
    "k1",
    "k2",
]
values = [
    parameter_changes["optical_centre_x_px"]["absolute_change"],
    parameter_changes["optical_centre_y_px"]["absolute_change"],
    parameter_changes["focal_scale_px_per_rad"]["absolute_change"],
    parameter_changes["radial_k1"]["absolute_change"],
    parameter_changes["radial_k2"]["absolute_change"],
]
ax.bar(names, values)
ax.set_ylabel("Absolute parameter change")
ax.set_title("Camera parameter sensitivity after excluding four points")
fig.tight_layout()
fig.savefig(OUT / "phase41_parameter_changes.png", dpi=160)
plt.close(fig)

print("\n" + "=" * 70)
print("PHASE 41 RESULTS")
print("=" * 70)

print("\nHELD-OUT TEST — ORIGINAL 47 POINTS")
print(
    f"Baseline: median={baseline_test_metrics['median_error_px']:.4f}px, "
    f"mean={baseline_test_metrics['mean_error_px']:.4f}px, "
    f"RMSE={baseline_test_metrics['rmse_px']:.4f}px, "
    f"max={baseline_test_metrics['max_error_px']:.4f}px"
)
print(
    f"Filtered: median={filtered_test_metrics['median_error_px']:.4f}px, "
    f"mean={filtered_test_metrics['mean_error_px']:.4f}px, "
    f"RMSE={filtered_test_metrics['rmse_px']:.4f}px, "
    f"max={filtered_test_metrics['max_error_px']:.4f}px"
)

print("\nCAMERA PARAMETERS")
for key, change in parameter_changes.items():
    print(
        f"{key}: {change['phase38_baseline']:.8f} -> "
        f"{change['phase41_filtered']:.8f}"
    )

print("\nOUTPUTS")
print("Report:", report_path)
print("Residual comparison:", comparison_path)
print("Test plot:", OUT / "phase41_test_comparison.png")
print("Parameter plot:", OUT / "phase41_parameter_changes.png")

print("\nPHASE 41 COMPLETED SUCCESSFULLY")
