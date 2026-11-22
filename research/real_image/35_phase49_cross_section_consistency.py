import csv
import json
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from astropy.wcs import WCS

BASE = Path("research/real_image")
RESULTS = BASE / "results/ASK033"

PHASE37 = RESULTS / "phase37_validation/phase37_all_matches.csv"
PHASE38 = RESULTS / "phase38_global_calibration/phase38_global_fit_residuals.csv"

OUT = RESULTS / "phase49_cross_section_consistency"
OUT.mkdir(parents=True, exist_ok=True)

OFFSETS = {
    "R1C2": (640, 0),
    "R2C1": (0, 480),
    "R2C2": (640, 480),
    "R3C1": (0, 960),
    "R3C2": (640, 960),
}

WCS_PATHS = {
    "R1C2": RESULTS / "phase36_section_solutions/R1C2_custom.wcs",
    "R2C1": RESULTS / "phase36_section_solutions/R2C1_custom.wcs",
    "R2C2": RESULTS / "custom_plate_solutions/R2C2_custom.wcs",
    "R3C1": RESULTS / "phase36_section_solutions/R3C1_custom.wcs",
    "R3C2": RESULTS / "phase36_section_solutions/R3C2_custom.wcs",
}

for path in (PHASE37, PHASE38, *WCS_PATHS.values()):
    if not path.exists():
        raise FileNotFoundError(path)

def load_csv(path):
    with path.open(newline="") as f:
        return list(csv.DictReader(f))

def stats(values):
    a = np.asarray(values, dtype=float)
    return {
        "count": int(len(a)),
        "median_px": float(np.median(a)),
        "mean_px": float(np.mean(a)),
        "rmse_px": float(np.sqrt(np.mean(a ** 2))),
        "p90_px": float(np.percentile(a, 90)),
        "max_px": float(np.max(a)),
        "over_1px": int(np.sum(a > 1)),
        "over_2px": int(np.sum(a > 2)),
        "over_3px": int(np.sum(a > 3)),
        "over_5px": int(np.sum(a > 5)),
    }

print("=" * 72)
print("STARLOC 2.0 — PHASE 49")
print("CROSS-SECTION LOCAL WCS / GLOBAL FISHEYE CONSISTENCY")
print("=" * 72)

local_rows = load_csv(PHASE37)
global_rows = load_csv(PHASE38)

# Index global model results by section. Match each local correspondence
# to its global row using its global image coordinates.
global_by_section = {}
for row in global_rows:
    global_by_section.setdefault(row["section"], []).append(row)

wcs_objects = {
    section: WCS(str(path)).celestial
    for section, path in WCS_PATHS.items()
}

records = []

for row in local_rows:
    section = row["section"]
    if section not in OFFSETS:
        continue

    ox, oy = OFFSETS[section]

    lx = float(row["candidate_x_local"])
    ly = float(row["candidate_y_local"])
    gx = lx + ox
    gy = ly + oy

    ra = float(row["hip_ra_deg"])
    dec = float(row["hip_dec_deg"])

    # Find the corresponding Phase 38 global-model row.
    candidates = global_by_section.get(section, [])
    if not candidates:
        raise RuntimeError(f"No Phase 38 rows for {section}")

    distances = [
        np.hypot(
            float(item["global_x"]) - gx,
            float(item["global_y"]) - gy
        )
        for item in candidates
    ]

    best_index = int(np.argmin(distances))
    if distances[best_index] > 0.01:
        raise RuntimeError(
            f"Could not match Phase 38 row for {section} "
            f"at ({gx:.3f}, {gy:.3f}); nearest difference "
            f"{distances[best_index]:.4f}px"
        )

    global_row = candidates[best_index]

    candidate_xy = np.array([gx, gy], dtype=float)

    # Directly project catalogue RA/Dec through the local TAN-SIP WCS.
    local_xy = wcs_objects[section].all_world2pix(
        np.array([[ra, dec]], dtype=float),
        0,
        quiet=True
    )[0]

    if not np.all(np.isfinite(local_xy)):
        continue

    local_global_xy = np.array([
        local_xy[0] + ox,
        local_xy[1] + oy
    ])

    global_xy = np.array([
        float(global_row["predicted_x"]),
        float(global_row["predicted_y"])
    ])

    local_candidate_error = local_global_xy - candidate_xy
    global_candidate_error = global_xy - candidate_xy
    model_difference = global_xy - local_global_xy

    records.append({
        "section": section,
        "global_x": gx,
        "global_y": gy,
        "hip_ra_deg": ra,
        "hip_dec_deg": dec,
        "local_wcs_x": float(local_global_xy[0]),
        "local_wcs_y": float(local_global_xy[1]),
        "global_model_x": float(global_xy[0]),
        "global_model_y": float(global_xy[1]),
        "local_wcs_candidate_dx": float(local_candidate_error[0]),
        "local_wcs_candidate_dy": float(local_candidate_error[1]),
        "local_wcs_candidate_error_px": float(np.linalg.norm(local_candidate_error)),
        "global_candidate_dx": float(global_candidate_error[0]),
        "global_candidate_dy": float(global_candidate_error[1]),
        "global_candidate_error_px": float(np.linalg.norm(global_candidate_error)),
        "global_vs_local_dx": float(model_difference[0]),
        "global_vs_local_dy": float(model_difference[1]),
        "global_vs_local_difference_px": float(np.linalg.norm(model_difference)),
        "phase38_dataset": global_row["dataset"],
    })

if len(records) != 233:
    print(
        f"\nWARNING: Expected 233 valid correspondences; "
        f"processed {len(records)}."
    )

# Save point-level comparison.
csv_path = OUT / "phase49_cross_section_point_comparison.csv"
with csv_path.open("w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=list(records[0].keys()))
    writer.writeheader()
    writer.writerows(records)

# Per-section and overall statistics.
section_report = {}
for section in OFFSETS:
    subset = [r for r in records if r["section"] == section]
    if not subset:
        continue

    section_report[section] = {
        "count": len(subset),
        "local_wcs_vs_candidate": stats([
            r["local_wcs_candidate_error_px"] for r in subset
        ]),
        "global_fisheye_vs_candidate": stats([
            r["global_candidate_error_px"] for r in subset
        ]),
        "global_fisheye_vs_local_wcs": stats([
            r["global_vs_local_difference_px"] for r in subset
        ]),
    }

overall = {
    "local_wcs_vs_candidate": stats([
        r["local_wcs_candidate_error_px"] for r in records
    ]),
    "global_fisheye_vs_candidate": stats([
        r["global_candidate_error_px"] for r in records
    ]),
    "global_fisheye_vs_local_wcs": stats([
        r["global_vs_local_difference_px"] for r in records
    ]),
}

report = {
    "phase": 49,
    "title": "Cross-section local WCS and global fisheye consistency",
    "correspondence_count": len(records),
    "method": (
        "For each Phase 37 catalogue correspondence, project RA/Dec "
        "through the corresponding local TAN-SIP WCS and compare the "
        "result with the Phase 38 global fisheye prediction and "
        "detected image candidate."
    ),
    "overall": overall,
    "per_section": section_report,
    "limitations": [
        "Local WCS and global model use the same underlying image detections and catalogue associations.",
        "This is a consistency analysis, not independent astrometric ground-truth validation.",
        "Local TAN-SIP solutions describe individual crops and do not alone establish a complete full-frame fisheye model.",
        "Differences may reflect local WCS uncertainty, catalogue matching uncertainty, or global model limitations."
    ]
}

report_path = BASE / "phase49_cross_section_consistency_report.json"
with report_path.open("w") as f:
    json.dump(report, f, indent=2)

# Plot 1: three error distributions for each section.
labels = list(section_report)
x = np.arange(len(labels))
width = 0.24

local_values = [
    section_report[s]["local_wcs_vs_candidate"]["median_px"]
    for s in labels
]
global_values = [
    section_report[s]["global_fisheye_vs_candidate"]["median_px"]
    for s in labels
]
agreement_values = [
    section_report[s]["global_fisheye_vs_local_wcs"]["median_px"]
    for s in labels
]

fig, ax = plt.subplots(figsize=(11, 6))
ax.bar(x - width, local_values, width, label="Local WCS vs candidate")
ax.bar(x, global_values, width, label="Global model vs candidate")
ax.bar(x + width, agreement_values, width, label="Global vs local WCS")
ax.set_xticks(x)
ax.set_xticklabels(labels)
ax.set_ylabel("Median pixel difference")
ax.set_title("Phase 49 — Median residual comparison by section")
ax.legend()
ax.grid(axis="y", alpha=0.25)
fig.tight_layout()

plot1 = OUT / "phase49_section_median_comparison.png"
fig.savefig(plot1, dpi=180)
plt.close(fig)

# Plot 2: global-vs-local WCS difference across the full image.
fig, ax = plt.subplots(figsize=(12, 8))

for section in labels:
    subset = [r for r in records if r["section"] == section]
    ax.scatter(
        [r["global_x"] for r in subset],
        [r["global_y"] for r in subset],
        c=[r["global_vs_local_difference_px"] for r in subset],
        s=25,
        label=section,
        alpha=0.8
    )

ax.set_xlim(0, 1920)
ax.set_ylim(1440, 0)
ax.set_xlabel("Global image X (pixels)")
ax.set_ylabel("Global image Y (pixels)")
ax.set_title("Phase 49 — Global fisheye vs local WCS disagreement")
ax.legend()
fig.tight_layout()

plot2 = OUT / "phase49_global_local_disagreement_map.png"
fig.savefig(plot2, dpi=180)
plt.close(fig)

# Plot 3: distributions of global-vs-local model differences.
fig, ax = plt.subplots(figsize=(10, 6))
box_data = [
    [
        r["global_vs_local_difference_px"]
        for r in records if r["section"] == section
    ]
    for section in labels
]
ax.boxplot(box_data, tick_labels=labels, showfliers=True)
ax.set_ylabel("Global-to-local prediction difference (pixels)")
ax.set_title("Phase 49 — Prediction disagreement by section")
ax.grid(axis="y", alpha=0.25)
fig.tight_layout()

plot3 = OUT / "phase49_global_local_boxplot.png"
fig.savefig(plot3, dpi=180)
plt.close(fig)

print("\n" + "=" * 72)
print("PHASE 49 RESULTS")
print("=" * 72)

print("Valid correspondences:", len(records))

for section, result in section_report.items():
    print(f"\n{section} — n={result['count']}")
    for label, key in [
        ("Local WCS vs candidate", "local_wcs_vs_candidate"),
        ("Global model vs candidate", "global_fisheye_vs_candidate"),
        ("Global vs local WCS", "global_fisheye_vs_local_wcs"),
    ]:
        s = result[key]
        print(
            f"  {label}: median={s['median_px']:.3f}px, "
            f"RMSE={s['rmse_px']:.3f}px, "
            f"max={s['max_px']:.3f}px"
        )

print("\nOVERALL")
for label, key in [
    ("Local WCS vs candidate", "local_wcs_vs_candidate"),
    ("Global model vs candidate", "global_fisheye_vs_candidate"),
    ("Global vs local WCS", "global_fisheye_vs_local_wcs"),
]:
    s = overall[key]
    print(
        f"  {label}: median={s['median_px']:.3f}px, "
        f"RMSE={s['rmse_px']:.3f}px, "
        f"max={s['max_px']:.3f}px"
    )

print("\nOUTPUTS")
print("Report:", report_path)
print("Point comparison:", csv_path)
print("Section comparison:", plot1)
print("Disagreement map:", plot2)
print("Boxplot:", plot3)

print("\nPHASE 49 COMPLETED SUCCESSFULLY")
