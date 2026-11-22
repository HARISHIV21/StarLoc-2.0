from pathlib import Path
import csv
import json
import cv2
import numpy as np

BASE = Path("research/real_image")
IMAGE_PATH = BASE / "data/network/ASK033/ASK033_live_grayscale.png"
OUT = BASE / "results/ASK033/phase52_global_prediction_test"
OUT.mkdir(parents=True, exist_ok=True)

if not IMAGE_PATH.exists():
    raise FileNotFoundError(IMAGE_PATH)

image = cv2.imread(str(IMAGE_PATH), cv2.IMREAD_GRAYSCALE)
if image is None:
    raise RuntimeError("Could not load ASK033 image.")

height, width = image.shape

# Coordinates are taken directly from the Phase 47 three-way comparison.
points = [
    {"id": "P1", "candidate": (1059.032, 524.367),
     "global": (1044.744, 551.557)},
    {"id": "P2", "candidate": (1074.072, 605.775),
     "global": (1055.858, 628.744)},
    {"id": "P3", "candidate": (1007.639, 505.110),
     "global": (993.159, 527.689)},
    {"id": "P4", "candidate": (966.337, 518.103),
     "global": (956.454, 535.199)},
]

def local_peak_search(cx, cy, radius):
    cx, cy = int(round(cx)), int(round(cy))
    x0, x1 = max(0, cx-radius), min(width, cx+radius+1)
    y0, y1 = max(0, cy-radius), min(height, cy+radius+1)
    crop = image[y0:y1, x0:x1]

    # A 3x3 maximum filter identifies local maxima without smoothing away
    # small stellar sources.
    maxima = cv2.dilate(crop, np.ones((3, 3), np.uint8))
    mask = (crop == maxima)
    yy, xx = np.where(mask)

    found = []
    for py, px in zip(yy, xx):
        gx, gy = x0 + int(px), y0 + int(py)
        distance = float(np.hypot(gx-cx, gy-cy))
        found.append({
            "x": gx,
            "y": gy,
            "intensity": int(image[gy, gx]),
            "distance_px": round(distance, 3)
        })

    found.sort(key=lambda p: (-p["intensity"], p["distance_px"]))

    # Remove duplicate maxima belonging to the same source.
    distinct = []
    for peak in found:
        if all(
            np.hypot(peak["x"]-old["x"], peak["y"]-old["y"]) >= 3
            for old in distinct
        ):
            distinct.append(peak)

    return distinct

def patch_statistics(cx, cy, radius=5):
    cx, cy = int(round(cx)), int(round(cy))
    x0, x1 = max(0, cx-radius), min(width, cx+radius+1)
    y0, y1 = max(0, cy-radius), min(height, cy+radius+1)
    patch = image[y0:y1, x0:x1]

    return {
        "patch_max": int(np.max(patch)),
        "patch_mean": round(float(np.mean(patch)), 3),
        "patch_median": round(float(np.median(patch)), 3),
    }

records = []
annotated = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

print("=" * 72)
print("STARLOC 2.0 — PHASE 52")
print("GLOBAL PREDICTION PEAK VERIFICATION")
print("=" * 72)

for point in points:
    pid = point["id"]
    cx, cy = point["candidate"]
    gx, gy = point["global"]

    candidate_peaks = local_peak_search(cx, cy, 8)
    global_peaks = local_peak_search(gx, gy, 10)

    candidate_stats = patch_statistics(cx, cy)
    global_stats = patch_statistics(gx, gy)

    nearest_global_peak = min(
        global_peaks,
        key=lambda p: p["distance_px"]
    ) if global_peaks else None

    brightest_global_peak = global_peaks[0] if global_peaks else None

    candidate_to_global = float(np.hypot(gx-cx, gy-cy))

    record = {
        "id": pid,
        "candidate_position": {"x": cx, "y": cy},
        "global_prediction": {"x": gx, "y": gy},
        "candidate_to_global_distance_px": round(candidate_to_global, 3),
        "candidate_patch": candidate_stats,
        "global_prediction_patch": global_stats,
        "candidate_region_peaks": candidate_peaks[:10],
        "global_region_peaks": global_peaks[:10],
        "nearest_peak_to_global_prediction": nearest_global_peak,
        "brightest_peak_in_global_region": brightest_global_peak,
        "interpretation": (
            "A local maximum exists near the global prediction."
            if nearest_global_peak and nearest_global_peak["distance_px"] <= 3
            else "No local maximum found within 3 px of the global prediction."
        )
    }
    records.append(record)

    # Red: original detected candidate. Green: global model prediction.
    cv2.circle(annotated, (round(cx), round(cy)), 9, (0, 0, 255), 2)
    cv2.circle(annotated, (round(gx), round(gy)), 9, (0, 255, 0), 2)
    cv2.line(
        annotated, (round(cx), round(cy)),
        (round(gx), round(gy)), (255, 255, 0), 1
    )
    cv2.putText(
        annotated, pid, (round(cx)+8, round(cy)-8),
        cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 0, 255), 2
    )

    if nearest_global_peak:
        px, py = nearest_global_peak["x"], nearest_global_peak["y"]
        cv2.circle(annotated, (px, py), 4, (255, 255, 0), 2)

    print(f"\n{pid}")
    print(f"  Candidate: ({cx:.2f}, {cy:.2f})")
    print(f"  Global prediction: ({gx:.2f}, {gy:.2f})")
    print(f"  Separation: {candidate_to_global:.2f}px")
    print(f"  Candidate patch: {candidate_stats}")
    print(f"  Prediction patch: {global_stats}")

    print("  Peaks near global prediction:")
    for peak in global_peaks[:6]:
        print(
            f"    ({peak['x']}, {peak['y']}) "
            f"intensity={peak['intensity']} "
            f"distance={peak['distance_px']:.2f}px"
        )

    print("  Nearest prediction-region peak:", nearest_global_peak)

# Create a compact four-panel crop montage.
panels = []
for point in points:
    cx, cy = point["candidate"]
    gx, gy = point["global"]

    midx = int(round((cx+gx)/2))
    midy = int(round((cy+gy)/2))

    half = 45
    x0, x1 = max(0, midx-half), min(width, midx+half)
    y0, y1 = max(0, midy-half), min(height, midy+half)

    crop = cv2.cvtColor(image[y0:y1, x0:x1], cv2.COLOR_GRAY2BGR)
    cv2.circle(crop, (round(cx)-x0, round(cy)-y0), 7, (0, 0, 255), 2)
    cv2.circle(crop, (round(gx)-x0, round(gy)-y0), 7, (0, 255, 0), 2)
    cv2.putText(
        crop, point["id"], (4, 16),
        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1
    )
    panels.append(cv2.resize(crop, (270, 270)))

montage = np.vstack([
    np.hstack(panels[:2]),
    np.hstack(panels[2:])
])

overlay_path = OUT / "phase52_global_prediction_overlay.jpg"
montage_path = OUT / "phase52_four_point_montage.jpg"
json_path = BASE / "phase52_global_prediction_test_report.json"
csv_path = OUT / "phase52_peak_comparison.csv"

cv2.imwrite(str(overlay_path), annotated)
cv2.imwrite(str(montage_path), montage)

with json_path.open("w") as f:
    json.dump({
        "phase": 52,
        "method": "Local image-maximum search around candidate and global predicted positions",
        "image": str(IMAGE_PATH),
        "points": records,
        "limitations": [
            "A local intensity maximum is not proof of a stellar identity.",
            "The global predictions are inherited from the existing Phase 38 model.",
            "This test does not independently validate the local WCS or catalogue identity.",
            "No calibration parameters or original data were modified."
        ]
    }, f, indent=2)

with csv_path.open("w", newline="") as f:
    fields = [
        "point", "candidate_x", "candidate_y",
        "global_x", "global_y", "separation_px",
        "candidate_patch_max", "global_patch_max",
        "nearest_global_peak_x", "nearest_global_peak_y",
        "nearest_global_peak_intensity", "nearest_global_peak_distance_px"
    ]
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()

    for r in records:
        peak = r["nearest_peak_to_global_prediction"] or {}
        writer.writerow({
            "point": r["id"],
            "candidate_x": r["candidate_position"]["x"],
            "candidate_y": r["candidate_position"]["y"],
            "global_x": r["global_prediction"]["x"],
            "global_y": r["global_prediction"]["y"],
            "separation_px": r["candidate_to_global_distance_px"],
            "candidate_patch_max": r["candidate_patch"]["patch_max"],
            "global_patch_max": r["global_prediction_patch"]["patch_max"],
            "nearest_global_peak_x": peak.get("x"),
            "nearest_global_peak_y": peak.get("y"),
            "nearest_global_peak_intensity": peak.get("intensity"),
            "nearest_global_peak_distance_px": peak.get("distance_px"),
        })

print("\n" + "=" * 72)
print("PHASE 52 COMPLETED")
print("=" * 72)
print("Annotated full image:", overlay_path)
print("Four-point montage:", montage_path)
print("Peak comparison CSV:", csv_path)
print("JSON report:", json_path)
print("No existing calibration files were changed.")
