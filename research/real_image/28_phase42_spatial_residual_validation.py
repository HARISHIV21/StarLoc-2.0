import csv
import json
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import spearmanr, pearsonr

BASE = Path("research/real_image")
RESULTS = BASE / "results/ASK033"
INPUT = RESULTS / "phase41_sensitivity/phase41_residual_comparison.csv"
PHASE38_REPORT = BASE / "phase38_global_calibration_report.json"
PHASE41_REPORT = BASE / "phase41_calibration_sensitivity_report.json"

OUT = RESULTS / "phase42_spatial_validation"
OUT.mkdir(parents=True, exist_ok=True)

WIDTH, HEIGHT = 1920, 1440

def load_csv(path):
    if not path.exists():
        raise FileNotFoundError(path)
    with path.open(newline="") as f:
        return list(csv.DictReader(f))

def load_json(path):
    with path.open() as f:
        return json.load(f)

rows = load_csv(INPUT)
phase38 = load_json(PHASE38_REPORT)
phase41 = load_json(PHASE41_REPORT)

if len(rows) != 233:
    raise RuntimeError(f"Expected 233 correspondences, found {len(rows)}")

x = np.array([float(r["global_x"]) for r in rows])
y = np.array([float(r["global_y"]) for r in rows])
baseline_error = np.array([
    float(r["phase38_baseline_residual_px"]) for r in rows
])
filtered_error = np.array([
    float(r["phase41_filtered_residual_px"]) for r in rows
])
sections = np.array([r["section"] for r in rows])
datasets = np.array([r["dataset"] for r in rows])
excluded = np.array([
    r["excluded_from_filtered_training"].strip().lower() == "true"
    for r in rows
])

centres = {
    "baseline": (
        phase38["parameters"]["optical_centre_x_px"],
        phase38["parameters"]["optical_centre_y_px"],
    ),
    "filtered": (
        phase41["filtered"]["parameters"]["optical_centre_x_px"],
        phase41["filtered"]["parameters"]["optical_centre_y_px"],
    ),
}

def safe_correlation(a, b, method):
    if len(a) < 3 or np.std(a) == 0 or np.std(b) == 0:
        return {"coefficient": None, "p_value": None}
    result = pearsonr(a, b) if method == "pearson" else spearmanr(a, b)
    return {
        "coefficient": float(result.statistic),
        "p_value": float(result.pvalue),
    }

def residual_summary(values):
    return {
        "count": int(len(values)),
        "median_px": float(np.median(values)),
        "mean_px": float(np.mean(values)),
        "rmse_px": float(np.sqrt(np.mean(values**2))),
        "p90_px": float(np.percentile(values, 90)),
        "maximum_px": float(np.max(values)),
        "count_over_2px": int(np.sum(values > 2)),
        "count_over_3px": int(np.sum(values > 3)),
        "count_over_5px": int(np.sum(values > 5)),
        "count_over_10px": int(np.sum(values > 10)),
    }

def analyse_model(name, errors, centre):
    cx, cy = centre
    radius = np.sqrt((x - cx)**2 + (y - cy)**2)
    normalized_radius = radius / (0.5 * min(WIDTH, HEIGHT))

    pearson = safe_correlation(radius, errors, "pearson")
    spearman = safe_correlation(radius, errors, "spearman")

    # Fixed radial bands make model comparisons consistent.
    radial_edges = [0, 200, 400, 600, 800, 1000, 1200]
    radial_bands = []

    for lo, hi in zip(radial_edges[:-1], radial_edges[1:]):
        mask = (radius >= lo) & (radius < hi)
        if np.any(mask):
            radial_bands.append({
                "radius_min_px": lo,
                "radius_max_px": hi,
                **residual_summary(errors[mask]),
            })

    section_stats = {}
    for section in sorted(set(sections)):
        mask = sections == section
        section_stats[section] = residual_summary(errors[mask])

    split_stats = {}
    for split in ["train", "test"]:
        mask = datasets == split
        split_stats[split] = residual_summary(errors[mask])

    return {
        "optical_centre_px": {"x": float(cx), "y": float(cy)},
        "overall": residual_summary(errors),
        "radial_distance_correlation": {
            "pearson": pearson,
            "spearman": spearman,
            "interpretation": (
                "Positive correlation means residual magnitude tends to "
                "increase farther from the estimated optical centre. "
                "Correlation alone does not prove optical distortion."
            ),
        },
        "radial_bands": radial_bands,
        "section_statistics": section_stats,
        "dataset_statistics": split_stats,
        "normalized_radius_range": [
            float(np.min(normalized_radius)),
            float(np.max(normalized_radius)),
        ],
    }, radius

baseline_report, baseline_radius = analyse_model(
    "baseline", baseline_error, centres["baseline"]
)
filtered_report, filtered_radius = analyse_model(
    "filtered", filtered_error, centres["filtered"]
)

# Spatial grid: median residual in each 4x4 image region.
def spatial_grid(errors):
    grid = np.full((4, 4), np.nan)
    counts = np.zeros((4, 4), dtype=int)

    col = np.clip((x / WIDTH * 4).astype(int), 0, 3)
    row = np.clip((y / HEIGHT * 4).astype(int), 0, 3)

    for r in range(4):
        for c in range(4):
            mask = (row == r) & (col == c)
            counts[r, c] = int(np.sum(mask))
            if np.any(mask):
                grid[r, c] = float(np.median(errors[mask]))

    return grid, counts

baseline_grid, grid_counts = spatial_grid(baseline_error)
filtered_grid, _ = spatial_grid(filtered_error)

# Write per-point spatial audit.
point_csv = OUT / "phase42_point_spatial_audit.csv"
with point_csv.open("w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow([
        "section", "global_x", "global_y", "dataset",
        "excluded_from_phase41_training",
        "baseline_radius_px", "filtered_radius_px",
        "baseline_residual_px", "filtered_residual_px",
    ])

    for i in range(len(rows)):
        writer.writerow([
            sections[i], x[i], y[i], datasets[i], excluded[i],
            baseline_radius[i], filtered_radius[i],
            baseline_error[i], filtered_error[i],
        ])

# Save spatial grid table.
grid_csv = OUT / "phase42_spatial_grid.csv"
with grid_csv.open("w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow([
        "grid_row", "grid_column", "point_count",
        "baseline_median_residual_px",
        "filtered_median_residual_px",
    ])
    for r in range(4):
        for c in range(4):
            writer.writerow([
                r + 1, c + 1, grid_counts[r, c],
                baseline_grid[r, c], filtered_grid[r, c],
            ])

# Save the machine-readable report.
report = {
    "phase": 42,
    "title": "Spatial residual and distortion validation",
    "input_correspondences": len(rows),
    "image_dimensions_px": [WIDTH, HEIGHT],
    "method": (
        "Spatial analysis of Phase 38 baseline and Phase 41 filtered "
        "pixel residual magnitudes. No new fitting or correspondence "
        "rejection was performed."
    ),
    "excluded_points_from_phase41": int(np.sum(excluded)),
    "baseline": baseline_report,
    "filtered": filtered_report,
    "spatial_grid": {
        "description": "4x4 image grid; values are median residual magnitudes in pixels",
        "baseline_median_residual_px": [
            [None if np.isnan(v) else float(v) for v in row]
            for row in baseline_grid
        ],
        "filtered_median_residual_px": [
            [None if np.isnan(v) else float(v) for v in row]
            for row in filtered_grid
        ],
        "point_counts": grid_counts.tolist(),
    },
    "limitations": [
        "Residual magnitude does not retain the direction of pixel error.",
        "A radial correlation does not independently establish optical distortion.",
        "The correspondence set originates from local WCS solutions.",
        "The five sections do not provide uniform full-image coverage.",
        "This analysis does not establish final camera calibration accuracy.",
    ],
}

report_path = BASE / "phase42_spatial_validation_report.json"
with report_path.open("w") as f:
    json.dump(report, f, indent=2)

# Plot 1: residual magnitude versus distance from optical centre.
fig, ax = plt.subplots(figsize=(10, 6))
ax.scatter(
    baseline_radius, baseline_error,
    s=20, alpha=0.65, label="Phase 38 baseline"
)
ax.scatter(
    filtered_radius, filtered_error,
    s=20, alpha=0.65, label="Phase 41 filtered"
)
ax.set_xlabel("Distance from estimated optical centre (pixels)")
ax.set_ylabel("Residual magnitude (pixels)")
ax.set_title("Phase 42 — residual magnitude versus image radius")
ax.grid(True, alpha=0.25)
ax.legend()
fig.tight_layout()
fig.savefig(OUT / "phase42_radial_residuals.png", dpi=160)
plt.close(fig)

# Plot 2: residual distribution by section.
section_order = sorted(set(sections))
baseline_data = [
    baseline_error[sections == s] for s in section_order
]
filtered_data = [
    filtered_error[sections == s] for s in section_order
]

fig, axes = plt.subplots(1, 2, figsize=(13, 5), sharey=True)
axes[0].boxplot(baseline_data, tick_labels=section_order, showfliers=True)
axes[0].set_title("Phase 38 baseline")
axes[0].set_ylabel("Residual magnitude (pixels)")
axes[1].boxplot(filtered_data, tick_labels=section_order, showfliers=True)
axes[1].set_title("Phase 41 filtered")
for ax in axes:
    ax.set_xlabel("Image section")
    ax.grid(True, axis="y", alpha=0.25)
fig.suptitle("Residual distribution by image section")
fig.tight_layout()
fig.savefig(OUT / "phase42_section_residuals.png", dpi=160)
plt.close(fig)

# Plot 3: spatial grid median residual heatmaps.
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

for ax, grid, title in [
    (axes[0], baseline_grid, "Phase 38 baseline"),
    (axes[1], filtered_grid, "Phase 41 filtered"),
]:
    im = ax.imshow(grid, origin="upper", aspect="auto")
    ax.set_title(title)
    ax.set_xlabel("Image grid column")
    ax.set_ylabel("Image grid row")
    ax.set_xticks(range(4), ["1", "2", "3", "4"])
    ax.set_yticks(range(4), ["1", "2", "3", "4"])

    for r in range(4):
        for c in range(4):
            if not np.isnan(grid[r, c]):
                ax.text(
                    c, r, f"{grid[r,c]:.2f}\n(n={grid_counts[r,c]})",
                    ha="center", va="center"
                )

    fig.colorbar(im, ax=ax, label="Median residual (pixels)")

fig.suptitle("Spatial distribution of residuals")
fig.tight_layout()
fig.savefig(OUT / "phase42_spatial_heatmaps.png", dpi=160)
plt.close(fig)

# Console summary.
print("=" * 70)
print("STARLOC 2.0 — PHASE 42")
print("SPATIAL RESIDUAL AND DISTORTION VALIDATION")
print("=" * 70)

for name, result in [
    ("PHASE 38 BASELINE", baseline_report),
    ("PHASE 41 FILTERED", filtered_report),
]:
    print(f"\n{name}")
    print("Overall median:", f"{result['overall']['median_px']:.4f}px")
    print("Overall RMSE:", f"{result['overall']['rmse_px']:.4f}px")
    print(
        "Spearman radius correlation:",
        result["radial_distance_correlation"]["spearman"]["coefficient"]
    )
    print("Section median residuals:")
    for section, stats in result["section_statistics"].items():
        print(
            f"  {section}: median={stats['median_px']:.3f}px, "
            f"RMSE={stats['rmse_px']:.3f}px, "
            f"n={stats['count']}"
        )

print("\nOUTPUTS")
print("Report:", report_path)
print("Point audit:", point_csv)
print("Spatial grid:", grid_csv)
print("Radial plot:", OUT / "phase42_radial_residuals.png")
print("Section plot:", OUT / "phase42_section_residuals.png")
print("Heatmaps:", OUT / "phase42_spatial_heatmaps.png")

print("\nPHASE 42 COMPLETED SUCCESSFULLY")
