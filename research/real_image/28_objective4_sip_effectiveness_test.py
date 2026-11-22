import csv
import json
import re
from pathlib import Path

import numpy as np
from astropy.io import fits
from astropy.wcs import WCS

R = Path("research/real_image/results/ASK033")
MATCHES = R / "phase37B_final_validation/phase37B_all_matches.csv"
OUT = R / "objective4_calibration_audit"
OUT.mkdir(parents=True, exist_ok=True)

SECTIONS = {
    "R1C2": R / "phase36_section_solutions/R1C2_custom.wcs",
    "R2C1": R / "phase36_section_solutions/R2C1_custom.wcs",
    "R3C1": R / "phase36_section_solutions/R3C1_custom.wcs",
    "R3C2": R / "phase36_section_solutions/R3C2_custom.wcs",
    "R2C2": R / "custom_plate_solutions/R2C2_custom.wcs",
}

with MATCHES.open(newline="") as f:
    rows = list(csv.DictReader(f))

report = {
    "objective": 4,
    "title": "SIP versus TAN-only positional comparison",
    "method": "Same Phase 37B star associations evaluated with full SIP and with SIP keywords removed",
    "sections": {}
}

print("=" * 68)
print("STARLOC — OBJECTIVE 4")
print("SIP EFFECTIVENESS TEST")
print("=" * 68)

for section, path in SECTIONS.items():
    section_rows = [r for r in rows if r["section"] == section]

    if not section_rows or not path.exists():
        print(section, "SKIPPED")
        continue

    header = fits.getheader(path)
    full_wcs = WCS(header, naxis=2)

    # Create a separate TAN-only header by removing SIP coefficients.
    linear_header = header.copy()
    sip_pattern = re.compile(
        r"^(A|B|AP|BP)_(ORDER|\d+_\d+)$"
    )

    for key in list(linear_header.keys()):
        if sip_pattern.match(key):
            del linear_header[key]

    linear_wcs = WCS(linear_header, naxis=2)

    ra = np.array([float(r["ra_deg"]) for r in section_rows])
    dec = np.array([float(r["dec_deg"]) for r in section_rows])

    # Candidate coordinates are zero-based local pixels.
    observed = np.column_stack((
        np.array([float(r["candidate_x_local"]) for r in section_rows]) + 1,
        np.array([float(r["candidate_y_local"]) for r in section_rows]) + 1
    ))

    sky = np.column_stack((ra, dec))

    predicted_sip = full_wcs.all_world2pix(sky, 1, quiet=True)
    predicted_tan = linear_wcs.all_world2pix(sky, 1, quiet=True)

    residual_sip = np.linalg.norm(predicted_sip - observed, axis=1)
    residual_tan = np.linalg.norm(predicted_tan - observed, axis=1)

    def metrics(values):
        return {
            "count": int(len(values)),
            "median_px": float(np.median(values)),
            "mean_px": float(np.mean(values)),
            "rms_px": float(np.sqrt(np.mean(values ** 2))),
            "maximum_px": float(np.max(values))
        }

    sip_metrics = metrics(residual_sip)
    tan_metrics = metrics(residual_tan)

    improvement = (
        (tan_metrics["rms_px"] - sip_metrics["rms_px"])
        / tan_metrics["rms_px"] * 100
        if tan_metrics["rms_px"] > 0 else None
    )

    report["sections"][section] = {
        "wcs_file": str(path),
        "sip_residuals": sip_metrics,
        "tan_only_residuals": tan_metrics,
        "sip_rms_improvement_percent": improvement
    }

    print(f"\n{section} — {len(section_rows)} matched stars")
    print(f"  Full SIP median: {sip_metrics['median_px']:.3f} px")
    print(f"  TAN-only median: {tan_metrics['median_px']:.3f} px")
    print(f"  Full SIP RMS:    {sip_metrics['rms_px']:.3f} px")
    print(f"  TAN-only RMS:    {tan_metrics['rms_px']:.3f} px")
    print(f"  SIP RMS change:  {improvement:.2f}%")

output = OUT / "objective4_sip_effectiveness_report.json"
output.write_text(json.dumps(report, indent=2))

print("\nReport:", output)
print("OBJECTIVE 4 SIP EFFECTIVENESS TEST COMPLETE")
