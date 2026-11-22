import csv, json
from pathlib import Path
import numpy as np
from astropy.wcs import WCS
from astropy.io import fits

RESULTS = Path("research/real_image/results/ASK033")
MATCHES = RESULTS / "phase37B_final_validation/phase37B_all_matches.csv"
OUT = RESULTS / "objective3_radec_to_pixel"
OUT.mkdir(parents=True, exist_ok=True)

SECTIONS = {
    "R1C2": ((640, 0), RESULTS / "phase36_section_solutions/R1C2_custom.wcs"),
    "R2C1": ((0, 480), RESULTS / "phase36_section_solutions/R2C1_custom.wcs"),
    "R3C1": ((0, 960), RESULTS / "phase36_section_solutions/R3C1_custom.wcs"),
    "R3C2": ((640, 960), RESULTS / "phase36_section_solutions/R3C2_custom.wcs"),
    "R2C2": ((640, 480), RESULTS / "custom_plate_solutions/R2C2_custom.wcs"),
}

if not MATCHES.exists():
    raise FileNotFoundError(MATCHES)

with MATCHES.open(newline="") as f:
    matches = list(csv.DictReader(f))

output = []
reports = []

for section, (offset, wcs_path) in SECTIONS.items():
    if not wcs_path.exists():
        print(f"{section}: WCS missing — skipped")
        continue

    selected = [r for r in matches if r["section"] == section]
    if not selected:
        continue

    wcs = WCS(fits.getheader(wcs_path))

    ra = np.array([float(r["ra_deg"]) for r in selected])
    dec = np.array([float(r["dec_deg"]) for r in selected])

    # Objective 3: celestial coordinates -> FITS pixel coordinates.
    pixels = wcs.all_world2pix(np.column_stack((ra, dec)), 1)

    # FITS origin 1 -> zero-based local image coordinates.
    x_local = pixels[:, 0] - 1
    y_local = pixels[:, 1] - 1

    ox, oy = offset
    x_global = x_local + ox
    y_global = y_local + oy

    # Round-trip check: pixel coordinates -> celestial coordinates.
    recovered = wcs.all_pix2world(pixels, 1)
    ra_error = (recovered[:, 0] - ra + 180) % 360 - 180
    dec_error = recovered[:, 1] - dec

    for i, row in enumerate(selected):
        output.append({
            "section": section,
            "hip_id": row["hip_id"],
            "input_ra_deg": ra[i],
            "input_dec_deg": dec[i],
            "fits_x_1based": pixels[i, 0],
            "fits_y_1based": pixels[i, 1],
            "local_x_0based": x_local[i],
            "local_y_0based": y_local[i],
            "global_x_0based": x_global[i],
            "global_y_0based": y_global[i],
            "roundtrip_ra_error_arcsec": ra_error[i] * 3600,
            "roundtrip_dec_error_arcsec": dec_error[i] * 3600,
        })

    reports.append({
        "section": section,
        "stars_processed": len(selected),
        "median_ra_roundtrip_error_arcsec":
            float(np.median(np.abs(ra_error * 3600))),
        "median_dec_roundtrip_error_arcsec":
            float(np.median(np.abs(dec_error * 3600))),
        "wcs": str(wcs_path)
    })

csv_path = OUT / "objective3_radec_to_pixel.csv"
fields = list(output[0].keys()) if output else []

with csv_path.open("w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerows(output)

report = {
    "objective": 3,
    "description": "Convert identified stellar RA/Dec coordinates to image pixels",
    "coordinate_convention": {
        "WCS_input_output_origin": 1,
        "local_image_coordinates": "zero-based",
        "global_image_coordinates": "zero-based with section offsets"
    },
    "total_stars_processed": len(output),
    "sections": reports,
    "method": "Astropy WCS all_world2pix with inverse all_pix2world round-trip"
}

report_path = OUT / "objective3_report.json"
report_path.write_text(json.dumps(report, indent=2))

print("\n========== OBJECTIVE 3 SUMMARY ==========")
print("Stars processed:", len(output))
for r in reports:
    print(
        r["section"],
        "| stars:", r["stars_processed"],
        "| median RA round-trip error:",
        f'{r["median_ra_roundtrip_error_arcsec"]:.8f} arcsec',
        "| median Dec round-trip error:",
        f'{r["median_dec_roundtrip_error_arcsec"]:.8f} arcsec'
    )

print("\nCSV:", csv_path)
print("Report:", report_path)
print("OBJECTIVE 3 INITIAL CONVERSION COMPLETE")
