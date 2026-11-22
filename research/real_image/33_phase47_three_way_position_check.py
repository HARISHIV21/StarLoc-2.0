import csv
import json
from pathlib import Path

import cv2
import numpy as np
import matplotlib.pyplot as plt
from astropy.wcs import WCS

BASE = Path("research/real_image")
RESULTS = BASE / "results/ASK033"

IMAGE = BASE / "data/network/ASK033/ASK033_live_grayscale.png"
PHASE37 = RESULTS / "phase37_validation/phase37_all_matches.csv"
PHASE45 = RESULTS / "phase45_leave_r2c2_out/phase45_leave_r2c2_out_residuals.csv"
WCS_FILE = RESULTS / "custom_plate_solutions/R2C2_custom.wcs"

OUT = RESULTS / "phase47_three_way_check"
OUT.mkdir(parents=True, exist_ok=True)

OFFSET_X, OFFSET_Y = 640, 480
CROP_RADIUS = 55

for path in [IMAGE, PHASE37, PHASE45, WCS_FILE]:
    if not path.exists():
        raise FileNotFoundError(path)

image = cv2.imread(str(IMAGE), cv2.IMREAD_GRAYSCALE)
if image is None:
    raise RuntimeError("Cannot read source image.")

with PHASE37.open(newline="") as f:
    phase37 = list(csv.DictReader(f))

with PHASE45.open(newline="") as f:
    phase45 = list(csv.DictReader(f))

phase45_r2c2 = [
    r for r in phase45
    if r["section"] == "R2C2"
    and float(r["residual_px"]) > 10
]
phase45_r2c2.sort(
    key=lambda r: float(r["residual_px"]),
    reverse=True
)

if len(phase45_r2c2) != 4:
    raise RuntimeError(f"Expected four points; found {len(phase45_r2c2)}")

wcs = WCS(str(WCS_FILE))

records = []

def local_peak(x, y, radius=5):
    """Find local maximum close to a specified predicted position."""
    x, y = int(round(x)), int(round(y))

    x0 = max(0, x - radius)
    x1 = min(image.shape[1], x + radius + 1)
    y0 = max(0, y - radius)
    y1 = min(image.shape[0], y + radius + 1)

    patch = image[y0:y1, x0:x1]
    if patch.size == 0:
        return None

    py, px = np.unravel_index(np.argmax(patch), patch.shape)
    return {
        "x": float(x0 + px),
        "y": float(y0 + py),
        "intensity": float(patch[py, px]),
        "distance_from_prediction_px": float(
            np.hypot(x0 + px - x, y0 + py - y)
        ),
    }

for number, p45 in enumerate(phase45_r2c2, start=1):
    gx = float(p45["global_x"])
    gy = float(p45["global_y"])

    lx = gx - OFFSET_X
    ly = gy - OFFSET_Y

    match = [
        r for r in phase37
        if r["section"] == "R2C2"
        and abs(float(r["candidate_x_local"]) - lx) < 0.002
        and abs(float(r["candidate_y_local"]) - ly) < 0.002
    ]

    if len(match) != 1:
        raise RuntimeError(f"Cannot identify unique Phase 37 match for Star {number}")

    match = match[0]
    ra = float(match["hip_ra_deg"])
    dec = float(match["hip_dec_deg"])

    # Direct local-WCS catalogue projection.
    local_wcs_xy = wcs.all_world2pix(
        np.array([[ra, dec]], dtype=float),
        0,
        quiet=True
    )[0]

    local_wcs_global = np.array([
        local_wcs_xy[0] + OFFSET_X,
        local_wcs_xy[1] + OFFSET_Y
    ])

    global_prediction = np.array([
        float(p45["predicted_x"]),
        float(p45["predicted_y"])
    ])

    candidate = np.array([gx, gy])

    positions = {
        "detected_candidate": candidate,
        "local_wcs_prediction": local_wcs_global,
        "global_fisheye_prediction": global_prediction,
    }

    measurements = {}
    for name, pos in positions.items():
        measurements[name] = {
            "position": [float(pos[0]), float(pos[1])],
            "distance_from_candidate_px": float(
                np.linalg.norm(pos - candidate)
            ),
            "local_peak": local_peak(pos[0], pos[1]),
        }

    records.append({
        "star": number,
        "hip_ra_deg": ra,
        "hip_dec_deg": dec,
        "phase37_wcs_residual_px": float(match["pixel_residual"]),
        "phase45_global_residual_px": float(p45["residual_px"]),
        "positions": measurements,
    })

    print(f"\nSTAR {number}")
    print(f"  Candidate: ({gx:.3f}, {gy:.3f})")
    print(
        "  Local WCS:",
        f"({local_wcs_global[0]:.3f}, {local_wcs_global[1]:.3f})",
    )
    print(
        "  Global fisheye:",
        f"({global_prediction[0]:.3f}, {global_prediction[1]:.3f})",
    )

    print("  Candidate-to-local-WCS distance:",
          f"{np.linalg.norm(local_wcs_global-candidate):.3f}px")
    print("  Candidate-to-global-model distance:",
          f"{np.linalg.norm(global_prediction-candidate):.3f}px")

    for name, measurement in measurements.items():
        print(f"  {name} nearby peak:", measurement["local_peak"])

# Four rows, three columns: same image region, three coordinate hypotheses.
fig, axes = plt.subplots(4, 3, figsize=(15, 18))

column_names = [
    "detected_candidate",
    "local_wcs_prediction",
    "global_fisheye_prediction",
]

for row_index, record in enumerate(records):
    candidate = np.array([
        record["positions"]["detected_candidate"]["position"][0],
        record["positions"]["detected_candidate"]["position"][1],
    ])

    for col_index, name in enumerate(column_names):
        ax = axes[row_index, col_index]

        position = np.array(
            record["positions"][name]["position"]
        )

        # Use a common crop centred on the detected candidate.
        cx, cy = int(round(candidate[0])), int(round(candidate[1]))
        x0 = max(0, cx - CROP_RADIUS)
        x1 = min(image.shape[1], cx + CROP_RADIUS + 1)
        y0 = max(0, cy - CROP_RADIUS)
        y1 = min(image.shape[0], cy + CROP_RADIUS + 1)

        crop = image[y0:y1, x0:x1]
        ax.imshow(crop, cmap="gray", vmin=0, vmax=255)

        ax.scatter(
            [candidate[0] - x0],
            [candidate[1] - y0],
            marker="+",
            s=130,
            linewidths=2,
            label="Detected candidate",
        )

        ax.scatter(
            [position[0] - x0],
            [position[1] - y0],
            marker="x",
            s=100,
            linewidths=2,
            label=name.replace("_", " "),
        )

        peak = record["positions"][name]["local_peak"]
        if peak:
            ax.scatter(
                [peak["x"] - x0],
                [peak["y"] - y0],
                marker="o",
                s=65,
                facecolors="none",
                edgecolors="yellow",
                label="Nearby local maximum",
            )

        ax.set_title(
            f"Star {record['star']} — {name.replace('_', ' ')}"
        )
        ax.axis("off")

        if row_index == 0 and col_index == 0:
            ax.legend(fontsize=7, loc="upper right")

fig.suptitle(
    "Phase 47 — Candidate vs local WCS vs global fisheye predictions",
    fontsize=14
)
fig.tight_layout()

plot_path = OUT / "phase47_three_way_comparison.png"
fig.savefig(plot_path, dpi=180)
plt.close(fig)

report_path = BASE / "phase47_three_way_position_report.json"
with report_path.open("w") as f:
    json.dump({
        "phase": 47,
        "method": "Direct comparison of detected, local WCS and global fisheye positions",
        "points": records,
        "limitations": [
            "Local WCS and global model are not independent ground truth.",
            "Nearby maximum intensity is not necessarily a stellar centroid.",
            "Image inspection is required before classifying a correspondence.",
        ],
    }, f, indent=2)

print("\n" + "=" * 70)
print("PHASE 47 COMPLETED")
print("=" * 70)
print("Comparison image:", plot_path)
print("JSON report:", report_path)
