import csv
import json
from pathlib import Path
from collections import defaultdict

import numpy as np
import matplotlib.pyplot as plt

BASE = Path("research/real_image")
RESULTS = BASE / "results/ASK033"
INPUT = RESULTS / "phase38_global_calibration/phase38_global_fit_residuals.csv"
OUT = RESULTS / "phase39_residual_audit"
OUT.mkdir(parents=True, exist_ok=True)

if not INPUT.exists():
    raise FileNotFoundError(INPUT)

with INPUT.open(newline="") as f:
    rows = list(csv.DictReader(f))

groups = defaultdict(list)
for row in rows:
    row["residual_px"] = float(row["residual_px"])
    row["global_x"] = float(row["global_x"])
    row["global_y"] = float(row["global_y"])
    groups[(row["section"], row["dataset"])].append(row)

def stats(items):
    values = np.array([r["residual_px"] for r in items])
    return {
        "count": int(len(values)),
        "median_px": float(np.median(values)),
        "mean_px": float(np.mean(values)),
        "rmse_px": float(np.sqrt(np.mean(values ** 2))),
        "p90_px": float(np.percentile(values, 90)),
        "max_px": float(np.max(values)),
        "count_over_2px": int(np.sum(values > 2)),
        "count_over_3px": int(np.sum(values > 3)),
        "count_over_5px": int(np.sum(values > 5))
    }

print("=" * 68)
print("STARLOC 2.0 — PHASE 39")
print("GLOBAL CALIBRATION RESIDUAL AUDIT")
print("=" * 68)

report = {
    "phase": 39,
    "input": str(INPUT),
    "total_correspondences": len(rows),
    "section_results": {},
    "outliers_over_3px": [],
    "outliers_over_5px": []
}

for section in sorted(set(r["section"] for r in rows)):
    section_rows = [r for r in rows if r["section"] == section]

    result = {
        "all": stats(section_rows),
        "training": stats([r for r in section_rows if r["dataset"] == "train"]),
        "test": stats([r for r in section_rows if r["dataset"] == "test"])
    }

    report["section_results"][section] = result

    print("\n", section)
    for split in ("all", "training", "test"):
        s = result[split]
        print(
            f"{split:>8}: n={s['count']:3d} | "
            f"median={s['median_px']:.3f}px | "
            f"RMSE={s['rmse_px']:.3f}px | "
            f"max={s['max_px']:.3f}px | "
            f">3px={s['count_over_3px']}"
        )

for row in rows:
    if row["residual_px"] > 3:
        report["outliers_over_3px"].append(row)
    if row["residual_px"] > 5:
        report["outliers_over_5px"].append(row)

report["outlier_counts"] = {
    "over_2px": sum(r["residual_px"] > 2 for r in rows),
    "over_3px": len(report["outliers_over_3px"]),
    "over_5px": len(report["outliers_over_5px"]),
    "over_10px": sum(r["residual_px"] > 10 for r in rows)
}

# Sort and save the worst residuals.
worst = sorted(rows, key=lambda r: r["residual_px"], reverse=True)

outlier_csv = OUT / "phase39_worst_residuals.csv"
with outlier_csv.open("w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(worst)

# Residual distribution by image section.
fig, ax = plt.subplots(figsize=(10, 6))
section_names = sorted(set(r["section"] for r in rows))
data = [
    [r["residual_px"] for r in rows if r["section"] == section]
    for section in section_names
]
ax.boxplot(data, tick_labels=section_names, showmeans=True)
ax.set_ylabel("Global model residual (pixels)")
ax.set_title("Phase 39 — residual distribution by section")
ax.grid(axis="y", alpha=0.3)
fig.tight_layout()
fig.savefig(OUT / "phase39_section_residuals.png", dpi=160)
plt.close(fig)

# Image-space residual scatter.
fig, ax = plt.subplots(figsize=(10, 7))
scatter = ax.scatter(
    [r["global_x"] for r in rows],
    [r["global_y"] for r in rows],
    c=[r["residual_px"] for r in rows],
    s=35
)
ax.set_xlim(0, 1920)
ax.set_ylim(1440, 0)
ax.set_aspect("equal")
ax.set_xlabel("Image X (pixels)")
ax.set_ylabel("Image Y (pixels)")
ax.set_title("Phase 39 — spatial distribution of global fit residuals")
fig.colorbar(scatter, ax=ax, label="Residual (pixels)")
fig.tight_layout()
fig.savefig(OUT / "phase39_spatial_residual_map.png", dpi=160)
plt.close(fig)

report_path = BASE / "phase39_residual_audit_report.json"
report_path.write_text(json.dumps(report, indent=2))

print("\n" + "=" * 68)
print("OUTLIER SUMMARY")
print("=" * 68)
print(json.dumps(report["outlier_counts"], indent=2))

print("\nWORST 10 CORRESPONDENCES")
for row in worst[:10]:
    print(
        row["section"],
        row["dataset"],
        f"x={row['global_x']:.1f}",
        f"y={row['global_y']:.1f}",
        f"residual={row['residual_px']:.3f}px"
    )

print("\nReport:", report_path)
print("Worst residuals:", outlier_csv)
print("Section plot:", OUT / "phase39_section_residuals.png")
print("Spatial plot:", OUT / "phase39_spatial_residual_map.png")
print("\nPHASE 39 COMPLETE")
