
import numpy as np

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


# ==========================================
# StarLoc 2.0 - Lesson 23
# False Star Experiment
# ==========================================

image_width = 1280
image_height = 720

fx = 500.0
fy = 500.0

cx = image_width / 2
cy = image_height / 2


# Five genuine star detections
real_pixels = np.array([
    [640, 360],
    [720, 340],
    [500, 400],
    [100, 100],
    [1180, 620]
], dtype=float)


# One false detection caused by noise or an image artifact
false_pixel = np.array([
    [850, 500]
], dtype=float)


def pixel_to_direction(u, v):

    x = (u - cx) / fx
    y = (v - cy) / fy

    direction = np.array([x, y, 1.0])

    return direction / np.linalg.norm(direction)


def calculate_fingerprint(directions):

    angles = []

    for i in range(len(directions)):

        for j in range(i + 1, len(directions)):

            dot = np.dot(
                directions[i],
                directions[j]
            )

            dot = np.clip(dot, -1.0, 1.0)

            angle = np.degrees(
                np.arccos(dot)
            )

            angles.append(angle)

    return np.sort(np.array(angles))


# Convert real pixels to 3D directions
real_directions = np.array([
    pixel_to_direction(u, v)
    for u, v in real_pixels
])


# Convert the false detection
false_direction = pixel_to_direction(
    false_pixel[0, 0],
    false_pixel[0, 1]
)


# Pattern containing only genuine detections
real_fingerprint = calculate_fingerprint(
    real_directions
)


# Pattern containing the false detection as well
all_directions = np.vstack([
    real_directions,
    false_direction
])

contaminated_fingerprint = calculate_fingerprint(
    all_directions
)


# ==========================================
# Print experiment results
# ==========================================

print("==========================================")
print("StarLoc 2.0 - Lesson 23")
print("False Star Experiment")
print("==========================================")

print("\nREAL DETECTIONS")
print(f"Star count: {len(real_directions)}")
print(f"Unique pairs: {len(real_fingerprint)}")

print("\nWITH ONE FALSE DETECTION")
print(f"Detected point count: {len(all_directions)}")
print(f"Unique pairs: {len(contaminated_fingerprint)}")

print("\nReal angular fingerprint:")

for i, angle in enumerate(real_fingerprint, start=1):
    print(f"{i:02d}: {angle:.4f} degrees")

print("\nFingerprint including false detection:")

for i, angle in enumerate(contaminated_fingerprint, start=1):
    print(f"{i:02d}: {angle:.4f} degrees")


# ==========================================
# Visualize the number of measurements
# ==========================================

labels = ["Real stars", "With false detection"]

counts = [
    len(real_fingerprint),
    len(contaminated_fingerprint)
]

plt.figure(figsize=(8, 5))

plt.bar(labels, counts)

plt.ylabel("Number of angular measurements")
plt.title("StarLoc 2.0 - Effect of a False Star")
plt.grid(axis="y", alpha=0.3)
plt.tight_layout()

output_file = "results/lesson_23_false_star.png"

plt.savefig(
    output_file,
    dpi=150,
    bbox_inches="tight"
)

plt.close()


np.save(
    "results/lesson_23_real_fingerprint.npy",
    real_fingerprint
)

np.save(
    "results/lesson_23_contaminated_fingerprint.npy",
    contaminated_fingerprint
)

print("\nSaved graph:", output_file)
print("Lesson 23 completed successfully.")
