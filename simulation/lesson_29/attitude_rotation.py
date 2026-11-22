
import numpy as np

# StarLoc 2.0 - Lesson 29
# Explore how camera directions change under rotation.

def normalize(vector):
    return vector / np.linalg.norm(vector)


def rotation_matrix_z(angle_degrees):
    angle = np.radians(angle_degrees)

    c = np.cos(angle)
    s = np.sin(angle)

    return np.array([
        [c, -s, 0.0],
        [s,  c, 0.0],
        [0.0, 0.0, 1.0]
    ])


# Three example star directions in the camera frame.
camera_directions = np.array([
    normalize([0.0, 0.0, 1.0]),
    normalize([0.2, 0.1, 1.0]),
    normalize([-0.3, 0.2, 1.0])
])

# Simulate a 30-degree rotation about the Z-axis.
angle_degrees = 30.0
R = rotation_matrix_z(angle_degrees)

rotated_directions = np.array([
    R @ direction
    for direction in camera_directions
])

print("========================================")
print("StarLoc 2.0 - Lesson 29")
print("Attitude and Rotation")
print("========================================")

print("\nRotation matrix:")
print(np.round(R, 4))

for i, (before, after) in enumerate(
    zip(camera_directions, rotated_directions),
    start=1
):
    print(f"\nStar {i}")
    print("Original direction:", np.round(before, 4))
    print("Rotated direction: ", np.round(after, 4))
    print("Original norm:", f"{np.linalg.norm(before):.6f}")
    print("Rotated norm: ", f"{np.linalg.norm(after):.6f}")

print("\nApplied rotation:", angle_degrees, "degrees about Z")
print("Lesson 29 completed successfully.")
