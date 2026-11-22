import json
from pathlib import Path
from datetime import date

BASE = Path("research/real_image")
DOCS = Path("research/docs")

def load(name):
    path = BASE / name
    if not path.exists():
        raise FileNotFoundError(f"Required report missing: {path}")
    return json.loads(path.read_text())

phase38 = load("phase38_global_calibration_report.json")
phase56 = load("phase56_strict_global_calibration_report.json")
phase57 = load("phase57_leave_one_section_out_report.json")
phase58 = load("phase58_section_error_diagnostics_report.json")

p38 = phase38["held_out_test_metrics"]
p56 = phase56["held_out_test_metrics"]

def find_metrics(obj, required=("count", "median_px", "rmse_px")):
    """Find the aggregate metric dictionary without assuming its key name."""
    if isinstance(obj, dict):
        if all(k in obj for k in required):
            return obj
        for value in obj.values():
            found = find_metrics(value, required)
            if found is not None:
                return found
    elif isinstance(obj, list):
        for value in obj:
            found = find_metrics(value, required)
            if found is not None:
                return found
    return None

p57 = find_metrics(phase57)

if p57 is None:
    print("Phase 57 report structure:")
    print(json.dumps(phase57, indent=2)[:10000])
    raise KeyError(
        "Could not locate Phase 57 aggregate metrics "
        "(count, median_px, rmse_px)."
    )


summary = {
    "phase": 59,
    "title": "StarLoc 2.0 — Final Real-Camera Validation Summary",
    "generated": str(date.today()),
    "camera": "ASK033 public AllSkyKamera image",
    "image_dimensions": [1920, 1440],
    "real_image_validation": {
        "solved_sections": 5,
        "sections": ["R1C2", "R2C1", "R2C2", "R3C1", "R3C2"],
        "phase37_provisional_correspondences": 233,
        "phase56_strict_correspondences": 74,
        "strict_filter": "Local WCS-to-candidate residual <= 1.0 pixel"
    },
    "phase38_global_model": {
        "model": phase38["model"],
        "test_count": p38["count"],
        "test_median_error_px": p38["median_error_px"],
        "test_rmse_px": p38["rmse_px"],
        "parameters": phase38["parameters"]
    },
    "phase56_strict_model": {
        "test_count": p56["count"],
        "test_median_error_px": p56["median_px"],
        "test_rmse_px": p56["rmse_px"],
        "parameters": phase56["parameters"]
    },
    "phase57_leave_one_section_out": {
        "count": p57["count"],
        "median_error_px": p57["median_px"],
        "mean_error_px": p57["mean_px"],
        "rmse_px": p57["rmse_px"],
        "p90_error_px": p57["p90_px"],
        "maximum_error_px": p57["max_px"],
        "within_1px": p57["within_1px"],
        "within_2px": p57["within_2px"],
        "within_3px": p57["within_3px"],
        "within_5px": p57["within_5px"]
    },
    "phase58_section_diagnostics": phase58["per_section"],
    "scientific_conclusion": [
        "The synthetic fisheye pipeline demonstrated controlled calibration performance.",
        "Five real-image sections produced local astrometric solutions.",
        "The real-image global fisheye model is exploratory.",
        "Random held-out validation and leave-one-section-out validation give different results.",
        "Cross-section generalisation is not uniform.",
        "R3C1 has the largest section-level prediction error.",
        "R2C2 contains outliers that materially affect RMSE.",
        "The strict subset improves correspondence quality but does not establish independent accuracy.",
        "The local WCS-derived catalogue correspondences are not independent ground truth.",
        "A separate camera image or independently verified astrometric reference is required for stronger validation."
    ],
    "limitations": [
        "Only one public camera image was used for this real-image investigation.",
        "Camera site and timestamp assumptions require independent verification.",
        "The five local WCS solutions are not independent camera calibration ground truth.",
        "The four excluded R2C2 associations remain unresolved.",
        "The small R2C1 leave-one-section-out test set contains only four points.",
        "No production-grade global calibration claim is made."
    ]
}

report_path = BASE / "phase59_final_real_camera_validation_summary.json"
report_path.write_text(json.dumps(summary, indent=2))

addendum = """
## Final real-camera validation update — Phases 38–59

### Real-image experiment

The project was extended to a public ASK033 AllSkyKamera image with dimensions
1920 × 1440 pixels. Five image sections obtained local astrometric solutions:
R1C2, R2C1, R2C2, R3C1 and R3C2.

The Phase 37 validation produced 233 provisional catalogue-to-image
correspondences. A stricter local-WCS residual filter selected 74 points
for the Phase 56 calibration experiment.

### Global fisheye calibration

The Phase 38 exploratory equidistant fisheye model used radial coefficients
k1 and k2. Its random held-out subset contained 47 points, with median
residual 0.608 px and RMSE 0.986 px.

Phase 56 fitted the same model using 74 strict correspondences. Its
15-point random held-out subset had median residual 0.797 px and RMSE
0.938 px. The optical centre and focal scale remained close to the
Phase 38 estimates. This does not establish a clear accuracy improvement.

### Cross-section validation

Phase 57 withheld each complete image section in turn. Across 74
predictions, the aggregate median error was 1.047 px and RMSE was
2.325 px. Section-level RMSE ranged from 0.718 px to 3.460 px.
R3C1 was the weakest section, with RMSE 3.460 px and maximum error
8.278 px. R2C1 had only four held-out points.

Phase 58 examined residual vectors and distributions. It identified
section-dependent directional biases and outlier sensitivity, especially
in R2C2. No further correction was accepted without independent evidence.

### Final interpretation and limitations

The synthetic calibration experiments demonstrate the feasibility of
the image-processing and geometric-calibration pipeline under controlled
conditions. The public real-camera experiment demonstrates that local
astrometric plate solving and an exploratory global fisheye fit can be
performed across multiple image sections.

However, the real-camera result is not a fully validated production
calibration. The correspondences inherit uncertainty from local WCS
solutions, only one public image was investigated, and the four suspect
R2C2 associations remain unresolved. Independent multi-frame or
independently verified astrometric validation is required.

The Phase 38 and Phase 56 models are retained as separate experimental
results. Neither is silently substituted for the other.
"""

marker = "<!-- STARLOC_PHASE59_FINAL_VALIDATION -->"

targets = [
    DOCS / "final_report.md",
    DOCS / "test_plan_and_results.md",
    DOCS / "README_RESEARCH.md",
]

for path in targets:
    if not path.exists():
        print("WARNING: documentation file not found:", path)
        continue

    content = path.read_text()
    if marker in content:
        content = content.split(marker)[0].rstrip()

    path.write_text(content + "\n\n" + marker + "\n" + addendum.strip() + "\n")
    print("Updated:", path)

print("\nPHASE 59 COMPLETED")
print("Summary:", report_path)
print("Real-camera validation documentation consolidated.")
