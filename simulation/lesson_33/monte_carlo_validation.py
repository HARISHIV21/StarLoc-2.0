
import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

# StarLoc 2.0 - Lesson 33
# Monte Carlo validation of 3D attitude estimation.

RNG = np.random.default_rng(33)
TRIALS = 500
ACCURACY_LIMIT_DEG = 0.1


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


# Eight reference star directions.
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

true_directions = np.array([
    R_true @ vector for vector in reference
])

# Standard deviation of Cartesian direction noise.
noise_levels = [0.0005, 0.001, 0.002, 0.005]

summary = []

print("========================================")
print("StarLoc 2.0 - Lesson 33")
print("Monte Carlo Validation")
print("========================================")
print("Trials per noise level:", TRIALS)
print("Success threshold:", ACCURACY_LIMIT_DEG, "degrees")

for sigma in noise_levels:
    errors = []

    for _ in range(TRIALS):
        noisy_directions = (
            true_directions
            + RNG.normal(
                0.0,
                sigma,
                size=true_directions.shape
            )
        )

        noisy_directions = np.array([
            normalize(vector)
            for vector in noisy_directions
        ])

        R_estimated = estimate_rotation(
            reference,
            noisy_directions
        )

        error = attitude_error_degrees(
            R_true,
            R_estimated
        )

        errors.append(error)

    errors = np.array(errors)

    mean_error = np.mean(errors)
    rmse = np.sqrt(np.mean(errors ** 2))
    percentile_95 = np.percentile(errors, 95)
    success_rate = np.mean(
        errors < ACCURACY_LIMIT_DEG
    ) * 100.0

    summary.append([
        sigma,
        mean_error,
        rmse,
        percentile_95,
        success_rate
    ])

    print(f"\nNoise sigma: {sigma:.4f}")
    print(f"Mean error: {mean_error:.6f} degrees")
    print(f"RMSE: {rmse:.6f} degrees")
    print(f"95th percentile: {percentile_95:.6f} degrees")
    print(f"Success rate: {success_rate:.2f}%")

summary = np.array(summary)

# Plot attitude RMSE versus noise.
plt.figure(figsize=(8, 5))
plt.plot(
    summary[:, 0],
    summary[:, 2],
    marker="o"
)
plt.xlabel("Direction noise standard deviation")
plt.ylabel("Attitude RMSE (degrees)")
plt.title("StarLoc 2.0 - Monte Carlo Validation")
plt.grid(True, alpha=0.3)
plt.tight_layout()

plot_path = "results/lesson_33_monte_carlo.png"
plt.savefig(plot_path, dpi=150, bbox_inches="tight")
plt.close()

np.save(
    "results/lesson_33_monte_carlo_summary.npy",
    summary
)

print("\nSaved graph:", plot_path)
print("Saved data: results/lesson_33_monte_carlo_summary.npy")
print("\nLesson 33 completed successfully.")
