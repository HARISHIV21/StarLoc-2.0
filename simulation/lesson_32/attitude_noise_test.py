
import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

# StarLoc 2.0 - Lesson 32
# Measure how direction noise affects 3D attitude estimation.

RNG = np.random.default_rng(42)


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


# Simulated reference directions for eight stars.
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

# Noise is the standard deviation of each Cartesian
# direction component before the vectors are normalized.
noise_levels = [0.0, 0.0005, 0.001, 0.002, 0.005]
trials = 100

mean_errors = []
rmse_errors = []
max_errors = []

print("========================================")
print("StarLoc 2.0 - Lesson 32")
print("Attitude Estimation Under Noise")
print("========================================")
print(f"\nTrials per noise level: {trials}")

for sigma in noise_levels:
    errors = []

    for _ in range(trials):
        noisy = true_directions + RNG.normal(
            loc=0.0,
            scale=sigma,
            size=true_directions.shape
        )

        noisy = np.array([
            normalize(vector) for vector in noisy
        ])

        R_estimated = estimate_rotation(reference, noisy)

        error = attitude_error_degrees(
            R_true, R_estimated
        )

        errors.append(error)

    errors = np.array(errors)

    mean_error = np.mean(errors)
    rmse_error = np.sqrt(np.mean(errors ** 2))
    max_error = np.max(errors)

    mean_errors.append(mean_error)
    rmse_errors.append(rmse_error)
    max_errors.append(max_error)

    print(f"\nNoise sigma: {sigma:.4f}")
    print(f"Mean error:  {mean_error:.6f} degrees")
    print(f"RMSE:        {rmse_error:.6f} degrees")
    print(f"Maximum:     {max_error:.6f} degrees")

# Save the RMSE plot.
plt.figure(figsize=(8, 5))
plt.plot(noise_levels, rmse_errors, marker="o")
plt.xlabel("Direction noise standard deviation")
plt.ylabel("Attitude error RMSE (degrees)")
plt.title("StarLoc 2.0 - Attitude Error vs Measurement Noise")
plt.grid(True, alpha=0.3)
plt.tight_layout()

output_file = "results/lesson_32_attitude_noise.png"
plt.savefig(output_file, dpi=150, bbox_inches="tight")
plt.close()

np.savez(
    "results/lesson_32_attitude_noise_data.npz",
    noise_levels=np.array(noise_levels),
    mean_errors=np.array(mean_errors),
    rmse_errors=np.array(rmse_errors),
    max_errors=np.array(max_errors)
)

print("\nSaved graph:", output_file)
print("Saved numerical results:")
print("results/lesson_32_attitude_noise_data.npz")
print("\nLesson 32 completed successfully.")
