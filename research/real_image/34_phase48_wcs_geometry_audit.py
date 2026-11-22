import csv
import json
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from astropy.wcs import WCS
from astropy.wcs.utils import proj_plane_pixel_scales

BASE = Path("research/real_image")
RESULTS = BASE / "results/ASK033"
OUT = RESULTS / "phase48_wcs_geometry"
OUT.mkdir(parents=True, exist_ok=True)

SECTIONS = {
    "R1C2": (640, 0),
    "R2C1": (0, 480),
    "R2C2": (640, 480),
    "R3C1": (0, 960),
    "R3C2": (640, 960),
}

TILE_W, TILE_H = 640, 480

def find_wcs(section):
    candidates = list(RESULTS.rglob("*.wcs"))
    candidates = [
        p for p in candidates
        if section.lower() in p.stem.lower()
    ]

    if not candidates:
        raise FileNotFoundError(
            f"No WCS file found for {section} under {RESULTS}"
        )

    # Prefer the known custom R2C2 plate solution.
    if section == "R2C2":
        preferred = [
            p for p in candidates
            if p.name == "R2C2_custom.wcs"
        ]
        if preferred:
            return preferred[0]

    # Prefer exact section filename over names with extra suffixes.
    exact = [p for p in candidates if p.stem == section]
    if exact:
        candidates = exact

    if len(candidates) > 1:
        print(f"\nMultiple WCS files found for {section}:")
        for p in candidates:
            print(" ", p)
        raise RuntimeError(
            f"Ambiguous WCS file for {section}; resolve before continuing."
        )

    return candidates[0]

def angular_separation(ra1, dec1, ra2, dec2):
    a1, d1, a2, d2 = np.deg2rad([ra1, dec1, ra2, dec2])
    cosine = (
        np.sin(d1) * np.sin(d2)
        + np.cos(d1) * np.cos(d2) * np.cos(a1 - a2)
    )
    return float(np.rad2deg(np.arccos(np.clip(cosine, -1, 1))))

def inspect_section(section, offset):
    path = find_wcs(section)
    wcs = WCS(str(path)).celestial

    if not wcs.has_celestial:
        raise RuntimeError(f"{section} WCS has no celestial axes")

    # Pixel scale and local tangent-plane transformation matrix.
    scales = proj_plane_pixel_scales(wcs) * 3600.0
    matrix = np.asarray(wcs.pixel_scale_matrix, dtype=float)
    determinant = float(np.linalg.det(matrix))

    # Pixel centre and celestial coordinates.
    centre_x = (TILE_W - 1) / 2
    centre_y = (TILE_H - 1) / 2
    centre = wcs.pixel_to_world(centre_x, centre_y)

    ra = float(centre.ra.deg)
    dec = float(centre.dec.deg)

    # Four corners of the tile.
    corner_pixels = np.array([
        [0, 0],
        [TILE_W - 1, 0],
        [TILE_W - 1, TILE_H - 1],
        [0, TILE_H - 1],
    ])

    corners = wcs.pixel_to_world(
        corner_pixels[:, 0],
        corner_pixels[:, 1]
    )

    corner_data = [
        {
            "ra_deg": float(r),
            "dec_deg": float(d),
        }
        for r, d in zip(corners.ra.deg, corners.dec.deg)
    ]

    # Orientation of the positive image X direction in the local
    # tangent plane. This is a diagnostic angle, not a universal
    # camera roll convention.
    x_angle = float(
        np.rad2deg(np.arctan2(matrix[1, 0], matrix[0, 0]))
    )

    # Global image position of the local tile centre.
    ox, oy = offset

    ctype = list(wcs.wcs.ctype)
    cunit = [str(unit) for unit in wcs.wcs.cunit]

    return {
        "section": section,
        "file": str(path),
        "tile_offset_global_px": [ox, oy],
        "tile_dimensions_px": [TILE_W, TILE_H],
        "centre_ra_deg": ra,
        "centre_dec_deg": dec,
        "pixel_scale_x_arcsec": float(scales[0]),
        "pixel_scale_y_arcsec": float(scales[1]),
        "pixel_scale_mean_arcsec": float(np.mean(scales)),
        "pixel_scale_difference_percent": float(
            abs(scales[0] - scales[1]) / np.mean(scales) * 100
        ),
        "pixel_scale_matrix_deg_per_pixel": matrix.tolist(),
        "matrix_determinant": determinant,
        "parity": "positive" if determinant > 0 else "negative",
        "local_x_axis_angle_deg": x_angle,
        "projection_type": ctype,
        "coordinate_units": cunit,
        "has_sip_distortion": bool(wcs.sip is not None),
        "corner_coordinates": corner_data,
        "angular_field_diagonal_deg": angular_separation(
            corner_data[0]["ra_deg"],
            corner_data[0]["dec_deg"],
            corner_data[2]["ra_deg"],
            corner_data[2]["dec_deg"],
        ),
    }

print("=" * 72)
print("STARLOC 2.0 — PHASE 48")
print("FIVE-SECTION WCS GEOMETRY AUDIT")
print("=" * 72)

results = {}

for section, offset in SECTIONS.items():
    print(f"\nInspecting {section}...")
    result = inspect_section(section, offset)
    results[section] = result

    print("  File:", result["file"])
    print(
        "  Field centre:",
        f"RA={result['centre_ra_deg']:.6f}°",
        f"Dec={result['centre_dec_deg']:.6f}°"
    )
    print(
        "  Pixel scale:",
        f"{result['pixel_scale_x_arcsec']:.3f} x",
        f"{result['pixel_scale_y_arcsec']:.3f} arcsec/pixel"
    )
    print("  Parity:", result["parity"])
    print("  X-axis angle:", f"{result['local_x_axis_angle_deg']:.4f}°")
    print("  Projection:", result["projection_type"])
    print("  SIP distortion:", result["has_sip_distortion"])

# Compare section centres and pixel scales.
reference = results["R2C2"]
comparisons = {}

for section, result in results.items():
    comparisons[section] = {
        "centre_separation_from_R2C2_deg": angular_separation(
            reference["centre_ra_deg"],
            reference["centre_dec_deg"],
            result["centre_ra_deg"],
            result["centre_dec_deg"],
        ),
        "scale_difference_from_R2C2_percent": float(
            (
                result["pixel_scale_mean_arcsec"]
                / reference["pixel_scale_mean_arcsec"] - 1
            ) * 100
        ),
        "same_parity_as_R2C2": (
            result["parity"] == reference["parity"]
        ),
    }

# Pairwise centre separations.
pairwise = {}

names = list(results)
for i, first in enumerate(names):
    for second in names[i + 1:]:
        a = results[first]
        b = results[second]
        pairwise[f"{first}_{second}"] = angular_separation(
            a["centre_ra_deg"], a["centre_dec_deg"],
            b["centre_ra_deg"], b["centre_dec_deg"]
        )

# Summary statistics.
scales = [
    r["pixel_scale_mean_arcsec"]
    for r in results.values()
]
parities = [r["parity"] for r in results.values()]
projections = [
    tuple(r["projection_type"])
    for r in results.values()
]

summary = {
    "section_count": len(results),
    "pixel_scale_mean_arcsec": float(np.mean(scales)),
    "pixel_scale_std_arcsec": float(np.std(scales)),
    "pixel_scale_min_arcsec": float(np.min(scales)),
    "pixel_scale_max_arcsec": float(np.max(scales)),
    "all_same_parity": len(set(parities)) == 1,
    "all_same_projection_type": len(set(projections)) == 1,
    "parities": parities,
    "projection_types": [list(p) for p in projections],
}

report = {
    "phase": 48,
    "title": "Five-section WCS geometry audit",
    "reference_section": "R2C2",
    "sections": results,
    "comparison_to_R2C2": comparisons,
    "pairwise_centre_separations_deg": pairwise,
    "summary": summary,
    "limitations": [
        "Local WCS solutions are not independent camera ground truth.",
        "A TAN plate solution over a crop does not establish the full fisheye projection.",
        "Local rotation angles must be interpreted with the WCS coordinate conventions.",
        "Differences can also arise from local plate-solving uncertainty.",
    ],
}

report_path = BASE / "phase48_wcs_geometry_report.json"
with report_path.open("w") as f:
    json.dump(report, f, indent=2)

# Save a concise CSV.
csv_path = OUT / "phase48_section_geometry.csv"
fields = [
    "section", "centre_ra_deg", "centre_dec_deg",
    "pixel_scale_x_arcsec", "pixel_scale_y_arcsec",
    "pixel_scale_mean_arcsec", "parity",
    "local_x_axis_angle_deg", "projection_type",
    "has_sip_distortion", "angular_field_diagonal_deg",
]

with csv_path.open("w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()

    for section, result in results.items():
        row = dict(result)
        row["projection_type"] = ",".join(result["projection_type"])
        writer.writerow({key: row[key] for key in fields})

# Pixel scale comparison plot.
fig, ax = plt.subplots(figsize=(9, 5))
labels = list(results)
x_scales = [results[s]["pixel_scale_x_arcsec"] for s in labels]
y_scales = [results[s]["pixel_scale_y_arcsec"] for s in labels]

x = np.arange(len(labels))
ax.bar(x - 0.18, x_scales, width=0.36, label="X scale")
ax.bar(x + 0.18, y_scales, width=0.36, label="Y scale")
ax.set_xticks(x)
ax.set_xticklabels(labels)
ax.set_ylabel("Arcseconds per pixel")
ax.set_title("Phase 48 — Local WCS pixel scale by section")
ax.legend()
ax.grid(axis="y", alpha=0.25)
fig.tight_layout()

scale_plot = OUT / "phase48_pixel_scale_comparison.png"
fig.savefig(scale_plot, dpi=180)
plt.close(fig)

# Field-centre sky distribution.
fig, ax = plt.subplots(figsize=(9, 6))

for section, result in results.items():
    ax.scatter(
        result["centre_ra_deg"],
        result["centre_dec_deg"],
        s=75,
        label=section
    )
    ax.annotate(
        section,
        (result["centre_ra_deg"], result["centre_dec_deg"]),
        xytext=(6, 5),
        textcoords="offset points"
    )

ax.set_xlabel("Right ascension (degrees)")
ax.set_ylabel("Declination (degrees)")
ax.set_title("Phase 48 — Plate-solved section field centres")
ax.grid(alpha=0.25)
ax.legend()
fig.tight_layout()

centre_plot = OUT / "phase48_field_centres.png"
fig.savefig(centre_plot, dpi=180)
plt.close(fig)

print("\n" + "=" * 72)
print("PHASE 48 SUMMARY")
print("=" * 72)

print("Sections:", summary["section_count"])
print("Mean pixel scale:", f"{summary['pixel_scale_mean_arcsec']:.3f} arcsec/px")
print("Scale standard deviation:", f"{summary['pixel_scale_std_arcsec']:.3f} arcsec/px")
print("All same parity:", summary["all_same_parity"])
print("All same projection:", summary["all_same_projection_type"])

print("\nCOMPARISON TO R2C2")
for section, result in comparisons.items():
    print(
        f"  {section}: centre separation="
        f"{result['centre_separation_from_R2C2_deg']:.4f}°, "
        f"scale difference="
        f"{result['scale_difference_from_R2C2_percent']:+.3f}%, "
        f"same parity={result['same_parity_as_R2C2']}"
    )

print("\nOUTPUTS")
print("Report:", report_path)
print("CSV:", csv_path)
print("Scale plot:", scale_plot)
print("Field-centre plot:", centre_plot)

print("\nPHASE 48 COMPLETED SUCCESSFULLY")
