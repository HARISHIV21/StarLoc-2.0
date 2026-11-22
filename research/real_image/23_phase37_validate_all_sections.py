import csv
import json
import warnings
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
from astropy.wcs import WCS
from astropy.wcs.wcs import NoConvergence
from scipy.optimize import linear_sum_assignment
from scipy.spatial.distance import cdist
from astropy.coordinates import SkyCoord
import astropy.units as u

warnings.filterwarnings("ignore", category=UserWarning)

BASE = Path("research/real_image")
RESULTS = BASE / "results/ASK033"
OUT = RESULTS / "phase37_validation"
OUT.mkdir(parents=True, exist_ok=True)

CANDIDATES = RESULTS / "refined_candidates.csv"
CATALOGUE = RESULTS / "ASK033_visible_hipparcos_catalogue.csv"

# Only sections with confirmed WCS solutions are included.
SECTIONS = {
    "R1C2": {
        "offset": (640, 0),
        "wcs": RESULTS / "phase36_section_solutions/R1C2_custom.wcs"
    },
    "R2C1": {
        "offset": (0, 480),
        "wcs": RESULTS / "phase36_section_solutions/R2C1_custom.wcs"
    },
    "R3C1": {
        "offset": (0, 960),
        "wcs": RESULTS / "phase36_section_solutions/R3C1_custom.wcs"
    },
    "R3C2": {
        "offset": (640, 960),
        "wcs": RESULTS / "phase36_section_solutions/R3C2_custom.wcs"
    },
    "R2C2": {
        "offset": (640, 480),
        "wcs": RESULTS / "custom_plate_solutions/R2C2_custom.wcs"
    }
}

def read_csv(path):
    with path.open(newline="") as f:
        return list(csv.DictReader(f))

def get_column(rows, names):
    for name in names:
        if name in rows[0]:
            return np.array([
                float(r[name]) if r[name] not in ("", None) else np.nan
                for r in rows
            ])
    raise KeyError("Missing columns: " + str(names))

if not CANDIDATES.exists():
    raise FileNotFoundError(CANDIDATES)

if not CATALOGUE.exists():
    raise FileNotFoundError(CATALOGUE)

candidates = read_csv(CANDIDATES)
catalogue = read_csv(CATALOGUE)

ra_all = get_column(
    catalogue, ["ra_2026_deg", "ra_deg", "RA"]
)
dec_all = get_column(
    catalogue, ["dec_2026_deg", "dec_deg", "DEC"]
)

valid = np.isfinite(ra_all) & np.isfinite(dec_all)
ra_all = ra_all[valid]
dec_all = dec_all[valid]

results = []
all_matches = []

print("=" * 68)
print("STARLOC 2.0 — PHASE 37 CORRECTED")
print("MULTI-SECTION HIPPARCOS VALIDATION")
print("=" * 68)
print("Catalogue stars:", len(ra_all))
print("Sections to validate:", len(SECTIONS))

for section, config in SECTIONS.items():

    print("\n" + "-" * 55)
    print("SECTION:", section)

    wcs_path = config["wcs"]
    if not wcs_path.exists():
        print("SKIPPED: WCS file missing:", wcs_path)
        continue

    ox, oy = config["offset"]

    section_rows = [
        r for r in candidates if r["section"] == section
    ]

    if not section_rows:
        print("SKIPPED: no detected candidates")
        continue

    # Refined candidate coordinates are global image coordinates.
    # Convert to local section coordinates and FITS origin 1.
    x = np.array([float(r["x"]) - ox + 1 for r in section_rows])
    y = np.array([float(r["y"]) - oy + 1 for r in section_rows])

    wcs = WCS(fits.getheader(wcs_path))

    # Limit catalogue projection to a practical radius around
    # the solved field centre to avoid distant projection failures.
    centre = SkyCoord(
        ra=float(wcs.wcs.crval[0]) * u.deg,
        dec=float(wcs.wcs.crval[1]) * u.deg,
        frame="icrs"
    )

    sky = SkyCoord(
        ra=ra_all * u.deg,
        dec=dec_all * u.deg,
        frame="icrs"
    )

    separation = centre.separation(sky).deg
    near = separation <= 30.0

    ra = ra_all[near]
    dec = dec_all[near]

    # Handle non-convergent WCS projections without terminating.
    world = np.column_stack((ra, dec))

    try:
        pixels = wcs.all_world2pix(world, 1, quiet=True)
        px = pixels[:, 0]
        py = pixels[:, 1]
        projection_method = "all_world2pix quiet mode"

    except NoConvergence as exc:
        # Astropy supplies its best available estimates.
        best = exc.best_solution
        px = best[:, 0]
        py = best[:, 1]
        projection_method = "NoConvergence best_solution"

    finite = np.isfinite(px) & np.isfinite(py)

    inside = (
        finite
        & (px >= 1) & (px <= 640)
        & (py >= 1) & (py <= 480)
    )

    px_inside = px[inside]
    py_inside = py[inside]
    ra_inside = ra[inside]
    dec_inside = dec[inside]

    print("Detected candidates:", len(x))
    print("Catalogue stars within 30 degrees:", len(ra))
    print("Projected inside section:", len(px_inside))
    print("Projection:", projection_method)

    if len(px_inside) == 0:
        print("No projected catalogue stars inside image.")
        continue

    detected = np.column_stack((x, y))
    projected = np.column_stack((px_inside, py_inside))

    distance_matrix = cdist(detected, projected)
    row_idx, col_idx = linear_sum_assignment(distance_matrix)
    assigned = distance_matrix[row_idx, col_idx]

    summary = {}

    for threshold in [1, 2, 3, 5, 10]:
        accepted = assigned <= threshold
        residuals = assigned[accepted]

        summary[str(threshold)] = {
            "unique_matches": int(np.sum(accepted)),
            "median_residual_px": (
                float(np.median(residuals))
                if len(residuals) else None
            ),
            "mean_residual_px": (
                float(np.mean(residuals))
                if len(residuals) else None
            )
        }

    accepted = assigned <= 5

    section_matches = []

    for i, j, residual in zip(
        row_idx[accepted],
        col_idx[accepted],
        assigned[accepted]
    ):
        match = {
            "section": section,
            "candidate_x_local": float(x[i] - 1),
            "candidate_y_local": float(y[i] - 1),
            "hip_ra_deg": float(ra_inside[j]),
            "hip_dec_deg": float(dec_inside[j]),
            "pixel_residual": float(residual)
        }

        section_matches.append(match)
        all_matches.append(match)

    result = {
        "section": section,
        "detected_candidates": len(x),
        "catalogue_stars_within_30deg": len(ra),
        "catalogue_stars_projected_inside": len(px_inside),
        "projection_method": projection_method,
        "pixel_validation": summary,
        "matches_within_5px": len(section_matches),
        "wcs_file": str(wcs_path)
    }

    results.append(result)

    for threshold, values in summary.items():
        print(
            f"Within {threshold:>2}px:",
            values["unique_matches"],
            "| median residual:",
            values["median_residual_px"]
        )

    # Save visual validation overlay.
    fig, ax = plt.subplots(figsize=(9, 7))

    ax.scatter(
        x - 1, y - 1,
        s=25,
        facecolors="none",
        edgecolors="red",
        label="Detected candidates"
    )

    ax.scatter(
        px_inside - 1, py_inside - 1,
        s=12,
        marker="+",
        label="Projected Hipparcos stars"
    )

    for i, j in zip(row_idx[accepted], col_idx[accepted]):
        ax.plot(
            [x[i] - 1, px_inside[j] - 1],
            [y[i] - 1, py_inside[j] - 1],
            linewidth=0.5
        )

    ax.set_xlim(0, 640)
    ax.set_ylim(480, 0)
    ax.set_aspect("equal")
    ax.set_title(f"ASK033 {section} — WCS validation")
    ax.set_xlabel("Local pixel X")
    ax.set_ylabel("Local pixel Y")
    ax.legend()
    fig.tight_layout()

    overlay = OUT / f"{section}_validation.png"
    fig.savefig(overlay, dpi=150)
    plt.close(fig)

report = {
    "phase": 37,
    "dataset": "Public ASK033 AllSkyKamera image",
    "catalogue": str(CATALOGUE),
    "valid_catalogue_stars": int(len(ra_all)),
    "sections_attempted": len(SECTIONS),
    "sections_validated": len(results),
    "total_unique_matches_within_5px": len(all_matches),
    "sections": results,
    "interpretation": (
        "Independent pixel-space WCS validation against the "
        "propagated Hipparcos catalogue. This does not establish "
        "a final global fisheye optical calibration."
    )
}

report_path = BASE / "phase37_multi_section_validation.json"
report_path.write_text(json.dumps(report, indent=2))

if all_matches:
    matches_path = OUT / "phase37_all_matches.csv"

    with matches_path.open("w", newline="") as f:
        writer = csv.DictWriter(
            f, fieldnames=list(all_matches[0].keys())
        )
        writer.writeheader()
        writer.writerows(all_matches)

print("\n" + "=" * 68)
print("PHASE 37 SUMMARY")
print("=" * 68)
print("Sections validated:", len(results))
print("Total unique matches within 5 px:", len(all_matches))
print("Report:", report_path)
print("Visual overlays:", OUT)
print("PHASE 37 CORRECTED COMPLETE")
