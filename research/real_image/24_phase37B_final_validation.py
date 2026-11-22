import csv, json, warnings
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from astropy.io import fits
from astropy.wcs import WCS
from astropy.coordinates import SkyCoord
import astropy.units as u
from astropy.wcs.wcs import NoConvergence
from scipy.optimize import linear_sum_assignment
from scipy.spatial.distance import cdist

warnings.filterwarnings("ignore")

RESULTS = Path("research/real_image/results/ASK033")
OUT = RESULTS / "phase37B_final_validation"
OUT.mkdir(parents=True, exist_ok=True)

CANDIDATES = RESULTS / "refined_candidates.csv"
CATALOGUE = RESULTS / "ASK033_visible_hipparcos_catalogue.csv"
MAX_DISTANCE = 5.0

SECTIONS = {
    "R1C2": ((640, 0), RESULTS / "phase36_section_solutions/R1C2_custom.wcs"),
    "R2C1": ((0, 480), RESULTS / "phase36_section_solutions/R2C1_custom.wcs"),
    "R3C1": ((0, 960), RESULTS / "phase36_section_solutions/R3C1_custom.wcs"),
    "R3C2": ((640, 960), RESULTS / "phase36_section_solutions/R3C2_custom.wcs"),
    "R2C2": ((640, 480), RESULTS / "custom_plate_solutions/R2C2_custom.wcs"),
}

def read_csv(path):
    with path.open(newline="") as f:
        return list(csv.DictReader(f))

def floats(rows, key):
    return np.array([
        float(r[key]) if r.get(key, "") not in ("", None) else np.nan
        for r in rows
    ])

if not CANDIDATES.exists() or not CATALOGUE.exists():
    raise FileNotFoundError("Required Phase 37 candidate or catalogue CSV is missing.")

candidates = read_csv(CANDIDATES)
catalogue = read_csv(CATALOGUE)

required = {"hip_id", "ra_deg", "dec_deg", "magnitude"}
if not catalogue or not required.issubset(catalogue[0]):
    raise ValueError(f"Catalogue must contain columns: {sorted(required)}")

hip_all = np.array([r["hip_id"] for r in catalogue])
ra_all = floats(catalogue, "ra_deg")
dec_all = floats(catalogue, "dec_deg")
mag_all = floats(catalogue, "magnitude")

valid = (
    np.isfinite(ra_all) & np.isfinite(dec_all)
    & np.isfinite(mag_all) & (hip_all != "")
)
hip_all, ra_all, dec_all, mag_all = (
    hip_all[valid], ra_all[valid], dec_all[valid], mag_all[valid]
)

all_matches, section_reports = [], []

print("=" * 65)
print("STARLOC 2.0 — PHASE 37B FINAL VALIDATION")
print("=" * 65)
print("Catalogue entries:", len(ra_all))
print("Maximum accepted residual:", MAX_DISTANCE, "pixels")

for section, (offset, wcs_path) in SECTIONS.items():
    print(f"\n--- {section} ---")

    if not wcs_path.exists():
        print("SKIPPED: WCS missing:", wcs_path)
        continue

    ox, oy = offset
    selected = [r for r in candidates if r["section"] == section]

    if not selected:
        print("SKIPPED: no detections")
        continue

    x = floats(selected, "x") - ox + 1
    y = floats(selected, "y") - oy + 1
    valid_det = np.isfinite(x) & np.isfinite(y) & (x >= 1) & (x <= 640) & (y >= 1) & (y <= 480)
    x, y = x[valid_det], y[valid_det]

    wcs = WCS(fits.getheader(wcs_path))

    centre = SkyCoord(
        ra=float(wcs.wcs.crval[0]) * u.deg,
        dec=float(wcs.wcs.crval[1]) * u.deg,
        frame="icrs"
    )
    sky = SkyCoord(ra=ra_all * u.deg, dec=dec_all * u.deg, frame="icrs")
    near = centre.separation(sky).deg <= 30.0

    hip, ra, dec, mag = hip_all[near], ra_all[near], dec_all[near], mag_all[near]

    try:
        pixels = wcs.all_world2pix(np.column_stack((ra, dec)), 1, quiet=True)
    except NoConvergence as exc:
        pixels = exc.best_solution

    px, py = pixels[:, 0], pixels[:, 1]
    inside = (
        np.isfinite(px) & np.isfinite(py)
        & (px >= 1) & (px <= 640)
        & (py >= 1) & (py <= 480)
    )

    px, py = px[inside], py[inside]
    hip, ra, dec, mag = hip[inside], ra[inside], dec[inside], mag[inside]

    if len(x) == 0 or len(px) == 0:
        print("No valid detections or projected catalogue stars.")
        continue

    distances = cdist(np.column_stack((x, y)), np.column_stack((px, py)))

    # Gate invalid pairs before assignment; dummy columns allow unmatched detections.
    n_det, n_cat = distances.shape
    cost = np.full((n_det, n_cat + n_det), MAX_DISTANCE + 1.0)
    cost[:, :n_cat] = np.where(distances <= MAX_DISTANCE, distances, 1e6)
    cost[:, n_cat:] = MAX_DISTANCE + 0.001
    row_idx, col_idx = linear_sum_assignment(cost)

    accepted_pairs = [
        (i, j, distances[i, j])
        for i, j in zip(row_idx, col_idx)
        if j < n_cat and distances[i, j] <= MAX_DISTANCE
    ]

    matches = []
    for i, j, residual in accepted_pairs:
        matches.append({
            "section": section,
            "candidate_x_local": float(x[i] - 1),
            "candidate_y_local": float(y[i] - 1),
            "hip_id": str(hip[j]),
            "ra_deg": float(ra[j]),
            "dec_deg": float(dec[j]),
            "magnitude": float(mag[j]),
            "pixel_residual": float(residual),
            "match_status": "accepted_provisional"
        })

    all_matches.extend(matches)
    residuals = np.array([m["pixel_residual"] for m in matches])

    thresholds = {}
    for threshold in (1, 2, 3, 5):
        subset = residuals[residuals <= threshold]
        thresholds[str(threshold)] = {
            "match_count": int(len(subset)),
            "median_residual_px": float(np.median(subset)) if len(subset) else None,
            "mean_residual_px": float(np.mean(subset)) if len(subset) else None
        }

    section_reports.append({
        "section": section,
        "detected_candidates": int(len(x)),
        "projected_catalogue_stars": int(len(px)),
        "accepted_matches": len(matches),
        "unmatched_detections": int(len(x) - len(matches)),
        "unique_hip_ids": len(set(m["hip_id"] for m in matches)),
        "median_residual_px": float(np.median(residuals)) if len(residuals) else None,
        "maximum_residual_px": float(np.max(residuals)) if len(residuals) else None,
        "threshold_statistics": thresholds,
        "wcs_file": str(wcs_path)
    })

    fig, ax = plt.subplots(figsize=(9, 7))
    ax.scatter(x - 1, y - 1, s=25, facecolors="none", edgecolors="red", label="Detected candidates")
    ax.scatter(px - 1, py - 1, s=12, marker="+", label="Projected catalogue stars")

    for i, j, _ in accepted_pairs:
        ax.plot([x[i] - 1, px[j] - 1], [y[i] - 1, py[j] - 1], linewidth=0.5)

    ax.set(xlim=(0, 640), ylim=(480, 0), aspect="equal",
           title=f"ASK033 {section} — Phase 37B validation",
           xlabel="Local pixel X", ylabel="Local pixel Y")
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT / f"{section}_validation.png", dpi=150)
    plt.close(fig)

    print("Detections:", len(x), "| Projected catalogue:", len(px))
    print("Accepted:", len(matches), "| Unmatched:", len(x) - len(matches))
    print("Median residual:", round(float(np.median(residuals)), 3) if len(residuals) else "N/A", "px")

csv_path = OUT / "phase37B_all_matches.csv"
fields = [
    "section", "candidate_x_local", "candidate_y_local", "hip_id",
    "ra_deg", "dec_deg", "magnitude", "pixel_residual", "match_status"
]
with csv_path.open("w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerows(all_matches)

residuals = np.array([m["pixel_residual"] for m in all_matches])
report = {
    "phase": "37B",
    "dataset": "ASK033 AllSkyKamera",
    "method": "WCS catalogue projection with gated one-to-one pixel matching",
    "maximum_match_distance_px": MAX_DISTANCE,
    "catalogue_entries": int(len(ra_all)),
    "sections_validated": len(section_reports),
    "total_accepted_matches": len(all_matches),
    "unique_hip_ids_global": len(set(m["hip_id"] for m in all_matches)),
    "median_residual_px": float(np.median(residuals)) if len(residuals) else None,
    "maximum_residual_px": float(np.max(residuals)) if len(residuals) else None,
    "sections": section_reports,
    "limitations": [
        "Observation timestamp and exposure midpoint are unverified.",
        "Catalogue epoch and astrometric provenance require confirmation.",
        "Matches are provisional geometric associations, not independent identity confirmation.",
        "No final global fisheye optical calibration is established."
    ]
}
report_path = OUT / "phase37B_final_report.json"
report_path.write_text(json.dumps(report, indent=2))

print("\n" + "=" * 65)
print("PHASE 37B COMPLETE")
print("Total accepted matches:", len(all_matches))
print("Globally unique HIP IDs:", report["unique_hip_ids_global"])
print("CSV:", csv_path)
print("JSON:", report_path)
print("Overlays:", OUT)
