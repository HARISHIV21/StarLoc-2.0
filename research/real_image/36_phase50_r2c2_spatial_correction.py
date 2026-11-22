import csv
import json
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

BASE = Path("research/real_image")
RESULTS = BASE / "results/ASK033"
SOURCE = RESULTS / "phase49_cross_section_consistency/phase49_cross_section_point_comparison.csv"
OUT = RESULTS / "phase50_r2c2_spatial_correction"
OUT.mkdir(parents=True, exist_ok=True)

if not SOURCE.exists():
    raise FileNotFoundError(SOURCE)

with SOURCE.open(newline="") as f:
    rows = [
        r for r in csv.DictReader(f)
        if r["section"] == "R2C2"
    ]

if len(rows) != 51:
    raise RuntimeError(f"Expected 51 R2C2 points, found {len(rows)}")

x = np.array([float(r["global_x"]) for r in rows])
y = np.array([float(r["global_y"]) for r in rows])

# Residual vector required to move global prediction onto the detection.
dx = -np.array([float(r["global_candidate_dx"]) for r in rows])
dy = -np.array([float(r["global_candidate_dy"]) for r in rows])

baseline = np.hypot(dx, dy)

# Four high-residual points are excluded from fitting, not deleted.
train = baseline <= 10.0
test = ~train

if train.sum() != 47 or test.sum() != 4:
    raise RuntimeError(
        f"Expected 47 training and 4 diagnostic points after excluding four extreme outliers; "
        f"got {train.sum()} and {test.sum()}"
    )

# Normalize local image coordinates for numerical stability.
xn = (x - 960.0) / 320.0
yn = (y - 720.0) / 240.0

# Affine correction: residual = a + b*x + c*y.
design = np.column_stack([
    np.ones(len(x)),
    xn,
    yn,
])

def fit_model(indices, values):
    return np.linalg.lstsq(
        design[indices],
        values[indices],
        rcond=None
    )[0]

def predict(coefficients):
    return design @ coefficients

# Constant correction.
constant_dx = np.mean(dx[train])
constant_dy = np.mean(dy[train])

constant_pred_dx = np.full(len(rows), constant_dx)
constant_pred_dy = np.full(len(rows), constant_dy)

# Affine correction.
affine_coef_x = fit_model(train, dx)
affine_coef_y = fit_model(train, dy)

affine_pred_dx = predict(affine_coef_x)
affine_pred_dy = predict(affine_coef_y)

constant_error = np.hypot(
    dx - constant_pred_dx,
    dy - constant_pred_dy
)

affine_error = np.hypot(
    dx - affine_pred_dx,
    dy - affine_pred_dy
)

# Leave-one-out cross-validation on the 47 fitting points.
loo_constant = []
loo_affine = []

train_indices = np.where(train)[0]

for held_out in train_indices:
    fit_indices = train.copy()
    fit_indices[held_out] = False

    cx = np.mean(dx[fit_indices])
    cy = np.mean(dy[fit_indices])

    loo_constant.append(
        np.hypot(dx[held_out] - cx, dy[held_out] - cy)
    )

    ax_coef = fit_model(fit_indices, dx)
    ay_coef = fit_model(fit_indices, dy)

    predicted_x = design[held_out] @ ax_coef
    predicted_y = design[held_out] @ ay_coef

    loo_affine.append(
        np.hypot(
            dx[held_out] - predicted_x,
            dy[held_out] - predicted_y
        )
    )

def summarize(values):
    values = np.asarray(values)
    return {
        "count": int(len(values)),
        "median_px": float(np.median(values)),
        "mean_px": float(np.mean(values)),
        "rmse_px": float(np.sqrt(np.mean(values ** 2))),
        "p90_px": float(np.percentile(values, 90)),
        "max_px": float(np.max(values)),
    }

report = {
    "phase": 50,
    "title": "R2C2 spatial residual correction experiment",
    "correspondences": len(rows),
    "training_count": int(train.sum()),
    "diagnostic_count": int(test.sum()),
    "baseline_training_error": summarize(baseline[train]),
    "baseline_diagnostic_error": summarize(baseline[test]),
    "constant_correction": {
        "coefficients_dx": float(constant_dx),
        "coefficients_dy": float(constant_dy),
        "training_error": summarize(constant_error[train]),
        "diagnostic_error": summarize(constant_error[test]),
        "leave_one_out_error": summarize(loo_constant),
    },
    "affine_correction": {
        "coefficients_dx": affine_coef_x.tolist(),
        "coefficients_dy": affine_coef_y.tolist(),
        "training_error": summarize(affine_error[train]),
        "diagnostic_error": summarize(affine_error[test]),
        "leave_one_out_error": summarize(loo_affine),
    },
    "diagnostic_points": [],
    "limitations": [
        "The four diagnostic points were deliberately excluded from fitting.",
        "The affine correction is an exploratory local residual model, not a new physical camera calibration.",
        "The four points are not an independent external validation dataset.",
        "A good correction on training points does not establish generalization beyond R2C2."
    ]
}

for i in np.where(test)[0]:
    report["diagnostic_points"].append({
        "x": float(x[i]),
        "y": float(y[i]),
        "baseline_error_px": float(baseline[i]),
        "constant_corrected_error_px": float(constant_error[i]),
        "affine_corrected_error_px": float(affine_error[i]),
        "affine_predicted_dx_px": float(affine_pred_dx[i]),
        "affine_predicted_dy_px": float(affine_pred_dy[i]),
    })

report_path = BASE / "phase50_r2c2_spatial_correction_report.json"
with report_path.open("w") as f:
    json.dump(report, f, indent=2)

# Save point-level audit.
csv_path = OUT / "phase50_correction_point_audit.csv"

fields = [
    "global_x", "global_y",
    "baseline_error_px",
    "constant_corrected_error_px",
    "affine_corrected_error_px",
    "affine_predicted_dx_px",
    "affine_predicted_dy_px",
    "role",
]

with csv_path.open("w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()

    for i in range(len(rows)):
        writer.writerow({
            "global_x": x[i],
            "global_y": y[i],
            "baseline_error_px": baseline[i],
            "constant_corrected_error_px": constant_error[i],
            "affine_corrected_error_px": affine_error[i],
            "affine_predicted_dx_px": affine_pred_dx[i],
            "affine_predicted_dy_px": affine_pred_dy[i],
            "role": "training" if train[i] else "diagnostic",
        })

# Plot 1: diagnostic four-point comparison.
fig, ax = plt.subplots(figsize=(9, 5))
labels = ["Baseline", "Constant correction", "Affine correction"]
values = [
    baseline[test],
    constant_error[test],
    affine_error[test],
]

positions = np.arange(len(labels))
for i, v in enumerate(values):
    ax.scatter(
        np.full(len(v), i),
        v,
        s=65,
        label=labels[i] if i == 0 else None
    )
    ax.plot(
        [i - 0.15, i + 0.15],
        [np.median(v), np.median(v)],
        linewidth=3
    )

ax.set_xticks(positions)
ax.set_xticklabels(labels)
ax.set_ylabel("Residual error (pixels)")
ax.set_title("Phase 50 — Four excluded R2C2 points")
ax.grid(axis="y", alpha=0.25)
fig.tight_layout()

plot1 = OUT / "phase50_four_point_comparison.png"
fig.savefig(plot1, dpi=180)
plt.close(fig)

# Plot 2: spatial distribution of baseline and affine residuals.
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

for ax, values, title in [
    (axes[0], baseline, "Baseline residual"),
    (axes[1], affine_error, "After affine correction"),
]:
    scatter = ax.scatter(
        x, y, c=values, cmap="viridis",
        s=55, edgecolors="black", linewidths=0.25
    )
    ax.scatter(
        x[test], y[test],
        marker="x", color="red", s=100,
        linewidths=2, label="Excluded diagnostic points"
    )
    ax.set_xlim(640, 1280)
    ax.set_ylim(960, 480)
    ax.set_aspect("equal")
    ax.set_xlabel("Global X (pixels)")
    ax.set_ylabel("Global Y (pixels)")
    ax.set_title(title)
    ax.legend()
    fig.colorbar(scatter, ax=ax, label="Error (pixels)")

fig.suptitle("Phase 50 — R2C2 spatial correction")
fig.tight_layout()

plot2 = OUT / "phase50_spatial_residual_comparison.png"
fig.savefig(plot2, dpi=180)
plt.close(fig)

print("=" * 72)
print("STARLOC 2.0 — PHASE 50")
print("R2C2 SPATIAL RESIDUAL CORRECTION")
print("=" * 72)

print(f"Training points: {train.sum()}")
print(f"Excluded diagnostic points: {test.sum()}")

print("\nBASELINE")
print("  Training:", report["baseline_training_error"])
print("  Diagnostic:", report["baseline_diagnostic_error"])

print("\nCONSTANT CORRECTION")
print("  Training:", report["constant_correction"]["training_error"])
print("  Diagnostic:", report["constant_correction"]["diagnostic_error"])
print("  Leave-one-out:", report["constant_correction"]["leave_one_out_error"])

print("\nAFFINE CORRECTION")
print("  Training:", report["affine_correction"]["training_error"])
print("  Diagnostic:", report["affine_correction"]["diagnostic_error"])
print("  Leave-one-out:", report["affine_correction"]["leave_one_out_error"])

print("\nFOUR EXCLUDED POINTS")
for p in report["diagnostic_points"]:
    print(
        f"  ({p['x']:.1f}, {p['y']:.1f}): "
        f"baseline={p['baseline_error_px']:.2f}px, "
        f"constant={p['constant_corrected_error_px']:.2f}px, "
        f"affine={p['affine_corrected_error_px']:.2f}px"
    )

print("\nOUTPUTS")
print("Report:", report_path)
print("Point audit:", csv_path)
print("Four-point comparison:", plot1)
print("Spatial comparison:", plot2)
print("\nPHASE 50 COMPLETED")
