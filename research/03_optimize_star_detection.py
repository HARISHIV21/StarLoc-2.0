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
image_u8 = np.clip(image * 255, 0, 255).astype(np.uint8)

with (DATA / "synthetic_star_catalogue.csv").open() as f:
    catalogue = list(csv.DictReader(f))

truth = np.array([
    [float(r["x_pixel"]), float(r["y_pixel"])]
    for r in catalogue
])

thresholds = [3, 4, 5, 6, 8, 10, 12]
minimum_areas = [1, 2, 3]
maximum_areas = [40, 80, 150, 250]

best = None
results = []

for threshold in thresholds:
    for min_area in minimum_areas:
        for max_area in maximum_areas:
            binary = (image_u8 > threshold).astype(np.uint8)

            count, labels, stats, centroids = (
                cv2.connectedComponentsWithStats(binary, 8)
            )

            detected = []

            for i in range(1, count):
                area = int(stats[i, cv2.CC_STAT_AREA])

                if min_area <= area <= max_area:
                    detected.append(centroids[i])

            detected = np.array(detected, dtype=float).reshape(-1, 2)

            used = set()
            errors = []

            for point in detected:
                distances = np.linalg.norm(truth - point, axis=1)
                nearest = int(np.argmin(distances))
                error = float(distances[nearest])

                if error <= 5.0 and nearest not in used:
                    used.add(nearest)
                    errors.append(error)

            result = {
                "threshold": threshold,
                "min_area": min_area,
                "max_area": max_area,
                "detections": len(detected),
                "matches": len(errors),
                "mean_error": float(np.mean(errors)) if errors else 999.0,
                "max_error": float(np.max(errors)) if errors else 999.0
            }

            results.append(result)

            score = (len(used), -result["mean_error"])

            if best is None or score > best["score"]:
                best = {
                    "score": score,
                    "config": result,
                    "detected": detected
                }

with (RESULTS / "detection_parameter_comparison.csv").open(
    "w", newline=""
) as f:
    writer = csv.DictWriter(f, fieldnames=list(results[0].keys()))
    writer.writeheader()
    writer.writerows(results)

config = best["config"]
detected = best["detected"]

# Save optimized detections.
with (RESULTS / "optimized_detections.csv").open("w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["detection_id", "x_pixel", "y_pixel"])

    for i, (x, y) in enumerate(detected, 1):
        writer.writerow([i, f"{x:.4f}", f"{y:.4f}"])

# Plot optimized detection result.
fig, ax = plt.subplots(figsize=(10, 10))
ax.imshow(image, cmap="gray", vmin=0, vmax=1)
ax.scatter(
    truth[:, 0], truth[:, 1],
    marker="+", s=18, label="Catalogue"
)

if len(detected):
    ax.scatter(
        detected[:, 0], detected[:, 1],
        facecolors="none", edgecolors="red",
        s=35, label="Optimized detections"
    )

ax.set_title("Optimized Fisheye Star Detection")
ax.set_xlabel("X pixel")
ax.set_ylabel("Y pixel")
ax.legend()
fig.tight_layout()
fig.savefig(RESULTS / "optimized_star_detection.png", dpi=160)
plt.close(fig)

print("\nSTAR DETECTION OPTIMIZATION")
print("--------------------------------")
print("Best threshold:", config["threshold"])
print("Minimum area:", config["min_area"])
print("Maximum area:", config["max_area"])
print("Detected regions:", config["detections"])
print("Catalogue matches:", config["matches"], "/", len(catalogue))
print("Mean matching error:", f'{config["mean_error"]:.4f} pixels')
print("Maximum matching error:", f'{config["max_error"]:.4f} pixels')
print("\nSaved:")
print(RESULTS / "detection_parameter_comparison.csv")
print(RESULTS / "optimized_detections.csv")
print(RESULTS / "optimized_star_detection.png")
