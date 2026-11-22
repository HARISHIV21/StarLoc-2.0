from pathlib import Path
from urllib.request import Request, urlopen
from urllib.parse import urlencode

output_dir = Path("research/data/catalogue")
output_dir.mkdir(parents=True, exist_ok=True)

output_file = output_dir / "hipparcos_raw.tsv"

base_url = "https://vizier.cfa.harvard.edu/viz-bin/asu-tsv"

params = {
    "-source": "I/239/hip_main",
    "-out": "HIP,RAhms,DEdms,Vmag",
    "-out.max": "unlimited",
    "Vmag": "<6",
}

url = base_url + "?" + urlencode(params)

request = Request(
    url,
    headers={"User-Agent": "StarLoc2.0 research project"}
)

print("Connecting to Harvard VizieR mirror...")
print("Catalogue: Hipparcos I/239/hip_main")
print("Filter: visual magnitude below 6")

try:
    with urlopen(request, timeout=90) as response:
        data = response.read()
        print("HTTP status:", response.status)

    if not data:
        raise RuntimeError("Empty response received.")

    text = data.decode("utf-8", errors="replace")

    if "<html" in text[:1000].lower():
        raise RuntimeError(
            "Received an HTML page instead of TSV catalogue data."
        )

    output_file.write_text(text, encoding="utf-8")

    print("\nDOWNLOAD SUCCESSFUL")
    print("Saved:", output_file)
    print("Size:", f"{len(data) / 1024:.1f} KB")

    print("\nCATALOGUE PREVIEW")
    print("-----------------")
    for line in text.splitlines()[:18]:
        print(line)

except Exception as error:
    print("\nDOWNLOAD FAILED")
    print(repr(error))
    raise SystemExit(1)
