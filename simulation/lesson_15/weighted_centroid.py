import numpy as np

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt


# ============================================================
# StarLoc 2.0 - Lesson 15
# Intensity-Weighted Centroid
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
# 2. Virtual stars
# ------------------------------------------------------------

stars = np.array([
    [0.0,  0.0,  1.0],
    [0.2,  0.1,  0.97],
    [-0.3, 0.1,  0.95],
    [0.1, -0.2, 0.97],
    [-0.2, -0.2, 0.95],
    [0.4, -0.1, 0.91]
], dtype=float)


# Normalize

stars = stars / np.linalg.norm(
    stars,
    axis=1,
    keepdims=True
)


# ------------------------------------------------------------
# 3. True star positions
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
# 6. Generate synthetic image
# ------------------------------------------------------------

image = np.zeros(
    (image_height, image_width),
    dtype=float
)


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


# ------------------------------------------------------------
# 7. Add realistic noise
# ------------------------------------------------------------

rng = np.random.default_rng(42)

noise_sigma = 0.01

noise = rng.normal(
    0,
    noise_sigma,
    image.shape
)

image = image + noise

image = np.clip(
    image,
    0,
    1
)


# ------------------------------------------------------------
# 8. Detect bright pixels
# ------------------------------------------------------------

threshold = 0.08

binary = image > threshold


# ------------------------------------------------------------
# 9. Connected-component detection
# ------------------------------------------------------------

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

        if len(pixels) >= 2:

            detections.append(
                pixels
            )


# ------------------------------------------------------------
# 10. Calculate two types of centroid
# ------------------------------------------------------------

simple_centroids = []

weighted_centroids = []


for region in detections:

    ys = np.array([
        pixel[0]
        for pixel in region
    ])

    xs = np.array([
        pixel[1]
        for pixel in region
    ])


    # --------------------------------------------------------
    # Simple centroid
    # --------------------------------------------------------

    simple_u = np.mean(xs)
    simple_v = np.mean(ys)

    simple_centroids.append([
        simple_u,
        simple_v
    ])


    # --------------------------------------------------------
    # Intensity-weighted centroid
    # --------------------------------------------------------

    intensities = image[
        ys,
        xs
    ]

    total_intensity = np.sum(
        intensities
    )

    weighted_u = np.sum(
        xs * intensities
    ) / total_intensity

    weighted_v = np.sum(
        ys * intensities
    ) / total_intensity

    weighted_centroids.append([
        weighted_u,
        weighted_v
    ])


simple_centroids = np.array(
    simple_centroids
)

weighted_centroids = np.array(
    weighted_centroids
)


# ------------------------------------------------------------
# 11. Match detected stars to true stars
# ------------------------------------------------------------

simple_errors = []
weighted_errors = []


for i in range(len(stars)):

    true_position = np.array([
        true_u[i],
        true_v[i]
    ])


    # Simple centroid

    distances_simple = np.linalg.norm(
        simple_centroids
        -
        true_position,
        axis=1
    )

    nearest_simple = np.argmin(
        distances_simple
    )

    simple_error = distances_simple[
        nearest_simple
    ]


    # Weighted centroid

    distances_weighted = np.linalg.norm(
        weighted_centroids
        -
        true_position,
        axis=1
    )

    nearest_weighted = np.argmin(
        distances_weighted
    )

    weighted_error = distances_weighted[
        nearest_weighted
    ]


    simple_errors.append(
        simple_error
    )

    weighted_errors.append(
        weighted_error
    )


simple_errors = np.array(
    simple_errors
)

weighted_errors = np.array(
    weighted_errors
)


# ------------------------------------------------------------
# 12. Calculate RMSE
# ------------------------------------------------------------

simple_rmse = np.sqrt(
    np.mean(
        simple_errors ** 2
    )
)

weighted_rmse = np.sqrt(
    np.mean(
        weighted_errors ** 2
    )
)


# ------------------------------------------------------------
# 13. Print results
# ------------------------------------------------------------

print("==========================================")
print("StarLoc 2.0 - Lesson 15")
print("Intensity-Weighted Centroid")
print("==========================================")

print()

for i in range(len(stars)):

    print(
        f"Star {i + 1}"
    )

    print(
        f"  True position     : "
        f"({true_u[i]:.3f}, {true_v[i]:.3f})"
    )

    print(
        f"  Simple error      : "
        f"{simple_errors[i]:.4f} pixels"
    )

    print(
        f"  Weighted error    : "
        f"{weighted_errors[i]:.4f} pixels"
    )

    print()


print("------------------------------------------")

print(
    f"Simple centroid RMSE   : "
    f"{simple_rmse:.4f} pixels"
)

print(
    f"Weighted centroid RMSE : "
    f"{weighted_rmse:.4f} pixels"
)

print("------------------------------------------")


# ------------------------------------------------------------
# 14. Plot comparison
# ------------------------------------------------------------

plt.figure(figsize=(12, 7))

plt.imshow(
    image,
    cmap="gray",
    vmin=0,
    vmax=1
)


# True positions

plt.scatter(
    true_u,
    true_v,
    marker="+",
    s=180,
    label="True position"
)


# Simple centroid

plt.scatter(
    simple_centroids[:, 0],
    simple_centroids[:, 1],
    facecolors="none",
    edgecolors="red",
    s=120,
    label="Simple centroid"
)


# Weighted centroid

plt.scatter(
    weighted_centroids[:, 0],
    weighted_centroids[:, 1],
    marker="x",
    s=100,
    label="Weighted centroid"
)


plt.title(
    "StarLoc 2.0 - Centroid Comparison"
)

plt.xlabel(
    "Pixel U"
)

plt.ylabel(
    "Pixel V"
)

plt.legend()

plt.tight_layout()


output_file = (
    "results/"
    "lesson_15_centroid_comparison.png"
)


plt.savefig(
    output_file,
    dpi=150,
    bbox_inches="tight"
)

plt.close()


print()

print(
    f"Result saved to: {output_file}"
)

print()

print(
    "Weighted centroid experiment completed."
)