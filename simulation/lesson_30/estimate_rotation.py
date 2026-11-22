
import numpy as np

# StarLoc 2.0 - Lesson 30
# Estimate a rotation about the Z-axis from
# corresponding reference and observed directions.


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


def estimate_z_rotation(reference, observed):
    # Estimate the rotation using the XY projections.
    cross_sum = 0.0
    dot_sum = 0.0

    for ref, obs in zip(reference, observed):
        cross_sum += ref[0] * obs[1] - ref[1] * obs[0]
        dot_sum += ref[0] * obs[0] + ref[1] * obs[1]

    return np.degrees(np.arctan2(cross_sum, dot_sum))


reference_directions = np.array([
    normalize([0.30, 0.10, 1.0]),
    normalize([-0.20, 0.25, 1.0]),
    normalize([0.10, -0.30, 1.0]),
    normalize([-0.35, -0.15, 1.0]),
    normalize([0.25, 0.30, 1.0])
])

# Simulate an unknown rotation.
true_angle = 30.0
R_true = rotation_matrix_z(true_angle)

observed_directions = np.array([
    R_true @ direction
    for direction in reference_directions
])

# Estimate the rotation from the two sets of directions.
estimated_angle = estimate_z_rotation(
    reference_directions,
    observed_directions
)

error = estimated_angle - true_angle

print("========================================")
print("StarLoc 2.0 - Lesson 30")
print("Rotation Estimation")
print("========================================")

print(f"\nTrue rotation:      {true_angle:.4f} degrees")
print(f"Estimated rotation: {estimated_angle:.4f} degrees")
print(f"Estimation error:   {error:.6f} degrees")

print("\nLesson 30 completed successfully.")
