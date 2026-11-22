from pathlib import Path
import numpy as np
from astropy.table import Table

INPUT = Path("research/data/catalogue/hipparcos_bright_stars.xml")
OUTPUT = Path("research/data/catalogue/hipparcos_bright_stars.csv")

print("=" * 60)
print("STARLOC 2.0 — HIPPARCOS CATALOGUE CLEANING")
print("=" * 60)

if not INPUT.exists():
    raise SystemExit(f"Missing input: {INPUT}")

table = Table.read(INPUT, format="votable")
print("Downloaded rows:", len(table))
print("Columns:", table.colnames)

def numeric_column(name):
    result = []

    for value in table[name]:
        if np.ma.is_masked(value):
            result.append(np.nan)
            continue

        text = str(value).strip()

        if text in ("", "?", "--", "None", "nan"):
            result.append(np.nan)
            continue

        try:
            result.append(float(text))
        except ValueError:
            result.append(np.nan)

    return np.asarray(result, dtype=float)

hip = numeric_column("hip_number")
ra = numeric_column("ra_deg")
dec = numeric_column("dec_deg")
vmag = numeric_column("vmag")
pm_ra = numeric_column("pm_ra")
pm_dec = numeric_column("pm_dec")

# Coordinates and magnitude are essential.
valid = (
    np.isfinite(hip) &
    np.isfinite(ra) &
    np.isfinite(dec) &
    np.isfinite(vmag) &
    (ra >= 0) & (ra < 360) &
    (dec >= -90) & (dec <= 90) &
    (vmag <= 6.5)
)

clean = Table()
clean["hip_number"] = hip[valid].astype(np.int64)
clean["ra_deg"] = ra[valid]
clean["dec_deg"] = dec[valid]
clean["vmag"] = vmag[valid]

# Missing proper motions are retained as NaN.
clean["pm_ra_mas_yr"] = pm_ra[valid]
clean["pm_dec_mas_yr"] = pm_dec[valid]

clean.sort("vmag")
clean.write(OUTPUT, format="csv", overwrite=True)

print("\nCLEANING SUCCESSFUL")
print("Original rows:", len(table))
print("Valid stars:", len(clean))
print("Rejected rows:", len(table) - len(clean))
print("Missing PM_RA:", np.sum(~np.isfinite(pm_ra[valid])))
print("Missing PM_Dec:", np.sum(~np.isfinite(pm_dec[valid])))

print("\nBRIGHTEST 15 STARS")
print(clean[:15])

print("\nSaved:", OUTPUT)
print("CATALOGUE CLEANING COMPLETE")
