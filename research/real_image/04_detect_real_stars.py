from pathlib import Path
import json
import csv
import cv2
import numpy as np

ROOT = Path("research/real_image/data/network/ASK033")
IMAGE_PATH = ROOT / "ASK033_live_original.jpg"
OUT = Path("research/real_image/results/ASK033")
OUT.mkdir(parents=True, exist_ok=True)

if not IMAGE_PATH.exists():
    raise SystemExit("Original ASK033 image not found: " + str(IMAGE_PATH))

image = cv2.imread(str(IMAGE_PATH), cv2.IMREAD_COLOR)
if image is None:
    raise SystemExit("Could not read the downloaded image.")

gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
height, width = gray.shape

# Estimate slowly varying background and subtract it.
background = cv2.GaussianBlur(gray, (0, 0), 12.0)
residual = gray.astype(np.float32) - background.astype(np.float32)

# Robust threshold based on the positive residual distribution.
positive = residual[residual > 0]
if positive.size == 0:
    raise SystemExit("No positive image features detected.")

median = float(np.median(positive))
mad = float(np.median(np.abs(positive - median)))
robust_sigma = max(1.4826 * mad, 1.0)
threshold = max(5.0, median + 4.0 * robust_sigma)

binary = (residual > threshold).astype(np.uint8) * 255

# Remove isolated single-pixel noise without erasing compact sources.
kernel = np.ones((2, 2), np.uint8)
binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)

count, labels, stats, centroids = cv2.connectedComponentsWithStats(
    binary, connectivity=8
)

detections = []
for i in range(1, count):
    x, y, w, h, area = stats[i]

    if area < 2 or area > 80:
        continue

    if w > 14 or h > 14:
        continue

    component = (labels[y:y+h, x:x+w] == i)
    patch = residual[y:y+h, x:x+w]
    weights = np.maximum(patch, 0) * component

    total = float(weights.sum())
    if total <= 0:
        continue

    yy, xx = np.indices(weights.shape)
    cx = float(x + (weights * xx).sum() / total)
    cy = float(y + (weights * yy).sum() / total)

    peak = float(patch[component].max())
    flux = float(total)

    detections.append({
        "id": len(detections) + 1,
        "x_px": cx,
        "y_px": cy,
        "area_px": int(area),
        "width_px": int(w),
        "height_px": int(h),
        "peak_residual": peak,
        "positive_flux": flux
    })

# Nine-section coverage report.
section_counts = []
for row in range(3):
    for col in range(3):
        x0 = col * width // 3
        x1 = (col + 1) * width // 3
        y0 = row * height // 3
        y1 = (row + 1) * height // 3

        local = [
            d for d in detections
            if x0 <= d["x_px"] < x1 and y0 <= d["y_px"] < y1
        ]

        section_counts.append({
            "section": f"R{row+1}C{col+1}",
            "x_min": x0,
            "x_max": x1,
            "y_min": y0,
            "y_max": y1,
            "candidate_count": len(local)
        })

# Draw detections and section boundaries.
annotated = image.copy()

for d in detections:
    point = (int(round(d["x_px"])), int(round(d["y_px"])))
    cv2.circle(annotated, point, 5, (0, 255, 0), 1)

for col in range(1, 3):
    x = col * width // 3
    cv2.line(annotated, (x, 0), (x, height), (255, 180, 0), 1)

for row in range(1, 3):
    y = row * height // 3
    cv2.line(annotated, (0, y), (width, y), (255, 180, 0), 1)

cv2.imwrite(str(OUT / "ASK033_detection_overlay.jpg"), annotated)
cv2.imwrite(str(OUT / "ASK033_background_subtracted.png"),
            np.clip(residual + 128, 0, 255).astype(np.uint8))
cv2.imwrite(str(OUT / "ASK033_detection_mask.png"), binary)

with open(OUT / "real_star_candidates.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=list(detections[0].keys())
                            if detections else
                            ["id", "x_px", "y_px", "area_px",
                             "width_px", "height_px",
                             "peak_residual", "positive_flux"])
    writer.writeheader()
    writer.writerows(detections)

report = {
    "camera_id": "ASK033",
    "image": str(IMAGE_PATH),
    "width_px": width,
    "height_px": height,
    "method": "Gaussian background subtraction + robust residual threshold + connected components",
    "threshold_residual": threshold,
    "robust_sigma": robust_sigma,
    "candidate_count": len(detections),
    "section_counts": section_counts,
    "important_note": (
        "These are image-feature candidates, not yet confirmed stars. "
        "Clouds, hot pixels, compression artifacts and lights may be included. "
        "No catalogue identification or astrometric calibration has been performed."
    )
}

(OUT / "detection_report.json").write_text(
    json.dumps(report, indent=2), encoding="utf-8"
)

print("\nSTARLOC 2.0 — REAL IMAGE STAR DETECTION")
print("=" * 58)
print("Image:", width, "x", height)
print("Residual threshold:", round(threshold, 3))
print("Robust noise estimate:", round(robust_sigma, 3))
print("Candidate sources:", len(detections))

print("\nNINE-SECTION DISTRIBUTION")
for section in section_counts:
    print(section["section"], ":", section["candidate_count"])

print("\nOUTPUTS")
for name in (
    "ASK033_detection_overlay.jpg",
    "ASK033_background_subtracted.png",
    "ASK033_detection_mask.png",
    "real_star_candidates.csv",
    "detection_report.json"
):
    print((OUT / name).resolve())

print("\nREAL IMAGE DETECTION COMPLETE")
print("Note: candidate sources are not yet confirmed astronomical stars.")
