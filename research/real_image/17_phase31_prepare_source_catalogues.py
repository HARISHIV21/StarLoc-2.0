from pathlib import Path
import csv
import json
import numpy as np
from astropy.table import Table

BASE = Path("research/real_image")
RESULTS = BASE / "results/ASK033"
INPUT = RESULTS / "refined_candidates.csv"
OUTPUT = RESULTS / "custom_source_catalogues"

OUTPUT.mkdir(parents=True, exist_ok=True)

print("=" * 65)
print("STARLOC 2.0 — PHASE 31")
print("PREPARE CUSTOM ASTROMETRY SOURCE CATALOGUES")
print("=" * 65)

if not INPUT.exists():
    raise FileNotFoundError(INPUT)

with INPUT.open(newline="") as f:
    rows = list(csv.DictReader(f))

if not rows:
    raise RuntimeError("Candidate CSV is empty.")

required = {"x", "y", "snr", "peak_residual", "section"}
missing = required - set(rows[0].keys())
if missing:
    raise RuntimeError("Missing CSV columns: " + str(missing))

print("\nTotal candidates:", len(rows))
print("Columns:", list(rows[0].keys()))

sections = {}

for row in rows:
    section = row["section"].strip()
    sections.setdefault(section, []).append(row)

report = {
    "phase": 31,
    "input": str(INPUT),
    "total_candidates": len(rows),
    "sections": {}
}

print("\nSECTION COORDINATE AUDIT")

for section, group in sorted(sections.items()):
    x = np.array([float(r["x"]) for r in group])
    y = np.array([float(r["y"]) for r in group])
    snr = np.array([float(r["snr"]) for r in group])

    print(
        section,
        "| count:", len(group),
        "| X:", round(x.min(), 2), "to", round(x.max(), 2),
        "| Y:", round(y.min(), 2), "to", round(y.max(), 2),
        "| median SNR:", round(float(np.median(snr)), 2)
    )

    report["sections"][section] = {
        "count": len(group),
        "x_min": float(x.min()),
        "x_max": float(x.max()),
        "y_min": float(y.min()),
        "y_max": float(y.max()),
        "median_snr": float(np.median(snr))
    }

print("\nSECTION IMAGE OFFSETS")

offsets = {
    "R1C1": (0, 0),
    "R1C2": (640, 0),
    "R1C3": (1280, 0),
    "R2C1": (0, 480),
    "R2C2": (640, 480),
    "R2C3": (1280, 480),
    "R3C1": (0, 960),
    "R3C2": (640, 960),
    "R3C3": (1280, 960)
}

for section, group in sorted(sections.items()):
    key = section.replace("ASK033_section_", "")
    if key not in offsets:
        print("Unknown section:", section)
        continue

    ox, oy = offsets[key]
    x = np.array([float(r["x"]) for r in group])
    y = np.array([float(r["y"]) for r in group])

    # Determine whether CSV coordinates are global or section-local.
    global_fit = (
        np.all(x >= ox - 2) and np.all(x <= ox + 642)
        and np.all(y >= oy - 2) and np.all(y <= oy + 482)
    )

    local_fit = (
        np.all(x >= -2) and np.all(x <= 642)
        and np.all(y >= -2) and np.all(y <= 482)
    )

    if global_fit and not local_fit:
        mode = "global"
    elif local_fit and not global_fit:
        mode = "local"
    elif global_fit and local_fit:
        mode = "ambiguous"
    else:
        mode = "outside_expected_bounds"

    print(section, "coordinate mode:", mode)

    report["sections"][section]["coordinate_mode"] = mode

report_path = BASE / "phase31_coordinate_audit.json"
report_path.write_text(json.dumps(report, indent=2))

print("\nCOORDINATE AUDIT SAVED:", report_path)
print("\nNo coordinates were transformed.")
print("No FITS catalogues were generated yet.")
print("PHASE 31 AUDIT COMPLETE")
