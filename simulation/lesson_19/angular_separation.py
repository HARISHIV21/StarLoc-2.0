
import numpy as np
import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt


# ==========================================
# StarLoc 2.0 - Lesson 19
# Angular Separation Between Stars
# ==========================================

# Camera parameters
image_width = 1280
image_height = 720

fx = 500.0
fy = 500.0

cx = image_width / 2
cy = image_height / 2


# Five example star positions from Lesson 18
pixels = np.array([
    [640, 360],
    [720, 340],
    [500, 400],
    [100, 100],
    [1180, 620]
], dtype=float)


# Convert pixel position into a unit 3D direction
def pixel_to_direction(u, v):

    x = (u - cx) / fx
    y = (v - cy) / fy

    direction = np.array([x, y, 1.0])

    direction = direction / np.linalg.norm(direction)

    return direction


# Calculate direction vectors
directions = np.array([
    pixel_to_direction(u, v)
    for u, v in pixels
])


# Calculate angle between two unit vectors
def angular_separation(vector_a, vector_b):

    dot_product = np.dot(vector_a, vector_b)

    # Protect against tiny floating-point errors
    dot_product = np.clip(dot_product, -1.0, 1.0)

    angle_radians = np.arccos(dot_product)

    angle_degrees = np.degrees(angle_radians)

    return angle_degrees


# ==========================================
# Print individual direction vectors
# ==========================================

print("==========================================")
print("StarLoc 2.0 - Lesson 19")
print("Angular Separation")
print("==========================================")

print("\nStar direction vectors:\n")

for i, direction in enumerate(directions):

    print(
        f"Star {i + 1}: "
        f"[{direction[0]:.4f}, "
        f"{direction[1]:.4f}, "
        f"{direction[2]:.4f}]"
    )


# ==========================================
# Calculate separation for every star pair
# ==========================================

pairs = []
angles = []

print("\nAngular separation between star pairs:\n")

for i in range(len(directions)):

    for j in range(i + 1, len(directions)):

        angle = angular_separation(
            directions[i],
            directions[j]
        )

        pairs.append((i + 1, j + 1))
        angles.append(angle)

        print(
            f"Star {i + 1} and Star {j + 1}: "
            f"{angle:.4f} degrees"
        )


# ==========================================
# Save a plot of the pairwise angles
# ==========================================

pair_labels = [
    f"S{i}-S{j}"
    for i, j in pairs
]

plt.figure(figsize=(11, 6))

plt.bar(pair_labels, angles)

plt.xlabel("Star pair")
plt.ylabel("Angular separation (degrees)")

plt.title(
    "StarLoc 2.0 - Angular Separation Between Star Pairs"
)

plt.xticks(rotation=45)
plt.grid(axis="y", alpha=0.3)
plt.tight_layout()

output_file = "results/lesson_19_angular_separation.png"

plt.savefig(
    output_file,
    dpi=150,
    bbox_inches="tight"
)

plt.close()


print("\n------------------------------------------")
print(f"Star pairs evaluated: {len(pairs)}")
print(f"Plot saved to: {output_file}")
print("Lesson 19 completed successfully.")
