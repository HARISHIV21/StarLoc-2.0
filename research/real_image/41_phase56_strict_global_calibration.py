import csv
import json
from pathlib import Path

import numpy as np
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation

BASE = Path("research/real_image")
INPUT = (
    BASE / "results/ASK033/phase49_cross_section_consistency/"
    / "phase49_cross_section_point_comparison.csv"
)
PHASE38 = BASE / "phase38_global_calibration_report.json"
OUT = BASE / "results/ASK033/phase56_strict_global_calibration"
OUT.mkdir(parents=True, exist_ok=True)

print("=" * 76)
print("STARLOC 2.0 — PHASE 56")
print("STRICT-SUBSET GLOBAL FISHEYE CALIBRATION")
print("=" * 76)

with INPUT.open(newline="") as f:
    all_rows = list(csv.DictReader(f))

rows = [
    r for r in all_rows
    if float(r["local_wcs_candidate_error_px"]) <= 1.0
]

if len(rows) < 30:
    raise RuntimeError(
        f"Insufficient strict correspondences: {len(rows)}"
    )

print(f"\nOriginal correspondences: {len(all_rows)}")
print(f"Strict correspondences: {len(rows)}")
print("Threshold: local WCS residual <= 1.0 px")

sections = sorted(set(r["section"] for r in rows))
print("Sections:", sections)

for section in sections:
    count = sum(r["section"] == section for r in rows)
    print(f"  {section}: {count}")

xy = np.array([
    [float(r["global_x"]), float(r["global_y"])]
    for r in rows
])

ra = np.deg2rad([
    float(r["hip_ra_deg"]) for r in rows
])
dec = np.deg2rad([
    float(r["hip_dec_deg"]) for r in rows
])

world = np.column_stack([
    np.cos(dec) * np.cos(ra),
    np.cos(dec) * np.sin(ra),
    np.sin(dec),
])

# Deterministic 80/20 split.
order = np.arange(len(rows))
train_idx = order[order % 5 != 0]
test_idx = order[order % 5 == 0]

if len(test_idx) < 8:
    raise RuntimeError("Not enough held-out test points.")

print(f"\nTraining: {len(train_idx)}")
print(f"Held-out test: {len(test_idx)}")

# Initial orientation: align mean catalogue direction with camera +Z.
mean_direction = np.mean(world[train_idx], axis=0)
mean_direction /= np.linalg.norm(mean_direction)

initial_rotation, _ = Rotation.align_vectors(
    np.array([[0.0, 0.0, 1.0]]),
    mean_direction.reshape(1, 3)
)

initial = np.array([
    *initial_rotation.as_rotvec(),
    960.0,
    720.0,
    np.log(700.0),
    0.0,
    0.0,
])

lower = np.array([
    -np.inf, -np.inf, -np.inf,
    0.0, 0.0, np.log(100.0), -1.0, -1.0
])
upper = np.array([
    np.inf, np.inf, np.inf,
    1920.0, 1440.0, np.log(3000.0), 1.0, 1.0
])

def project(params, vectors):
    rotation = Rotation.from_rotvec(params[:3])
    camera = rotation.apply(vectors)

    cx, cy = params[3:5]
    focal = np.exp(params[5])
    k1, k2 = params[6:8]

    z = camera[:, 2]
    rho = np.hypot(camera[:, 0], camera[:, 1])
    theta = np.arctan2(rho, z)

    radial = focal * (
        theta + k1 * theta**3 + k2 * theta**5
    )

    safe_rho = np.maximum(rho, 1e-12)

    predicted = np.column_stack([
        cx + radial * camera[:, 0] / safe_rho,
        cy + radial * camera[:, 1] / safe_rho,
    ])

    behind = z <= 0
    predicted[behind] = 1e6

    return predicted

def residual(params, indices):
    predicted = project(params, world[indices])
    return (predicted - xy[indices]).ravel()

print("\nOptimising strict-subset model...")

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
    print("Optimizer message:", fit.message)

def metrics(indices):
    predicted = project(fit.x, world[indices])
    errors = np.linalg.norm(predicted - xy[indices], axis=1)

    return {
        "count": int(len(errors)),
        "median_px": float(np.median(errors)),
        "mean_px": float(np.mean(errors)),
        "rmse_px": float(np.sqrt(np.mean(errors**2))),
        "p90_px": float(np.percentile(errors, 90)),
        "max_px": float(np.max(errors)),
        "within_1px": int(np.sum(errors <= 1.0)),
        "within_2px": int(np.sum(errors <= 2.0)),
        "within_3px": int(np.sum(errors <= 3.0)),
        "within_5px": int(np.sum(errors <= 5.0)),
    }

train_metrics = metrics(train_idx)
test_metrics = metrics(test_idx)
all_metrics = metrics(order)

rotation = Rotation.from_rotvec(fit.x[:3])
axis_camera = rotation.inv().apply([0.0, 0.0, 1.0])

axis_ra = np.degrees(
    np.arctan2(axis_camera[1], axis_camera[0])
) % 360
axis_dec = np.degrees(
    np.arcsin(np.clip(axis_camera[2], -1, 1))
)

parameters = {
    "optical_centre_x_px": float(fit.x[3]),
    "optical_centre_y_px": float(fit.x[4]),
    "focal_scale_px_per_rad": float(np.exp(fit.x[5])),
    "radial_k1": float(fit.x[6]),
    "radial_k2": float(fit.x[7]),
    "optical_axis_ra_deg": float(axis_ra),
    "optical_axis_dec_deg": float(axis_dec),
}

print("\n" + "=" * 76)
print("PHASE 56 RESULTS")
print("=" * 76)

print("\nPARAMETERS")
for key, value in parameters.items():
    print(f"  {key}: {value:.8f}")

for label, result in [
    ("TRAINING", train_metrics),
    ("HELD-OUT TEST", test_metrics),
    ("ALL STRICT DATA", all_metrics),
]:
    print(f"\n{label}")
    for key, value in result.items():
        if isinstance(value, float):
            print(f"  {key}: {value:.4f}")
        else:
            print(f"  {key}: {value}")

phase38 = json.loads(PHASE38.read_text())
old = phase38["parameters"]
old_test = phase38["held_out_test_metrics"]

comparison = {
    "phase38": {
        "optical_centre_x_px": old["optical_centre_x_px"],
        "optical_centre_y_px": old["optical_centre_y_px"],
        "focal_scale_px_per_rad": old["focal_scale_px_per_rad"],
        "radial_k1": old["radial_k1"],
        "radial_k2": old["radial_k2"],
        "test_median_px": old_test["median_error_px"],
        "test_rmse_px": old_test["rmse_px"],
    },
    "phase56": {
        **parameters,
        "test_median_px": test_metrics["median_px"],
        "test_rmse_px": test_metrics["rmse_px"],
    },
}

print("\nPHASE 38 vs PHASE 56")
for key in comparison["phase38"]:
    print(
        f"  {key}: "
        f"{comparison['phase38'][key]:.6f} -> "
        f"{comparison['phase56'][key]:.6f}"
    )

report = {
    "phase": 56,
    "title": "Strict-subset global fisheye calibration",
    "input": str(INPUT),
    "selection": {
        "criterion": "local_wcs_candidate_error_px <= 1.0",
        "total_original": len(all_rows),
        "strict_count": len(rows),
        "sections": sections,
        "training_count": len(train_idx),
        "test_count": len(test_idx),
    },
    "optimizer_success": bool(fit.success),
    "optimizer_message": str(fit.message),
    "parameters": parameters,
    "training_metrics": train_metrics,
    "held_out_test_metrics": test_metrics,
    "all_data_metrics": all_metrics,
    "phase38_comparison": comparison,
    "limitations": [
        "The strict subset is selected using residuals from local WCS solutions.",
        "Local WCS catalogue associations are not independent ground truth.",
        "The held-out split is internal to one image and one camera.",
        "This is an exploratory model, not a validated production calibration.",
    ],
}

report_path = BASE / "phase56_strict_global_calibration_report.json"
report_path.write_text(json.dumps(report, indent=2))

predicted = project(fit.x, world)
point_path = OUT / "phase56_strict_point_residuals.csv"

with point_path.open("w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow([
        "section", "global_x", "global_y",
        "predicted_x", "predicted_y",
        "residual_px", "dataset", "local_wcs_residual_px"
    ])

    for i, r in enumerate(rows):
        error = float(np.linalg.norm(predicted[i] - xy[i]))
        writer.writerow([
            r["section"],
            xy[i, 0], xy[i, 1],
            predicted[i, 0], predicted[i, 1],
            error,
            "test" if i in test_idx else "train",
            r["local_wcs_candidate_error_px"],
        ])

print("\nOUTPUTS")
print("Report:", report_path)
print("Point residuals:", point_path)
print("\nOriginal Phase 38 files were not modified.")
print("PHASE 56 COMPLETED")
