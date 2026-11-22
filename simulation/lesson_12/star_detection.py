import numpy as np

# Use a non-GUI backend so the program runs cleanly
# inside the VS Code terminal.
import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt


# ============================================================
# StarLoc 2.0 - Lesson 12
# First Star Detection Algorithm
# ============================================================


# ------------------------------------------------------------
# 1. Load the synthetic camera image
# ------------------------------------------------------------

input_file = "results/lesson_11_sensor.npy"

image = np.load(input_file)


# ------------------------------------------------------------
# 2. Detection threshold
# ------------------------------------------------------------

threshold = 0.08


# ------------------------------------------------------------
# 3. Create a binary image
# ------------------------------------------------------------

# False = background
# True  = potentially a star

binary = image > threshold


print("==========================================")
print("StarLoc 2.0 - Lesson 12")
print("First Star Detection")
print("==========================================")

print(f"Image size: {image.shape[1]} x {image.shape[0]}")
print(f"Detection threshold: {threshold}")
print(f"Bright pixels: {np.sum(binary)}")


# ------------------------------------------------------------
# 4. Find connected bright regions
# ------------------------------------------------------------

height, width = image.shape

visited = np.zeros_like(binary, dtype=bool)

detections = []


for y in range(height):

    for x in range(width):

        # Ignore dark pixels
        if not binary[y, x]:
            continue

        # Ignore pixels already processed
        if visited[y, x]:
            continue


        # Start a new bright region
        stack = [(y, x)]

        visited[y, x] = True

        pixels = []


        # ----------------------------------------------------
        # Explore the connected region
        # ----------------------------------------------------

        while stack:

            current_y, current_x = stack.pop()

            pixels.append(
                (current_y, current_x)
            )


            # Four-connected neighbours
            neighbours = [
                (current_y - 1, current_x),
                (current_y + 1, current_x),
                (current_y, current_x - 1),
                (current_y, current_x + 1)
            ]


            for neighbour_y, neighbour_x in neighbours:

                # Make sure the neighbour is inside the image
                if not (
                    0 <= neighbour_y < height
                    and 0 <= neighbour_x < width
                ):
                    continue


                # Check whether it is a bright pixel
                if not binary[neighbour_y, neighbour_x]:
                    continue


                # Check whether we already visited it
                if visited[neighbour_y, neighbour_x]:
                    continue


                visited[
                    neighbour_y,
                    neighbour_x
                ] = True


                stack.append(
                    (neighbour_y, neighbour_x)
                )


        # ----------------------------------------------------
        # Keep regions that contain at least 2 pixels
        # ----------------------------------------------------

        if len(pixels) >= 2:

            detections.append(pixels)


# ------------------------------------------------------------
# 5. Calculate the centroid of each detected region
# ------------------------------------------------------------

centroids = []


for region in detections:

    ys = np.array(
        [pixel[0] for pixel in region]
    )

    xs = np.array(
        [pixel[1] for pixel in region]
    )


    centroid_x = np.mean(xs)
    centroid_y = np.mean(ys)


    centroids.append(
        (centroid_x, centroid_y)
    )


# ------------------------------------------------------------
# 6. Print detected stars
# ------------------------------------------------------------

print()
print(f"Detected star regions: {len(detections)}")
print()


for i, region in enumerate(detections):

    x, y = centroids[i]

    print(
        f"Star candidate {i + 1}: "
        f"u = {x:.2f}, "
        f"v = {y:.2f}, "
        f"pixels = {len(region)}"
    )


# ------------------------------------------------------------
# 7. Create detection visualization
# ------------------------------------------------------------

plt.figure(figsize=(12, 7))


plt.imshow(
    image,
    cmap="gray",
    vmin=0,
    vmax=1
)


# Draw detected centroids
if len(centroids) > 0:

    detected_x = [
        point[0]
        for point in centroids
    ]

    detected_y = [
        point[1]
        for point in centroids
    ]


    plt.scatter(
        detected_x,
        detected_y,
        facecolors="none",
        edgecolors="red",
        s=150,
        linewidths=1.5,
        label="Detected stars"
    )


plt.title(
    "StarLoc 2.0 - First Star Detection"
)

plt.xlabel("Pixel U")
plt.ylabel("Pixel V")

plt.legend()

plt.tight_layout()


# ------------------------------------------------------------
# 8. Save detection result
# ------------------------------------------------------------

output_file = (
    "results/lesson_12_star_detection.png"
)


plt.savefig(
    output_file,
    dpi=150,
    bbox_inches="tight"
)

plt.close()


# ------------------------------------------------------------
# 9. Finish
# ------------------------------------------------------------

print()
print(
    f"Detection result saved to: {output_file}"
)

print()
print("Star detection completed successfully.")