import csv
import json
import re
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo

import numpy as np
from astropy.coordinates import SkyCoord, EarthLocation, AltAz
from astropy.time import Time
import astropy.units as u

ROOT = Path.cwd()
CATALOGUE = ROOT / "research/data/catalogue/hipparcos_positions_2026.csv"
OUT = ROOT / "research/real_image/results/ASK033"
OUT.mkdir(parents=True, exist_ok=True)

if not CATALOGUE.exists():
    raise SystemExit(f"Hipparcos catalogue not found: {CATALOGUE}")

# Observation information read from the ASK033 image.
LOCAL_TIME = datetime(
    2026, 11, 20, 20, 21, 52,
    tzinfo=ZoneInfo("Europe/Vienna")
)
UTC_TIME = LOCAL_TIME.astimezone(ZoneInfo("UTC"))

# The displayed timestamp is not yet verified as exposure start or midpoint.
# We use it provisionally as the reference epoch.
observation_time = Time(UTC_TIME)

location = EarthLocation(
    lat=47.834 * u.deg,
    lon=16.005 * u.deg,
    height=0 * u.m
)

with open(CATALOGUE, newline="", encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    rows = list(reader)
    columns = reader.fieldnames or []

if not rows:
    raise SystemExit("Hipparcos catalogue is empty")

def normalise(name):
    return re.sub(r"[^a-z0-9]", "", name.lower())

normalised = {normalise(c): c for c in columns}

def find_column(candidates):
    for candidate in candidates:
        if normalise(candidate) in normalised:
            return normalised[normalise(candidate)]
    return None

ra_col = find_column([
    "ra_deg_2026", "ra_2026_deg", "ra_propagated_deg",
    "ra_epoch_deg", "ra_deg", "ra_icrs", "ra"
])
dec_col = find_column([
    "dec_deg_2026", "dec_2026_deg", "dec_propagated_deg",
    "dec_epoch_deg", "dec_deg", "dec_icrs", "dec"
])
mag_col = find_column([
    "vmag", "v_mag", "magnitude", "mag", "phot_g_mean_mag"
])
hip_col = find_column(["hip", "hip_id", "hipparcos", "hipparcos_id"])

print("\nHIPPARCOS INPUT")
print("File:", CATALOGUE)
print("Rows:", len(rows))
print("Columns:", columns)
print("Selected RA:", ra_col)
print("Selected Dec:", dec_col)
print("Selected magnitude:", mag_col)
print("Selected HIP ID:", hip_col)

if not ra_col or not dec_col:
    raise SystemExit(
        "Could not identify RA/Dec columns. "
        "Use the printed column list to map the correct fields."
    )

def number(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return float("nan")

ra_values = np.array([number(r.get(ra_col)) for r in rows])
dec_values = np.array([number(r.get(dec_col)) for r in rows])

valid = (
    np.isfinite(ra_values) &
    np.isfinite(dec_values) &
    (ra_values >= 0) & (ra_values < 360) &
    (dec_values >= -90) & (dec_values <= 90)
)

if valid.sum() == 0:
    raise SystemExit("No valid celestial coordinates found.")

# Do not silently interpret an hour-angle catalogue as degrees.
if np.nanmax(ra_values[valid]) <= 24 and "hour" in ra_col.lower():
    raise SystemExit(
        "RA appears to be in hours. Convert to degrees before continuing."
    )

filtered_rows = [r for r, ok in zip(rows, valid) if ok]
ra_values = ra_values[valid]
dec_values = dec_values[valid]

coords = SkyCoord(
    ra=ra_values * u.deg,
    dec=dec_values * u.deg,
    frame="icrs"
)

frame = AltAz(
    obstime=observation_time,
    location=location,
    pressure=0 * u.hPa
)
horizontal = coords.transform_to(frame)

alt = horizontal.alt.deg
az = horizontal.az.deg

output = []
for i, row in enumerate(filtered_rows):
    magnitude = number(row.get(mag_col)) if mag_col else float("nan")

    if not np.isfinite(alt[i]) or alt[i] <= 5:
        continue

    output.append({
        "hip_id": row.get(hip_col, "") if hip_col else "",
        "ra_deg": float(ra_values[i]),
        "dec_deg": float(dec_values[i]),
        "altitude_deg": float(alt[i]),
        "azimuth_deg": float(az[i]),
        "magnitude": magnitude
    })

output.sort(
    key=lambda r: (
        r["magnitude"] if np.isfinite(r["magnitude"]) else 99
    )
)

csv_path = OUT / "ASK033_visible_hipparcos_catalogue.csv"
fields = [
    "hip_id", "ra_deg", "dec_deg",
    "altitude_deg", "azimuth_deg", "magnitude"
]
with open(csv_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerows(output)

report = {
    "camera": "ASK033",
    "location": {
        "latitude_deg": 47.834,
        "longitude_deg": 16.005,
        "height_m_assumed": 0
    },
    "displayed_local_time": LOCAL_TIME.isoformat(),
    "converted_utc_time": UTC_TIME.isoformat(),
    "time_interpretation": "Provisional: displayed time treated as observation reference time",
    "exposure_seconds": 50,
    "exposure_midpoint_verified": False,
    "catalogue_source": str(CATALOGUE),
    "catalogue_input_rows": len(rows),
    "valid_coordinate_rows": int(valid.sum()),
    "visible_stars_altitude_above_5deg": len(output),
    "ra_column": ra_col,
    "dec_column": dec_col,
    "magnitude_column": mag_col,
    "hip_id_column": hip_col,
    "refraction": "Disabled",
    "warning": "Catalogue coordinates are used as supplied in the 2026 propagated file. Proper-motion epoch and source astrometry must be checked before final calibration."
}
(OUT / "ASK033_catalogue_metadata.json").write_text(
    json.dumps(report, indent=2)
)

print("\nSTARLOC 2.0 — PHASE 20")
print("=" * 58)
print("Displayed local time:", LOCAL_TIME.isoformat())
print("Provisional UTC time:", UTC_TIME.isoformat())
print("Valid catalogue coordinates:", int(valid.sum()))
print("Visible stars above 5 degrees:", len(output))
print("Output:", csv_path.resolve())
print("Metadata:", (OUT / "ASK033_catalogue_metadata.json").resolve())
print("\nPHASE 20 COMPLETE")
