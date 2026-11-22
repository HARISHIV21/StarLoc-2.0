import csv
import json
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from astropy.wcs import WCS

BASE = Path("research/real_image")
RESULTS = BASE / "results/ASK033"

INPUT37 = RESULTS / "phase37_validation/phase37_all_matches.csv"
INPUT41 = RESULTS / "phase41_sensitivity/phase41_residual_comparison.csv"
WCS_FILE = RESULTS / "custom_plate_solutions/R2C2_custom.wcs"

OUT = RESULTS / "phase44_direct_wcs_comparison"
OUT.mkdir(parents=True, exist_ok=True)

OFFSET_X, OFFSET_Y = 640, 480

def read_csv(path):
    if not path.exists():
        raise FileNotFoundError(path)
    with path.open(newline="") as f:
        return list(csv.DictReader(f))

def summary(values):
    values = np.asarray(values, dtype=float)
    values = values[np.isfinite(values)]
    if len(values) == 0:
        return {"count": 0}
    return {
        "count": int(len(values)),
        "median_px": float(np.median(values)),
        "mean_px": float(np.mean(values)),
        "rmse_px": float(np.sqrt(np.mean(values**2))),
        "p90_px": float(np.percentile(values, 90)),
        "max_px": float(np.max(values)),
        "over_2px": int(np.sum(values > 2)),
        "over_3px": int(np.sum(values > 3)),
        "over_5px": int(np.sum(values > 5)),
        "over_10px": int(np.sum(values > 10)),
    }

def corr(a, b):
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    valid = np.isfinite(a) & np.isfinite(b)
    a, b = a[valid], b[valid]
    if len(a) < 3 or np.std(a) == 0 or np.std(b) == 0:
        return None
    return float(np.corrcoef(a, b)[0, 1])

rows37 = [
    r for r in read_csv(INPUT37)
    if r["section"] == "R2C2"
]
rows41 = read_csv(INPUT41)

lookup41 = {}
for r in rows41:
    key = (
        r["section"],
        round(float(r["global_x"]), 3),
        round(float(r["global_y"]), 3),
    )
    lookup41[key] = r

if len(rows37) != 51:
    raise RuntimeError(f"Expected 51 R2C2 rows, found {len(rows37)}")

if not WCS_FILE.exists():
    raise FileNotFoundError(
        f"R2C2 WCS solution not found: {WCS_FILE}"
    )

print("Loading R2C2 local WCS:", WCS_FILE)
wcs = WCS(str(WCS_FILE))

if not wcs.has_celestial:
    raise RuntimeError("The supplied WCS file has no celestial WCS axes.")

ra = np.array([float(r["hip_ra_deg"]) for r in rows37])
dec = np.array([float(r["hip_dec_deg"]) for r in rows37])

observed_x = np.array([
    float(r["candidate_x_local"]) for r in rows37
])
observed_y = np.array([
    float(r["candidate_y_local"]) for r in rows37
])

# Directly project catalogue RA/Dec through the local R2C2 WCS.
# FITS pixel origin 0 matches the zero-based candidate coordinates.
try:
    local_predicted = wcs.all_world2pix(
        np.column_stack((ra, dec)),
        0,
        quiet=True,
    )
except TypeError:
    local_predicted = wcs.all_world2pix(
        np.column_stack((ra, dec)),
        0,
    )

local_dx = local_predicted[:, 0] - observed_x
local_dy = local_predicted[:, 1] - observed_y
local_error = np.hypot(local_dx, local_dy)

records = []

for i, row in enumerate(rows37):
    gx = observed_x[i] + OFFSET_X
    gy = observed_y[i] + OFFSET_Y
    key = ("R2C2", round(gx, 3), round(gy, 3))

    if key not in lookup41:
        raise RuntimeError(f"Phase 41 match missing for {key}")

    row41 = lookup41[key]

    # Phase 41 stores global-model predicted minus observed vectors.
    p38_error = float(row41["phase38_baseline_residual_px"])
    p41_error = float(row41["phase41_filtered_residual_px"])

    # Recover signed global model vectors from the saved global predictions.
    # The Phase 41 CSV stores magnitudes only, so obtain vectors by reusing
    # the exact Phase 38 and Phase 41 calibration reports below.
    records.append({
        "local_x": float(observed_x[i]),
        "local_y": float(observed_y[i]),
        "global_x": float(gx),
        "global_y": float(gy),
        "ra_deg": float(ra[i]),
        "dec_deg": float(dec[i]),
        "local_wcs_predicted_x": float(local_predicted[i, 0]),
        "local_wcs_predicted_y": float(local_predicted[i, 1]),
        "local_wcs_dx": float(local_dx[i]),
        "local_wcs_dy": float(local_dy[i]),
        "local_wcs_error": float(local_error[i]),
        "phase38_global_error": p38_error,
        "phase41_global_error": p41_error,
        "phase41_excluded": (
            row41["excluded_from_filtered_training"].strip().lower()
            == "true"
        ),
        "phase37_nearest_match_residual": float(row["pixel_residual"]),
    })

valid = np.array([
    np.isfinite(r["local_wcs_error"]) for r in records
])

if np.sum(valid) < 40:
    raise RuntimeError(
        f"Only {np.sum(valid)} of 51 WCS projections are valid. "
        "Inspect the WCS solution before drawing conclusions."
    )

valid_records = [r for r, ok in zip(records, valid) if ok]

# Analyse upper, middle and lower bands using direct WCS residuals.
bands = {
    "upper": (0, 160),
    "middle": (160, 320),
    "lower": (320, 480),
}

band_report = {}
for name, (lo, hi) in bands.items():
    subset = [
        r for r in valid_records
        if lo <= r["local_y"] < hi
    ]
    band_report[name] = {
        "count": len(subset),
        "direct_local_wcs": summary([
            r["local_wcs_error"] for r in subset
        ]),
        "phase38_global": summary([
            r["phase38_global_error"] for r in subset
        ]),
        "phase41_global": summary([
            r["phase41_global_error"] for r in subset
        ]),
    }

local_errors = np.array([
    r["local_wcs_error"] for r in valid_records
])
phase38_errors = np.array([
    r["phase38_global_error"] for r in valid_records
])
phase41_errors = np.array([
    r["phase41_global_error"] for r in valid_records
])

local_x = np.array([r["local_x"] for r in valid_records])
local_y = np.array([r["local_y"] for r in valid_records])

# Compare direct WCS error with global model error.
correlations = {
    "direct_local_wcs_vs_phase38_global": corr(
        local_errors, phase38_errors
    ),
    "direct_local_wcs_vs_phase41_global": corr(
        local_errors, phase41_errors
    ),
    "local_x_vs_direct_wcs_error": corr(local_x, local_errors),
    "local_y_vs_direct_wcs_error": corr(local_y, local_errors),
    "local_x_vs_phase38_global_error": corr(
        local_x, phase38_errors
    ),
    "local_y_vs_phase38_global_error": corr(
        local_y, phase38_errors
    ),
}

excluded = [
    r for r in valid_records if r["phase41_excluded"]
]
retained = [
    r for r in valid_records if not r["phase41_excluded"]
]

excluded_report = {
    "count": len(excluded),
    "direct_local_wcs": summary([
        r["local_wcs_error"] for r in excluded
    ]),
    "phase38_global": summary([
        r["phase38_global_error"] for r in excluded
    ]),
    "phase41_global": summary([
        r["phase41_global_error"] for r in excluded
    ]),
    "retained_count": len(retained),
    "retained_direct_local_wcs": summary([
        r["local_wcs_error"] for r in retained
    ]),
}

# Save point-level direct WCS audit.
csv_path = OUT / "phase44_direct_wcs_point_audit.csv"
with csv_path.open("w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow([
        "local_x", "local_y", "global_x", "global_y",
        "ra_deg", "dec_deg",
        "wcs_predicted_x", "wcs_predicted_y",
        "wcs_dx", "wcs_dy", "wcs_error_px",
        "phase37_nearest_match_residual_px",
        "phase38_global_error_px",
        "phase41_global_error_px",
        "phase41_excluded",
    ])

    for r in records:
        writer.writerow([
            r["local_x"], r["local_y"],
            r["global_x"], r["global_y"],
            r["ra_deg"], r["dec_deg"],
            r["local_wcs_predicted_x"],
            r["local_wcs_predicted_y"],
            r["local_wcs_dx"], r["local_wcs_dy"],
            r["local_wcs_error"],
            r["phase37_nearest_match_residual"],
            r["phase38_global_error"],
            r["phase41_global_error"],
            r["phase41_excluded"],
        ])

report = {
    "phase": 44,
    "title": "Direct local WCS versus global model comparison",
    "section": "R2C2",
    "total_correspondences": len(records),
    "valid_direct_wcs_projections": len(valid_records),
    "wcs_file": str(WCS_FILE),
    "pixel_origin": 0,
    "direct_local_wcs_error": summary(local_errors),
    "phase38_global_model_error": summary(phase38_errors),
    "phase41_global_model_error": summary(phase41_errors),
    "vertical_band_analysis": band_report,
    "excluded_point_analysis": excluded_report,
    "correlations": correlations,
    "interpretation_limits": [
        "The local WCS and global fisheye model are fitted from related catalogue information.",
        "The local WCS is not independent ground truth.",
        "Residual magnitudes do not by themselves identify the source of disagreement.",
        "WCS projection failures and points outside the local tile must be inspected.",
    ],
}

report_path = BASE / "phase44_direct_wcs_comparison_report.json"
with report_path.open("w") as f:
    json.dump(report, f, indent=2)

# Plot 1: direct local WCS versus global model errors.
fig, ax = plt.subplots(figsize=(8, 6))
normal = np.array([not r["phase41_excluded"] for r in valid_records])
outliers = ~normal

ax.scatter(
    local_errors[normal],
    phase38_errors[normal],
    label="Retained points",
    alpha=0.75,
)
if np.any(outliers):
    ax.scatter(
        local_errors[outliers],
        phase38_errors[outliers],
        marker="x",
        s=80,
        label="Phase 41 excluded",
    )

ax.set_xlabel("Direct local WCS residual (pixels)")
ax.set_ylabel("Phase 38 global-model residual (pixels)")
ax.set_title("R2C2 — direct local WCS versus global model")
ax.grid(True, alpha=0.25)
ax.legend()
fig.tight_layout()
fig.savefig(OUT / "phase44_local_vs_global.png", dpi=180)
plt.close(fig)

# Plot 2: direct WCS residual across tile coordinates.
fig, ax = plt.subplots(figsize=(9, 6))
sc = ax.scatter(
    local_x,
    local_y,
    c=local_errors,
    s=40,
)
ax.set_xlim(0, 640)
ax.set_ylim(480, 0)
ax.set_aspect("equal")
ax.set_xlabel("R2C2 local X (pixels)")
ax.set_ylabel("R2C2 local Y (pixels)")
ax.set_title("R2C2 — direct local WCS residual map")
fig.colorbar(sc, ax=ax, label="Direct WCS residual (pixels)")
fig.tight_layout()
fig.savefig(OUT / "phase44_direct_wcs_residual_map.png", dpi=180)
plt.close(fig)

# Plot 3: compare errors against local horizontal position.
fig, ax = plt.subplots(figsize=(9, 6))
ax.scatter(local_x, local_errors, label="Direct local WCS", alpha=0.75)
ax.scatter(local_x, phase38_errors, label="Phase 38 global model", alpha=0.75)
ax.set_xlabel("R2C2 local X (pixels)")
ax.set_ylabel("Residual magnitude (pixels)")
ax.set_title("R2C2 — horizontal residual distribution")
ax.grid(True, alpha=0.25)
ax.legend()
fig.tight_layout()
fig.savefig(OUT / "phase44_horizontal_residuals.png", dpi=180)
plt.close(fig)

print("=" * 70)
print("STARLOC 2.0 — PHASE 44")
print("DIRECT LOCAL WCS VS GLOBAL MODEL")
print("=" * 70)

print("\nVALID WCS PROJECTIONS:", len(valid_records), "/", len(records))

print("\nDIRECT LOCAL WCS")
print(summary(local_errors))

print("\nPHASE 38 GLOBAL MODEL")
print(summary(phase38_errors))

print("\nPHASE 41 GLOBAL MODEL")
print(summary(phase41_errors))

print("\nVERTICAL BAND COMPARISON")
for name, values in band_report.items():
    print(f"\n{name.upper()} — n={values['count']}")
    print("  Direct local WCS:", values["direct_local_wcs"])
    print("  Phase 38 global:", values["phase38_global"])
    print("  Phase 41 global:", values["phase41_global"])

print("\nFOUR PREVIOUSLY EXCLUDED POINTS")
print(excluded_report)

print("\nCORRELATIONS")
for key, value in correlations.items():
    print(f"  {key}: {value}")

print("\nOUTPUTS")
print("Report:", report_path)
print("Point audit:", csv_path)
print("Comparison plot:", OUT / "phase44_local_vs_global.png")
print("WCS residual map:", OUT / "phase44_direct_wcs_residual_map.png")
print("Horizontal plot:", OUT / "phase44_horizontal_residuals.png")

print("\nPHASE 44 COMPLETED SUCCESSFULLY")
