import json
from pathlib import Path

import numpy as np
from astropy.io import fits
from astropy.wcs import WCS
from astropy.coordinates import SkyCoord
import astropy.units as u

R = Path("research/real_image/results/ASK033")
OUT = R / "objective4_calibration_audit"
OUT.mkdir(parents=True, exist_ok=True)

FILES = {
    "R1C2": R / "phase36_section_solutions/R1C2_custom.wcs",
    "R2C1": R / "phase36_section_solutions/R2C1_custom.wcs",
    "R3C1": R / "phase36_section_solutions/R3C1_custom.wcs",
    "R3C2": R / "phase36_section_solutions/R3C2_custom.wcs",
    "R2C2": R / "custom_plate_solutions/R2C2_custom.wcs",
}

# Each pair shares an image boundary.
# Coordinates are FITS 1-based local pixel coordinates.
SEAMS = [
    ("R2C1", "R2C2", "vertical"),
    ("R3C1", "R3C2", "vertical"),
    ("R1C2", "R2C2", "horizontal"),
    ("R2C1", "R3C1", "horizontal"),
    ("R2C2", "R3C2", "horizontal"),
]

wcs_map = {}

for name, path in FILES.items():
    if path.exists():
        wcs_map[name] = WCS(fits.getheader(path), naxis=2)

report = {
    "objective": 4,
    "test": "Adjacent section WCS boundary continuity",
    "sampling_points_per_seam": 25,
    "seams": []
}

print("=" * 68)
print("STARLOC — SECTION BOUNDARY CONTINUITY TEST")
print("=" * 68)

for first, second, direction in SEAMS:
    if first not in wcs_map or second not in wcs_map:
        print(f"\n{first} / {second}: WCS missing; skipped")
        continue

    t = np.linspace(1, 480 if direction == "vertical" else 640, 25)

    if direction == "vertical":
        x1, y1 = np.full_like(t, 640), t
        x2, y2 = np.full_like(t, 1), t
    else:
        x1, y1 = t, np.full_like(t, 480)
        x2, y2 = t, np.full_like(t, 1)

    sky1 = wcs_map[first].all_pix2world(
        np.column_stack((x1, y1)), 1
    )
    sky2 = wcs_map[second].all_pix2world(
        np.column_stack((x2, y2)), 1
    )

    c1 = SkyCoord(
        ra=sky1[:, 0] * u.deg,
        dec=sky1[:, 1] * u.deg,
        frame="icrs"
    )
    c2 = SkyCoord(
        ra=sky2[:, 0] * u.deg,
        dec=sky2[:, 1] * u.deg,
        frame="icrs"
    )

    separation = c1.separation(c2).arcmin
    item = {
        "sections": [first, second],
        "boundary": direction,
        "median_separation_arcmin": float(np.median(separation)),
        "mean_separation_arcmin": float(np.mean(separation)),
        "maximum_separation_arcmin": float(np.max(separation)),
        "minimum_separation_arcmin": float(np.min(separation)),
        "sample_separations_arcmin": separation.tolist()
    }
    report["seams"].append(item)

    print(f"\n{first} ↔ {second} ({direction})")
    print(f"  Median separation: {np.median(separation):.3f} arcmin")
    print(f"  Mean separation:   {np.mean(separation):.3f} arcmin")
    print(f"  Maximum:           {np.max(separation):.3f} arcmin")
    print(f"  Minimum:           {np.min(separation):.3f} arcmin")

output = OUT / "objective4_boundary_continuity_report.json"
output.write_text(json.dumps(report, indent=2))

print("\nReport:", output)
print("SECTION BOUNDARY CONTINUITY TEST COMPLETE")
