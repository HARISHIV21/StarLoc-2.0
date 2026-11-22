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

report = {
    "objective": 4,
    "title": "Local WCS optical calibration parameter audit",
    "sections": {},
    "interpretation": [
        "This audit characterizes existing local WCS models.",
        "It does not establish a global fisheye distortion model."
    ]
}

for name, path in SECTIONS.items():
    if not path.exists():
        print(name, "WCS missing")
        continue

    header = fits.getheader(path)
    wcs = WCS(header, naxis=2)
    matrix = np.asarray(wcs.pixel_scale_matrix, dtype=float)

    sx = float(np.linalg.norm(matrix[:, 0]))
    sy = float(np.linalg.norm(matrix[:, 1]))
    determinant = float(np.linalg.det(matrix))

    # Local orientation of the image X axis in the tangent plane.
    rotation = float(np.degrees(np.arctan2(matrix[1, 0], matrix[0, 0])))

    distortion = {
        "sip_present": wcs.sip is not None,
        "cpdis1_present": wcs.cpdis1 is not None,
        "cpdis2_present": wcs.cpdis2 is not None,
        "det2im1_present": wcs.det2im1 is not None,
        "det2im2_present": wcs.det2im2 is not None,
    }

    item = {
        "wcs_file": str(path),
        "ctype": list(wcs.wcs.ctype),
        "crpix": [float(v) for v in wcs.wcs.crpix],
        "crval_deg": [float(v) for v in wcs.wcs.crval],
        "pixel_scale_matrix_deg_per_pixel": matrix.tolist(),
        "x_axis_scale_deg_per_pixel": sx,
        "y_axis_scale_deg_per_pixel": sy,
        "determinant": determinant,
        "orientation_deg": rotation,
        "distortion_models": distortion,
        "header_cd_matrix": {
            key: float(header[key])
            for key in ("CD1_1", "CD1_2", "CD2_1", "CD2_2")
            if key in header
        }
    }

    report["sections"][name] = item

    print(f"\n{name}")
    print("Projection:", item["ctype"])
    print("Reference sky:", item["crval_deg"])
    print("Reference pixel:", item["crpix"])
    print("X/Y scales:", sx, sy, "deg/pixel")
    print("Orientation:", rotation, "degrees")
    print("Distortion:", distortion)

path = OUT / "objective4_wcs_parameter_report.json"
path.write_text(json.dumps(report, indent=2))

print("\nSections audited:", len(report["sections"]))
print("Report:", path)
print("OBJECTIVE 4 PARAMETER AUDIT COMPLETE")
