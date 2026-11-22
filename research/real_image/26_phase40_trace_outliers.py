import csv
import json
from pathlib import Path

SOURCE = Path("research/real_image/results/ASK033/phase37_validation/phase37_all_matches.csv")
OUT = Path("research/real_image/results/ASK033/phase40_outlier_trace")
OUT.mkdir(parents=True, exist_ok=True)

targets = [
    (1059.032, 524.367, 30.018661),
    (1074.072, 605.775, 28.595389),
    (1007.639, 505.110, 26.123057),
    (966.337, 518.103, 19.094066),
    (856.631, 507.827, 6.077997),
    (785.741, 714.566, 3.512942),
    (854.682, 514.187, 3.057677),
]

OFFSET_X, OFFSET_Y = 640.0, 480.0

with SOURCE.open(newline="") as f:
    rows = list(csv.DictReader(f))

required = {
    "section", "candidate_x_local", "candidate_y_local",
    "hip_ra_deg", "hip_dec_deg", "pixel_residual"
}
if not rows or not required.issubset(rows[0]):
    raise ValueError(f"Unexpected Phase 37 columns: {list(rows[0]) if rows else 'empty'}")

r2c2 = [r for r in rows if r["section"] == "R2C2"]
results = []

print("=" * 70)
print("PHASE 40 — ORIGINAL HIPPARCOS CORRESPONDENCE TRACE")
print("=" * 70)

for gx, gy, phase38_error in targets:
    lx, ly = gx - OFFSET_X, gy - OFFSET_Y

    ranked = sorted(
        r2c2,
        key=lambda r: (
            (float(r["candidate_x_local"]) - lx) ** 2 +
            (float(r["candidate_y_local"]) - ly) ** 2
        ) ** 0.5
    )

    nearest = ranked[0]
    distance = (
        (float(nearest["candidate_x_local"]) - lx) ** 2 +
        (float(nearest["candidate_y_local"]) - ly) ** 2
    ) ** 0.5

    result = {
        "phase38_global_x": gx,
        "phase38_global_y": gy,
        "phase38_residual_px": phase38_error,
        "target_local_x": lx,
        "target_local_y": ly,
        "nearest_phase37_record_distance_px": distance,
        "phase37_correspondence": nearest,
        "next_nearest_records": ranked[1:3]
    }
    results.append(result)

    print(f"\nPhase 38 residual: {phase38_error:.3f} px")
    print(f"Global pixel: ({gx:.3f}, {gy:.3f})")
    print(f"Local pixel:  ({lx:.3f}, {ly:.3f})")
    print(f"Nearest Phase 37 distance: {distance:.4f} px")
    print("Original correspondence:")
    print(json.dumps(nearest, indent=2))

report = {
    "phase": 40,
    "section": "R2C2",
    "coordinate_conversion": "global = local + (640, 480)",
    "source": str(SOURCE),
    "traced_outliers": results
}

report_path = OUT / "phase40_outlier_trace.json"
report_path.write_text(json.dumps(report, indent=2))

csv_path = OUT / "phase40_outlier_trace.csv"
with csv_path.open("w", newline="") as f:
    fields = [
        "phase38_global_x", "phase38_global_y",
        "phase38_residual_px", "target_local_x", "target_local_y",
        "nearest_distance_px", "candidate_x_local",
        "candidate_y_local", "hip_ra_deg", "hip_dec_deg",
        "phase37_pixel_residual"
    ]
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()

    for item in results:
        r = item["phase37_correspondence"]
        writer.writerow({
            "phase38_global_x": item["phase38_global_x"],
            "phase38_global_y": item["phase38_global_y"],
            "phase38_residual_px": item["phase38_residual_px"],
            "target_local_x": item["target_local_x"],
            "target_local_y": item["target_local_y"],
            "nearest_distance_px": item["nearest_phase37_record_distance_px"],
            "candidate_x_local": r["candidate_x_local"],
            "candidate_y_local": r["candidate_y_local"],
            "hip_ra_deg": r["hip_ra_deg"],
            "hip_dec_deg": r["hip_dec_deg"],
            "phase37_pixel_residual": r["pixel_residual"]
        })

print("\nSaved:", report_path)
print("Saved:", csv_path)
print("\nPHASE 40 TRACE COMPLETE")
