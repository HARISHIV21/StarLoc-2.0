from pathlib import Path
import csv
import json

import numpy as np
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "research/data/catalogue/visible_sky_rouen_2026.csv"
DATA = ROOT / "research/data/synthetic"
RESULTS = ROOT / "research/results"

DATA.mkdir(parents=True, exist_ok=True)
RESULTS.mkdir(parents=True, exist_ok=True)

SIZE = 1024
CX = CY = 511.5
RADIUS = 500.0
FOV_DEG = 180.0
FOCAL = RADIUS / np.deg2rad(FOV_DEG / 2.0)

# Hidden camera orientation used only to create the test observation.
CAMERA_ROLL_DEG = 37.0
MAGNITUDE_LIMIT = 5.5
MIN_ALTITUDE_DEG = 5.0
SEED = 20261120

def main():
    if not INPUT.exists():
        raise FileNotFoundError(INPUT)

    rng = np.random.default_rng(SEED)
    with INPUT.open(newline="", encoding="utf-8") as f:
        stars = list(csv.DictReader(f))

    image = np.zeros((SIZE, SIZE), dtype=np.float64)
    yy, xx = np.mgrid[0:SIZE, 0:SIZE]
    radial_mask = (xx - CX)**2 + (yy - CY)**2 <= RADIUS**2

    image[radial_mask] = 18.0
    image += rng.normal(0.0, 3.0, image.shape)

    roll = np.deg2rad(CAMERA_ROLL_DEG)
    c, s = np.cos(roll), np.sin(roll)

    truth = []
    sigma = 1.15
    patch_radius = 5

    for star in stars:
        hip = int(star["hip_number"])
        magnitude = float(star["vmag"])
        altitude = float(star["altitude_deg"])
        azimuth = float(star["azimuth_deg"])

        if magnitude > MAGNITUDE_LIMIT or altitude < MIN_ALTITUDE_DEG:
            continue

        alt = np.deg2rad(altitude)
        az = np.deg2rad(azimuth)

        # Local ENU direction: east, north, up.
        east = np.cos(alt) * np.sin(az)
        north = np.cos(alt) * np.cos(az)
        up = np.sin(alt)

        # Apply unknown camera roll.
        cam_x = c * east - s * north
        cam_y = s * east + c * north

        theta = np.arccos(np.clip(up, -1.0, 1.0))
        horizontal = np.hypot(cam_x, cam_y)

        if horizontal < 1e-12:
            px, py = CX, CY
        else:
            px = CX + FOCAL * theta * cam_x / horizontal
            py = CY - FOCAL * theta * cam_y / horizontal

        if not (0 <= px < SIZE and 0 <= py < SIZE):
            continue

        # Approximate brightness with magnitude and atmospheric extinction.
        airmass = 1.0 / max(np.sin(alt), 0.12)
        apparent_mag = magnitude + 0.15 * (airmass - 1.0)
        amplitude = 4500.0 * 10.0 ** (-0.4 * apparent_mag)

        ix, iy = int(round(px)), int(round(py))
        x0, x1 = max(0, ix-patch_radius), min(SIZE, ix+patch_radius+1)
        y0, y1 = max(0, iy-patch_radius), min(SIZE, iy+patch_radius+1)

        local_x = np.arange(x0, x1)
        local_y = np.arange(y0, y1)
        gx, gy = np.meshgrid(local_x, local_y)

        psf = amplitude * np.exp(
            -((gx-px)**2 + (gy-py)**2) / (2.0 * sigma**2)
        )
        image[y0:y1, x0:x1] += psf

        truth.append({
            "hip_number": hip,
            "ra_deg": float(star["ra_deg"]),
            "dec_deg": float(star["dec_deg"]),
            "vmag": magnitude,
            "altitude_deg": altitude,
            "azimuth_deg": azimuth,
            "true_x_px": float(px),
            "true_y_px": float(py)
        })

    image = np.clip(image, 0, 65535).astype(np.uint16)

    np.save(DATA / "catalogue_fisheye_observation.npy", image)

    preview = np.log1p(image.astype(float))
    preview[~radial_mask] = 0

    plt.figure(figsize=(9, 9))
    plt.imshow(preview, cmap="gray", origin="upper")
    plt.scatter(
        [item["true_x_px"] for item in truth],
        [item["true_y_px"] for item in truth],
        s=5, facecolors="none", edgecolors="red", linewidths=0.35
    )
    plt.title("Synthetic 180° Fisheye — Hipparcos Catalogue Observation")
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(RESULTS / "catalogue_fisheye_observation.png", dpi=160)
    plt.close()

    with (DATA / "catalogue_fisheye_ground_truth.csv").open(
        "w", newline="", encoding="utf-8"
    ) as f:
        writer = csv.DictWriter(f, fieldnames=list(truth[0].keys()))
        writer.writeheader()
        writer.writerows(truth)

    metadata = {
        "image_size_px": SIZE,
        "projection": "Equidistant fisheye: r = f * theta",
        "nominal_fov_deg": FOV_DEG,
        "optical_center_px": [CX, CY],
        "focal_scale_px": FOCAL,
        "camera_roll_deg": CAMERA_ROLL_DEG,
        "camera_roll_status": "Hidden test parameter; not supplied to identification",
        "magnitude_limit": MAGNITUDE_LIMIT,
        "stars_rendered": len(truth),
        "catalogue": "Hipparcos propagated positions, Rouen test observation",
        "noise_sigma": 3.0,
        "psf_sigma_px": sigma,
        "ground_truth_file": "catalogue_fisheye_ground_truth.csv",
        "warning": "Synthetic image, not a real AllSkyKamera exposure."
    }

    (DATA / "catalogue_fisheye_metadata.json").write_text(
        json.dumps(metadata, indent=4), encoding="utf-8"
    )

    print("\nSTARLOC 2.0 — CATALOGUE FISHEYE OBSERVATION")
    print("=" * 55)
    print("Image:", SIZE, "x", SIZE)
    print("Projection: Equidistant fisheye")
    print("FOV:", FOV_DEG, "degrees")
    print("Stars rendered:", len(truth))
    print("Magnitude limit:", MAGNITUDE_LIMIT)
    print("Image noise: enabled")
    print("Camera roll: hidden from identification stage")
    print("\nGenerated:")
    print(DATA / "catalogue_fisheye_observation.npy")
    print(DATA / "catalogue_fisheye_ground_truth.csv")
    print(DATA / "catalogue_fisheye_metadata.json")
    print(RESULTS / "catalogue_fisheye_observation.png")
    print("\nPHASE 11 COMPLETE")

if __name__ == "__main__":
    main()
