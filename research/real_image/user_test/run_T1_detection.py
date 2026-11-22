from pathlib import Path
import json
import csv
import cv2
import numpy as np

IMAGE_PATH = Path("research/real_image/user_test/T1.jpeg")
OUT = Path("research/real_image/user_test/T1_detection_results")
OUT.mkdir(parents=True, exist_ok=True)

image = cv2.imread(str(IMAGE_PATH), cv2.IMREAD_COLOR)
if image is None:
    raise SystemExit("Could not load T1.jpeg")

gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
height, width = gray.shape

# Same detection algorithm as the existing StarLoc real-image detector.
background = cv2.GaussianBlur(gray, (0, 0), 12.0)
residual = gray.astype(np.float32) - background.astype(np.float32)

positive = residual[residual > 0]
if positive.size == 0:
    raise SystemExit("No positive image features detected.")

median = float(np.median(positive))
mad = float(np.median(np.abs(positive - median)))
robust_sigma = max(1.4826 * mad, 1.0)
threshold = max(5.0, median + 4.0 * robust_sigma)

binary = (residual > threshold).astype(np.uint8) * 255
kernel = np.ones((2, 2), np.uint8)
binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)

count, labels, stats, centroids = cv2.connectedComponentsWithStats(
    binary, connectivity=8
)

detections = []
for i in range(1, count):
    x, y, w, h, area = stats[i]

    if area < 2 or area > 80 or w > 14 or h > 14:
        continue

    component = labels[y:y+h, x:x+w] == i
    patch = residual[y:y+h, x:x+w]
    weights = np.maximum(patch, 0) * component

    total = float(weights.sum())
    if total <= 0:
        continue

    yy, xx = np.indices(weights.shape)
    cx = float(x + (weights * xx).sum() / total)
    cy = float(y + (weights * yy).sum() / total)

    detections.append({
        "id": len(detections) + 1,
        "x_px": cx,
        "y_px": cy,
        "area_px": int(area),
        "width_px": int(w),
        "height_px": int(h),
        "peak_residual": float(patch[component].max()),
        "positive_flux": total
    })

# Save overlay.
annotated = image.copy()
for d in detections:
    point = (round(d["x_px"]), round(d["y_px"]))
    cv2.circle(annotated, point, 5, (0, 255, 0), 1)

cv2.imwrite(str(OUT / "T1_detection_overlay.jpg"), annotated)
cv2.imwrite(
    str(OUT / "T1_background_subtracted.png"),
    np.clip(residual + 128, 0, 255).astype(np.uint8)
)
cv2.imwrite(str(OUT / "T1_detection_mask.png"), binary)

with (OUT / "T1_detected_candidates.csv").open("w", newline="") as f:
    fields = [
        "id", "x_px", "y_px", "area_px",
        "width_px", "height_px", "peak_residual", "positive_flux"
    ]
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerows(detections)

report = {
    "input": str(IMAGE_PATH),
    "dimensions": [width, height],
    "method": "Existing StarLoc Gaussian background subtraction, robust threshold and connected components",
    "threshold": threshold,
    "robust_sigma": robust_sigma,
    "candidate_count": len(detections),
    "classification": "Unverified image-feature candidates, not confirmed stars"
}

(OUT / "T1_detection_report.json").write_text(
    json.dumps(report, indent=2)
)

print("\n========== STARLOC 2.0: T1 DETECTION ==========")
print("Image dimensions:", width, "x", height)
print("Threshold:", round(threshold, 3))
print("Robust noise estimate:", round(robust_sigma, 3))
print("Detected candidates:", len(detections))
print("\nOUTPUTS:")
for p in sorted(OUT.iterdir()):
    print(p.resolve())
print("\nDetection run complete. Candidates still require astronomical verification.")
