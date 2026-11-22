import numpy as np
import matplotlib.pyplot as plt


# --------------------------------------------------
# 1. Artificial star directions
# --------------------------------------------------

stars = np.array([
    [0.0,  0.0,  1.0],
    [0.2,  0.1,  0.97],
    [-0.3, 0.1,  0.95],
    [0.1, -0.2, 0.97],
    [-0.2, -0.2, 0.95],
    [0.4, -0.1, 0.91]
])


# --------------------------------------------------
# 2. Normalize directions
# --------------------------------------------------

stars = stars / np.linalg.norm(
    stars,
    axis=1,
    keepdims=True
)


# --------------------------------------------------
# 3. Camera parameters
# --------------------------------------------------

image_width = 1280
image_height = 720

f = 500

cx = image_width / 2
cy = image_height / 2


# --------------------------------------------------
# 4. Project 3D directions onto image
# --------------------------------------------------

u = f * stars[:, 0] / stars[:, 2] + cx
v = f * stars[:, 1] / stars[:, 2] + cy


# --------------------------------------------------
# 5. Display camera image
# --------------------------------------------------

plt.figure(figsize=(10, 6))

plt.scatter(u, v, s=80)

plt.xlabel("Pixel U")
plt.ylabel("Pixel V")

plt.title("StarLoc 2.0 - 1280 × 720 Virtual Camera")

plt.xlim(0, image_width)
plt.ylim(image_height, 0)

plt.grid(True)

plt.savefig(
    "results/lesson_09_camera_image.png",
    dpi=150,
    bbox_inches="tight"
)

plt.show()