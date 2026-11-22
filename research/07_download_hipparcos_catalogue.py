from pathlib import Path
from urllib.request import Request, urlopen
from urllib.parse import urlencode
from io import BytesIO

from astropy.table import Table

OUTPUT_DIR = Path("research/data/catalogue")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

TAP_URL = "https://heasarc.gsfc.nasa.gov/xamin/vo/tap/sync"

QUERY = """
SELECT
    HIP_Number,
    RA_Deg,
    Dec_Deg,
    Vmag,
    PM_RA,
    PM_Dec
FROM hipparcos
WHERE Vmag <= 6.5
"""

params = {
    "REQUEST": "doQuery",
    "LANG": "ADQL",
    "FORMAT": "votable",
    "MAXREC": "50000",
    "QUERY": QUERY
}

request = Request(
    TAP_URL,
    data=urlencode(params).encode("utf-8"),
    headers={"User-Agent": "StarLoc2.0/1.0"}
)

print("=" * 60)
print("STARLOC 2.0 — HIPPARCOS BRIGHT-STAR CATALOGUE")
print("=" * 60)
print("Magnitude limit: Vmag <= 6.5")
print("Connecting to NASA HEASARC...")

try:
    with urlopen(request, timeout=180) as response:
        data = response.read()

    if b"<VOTABLE" not in data.upper():
        print(data[:3000].decode("utf-8", errors="replace"))
        raise RuntimeError("NASA did not return a valid VOTable.")

    raw_file = OUTPUT_DIR / "hipparcos_bright_stars.xml"
    raw_file.write_bytes(data)

    table = Table.read(BytesIO(data), format="votable")

    required = [
        "hip_number", "ra_deg", "dec_deg",
        "vmag", "pm_ra", "pm_dec"
    ]

    missing = [name for name in required if name not in table.colnames]
    if missing:
        raise RuntimeError(f"Missing catalogue columns: {missing}")

    clean = Table()

    clean["hip_number"] = table["hip_number"]
    clean["ra_deg"] = table["ra_deg"]
    clean["dec_deg"] = table["dec_deg"]
    clean["vmag"] = table["vmag"]
    clean["pm_ra_mas_yr"] = table["pm_ra"]
    clean["pm_dec_mas_yr"] = table["pm_dec"]

    # Remove invalid coordinates and magnitudes.
    clean = clean[
        (clean["ra_deg"] >= 0) &
        (clean["ra_deg"] < 360) &
        (clean["dec_deg"] >= -90) &
        (clean["dec_deg"] <= 90)
    ]

    csv_file = OUTPUT_DIR / "hipparcos_bright_stars.csv"
    clean.write(csv_file, format="csv", overwrite=True)

    print("\nDOWNLOAD SUCCESSFUL")
    print("Number of valid stars:", len(clean))
    print("Columns:", clean.colnames)

    print("\nFIRST 15 CATALOGUE ENTRIES")
    print(clean[:15])

    print("\nMAGNITUDE RANGE")
    print(
        f"{min(clean['vmag']):.2f} to "
        f"{max(clean['vmag']):.2f}"
    )

    print("\nSAVED FILES")
    print(raw_file)
    print(csv_file)

    print("\nCATALOGUE DOWNLOAD COMPLETE")

except Exception as error:
    print("\nCATALOGUE DOWNLOAD FAILED")
    print(type(error).__name__, str(error))
    raise SystemExit(1)
