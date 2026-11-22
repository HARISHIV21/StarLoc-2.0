from pathlib import Path
import urllib.request
import json
import hashlib
import time

ROOT = Path("research/real_image/astrometry")
INDEX_DIR = ROOT / "indexes"
INDEX_DIR.mkdir(parents=True, exist_ok=True)

BASE = "https://data.astrometry.net/4100/"
SCALES = range(4110, 4120)

report = {
    "phase": 25,
    "source": BASE,
    "index_files": [],
    "total_bytes": 0,
    "failures": []
}

print("\nSTARLOC 2.0 — PHASE 25")
print("=" * 60)

for scale in SCALES:
    filename = f"index-{scale}.fits"
    destination = INDEX_DIR / filename
    url = BASE + filename

    if destination.exists() and destination.stat().st_size > 1000:
        print("Already downloaded:", filename)
    else:
        print("\nDownloading:", filename)
        request = urllib.request.Request(
            url, headers={"User-Agent": "StarLoc2.0-research/1.0"}
        )
        try:
            with urllib.request.urlopen(request, timeout=180) as response:
                content = response.read()

            if len(content) < 1000:
                raise ValueError("Downloaded file is unexpectedly small")

            destination.write_bytes(content)
            print("Downloaded:", round(len(content) / 1024, 1), "KB")

        except Exception as exc:
            print("FAILED:", filename, str(exc))
            report["failures"].append({
                "file": filename,
                "error": str(exc)
            })
            continue

    content = destination.read_bytes()
    digest = hashlib.sha256(content).hexdigest()

    report["index_files"].append({
        "filename": filename,
        "bytes": len(content),
        "sha256": digest
    })
    report["total_bytes"] += len(content)

# Local configuration: no modification to Homebrew files.
config = ROOT / "astrometry.cfg"
config.write_text(
    "# StarLoc 2.0 local Astrometry.net configuration\n"
    f"add_path {INDEX_DIR.resolve()}\n"
    "autoindex\n",
    encoding="utf-8"
)

report["index_directory"] = str(INDEX_DIR.resolve())
report["configuration"] = str(config.resolve())
report["successful_index_count"] = len(report["index_files"])
report["failed_index_count"] = len(report["failures"])

(ROOT / "phase25_index_download_report.json").write_text(
    json.dumps(report, indent=2),
    encoding="utf-8"
)

print("\nINDEX SUMMARY")
print("Successful indexes:", len(report["index_files"]), "/ 10")
print("Failed indexes:", len(report["failures"]))
print("Total downloaded:", round(report["total_bytes"] / 1024 / 1024, 2), "MB")
print("Configuration:", config.resolve())

print("\nPHASE 25 COMPLETE")
if report["failures"]:
    print("Some downloads failed. Do not start plate solving yet.")
else:
    print("All requested index files are ready.")
