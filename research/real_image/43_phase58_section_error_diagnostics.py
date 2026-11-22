import csv
import json
from pathlib import Path
from collections import defaultdict

import numpy as np
import matplotlib.pyplot as plt

BASE = Path("research/real_image")
INPUT = (
    BASE / "results/ASK033/phase57_leave_one_section_out/"
    / "phase57_held_out_predictions.csv"
)
OUT = BASE / "results/ASK033/phase58_section_error_diagnostics"
OUT.mkdir(parents=True, exist_ok=True)

print("=" * 76)
print("STARLOC 2.0 — PHASE 58")
print("SECTION-DEPENDENT RESIDUAL DIAGNOSTICS")
print("=" * 76)

with INPUT.open(newline="") as f:
    rows = list(csv.DictReader(f))

if not rows:
    raise RuntimeError("Phase 57 prediction file is empty.")

groups = defaultdict(list)
output_rows = []

for r in rows:
    section = r["section"]
    x = float(r["global_x"])
    y = float(r["global_y"])
    px = float(r["predicted_x"])
    py = float(r["predicted_y"])

    # Residual vector: prediction minus observed candidate.
    dx = px - x
    dy = py - y
    error = float(np.hypot(dx, dy))

    record = {
        "section": section,
        "global_x": x,
        "global_y": y,
        "predicted_x": px,
        "predicted_y": py,
        "residual_dx_px": dx,
        "residual_dy_px": dy,
        "residual_magnitude_px": error,
        "held_out_section": r["held_out_section"],
    }

    groups[section].append(record)
    output_rows.append(record)

summary = {}

print("\nSECTION SUMMARY")

for section in sorted(groups):
    data = groups[section]
    dx = np.array([r["residual_dx_px"] for r in data])
    dy = np.array([r["residual_dy_px"] for r in data])
    errors = np.array([r["residual_magnitude_px"] for r in data])

    stats = {
        "count": len(data),
        "mean_dx_px": float(np.mean(dx)),
        "mean_dy_px": float(np.mean(dy)),
        "median_dx_px": float(np.median(dx)),
        "median_dy_px": float(np.median(dy)),
        "median_error_px": float(np.median(errors)),
        "rmse_px": float(np.sqrt(np.mean(errors ** 2))),
        "p90_px": float(np.percentile(errors, 90)),
        "max_px": float(np.max(errors)),
        "within_1px": int(np.sum(errors <= 1)),
        "within_2px": int(np.sum(errors <= 2)),
        "within_3px": int(np.sum(errors <= 3)),
        "within_5px": int(np.sum(errors <= 5)),
    }

    summary[section] = stats

    print(
        f"\n{section}: n={stats['count']}"
        f"\n  Mean residual vector: "
        f"dx={stats['mean_dx_px']:.3f}px, "
        f"dy={stats['mean_dy_px']:.3f}px"
        f"\n  Median error: {stats['median_error_px']:.3f}px"
        f"\n  RMSE: {stats['rmse_px']:.3f}px"
        f"\n  P90: {stats['p90_px']:.3f}px"
        f"\n  Maximum: {stats['max_px']:.3f}px"
    )

# Save point-level residual vectors.
point_csv = OUT / "phase58_residual_vectors.csv"

with point_csv.open("w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=output_rows[0].keys())
    writer.writeheader()
    writer.writerows(output_rows)

# Plot 1: spatial residual vectors.
fig, ax = plt.subplots(figsize=(12, 8))

for section in sorted(groups):
    data = groups[section]
    x = np.array([r["global_x"] for r in data])
    y = np.array([r["global_y"] for r in data])
    dx = np.array([r["residual_dx_px"] for r in data])
    dy = np.array([r["residual_dy_px"] for r in data])

    ax.scatter(x, y, s=16, label=section)
    ax.quiver(
        x, y, dx, dy,
        angles="xy",
        scale_units="xy",
        scale=1,
        width=0.003,
        alpha=0.75,
    )

ax.set_xlim(0, 1920)
ax.set_ylim(1440, 0)
ax.set_aspect("equal")
ax.set_xlabel("Image X (pixels)")
ax.set_ylabel("Image Y (pixels)")
ax.set_title("Phase 57 — Leave-One-Section-Out Residual Vectors")
ax.legend()
ax.grid(alpha=0.2)
fig.tight_layout()

vector_plot = OUT / "phase58_spatial_residual_vectors.png"
fig.savefig(vector_plot, dpi=180)
plt.close(fig)

# Plot 2: error distribution by section.
labels = sorted(groups)
values = [
    [r["residual_magnitude_px"] for r in groups[s]]
    for s in labels
]

fig, ax = plt.subplots(figsize=(10, 6))
ax.boxplot(values, tick_labels=labels, showmeans=True)
ax.set_ylabel("Prediction error (pixels)")
ax.set_title("Phase 57 — Held-Out Error Distribution by Section")
ax.grid(axis="y", alpha=0.25)
fig.tight_layout()

box_plot = OUT / "phase58_section_error_distribution.png"
fig.savefig(box_plot, dpi=180)
plt.close(fig)

report = {
    "phase": 58,
    "title": "Section-dependent residual diagnostics",
    "input": str(INPUT),
    "total_points": len(rows),
    "per_section": summary,
    "interpretation": [
        "Residual vectors show the direction of prediction error.",
        "A consistent mean vector may indicate a systematic section offset.",
        "Large individual errors may indicate outliers or incorrect associations.",
        "This diagnostic does not establish independent astrometric ground truth.",
        "No calibration parameters were modified.",
    ],
}

report_path = BASE / "phase58_section_error_diagnostics_report.json"
report_path.write_text(json.dumps(report, indent=2))

print("\nOUTPUTS")
print("Report:", report_path)
print("Residual vectors:", point_csv)
print("Vector plot:", vector_plot)
print("Error distribution:", box_plot)
print("\nOriginal calibration files preserved.")
print("PHASE 58 COMPLETED")
