import numpy as np

# Use a non-GUI backend.
import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt


# ============================================================
# StarLoc 2.0 - Lesson 11
# Realistic Synthetic Star Sensor
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
# 7. Gaussian star model
# ------------------------------------------------------------

sigma = 1.5

patch_radius = 5


for i in range(len(stars)):

    center_x = u[i]
    center_y = v[i]

    x_min = max(0, int(np.floor(center_x)) - patch_radius)
    x_max = min(
        image_width - 1,
        int(np.floor(center_x)) + patch_radius
    )

    y_min = max(0, int(np.floor(center_y)) - patch_radius)
    y_max = min(
        image_height - 1,
        int(np.floor(center_y)) + patch_radius
    )

    for y in range(y_min, y_max + 1):

        for x in range(x_min, x_max + 1):

            distance_squared = (
                (x - center_x) ** 2
                + (y - center_y) ** 2
            )

            gaussian = np.exp(
                -distance_squared / (2 * sigma ** 2)
            )

            image[y, x] += brightness[i] * gaussian


# ------------------------------------------------------------
# 8. Add sensor noise
# ------------------------------------------------------------

rng = np.random.default_rng(42)

noise_sigma = 0.01

noise = rng.normal(
    loc=0.0,
    scale=noise_sigma,
    size=image.shape
)

image = image + noise


# ------------------------------------------------------------
# 9. Keep pixel values inside valid range
# ------------------------------------------------------------

image = np.clip(
    image,
    0.0,
    1.0
)
# Save the raw sensor data for later processing
np.save(
    "results/lesson_11_sensor.npy",
    image
)

# ------------------------------------------------------------
# 10. Save the synthetic image
# ------------------------------------------------------------

output_file = "results/lesson_11_realistic_star_sensor.png"

plt.figure(figsize=(12, 7))

plt.imshow(
    image,
    cmap="gray",
    vmin=0,
    vmax=1
)

plt.title(
    "StarLoc 2.0 - Realistic Synthetic Star Sensor"
)

plt.xlabel("Pixel U")
plt.ylabel("Pixel V")

plt.tight_layout()

plt.savefig(
    output_file,
    dpi=150,
    bbox_inches="tight"
)

plt.close()


# ------------------------------------------------------------
# 11. Print experiment information
# ------------------------------------------------------------

print("==========================================")
print("StarLoc 2.0 - Lesson 11")
print("==========================================")

print(f"Image size: {image_width} x {image_height}")
print(f"Number of stars: {len(stars)}")
print(f"Gaussian sigma: {sigma} pixels")
print(f"Noise sigma: {noise_sigma}")

print()
print(f"Saved to: {output_file}")
print()
print("Simulation completed successfully.")