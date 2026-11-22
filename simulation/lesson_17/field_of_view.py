
import numpy as np

# ==========================================
# StarLoc 2.0 - Lesson 17
# Camera Field of View
# ==========================================

image_width = 1280
image_height = 720

fx = 500.0
fy = 500.0

# Calculate FOV in radians
fov_x = 2 * np.arctan(image_width / (2 * fx))
fov_y = 2 * np.arctan(image_height / (2 * fy))

# Convert radians to degrees
fov_x_deg = np.degrees(fov_x)
fov_y_deg = np.degrees(fov_y)

print("===================================")
print("StarLoc 2.0 - Lesson 17")
print("Camera Field of View")
print("===================================")

print(f"Image width: {image_width} pixels")
print(f"Image height: {image_height} pixels")
print(f"Focal length X: {fx} pixels")
print(f"Focal length Y: {fy} pixels")

print()
print(f"Horizontal FOV: {fov_x_deg:.2f} degrees")
print(f"Vertical FOV:   {fov_y_deg:.2f} degrees")

print()
print("Testing different focal lengths:")
print()

for focal_length in [300, 500, 800, 1200]:
    fov = 2 * np.arctan(
        image_width / (2 * focal_length)
    )

    print(
        f"Focal length {focal_length:4d} px "
        f"-> Horizontal FOV {np.degrees(fov):.2f} degrees"
    )

print()
print("Lesson 17 completed successfully.")
