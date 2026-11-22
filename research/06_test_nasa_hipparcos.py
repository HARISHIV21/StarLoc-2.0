from pathlib import Path
from urllib.request import Request, urlopen
from urllib.parse import urlencode
from astropy.table import Table
from io import BytesIO

BASE_URL = "https://heasarc.gsfc.nasa.gov/xamin/vo/tap/sync"
OUTPUT = Path("research/data/catalogue/hipparcos_sample.xml")

query = """
SELECT TOP 10
    HIP_Number, RA_Deg, Dec_Deg, Vmag, PM_RA, PM_Dec
FROM hipparcos
WHERE Vmag < 6
"""

params = {
    "REQUEST": "doQuery",
    "LANG": "ADQL",
    "FORMAT": "votable",
    "QUERY": query
}

request = Request(
    BASE_URL,
    data=urlencode(params).encode("utf-8"),
    headers={"User-Agent": "StarLoc2.0/1.0"}
)

print("=" * 55)
print("STARLOC 2.0 — NASA HIPPARCOS CONNECTION TEST")
print("=" * 55)
print("Connecting to NASA HEASARC TAP...")

try:
    with urlopen(request, timeout=90) as response:
        data = response.read()

    if not data:
        raise RuntimeError("Empty response received.")

    if b"<VOTABLE" not in data.upper():
        print(data[:2000].decode("utf-8", errors="replace"))
        raise RuntimeError("Response is not a valid VOTable.")

    table = Table.read(BytesIO(data), format="votable")

    OUTPUT.write_bytes(data)

    print("\nCONNECTION SUCCESSFUL")
    print("Rows received:", len(table))
    print("Columns:", table.colnames)
    print("\nSAMPLE STARS")
    print(table)

    print("\nSaved:", OUTPUT)
    print("Size:", f"{OUTPUT.stat().st_size / 1024:.2f} KB")

except Exception as error:
    print("\nCONNECTION FAILED")
    print(type(error).__name__, str(error))
    raise SystemExit(1)
