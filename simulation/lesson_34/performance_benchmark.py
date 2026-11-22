
import time
import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

# StarLoc 2.0 - Lesson 34
# Benchmark attitude estimation with different star counts.

RNG = np.random.default_rng(34)
TRIALS = 100
NOISE_SIGMA = 0.001


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


def attitude_error_degrees(R_true, R_estimated):
    relative = R_estimated @ R_true.T
    cosine = (np.trace(relative) - 1.0) / 2.0
    cosine = np.clip(cosine, -1.0, 1.0)
    return np.degrees(np.arccos(cosine))


R_true = (
    rotation_z(30.0)
    @ rotation_y(15.0)
    @ rotation_x(-10.0)
)

# Generate 30 diverse reference directions.
reference_pool = np.array([
    normalize([
        RNG.uniform(-0.4, 0.4),
        RNG.uniform(-0.4, 0.4),
        1.0
    ])
    for _ in range(30)
])

observed_pool = np.array([
    R_true @ direction
    for direction in reference_pool
])

star_counts = [3, 5, 8, 12, 20]
results = []

print("========================================")
print("StarLoc 2.0 - Lesson 34")
print("Computational Performance Benchmark")
print("========================================")
print("Trials per star count:", TRIALS)
print("Direction noise sigma:", NOISE_SIGMA)

for star_count in star_counts:
    errors = []
    elapsed_times = []

    for _ in range(TRIALS):
        # Use the same fixed number of stars for each trial.
        indices = RNG.choice(
            len(reference_pool),
            size=star_count,
            replace=False
        )

        reference = reference_pool[indices]
        true_observed = observed_pool[indices]

        noisy_observed = np.array([
            normalize(
                vector + RNG.normal(
                    0.0, NOISE_SIGMA, size=3
                )
            )
            for vector in true_observed
        ])

        start = time.perf_counter()

        R_estimated = estimate_rotation(
            reference, noisy_observed
        )

        elapsed = time.perf_counter() - start

        error = attitude_error_degrees(
            R_true, R_estimated
        )

        errors.append(error)
        elapsed_times.append(elapsed)

    mean_error = np.mean(errors)
    rmse = np.sqrt(np.mean(np.array(errors) ** 2))
    mean_time_ms = np.mean(elapsed_times) * 1000.0

    results.append([
        star_count,
        mean_error,
        rmse,
        mean_time_ms
    ])

    print(f"\nStars used: {star_count}")
    print(f"Mean attitude error: {mean_error:.6f} degrees")
    print(f"Attitude RMSE: {rmse:.6f} degrees")
    print(f"Mean estimator time: {mean_time_ms:.4f} ms")

results = np.array(results)

# Plot 1: attitude RMSE versus star count.
plt.figure(figsize=(8, 5))
plt.plot(results[:, 0], results[:, 2], marker="o")
plt.xlabel("Number of stars used")
plt.ylabel("Attitude RMSE (degrees)")
plt.title("Attitude Accuracy vs Number of Stars")
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(
    "results/lesson_34_accuracy.png",
    dpi=150,
    bbox_inches="tight"
)
plt.close()

# Plot 2: estimator execution time versus star count.
plt.figure(figsize=(8, 5))
plt.plot(results[:, 0], results[:, 3], marker="o")
plt.xlabel("Number of stars used")
plt.ylabel("Mean estimator time (milliseconds)")
plt.title("Estimator Time vs Number of Stars")
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(
    "results/lesson_34_execution_time.png",
    dpi=150,
    bbox_inches="tight"
)
plt.close()

np.save(
    "results/lesson_34_performance_results.npy",
    results
)

print("\nSaved graph: results/lesson_34_accuracy.png")
print("Saved graph: results/lesson_34_execution_time.png")
print("Saved data: results/lesson_34_performance_results.npy")
print("\nLesson 34 completed successfully.")
