from pathlib import Path
import csv
import json

import cv2
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import least_squares
from scipy.spatial import cKDTree

ROOT = Path(__file__).resolve().parents[1]
CATALOGUE = ROOT / "research/data/catalogue/visible_sky_rouen_2026.csv"
RESULTS = ROOT / "research/results"
RESULTS.mkdir(parents=True, exist_ok=True)

SIZE = 1024
RADIUS = 500.0
FOV = np.pi
CX = 511.5
CY = 511.5
FOCAL = RADIUS / (FOV / 2)
SEED = 202613

def read_catalogue():
    with CATALOGUE.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    rows = [r for r in rows if float(r["vmag"]) <= 5.5]
    altitude = np.deg2rad([float(r["altitude_deg"]) for r in rows])
    azimuth = np.deg2rad([float(r["azimuth_deg"]) for r in rows])
    magnitude = np.array([float(r["vmag"]) for r in rows])
    return rows, altitude, azimuth, magnitude

def project(altitude, azimuth, cx, cy, focal, roll):
    east = np.cos(altitude) * np.sin(azimuth)
    north = np.cos(altitude) * np.cos(azimuth)
    cam_x = np.cos(roll) * east - np.sin(roll) * north
    cam_y = np.sin(roll) * east + np.cos(roll) * north
    theta = np.pi / 2 - altitude
    horizontal = np.hypot(cam_x, cam_y)
    scale = np.divide(
        focal * theta, horizontal,
        out=np.zeros_like(theta), where=horizontal > 1e-12
    )
    return np.column_stack((cx + scale * cam_x, cy - scale * cam_y))

def render(rows, altitude, azimuth, magnitude, roll, rng,
           noise_sigma=3.0, missing_fraction=0.08, false_count=35):
    image = np.full((SIZE, SIZE), 18.0, dtype=np.float32)
    truth_xy = project(altitude, azimuth, CX, CY, FOCAL, roll)

    eligible = np.where(
        (magnitude <= 5.5) &
        (np.linalg.norm(truth_xy - [CX, CY], axis=1) < RADIUS - 4) &
        (truth_xy[:, 0] >= 3) & (truth_xy[:, 0] < SIZE - 3) &
        (truth_xy[:, 1] >= 3) & (truth_xy[:, 1] < SIZE - 3)
    )[0]

    keep = rng.random(len(eligible)) >= missing_fraction
    visible = eligible[keep]

    yy, xx = np.mgrid[-3:4, -3:4]
    sigma = 1.15
    kernel = np.exp(-(xx**2 + yy**2) / (2*sigma**2))
    kernel /= kernel.max()

    for index in visible:
        x, y = truth_xy[index]
        brightness = 90.0 * 10 ** (-0.4 * (magnitude[index] - 1.0))
        brightness = float(np.clip(brightness, 35, 220))
        ix, iy = int(round(x)), int(round(y))
        image[iy-3:iy+4, ix-3:ix+4] += brightness * kernel

    image += rng.normal(0, noise_sigma, image.shape)

    # Add isolated false-positive spots.
    for _ in range(false_count):
        x = int(rng.integers(5, SIZE-5))
        y = int(rng.integers(5, SIZE-5))
        image[y-1:y+2, x-1:x+2] += 45.0

    return np.clip(image, 0, 255), truth_xy, visible

def detect(image):
    binary = (image > 33).astype(np.uint8)
    count, labels, stats, _ = cv2.connectedComponentsWithStats(
        binary, connectivity=8
    )
    found = []

    for label in range(1, count):
        x, y, w, h, area = stats[label]
        if area < 1 or area > 200:
            continue

        mask = labels[y:y+h, x:x+w] == label
        patch = image[y:y+h, x:x+w].astype(float)
        weights = np.maximum(patch - 18.0, 0) * mask
        total = weights.sum()
        if total <= 0:
            continue

        yy, xx = np.mgrid[y:y+h, x:x+w]
        found.append([
            (weights * xx).sum() / total,
            (weights * yy).sum() / total
        ])

    return np.asarray(found, dtype=float)

def estimate_roll(detections, altitude, azimuth):
    dx = detections[:, 0] - CX
    dy = detections[:, 1] - CY
    radius = np.hypot(dx, dy)
    angle = np.arctan2(-dy, dx)
    expected_radius = FOCAL * (np.pi/2 - altitude)

    votes = []
    for r, a in zip(radius, angle):
        candidates = np.where(np.abs(expected_radius-r) < 5.0)[0]
        if len(candidates):
            votes.extend((a - np.pi/2 + azimuth[candidates]).tolist())

    if len(votes) < 10:
        raise RuntimeError("Insufficient roll-estimation candidates.")

    votes = np.asarray(votes)
    hist, edges = np.histogram(
        np.mod(votes, 2*np.pi), bins=1440, range=(0, 2*np.pi)
    )
    peak = (edges[np.argmax(hist)] + edges[np.argmax(hist)+1]) / 2
    delta = np.angle(np.exp(1j*(votes-peak)))
    selected = votes[np.abs(delta) < np.deg2rad(2)]
    if len(selected) < 5:
        raise RuntimeError("No stable roll consensus.")
    return float(np.angle(np.mean(np.exp(1j*selected))))

def associate(detections, predicted, tolerance=8.0):
    tree = cKDTree(predicted)
    candidates = []
    for di, point in enumerate(detections):
        for ci in tree.query_ball_point(point, tolerance):
            candidates.append((
                np.linalg.norm(point-predicted[ci]), di, ci
            ))
    candidates.sort()
    used_d, used_c, matches = set(), set(), []
    for error, di, ci in candidates:
        if di not in used_d and ci not in used_c:
            used_d.add(di)
            used_c.add(ci)
            matches.append((di, ci))
    return matches

def fit_camera(observed, altitude, azimuth, initial_roll):
    p0 = np.array([CX, CY, FOCAL, initial_roll], dtype=float)

    def residual(p):
        return (
            project(altitude, azimuth, *p) - observed
        ).ravel()

    result = least_squares(
        residual, p0, loss="soft_l1", f_scale=1.0, max_nfev=300
    )
    return result.x

def run_case(case, rows, altitude, azimuth, magnitude, rng):
    image, truth_xy, visible = render(
        rows, altitude, azimuth, magnitude, case["roll_deg"] * np.pi/180,
        rng, case["noise"], case["missing"], case["false"]
    )
    detections = detect(image)
    roll0 = estimate_roll(detections, altitude, azimuth)
    initial_projection = project(
        altitude, azimuth, CX, CY, FOCAL, roll0
    )
    matches = associate(detections, initial_projection)

    if len(matches) < 20:
        raise RuntimeError(
            f"{case['name']}: only {len(matches)} initial matches."
        )

    di = np.array([m[0] for m in matches])
    ci = np.array([m[1] for m in matches])
    observed = detections[di]
    p = fit_camera(observed, altitude[ci], azimuth[ci], roll0)

    fitted = project(altitude[ci], azimuth[ci], *p)
    errors = np.linalg.norm(fitted-observed, axis=1)

    # Evaluate estimated parameters against simulation settings.
    roll_error = abs(np.rad2deg(np.angle(
        np.exp(1j*(p[3] - case["roll_deg"]*np.pi/180))
    )))

    result = {
        "case": case["name"],
        "roll_true_deg": case["roll_deg"],
        "roll_estimated_deg": float(np.rad2deg(p[3]) % 360),
        "roll_error_deg": float(roll_error),
        "detected_regions": int(len(detections)),
        "catalogue_matches": int(len(matches)),
        "match_rate_percent": float(100*len(matches)/max(len(visible), 1)),
        "centre_x_error_px": float(p[0]-CX),
        "centre_y_error_px": float(p[1]-CY),
        "focal_error_px": float(p[2]-FOCAL),
        "mean_reprojection_error_px": float(np.mean(errors)),
        "rmse_px": float(np.sqrt(np.mean(errors**2))),
        "maximum_error_px": float(np.max(errors))
    }

    # Four overlapping image sections; fit each from its local matches.
    sections = [
        ("top_left", 0, 0, 540, 540),
        ("top_right", 484, 0, 1024, 540),
        ("bottom_left", 0, 484, 540, 1024),
        ("bottom_right", 484, 484, 1024, 1024)
    ]
    section_results = []

    for name, x0, y0, x1, y1 in sections:
        mask = (
            (observed[:, 0] >= x0) & (observed[:, 0] < x1) &
            (observed[:, 1] >= y0) & (observed[:, 1] < y1)
        )
        if mask.sum() < 8:
            section_results.append({
                "section": name, "matches": int(mask.sum()),
                "status": "insufficient stars"
            })
            continue

        local_p = fit_camera(
            observed[mask], altitude[ci][mask], azimuth[ci][mask], p[3]
        )
        local_projected = project(
            altitude[ci][mask], azimuth[ci][mask], *local_p
        )
        local_error = np.linalg.norm(
            local_projected-observed[mask], axis=1
        )
        section_results.append({
            "section": name,
            "matches": int(mask.sum()),
            "centre_x_error_px": float(local_p[0]-CX),
            "centre_y_error_px": float(local_p[1]-CY),
            "focal_error_px": float(local_p[2]-FOCAL),
            "roll_error_deg": float(abs(np.rad2deg(np.angle(
                np.exp(1j*(local_p[3]-case["roll_deg"]*np.pi/180))
            )))),
            "rmse_px": float(np.sqrt(np.mean(local_error**2))),
            "status": "fitted"
        })

    result["sections"] = section_results
    return result, image, detections, observed

def main():
    rng = np.random.default_rng(SEED)
    rows, altitude, azimuth, magnitude = read_catalogue()

    cases = [
        {"name": "roll_0_clean", "roll_deg": 0, "noise": 2.0,
         "missing": 0.03, "false": 10},
        {"name": "roll_37_noisy", "roll_deg": 37, "noise": 3.0,
         "missing": 0.08, "false": 35},
        {"name": "roll_123_degraded", "roll_deg": 123, "noise": 4.0,
         "missing": 0.18, "false": 60},
        {"name": "roll_271_stress", "roll_deg": 271, "noise": 5.0,
         "missing": 0.25, "false": 90}
    ]

    all_results = []
    for case in cases:
        print("\nRunning:", case["name"])
        result, image, detections, observed = run_case(
            case, rows, altitude, azimuth, magnitude, rng
        )
        all_results.append(result)
        print(
            "Matches:", result["catalogue_matches"],
            "| Roll error:", f'{result["roll_error_deg"]:.4f}°',
            "| RMSE:", f'{result["rmse_px"]:.4f} px'
        )

        if case["name"] == "roll_37_noisy":
            plt.figure(figsize=(8, 8))
            plt.imshow(np.log1p(image), cmap="gray")
            plt.scatter(
                detections[:, 0], detections[:, 1],
                s=5, facecolors="none", edgecolors="yellow",
                linewidths=0.4
            )
            plt.scatter(
                observed[:, 0], observed[:, 1],
                s=10, facecolors="none", edgecolors="lime",
                linewidths=0.5
            )
            plt.title("Phase 13: detected and identified stars")
            plt.axis("off")
            plt.tight_layout()
            plt.savefig(
                RESULTS / "phase13_robustness_example.png", dpi=160
            )
            plt.close()

    summary = {
        "title": "StarLoc 2.0 robustness and multi-section validation",
        "synthetic_test_only": True,
        "camera_model": "Zenith-pointed equidistant fisheye",
        "ground_truth_used_for_matching": False,
        "cases": all_results,
        "overall": {
            "mean_roll_error_deg": float(np.mean([
                r["roll_error_deg"] for r in all_results
            ])),
            "mean_reprojection_rmse_px": float(np.mean([
                r["rmse_px"] for r in all_results
            ])),
            "total_catalogue_matches": int(sum(
                r["catalogue_matches"] for r in all_results
            ))
        }
    }

    output = RESULTS / "phase13_robustness_report.json"
    output.write_text(json.dumps(summary, indent=4), encoding="utf-8")

    with (RESULTS / "phase13_summary.csv").open(
        "w", newline="", encoding="utf-8"
    ) as f:
        fields = [
            "case", "roll_true_deg", "roll_estimated_deg",
            "roll_error_deg", "detected_regions", "catalogue_matches",
            "match_rate_percent", "centre_x_error_px",
            "centre_y_error_px", "focal_error_px",
            "mean_reprojection_error_px", "rmse_px", "maximum_error_px"
        ]
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for result in all_results:
            writer.writerow({k: result[k] for k in fields})

    print("\n" + "="*58)
    print("STARLOC 2.0 — PHASE 13 VALIDATION")
    print("="*58)
    print("Test cases:", len(all_results))
    print("Total catalogue matches:",
          summary["overall"]["total_catalogue_matches"])
    print("Mean roll error:",
          f'{summary["overall"]["mean_roll_error_deg"]:.5f} degrees')
    print("Mean reprojection RMSE:",
          f'{summary["overall"]["mean_reprojection_rmse_px"]:.5f} pixels')
    print("\nSaved:")
    print(output)
    print(RESULTS / "phase13_summary.csv")
    print(RESULTS / "phase13_robustness_example.png")
    print("\nPHASE 13 COMPLETE")

if __name__ == "__main__":
    main()
