from urllib.request import Request, urlopen
from urllib.parse import urlencode
from pathlib import Path

ENDPOINTS = [
    "https://tapvizier.cds.unistra.fr/TAPVizieR/tap/sync",
    "https://tapvizier.u-strasbg.fr/TAPVizieR/tap/sync",
]

OUTPUT = Path("research/data/catalogue")
OUTPUT.mkdir(parents=True, exist_ok=True)

def tap_query(endpoint, query):
    payload = urlencode({
        "REQUEST": "doQuery",
        "LANG": "ADQL",
        "FORMAT": "csv",
        "QUERY": query,
    }).encode("utf-8")

    request = Request(
        endpoint,
        data=payload,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )

    with urlopen(request, timeout=120) as response:
        return response.read().decode("utf-8", errors="replace")

metadata_query = """
SELECT TOP 30 column_name, datatype
FROM TAP_SCHEMA.columns
WHERE table_name = 'I/239/hip_main'
"""

sample_query = """
SELECT TOP 10 *
FROM "I/239/hip_main"
"""

for endpoint in ENDPOINTS:
    print("\nTrying:", endpoint)

    try:
        print("\n--- HIPPARCOS TABLE COLUMNS ---")
        metadata = tap_query(endpoint, metadata_query)
        print(metadata[:5000])

        print("\n--- SAMPLE CATALOGUE ROWS ---")
        sample = tap_query(endpoint, sample_query)
        print(sample[:5000])

        (OUTPUT / "hipparcos_tap_sample.csv").write_text(sample)
        (OUTPUT / "hipparcos_tap_columns.csv").write_text(metadata)

        print("\nTAP CONNECTION SUCCESSFUL")
        print("Saved column metadata and sample catalogue.")
        break

    except Exception as error:
        print("Endpoint failed:", repr(error))
else:
    raise SystemExit(
        "\nBoth TAP endpoints failed. Send me this complete output."
    )
