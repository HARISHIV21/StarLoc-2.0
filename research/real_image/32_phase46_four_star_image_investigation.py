import csv
import json
from pathlib import Path

import cv2
import numpy as np
import matplotlib.pyplot as plt

BASE = Path("research/real_image")
RESULTS = BASE / "results/ASK033"

PHASE45 = (
    RESULTS / "phase45_leave_r2c2_out/"
    "phase45_leave_r2c2_out_residuals.csv"
)
PHASE37 = RESULTS / "phase37_validation/phase37_all_matches.csv"

OUT = RESULTS / "phase46_four_star_investigation"
OUT.mkdir(parents=True, exist_ok=True)

WIDTH, HEIGHT = 1920, 1440
CROP_RADIUS = 65

def find_source_image():
    extensions = {".jpg", ".jpeg", ".png", ".tif", ".tiff"}

    candidates = []
    for path in BASE.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in extensions:
            continue
        if "phase46" in str(path).lower():
            continue

        image = cv2.imread(str(path), cv2.IMREAD_COLOR)
        if image is None:
            continue

        h, w = image.shape[:2]
        if (w, h) == (WIDTH, HEIGHT):
            priority = 0 if "ASK033" in path.name.upper() else 1
            candidates.append((priority, path))

    candidates.sort(key=lambda item: (item[0], str(item[1])))

    if not candidates:
        raise FileNotFoundError(
            "No 1920x1440 source image found under research/real_image. "
            "Check that the original ASK033 image is present."
        )

    print("Image candidates:")
    for priority, path in candidates:
        print(" ", path)

    return candidates[0][1]

if not PHASE45.exists():
    raise FileNotFoundError(PHASE45)

if not PHASE37.exists():
    raise FileNotFoundError(PHASE37)

print("=" * 70)
print("STARLOC 2.0 — PHASE 46")
print("FOUR-STAR IMAGE AND CENTROID INVESTIGATION")
print("=" * 70)

image_path = find_source_image()
image_bgr = cv2.imread(str(image_path), cv2.IMREAD_COLOR)

if image_bgr is None:
    raise RuntimeError("Could not read source image.")

gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
height, width = gray.shape

print("\nSource image:", image_path)
print("Dimensions:", width, "x", height)

with PHASE45.open(newline="") as f:
    phase45_rows = list(csv.DictReader(f))

with PHASE37.open(newline="") as f:
    phase37_rows = list(csv.DictReader(f))

# Select the four largest withheld R2C2 residuals.
suspects = [
    row for row in phase45_rows
    if row["section"] == "R2C2"
    and float(row["residual_px"]) > 10.0
]

suspects.sort(
    key=lambda row: float(row["residual_px"]),
    reverse=True
)

if len(suspects) != 4:
    raise RuntimeError(
        f"Expected 4 R2C2 points above 10 px; found {len(suspects)}"
    )

# Match each Phase 45 point to its Phase 37 catalogue correspondence.
def find_phase37_match(point):
    x = float(point["global_x"]) - 640
    y = float(point["global_y"]) - 480

    matches = [
        row for row in phase37_rows
        if row["section"] == "R2C2"
        and abs(float(row["candidate_x_local"]) - x) < 0.002
        and abs(float(row["candidate_y_local"]) - y) < 0.002
    ]

    if len(matches) != 1:
        raise RuntimeError(
            f"Could not uniquely match Phase 37 point at local ({x}, {y})"
        )

    return matches[0]

records = []
patches = []

for number, point in enumerate(suspects, start=1):
    global_x = float(point["global_x"])
    global_y = float(point["global_y"])
    local_x = global_x - 640
    local_y = global_y - 480

    match = find_phase37_match(point)

    x0 = max(0, int(round(global_x)) - CROP_RADIUS)
    x1 = min(width, int(round(global_x)) + CROP_RADIUS + 1)
    y0 = max(0, int(round(global_y)) - CROP_RADIUS)
    y1 = min(height, int(round(global_y)) + CROP_RADIUS + 1)

    patch = gray[y0:y1, x0:x1].astype(np.float64)

    # Estimate background from the outer ring of the crop.
    border = np.concatenate([
        patch[0, :], patch[-1, :],
        patch[:, 0], patch[:, -1]
    ])
    background = float(np.median(border))
    noise_mad = float(np.median(np.abs(border - background)))
    noise_sigma = 1.4826 * noise_mad

    peak = float(np.max(patch))
    peak_y, peak_x = np.unravel_index(np.argmax(patch), patch.shape)

    # Background-subtracted weighted centroid in a  nine-by-nine window.
    px = int(round(global_x))
    py = int(round(global_y))

    xa, xb = max(0, px - 4), min(width, px + 5)
    ya, yb = max(0, py - 4), min(height, py + 5)

    window = gray[ya:yb, xa:xb].astype(np.float64)
    weights = np.maximum(window - background, 0.0)

    total_weight = float(np.sum(weights))

    if total_weight > 0:
        yy, xx = np.indices(window.shape)
        centroid_x = float(np.sum((xx + xa) * weights) / total_weight)
        centroid_y = float(np.sum((yy + ya) * weights) / total_weight)
        centroid_shift = float(
            np.hypot(centroid_x - global_x, centroid_y - global_y)
        )
    else:
        centroid_x = None
        centroid_y = None
        centroid_shift = None

    # Local signal-to-noise estimate.
    if noise_sigma > 0:
        snr = (peak - background) / noise_sigma
    else:
        snr = None

    record = {
        "point_number": number,
        "section": "R2C2",
        "global_x": global_x,
        "global_y": global_y,
        "local_x": local_x,
        "local_y": local_y,
        "phase45_global_residual_px": float(point["residual_px"]),
        "hip_ra_deg": float(match["hip_ra_deg"]),
        "hip_dec_deg": float(match["hip_dec_deg"]),
        "phase37_local_wcs_residual_px": float(match["pixel_residual"]),
        "background_median": background,
        "border_noise_sigma_robust": noise_sigma,
        "peak_intensity": peak,
        "peak_minus_background": peak - background,
        "estimated_peak_snr": snr,
        "weighted_centroid_x": centroid_x,
        "weighted_centroid_y": centroid_y,
        "centroid_shift_from_detection_px": centroid_shift,
        "peak_position_x_global": x0 + int(peak_x),
        "peak_position_y_global": y0 + int(peak_y),
    }

    records.append(record)

    # Colour crop with detected point and measured peak marked.
    crop_bgr = image_bgr[y0:y1, x0:x1].copy()
    crop_rgb = cv2.cvtColor(crop_bgr, cv2.COLOR_BGR2RGB)

    patches.append({
        "number": number,
        "crop": crop_rgb,
        "x0": x0,
        "y0": y0,
        "global_x": global_x,
        "global_y": global_y,
        "peak_x": x0 + int(peak_x),
        "peak_y": y0 + int(peak_y),
        "record": record,
    })

    print(f"\nSTAR {number}")
    print(f"  Global position: ({global_x:.3f}, {global_y:.3f})")
    print(f"  Catalogue RA/Dec: {match['hip_ra_deg']}, {match['hip_dec_deg']}")
    print(f"  Phase 37 WCS residual: {float(match['pixel_residual']):.3f}px")
    print(f"  Phase 45 global residual: {float(point['residual_px']):.3f}px")
    print(f"  Background: {background:.2f}")
    print(f"  Peak intensity: {peak:.2f}")
    print(f"  Estimated peak SNR: {snr}")
    print(f"  Weighted centroid: ({centroid_x}, {centroid_y})")
    print(f"  Centroid shift: {centroid_shift}px")

# Save numerical audit.
csv_path = OUT / "phase46_four_star_measurements.csv"

with csv_path.open("w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=list(records[0].keys()))
    writer.writeheader()
    writer.writerows(records)

# Save four individual enlarged crops.
fig, axes = plt.subplots(2, 2, figsize=(12, 11))

for ax, item in zip(axes.ravel(), patches):
    ax.imshow(item["crop"])

    detected_x = item["global_x"] - item["x0"]
    detected_y = item["global_y"] - item["y0"]

    peak_x = item["peak_x"] - item["x0"]
    peak_y = item["peak_y"] - item["y0"]

    ax.scatter(
        [detected_x], [detected_y],
        marker="+", s=150, linewidths=2,
        label="Detected candidate"
    )
    ax.scatter(
        [peak_x], [peak_y],
        marker="x", s=100, linewidths=2,
        label="Brightest pixel"
    )

    centroid_x = item["record"]["weighted_centroid_x"]
    centroid_y = item["record"]["weighted_centroid_y"]

    if centroid_x is not None:
        ax.scatter(
            [centroid_x - item["x0"]],
            [centroid_y - item["y0"]],
            marker="o", s=65, facecolors="none",
            label="Weighted centroid"
        )

    ax.set_title(
        f"Star {item['number']} | "
        f"Global residual {item['record']['phase45_global_residual_px']:.2f}px"
    )
    ax.legend(fontsize=8)
    ax.axis("off")

fig.suptitle(
    "ASK033 R2C2 — Four suspicious star detections",
    fontsize=14
)
fig.tight_layout()

montage_path = OUT / "phase46_four_star_crops.png"
fig.savefig(montage_path, dpi=200)
plt.close(fig)

# Save a full-image locator showing all four points.
fig, ax = plt.subplots(figsize=(12, 8))
ax.imshow(cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB))

for item in patches:
    ax.scatter(
        [item["global_x"]],
        [item["global_y"]],
        s=110,
        marker="x",
        label=f"Star {item['number']}"
    )
    ax.annotate(
        str(item["number"]),
        (item["global_x"], item["global_y"]),
        xytext=(8, 8),
        textcoords="offset points",
        color="yellow",
        fontsize=12
    )

ax.set_title("ASK033 — Locations of four high-residual correspondences")
ax.set_xlim(0, width)
ax.set_ylim(height, 0)
ax.legend()
fig.tight_layout()

locator_path = OUT / "phase46_full_image_locator.png"
fig.savefig(locator_path, dpi=180)
plt.close(fig)

report = {
    "phase": 46,
    "source_image": str(image_path),
    "image_dimensions": [width, height],
    "investigated_points": len(records),
    "method": (
        "Image crop inspection, border-median background estimation, "
        "robust border-noise estimate, local peak intensity and "
        "9x9 background-subtracted weighted centroid"
    ),
    "points": records,
    "limitations": [
        "Peak SNR is an approximate local image statistic, not a calibrated photometric SNR.",
        "A local weighted centroid can be biased by nearby stars, clouds, gradients and saturation.",
        "Visual and centroid measurements alone cannot prove a catalogue identity.",
    ],
}

report_path = BASE / "phase46_four_star_investigation_report.json"

with report_path.open("w") as f:
    json.dump(report, f, indent=2)

print("\n" + "=" * 70)
print("PHASE 46 COMPLETED SUCCESSFULLY")
print("=" * 70)
print("Source image:", image_path)
print("Measurements:", csv_path)
print("Four-star crop montage:", montage_path)
print("Full-image locator:", locator_path)
print("JSON report:", report_path)
