
import numpy as np

# StarLoc 2.0 - Lesson 28
# Rank hypothetical star-pattern candidates by angular RMSE.

measured = np.array([
    10.1,
    15.1,
    22.1
])

candidates = {
    "Candidate A": np.array([10.0, 15.0, 22.0]),
    "Candidate B": np.array([10.5, 16.0, 23.0]),
    "Candidate C": np.array([9.8, 15.4, 21.7]),
}


def calculate_rmse(reference, observed):
    if len(reference) != len(observed):
        raise ValueError("Angle arrays must have equal lengths.")

    errors = reference - observed
    return np.sqrt(np.mean(errors ** 2))


print("========================================")
print("StarLoc 2.0 - Lesson 28")
print("Candidate Pattern Ranking")
print("========================================")

results = []

for name, reference in candidates.items():
    rmse = calculate_rmse(reference, measured)
    results.append((name, rmse))

    print(f"\n{name}")
    print("Reference angles:", reference)
    print("Measured angles: ", measured)
    print("RMSE:", f"{rmse:.4f} degrees")

# Lowest RMSE is ranked first.
results.sort(key=lambda item: item[1])

print("\n========================================")
print("CANDIDATE RANKING")
print("========================================")

for rank, (name, rmse) in enumerate(results, start=1):
    print(f"{rank}. {name}: {rmse:.4f} degrees")

print("\nBest-fitting candidate:", results[0][0])
print("Lesson 28 completed successfully.")
