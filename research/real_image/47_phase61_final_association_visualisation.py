from pathlib import Path
import csv
import json
import cv2

ROOT = Path.cwd()
BASE = ROOT / "research/real_image"
ASK = BASE / "results/ASK033"

IMAGE = BASE / "data/network/ASK033/ASK033_live_grayscale.png"
INPUT = (
    ASK / "phase49_cross_section_consistency"
    / "phase49_cross_section_point_comparison.csv"
)

OUT = ASK / "phase61_final_association_visualisation"
OUT.mkdir(parents=True, exist_ok=True)

for p in (IMAGE, INPUT):
    if not p.exists():
        raise SystemExit(f"Missing required input: {p}")

image = cv2.imread(str(IMAGE), cv2.IMREAD_GRAYSCALE)
if image is None:
    raise SystemExit("Could not read the ASK033 image.")

canvas = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

with INPUT.open(newline="") as f:
    rows = list(csv.DictReader(f))

if not rows:
    raise SystemExit("No correspondence records found.")

suspects = [
    (1059.032, 524.367),
    (1074.072, 605.775),
    (1007.639, 505.110),
    (966.337, 518.103),
]

classified = []
strict_count = 0
uncertain_count = 0
suspect_count = 0

for row in rows:
    x = float(row["global_x"])
    y = float(row["global_y"])
    residual = float(row["local_wcs_candidate_error_px"])

    is_suspect = any(
        ((x - sx)**2 + (y - sy)**2)**0.5 < 0.5
        for sx, sy in suspects
    )

    if is_suspect:
        category = "SUSPECT_ASSOCIATION"
        color = (0, 0, 255)       # Red
        suspect_count += 1
    elif residual <= 1.0:
        category = "STRICT_INTERNAL_CONSISTENCY"
        color = (0, 220, 0)       # Green
        strict_count += 1
    else:
        category = "UNCERTAIN_INTERNAL_CONSISTENCY"
        color = (0, 165, 255)     # Orange
        uncertain_count += 1

    px, py = int(round(x)), int(round(y))

    if 0 <= px < canvas.shape[1] and 0 <= py < canvas.shape[0]:
        if is_suspect:
            cv2.drawMarker(
                canvas, (px, py), color,
                markerType=cv2.MARKER_TILTED_CROSS,
                markerSize=18, thickness=2
            )
        else:
            cv2.circle(canvas, (px, py), 5, color, 1)
            cv2.circle(canvas, (px, py), 2, color, -1)

    result = dict(row)
    result["classification"] = category
    result["is_one_of_four_suspect_points"] = str(is_suspect)
    classified.append(result)

# Add a readable legend.
overlay = canvas.copy()
cv2.rectangle(
    overlay, (15, 15), (660, 145), (20, 20, 20), -1
)
canvas = cv2.addWeighted(overlay, 0.78, canvas, 0.22, 0)

legend = [
    ((0, 220, 0), f"Strict internal consistency: {strict_count}"),
    ((0, 165, 255), f"Uncertain: {uncertain_count}"),
    ((0, 0, 255), f"Suspect associations: {suspect_count}"),
]

for i, (color, label) in enumerate(legend):
    y = 48 + i * 34
    cv2.circle(canvas, (35, y - 5), 7, color, -1)
    cv2.putText(
        canvas, label, (55, y),
        cv2.FONT_HERSHEY_SIMPLEX, 0.65,
        (255, 255, 255), 1, cv2.LINE_AA
    )

overlay_path = OUT / "phase61_real_star_association_overlay.jpg"
cv2.imwrite(str(overlay_path), canvas, [cv2.IMWRITE_JPEG_QUALITY, 95])

csv_path = OUT / "phase61_all_classified_correspondences.csv"
with csv_path.open("w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=list(classified[0].keys()))
    writer.writeheader()
    writer.writerows(classified)

report = {
    "phase": 61,
    "title": "Final real-star association visualisation",
    "source_image": str(IMAGE.relative_to(ROOT)),
    "input_correspondences": len(rows),
    "strict_internal_consistency": strict_count,
    "uncertain_internal_consistency": uncertain_count,
    "suspect_associations": suspect_count,
    "strict_threshold_px": 1.0,
    "overlay": str(overlay_path.relative_to(ROOT)),
    "classified_csv": str(csv_path.relative_to(ROOT)),
    "interpretation": (
        "The overlay visualises local-WCS residual quality. "
        "Green points are internally consistent within 1 pixel; "
        "orange points exceed that threshold; red crosses mark four "
        "previously suspected associations. These classifications "
        "do not independently certify stellar catalogue identities."
    )
}

report_path = BASE / "phase61_final_association_visualisation_report.json"
report_path.write_text(json.dumps(report, indent=2))

print("=" * 72)
print("STARLOC 2.0 — PHASE 61 COMPLETED")
print("=" * 72)
print("Total correspondences:", len(rows))
print("Strict internal consistency:", strict_count)
print("Uncertain:", uncertain_count)
print("Suspect associations:", suspect_count)
print("\nOverlay:", overlay_path.relative_to(ROOT))
print("Classified CSV:", csv_path.relative_to(ROOT))
print("Report:", report_path.relative_to(ROOT))
print("\nNo calibration parameters or previous results were modified.")
