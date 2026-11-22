from pathlib import Path
import csv
import json
import subprocess
import time
import numpy as np
from astropy.io import fits

BASE = Path("research/real_image")
RESULTS = BASE / "results/ASK033"
INPUT = RESULTS / "refined_candidates.csv"
OUT = RESULTS / "custom_source_catalogues"
SOLVE = RESULTS / "custom_plate_solutions"

OUT.mkdir(parents=True, exist_ok=True)
SOLVE.mkdir(parents=True, exist_ok=True)

SECTION = "R2C2"
OFFSET_X, OFFSET_Y = 640, 480
IMAGE_W, IMAGE_H = 640, 480

print("=" * 65)
print("STARLOC 2.0 — PHASE 32")
print("CUSTOM SOURCE CATALOGUE AND PLATE-SOLVE TEST")
print("=" * 65)

with INPUT.open(newline="") as f:
    rows = list(csv.DictReader(f))

selected = [
    r for r in rows
    if r["section"].strip() == SECTION
]

if len(selected) < 10:
    raise RuntimeError("Insufficient candidates for selected section.")

x_global = np.array([float(r["x"]) for r in selected])
y_global = np.array([float(r["y"]) for r in selected])
snr = np.array([float(r["snr"]) for r in selected])

# Convert global image coordinates to section-local coordinates.
# OpenCV-style pixel-centre coordinates are converted to Astrometry.net
# FITS XY convention by adding one pixel.
x_local = x_global - OFFSET_X + 1.0
y_local = y_global - OFFSET_Y + 1.0

valid = (
    np.isfinite(x_local) &
    np.isfinite(y_local) &
    np.isfinite(snr) &
    (x_local >= 1) & (x_local <= IMAGE_W) &
    (y_local >= 1) & (y_local <= IMAGE_H)
)

x_local = x_local[valid]
y_local = y_local[valid]
snr = snr[valid]

if len(x_local) < 10:
    raise RuntimeError("Too few valid local coordinates.")

# Use SNR as a relative flux proxy; it is not a photometric flux.
flux = np.maximum(snr, 0.01)

catalogue_path = OUT / f"{SECTION}_custom.xyls"

primary = fits.PrimaryHDU()
primary.header["IMAGEW"] = IMAGE_W
primary.header["IMAGEH"] = IMAGE_H
primary.header["AN_FILE"] = "XYLS"

columns = [
    fits.Column(name="X", format="D", array=x_local),
    fits.Column(name="Y", format="D", array=y_local),
    fits.Column(name="FLUX", format="D", array=flux)
]

table = fits.BinTableHDU.from_columns(columns)
table.header["IMAGEW"] = IMAGE_W
table.header["IMAGEH"] = IMAGE_H

fits.HDUList([primary, table]).writeto(
    catalogue_path, overwrite=True
)

print("\nCUSTOM CATALOGUE")
print("Section:", SECTION)
print("Candidates:", len(x_local))
print("X range:", round(float(x_local.min()), 2),
      "to", round(float(x_local.max()), 2))
print("Y range:", round(float(y_local.min()), 2),
      "to", round(float(y_local.max()), 2))
print("Median SNR:", round(float(np.median(snr)), 2))
print("FITS:", catalogue_path)

# Verify the FITS catalogue before invoking the solver.
with fits.open(catalogue_path) as hdul:
    data = hdul[1].data
    assert len(data) == len(x_local)
    assert all(name in data.names for name in ("X", "Y", "FLUX"))

config = BASE / "astrometry/astrometry.cfg"
if not config.exists():
    raise FileNotFoundError(config)

command = [
    "solve-field",
    "--backend-config", str(config.resolve()),
    "--overwrite",
    "--no-plots",
    "--dir", str(SOLVE.resolve()),
    "--out", f"{SECTION}_custom",
    "--scale-units", "degwidth",
    "--scale-low", "15",
    "--scale-high", "80",
    "--quad-size-min", "0.05",
    "--pixel-error", "2",
    "--cpulimit", "60",
    str(catalogue_path.resolve())
]

print("\nPLATE SOLVE COMMAND")
print(" ".join(command))
print("\nRunning one controlled test (maximum 90 seconds)...")

start = time.time()
try:
    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        errors="replace",
        timeout=90
    )
    stdout = result.stdout or ""
    stderr = result.stderr or ""
    return_code = result.returncode
    timed_out = False
except subprocess.TimeoutExpired as exc:
    stdout = exc.stdout or ""
    stderr = exc.stderr or ""
    if isinstance(stdout, bytes):
        stdout = stdout.decode("utf-8", errors="replace")
    if isinstance(stderr, bytes):
        stderr = stderr.decode("utf-8", errors="replace")
    return_code = None
    timed_out = True

elapsed = time.time() - start

log_path = SOLVE / f"{SECTION}_custom_solver.log"
log_path.write_text(
    "STDOUT\n" + stdout + "\nSTDERR\n" + stderr,
    encoding="utf-8"
)

wcs_path = SOLVE / f"{SECTION}_custom.wcs"
rdls_path = SOLVE / f"{SECTION}_custom.rdls"
solved_path = SOLVE / f"{SECTION}_custom.solved"

solved = (
    solved_path.exists() and
    solved_path.stat().st_size > 0 and
    wcs_path.exists() and
    wcs_path.stat().st_size > 0
)

report = {
    "phase": 32,
    "section": SECTION,
    "method": "Custom FITS XYLS source catalogue",
    "candidate_count": int(len(x_local)),
    "median_snr": float(np.median(snr)),
    "scale_low_deg": 15,
    "scale_high_deg": 80,
    "return_code": return_code,
    "timed_out": timed_out,
    "elapsed_seconds": round(elapsed, 2),
    "solved": solved,
    "wcs_created": wcs_path.exists(),
    "rdls_created": rdls_path.exists(),
    "catalogue": str(catalogue_path),
    "log": str(log_path)
}

report_path = BASE / "phase32_custom_solve_report.json"
report_path.write_text(json.dumps(report, indent=2))

print("\n" + "=" * 65)
print("PHASE 32 RESULT")
print("=" * 65)
print(json.dumps(report, indent=2))
print("\nSOLVER OUTPUT (last 30 lines)")
print("\n".join((stdout + "\n" + stderr).splitlines()[-30:]))
print("\nReport:", report_path)
print("Log:", log_path)
print("\nPHASE 32 COMPLETE")
