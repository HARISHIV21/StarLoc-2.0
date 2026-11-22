from pathlib import Path
import ast
import json
import zipfile
import hashlib
from datetime import datetime, timezone

ROOT = Path.cwd()
RESEARCH = ROOT / "research"
DOCS = RESEARCH / "docs"
REAL = RESEARCH / "real_image"
ASK = REAL / "results" / "ASK033"

required = [
    DOCS / "state_of_art.md",
    DOCS / "feasibility_study.md",
    DOCS / "functional_technical_specifications.md",
    DOCS / "risk_analysis.md",
    DOCS / "test_plan_and_results.md",
    DOCS / "project_schedule_gantt.md",
    DOCS / "final_report.md",
    DOCS / "presentation_outline.md",
    DOCS / "README_RESEARCH.md",
    REAL / "phase36_multi_section_solve_report.json",
    REAL / "phase37_multi_section_validation.json",
    REAL / "phase38_global_calibration_report.json",
    REAL / "phase49_cross_section_consistency_report.json",
    REAL / "phase55_strict_correspondence_audit_report.json",
    REAL / "phase56_strict_global_calibration_report.json",
    REAL / "phase57_leave_one_section_out_report.json",
    REAL / "phase58_section_error_diagnostics_report.json",
    REAL / "phase59_final_real_camera_validation_summary.json",
    REAL / "phase60_real_star_association_audit_report.json",
    REAL / "phase61_final_association_visualisation_report.json",
    ASK / "phase62_integrated_demo/phase62_integrated_demo_report.json",
    ASK / "phase62_integrated_demo/phase62_integrated_demo.md",
    ASK / "phase62_integrated_demo/phase62_integrated_demo.html",
    ASK / "phase61_final_association_visualisation/phase61_real_star_association_overlay.jpg",
]

print("=" * 72)
print("STARLOC 2.0 — FINAL INTEGRITY CHECK")
print("=" * 72)

missing = [str(p.relative_to(ROOT)) for p in required if not p.is_file()]

if missing:
    print("\nMISSING REQUIRED FILES:")
    for item in missing:
        print("  -", item)
    raise SystemExit("Integrity check failed. Packaging stopped.")

print(f"\nRequired documents/reports: {len(required)}/{len(required)} present")

# Validate all Python scripts without executing them.
scripts = list(RESEARCH.rglob("*.py"))
syntax_errors = []

for script in scripts:
    try:
        ast.parse(script.read_text(encoding="utf-8"))
    except Exception as exc:
        syntax_errors.append((script, str(exc)))

print(f"Python scripts checked: {len(scripts)}")

if syntax_errors:
    print("\nPYTHON SYNTAX ERRORS:")
    for path, error in syntax_errors:
        print(path.relative_to(ROOT), error)
    raise SystemExit("Syntax check failed. Packaging stopped.")

print("Python syntax: PASS")

# Validate important JSON reports.
json_reports = [
    REAL / "phase36_multi_section_solve_report.json",
    REAL / "phase37_multi_section_validation.json",
    REAL / "phase38_global_calibration_report.json",
    REAL / "phase49_cross_section_consistency_report.json",
    REAL / "phase55_strict_correspondence_audit_report.json",
    REAL / "phase56_strict_global_calibration_report.json",
    REAL / "phase57_leave_one_section_out_report.json",
    REAL / "phase58_section_error_diagnostics_report.json",
    REAL / "phase59_final_real_camera_validation_summary.json",
    REAL / "phase60_real_star_association_audit_report.json",
    REAL / "phase61_final_association_visualisation_report.json",
    ASK / "phase62_integrated_demo/phase62_integrated_demo_report.json",
]

for path in json_reports:
    with path.open(encoding="utf-8") as f:
        json.load(f)

print(f"JSON report validation: PASS ({len(json_reports)} reports)")

# Verify important visual and tabular outputs.
visuals = [
    REAL / "results/ASK033/phase35_wcs_match_overlay.jpg",
    REAL / "results/ASK033/phase38_global_calibration/phase38_residual_map.png",
    REAL / "results/ASK033/phase52_global_prediction_test/phase52_four_point_montage.jpg",
    REAL / "results/ASK033/phase58_section_error_diagnostics/phase58_spatial_residual_vectors.png",
    REAL / "results/ASK033/phase58_section_error_diagnostics/phase58_section_error_distribution.png",
    ASK / "phase61_final_association_visualisation/phase61_real_star_association_overlay.jpg",
    ASK / "phase38_global_calibration/phase38_residual_map.png",
    ASK / "phase58_section_error_diagnostics/phase58_spatial_residual_vectors.png",
    ASK / "phase58_section_error_diagnostics/phase58_section_error_distribution.png",
    ASK / "phase52_global_prediction_test/phase52_four_point_montage.jpg",
]

for path in visuals:
    if not path.is_file():
        print("WARNING: visual output missing:", path.relative_to(ROOT))
    else:
        print("Visual verified:", path.relative_to(ROOT))


# Verify that all local image references in the Phase 62 HTML resolve.
from html.parser import HTMLParser
from urllib.parse import urlparse

class ImageReferenceParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.sources = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() == "img":
            src = dict(attrs).get("src")
            if src:
                self.sources.append(src)

demo_html = ASK / "phase62_integrated_demo/phase62_integrated_demo.html"
parser = ImageReferenceParser()
parser.feed(demo_html.read_text(encoding="utf-8"))

broken_images = []
for source in parser.sources:
    parsed = urlparse(source)
    if parsed.scheme or source.startswith("data:"):
        continue
    target = (demo_html.parent / parsed.path).resolve()
    if not target.is_file():
        broken_images.append(source)

if broken_images:
    for source in broken_images:
        print("BROKEN HTML IMAGE:", source)
    raise SystemExit("Phase 62 HTML image verification failed.")

print(f"Phase 62 HTML images: PASS ({len(parser.sources)} references)")

# Build a fresh manifest.
manifest = {
    "project": "StarLoc 2.0",
    "generated_utc": datetime.now(timezone.utc).isoformat(),
    "python_scripts_checked": len(scripts),
    "required_files_verified": len(required),
    "json_reports_verified": len(json_reports),
    "phases_integrated": [60, 61, 62],
    "real_camera_validation": {
        "camera": "ASK033",
        "sections_solved": 5,
        "phase37_correspondences": 233,
        "phase56_strict_correspondences": 74,
        "phase57_leave_one_section_out": {
            "median_px": 1.0468,
            "rmse_px": 2.3247,
            "max_px": 8.2780
        },
        "qualification": (
            "Exploratory single-image calibration. "
            "WCS-derived correspondences are not independent ground truth."
        )
    }
}

manifest_path = DOCS / "final_integrity_manifest.json"
manifest_path.write_text(json.dumps(manifest, indent=2))

# Archive exclusions.
excluded_dirs = {
    ".venv", ".git", "__pycache__", ".pytest_cache",
    ".mypy_cache", ".DS_Store"
}

def eligible(path):
    return not any(part in excluded_dirs for part in path.parts)

def make_zip(destination, files):
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        destination.unlink()

    count = 0
    with zipfile.ZipFile(
        destination, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6
    ) as archive:
        for path in files:
            if not path.is_file() or not eligible(path.relative_to(ROOT)):
                continue
            if path == destination:
                continue
            archive.write(path, path.relative_to(ROOT))
            count += 1

    with zipfile.ZipFile(destination, "r") as archive:
        bad = archive.testzip()
        if bad:
            raise RuntimeError(f"ZIP integrity failure: {bad}")

    return count, destination.stat().st_size

all_files = [
    p for p in ROOT.rglob("*")
    if p.is_file()
    and eligible(p.relative_to(ROOT))
    and p.suffix.lower() not in {".zip", ".pyc"}
    and not any(part.startswith(".") and part not in {".github"} 
                for part in p.relative_to(ROOT).parts)
]

submission_files = [
    p for p in all_files
    if p.is_relative_to(RESEARCH)
    or p.name in {
        "README.md", "requirements.txt", "pyproject.toml",
        "setup.py", "LICENSE"
    }
    or p.suffix.lower() == ".py"
]

research_files = [
    p for p in all_files if p.is_relative_to(RESEARCH)
]

submission_zip = ROOT / "StarLoc_2.0_Submission.zip"
results_zip = ROOT / "StarLoc_2.0_Research_Results.zip"

n1, s1 = make_zip(submission_zip, submission_files)
n2, s2 = make_zip(results_zip, research_files)

print("\n" + "=" * 72)
print("FINAL PACKAGING COMPLETED")
print("=" * 72)
print(f"Submission ZIP: {submission_zip.name}")
print(f"  Files: {n1} | Size: {s1 / 1024 / 1024:.2f} MB")
print(f"Research ZIP: {results_zip.name}")
print(f"  Files: {n2} | Size: {s2 / 1024 / 1024:.2f} MB")
print("Manifest:", manifest_path.relative_to(ROOT))
print("\nBoth ZIP archives passed integrity testing.")
print("No calibration or experimental results were rerun or modified.")
