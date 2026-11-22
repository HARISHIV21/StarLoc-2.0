import csv
import json
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial.transform import Rotation

BASE = Path("research/real_image")
RESULTS = BASE / "results/ASK033"

PHASE37 = RESULTS / "phase37_validation/phase37_all_matches.csv"
PHASE41 = RESULTS / "phase41_sensitivity/phase41_residual_comparison.csv"
REPORT38 = BASE / "phase38_global_calibration_report.json"
REPORT41 = BASE / "phase41_calibration_sensitivity_report.json"

OUT = RESULTS / "phase43_r2c2_investigation"
OUT.mkdir(parents=True, exist_ok=True)

WIDTH, HEIGHT = 1920, 1440
SECTION = "R2C2"
OFFSET_X, OFFSET_Y = 640, 480

def read_csv(path):
    if not path.exists():
        raise FileNotFoundError(path)
    with path.open(newline="") as f:
        return list(csv.DictReader(f))

def read_json(path):
    if not path.exists():
        raise FileNotFoundError(path)
    with path.open() as f:
        return json.load(f)

phase37 = read_csv(PHASE37)
phase41 = read_csv(PHASE41)
report38 = read_json(REPORT38)
report41 = read_json(REPORT41)

# Match records by section and rounded global pixel coordinates.
phase41_lookup = {}
for row in phase41:
    key = (
        row["section"],
        round(float(row["global_x"]), 3),
        round(float(row["global_y"]), 3),
    )
    phase41_lookup[key] = row

matches = []

for row in phase37:
    if row["section"] != SECTION:
        continue

    local_x = float(row["candidate_x_local"])
    local_y = float(row["candidate_y_local"])
    global_x = local_x + OFFSET_X
    global_y = local_y + OFFSET_Y

    key = (SECTION, round(global_x, 3), round(global_y, 3))

    if key not in phase41_lookup:
        raise RuntimeError(f"Missing Phase 41 correspondence: {key}")

    matches.append({
        "section": SECTION,
        "local_x": local_x,
        "local_y": local_y,
        "global_x": global_x,
        "global_y": global_y,
        "ra": float(row["hip_ra_deg"]),
        "dec": float(row["hip_dec_deg"]),
        "local_wcs_residual": float(row["pixel_residual"]),
        "phase41_row": phase41_lookup[key],
    })

if len(matches) != 51:
    raise RuntimeError(
        f"Expected 51 R2C2 correspondences, found {len(matches)}"
    )

def model_parameters(report, branch=None):
    if branch is None:
        p = report["parameters"]
    else:
        p = report[branch]["parameters"]

    return {
        "rotation": Rotation.from_matrix(
            np.asarray(p["rotation_matrix_world_to_camera"], dtype=float)
        ),
        "cx": float(p["optical_centre_x_px"]),
        "cy": float(p["optical_centre_y_px"]),
        "focal": float(p["focal_scale_px_per_rad"]),
        "k1": float(p["radial_k1"]),
        "k2": float(p["radial_k2"]),
    }

models = {
    "phase38": model_parameters(report38),
    "phase41": model_parameters(report41, "filtered"),
}

def project_one(ra_deg, dec_deg, params):
    ra = np.deg2rad(ra_deg)
    dec = np.deg2rad(dec_deg)

    vector = np.array([
        np.cos(dec) * np.cos(ra),
        np.cos(dec) * np.sin(ra),
        np.sin(dec),
    ])

    camera = params["rotation"].apply(vector)
    z = camera[2]
    rho = np.hypot(camera[0], camera[1])
    theta = np.arctan2(rho, z)

    radial = params["focal"] * (
        theta
        + params["k1"] * theta**3
        + params["k2"] * theta**5
    )

    safe_rho = max(rho, 1e-12)
    predicted_x = params["cx"] + radial * camera[0] / safe_rho
    predicted_y = params["cy"] + radial * camera[1] / safe_rho

    return np.array([predicted_x, predicted_y]), float(z)

# Calculate signed residual vectors.
for item in matches:
    observed = np.array([item["global_x"], item["global_y"]])

    for model_name, params in models.items():
        predicted, z = project_one(item["ra"], item["dec"], params)
        delta = predicted - observed

        item[model_name + "_predicted_x"] = float(predicted[0])
        item[model_name + "_predicted_y"] = float(predicted[1])
        item[model_name + "_dx"] = float(delta[0])
        item[model_name + "_dy"] = float(delta[1])
        item[model_name + "_error"] = float(np.linalg.norm(delta))
        item[model_name + "_front_facing"] = bool(z > 0)

    item["phase41_excluded"] = (
        item["phase41_row"]["excluded_from_filtered_training"]
        .strip().lower() == "true"
    )

def summary(values):
    values = np.asarray(values, dtype=float)
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

def vector_statistics(items, prefix):
    dx = np.array([r[prefix + "_dx"] for r in items])
    dy = np.array([r[prefix + "_dy"] for r in items])
    errors = np.array([r[prefix + "_error"] for r in items])

    return {
        "residuals": summary(errors),
        "mean_signed_dx_px": float(np.mean(dx)),
        "mean_signed_dy_px": float(np.mean(dy)),
        "median_signed_dx_px": float(np.median(dx)),
        "median_signed_dy_px": float(np.median(dy)),
        "mean_vector_magnitude_px": float(
            np.hypot(np.mean(dx), np.mean(dy))
        ),
        "front_facing_count": int(sum(
            r[prefix + "_front_facing"] for r in items
        )),
    }

# Analyse upper/middle/lower regions of the R2C2 tile.
vertical_bands = [
    ("upper", 0, 160),
    ("middle", 160, 320),
    ("lower", 320, 480),
]

band_report = {}

for name, low, high in vertical_bands:
    subset = [
        r for r in matches
        if low <= r["local_y"] < high
    ]

    if not subset:
        band_report[name] = {"count": 0}
        continue

    band_report[name] = {
        "local_y_range_px": [low, high],
        "count": len(subset),
        "local_wcs": summary([
            r["local_wcs_residual"] for r in subset
        ]),
        "phase38": vector_statistics(subset, "phase38"),
        "phase41": vector_statistics(subset, "phase41"),
    }

# Analyse previously excluded points separately.
excluded_points = [
    r for r in matches if r["phase41_excluded"]
]
retained_points = [
    r for r in matches if not r["phase41_excluded"]
]

excluded_report = {
    "excluded_count": len(excluded_points),
    "excluded_points": [
        {
            "local_x": r["local_x"],
            "local_y": r["local_y"],
            "local_wcs_residual_px": r["local_wcs_residual"],
            "phase38_global_residual_px": r["phase38_error"],
            "phase41_global_residual_px": r["phase41_error"],
        }
        for r in excluded_points
    ],
    "excluded_local_wcs": summary([
        r["local_wcs_residual"] for r in excluded_points
    ]) if excluded_points else None,
    "excluded_phase38": summary([
        r["phase38_error"] for r in excluded_points
    ]) if excluded_points else None,
    "excluded_phase41": summary([
        r["phase41_error"] for r in excluded_points
    ]) if excluded_points else None,
    "retained_phase38": summary([
        r["phase38_error"] for r in retained_points
    ]) if retained_points else None,
    "retained_phase41": summary([
        r["phase41_error"] for r in retained_points
    ]) if retained_points else None,
}

# Section-wide statistics.
local_wcs_stats = summary([
    r["local_wcs_residual"] for r in matches
])
phase38_stats = vector_statistics(matches, "phase38")
phase41_stats = vector_statistics(matches, "phase41")

# Compare signed residual directions with local tile coordinates.
def correlation(a, b):
    if len(a) < 3 or np.std(a) == 0 or np.std(b) == 0:
        return None
    return float(np.corrcoef(a, b)[0, 1])

local_x = np.array([r["local_x"] for r in matches])
local_y = np.array([r["local_y"] for r in matches])

spatial_correlations = {}
for prefix in ["phase38", "phase41"]:
    dx = np.array([r[prefix + "_dx"] for r in matches])
    dy = np.array([r[prefix + "_dy"] for r in matches])
    error = np.array([r[prefix + "_error"] for r in matches])

    spatial_correlations[prefix] = {
        "local_y_vs_dx": correlation(local_y, dx),
        "local_y_vs_dy": correlation(local_y, dy),
        "local_y_vs_error": correlation(local_y, error),
        "local_x_vs_dx": correlation(local_x, dx),
        "local_x_vs_dy": correlation(local_x, dy),
        "local_x_vs_error": correlation(local_x, error),
    }

# Save detailed point-level audit.
csv_path = OUT / "phase43_r2c2_point_audit.csv"

with csv_path.open("w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow([
        "local_x", "local_y", "global_x", "global_y",
        "ra_deg", "dec_deg",
        "local_wcs_residual_px",
        "phase38_dx_px", "phase38_dy_px", "phase38_error_px",
        "phase41_dx_px", "phase41_dy_px", "phase41_error_px",
        "excluded_from_phase41_training",
    ])

    for r in matches:
        writer.writerow([
            r["local_x"], r["local_y"],
            r["global_x"], r["global_y"],
            r["ra"], r["dec"],
            r["local_wcs_residual"],
            r["phase38_dx"], r["phase38_dy"], r["phase38_error"],
            r["phase41_dx"], r["phase41_dy"], r["phase41_error"],
            r["phase41_excluded"],
        ])

# Plot 1: residual vectors on R2C2 local tile.
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

for ax, prefix, title in [
    (axes[0], "phase38", "Phase 38 baseline"),
    (axes[1], "phase41", "Phase 41 filtered"),
]:
    px = np.array([r["local_x"] for r in matches])
    py = np.array([r["local_y"] for r in matches])
    dx = np.array([r[prefix + "_dx"] for r in matches])
    dy = np.array([r[prefix + "_dy"] for r in matches])
    errors = np.array([r[prefix + "_error"] for r in matches])

    normal = ~np.array([r["phase41_excluded"] for r in matches])
    outlier = ~normal

    ax.scatter(
        px[normal], py[normal],
        c=errors[normal], s=28, alpha=0.8
    )
    if np.any(outlier):
        ax.scatter(
            px[outlier], py[outlier],
            marker="x", s=65, label="Phase 41 excluded"
        )

    # Arrow directions are predicted minus observed pixel coordinates.
    # A common display scale keeps direction visible without changing data.
    arrow_scale = 4.0
    ax.quiver(
        px, py, dx, dy,
        angles="xy", scale_units="xy", scale=arrow_scale,
        color="black", alpha=0.65, width=0.003
    )

    ax.set_xlim(0, 640)
    ax.set_ylim(480, 0)
    ax.set_aspect("equal")
    ax.set_xlabel("R2C2 local X (pixels)")
    ax.set_ylabel("R2C2 local Y (pixels)")
    ax.set_title(title)
    ax.grid(True, alpha=0.2)
    if np.any(outlier):
        ax.legend()

fig.suptitle("R2C2 — signed global-model residual vectors")
fig.tight_layout()
fig.savefig(OUT / "phase43_r2c2_residual_vectors.png", dpi=180)
plt.close(fig)

# Plot 2: local WCS residual versus global model residual.
fig, ax = plt.subplots(figsize=(8, 6))

for r in matches:
    marker = "x" if r["phase41_excluded"] else "o"
    ax.scatter(
        r["local_wcs_residual"],
        r["phase38_error"],
        marker=marker,
        s=55 if marker == "x" else 30,
        alpha=0.8,
    )

ax.set_xlabel("Phase 37 local WCS residual (pixels)")
ax.set_ylabel("Phase 38 global-model residual (pixels)")
ax.set_title("R2C2 — local WCS versus global calibration residual")
ax.grid(True, alpha=0.25)
fig.tight_layout()
fig.savefig(OUT / "phase43_local_vs_global_residuals.png", dpi=180)
plt.close(fig)

# Plot 3: residual magnitude against vertical position.
fig, ax = plt.subplots(figsize=(9, 6))

ax.scatter(
    local_y,
    [r["phase38_error"] for r in matches],
    label="Phase 38",
    alpha=0.75,
)
ax.scatter(
    local_y,
    [r["phase41_error"] for r in matches],
    label="Phase 41",
    alpha=0.75,
)
ax.set_xlabel("R2C2 local Y (pixels; top to bottom)")
ax.set_ylabel("Global-model residual magnitude (pixels)")
ax.set_title("R2C2 — residuals by vertical image position")
ax.grid(True, alpha=0.25)
ax.legend()
fig.tight_layout()
fig.savefig(OUT / "phase43_vertical_residual_distribution.png", dpi=180)
plt.close(fig)

report = {
    "phase": 43,
    "title": "R2C2 correspondence investigation",
    "section": SECTION,
    "correspondence_count": len(matches),
    "tile_dimensions_px": [640, 480],
    "global_tile_offset_px": [OFFSET_X, OFFSET_Y],
    "residual_vector_definition": (
        "Predicted global pixel coordinate minus observed global pixel coordinate."
    ),
    "local_wcs_statistics": local_wcs_stats,
    "phase38_global_statistics": phase38_stats,
    "phase41_global_statistics": phase41_stats,
    "vertical_band_analysis": band_report,
    "previously_excluded_points": excluded_report,
    "spatial_correlations": spatial_correlations,
    "interpretation_limits": [
        "Local WCS residuals and global-model residuals are not independent measurements.",
        "The Phase 37 local WCS residual is a pixel-space nearest-match residual.",
        "Residual vector direction can reveal systematic disagreement but does not alone identify its cause.",
        "The investigation does not establish whether the source is optical distortion, WCS error, or correspondence error.",
    ],
}

report_path = BASE / "phase43_r2c2_investigation_report.json"
with report_path.open("w") as f:
    json.dump(report, f, indent=2)

print("=" * 70)
print("STARLOC 2.0 — PHASE 43")
print("R2C2 CORRESPONDENCE INVESTIGATION")
print("=" * 70)

print("\nR2C2 CORRESPONDENCE COUNT:", len(matches))

print("\nLOCAL WCS RESIDUALS")
for key, value in local_wcs_stats.items():
    print(f"  {key}: {value}")

print("\nPHASE 38 GLOBAL MODEL")
for key, value in phase38_stats.items():
    print(f"  {key}: {value}")

print("\nPHASE 41 GLOBAL MODEL")
for key, value in phase41_stats.items():
    print(f"  {key}: {value}")

print("\nVERTICAL BAND ANALYSIS")
for band, result in band_report.items():
    print(f"\n  {band.upper()} — n={result['count']}")
    if result["count"]:
        print(
            "    Local WCS median:",
            f"{result['local_wcs']['median_px']:.3f}px"
        )
        print(
            "    Phase 38 median:",
            f"{result['phase38']['residuals']['median_px']:.3f}px"
        )
        print(
            "    Phase 41 median:",
            f"{result['phase41']['residuals']['median_px']:.3f}px"
        )

print("\nPREVIOUSLY EXCLUDED POINTS")
print("  Count:", excluded_report["excluded_count"])
print("  Local WCS:", excluded_report["excluded_local_wcs"])
print("  Phase 38:", excluded_report["excluded_phase38"])
print("  Phase 41:", excluded_report["excluded_phase41"])

print("\nSPATIAL CORRELATIONS")
for model, values in spatial_correlations.items():
    print(f"  {model}:")
    for key, value in values.items():
        print(f"    {key}: {value}")

print("\nOUTPUTS")
print("Report:", report_path)
print("Point audit:", csv_path)
print("Residual vectors:", OUT / "phase43_r2c2_residual_vectors.png")
print("Local/global comparison:", OUT / "phase43_local_vs_global_residuals.png")
print("Vertical distribution:", OUT / "phase43_vertical_residual_distribution.png")

print("\nPHASE 43 COMPLETED SUCCESSFULLY")
