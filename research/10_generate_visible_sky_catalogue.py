from pathlib import Path
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import csv
import json

import astropy.units as u
from astropy.coordinates import SkyCoord, EarthLocation, AltAz
from astropy.time import Time

ROOT = Path(__file__).resolve().parents[1]

INPUT = ROOT / "research/data/catalogue/hipparcos_positions_2026.csv"
OUTPUT = ROOT / "research/data/catalogue/visible_sky_rouen_2026.csv"
METADATA = ROOT / "research/data/catalogue/visible_sky_rouen_metadata.json"

# TEMPORARY TEST SITE ONLY — NOT THE CONFIRMED ALLSKYKAMERA LOCATION
SITE = {
    "name": "Rouen temporary test location",
    "latitude_deg": 49.4431,
    "longitude_deg": 1.0993,
    "height_m": 20.0
}

# Fixed local observation time for reproducible testing.
LOCAL_DATETIME = datetime(
    2026, 11, 20, 22, 0, 0,
    tzinfo=ZoneInfo("Europe/Paris")
)

MIN_ALTITUDE_DEG = 5.0
MAX_MAGNITUDE = 6.5

def main():
    if not INPUT.exists():
        raise FileNotFoundError(f"Missing input catalogue: {INPUT}")

    observation_utc = LOCAL_DATETIME.astimezone(timezone.utc)
    observation_time = Time(observation_utc)

    location = EarthLocation(
        lat=SITE["latitude_deg"] * u.deg,
        lon=SITE["longitude_deg"] * u.deg,
        height=SITE["height_m"] * u.m
    )

    with INPUT.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    if not rows:
        raise RuntimeError("The propagated Hipparcos catalogue is empty.")

    required = {
        "hip_number", "vmag", "ra_2026_deg", "dec_2026_deg"
    }
    missing = required - set(rows[0].keys())
    if missing:
        raise RuntimeError(f"Missing catalogue columns: {sorted(missing)}")

    valid = []
    for row in rows:
        try:
            ra = float(row["ra_2026_deg"])
            dec = float(row["dec_2026_deg"])
            magnitude = float(row["vmag"])
            hip = int(float(row["hip_number"]))
            if all(map(lambda x: x == x, [ra, dec, magnitude])):
                valid.append((hip, ra, dec, magnitude))
        except (ValueError, TypeError):
            continue

    if not valid:
        raise RuntimeError("No valid catalogue coordinates found.")

    coordinates = SkyCoord(
        ra=[r[1] for r in valid] * u.deg,
        dec=[r[2] for r in valid] * u.deg,
        frame="icrs"
    )

    frame = AltAz(
        obstime=observation_time,
        location=location,
        pressure=0 * u.hPa
    )

    horizontal = coordinates.transform_to(frame)

    output_rows = []
    for star, alt, az in zip(valid, horizontal.alt.deg, horizontal.az.deg):
        hip, ra, dec, magnitude = star

        if alt >= MIN_ALTITUDE_DEG and magnitude <= MAX_MAGNITUDE:
            output_rows.append({
                "hip_number": hip,
                "ra_deg": ra,
                "dec_deg": dec,
                "vmag": magnitude,
                "altitude_deg": float(alt),
                "azimuth_deg": float(az)
            })

    output_rows.sort(key=lambda r: r["vmag"])

    with OUTPUT.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(output_rows[0].keys()))
        writer.writeheader()
        writer.writerows(output_rows)

    metadata = {
        "dataset_type": "Real Hipparcos catalogue transformed to local horizontal coordinates",
        "catalogue": "Hipparcos",
        "input_stars": len(rows),
        "valid_stars": len(valid),
        "visible_stars": len(output_rows),
        "minimum_altitude_deg": MIN_ALTITUDE_DEG,
        "maximum_visual_magnitude": MAX_MAGNITUDE,
        "observation_local": LOCAL_DATETIME.isoformat(),
        "observation_utc": observation_utc.isoformat(),
        "site": SITE,
        "site_status": "TEMPORARY TEST LOCATION — NOT CONFIRMED CAMERA LOCATION",
        "atmospheric_refraction": "Disabled",
        "output_coordinates": "Altitude and azimuth, degrees",
        "limitations": [
            "This is a catalogue visibility calculation, not an actual camera observation.",
            "Camera orientation and lens projection are not yet applied.",
            "A real AllSkyKamera image, its timestamp and actual location are required for final real-camera validation."
        ]
    }

    METADATA.write_text(json.dumps(metadata, indent=4), encoding="utf-8")

    print("\nSTARLOC 2.0 — REAL CATALOGUE SKY PROJECTION")
    print("=" * 55)
    print("Catalogue stars:", len(rows))
    print("Valid propagated positions:", len(valid))
    print("Visible stars:", len(output_rows))
    print("Minimum altitude:", MIN_ALTITUDE_DEG, "degrees")
    print("Magnitude limit:", MAX_MAGNITUDE)
    print("Test site:", SITE["name"])
    print("Observation local:", LOCAL_DATETIME.isoformat())
    print("Observation UTC:", observation_utc.isoformat())

    print("\nBRIGHTEST VISIBLE STARS")
    for star in output_rows[:15]:
        print(
            f"HIP {star['hip_number']:6d} | "
            f"Mag {star['vmag']:5.2f} | "
            f"Alt {star['altitude_deg']:7.2f}° | "
            f"Az {star['azimuth_deg']:7.2f}°"
        )

    print("\nSAVED:")
    print(OUTPUT)
    print(METADATA)
    print("\nVISIBLE-SKY CATALOGUE COMPLETE")

if __name__ == "__main__":
    main()
