
import numpy as np

# StarLoc 2.0 - Lesson 31
# Recover a full 3D rotation using corresponding star directions.


def normalize(vector):
    return vector / np.linalg.norm(vector)


def rotation_x(degrees):
    a = np.radians(degrees)
    c, s = np.cos(a), np.sin(a)

    return np.array([
        [1, 0, 0],
        [0, c, -s],
        [0, s, c]
    ])


def rotation_y(degrees):
    a = np.radians(degrees)
    c, s = np.cos(a), np.sin(a)

    return np.array([
        [c, 0, s],
        [0, 1, 0],
        [-s, 0, c]
    ])


def rotation_z(degrees):
    a = np.radians(degrees)
    c, s = np.cos(a), np.sin(a)

    return np.array([
        [c, -s, 0],
        [s, c, 0],
        [0, 0, 1]
    ])


def estimate_rotation(reference, observed):
    # Find R such that observed ~= R @ reference.
    # Each row in the input arrays is one direction vector.

    H = observed.T @ reference

    U, singular_values, Vt = np.linalg.svd(H)

    # Enforce a proper rotation, with determinant +1.
    correction = np.eye(3)

    if np.linalg.det(U @ Vt) < 0:
        correction[2, 2] = -1

    R = U @ correction @ Vt

    return R


def rotation_error_degrees(R_true, R_estimated):
    relative_rotation = R_estimated @ R_true.T

    cosine = (np.trace(relative_rotation) - 1) / 2
    cosine = np.clip(cosine, -1.0, 1.0)

    return np.degrees(np.arccos(cosine))


# Six non-identical reference star directions.
reference = np.array([
    normalize([0.30, 0.10, 1.00]),
    normalize([-0.20, 0.25, 1.00]),
    normalize([0.10, -0.30, 1.00]),
    normalize([-0.35, -0.15, 1.00]),
    normalize([0.25, 0.30, 1.00]),
    normalize([-0.10, 0.05, 1.00])
])

# Simulate a full 3D spacecraft rotation.
R_true = (
    rotation_z(30.0)
    @ rotation_y(15.0)
    @ rotation_x(-10.0)
)

observed = np.array([
    R_true @ vector for vector in reference
])

# Recover the rotation from the vector correspondences.
R_estimated = estimate_rotation(reference, observed)

error = rotation_error_degrees(R_true, R_estimated)

print("========================================")
print("StarLoc 2.0 - Lesson 31")
print("3D Attitude Estimation")
print("========================================")

print("\nTrue rotation matrix:")
print(np.round(R_true, 5))

print("\nEstimated rotation matrix:")
print(np.round(R_estimated, 5))

print(f"\nRotation estimation error: {error:.8f} degrees")

print("\nRotation determinant:", f"{np.linalg.det(R_estimated):.6f}")
print("Orthogonality check:")
print(np.round(R_estimated @ R_estimated.T, 5))

print("\nLesson 31 completed successfully.")
