
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# StarLoc 2.0 - Lesson 18
# Visualizing camera rays

image_width = 1280
image_height = 720
fx = 500.0
fy = 500.0

cx = image_width / 2
cy = image_height / 2

pixels = np.array([
    [640, 360],    # Centre
    [720, 340],    # Right and up
    [500, 400],    # Left and down
    [100, 100],    # Near upper-left edge
    [1180, 620]    # Near lower-right edge
], dtype=float)

def pixel_to_direction(u, v):
    x = (u - cx) / fx
    y = (v - cy) / fy

    direction = np.array([x, y, 1.0])
    return direction / np.linalg.norm(direction)

fig = plt.figure(figsize=(9, 7))
ax = fig.add_subplot(111, projection="3d")

for i, (u, v) in enumerate(pixels):
    d = pixel_to_direction(u, v)

    ax.quiver(
        0, 0, 0,
        d[0], d[1], d[2],
        arrow_length_ratio=0.12
    )

    ax.text(
        d[0], d[1], d[2],
        f"Star {i + 1}"
    )

print("StarLoc 2.0 - Lesson 18")
print("Camera ray directions")
print()

for i, (u, v) in enumerate(pixels):
    d = pixel_to_direction(u, v)
    print(
        f"Star {i + 1}: "
        f"[{d[0]:.4f}, {d[1]:.4f}, {d[2]:.4f}]"
    )

ax.set_xlabel("Camera X")
ax.set_ylabel("Camera Y")
ax.set_zlabel("Camera Z")
ax.set_title("StarLoc 2.0 - Camera Ray Directions")
ax.set_xlim(-1, 1)
ax.set_ylim(-1, 1)
ax.set_zlim(0, 1)
ax.set_box_aspect((1, 1, 1))

plt.tight_layout()
plt.savefig(
    "results/lesson_18_camera_rays.png",
    dpi=150,
    bbox_inches="tight"
)
plt.close()

print()
print("Saved: results/lesson_18_camera_rays.png")
