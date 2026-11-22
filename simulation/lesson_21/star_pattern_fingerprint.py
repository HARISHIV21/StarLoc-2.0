
import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


# ==========================================
# StarLoc 2.0 - Lesson 21
# Star Pattern Fingerprint
# ==========================================

image_width = 1280
image_height = 720

fx = 500.0
fy = 500.0

cx = image_width / 2
cy = image_height / 2


# Six simulated stars from earlier lessons
pixels = np.array([
    [640, 360],
    [720, 340],
    [500, 400],
    [100, 100],
    [1180, 620],
    [850, 250]
], dtype=float)


def pixel_to_direction(u, v):

    x = (u - cx) / fx
    y = (v - cy) / fy

    direction = np.array([x, y, 1.0])

    return direction / np.linalg.norm(direction)


def angular_separation(a, b):

    dot_product = np.dot(a, b)
    dot_product = np.clip(dot_product, -1.0, 1.0)

    return np.degrees(np.arccos(dot_product))


# Convert pixels to direction vectors
directions = np.array([
    pixel_to_direction(u, v)
    for u, v in pixels
])


# Calculate every unique star pair
pairs = []

for i in range(len(directions)):

    for j in range(i + 1, len(directions)):

        angle = angular_separation(
            directions[i],
            directions[j]
        )

        pairs.append((i + 1, j + 1, angle))


# Sort angles from smallest to largest
pairs.sort(key=lambda item: item[2])


print("==========================================")
print("StarLoc 2.0 - Lesson 21")
print("Star Pattern Fingerprint")
print("==========================================")

print(f"\nNumber of detected stars: {len(directions)}")
print(f"Number of unique pairs: {len(pairs)}")

print("\nSorted angular fingerprint:\n")

for rank, (star_a, star_b, angle) in enumerate(pairs, start=1):

    print(
        f"{rank:02d}. "
        f"Star {star_a} - Star {star_b}: "
        f"{angle:.4f} degrees"
    )


# Save fingerprint as a numerical file
fingerprint = np.array([
    [star_a, star_b, angle]
    for star_a, star_b, angle in pairs
])

np.save(
    "results/lesson_21_fingerprint.npy",
    fingerprint
)


# Plot the sorted angular fingerprint
angles = [pair[2] for pair in pairs]

plt.figure(figsize=(10, 6))

plt.plot(
    range(1, len(angles) + 1),
    angles,
    marker="o"
)

plt.xlabel("Pair rank (sorted by angle)")
plt.ylabel("Angular separation (degrees)")

plt.title("StarLoc 2.0 - Star Pattern Fingerprint")

plt.grid(True, alpha=0.3)
plt.tight_layout()

output_file = "results/lesson_21_fingerprint.png"

plt.savefig(
    output_file,
    dpi=150,
    bbox_inches="tight"
)

plt.close()

print("\nSaved:")
print("results/lesson_21_fingerprint.npy")
print(output_file)

print("\nLesson 21 completed successfully.")
