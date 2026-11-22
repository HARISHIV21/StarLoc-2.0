from pathlib import Path
import csv
import json
import cv2
import numpy as np

BASE = Path("research/real_image")
ROOT = BASE / "results/ASK033"
OUT = ROOT / "phase51_correspondence_verification"
OUT.mkdir(parents=True, exist_ok=True)

audit_path = ROOT / "phase50_r2c2_spatial_correction/phase50_correction_point_audit.csv"
image_path = BASE / "data/network/ASK033/ASK033_live_grayscale.png"

if not audit_path.exists():
    raise FileNotFoundError(audit_path)
if not image_path.exists():
    raise FileNotFoundError(image_path)

with audit_path.open(newline="") as f:
    rows = list(csv.DictReader(f))

if not rows:
    raise RuntimeError("Phase 50 point audit is empty.")

print("=" * 72)
print("STARLOC 2.0 — PHASE 51")
print("R2C2 IMAGE-BASED CORRESPONDENCE VERIFICATION")
print("=" * 72)

print("\nPhase 50 CSV columns:")
print(", ".join(rows[0].keys()))

def find_column(names):
    normalized = {k.lower().replace(" ", "_"): k for k in rows[0]}
    for name in names:
        if name in normalized:
            return normalized[name]
    return None

x_col = find_column(["x", "global_x", "candidate_x", "global_x_px"])
y_col = find_column(["y", "global_y", "candidate_y", "global_y_px"])

if x_col is None or y_col is None:
    raise RuntimeError(
        "Could not identify candidate coordinate columns. "
        f"Available columns: {list(rows[0].keys())}"
    )

# The four diagnostic points are the rows with the largest baseline residuals.
error_col = find_column([
    "baseline_error_px", "baseline", "baseline_residual_px",
    "global_error_px", "baseline_error"
])

if error_col:
    rows.sort(key=lambda r: float(r[error_col]), reverse=True)
    diagnostic = rows[:4]
else:
    # If the audit contains only the four diagnostic rows, use all of them.
    diagnostic = rows
    if len(diagnostic) != 4:
        raise RuntimeError(
            "No baseline-error column found and the CSV does not contain "
            f"exactly four rows. Found {len(rows)} rows."
        )

image = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)
if image is None:
    raise RuntimeError(f"Could not load image: {image_path}")

height, width = image.shape
records = []
marked = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

def local_peaks(img, x, y, radius=35, max_peaks=12):
    x0, x1 = max(0, x-radius), min(width, x+radius+1)
    y0, y1 = max(0, y-radius), min(height, y+radius+1)
    crop = img[y0:y1, x0:x1]

    # Local maxima, with a small neighbourhood to suppress duplicate peaks.
    dilated = cv2.dilate(crop, np.ones((5, 5), np.uint8))
    mask = (crop == dilated) & (crop >= np.percentile(crop, 90))
    yy, xx = np.where(mask)

    peaks = []
    for py, px in zip(yy, xx):
        gx, gy = x0 + int(px), y0 + int(py)
        distance = float(np.hypot(gx-x, gy-y))
        peaks.append({
            "x": gx,
            "y": gy,
            "intensity": int(img[gy, gx]),
            "distance_from_candidate_px": round(distance, 3),
        })

    peaks.sort(key=lambda p: (-p["intensity"], p["distance_from_candidate_px"]))

    # Keep spatially distinct peaks.
    selected = []
    for p in peaks:
        if all(np.hypot(p["x"]-q["x"], p["y"]-q["y"]) >= 5 for q in selected):
            selected.append(p)
        if len(selected) >= max_peaks:
            break
    return selected

for index, row in enumerate(diagnostic, 1):
    x = int(round(float(row[x_col])))
    y = int(round(float(row[y_col])))

    peaks = local_peaks(image, x, y)
    background_crop = image[
        max(0, y-25):min(height, y+26),
        max(0, x-25):min(width, x+26)
    ]

    background = float(np.median(background_crop))
    noise = float(1.4826 * np.median(np.abs(background_crop-background)))
    candidate_intensity = int(image[y, x])
    approximate_snr = (
        (candidate_intensity-background)/noise if noise > 0 else None
    )

    record = {
        "point_number": index,
        "candidate_x": x,
        "candidate_y": y,
        "candidate_intensity": candidate_intensity,
        "local_background_median": round(background, 3),
        "local_noise_mad_estimate": round(noise, 3),
        "approximate_snr": (
            round(approximate_snr, 3) if approximate_snr is not None else None
        ),
        "phase50_source_row": row,
        "nearby_image_peaks": peaks,
    }
    records.append(record)

    cv2.circle(marked, (x, y), 9, (0, 0, 255), 2)
    cv2.putText(
        marked, f"P{index}", (x+10, y-8),
        cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 0, 255), 2
    )

    for peak in peaks[:5]:
        cv2.circle(marked, (peak["x"], peak["y"]), 4, (0, 255, 255), 1)

    print(f"\nPOINT {index}: candidate=({x}, {y})")
    print("  Intensity:", candidate_intensity)
    print("  Local background:", round(background, 2))
    print("  Approximate SNR:", record["approximate_snr"])
    print("  Nearby distinct intensity peaks:")
    for peak in peaks[:8]:
        print(
            f"    ({peak['x']:4d}, {peak['y']:4d}) "
            f"intensity={peak['intensity']:3d}, "
            f"distance={peak['distance_from_candidate_px']:.2f}px"
        )

json_path = BASE / "phase51_correspondence_verification_report.json"
with json_path.open("w") as f:
    json.dump({
        "phase": 51,
        "image": str(image_path),
        "source_audit": str(audit_path),
        "diagnostic_points": records,
        "limitations": [
            "Image intensity peaks are not automatically confirmed stars.",
            "Approximate SNR uses local median and MAD, not calibrated photometry.",
            "This phase does not independently establish Hipparcos identities.",
            "The four points were selected from Phase 50 diagnostic residuals."
        ]
    }, f, indent=2)

overlay_path = OUT / "phase51_four_point_peak_overlay.jpg"
cv2.imwrite(str(overlay_path), marked)

print("\n" + "=" * 72)
print("PHASE 51 COMPLETED")
print("=" * 72)
print("Report:", json_path)
print("Image overlay:", overlay_path)
print("Original calibration and Phase 50 files preserved.")
