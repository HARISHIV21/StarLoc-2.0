
import numpy as np

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


# ==========================================
# StarLoc 2.0 - Lesson 20
# Rotation and Angular Separation
# ==========================================

# Camera parameters
image_width = 1280
image_height = 720

fx = 500.0
fy = 500.0

cx = image_width / 2
cy = image_height / 2


# Five example star pixel positions from Lesson 19
pixels = np.array([
    [640, 360],
    [720, 340],
    [500, 400],
    [100, 100],
    [1180, 620]
], dtype=float)


# Convert pixel coordinates into unit direction vectors
def pixel_to_direction(u, v):

    x = (u - cx) / fx
    y = (v - cy) / fy

    direction = np.array([x, y, 1.0])

    return direction / np.linalg.norm(direction)


directions = np.array([
    pixel_to_direction(u, v)
    for u, v in pixels
])


# Calculate the angle between two unit vectors
def angular_separation(a, b):

    dot_product = np.dot(a, b)
    dot_product = np.clip(dot_product, -1.0, 1.0)

    return np.degrees(np.arccos(dot_product))


# Calculate all unique pairwise angles
def calculate_all_angles(vectors):

    angles = []
    labels = []

    for i in range(len(vectors)):

        for j in range(i + 1, len(vectors)):

            angle = angular_separation(
                vectors[i],
                vectors[j]
            )

            angles.append(angle)
            labels.append(f"S{i + 1}-S{j + 1}")

    return np.array(angles), labels


# ==========================================
# Create a 3D rotation
# ==========================================

def rotation_x(angle):
    c = np.cos(angle)
    s = np.sin(angle)

    return np.array([
        [1, 0, 0],
        [0, c, -s],
        [0, s, c]
    ])


def rotation_y(angle):
    c = np.cos(angle)
    s = np.sin(angle)

    return np.array([
        [c, 0, s],
        [0, 1, 0],
        [-s, 0, c]
    ])


def rotation_z(angle):
    c = np.cos(angle)
    s = np.sin(angle)

    return np.array([
        [c, -s, 0],
        [s, c, 0],
        [0, 0, 1]
    ])


# Rotate by 20 degrees around X,
# 30 degrees around Y, and 40 degrees around Z.

rx = np.radians(20)
ry = np.radians(30)
rz = np.radians(40)

R = rotation_z(rz) @ rotation_y(ry) @ rotation_x(rx)


# Apply the same rotation to every star
rotated_directions = (R @ directions.T).T


# ==========================================
# Compare angular separations
# ==========================================

original_angles, labels = calculate_all_angles(
    directions
)

rotated_angles, _ = calculate_all_angles(
    rotated_directions
)

differences = np.abs(
    original_angles - rotated_angles
)


print("==========================================")
print("StarLoc 2.0 - Lesson 20")
print("Rotation Invariance Test")
print("==========================================")

print("\nApplied rotation:")
print("X axis: 20 degrees")
print("Y axis: 30 degrees")
print("Z axis: 40 degrees")

print("\nPairwise angular separation:\n")

for i, label in enumerate(labels):

    print(
        f"{label}: "
        f"Before = {original_angles[i]:.6f} degrees, "
        f"After = {rotated_angles[i]:.6f} degrees, "
        f"Difference = {differences[i]:.10f} degrees"
    )


print("\n------------------------------------------")
print(f"Number of star pairs: {len(labels)}")
print(
    "Maximum angle difference: "
    f"{np.max(differences):.12f} degrees"
)
print("------------------------------------------")


# ==========================================
# Plot original vs rotated angles
# ==========================================

x = np.arange(len(labels))
bar_width = 0.4

plt.figure(figsize=(12, 6))

plt.bar(
    x - bar_width / 2,
    original_angles,
    bar_width,
    label="Before rotation"
)

plt.bar(
    x + bar_width / 2,
    rotated_angles,
    bar_width,
    label="After rotation"
)

plt.xticks(x, labels, rotation=45)

plt.xlabel("Star pair")
plt.ylabel("Angular separation (degrees)")

plt.title(
    "StarLoc 2.0 - Angular Separation Before and After Rotation"
)

plt.legend()
plt.grid(axis="y", alpha=0.3)
plt.tight_layout()

output_file = "results/lesson_20_rotation_invariance.png"

plt.savefig(
    output_file,
    dpi=150,
    bbox_inches="tight"
)

plt.close()


print(f"\nPlot saved to: {output_file}")
print("Lesson 20 completed successfully.")
