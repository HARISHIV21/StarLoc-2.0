
import numpy as np

# StarLoc 2.0 - Lesson 25
# Three-star angular fingerprint matching

tolerance = 0.20  # degrees


def pixel_to_direction(pixel, fx=500.0, fy=500.0,
                       cx=640.0, cy=360.0):
    u, v = pixel

    x = (u - cx) / fx
    y = (v - cy) / fy

    direction = np.array([x, y, 1.0])
    return direction / np.linalg.norm(direction)


def calculate_fingerprint(directions):
    angles = []

    for i in range(len(directions)):
        for j in range(i + 1, len(directions)):
            dot = np.dot(directions[i], directions[j])
            dot = np.clip(dot, -1.0, 1.0)

            angle = np.degrees(np.arccos(dot))
            angles.append(angle)

    return np.sort(np.array(angles))


def compare_fingerprints(reference, measured, tolerance):
    if len(reference) != len(measured):
        return False, np.array([])

    errors = np.abs(reference - measured)
    matched = np.all(errors <= tolerance)

    return bool(matched), errors


# Three reference stars represented by image coordinates.
reference_pixels = np.array([
    [640, 360],
    [720, 340],
    [500, 400]
], dtype=float)

# Simulated camera measurements with small pixel errors.
measured_pixels = np.array([
    [641, 360],
    [719, 341],
    [501, 399]
], dtype=float)

# Convert pixel coordinates into unit direction vectors.
reference_directions = np.array([
    pixel_to_direction(pixel)
    for pixel in reference_pixels
])

measured_directions = np.array([
    pixel_to_direction(pixel)
    for pixel in measured_pixels
])

# Build the angular fingerprints.
reference_fingerprint = calculate_fingerprint(
    reference_directions
)

measured_fingerprint = calculate_fingerprint(
    measured_directions
)

# Compare the two patterns.
matched, errors = compare_fingerprints(
    reference_fingerprint,
    measured_fingerprint,
    tolerance
)

print("========================================")
print("StarLoc 2.0 - Lesson 25")
print("Three-Star Pattern Identification")
print("========================================")

print("\nReference fingerprint:")
print(np.round(reference_fingerprint, 4))

print("\nMeasured fingerprint:")
print(np.round(measured_fingerprint, 4))

print("\nAngular differences:")
print(np.round(errors, 4), "degrees")

print(f"\nTolerance: {tolerance:.2f} degrees")
print("Pattern result:", "MATCH" if matched else "MISMATCH")

print("\nNumber of stars:", len(reference_pixels))
print("Number of angular pairs:", len(reference_fingerprint))

print("\nLesson 25 completed successfully.")
