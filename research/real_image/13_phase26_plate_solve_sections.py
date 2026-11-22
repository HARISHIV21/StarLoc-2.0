from pathlib import Path
import subprocess
import json
import time

ROOT = Path("research/real_image")
IMAGE_DIR = ROOT / "results" / "ASK033"
ASTROMETRY_DIR = ROOT / "astrometry"
INDEX_DIR = ASTROMETRY_DIR / "indexes"
CONFIG = ASTROMETRY_DIR / "astrometry.cfg"
OUTPUT_DIR = ROOT / "results" / "ASK033" / "plate_solutions"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

sections = sorted(IMAGE_DIR.glob("ASK033_section_*.jpg"))

report = {
    "phase": 26,
    "method": "Astrometry.net independent section plate solving",
    "image_source": "Public AllSkyKamera ASK033 image",
    "sections_tested": len(sections),
    "index_directory": str(INDEX_DIR.resolve()),
    "results": []
}

print("=" * 65)
print("STARLOC 2.0 — PHASE 26")
print("REAL IMAGE SECTION PLATE SOLVING")
print("=" * 65)

if not CONFIG.exists():
    raise FileNotFoundError("Astrometry configuration is missing.")

if len(list(INDEX_DIR.glob("index-*.fits"))) != 10:
    raise RuntimeError("Expected 10 index files. Check Phase 25.")

for image in sections:
    name = image.stem
    out = OUTPUT_DIR / name
    print("\nSolving:", name, flush=True)

    command = [
        "solve-field",
        "--backend-config", str(CONFIG.resolve()),
        "--overwrite",
        "--no-plots",
        "--dir", str(OUTPUT_DIR.resolve()),
        "--out", name,
        "--scale-units", "degwidth",
        "--scale-low", "15",
        "--scale-high", "80",
        "--downsample", "2",
        "--cpulimit", "180",
        str(image.resolve())
    ]

    start = time.time()
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=240
        )
        elapsed = round(time.time() - start, 2)

        solved = Path(str(out) + ".solved").exists()
        wcs = Path(str(out) + ".wcs").exists()
        rdls = Path(str(out) + ".rdls").exists()

        item = {
            "section": name,
            "solved": solved,
            "wcs_created": wcs,
            "rdls_created": rdls,
            "return_code": result.returncode,
            "elapsed_seconds": elapsed,
            "stdout_tail": result.stdout[-1800:],
            "stderr_tail": result.stderr[-1000:]
        }

        if solved:
            print("  PLATE SOLVE: SUCCESS")
        else:
            print("  PLATE SOLVE: NOT SOLVED")

        print("  Time:", elapsed, "seconds")

    except subprocess.TimeoutExpired:
        item = {
            "section": name,
            "solved": False,
            "error": "Timeout after 240 seconds"
        }
        print("  TIMEOUT")

    report["results"].append(item)

    (OUTPUT_DIR / (name + "_solver_log.txt")).write_text(
        item.get("stdout_tail", "") + "\n" +
        item.get("stderr_tail", ""),
        encoding="utf-8"
    )

report["successful_sections"] = sum(
    1 for item in report["results"] if item.get("solved")
)
report["failed_sections"] = (
    report["sections_tested"] - report["successful_sections"]
)

report_path = ROOT / "phase26_plate_solve_report.json"
report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

print("\n" + "=" * 65)
print("PHASE 26 SUMMARY")
print("=" * 65)
print("Sections tested:", report["sections_tested"])
print("Successful solves:", report["successful_sections"])
print("Unsolved sections:", report["failed_sections"])
print("Report:", report_path.resolve())
print("\nPHASE 26 COMPLETE")
