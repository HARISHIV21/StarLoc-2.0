from pathlib import Path
import cv2
import numpy as np
import csv
import json

ROOT = Path("research/real_image/user_test")
IMAGE = ROOT / "T1.jpeg"
OUT = ROOT / "T1_refined_v2_results"
OUT.mkdir(parents=True, exist_ok=True)

img = cv2.imread(str(IMAGE))
if img is None:
    raise SystemExit("Cannot read T1.jpeg")

gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(np.float32)
h, w = gray.shape

# 1. Estimate large-scale background while preserving faint sources
background = cv2.GaussianBlur(gray, (0, 0), 20)
residual = gray - background

# 2. Estimate spatially varying local noise
mean = cv2.boxFilter(residual, -1, (31, 31), normalize=True)
mean_sq = cv2.boxFilter(residual * residual, -1, (31, 31), normalize=True)
local_noise = np.sqrt(np.maximum(mean_sq - mean * mean, 0))
local_noise = np.maximum(local_noise, 1.0)

# 3. Multi-scale matched response
scales = (1.0, 1.5, 2.0, 2.8, 3.6)
responses = []

for sigma in scales:
    response = cv2.GaussianBlur(
        np.maximum(residual, 0),
        (0, 0),
        sigma
    )
    responses.append(response / local_noise)

response = np.maximum.reduce(responses)

# 4. Adaptive threshold
threshold_map = np.maximum(3.0, 3.5 * np.ones_like(response))

# 5. Detect local maxima with a small neighbourhood
local_max = cv2.dilate(response, np.ones((3, 3), np.uint8))
peak_mask = (response >= local_max) & (response >= threshold_map)

ys, xs = np.where(peak_mask)

# 6. Measure candidate properties without aggressive rejection
records = []

for x, y in zip(xs, ys):
    if x < 6 or y < 6 or x >= w-6 or y >= h-6:
        continue

    patch = np.maximum(residual[y-5:y+6, x-5:x+6], 0)
    yy, xx = np.mgrid[-5:6, -5:6]
    flux = float(patch.sum())

    if flux <= 0:
        continue

    cx = float((patch * xx).sum() / flux)
    cy = float((patch * yy).sum() / flux)

    dx, dy = xx-cx, yy-cy
    mxx = float((patch * dx*dx).sum()/flux)
    myy = float((patch * dy*dy).sum()/flux)
    mxy = float((patch * dx*dy).sum()/flux)

    eig = np.maximum(
        np.linalg.eigvalsh([[mxx, mxy], [mxy, myy]]),
        0.01
    )
    major, minor = np.sqrt(eig[1]), np.sqrt(eig[0])
    ellipticity = float(major/minor)

    significance = float(response[y, x])
    compactness = 1.0 / max(ellipticity, 1.0)
    score = significance * compactness

    if significance >= 7 and ellipticity <= 2.0:
        tier = "high_confidence_candidate"
    elif significance >= 5:
        tier = "medium_confidence_candidate"
    else:
        tier = "low_confidence_candidate"

    records.append({
        "x": round(x+cx, 3),
        "y": round(y+cy, 3),
        "peak_x": int(x),
        "peak_y": int(y),
        "significance": round(significance, 3),
        "flux": round(flux, 3),
        "ellipticity": round(ellipticity, 3),
        "major_sigma": round(float(major), 3),
        "minor_sigma": round(float(minor), 3),
        "score": round(score, 3),
        "tier": tier
    })

# 7. Rank candidates
records.sort(key=lambda r: r["score"], reverse=True)

for i, record in enumerate(records, 1):
    record["rank"] = i

# 8. Save CSV
fields = list(records[0].keys()) if records else [
    "x", "y", "peak_x", "peak_y", "significance",
    "flux", "ellipticity", "major_sigma", "minor_sigma",
    "score", "tier", "rank"
]

with open(OUT / "T1_v2_all_candidates.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerows(records)

# 9. Separate confidence groups
for tier, filename in [
    ("high_confidence_candidate", "T1_v2_high_confidence.csv"),
    ("medium_confidence_candidate", "T1_v2_medium_confidence.csv"),
    ("low_confidence_candidate", "T1_v2_low_confidence.csv")
]:
    subset = [r for r in records if r["tier"] == tier]
    with open(OUT / filename, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(subset)

# 10. Create separate overlays for visual comparison
for tier, filename, limit in [
    ("high_confidence_candidate", "T1_v2_high_overlay.jpg", 1000),
    ("medium_confidence_candidate", "T1_v2_all_overlay.jpg", 1500)
]:
    overlay = img.copy()
    subset = [r for r in records if r["tier"] == tier][:limit]

    for r in subset:
        x, y = int(round(r["x"])), int(round(r["y"]))
        cv2.circle(overlay, (x, y), 6, (0, 255, 0), 1)
        cv2.circle(overlay, (x, y), 1, (0, 0, 255), -1)

    cv2.imwrite(str(OUT / filename), overlay)

# 11. Save report
counts = {
    tier: sum(r["tier"] == tier for r in records)
    for tier in [
        "high_confidence_candidate",
        "medium_confidence_candidate",
        "low_confidence_candidate"
    ]
}

report = {
    "image": str(IMAGE),
    "dimensions": [w, h],
    "method": "multi-scale response with adaptive local noise normalization and 3x3 local maxima",
    "total_candidates": len(records),
    "confidence_groups": counts,
    "warning": "Confidence tiers are algorithmic rankings, not confirmed star classifications."
}

with open(OUT / "T1_v2_report.json", "w") as f:
    json.dump(report, f, indent=2)

print("\n========== STARLOC REFINED DETECTOR V2 ==========")
print(f"Image: {w} x {h}")
print(f"Total candidates: {len(records)}")
for tier, count in counts.items():
    print(f"{tier}: {count}")
print(f"Output: {OUT}")
print("Detection complete. Catalogue verification is still required.")
