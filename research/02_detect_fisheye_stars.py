import csv
from pathlib import Path

import cv2
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "research" / "data" / "synthetic"
RESULTS = ROOT / "research" / "results"

image = np.load(DATA / "synthetic_fisheye.npy")
catalogue_path = DATA / "synthetic_star_catalogue.csv"

# Smooth background noise while preserving compact star peaks.
image_u8 = np.clip(image * 255, 0, 255).astype(np.uint8)
blurred = cv2.GaussianBlur(image_u8, (3, 3), 0)

# Threshold and connected-component detection.
threshold = 12
binary = (blurred > threshold).astype(np.uint8)

count, labels, stats, centroids = cv2.connectedComponentsWithStats(
    binary, connectivity=8
)

detections = []

for i in range(1, count):
    area = int(stats[i, cv2.CC_STAT_AREA])

    if area < 2 or area > 250:
        continue

    x, y = centroids[i]
    detections.append((float(x), float(y), area))

# Load ground-truth synthetic catalogue.
with catalogue_path.open() as f:
    reader = csv.DictReader(f)
    catalogue = list(reader)

truth = np.array([
    [float(row["x_pixel"]), float(row["y_pixel"])]
    for row in catalogue
])

detected = np.array([
    [item[0], item[1]] for item in detections
])

# Match each detected centroid to its nearest catalogue star.
matches = []
used_truth = set()
tolerance_px = 5.0

for detection_index, point in enumerate(detected):
    distances = np.linalg.norm(truth - point, axis=1)
    nearest = int(np.argmin(distances))
    error = float(distances[nearest])

    if error <= tolerance_px and nearest not in used_truth:
        matches.append((detection_index, nearest, error))
        used_truth.add(nearest)

# Save detections.
with (RESULTS / "detected_stars.csv").open("w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["detection_id", "x_pixel", "y_pixel", "area_pixels"])
    for i, (x, y, area) in enumerate(detections, 1):
        writer.writerow([i, f"{x:.3f}", f"{y:.3f}", area])

# Save matched correspondences.
with (RESULTS / "star_matches.csv").open("w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow([
        "detection_id", "catalogue_star_id",
        "detected_x", "detected_y",
        "catalogue_x", "catalogue_y", "pixel_error"
    ])
    for detection_index, truth_index, error in matches:
        d = detections[detection_index]
        c = catalogue[truth_index]
        writer.writerow([
            detection_index + 1,
            c["star_id"],
            f"{d[0]:.3f}", f"{d[1]:.3f}",
            c["x_pixel"], c["y_pixel"],
            f"{error:.4f}"
        ])

# Visualise detections and catalogue reference positions.
fig, ax = plt.subplots(figsize=(10, 10))
ax.imshow(image, cmap="gray", origin="upper", vmin=0, vmax=1)

if len(detected):
    ax.scatter(
        detected[:, 0], detected[:, 1],
        s=35, facecolors="none", edgecolors="red",
        label="Detected stars"
    )

ax.scatter(
    truth[:, 0], truth[:, 1],
    s=12, marker="+", color="lime",
    label="Catalogue positions"
)

ax.set_title("StarLoc 2.0 — Synthetic Fisheye Star Detection")
ax.set_xlabel("X pixel")
ax.set_ylabel("Y pixel")
ax.legend()
fig.tight_layout()
fig.savefig(RESULTS / "fisheye_star_detection.png", dpi=160)
plt.close(fig)

errors = [item[2] for item in matches]

print("\nSTARLOC 2.0 — STAR DETECTION")
print("--------------------------------")
print(f"Catalogue stars: {len(catalogue)}")
print(f"Detected regions: {len(detections)}")
print(f"Matched stars: {len(matches)}")
print(f"Unmatched catalogue stars: {len(catalogue) - len(used_truth)}")
print(f"Matching tolerance: {tolerance_px:.1f} pixels")

if errors:
    print(f"Mean matching error: {np.mean(errors):.4f} pixels")
    print(f"Maximum matching error: {np.max(errors):.4f} pixels")

print("\nSaved:")
print(RESULTS / "detected_stars.csv")
print(RESULTS / "star_matches.csv")
print(RESULTS / "fisheye_star_detection.png")
print("\nSTAR DETECTION COMPLETE")
