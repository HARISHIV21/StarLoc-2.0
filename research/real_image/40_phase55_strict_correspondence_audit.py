import csv
import json
from pathlib import Path
import numpy as np

BASE = Path("research/real_image")
CSV_PATH = (
    BASE / "results/ASK033/phase49_cross_section_consistency/"
    / "phase49_cross_section_point_comparison.csv"
)
OUT = BASE / "results/ASK033/phase55_strict_correspondence_audit"
OUT.mkdir(parents=True, exist_ok=True)

with CSV_PATH.open(newline="") as f:
    rows = list(csv.DictReader(f))

for r in rows:
    for key in (
        "global_x", "global_y",
        "local_wcs_candidate_error_px",
        "global_candidate_error_px",
        "global_vs_local_difference_px",
    ):
        r[key] = float(r[key])

suspects = [
    (1059.032, 524.367),
    (1074.072, 605.775),
    (1007.639, 505.110),
    (966.337, 518.103),
]

print("=" * 72)
print("STARLOC 2.0 — PHASE 55")
print("STRICT CORRESPONDENCE QUALITY AUDIT")
print("=" * 72)

summary = {}

for section in sorted(set(r["section"] for r in rows)):
    subset = [r for r in rows if r["section"] == section]
    errors = np.array([
        r["local_wcs_candidate_error_px"] for r in subset
    ])

    counts = {
        str(t): int(np.sum(errors <= t))
        for t in (0.5, 1.0, 1.5, 2.0, 3.0, 5.0)
    }

    summary[section] = {
        "total": len(subset),
        "threshold_counts": counts,
        "median_error_px": float(np.median(errors)),
        "rmse_px": float(np.sqrt(np.mean(errors ** 2))),
    }

    print(
        f"\n{section}: {len(subset)} correspondences | "
        f"median={np.median(errors):.3f}px | "
        f"RMSE={np.sqrt(np.mean(errors**2)):.3f}px"
    )
    print("  Accepted at thresholds:", counts)

print("\nFOUR SUSPECT POINTS")
suspect_results = []

for x, y in suspects:
    nearest = min(
        rows,
        key=lambda r: (r["global_x"] - x)**2 + (r["global_y"] - y)**2
    )

    distance = np.hypot(
        nearest["global_x"] - x,
        nearest["global_y"] - y
    )

    result = {
        "target_x": x,
        "target_y": y,
        "matched_section": nearest["section"],
        "matched_x": nearest["global_x"],
        "matched_y": nearest["global_y"],
        "coordinate_difference_px": float(distance),
        "local_wcs_candidate_error_px":
            nearest["local_wcs_candidate_error_px"],
        "global_candidate_error_px":
            nearest["global_candidate_error_px"],
    }
    suspect_results.append(result)

    print(
        f"  ({x:.3f}, {y:.3f}) -> {nearest['section']} | "
        f"coordinate difference={distance:.4f}px | "
        f"local WCS residual="
        f"{nearest['local_wcs_candidate_error_px']:.3f}px"
    )

r2c2 = [r for r in rows if r["section"] == "R2C2"]
strict = [
    r for r in r2c2
    if r["local_wcs_candidate_error_px"] <= 1.0
]

report = {
    "phase": 55,
    "total_correspondences": len(rows),
    "per_section": summary,
    "r2c2_strict_subset": {
        "threshold_px": 1.0,
        "count": len(strict),
        "total": len(r2c2),
    },
    "four_suspect_points": suspect_results,
    "interpretation": (
        "Strict local-WCS residual filtering is a quality-control step. "
        "It does not independently prove catalogue identities or calibration accuracy."
    ),
}

report_path = BASE / "phase55_strict_correspondence_audit_report.json"
report_path.write_text(json.dumps(report, indent=2))

strict_path = OUT / "phase55_r2c2_strict_matches.csv"
with strict_path.open("w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(strict)

print("\nOUTPUTS")
print("Report:", report_path)
print("Strict R2C2 matches:", strict_path)
print(f"R2C2 strict subset: {len(strict)}/{len(r2c2)}")
print("\nPHASE 55 COMPLETED")
