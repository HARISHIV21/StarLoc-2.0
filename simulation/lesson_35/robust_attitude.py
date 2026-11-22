 
import itertools
import numpy as np

# StarLoc 2.0 - Lesson 35
# Simplified consensus-based attitude estimation.
# Uses synthetic, known star correspondences.

RNG = np.random.default_rng(35)

NOISE_SIGMA = 0.0005
INLIER_THRESHOLD_DEG = 0.15
TRIALS = 250


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
    H = observed.T @ reference
    U, _, Vt = np.linalg.svd(H)

    correction = np.eye(3)
    if np.linalg.det(U @ Vt) < 0:
        correction[2, 2] = -1

    return U @ correction @ Vt


def angular_errors(R, reference, observed):
    predicted = np.array([R @ v for v in reference])

    dots = np.sum(predicted * observed, axis=1)
    dots = np.clip(dots, -1.0, 1.0)

    return np.degrees(np.arccos(dots))


def consensus_estimate(reference, observed):
    count = len(reference)
    best_inliers = np.array([], dtype=int)
    best_rotation = None

    # For this small educational example, test all pairs.
    # A pair can define a candidate rotation, provided its
    # two reference directions are not nearly parallel.
    for i, j in itertools.combinations(range(count), 2):
        subset = [i, j]

        R_candidate = estimate_rotation(
            reference[subset],
            observed[subset]
        )

        errors = angular_errors(
            R_candidate, reference, observed
        )

        inliers = np.where(
            errors < INLIER_THRESHOLD_DEG
        )[0]

        if len(inliers) > len(best_inliers):
            best_inliers = inliers
            best_rotation = R_candidate

    if best_rotation is None or len(best_inliers) < 3:
        return None, best_inliers

    # Refit using the largest consensus group.
    refined_rotation = estimate_rotation(
        reference[best_inliers],
        observed[best_inliers]
    )

    return refined_rotation, best_inliers


# Generate eight known reference directions.
reference = np.array([
    normalize([0.30, 0.10, 1.00]),
    normalize([-0.20, 0.25, 1.00]),
    normalize([0.10, -0.30, 1.00]),
    normalize([-0.35, -0.15, 1.00]),
    normalize([0.25, 0.30, 1.00]),
    normalize([-0.10, 0.05, 1.00]),
    normalize([0.05, 0.35, 1.00]),
    normalize([-0.25, -0.25, 1.00])
])

R_true = (
    rotation_z(30.0)
    @ rotation_y(15.0)
    @ rotation_x(-10.0)
)

observed = np.array([
    R_true @ direction for direction in reference
])

# Add small noise to every observation.
observed = np.array([
    normalize(v + RNG.normal(0, NOISE_SIGMA, size=3))
    for v in observed
])

# Deliberately corrupt one correspondence.
bad_index = 0
observed[bad_index] = normalize([0.8, -0.5, 0.3])

# Compare ordinary least squares with consensus estimation.
ordinary_rotation = estimate_rotation(reference, observed)
ordinary_errors = angular_errors(
    ordinary_rotation, reference, observed
)

robust_rotation, inliers = consensus_estimate(
    reference, observed
)

print("========================================")
print("StarLoc 2.0 - Lesson 35")
print("Robust Attitude Estimation")
print("========================================")

print("\nTotal correspondences:", len(reference))
print("Deliberately corrupted index:", bad_index)

print("\nOrdinary estimation:")
print("Inliers within threshold:", np.sum(
    ordinary_errors < INLIER_THRESHOLD_DEG
), "/", len(reference))
print("Median angular error:", f"{np.median(ordinary_errors):.4f} degrees")

print("\nConsensus estimation:")
if robust_rotation is None:
    print("No sufficiently large consensus found.")
else:
    robust_errors = angular_errors(
        robust_rotation, reference, observed
    )

    print("Inlier indices:", inliers.tolist())
    print("Inlier count:", len(inliers), "/", len(reference))
    print("Median angular error:", f"{np.median(robust_errors):.4f} degrees")

print("\nLesson 35 completed successfully.")
