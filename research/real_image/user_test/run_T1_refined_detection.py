from pathlib import Path
import cv2
import numpy as np
import csv
import json

ROOT = Path("research/real_image/user_test")
IMAGE = ROOT / "T1.jpeg"
OUT = ROOT / "T1_refined_detection_results"
OUT.mkdir(parents=True, exist_ok=True)

image = cv2.imread(str(IMAGE))
if image is None:
    raise SystemExit("Cannot read T1.jpeg")

gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY).astype(np.float32)

# 1. Estimate and subtract large-scale background
background = cv2.GaussianBlur(gray, (0, 0), 12)
residual = np.maximum(gray - background, 0)

# 2. Multi-scale point-source response
responses = []
for sigma in (1.2, 1.8, 2.5):
    response = cv2.GaussianBlur(residual, (0, 0), sigma)
    responses.append(response)

matched = np.maximum.reduce(responses)

# 3. Robust threshold and local maxima
values = matched[matched > 0]
median = float(np.median(values))
mad = float(np.median(np.abs(values - median)))
noise = max(1.4826 * mad, 0.5)
threshold = max(3.0, median + 5.0 * noise)

local_max = cv2.dilate(matched, np.ones((7, 7), np.uint8))
peak_mask = (matched >= local_max) & (matched > threshold)
ys, xs = np.where(peak_mask)

# 4. Measure candidate shape and photometry
records = []
h, w = gray.shape

for x, y in zip(xs, ys):
    if x < 6 or y < 6 or x >= w - 6 or y >= h - 6:
        continue

    patch = residual[y-5:y+6, x-5:x+6]
    yy, xx = np.mgrid[-5:6, -5:6]
    weights = patch.astype(np.float64)

    flux = float(weights.sum())
    if flux <= 0:
        continue

    cx = float((weights * xx).sum() / flux)
    cy = float((weights * yy).sum() / flux)

    dx = xx - cx
    dy = yy - cy
    mxx = float((weights * dx * dx).sum() / flux)
    myy = float((weights * dy * dy).sum() / flux)
    mxy = float((weights * dx * dy).sum() / flux)

    covariance = np.array([[mxx, mxy], [mxy, myy]])
    eigenvalues = np.maximum(np.linalg.eigvalsh(covariance), 0.01)

    major = float(np.sqrt(eigenvalues[1]))
    minor = float(np.sqrt(eigenvalues[0]))
    ellipticity = major / minor

    peak = float(matched[y, x])
    compactness = min(1.0, 1.0 / max(ellipticity, 1.0))
    significance = peak / noise
    score = significance * compactness

    records.append({
        "x": round(x + cx, 3),
        "y": round(y + cy, 3),
        "peak_x": int(x),
        "peak_y": int(y),
        "peak_response": round(peak, 3),
        "flux": round(flux, 3),
        "ellipticity": round(ellipticity, 3),
        "major_sigma": round(major, 3),
        "minor_sigma": round(minor, 3),
        "significance": round(significance, 3),
        "score": round(score, 3),
    })

# 5. Rank candidates; retain a compact-source subset for comparison
records.sort(key=lambda r: r["score"], reverse=True)

for rank, record in enumerate(records, 1):
    record["rank"] = rank
    record["compact_candidate"] = (
        record["ellipticity"] <= 2.5
        and 0.5 <= record["minor_sigma"] <= 4.0
        and record["significance"] >= 5.0
    )

compact = [r for r in records if r["compact_candidate"]]

# 6. Save CSV files
fields = list(records[0].keys()) if records else []

for filename, data in (
    ("T1_all_refined_candidates.csv", records),
    ("T1_compact_candidates.csv", compact),
):
    with open(OUT / filename, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(data)

# 7. Generate overlay of strongest compact candidates
overlay = image.copy()
for r in compact[:500]:
    x, y = int(round(r["x"])), int(round(r["y"]))
    cv2.circle(overlay, (x, y), 7, (0, 255, 0), 1)
    cv2.circle(overlay, (x, y), 2, (0, 0, 255), -1)

cv2.imwrite(str(OUT / "T1_refined_overlay.jpg"), overlay)
cv2.imwrite(str(OUT / "T1_refined_background_subtracted.png"),
            np.clip(residual, 0, 255).astype(np.uint8))

# 8. Save report
report = {
    "image": str(IMAGE),
    "dimensions": [int(w), int(h)],
    "method": "multi-scale Gaussian response, local maxima, weighted centroid and shape ranking",
    "threshold": threshold,
    "robust_noise_estimate": noise,
    "total_candidates": len(records),
    "compact_candidates": len(compact),
    "warning": "Candidates are not confirmed astronomical stars. Catalogue verification is required."
}

with open(OUT / "T1_refined_report.json", "w") as f:
    json.dump(report, f, indent=2)

print("\n========== STARLOC 2.0 REFINED DETECTION ==========")
print(f"Image: {w} x {h}")
print(f"Detection threshold: {threshold:.3f}")
print(f"Total refined candidates: {len(records)}")
print(f"Compact candidates: {len(compact)}")
print(f"Output directory: {OUT}")
print("Overlay: T1_refined_overlay.jpg")
print("CSV: T1_all_refined_candidates.csv")
print("Compact CSV: T1_compact_candidates.csv")
print("\nCandidates still require astronomical verification.")
