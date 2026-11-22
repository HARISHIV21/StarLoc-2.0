from pathlib import Path
import csv
import json
import subprocess
import sys
import time

ROOT = Path.cwd()
RESULTS = ROOT / "research/results"
DOCS = ROOT / "research/docs"

steps = [
    ("Catalogue fisheye observation", "research/11_render_catalogue_fisheye.py"),
    ("Blind catalogue calibration", "research/12_blind_catalogue_calibration.py"),
    ("Robustness validation", "research/13_robustness_validation.py"),
]

print("=" * 65)
print("STARLOC 2.0 — CONSOLIDATED FINAL DEMONSTRATION")
print("=" * 65)

start = time.time()

for name, script in steps:
    print(f"\n>>> {name}")
    print("-" * 65)

    result = subprocess.run(
        [sys.executable, script],
        cwd=ROOT,
        text=True
    )

    if result.returncode != 0:
        raise SystemExit(f"DEMO FAILED at: {name}")

calibration_path = RESULTS / "blind_fisheye_calibration.json"
robustness_path = RESULTS / "phase13_robustness_report.json"

calibration = json.loads(calibration_path.read_text())
robustness = json.loads(robustness_path.read_text())

report = {
    "project": "StarLoc 2.0",
    "demonstration": "Catalogue-based synthetic all-sky fisheye calibration",
    "calibration": calibration,
    "robustness": robustness.get("overall", {}),
    "validation_scope": (
        "Synthetic observation generated using real Hipparcos catalogue data. "
        "Zenith-pointed equidistant fisheye model with unknown roll. "
        "Not yet validated against a real AllSkyKamera exposure."
    ),
    "completed_demo_steps": [name for name, _ in steps],
    "execution_time_seconds": round(time.time() - start, 2)
}

output = RESULTS / "final_demo_report.json"
output.write_text(json.dumps(report, indent=4))

print("\n" + "=" * 65)
print("FINAL DEMONSTRATION SUMMARY")
print("=" * 65)
print("Detected regions:", calibration["detected_regions"])
print("Identified stars:", calibration["identified_stars"])
print("Optical centre:",
      calibration["optical_center_x_px"],
      calibration["optical_center_y_px"])
print("Focal scale:", calibration["focal_scale_px"], "px")
print("Estimated FOV:", calibration["estimated_fov_deg"], "degrees")
print("Estimated roll:", calibration["estimated_roll_deg"], "degrees")
print("Reprojection RMSE:", calibration["rmse_px"], "px")
print("Mean robustness roll error:",
      robustness.get("mean_roll_error_deg", "See robustness report"))
print("Demo execution time:", report["execution_time_seconds"], "seconds")

print("\nREPORT SAVED:")
print(output)

print("\nDEMONSTRATION COMPLETED SUCCESSFULLY")
