from pathlib import Path
import subprocess
import shutil
import json
import time

print("=" * 65)
print("STARLOC 2.0 — PHASE 28")
print("ASTROMETRY.NET COMPATIBILITY FIX AND SINGLE-SECTION TEST")
print("=" * 65)

# Locate the installed Astrometry.net Python utility.
matches = list(
    Path("/opt/homebrew/Cellar/astrometry-net").glob(
        "*/libexec/lib/python3.15/site-packages/astrometry/util/run_command.py"
    )
)

if len(matches) != 1:
    raise RuntimeError(
        "Could not uniquely locate run_command.py: " + str(matches)
    )

target = matches[0]
source = target.read_text(encoding="utf-8")

backup = target.with_suffix(".py.starloc_backup")
if not backup.exists():
    shutil.copy2(target, backup)

updated = source.replace(
    "out.decode()",
    "out.decode(errors='replace')"
).replace(
    "err.decode()",
    "err.decode(errors='replace')"
)

if updated == source:
    if "decode(errors='replace')" not in source:
        raise RuntimeError("Expected decode calls were not found.")
    print("Compatibility fix already present.")
else:
    target.write_text(updated, encoding="utf-8")
    print("Patched:", target)
    print("Backup:", backup)

# Test only R1C1.
image = Path(
    "research/real_image/results/ASK033/ASK033_section_R1C1.jpg"
).resolve()

config = Path(
    "research/real_image/astrometry/astrometry.cfg"
).resolve()

output_dir = Path(
    "research/real_image/results/ASK033/plate_solutions"
).resolve()
output_dir.mkdir(parents=True, exist_ok=True)

name = "ASK033_R1C1_phase28"

command = [
    "solve-field",
    "--backend-config", str(config),
    "--overwrite",
    "--no-plots",
    "--verbose",
    "--dir", str(output_dir),
    "--out", name,
    "--scale-units", "degwidth",
    "--scale-low", "5",
    "--scale-high", "90",
    "--downsample", "2",
    "--cpulimit", "90",
    str(image)
]

print("\nTesting:", image.name)
print("Scale search: 5–90 degrees")
start = time.time()

try:
    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        errors="replace",
        timeout=120
    )
    elapsed = round(time.time() - start, 2)

    log = (
        "COMMAND:\n" + " ".join(command) +
        "\n\nRETURN CODE:\n" + str(result.returncode) +
        "\n\nSTDOUT:\n" + result.stdout +
        "\n\nSTDERR:\n" + result.stderr
    )

    log_path = output_dir / "phase28_R1C1_full_solver_log.txt"
    log_path.write_text(log, encoding="utf-8")

    solved = (output_dir / (name + ".solved")).exists()
    wcs = (output_dir / (name + ".wcs")).exists()

    report = {
        "phase": 28,
        "compatibility_patch_applied": True,
        "test_section": "R1C1",
        "return_code": result.returncode,
        "elapsed_seconds": elapsed,
        "solved": solved,
        "wcs_created": wcs,
        "log": str(log_path)
    }

except subprocess.TimeoutExpired as exc:
    report = {
        "phase": 28,
        "test_section": "R1C1",
        "solved": False,
        "error": "Timeout after 120 seconds"
    }

report_path = Path("research/real_image/phase28_report.json")
report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

print("\nRESULT")
print(json.dumps(report, indent=2))
print("\nPHASE 28 TEST COMPLETE")
