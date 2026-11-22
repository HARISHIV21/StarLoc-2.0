import cv2
import csv
import json
import numpy as np
from pathlib import Path

ROOT = Path.cwd()
BASE = ROOT / "research/real_image"
DATA = BASE / "data/network/ASK033"
OUT = BASE / "results/ASK033"
OUT.mkdir(parents=True, exist_ok=True)

IMAGE = DATA / "ASK033_live_original.jpg"
if not IMAGE.exists():
    raise SystemExit(f"Image not found: {IMAGE}")

image = cv2.imread(str(IMAGE), cv2.IMREAD_COLOR)
if image is None:
    raise SystemExit("Could not read original image")

gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
h, w = gray.shape

# Valid image area: exclude borders and camera information overlays.
valid = np.ones((h, w), dtype=np.uint8) * 255
valid[:145, :330] = 0
valid[:115, 1180:] = 0
valid[h-220:, :350] = 0
valid[h-220:, w-370:] = 0
valid[:35, 600:1320] = 0

# Mask compass labels and other known graphical markers.
cv2.circle(valid, (285, 600), 28, 0, -1)
cv2.circle(valid, (1640, 600), 35, 0, -1)
cv2.circle(valid, (840, 1390), 35, 0, -1)

# Mask Moon disc and strong lower-right glare/reflection.
cv2.circle(valid, (1860, 130), 85, 0, -1)
cv2.circle(valid, (1540, 700), 235, 0, -1)

# Exclude the obstructed upper-right tree region.
tree = np.array([
    [1710, 40], [1919, 40], [1919, 510],
    [1870, 430], [1810, 330], [1760, 220]
], dtype=np.int32)
cv2.fillPoly(valid, [tree], 0)

# Exclude a narrow outer border where the fisheye housing is visible.
valid[:12, :] = 0
valid[-12:, :] = 0
valid[:, :12] = 0
valid[:, -12:] = 0

# Estimate smooth background and retain compact positive sources.
background = cv2.GaussianBlur(
    gray.astype(np.float32), (0, 0), 15
)
residual = gray.astype(np.float32) - background

pixels = residual[valid > 0]
med = float(np.median(pixels))
mad = float(np.median(np.abs(pixels - med)))
sigma = max(1.0, 1.4826 * mad)
threshold = max(5.0, med + 4.5 * sigma)

# Candidate local maxima.
residual_u8 = np.clip(residual, 0, 255).astype(np.uint8)
local_max = cv2.dilate(
    residual_u8,
    cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
)

peak_mask = (
    (residual >= threshold) &
    (residual_u8 == local_max) &
    (valid > 0)
).astype(np.uint8)

ys, xs = np.where(peak_mask)

detections = []
for x, y in zip(xs, ys):
    # Avoid image-boundary patches.
    if x < 5 or y < 5 or x >= w-5 or y >= h-5:
        continue

    patch = residual[y-4:y+5, x-4:x+5].copy()
    weights = np.maximum(patch, 0)
    total = float(weights.sum())
    if total <= 0:
        continue

    yy, xx = np.mgrid[-4:5, -4:5]
    cx = float((weights * xx).sum() / total)
    cy = float((weights * yy).sum() / total)

    # Weighted source-shape moments.
    xx2 = float((weights * (xx-cx)**2).sum() / total)
    yy2 = float((weights * (yy-cy)**2).sum() / total)
    xy2 = float((weights * (xx-cx) * (yy-cy)).sum() / total)

    cov = np.array([[xx2, xy2], [xy2, yy2]])
    eig = np.maximum(np.linalg.eigvalsh(cov), 0)
    major = float(np.sqrt(eig[1]))
    minor = float(np.sqrt(eig[0]))
    elongation = major / max(minor, 0.01)

    peak = float(residual[y, x])
    local_snr = peak / sigma

    # Reject broad or strongly elongated structures.
    if major > 3.5 or elongation > 3.0:
        continue

    detections.append({
        "x": x + cx,
        "y": y + cy,
        "peak": peak,
        "snr_estimate": local_snr,
        "major_sigma": major,
        "minor_sigma": minor,
        "elongation": elongation
    })

# Assign nine image sections.
for d in detections:
    col = min(3, int(d["x"] / (w / 3)) + 1)
    row = min(3, int(d["y"] / (h / 3)) + 1)
    d["section"] = f"R{row}C{col}"

# Draw quality-filtered candidates.
overlay = image.copy()
for d in detections:
    p = (int(round(d["x"])), int(round(d["y"])))
    cv2.circle(overlay, p, 5, (0, 255, 0), 1)

# Draw section boundaries.
for x in (w//3, 2*w//3):
    cv2.line(overlay, (x, 0), (x, h), (255, 180, 0), 1)
for y in (h//3, 2*h//3):
    cv2.line(overlay, (0, y), (w, y), (255, 180, 0), 1)

cv2.imwrite(str(OUT / "ASK033_quality_detections.jpg"), overlay)
cv2.imwrite(str(OUT / "ASK033_valid_sky_mask.png"), valid)
cv2.imwrite(
    str(OUT / "ASK033_background_residual.png"),
    np.clip(residual + 128, 0, 255).astype(np.uint8)
)

fields = [
    "x", "y", "peak", "snr_estimate",
    "major_sigma", "minor_sigma", "elongation", "section"
]
with open(OUT / "quality_candidates.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerows(detections)

section_counts = {}
for row in range(1, 4):
    for col in range(1, 4):
        name = f"R{row}C{col}"
        section_counts[name] = sum(
            d["section"] == name for d in detections
        )

report = {
    "image": str(IMAGE),
    "dimensions": [w, h],
    "background_median": med,
    "robust_noise_sigma": sigma,
    "detection_threshold": threshold,
    "quality_filtered_candidates": len(detections),
    "section_counts": section_counts,
    "method": "Local background subtraction, local maxima, centroid moments and compactness filtering",
    "warning": "Candidates are not yet confirmed catalogue stars."
}
(OUT / "quality_detection_report.json").write_text(
    json.dumps(report, indent=2)
)

print("\nSTARLOC 2.0 — PHASE 18")
print("=" * 58)
print("Image:", w, "x", h)
print("Background median:", round(med, 3))
print("Robust noise sigma:", round(sigma, 3))
print("Detection threshold:", round(threshold, 3))
print("Quality-filtered candidates:", len(detections))

print("\nNINE-SECTION DISTRIBUTION")
for name, count in section_counts.items():
    print(name, ":", count)

print("\nSAVED RESULTS")
for name in (
    "ASK033_quality_detections.jpg",
    "ASK033_valid_sky_mask.png",
    "ASK033_background_residual.png",
    "quality_candidates.csv",
    "quality_detection_report.json"
):
    print((OUT / name).resolve())

print("\nPHASE 18 COMPLETE")
print("These are filtered candidates, not confirmed stars.")
