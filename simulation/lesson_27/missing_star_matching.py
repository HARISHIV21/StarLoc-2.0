
import itertools
import numpy as np

# StarLoc 2.0 - Lesson 27
# Recover a smaller pattern from a reference pattern
# when one genuine star is missing.

TOLERANCE = 0.20  # degrees


def pixel_to_direction(pixel):
    u, v = pixel

    fx = 500.0
    fy = 500.0
    cx = 640.0
    cy = 360.0

    direction = np.array([
        (u - cx) / fx,
        (v - cy) / fy,
        1.0
    ])

    return direction / np.linalg.norm(direction)


def angular_separation(a, b):
    dot = np.clip(np.dot(a, b), -1.0, 1.0)
    return np.degrees(np.arccos(dot))


def fingerprint(directions):
    angles = []

    for i, j in itertools.combinations(
        range(len(directions)), 2
    ):
        angles.append(
            angular_separation(directions[i], directions[j])
        )

    return np.sort(np.array(angles))


def match_fingerprints(reference, measured, tolerance):
    # A smaller pattern may match a subset of the reference.
    if len(measured) > len(reference):
        return False, None

    for selected in itertools.combinations(
        reference, len(measured)
    ):
        candidate = np.sort(np.array(selected))
        errors = np.abs(candidate - measured)

        if np.all(errors <= tolerance):
            return True, errors

    return False, None


# Four genuine stars in the reference pattern.
reference_pixels = np.array([
    [640, 360],
    [720, 340],
    [500, 400],
    [850, 250]
], dtype=float)

reference_directions = np.array([
    pixel_to_direction(p) for p in reference_pixels
])

reference_fingerprint = fingerprint(reference_directions)

# Simulate one missing star: remove the fourth star.
observed_pixels = reference_pixels[:3]

observed_directions = np.array([
    pixel_to_direction(p) for p in observed_pixels
])

observed_fingerprint = fingerprint(observed_directions)

matched, errors = match_fingerprints(
    reference_fingerprint,
    observed_fingerprint,
    TOLERANCE
)

print("========================================")
print("StarLoc 2.0 - Lesson 27")
print("Missing-Star Pattern Matching")
print("========================================")

print("\nREFERENCE")
print("Stars:", len(reference_pixels))
print("Angular pairs:", len(reference_fingerprint))
print(
    "Fingerprint:",
    np.round(reference_fingerprint, 4)
)

print("\nOBSERVED IMAGE")
print("Stars:", len(observed_pixels))
print("Angular pairs:", len(observed_fingerprint))
print(
    "Fingerprint:",
    np.round(observed_fingerprint, 4)
)

print("\nMATCHING")
print("Tolerance:", TOLERANCE, "degrees")
print("Pattern match:", "MATCH" if matched else "NO MATCH")

if matched:
    print("Matched angular differences:", np.round(errors, 4))

print("\nLesson 27 completed successfully.")
