
import numpy as np

# ==========================================
# StarLoc 2.0 - Lesson 16
# Pixel to 3D Direction
# ==========================================

# Camera parameters
image_width = 1280
image_height = 720

fx = 500.0
fy = 500.0

cx = image_width / 2
cy = image_height / 2

# Example star pixel positions
pixels = np.array([
    [640.0, 360.0],  # Image centre
    [720.0, 340.0],  # Right and slightly up
    [500.0, 400.0],  # Left and down
    [800.0, 450.0]   # Right and down
])

def pixel_to_direction(u, v):
    # Convert pixel coordinates to camera coordinates
    x = (u - cx) / fx
    y = (v - cy) / fy

    # Create a 3D direction vector
    direction = np.array([x, y, 1.0])

    # Normalize the vector
    direction = direction / np.linalg.norm(direction)

    return direction

print("===================================")
print("StarLoc 2.0 - Lesson 16")
print("Pixel to 3D Direction")
print("===================================")

for i, (u, v) in enumerate(pixels):
    direction = pixel_to_direction(u, v)

    print(f"\nStar {i + 1}")
    print(f"Pixel position: ({u:.1f}, {v:.1f})")
    print(
        "Direction vector: "
        f"[{direction[0]:.5f}, "
        f"{direction[1]:.5f}, "
        f"{direction[2]:.5f}]"
    )
    print(f"Vector length: {np.linalg.norm(direction):.5f}")

print("\nLesson 16 completed successfully.")
