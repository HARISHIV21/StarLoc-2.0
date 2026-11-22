
import numpy as np

# StarLoc 2.0 - Lesson 24
# Demonstrate tolerant angular-pattern matching.

reference_angles = np.array([
    10.00,
    15.00,
    22.00
])

measured_angles = np.array([
    10.12,
    14.91,
    22.08
])

tolerance = 0.20  # degrees


def compare_patterns(reference, measured, tolerance):
    if len(reference) != len(measured):
        return False, np.array([])

    differences = np.abs(reference - measured)
    matches = differences <= tolerance

    return bool(np.all(matches)), differences


matched, differences = compare_patterns(
    reference_angles,
    measured_angles,
    tolerance
)

print("====================================")
print("StarLoc 2.0 - Lesson 24")
print("Tolerance-Based Pattern Matching")
print("====================================")

print(f"\nAllowed tolerance: {tolerance:.2f} degrees")

print("\nComparison:")
for i, (ref, meas, diff) in enumerate(
    zip(reference_angles, measured_angles, differences),
    start=1
):
    status = "MATCH" if diff <= tolerance else "MISMATCH"

    print(
        f"Pair {i}: reference={ref:.2f}°, "
        f"measured={meas:.2f}°, "
        f"error={diff:.2f}° -> {status}"
    )

print("\nFINAL RESULT:")
if matched:
    print("The two patterns match within the tolerance.")
else:
    print("The two patterns do NOT match.")

# Test a pattern with one deliberately incorrect angle.
bad_measurements = np.array([
    10.12,
    14.91,
    22.50
])

bad_match, bad_differences = compare_patterns(
    reference_angles,
    bad_measurements,
    tolerance
)

print("\nSECOND TEST: One incorrect angle")
print(f"Reference: {reference_angles}")
print(f"Measured:  {bad_measurements}")
print(f"Errors:    {np.round(bad_differences, 3)} degrees")
print("Result:", "MATCH" if bad_match else "MISMATCH")
print("\nLesson 24 completed successfully.")
