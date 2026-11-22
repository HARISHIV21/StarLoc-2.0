
import numpy as np

# StarLoc 2.0 - Lesson 26
# Test whether a genuine three-star pattern can be
# recovered after adding a false detection.

TOLERANCE = 0.20  # degrees


def pixel_to_direction(pixel):
    u, v = pixel

    fx = 500.0
    fy = 500.0
    cx = 640.0
    cy = 360.0

    x = (u - cx) / fx
    y = (v - cy) / fy

    direction = np.array([x, y, 1.0])
    return direction / np.linalg.norm(direction)


def angular_separation(a, b):
    dot = np.clip(np.dot(a, b), -1.0, 1.0)
    return np.degrees(np.arccos(dot))


def fingerprint(directions):
    angles = []

    for i in range(len(directions)):
        for j in range(i + 1, len(directions)):
            angles.append(
                angular_separation(directions[i], directions[j])
            )

    return np.sort(np.array(angles))


def find_matching_triplets(directions, reference, tolerance):
    matches = []
    count = len(directions)

    # Try every possible group of three detections.
    for i in range(count):
        for j in range(i + 1, count):
            for k in range(j + 1, count):
                candidate = directions[[i, j, k]]
                candidate_fingerprint = fingerprint(candidate)

                errors = np.abs(
                    candidate_fingerprint - reference
                )

                if np.all(errors <= tolerance):
                    matches.append((i, j, k))

    return matches


# Three genuine stars.
real_pixels = np.array([
    [640, 360],
    [720, 340],
    [500, 400]
], dtype=float)

real_directions = np.array([
    pixel_to_direction(p) for p in real_pixels
])

reference = fingerprint(real_directions)

# Add one deliberately false detection.
false_pixel = np.array([1100, 100], dtype=float)
all_pixels = np.vstack([real_pixels, false_pixel])

all_directions = np.array([
    pixel_to_direction(p) for p in all_pixels
])

print("========================================")
print("StarLoc 2.0 - Lesson 26")
print("False-Star Rejection")
print("========================================")

print("\nReference angular fingerprint:")
print(np.round(reference, 4), "degrees")

print("\nTest A: Genuine detections only")
print("Detected points:", len(real_directions))
print("Angular pairs:", len(reference))

matches_a = find_matching_triplets(
    real_directions, reference, TOLERANCE
)

print("Matching triplets:", matches_a)

print("\nTest B: One false detection added")
print("Detected points:", len(all_directions))
print("Possible three-star groups:", 4)

matches_b = find_matching_triplets(
    all_directions, reference, TOLERANCE
)

print("Matching triplets:", matches_b)
print("Tolerance:", TOLERANCE, "degrees")

if (0, 1, 2) in matches_b:
    print("\nOriginal genuine pattern successfully recovered.")
else:
    print("\nOriginal pattern was not recovered.")

print("\nLesson 26 completed successfully.")
