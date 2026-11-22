import numpy as np

# Use a non-GUI backend.
# This lets us save images without opening a Matplotlib window.
import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt


# ============================================================
# StarLoc 2.0 - Lesson 10
# Synthetic Star Sensor Image
# ============================================================


# ------------------------------------------------------------
# 1. Camera parameters
# ------------------------------------------------------------

image_width = 1280
image_height = 720

f = 500.0

# Principal point
cx = image_width / 2
cy = image_height / 2


# ------------------------------------------------------------
# 2. Artificial star directions
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
# 3. Normalize star directions
# ------------------------------------------------------------

stars = stars / np.linalg.norm(
    stars,
    axis=1,
    keepdims=True
)


# ------------------------------------------------------------
# 4. Project stars onto the camera
# ------------------------------------------------------------

u = f * stars[:, 0] / stars[:, 2] + cx
v = f * stars[:, 1] / stars[:, 2] + cy


# ------------------------------------------------------------
# 5. Create a dark camera sensor
# ------------------------------------------------------------

image = np.zeros(
    (image_height, image_width),
    dtype=np.float32
)


# ------------------------------------------------------------
# 6. Star brightness
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
# 7. Put a small bright spot at each star position
# ------------------------------------------------------------

for i in range(len(stars)):

    x = int(round(u[i]))
    y = int(round(v[i]))

    # Check that the star is inside the image
    if 0 <= x < image_width and 0 <= y < image_height:

        image[y, x] = brightness[i]


# ------------------------------------------------------------
# 8. Display/save the synthetic image
# ------------------------------------------------------------

plt.figure(figsize=(12, 7))

plt.imshow(
    image,
    cmap="gray",
    vmin=0,
    vmax=1
)

plt.title(
    "StarLoc 2.0 - First Synthetic Star Sensor Image"
)

plt.xlabel("Pixel U")
plt.ylabel("Pixel V")

plt.tight_layout()


# ------------------------------------------------------------
# 9. Save result
# ------------------------------------------------------------

output_file = "results/lesson_10_synthetic_star_image.png"

plt.savefig(
    output_file,
    dpi=150,
    bbox_inches="tight"
)

plt.close()


print("==========================================")
print("StarLoc Lesson 10")
print("Synthetic star image generated")
print("==========================================")
print(f"Image size: {image_width} x {image_height}")
print(f"Number of stars: {len(stars)}")
print(f"Saved to: {output_file}")