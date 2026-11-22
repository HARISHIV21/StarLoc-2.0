import numpy as np

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt


# ============================================================
# StarLoc 2.0 - Lesson 13
# Centroid Accuracy Evaluation
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
# 2. Star directions
# ------------------------------------------------------------

stars = np.array([
    [0.0,  0.0,  1.0],
    [0.2,  0.1,  0.97],
    [-0.3, 0.1,  0.95],
    [0.1, -0.2, 0.97],
    [-0.2, -0.2, 0.95],
    [0.4, -0.1, 0.91]
], dtype=float)


# ------------------------------------------------------------
# 3. Normalize directions
# ------------------------------------------------------------

stars = stars / np.linalg.norm(
    stars,
    axis=1,
    keepdims=True
)


# ------------------------------------------------------------
# 4. Calculate TRUE pixel positions
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
# 5. Load detected positions from Lesson 12
# ------------------------------------------------------------

input_file = "results/lesson_11_sensor.npy"

image = np.load(input_file)


# ------------------------------------------------------------
# 6. Detect bright regions
# ------------------------------------------------------------

threshold = 0.08

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
                    and 0 <= neighbour_x < width
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

            detections.append(pixels)


# ------------------------------------------------------------
# 7. Calculate detected centroids
# ------------------------------------------------------------

detected_centroids = []


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


    detected_centroids.append(
        [centroid_u, centroid_v]
    )


detected_centroids = np.array(
    detected_centroids
)


# ------------------------------------------------------------
# 8. Match detections to true stars
# ------------------------------------------------------------

errors = []


for i in range(len(true_u)):

    distances = np.sqrt(
        (detected_centroids[:, 0] - true_u[i]) ** 2
        +
        (detected_centroids[:, 1] - true_v[i]) ** 2
    )

    nearest_index = np.argmin(distances)

    error = distances[nearest_index]

    errors.append(error)


errors = np.array(errors)


# ------------------------------------------------------------
# 9. Calculate statistics
# ------------------------------------------------------------

mean_error = np.mean(errors)

rmse = np.sqrt(
    np.mean(errors ** 2)
)

maximum_error = np.max(errors)


# ------------------------------------------------------------
# 10. Print results
# ------------------------------------------------------------

print("==========================================")
print("StarLoc 2.0 - Lesson 13")
print("Centroid Accuracy")
print("==========================================")

print()

for i in range(len(true_u)):

    print(
        f"Star {i + 1}: "
        f"True = "
        f"({true_u[i]:.3f}, {true_v[i]:.3f})   "
        f"Error = {errors[i]:.4f} pixels"
    )


print()
print("------------------------------------------")
print(f"Mean centroid error : {mean_error:.4f} pixels")
print(f"Centroid RMSE       : {rmse:.4f} pixels")
print(f"Maximum error       : {maximum_error:.4f} pixels")
print("------------------------------------------")


# ------------------------------------------------------------
# 11. Create visualization
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
    s=150,
    label="True star position"
)


# Detected positions
if len(detected_centroids) > 0:

    plt.scatter(
        detected_centroids[:, 0],
        detected_centroids[:, 1],
        facecolors="none",
        edgecolors="red",
        s=120,
        label="Detected centroid"
    )


plt.title(
    "StarLoc 2.0 - Centroid Accuracy"
)

plt.xlabel("Pixel U")
plt.ylabel("Pixel V")

plt.legend()

plt.tight_layout()


# ------------------------------------------------------------
# 12. Save result
# ------------------------------------------------------------

output_file = (
    "results/lesson_13_centroid_accuracy.png"
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
print("Centroid accuracy evaluation completed.")