from pathlib import Path
import csv
import json

import cv2
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import least_squares
from scipy.spatial import cKDTree

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "research/data"
RESULTS = ROOT / "research/results"
SYNTH = DATA / "synthetic"
CATALOGUE = DATA / "catalogue/visible_sky_rouen_2026.csv"
IMAGE_FILE = SYNTH / "catalogue_fisheye_observation.npy"

SIZE = 1024
INITIAL_CX = 511.5
INITIAL_CY = 511.5
INITIAL_F = 500.0 / (np.pi / 2.0)
RADIAL_TOLERANCE = 5.0
MATCH_TOLERANCE = 8.0

def load_catalogue():
    with CATALOGUE.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    rows = [r for r in rows if float(r["vmag"]) <= 5.5]
    return rows

def detect_stars(image):
    # Background is approximately 18 ADU; threshold rejects noise.
    threshold = 33
    binary = (image > threshold).astype(np.uint8)

    count, labels, stats, centroids = cv2.connectedComponentsWithStats(
        binary, connectivity=8
    )

    detections = []
    for label in range(1, count):
        x, y, w, h, area = stats[label]

        if area < 1 or area > 200:
            continue

        mask = labels[y:y+h, x:x+w] == label
        patch = image[y:y+h, x:x+w].astype(float)

        weights = np.maximum(patch - 18.0, 0.0) * mask
        total = weights.sum()

        if total <= 0:
            continue

        yy, xx = np.mgrid[y:y+h, x:x+w]
        cx = float((weights * xx).sum() / total)
        cy = float((weights * yy).sum() / total)

        detections.append((cx, cy, int(area), float(total)))

    return np.asarray(detections, dtype=float)

def catalogue_coordinates(rows):
    altitude = np.deg2rad(
        np.array([float(r["altitude_deg"]) for r in rows])
    )
    azimuth = np.deg2rad(
        np.array([float(r["azimuth_deg"]) for r in rows])
    )

    east = np.cos(altitude) * np.sin(azimuth)
    north = np.cos(altitude) * np.cos(azimuth)
    up = np.sin(altitude)

    return altitude, azimuth, east, north, up

def estimate_roll(detections, rows, altitude, azimuth):
    dx = detections[:, 0] - INITIAL_CX
    dy = detections[:, 1] - INITIAL_CY
    observed_radius = np.hypot(dx, dy)
    observed_angle = np.arctan2(-dy, dx)

    expected_radius = INITIAL_F * (np.pi / 2.0 - altitude)

    votes = []
    for radius, angle in zip(observed_radius, observed_angle):
        candidates = np.where(
            np.abs(expected_radius - radius) < RADIAL_TOLERANCE
        )[0]

        if len(candidates):
            # For the zenith-pointed camera model:
            # image_angle = pi/2 - azimuth + roll
            candidate_rolls = angle - np.pi / 2.0 + azimuth[candidates]
            votes.extend(candidate_rolls.tolist())

    if len(votes) < 10:
        raise RuntimeError(
            f"Insufficient radial candidates for roll estimation: {len(votes)}"
        )

    votes = np.asarray(votes)
    bins = 1440
    histogram, edges = np.histogram(
        np.mod(votes, 2*np.pi), bins=bins, range=(0, 2*np.pi)
    )

    peak = int(np.argmax(histogram))
    peak_angle = (edges[peak] + edges[peak+1]) / 2.0
    difference = np.angle(np.exp(1j * (votes - peak_angle)))
    selected = votes[np.abs(difference) < np.deg2rad(2.0)]

    if len(selected) < 5:
        raise RuntimeError("No stable roll consensus found.")

    return float(np.angle(np.mean(np.exp(1j * selected))))

def project_catalogue(parameters, altitude, azimuth):
    cx, cy, focal, roll = parameters

    east = np.cos(altitude) * np.sin(azimuth)
    north = np.cos(altitude) * np.cos(azimuth)

    cam_x = np.cos(roll) * east - np.sin(roll) * north
    cam_y = np.sin(roll) * east + np.cos(roll) * north

    theta = np.pi / 2.0 - altitude
    horizontal = np.hypot(cam_x, cam_y)

    scale = np.divide(
        focal * theta, horizontal,
        out=np.zeros_like(theta),
        where=horizontal > 1e-12
    )

    x = cx + scale * cam_x
    y = cy - scale * cam_y

    return np.column_stack((x, y))

def unique_matches(detections, predicted, tolerance):
    tree = cKDTree(predicted)
    candidates = []

    for di, point in enumerate(detections[:, :2]):
        indices = tree.query_ball_point(point, tolerance)
        for ci in indices:
            distance = np.linalg.norm(point - predicted[ci])
            candidates.append((distance, di, ci))

    candidates.sort(key=lambda item: item[0])

    used_detections = set()
    used_catalogue = set()
    matches = []

    for distance, di, ci in candidates:
        if di in used_detections or ci in used_catalogue:
            continue
        used_detections.add(di)
        used_catalogue.add(ci)
        matches.append((di, ci, distance))

    return matches

def main():
    if not IMAGE_FILE.exists() or not CATALOGUE.exists():
        raise FileNotFoundError("Phase 10 or Phase 11 data is missing.")

    image = np.load(IMAGE_FILE)
    rows = load_catalogue()

    altitude, azimuth, east, north, up = catalogue_coordinates(rows)

    detections = detect_stars(image)
    if len(detections) < 10:
        raise RuntimeError(f"Only {len(detections)} stars detected.")

    roll = estimate_roll(detections, rows, altitude, azimuth)

    parameters = np.array([
        INITIAL_CX, INITIAL_CY, INITIAL_F, roll
    ], dtype=float)

    # Alternate unique matching and robust parameter refinement.
    for iteration in range(5):
        predicted = project_catalogue(parameters, altitude, azimuth)
        matches = unique_matches(
            detections, predicted, MATCH_TOLERANCE
        )

        if len(matches) < 10:
            raise RuntimeError(
                f"Only {len(matches)} catalogue matches found."
            )

        det_idx = np.array([m[0] for m in matches], dtype=int)
        cat_idx = np.array([m[1] for m in matches], dtype=int)

        observed = detections[det_idx, :2]
        matched_alt = altitude[cat_idx]
        matched_az = azimuth[cat_idx]

        def residual(p):
            projected = project_catalogue(p, matched_alt, matched_az)
            return (projected - observed).ravel()

        fit = least_squares(
            residual,
            parameters,
            loss="soft_l1",
            f_scale=1.0,
            max_nfev=300
        )
        parameters = fit.x

    # Final association and independent residual reporting.
    predicted = project_catalogue(parameters, altitude, azimuth)
    matches = unique_matches(
        detections, predicted, MATCH_TOLERANCE
    )

    det_idx = np.array([m[0] for m in matches], dtype=int)
    cat_idx = np.array([m[1] for m in matches], dtype=int)

    observed = detections[det_idx, :2]
    fitted = predicted[cat_idx]
    errors = np.linalg.norm(observed - fitted, axis=1)

    cx, cy, focal, roll = parameters
    fov = 2.0 * (500.0 / focal) * (180.0 / np.pi)

    output = []
    for di, ci, error in zip(det_idx, cat_idx, errors):
        row = rows[ci]
        output.append({
            "hip_number": int(row["hip_number"]),
            "vmag": float(row["vmag"]),
            "ra_deg": float(row["ra_deg"]),
            "dec_deg": float(row["dec_deg"]),
            "altitude_deg": float(row["altitude_deg"]),
            "azimuth_deg": float(row["azimuth_deg"]),
            "detected_x_px": float(detections[di, 0]),
            "detected_y_px": float(detections[di, 1]),
            "predicted_x_px": float(predicted[ci, 0]),
            "predicted_y_px": float(predicted[ci, 1]),
            "residual_px": float(error)
        })

    with (RESULTS / "blind_catalogue_matches.csv").open(
        "w", newline="", encoding="utf-8"
    ) as f:
        writer = csv.DictWriter(f, fieldnames=list(output[0].keys()))
        writer.writeheader()
        writer.writerows(output)

    calibration = {
        "method": "Blind Hipparcos catalogue matching and robust fisheye refinement",
        "camera_model": "Zenith-pointed equidistant fisheye with unknown roll",
        "optical_center_x_px": float(cx),
        "optical_center_y_px": float(cy),
        "focal_scale_px": float(focal),
        "estimated_fov_deg": float(fov),
        "estimated_roll_deg": float(np.rad2deg(roll) % 360),
        "detected_regions": int(len(detections)),
        "catalogue_candidates": int(len(rows)),
        "identified_stars": int(len(matches)),
        "mean_residual_px": float(np.mean(errors)),
        "median_residual_px": float(np.median(errors)),
        "rmse_px": float(np.sqrt(np.mean(errors**2))),
        "maximum_residual_px": float(np.max(errors)),
        "ground_truth_used_for_matching": False,
        "validation_note": "Synthetic observation; not real camera calibration."
    }

    (RESULTS / "blind_fisheye_calibration.json").write_text(
        json.dumps(calibration, indent=4), encoding="utf-8"
    )

    plt.figure(figsize=(9, 9))
    plt.imshow(np.log1p(image.astype(float)), cmap="gray")
    plt.scatter(
        detections[:, 0], detections[:, 1],
        s=7, facecolors="none", edgecolors="yellow",
        linewidths=0.4, label="Detected"
    )
    plt.scatter(
        observed[:, 0], observed[:, 1],
        s=12, facecolors="none", edgecolors="lime",
        linewidths=0.6, label="Catalogue identified"
    )
    plt.title("Blind Hipparcos Star Identification")
    plt.legend(loc="upper right")
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(RESULTS / "blind_catalogue_identification.png", dpi=160)
    plt.close()

    with (RESULTS / "blind_calibration_residuals.csv").open(
        "w", newline="", encoding="utf-8"
    ) as f:
        writer = csv.writer(f)
        writer.writerow(["hip_number", "residual_px"])
        for item in output:
            writer.writerow([item["hip_number"], item["residual_px"]])

    print("\nSTARLOC 2.0 — BLIND CATALOGUE CALIBRATION")
    print("=" * 55)
    print("Detected image regions:", len(detections))
    print("Available catalogue candidates:", len(rows))
    print("Identified stars:", len(matches))
    print("\nESTIMATED CAMERA PARAMETERS")
    print(f"Optical centre X: {cx:.3f} px")
    print(f"Optical centre Y: {cy:.3f} px")
    print(f"Focal scale: {focal:.3f} px")
    print(f"Estimated FOV: {fov:.3f} degrees")
    print(f"Estimated roll: {np.rad2deg(roll) % 360:.3f} degrees")
    print("\nREPROJECTION RESIDUALS")
    print(f"Mean: {np.mean(errors):.4f} px")
    print(f"Median: {np.median(errors):.4f} px")
    print(f"RMSE: {np.sqrt(np.mean(errors**2)):.4f} px")
    print(f"Maximum: {np.max(errors):.4f} px")
    print("\nSaved:")
    print(RESULTS / "blind_catalogue_matches.csv")
    print(RESULTS / "blind_fisheye_calibration.json")
    print(RESULTS / "blind_calibration_residuals.csv")
    print(RESULTS / "blind_catalogue_identification.png")
    print("\nPHASE 12 COMPLETE")

if __name__ == "__main__":
    main()
