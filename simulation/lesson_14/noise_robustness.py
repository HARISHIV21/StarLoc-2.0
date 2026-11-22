import numpy as np

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt


# ============================================================
# StarLoc 2.0 - Lesson 14
# Noise Robustness Experiment
# ============================================================


# ------------------------------------------------------------
# 1. Camera parameters
# ------------------------------------------------------------

image_width = 1280
image_height = 720

f = 500.0

cx = image_width / 2
cy = image_height / 2


# ------------------------------------------------------------
# 2. Virtual star directions
# ------------------------------------------------------------

stars = np.array([
    [0.0,  0.0,  1.0],
    [0.2,  0.1,  0.97],
    [-0.3, 0.1,  0.95],
    [0.1, -0.2, 0.97],
    [-0.2, -0.2, 0.95],
    [0.4, -0.1, 0.91]
], dtype=float)


# Normalize star vectors

stars = stars / np.linalg.norm(
    stars,
    axis=1,
    keepdims=True
)


# ------------------------------------------------------------
# 3. True star pixel positions
# ------------------------------------------------------------

true_u = (
    f * stars[:, 0] / stars[:, 2]
    + cx
)

true_v = (
    f * stars[:, 1] / stars[:, 2]
    + cy
)


# ------------------------------------------------------------
# 4. Star brightness
# ------------------------------------------------------------

brightness = np.array([
    1.00,
    0.80,
    0.60,
    0.90,
    0.50,
    0.70
])


# ------------------------------------------------------------
# 5. Star spot parameters
# ------------------------------------------------------------

sigma = 1.5
radius = 5


# ------------------------------------------------------------
# 6. Noise levels to test
# ------------------------------------------------------------

noise_levels = [
    0.0,
    0.005,
    0.01,
    0.02,
    0.05
]


# ------------------------------------------------------------
# 7. Detection threshold
# ------------------------------------------------------------

threshold = 0.08


# ------------------------------------------------------------
# 8. Star image generator
# ------------------------------------------------------------

def generate_image(noise_sigma, seed):

    image = np.zeros(
        (image_height, image_width),
        dtype=float
    )

    # --------------------------------------------------------
    # Create Gaussian star spots
    # --------------------------------------------------------

    for i in range(len(stars)):

        center_u = true_u[i]
        center_v = true_v[i]

        min_x = max(
            0,
            int(np.floor(center_u - radius))
        )

        max_x = min(
            image_width - 1,
            int(np.ceil(center_u + radius))
        )

        min_y = max(
            0,
            int(np.floor(center_v - radius))
        )

        max_y = min(
            image_height - 1,
            int(np.ceil(center_v + radius))
        )

        for y in range(min_y, max_y + 1):

            for x in range(min_x, max_x + 1):

                distance_squared = (
                    (x - center_u) ** 2
                    +
                    (y - center_v) ** 2
                )

                value = brightness[i] * np.exp(
                    -distance_squared
                    /
                    (2 * sigma ** 2)
                )

                image[y, x] += value

    # --------------------------------------------------------
    # Add Gaussian noise
    # --------------------------------------------------------

    rng = np.random.default_rng(seed)

    noise = rng.normal(
        0,
        noise_sigma,
        image.shape
    )

    image = image + noise

    # Keep image between 0 and 1

    image = np.clip(
        image,
        0,
        1
    )

    return image


# ------------------------------------------------------------
# 9. Simple connected-component detector
# ------------------------------------------------------------

def detect_stars(image):

    binary = image > threshold

    height, width = image.shape

    visited = np.zeros_like(
        binary,
        dtype=bool
    )

    detections = []

    for y in range(height):

        for x in range(width):

            if not binary[y, x]:
                continue

            if visited[y, x]:
                continue

            stack = [(y, x)]

            visited[y, x] = True

            pixels = []

            while stack:

                current_y, current_x = stack.pop()

                pixels.append(
                    (current_y, current_x)
                )

                neighbours = [
                    (current_y - 1, current_x),
                    (current_y + 1, current_x),
                    (current_y, current_x - 1),
                    (current_y, current_x + 1)
                ]

                for neighbour_y, neighbour_x in neighbours:

                    if not (
                        0 <= neighbour_y < height
                        and
                        0 <= neighbour_x < width
                    ):
                        continue

                    if not binary[
                        neighbour_y,
                        neighbour_x
                    ]:
                        continue

                    if visited[
                        neighbour_y,
                        neighbour_x
                    ]:
                        continue

                    visited[
                        neighbour_y,
                        neighbour_x
                    ] = True

                    stack.append(
                        (neighbour_y, neighbour_x)
                    )

            # Ignore isolated single pixels

            if len(pixels) >= 2:

                detections.append(
                    pixels
                )

    # --------------------------------------------------------
    # Calculate centroids
    # --------------------------------------------------------

    centroids = []

    for region in detections:

        ys = np.array([
            pixel[0]
            for pixel in region
        ])

        xs = np.array([
            pixel[1]
            for pixel in region
        ])

        centroid_u = np.mean(xs)
        centroid_v = np.mean(ys)

        centroids.append([
            centroid_u,
            centroid_v
        ])

    return np.array(
        centroids,
        dtype=float
    )


# ------------------------------------------------------------
# 10. Run experiment
# ------------------------------------------------------------

results = []


print("==========================================")
print("StarLoc 2.0 - Lesson 14")
print("Noise Robustness Experiment")
print("==========================================")
print()

for index, noise_sigma in enumerate(noise_levels):

    print(
        f"Testing noise sigma = {noise_sigma}"
    )

    image = generate_image(
        noise_sigma,
        seed=42 + index
    )

    detected_centroids = detect_stars(
        image
    )

    detection_count = len(
        detected_centroids
    )

    # --------------------------------------------------------
    # Match detected stars to true stars
    # --------------------------------------------------------

    errors = []

    if detection_count > 0:

        for i in range(len(true_u)):

            distances = np.sqrt(
                (
                    detected_centroids[:, 0]
                    -
                    true_u[i]
                ) ** 2
                +
                (
                    detected_centroids[:, 1]
                    -
                    true_v[i]
                ) ** 2
            )

            nearest_index = np.argmin(
                distances
            )

            errors.append(
                distances[nearest_index]
            )

    # --------------------------------------------------------
    # Calculate metrics
    # --------------------------------------------------------

    if len(errors) > 0:

        errors = np.array(errors)

        centroid_rmse = np.sqrt(
            np.mean(errors ** 2)
        )

        mean_error = np.mean(errors)

    else:

        centroid_rmse = np.nan
        mean_error = np.nan

    missed_stars = max(
        0,
        len(stars) - detection_count
    )

    false_detections = max(
        0,
        detection_count - len(stars)
    )

    results.append([
        noise_sigma,
        detection_count,
        missed_stars,
        false_detections,
        mean_error,
        centroid_rmse
    ])

    print(
        f"Detected stars   : {detection_count}"
    )

    print(
        f"Missed stars     : {missed_stars}"
    )

    print(
        f"False detections : {false_detections}"
    )

    print(
        f"Centroid RMSE    : {centroid_rmse:.4f} pixels"
    )

    print()


# ------------------------------------------------------------
# 11. Convert results to NumPy array
# ------------------------------------------------------------

results = np.array(
    results,
    dtype=float
)


# ------------------------------------------------------------
# 12. Print final table
# ------------------------------------------------------------

print("------------------------------------------")
print("FINAL RESULTS")
print("------------------------------------------")

print(
    "Noise     Detected   Missed   False   RMSE"
)

for row in results:

    print(
        f"{row[0]:.3f}"
        f"       {int(row[1]):3d}"
        f"        {int(row[2]):3d}"
        f"      {int(row[3]):3d}"
        f"      {row[5]:.4f}"
    )


# ------------------------------------------------------------
# 13. Save numerical results
# ------------------------------------------------------------

np.save(
    "results/lesson_14_noise_results.npy",
    results
)


# ------------------------------------------------------------
# 14. Plot centroid RMSE
# ------------------------------------------------------------

plt.figure(figsize=(9, 6))

plt.plot(
    results[:, 0],
    results[:, 5],
    marker="o"
)

plt.xlabel(
    "Noise Sigma"
)

plt.ylabel(
    "Centroid RMSE (pixels)"
)

plt.title(
    "StarLoc 2.0 - Noise vs Centroid Error"
)

plt.grid(True)

plt.tight_layout()

plt.savefig(
    "results/lesson_14_noise_vs_rmse.png",
    dpi=150,
    bbox_inches="tight"
)

plt.close()


# ------------------------------------------------------------
# 15. Plot detection count
# ------------------------------------------------------------

plt.figure(figsize=(9, 6))

plt.plot(
    results[:, 0],
    results[:, 1],
    marker="o"
)

plt.xlabel(
    "Noise Sigma"
)

plt.ylabel(
    "Detected Star Count"
)

plt.title(
    "StarLoc 2.0 - Noise vs Detection Count"
)

plt.grid(True)

plt.tight_layout()

plt.savefig(
    "results/lesson_14_noise_vs_detection.png",
    dpi=150,
    bbox_inches="tight"
)

plt.close()


print()
print("Results saved:")
print(
    "results/lesson_14_noise_results.npy"
)
print(
    "results/lesson_14_noise_vs_rmse.png"
)
print(
    "results/lesson_14_noise_vs_detection.png"
)

print()
print("Noise robustness experiment completed.")