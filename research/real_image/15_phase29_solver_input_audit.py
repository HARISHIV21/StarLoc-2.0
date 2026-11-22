from pathlib import Path
import json
import subprocess

from astropy.io import fits

BASE = Path("research/real_image")
OUT = BASE / "results/ASK033/plate_solutions"
INDEX = BASE / "astrometry/indexes"

print("=" * 65)
print("STARLOC 2.0 — PHASE 29")
print("SOLVER INPUT AND INDEX AUDIT")
print("=" * 65)

print("\n1. EXISTING ASTROMETRY SOURCE FILES")

for path in sorted(OUT.glob("*.axy")):
    print("\n", path.name)
    try:
        with fits.open(path) as hdul:
            for i, hdu in enumerate(hdul):
                print(" HDU", i, "type:", type(hdu).__name__)
                print("  dimensions:", hdu.header.get("NAXIS"))
                if getattr(hdu, "data", None) is not None:
                    print("  rows:", len(hdu.data))
                    if getattr(hdu.data, "names", None):
                        print("  columns:", hdu.data.names)
    except Exception as exc:
        print(" Could not inspect:", exc)

print("\n2. INDEX FILE METADATA")

for path in sorted(INDEX.glob("index-*.fits")):
    try:
        with fits.open(path) as hdul:
            print(
                path.name,
                "HDU count:", len(hdul),
                "primary header:", {
                    key: hdul[0].header.get(key)
                    for key in ("NAXIS", "NAXIS1", "NAXIS2", "AN_FILE")
                    if key in hdul[0].header
                }
            )
    except Exception as exc:
        print(path.name, "ERROR:", exc)

print("\n3. PHASE 28 REPORT")

report_path = BASE / "phase28_report.json"
if report_path.exists():
    print(json.dumps(json.loads(report_path.read_text()), indent=2))
else:
    print("No Phase 28 report found.")

print("\n4. SOLVER AND SOURCE-EXTRACTION OPTIONS")

for executable in ("solve-field", "image2xy"):
    result = subprocess.run(
        [executable, "--help"],
        capture_output=True,
        text=True,
        errors="replace",
        timeout=15
    )
    print("\n---", executable, "---")
    print((result.stdout + result.stderr)[:5000])

print("\n5. PHASE 28 OUTPUT FILES")
for path in sorted(OUT.glob("ASK033_R1C1_phase28*")):
    print(path.name, path.stat().st_size, "bytes")

print("\nPHASE 29 AUDIT COMPLETE")
