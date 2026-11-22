from pathlib import Path
from astropy.io import fits
import json
import numpy as np

BASE = Path("research/real_image")
INDEX = BASE / "astrometry/indexes"
SOLUTIONS = BASE / "results/ASK033/plate_solutions"

print("=" * 65)
print("STARLOC 2.0 — PHASE 30")
print("INDEX COVERAGE AND SOURCE EXTRACTION DIAGNOSTIC")
print("=" * 65)

print("\n1. ASTROMETRY INDEX SCALE METADATA")

for path in sorted(INDEX.glob("index-*.fits")):
    print("\n", path.name)
    try:
        with fits.open(path) as hdul:
            for i, hdu in enumerate(hdul):
                header = hdu.header
                keys = [
                    k for k in header.keys()
                    if any(s in k.upper() for s in (
                        "SCALE", "QUAD", "INDEX", "HEALPIX",
                        "HPNSIDE", "HPN", "NAXIS"
                    ))
                ]
                if keys:
                    print(" HDU", i)
                    for key in keys:
                        print("  ", key, "=", header.get(key))
    except Exception as exc:
        print(" ERROR:", exc)

print("\n2. SOURCE COUNTS AND COORDINATE DISTRIBUTION")

for path in sorted(SOLUTIONS.glob("ASK033_section_*.axy")):
    try:
        with fits.open(path) as hdul:
            data = hdul[1].data
            x = np.asarray(data["X"], dtype=float)
            y = np.asarray(data["Y"], dtype=float)
            flux = np.asarray(data["FLUX"], dtype=float)

            print("\n", path.name)
            print(" Sources:", len(x))
            if len(x):
                print(" X range:", round(x.min(), 2), "to", round(x.max(), 2))
                print(" Y range:", round(y.min(), 2), "to", round(y.max(), 2))
                print(" Flux min/median/max:",
                      round(float(np.min(flux)), 2),
                      round(float(np.median(flux)), 2),
                      round(float(np.max(flux)), 2))
    except Exception as exc:
        print(path.name, "ERROR:", exc)

print("\n3. REFINED CANDIDATE COUNTS")

candidate_path = BASE / "results/ASK033/refined_candidates.csv"
if candidate_path.exists():
    import csv
    with candidate_path.open(newline="") as f:
        rows = list(csv.DictReader(f))
    print("Refined candidates:", len(rows))
    print("CSV columns:", list(rows[0].keys()) if rows else "No rows")
else:
    print("Refined candidate CSV not found.")

print("\n4. ORIGINAL SECTION IMAGE DIMENSIONS")

for path in sorted((BASE / "results/ASK033").glob("ASK033_section_*.jpg")):
    try:
        from PIL import Image
        with Image.open(path) as im:
            print(path.name, im.size, im.mode)
    except Exception as exc:
        print(path.name, "ERROR:", exc)

print("\n5. PHASE 30 SUMMARY")
print("No plate solving was performed.")
print("No existing project results were modified.")
print("\nPHASE 30 DIAGNOSTIC COMPLETE")
