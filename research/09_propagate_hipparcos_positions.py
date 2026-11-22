from pathlib import Path
import csv
import json
import numpy as np
import astropy.units as u
from astropy.time import Time
from astropy.coordinates import SkyCoord

BASE = Path("research/data/catalogue")
INPUT = BASE / "hipparcos_bright_stars.csv"
OUTPUT = BASE / "hipparcos_positions_2026.csv"
METADATA = BASE / "hipparcos_epoch_metadata.json"

REFERENCE_DATE = "2026-11-20T00:00:00"

print("=" * 65)
print("STARLOC 2.0 — HIPPARCOS EPOCH PROPAGATION")
print("=" * 65)

if not INPUT.exists():
    raise SystemExit(f"Catalogue not found: {INPUT}")

with INPUT.open("r", newline="") as file:
    reader = csv.DictReader(file)
    rows = list(reader)
    fieldnames = reader.fieldnames

required = [
    "hip_number", "ra_deg", "dec_deg",
    "vmag", "pm_ra_mas_yr", "pm_dec_mas_yr"
]

missing = [name for name in required if name not in fieldnames]
if missing:
    raise SystemExit(f"Missing columns: {missing}")

ra = np.array([float(row["ra_deg"]) for row in rows])
dec = np.array([float(row["dec_deg"]) for row in rows])
pm_ra = np.array([float(row["pm_ra_mas_yr"]) for row in rows])
pm_dec = np.array([float(row["pm_dec_mas_yr"]) for row in rows])

catalogue_epoch = Time(1991.25, format="jyear")
target_epoch = Time(REFERENCE_DATE, format="isot", scale="utc")

coordinates = SkyCoord(
    ra=ra * u.deg,
    dec=dec * u.deg,
    pm_ra_cosdec=pm_ra * u.mas / u.yr,
    pm_dec=pm_dec * u.mas / u.yr,
    obstime=catalogue_epoch,
    frame="icrs"
)

updated = coordinates.apply_space_motion(new_obstime=target_epoch)
separation = coordinates.separation(updated)

output_fields = fieldnames + [
    "ra_2026_deg",
    "dec_2026_deg",
    "proper_motion_shift_arcsec"
]

with OUTPUT.open("w", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=output_fields)
    writer.writeheader()

    for index, row in enumerate(rows):
        result = dict(row)
        result["ra_2026_deg"] = f"{updated.ra.deg[index]:.10f}"
        result["dec_2026_deg"] = f"{updated.dec.deg[index]:.10f}"
        result["proper_motion_shift_arcsec"] = (
            f"{separation.arcsec[index]:.6f}"
        )
        writer.writerow(result)

metadata = {
    "catalogue": "Hipparcos Main Catalogue",
    "source": "NASA HEASARC",
    "coordinate_frame": "ICRS",
    "catalogue_epoch": "J1991.25",
    "reference_epoch": REFERENCE_DATE,
    "proper_motion_convention": {
        "pm_ra": "mu_alpha*cos(dec), milliarcseconds/year",
        "pm_dec": "mu_delta, milliarcseconds/year"
    },
    "method": "Astropy SkyCoord.apply_space_motion",
    "parallax_included": False,
    "radial_velocity_included": False,
    "note": "Catalogue position propagation only; not camera calibration."
}

METADATA.write_text(json.dumps(metadata, indent=4))

print("\nINPUT STARS:", len(rows))
print("REFERENCE DATE:", REFERENCE_DATE)
print("CATALOGUE EPOCH: J1991.25")
print("COORDINATE FRAME: ICRS")

print("\nPROPER-MOTION SHIFT")
print("Mean:", f"{np.mean(separation.arcsec):.4f} arcsec")
print("Median:", f"{np.median(separation.arcsec):.4f} arcsec")
print("Maximum:", f"{np.max(separation.arcsec):.4f} arcsec")

print("\nBRIGHTEST 10 PROPAGATED STARS")
for row in rows[:10]:
    hip = int(float(row["hip_number"]))
    index = next(
        i for i, item in enumerate(rows)
        if int(float(item["hip_number"])) == hip
    )
    print(
        f"HIP {hip:6d} | "
        f"RA {updated.ra.deg[index]:.6f}° | "
        f"Dec {updated.dec.deg[index]:.6f}°"
    )

print("\nSAVED:")
print(OUTPUT)
print(METADATA)
print("\nEPOCH PROPAGATION COMPLETE")
