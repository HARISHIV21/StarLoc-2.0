import json
from pathlib import Path
import numpy as np
from astropy.io import fits
from astropy.wcs import WCS

R = Path("research/real_image/results/ASK033")
OUT = R / "objective4_calibration_audit"
OUT.mkdir(parents=True, exist_ok=True)

SECTIONS = {
    "R1C2": R / "phase36_section_solutions/R1C2_custom.wcs",
    "R2C1": R / "phase36_section_solutions/R2C1_custom.wcs",
    "R3C1": R / "phase36_section_solutions/R3C1_custom.wcs",
    "R3C2": R / "phase36_section_solutions/R3C2_custom.wcs",
    "R2C2": R / "custom_plate_solutions/R2C2_custom.wcs",
}

def evaluate_poly(coeff, u, v):
    result = np.zeros_like(u, dtype=float)
    for i in range(coeff.shape[0]):
        for j in range(coeff.shape[1]):
            if coeff[i, j] != 0:
                result += coeff[i, j] * (u ** i) * (v ** j)
    return result

# Sample the full section, including its boundaries.
xx, yy = np.meshgrid(
    np.linspace(1, 640, 81),
    np.linspace(1, 480, 61)
)

report = {
    "objective": 4,
    "title": "SIP polynomial distortion analysis",
    "grid": "81 x 61 samples per 640 x 480 section",
    "sections": {}
}

for name, path in SECTIONS.items():
    if not path.exists():
        continue

    wcs = WCS(fits.getheader(path), naxis=2)
    sip = wcs.sip

    if sip is None:
        print(f"\n{name}: no SIP model")
        continue

    u = xx - sip.crpix[0]
    v = yy - sip.crpix[1]

    # SIP forward correction: (u,v) -> (u+A, v+B)
    da = evaluate_poly(sip.a, u, v)
    db = evaluate_poly(sip.b, u, v)
    correction = np.hypot(da, db)

    corners = {}
    for label, x, y in [
        ("top_left", 1, 1),
        ("top_right", 640, 1),
        ("bottom_left", 1, 480),
        ("bottom_right", 640, 480),
    ]:
        cu = np.array([x - sip.crpix[0]], dtype=float)
        cv = np.array([y - sip.crpix[1]], dtype=float)
        ca = evaluate_poly(sip.a, cu, cv)[0]
        cb = evaluate_poly(sip.b, cu, cv)[0]
        corners[label] = {
            "delta_x_px": float(ca),
            "delta_y_px": float(cb),
            "magnitude_px": float(np.hypot(ca, cb))
        }

    item = {
        "wcs_file": str(path),
        "sip_a_order": int(sip.a_order),
        "sip_b_order": int(sip.b_order),
        "sip_ap_order": int(sip.ap_order) if sip.ap is not None else None,
        "sip_bp_order": int(sip.bp_order) if sip.bp is not None else None,
        "reference_pixel": [float(x) for x in sip.crpix],
        "correction_magnitude_px": {
            "minimum": float(np.min(correction)),
            "median": float(np.median(correction)),
            "rms": float(np.sqrt(np.mean(correction ** 2))),
            "maximum": float(np.max(correction))
        },
        "corner_corrections": corners
    }

    report["sections"][name] = item

    print(f"\n{name}")
    print("SIP A/B orders:", sip.a_order, sip.b_order)
    print("Median correction:", f'{item["correction_magnitude_px"]["median"]:.4f}', "px")
    print("RMS correction:", f'{item["correction_magnitude_px"]["rms"]:.4f}', "px")
    print("Maximum correction:", f'{item["correction_magnitude_px"]["maximum"]:.4f}', "px")
    print("Corner corrections:")
    for corner, values in corners.items():
        print(f"  {corner}: {values['magnitude_px']:.4f} px")

output = OUT / "objective4_sip_distortion_report.json"
output.write_text(json.dumps(report, indent=2))

print("\nSections analysed:", len(report["sections"]))
print("Report:", output)
print("OBJECTIVE 4 SIP DISTORTION ANALYSIS COMPLETE")
