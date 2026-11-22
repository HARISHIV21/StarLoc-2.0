import csv
import json
from pathlib import Path
from collections import Counter

OUT = Path("research/real_image/results/ASK033")
SOURCE = Path("research/data/catalogue/hipparcos_positions_2026.csv")
DEST = OUT / "ASK033_visible_hipparcos_catalogue.csv"

with open(SOURCE, newline="", encoding="utf-8-sig") as f:
    source_rows = list(csv.DictReader(f))

with open(DEST, newline="", encoding="utf-8") as f:
    visible_rows = list(csv.DictReader(f))

by_id = {r["hip_number"]: r for r in source_rows}

corrected = []
for row in visible_rows:
    # Recover the original HIP number using the propagated coordinates.
    match = min(
        source_rows,
        key=lambda r: (
            float(r["ra_2026_deg"]) - float(row["ra_deg"])
        )**2 + (
            float(r["dec_2026_deg"]) - float(row["dec_deg"])
        )**2
    )
    row["hip_id"] = match["hip_number"]
    corrected.append(row)

fields = [
    "hip_id", "ra_deg", "dec_deg",
    "altitude_deg", "azimuth_deg", "magnitude"
]

with open(DEST, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerows(corrected)

mags = [float(r["magnitude"]) for r in corrected]
bins = {
    "mag_le_2": sum(m <= 2 for m in mags),
    "mag_2_to_3": sum(2 < m <= 3 for m in mags),
    "mag_3_to_4": sum(3 < m <= 4 for m in mags),
    "mag_4_to_5": sum(4 < m <= 5 for m in mags),
    "mag_5_to_6_5": sum(5 < m <= 6.5 for m in mags)
}

report = {
    "catalogue_stars": len(corrected),
    "unique_hip_ids": len(set(r["hip_id"] for r in corrected)),
    "magnitude_distribution": bins,
    "catalogue_file": str(DEST)
}
(OUT / "ASK033_catalogue_id_validation.json").write_text(
    json.dumps(report, indent=2)
)

print("\nSTARLOC — PHASE 20B")
print("=" * 50)
print("Visible catalogue rows:", len(corrected))
print("Unique HIP identifiers:", report["unique_hip_ids"])
print("Magnitude distribution:")
for key, value in bins.items():
    print(key, ":", value)
print("Saved:", DEST.resolve())

if len(corrected) != len(set(r["hip_id"] for r in corrected)):
    raise SystemExit("ERROR: duplicate HIP identifiers detected")

print("\nPHASE 20B COMPLETE")
