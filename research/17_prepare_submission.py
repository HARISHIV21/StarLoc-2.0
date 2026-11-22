from pathlib import Path
import zipfile
import hashlib
import json
from datetime import datetime, timezone

ROOT = Path.cwd()
DOCS = ROOT / "research" / "docs"
DOCS.mkdir(parents=True, exist_ok=True)

README_LINES = [
    "# StarLoc 2.0",
    "## Software-Defined All-Sky Camera Calibration Using Stellar Identification",
    "",
    "### Objective",
    "Detect stars in all-sky fisheye images, identify them using an astronomical catalogue, associate celestial coordinates with image pixels, and estimate optical calibration parameters.",
    "",
    "### Implemented workflow",
    "- Synthetic 180-degree equidistant fisheye image generation.",
    "- Star detection and centroid extraction.",
    "- Hipparcos catalogue processing.",
    "- Proper-motion propagation to the observation epoch.",
    "- Visible-sky catalogue generation.",
    "- Blind catalogue matching and optical calibration.",
    "- Robustness testing under simulated image degradation.",
    "- Four-section synthetic image analysis.",
    "",
    "### Main demonstration",
    "Run: python research/16_run_final_demo.py",
    "",
    "### Main synthetic results",
    "- Detected regions: 1,136",
    "- Identified stars: 1,136",
    "- Estimated FOV: 179.998 degrees",
    "- Estimated roll: 36.999 degrees",
    "- Reprojection RMSE: 0.285 pixels",
    "",
    "### Validation limitation",
    "These results are from synthetic observations generated using real astronomical catalogue data. They are not real AllSkyKamera measurements. The current model assumes a zenith-pointed equidistant fisheye camera with unknown roll. Validation using a real camera exposure remains pending."
]
README = "\n".join(README_LINES) + "\n"

(ROOT / "README_STARLOC_FINAL.md").write_text(README, encoding="utf-8")
(DOCS / "README_STARLOC_FINAL.md").write_text(README, encoding="utf-8")

CHECKLIST = "\n".join([
    "# StarLoc 2.0 Submission Checklist",
    "",
    "## Documentation",
    "- [x] State-of-the-art study",
    "- [x] Feasibility study",
    "- [x] Functional and technical specifications",
    "- [x] Risk analysis",
    "- [x] Test plan and results",
    "- [x] Project schedule",
    "- [x] Final report",
    "- [x] Presentation outline",
    "",
    "## Software",
    "- [x] Star detection pipeline",
    "- [x] Hipparcos catalogue processing",
    "- [x] Epoch propagation",
    "- [x] Visible-sky catalogue generation",
    "- [x] Blind catalogue matching",
    "- [x] Optical calibration",
    "- [x] Robustness validation",
    "- [x] Consolidated demonstration",
    "- [x] Project integrity check",
    "",
    "## Remaining",
    "- [ ] Real AllSkyKamera image validation",
    "- [ ] Final oral presentation",
    "",
    "Important: numerical results currently represent synthetic validation, not real-camera calibration."
]) + "\n"

(DOCS / "submission_checklist.md").write_text(CHECKLIST, encoding="utf-8")

EXCLUDED = {
    ".git", ".venv", ".venv-1", "venv", "env",
    "__pycache__", ".pytest_cache", ".mypy_cache",
    "node_modules", "build", "dist"
}
ARCHIVES = {"StarLoc_2.0_Submission.zip", "StarLoc_2.0_Research_Results.zip"}

def include(path):
    rel = path.relative_to(ROOT)
    return (
        path.is_file()
        and not any(part in EXCLUDED for part in rel.parts)
        and path.name not in ARCHIVES
        and path.name != ".DS_Store"
        and path.suffix != ".pyc"
    )

def add_files(zf, paths):
    count = 0
    for path in sorted(paths):
        if include(path):
            zf.write(path, path.relative_to(ROOT))
            count += 1
    return count

def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

main_zip = ROOT / "StarLoc_2.0_Submission.zip"
research_zip = ROOT / "StarLoc_2.0_Research_Results.zip"

all_files = [p for p in ROOT.rglob("*") if include(p)]

with zipfile.ZipFile(main_zip, "w", zipfile.ZIP_DEFLATED) as zf:
    main_count = add_files(zf, all_files)

research_files = [p for p in (ROOT / "research").rglob("*") if include(p)]
with zipfile.ZipFile(research_zip, "w", zipfile.ZIP_DEFLATED) as zf:
    research_count = add_files(zf, research_files)

manifest = {
    "project": "StarLoc 2.0",
    "created_utc": datetime.now(timezone.utc).isoformat(),
    "main_archive": {
        "filename": main_zip.name,
        "size_bytes": main_zip.stat().st_size,
        "sha256": digest(main_zip)
    },
    "research_archive": {
        "filename": research_zip.name,
        "size_bytes": research_zip.stat().st_size,
        "sha256": digest(research_zip)
    },
    "real_camera_validation": "pending"
}
(DOCS / "submission_manifest.json").write_text(
    json.dumps(manifest, indent=2), encoding="utf-8"
)

with zipfile.ZipFile(main_zip) as zf:
    main_test = zf.testzip()
    names = set(zf.namelist())

with zipfile.ZipFile(research_zip) as zf:
    research_test = zf.testzip()

required = [
    "README_STARLOC_FINAL.md",
    "research/16_run_final_demo.py",
    "research/15_project_integrity_check.py",
    "research/docs/final_report.md",
    "research/results/blind_fisheye_calibration.json"
]
missing = [name for name in required if name not in names]

print("\nSTARLOC 2.0 — PHASE 17")
print("=" * 55)
print("Main archive files:", main_count)
print("Research archive files:", research_count)
print("Main archive integrity:", "PASS" if main_test is None else "FAIL")
print("Research archive integrity:", "PASS" if research_test is None else "FAIL")
print("Missing required files:", missing if missing else "None")
print("\nCreated files:")
print(main_zip.name, f"({main_zip.stat().st_size / 1024 / 1024:.2f} MB)")
print(research_zip.name, f"({research_zip.stat().st_size / 1024 / 1024:.2f} MB)")
print("Manifest:", DOCS / "submission_manifest.json")

if main_test or research_test or missing:
    raise SystemExit("PACKAGING FAILED")

print("\nPHASE 17 COMPLETE — SUBMISSION PACKAGING PASSED")
