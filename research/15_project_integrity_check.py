from pathlib import Path
import json
import py_compile
import sys

ROOT = Path.cwd()

required = [
    "research/11_render_catalogue_fisheye.py",
    "research/12_blind_catalogue_calibration.py",
    "research/13_robustness_validation.py",
    "research/14_generate_documentation.py",
    "research/data/catalogue/hipparcos_bright_stars.csv",
    "research/data/catalogue/hipparcos_positions_2026.csv",
    "research/data/catalogue/visible_sky_rouen_2026.csv",
    "research/data/synthetic/catalogue_fisheye_observation.npy",
    "research/data/synthetic/catalogue_fisheye_ground_truth.csv",
    "research/results/blind_catalogue_matches.csv",
    "research/results/blind_fisheye_calibration.json",
    "research/results/blind_calibration_residuals.csv",
    "research/results/phase13_robustness_report.json",
    "research/results/phase13_summary.csv",
    "research/docs/state_of_art.md",
    "research/docs/feasibility_study.md",
    "research/docs/functional_technical_specifications.md",
    "research/docs/risk_analysis.md",
    "research/docs/test_plan_and_results.md",
    "research/docs/project_schedule_gantt.md",
    "research/docs/final_report.md",
    "research/docs/presentation_outline.md",
    "research/docs/README_RESEARCH.md",
]

print("=" * 65)
print("STARLOC 2.0 — PROJECT INTEGRITY CHECK")
print("=" * 65)

missing = []

for item in required:
    path = ROOT / item
    if path.is_file() and path.stat().st_size > 0:
        print(f"[OK]      {item}")
    else:
        print(f"[MISSING] {item}")
        missing.append(item)

print("\nPYTHON SOURCE VALIDATION")
print("-" * 65)

scripts = sorted((ROOT / "research").glob("*.py"))
syntax_errors = []

for script in scripts:
    try:
        py_compile.compile(str(script), doraise=True)
        print(f"[PASS] {script.relative_to(ROOT)}")
    except py_compile.PyCompileError as error:
        print(f"[FAIL] {script.relative_to(ROOT)}")
        print(error)
        syntax_errors.append(str(script))

print("\nCALIBRATION RESULT")
print("-" * 65)

calibration_file = ROOT / "research/results/blind_fisheye_calibration.json"

if calibration_file.exists():
    calibration = json.loads(calibration_file.read_text())
    print(json.dumps(calibration, indent=2))
else:
    print("Calibration JSON unavailable.")

print("\nFINAL CHECK")
print("-" * 65)
print("Required files:", len(required))
print("Missing files:", len(missing))
print("Python scripts checked:", len(scripts))
print("Syntax errors:", len(syntax_errors))

if missing or syntax_errors:
    print("\nINTEGRITY CHECK: FAILED")
    sys.exit(1)

print("\nINTEGRITY CHECK: PASSED")
