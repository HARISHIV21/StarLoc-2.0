import csv
import json
from pathlib import Path

import numpy as np
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation

BASE = Path("research/real_image")
INPUT = (
    BASE / "results/ASK033/phase49_cross_section_consistency/"
    "phase49_cross_section_point_comparison.csv"
)
OUT = BASE / "results/ASK033/phase57_leave_one_section_out"
OUT.mkdir(parents=True, exist_ok=True)

with INPUT.open(newline="") as f:
    all_rows = list(csv.DictReader(f))

rows = [
    r for r in all_rows
    if float(r["local_wcs_candidate_error_px"]) <= 1.0
]

sections = sorted(set(r["section"] for r in rows))

xy = np.array([
    [float(r["global_x"]), float(r["global_y"])]
    for r in rows
])

ra = np.deg2rad([float(r["hip_ra_deg"]) for r in rows])
dec = np.deg2rad([float(r["hip_dec_deg"]) for r in rows])

world = np.column_stack([
    np.cos(dec) * np.cos(ra),
    np.cos(dec) * np.sin(ra),
    np.sin(dec),
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

    radial = focal * (theta + k1 * theta**3 + k2 * theta**5)
    safe_rho = np.maximum(rho, 1e-12)

    predicted = np.column_stack([
        cx + radial * camera[:, 0] / safe_rho,
        cy + radial * camera[:, 1] / safe_rho,
    ])

    predicted[z <= 0] = 1e6
    return predicted

lower = np.array([
    -np.inf, -np.inf, -np.inf,
    0, 0, np.log(100), -1, -1
])
upper = np.array([
    np.inf, np.inf, np.inf,
    1920, 1440, np.log(3000), 1, 1
])

def fit_model(train_idx):
    mean_direction = np.mean(world[train_idx], axis=0)
    mean_direction /= np.linalg.norm(mean_direction)

    initial_rotation, _ = Rotation.align_vectors(
        np.array([[0.0, 0.0, 1.0]]),
        mean_direction.reshape(1, 3)
    )

    initial = np.array([
        *initial_rotation.as_rotvec(),
        960, 720, np.log(700), 0, 0
    ])

    def residual(params):
        return (
            project(params, world[train_idx]) - xy[train_idx]
        ).ravel()

    fit = least_squares(
        residual,
        initial,
        bounds=(lower, upper),
        loss="soft_l1",
        f_scale=2.5,
        max_nfev=5000,
    )

    if not fit.success:
        raise RuntimeError(fit.message)

    return fit

def metrics(errors):
    return {
        "count": int(len(errors)),
        "median_px": float(np.median(errors)),
        "mean_px": float(np.mean(errors)),
        "rmse_px": float(np.sqrt(np.mean(errors**2))),
        "p90_px": float(np.percentile(errors, 90)),
        "max_px": float(np.max(errors)),
        "within_1px": int(np.sum(errors <= 1)),
        "within_2px": int(np.sum(errors <= 2)),
        "within_3px": int(np.sum(errors <= 3)),
        "within_5px": int(np.sum(errors <= 5)),
    }

results = []
point_results = []

print("=" * 72)
print("STARLOC — PHASE 57: LEAVE-ONE-SECTION-OUT VALIDATION")
print("=" * 72)
print(f"Strict correspondences: {len(rows)}")
print("Selection: local WCS residual <= 1 pixel")

for held_section in sections:
    test_idx = np.array([
        i for i, r in enumerate(rows)
        if r["section"] == held_section
    ], dtype=int)

    train_idx = np.array([
        i for i, r in enumerate(rows)
        if r["section"] != held_section
    ], dtype=int)

    if len(test_idx) < 1 or len(train_idx) < 20:
        print(f"Skipping {held_section}: insufficient data")
        continue

    fit = fit_model(train_idx)

    train_errors = np.linalg.norm(
        project(fit.x, world[train_idx]) - xy[train_idx], axis=1
    )
    test_errors = np.linalg.norm(
        project(fit.x, world[test_idx]) - xy[test_idx], axis=1
    )

    train_metrics = metrics(train_errors)
    test_metrics = metrics(test_errors)

    result = {
        "held_out_section": held_section,
        "training_sections": [
            s for s in sections if s != held_section
        ],
        "training": train_metrics,
        "held_out": test_metrics,
        "optimizer_success": bool(fit.success),
        "parameters": {
            "optical_centre_x_px": float(fit.x[3]),
            "optical_centre_y_px": float(fit.x[4]),
            "focal_scale_px_per_rad": float(np.exp(fit.x[5])),
            "radial_k1": float(fit.x[6]),
            "radial_k2": float(fit.x[7]),
        }
    }
    results.append(result)

    print(f"\nHELD OUT: {held_section}")
    print(f"  Training points: {len(train_idx)}")
    print(f"  Test points:     {len(test_idx)}")
    print(f"  Training RMSE:   {train_metrics['rmse_px']:.3f} px")
    print(f"  Test median:     {test_metrics['median_px']:.3f} px")
    print(f"  Test RMSE:       {test_metrics['rmse_px']:.3f} px")
    print(f"  Test maximum:    {test_metrics['max_px']:.3f} px")

    predictions = project(fit.x, world[test_idx])

    for j, idx in enumerate(test_idx):
        point_results.append({
            "held_out_section": held_section,
            "source_section": rows[idx]["section"],
            "global_x": float(xy[idx, 0]),
            "global_y": float(xy[idx, 1]),
            "predicted_x": float(predictions[j, 0]),
            "predicted_y": float(predictions[j, 1]),
            "residual_px": float(test_errors[j]),
        })

report = {
    "phase": 57,
    "title": "Leave-one-section-out global fisheye validation",
    "selection": "local_wcs_candidate_error_px <= 1.0",
    "total_strict_points": len(rows),
    "folds": results,
    "limitations": [
        "Calibration correspondences were selected using local-WCS residuals.",
        "Local WCS associations are not independent ground truth.",
        "All sections originate from one image and one camera.",
        "R2C1 has only four strict points, so its fold is weakly supported."
    ]
}

report_path = OUT / "phase57_leave_one_section_out_report.json"
report_path.write_text(json.dumps(report, indent=2))

csv_path = OUT / "phase57_held_out_predictions.csv"
with csv_path.open("w", newline="") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=list(point_results[0].keys())
    )
    writer.writeheader()
    writer.writerows(point_results)

print("\n" + "=" * 72)
print("PHASE 57 COMPLETE")
print("Report:", report_path)
print("Predictions:", csv_path)
print("=" * 72)
