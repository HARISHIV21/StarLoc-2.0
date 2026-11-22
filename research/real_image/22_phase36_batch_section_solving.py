from pathlib import Path
import csv
import json
import subprocess
import time
import numpy as np

from astropy.table import Table
from astropy.io import fits

BASE = Path("research/real_image")
RESULTS = BASE / "results/ASK033"
CATALOGUE = RESULTS / "refined_candidates.csv"
CONFIG = BASE / "astrometry/astrometry.cfg"
OUT = RESULTS / "phase36_section_solutions"
OUT.mkdir(parents=True, exist_ok=True)

# Sections with sufficient candidate detections.
SECTIONS = {
    "R1C2": (640, 0),
    "R1C3": (1280, 0),
    "R2C1": (0, 480),
    "R3C1": (0, 960),
    "R3C2": (640, 960),
}

print("=" * 65)
print("STARLOC 2.0 — PHASE 36 CORRECTED")
print("MULTI-SECTION ASTROMETRIC SOLVING")
print("=" * 65)

with CATALOGUE.open(newline="") as f:
    rows = list(csv.DictReader(f))

results = []

for section, (offset_x, offset_y) in SECTIONS.items():

    selected = [r for r in rows if r["section"] == section]

    print(f"\n--- {section} ---")
    print("Candidates:", len(selected))

    if len(selected) < 15:
        results.append({
            "section": section,
            "candidate_count": len(selected),
            "solved": False,
            "reason": "Insufficient candidates"
        })
        print("Skipped")
        continue

    x = np.array([float(r["x"]) - offset_x for r in selected])
    y = np.array([float(r["y"]) - offset_y for r in selected])
    snr = np.array([float(r["snr"]) for r in selected])

    table = Table()
    table["X"] = x + 1.0
    table["Y"] = y + 1.0
    table["FLUX"] = np.maximum(snr, 0.01)

    prefix = f"{section}_custom"
    xyls = OUT / f"{prefix}.xyls"

    table.write(xyls, format="fits", overwrite=True)

    log_path = OUT / f"{prefix}_solver.log"

    command = [
        "solve-field",
        "--backend-config", str(CONFIG.resolve()),
        "--overwrite",
        "--no-plots",
        "--dir", str(OUT.resolve()),
        "--out", prefix,

        # Required for custom XYLS inputs.
        "--width", "640",
        "--height", "480",

        "--scale-units", "degwidth",
        "--scale-low", "15",
        "--scale-high", "80",
        "--quad-size-min", "0.05",
        "--pixel-error", "2",
        "--cpulimit", "60",
        str(xyls.resolve())
    ]

    start = time.time()

    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=90
        )
        output = completed.stdout + "\n" + completed.stderr
        return_code = completed.returncode
        timed_out = False

    except subprocess.TimeoutExpired as exc:
        output = str(exc)
        return_code = -1
        timed_out = True

    elapsed = time.time() - start
    log_path.write_text(output)

    wcs_path = OUT / f"{prefix}.wcs"
    solved_path = OUT / f"{prefix}.solved"

    solved = solved_path.exists() and wcs_path.exists()

    item = {
        "section": section,
        "candidate_count": len(selected),
        "median_snr": round(float(np.median(snr)), 3),
        "return_code": return_code,
        "timed_out": timed_out,
        "elapsed_seconds": round(elapsed, 2),
        "solved": solved,
        "wcs": str(wcs_path) if solved else None,
        "log": str(log_path)
    }

    if solved:
        with fits.open(wcs_path) as hdul:
            header = hdul[0].header
            item["ra_center_deg"] = float(header["CRVAL1"])
            item["dec_center_deg"] = float(header["CRVAL2"])
            item["pixel_scale_deg"] = float(
                np.sqrt(abs(header["CD1_1"] * header["CD2_2"]
                            - header["CD1_2"] * header["CD2_1"]))
            ) if "CD1_1" in header else None

        print("PLATE SOLVE SUCCESS")
        print("RA centre:", item["ra_center_deg"])
        print("Dec centre:", item["dec_center_deg"])

    else:
        print("PLATE SOLVE NOT CONFIRMED")
        print("\n".join(output.splitlines()[-12:]))

    print("Elapsed:", round(elapsed, 2), "seconds")
    results.append(item)

report = {
    "phase": 36,
    "method": "Independent Astrometry.net solving of 640x480 image sections",
    "sections_tested": len(SECTIONS),
    "sections_solved": sum(
        r.get("solved", False) for r in results
    ),
    "results": results
}

report_path = BASE / "phase36_multi_section_solve_report.json"
report_path.write_text(json.dumps(report, indent=2))

print("\n" + "=" * 65)
print("PHASE 36 SUMMARY")
print("=" * 65)
print("Sections tested:", len(SECTIONS))
print("Sections solved:", report["sections_solved"])

for item in results:
    print(
        item["section"],
        "| candidates:", item["candidate_count"],
        "| solved:", item.get("solved", False)
    )

print("\nReport:", report_path)
print("Solutions:", OUT)
print("\nPHASE 36 CORRECTED COMPLETE")
