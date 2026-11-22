import csv
import json
from pathlib import Path

import cv2
import numpy as np

RNG = np.random.default_rng(2026)

IMAGE_SIZE = 1024
IMAGE_CENTER = IMAGE_SIZE / 2
IMAGE_RADIUS = 500.0
FISHEYE_FOV_DEG = 180.0
NUMBER_OF_STARS = 100
GAUSSIAN_SIGMA = 1.35
BACKGROUND_NOISE = 0.003

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "research" / "data" / "synthetic"
RESULTS_DIR = ROOT / "research" / "results"

DATA_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def rotation_matrix_x(angle):
    a = np.radians(angle)
    c, s = np.cos(a), np.sin(a)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])


def rotation_matrix_y(angle):
    a = np.radians(angle)
    c, s = np.cos(a), np.sin(a)
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])


def rotation_matrix_z(angle):
    a = np.radians(angle)
    c, s = np.cos(a), np.sin(a)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])


def camera_to_celestial_rotation():
    return (
        rotation_matrix_z(25.0)
        @ rotation_matrix_y(-12.0)
        @ rotation_matrix_x(8.0)
    )


def generate_star_directions(count):
    min_cos = np.cos(np.radians(85.0))
    cos_theta = RNG.uniform(min_cos, 1.0, count)
    phi = RNG.uniform(0.0, 2.0 * np.pi, count)
    sin_theta = np.sqrt(1.0 - cos_theta**2)

    return np.column_stack((
        sin_theta * np.cos(phi),
        sin_theta * np.sin(phi),
        cos_theta
    ))


def camera_direction_to_pixel(direction):
    x, y, z = direction
    theta = np.arccos(np.clip(z, -1.0, 1.0))
    phi = np.arctan2(y, x)
    focal_length = IMAGE_RADIUS / np.radians(FISHEYE_FOV_DEG / 2)

    u = IMAGE_CENTER + focal_length * theta * np.cos(phi)
    v = IMAGE_CENTER - focal_length * theta * np.sin(phi)
    return float(u), float(v)


def celestial_coordinates(direction):
    x, y, z = direction
    ra = np.degrees(np.arctan2(y, x)) % 360.0
    dec = np.degrees(np.arcsin(np.clip(z, -1.0, 1.0)))
    return float(ra), float(dec)


def add_gaussian_star(image, u, v, magnitude):
    amplitude = 0.75 * 10 ** (-0.4 * (magnitude - 1.0))
    x0, y0 = int(round(u)), int(round(v))
    r = 6

    x_min, x_max = max(0, x0-r), min(IMAGE_SIZE, x0+r+1)
    y_min, y_max = max(0, y0-r), min(IMAGE_SIZE, y0+r+1)

    yy, xx = np.mgrid[y_min:y_max, x_min:x_max]
    gaussian = amplitude * np.exp(
        -((xx-u)**2 + (yy-v)**2) / (2.0*GAUSSIAN_SIGMA**2)
    )
    image[y_min:y_max, x_min:x_max] += gaussian


def main():
    image = np.zeros((IMAGE_SIZE, IMAGE_SIZE), dtype=np.float32)
    camera_directions = generate_star_directions(NUMBER_OF_STARS)
    rotation = camera_to_celestial_rotation()
    records = []

    for index, camera_direction in enumerate(camera_directions, start=1):
        u, v = camera_direction_to_pixel(camera_direction)

        if not (0 <= u < IMAGE_SIZE and 0 <= v < IMAGE_SIZE):
            continue

        celestial_direction = rotation @ camera_direction
        ra, dec = celestial_coordinates(celestial_direction)
        magnitude = float(RNG.uniform(1.0, 5.0))

        add_gaussian_star(image, u, v, magnitude)

        records.append({
            "star_id": index,
            "ra_deg": ra,
            "dec_deg": dec,
            "x_pixel": u,
            "y_pixel": v,
            "magnitude": magnitude
        })

    image += RNG.normal(
        0.0, BACKGROUND_NOISE, image.shape
    ).astype(np.float32)
    image = np.clip(image, 0.0, 1.0)

    np.save(DATA_DIR / "synthetic_fisheye.npy", image)
    cv2.imwrite(
        str(DATA_DIR / "synthetic_fisheye.png"),
        (image * 255).astype(np.uint8)
    )

    with (DATA_DIR / "synthetic_star_catalogue.csv").open(
        "w", newline=""
    ) as file:
        writer = csv.DictWriter(file, fieldnames=[
            "star_id", "ra_deg", "dec_deg",
            "x_pixel", "y_pixel", "magnitude"
        ])
        writer.writeheader()
        writer.writerows(records)

    metadata = {
        "project": "StarLoc 2.0",
        "dataset_type": "synthetic",
        "projection": "equidistant_fisheye",
        "nominal_fov_deg": FISHEYE_FOV_DEG,
        "image_width": IMAGE_SIZE,
        "image_height": IMAGE_SIZE,
        "image_radius_pixels": IMAGE_RADIUS,
        "number_of_stars": len(records),
        "camera_orientation_euler_deg": {
            "x": 8.0, "y": -12.0, "z": 25.0
        },
        "random_seed": 2026,
        "note": "Synthetic test data, not real AllSkyKamera data."
    }

    with (DATA_DIR / "synthetic_metadata.json").open("w") as file:
        json.dump(metadata, file, indent=4)

    print("\nSTARLOC 2.0 - SYNTHETIC DATASET")
    print("--------------------------------")
    print(f"Image: {IMAGE_SIZE} x {IMAGE_SIZE}")
    print(f"Fisheye FOV: {FISHEYE_FOV_DEG} degrees")
    print(f"Stars generated: {len(records)}")
    print(f"Output directory: {DATA_DIR}")
    print("DATASET GENERATION COMPLETE")


if __name__ == "__main__":
    main()
