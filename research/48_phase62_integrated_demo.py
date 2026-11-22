from pathlib import Path
import json
import html
import os
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
RESEARCH = ROOT / "research"
REAL = RESEARCH / "real_image"
ASK = REAL / "results" / "ASK033"
OUT = ASK / "phase62_integrated_demo"
OUT.mkdir(parents=True, exist_ok=True)

def load_json(path):
    try:
        return json.loads(path.read_text())
    except Exception as exc:
        return {"_read_error": str(exc)}

def find_report(name):
    matches = list(REAL.glob(name))
    if not matches:
        matches = list(RESEARCH.glob(name))
    return load_json(matches[0]) if matches else {}

def rel(path):
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)

def first_existing(paths):
    for p in paths:
        if p.exists():
            return p
    return None

# Core real-camera reports
report_names = [
    "phase38_global_calibration_report.json",
    "phase56_strict_global_calibration_report.json",
    "phase57_leave_one_section_out_report.json",
    "phase59_final_real_camera_validation_summary.json",
    "phase60_real_star_association_audit_report.json",
    "phase61_final_association_visualisation_report.json",
]
reports = {name: find_report(name) for name in report_names}

# Required Phase 61 outputs
overlay = ASK / "phase61_final_association_visualisation/phase61_real_star_association_overlay.jpg"
classified_csv = ASK / "phase61_final_association_visualisation/phase61_all_classified_correspondences.csv"
strict_csv = ASK / "phase60_association_audit/phase60_strict_internal_consistency.csv"
uncertain_csv = ASK / "phase60_association_audit/phase60_uncertain_correspondences.csv"

# Additional visual evidence
visuals = [
    ("Real-camera association overlay — Phase 61", overlay),
    ("Global calibration residual map — Phase 38",
     ASK / "phase38_global_calibration/phase38_residual_map.png"),
    ("Section residual vectors — Phase 58",
     ASK / "phase58_section_error_diagnostics/phase58_spatial_residual_vectors.png"),
    ("Section error distribution — Phase 58",
     ASK / "phase58_section_error_diagnostics/phase58_section_error_distribution.png"),
    ("Four-point investigation — Phase 52",
     ASK / "phase52_global_prediction_test/phase52_four_point_montage.jpg"),
    ("WCS validation overlay — Phase 35",
     ASK / "phase35_wcs_match_overlay.jpg"),
]

# Phase 61 classification, taken from the verified phase output.
classification = {
    "total_correspondences": 233,
    "strict_internal_consistency": 74,
    "uncertain": 155,
    "suspect_associations": 4,
    "interpretation": (
        "Strict internal consistency is a quality-control category, not "
        "independent confirmation of Hipparcos identities."
    ),
}

# Calibration parameter values from the recorded Phase 38 and Phase 56 runs.
calibration = {
    "phase38_exploratory": {
        "optical_centre_x_px": 940.879296,
        "optical_centre_y_px": 755.538812,
        "focal_scale_px_per_rad": 822.970865,
        "radial_k1": -0.03333727,
        "radial_k2": 0.00089815,
        "optical_axis_ra_deg": 2.12754,
        "optical_axis_dec_deg": 50.34241,
        "held_out_rmse_px": 0.986347,
    },
    "phase56_strict_subset": {
        "optical_centre_x_px": 941.08836649,
        "optical_centre_y_px": 755.98713900,
        "focal_scale_px_per_rad": 823.00717669,
        "radial_k1": -0.03258449,
        "radial_k2": -0.00120724,
        "optical_axis_ra_deg": 2.18183666,
        "optical_axis_dec_deg": 50.30771236,
        "held_out_rmse_px": 0.938114,
        "training_points": 59,
        "held_out_points": 15,
    },
}

# Leave-one-section-out values are explicitly recorded from Phase 57.
leave_one_out = {
    "aggregate": {
        "count": 74, "median_px": 1.0468, "mean_px": 1.5935,
        "rmse_px": 2.3247, "p90_px": 3.2666, "max_px": 8.2780,
    },
    "sections": {
        "R1C2": {"count": 11, "median_px": 1.437, "rmse_px": 1.741},
        "R2C1": {"count": 4, "median_px": 0.506, "rmse_px": 0.718},
        "R2C2": {"count": 14, "median_px": 0.827, "rmse_px": 1.876},
        "R3C1": {"count": 24, "median_px": 1.342, "rmse_px": 3.460},
        "R3C2": {"count": 21, "median_px": 0.934, "rmse_px": 1.152},
    },
}

# Collect source artifacts and flag missing inputs rather than fabricating them.
artifacts = {
    "phase61_overlay": overlay,
    "phase61_classified_correspondences": classified_csv,
    "phase60_strict_correspondences": strict_csv,
    "phase60_uncertain_correspondences": uncertain_csv,
    "hipparcos_visible_catalogue": ASK / "ASK033_visible_hipparcos_catalogue.csv",
    "phase49_cross_section_correspondences":
        ASK / "phase49_cross_section_consistency/phase49_cross_section_point_comparison.csv",
    "phase56_point_residuals":
        ASK / "phase56_strict_global_calibration/phase56_strict_point_residuals.csv",
    "phase57_held_out_predictions":
        ASK / "phase57_leave_one_section_out/phase57_held_out_predictions.csv",
    "phase58_residual_vectors":
        ASK / "phase58_section_error_diagnostics/phase58_residual_vectors.csv",
}

artifact_status = {
    key: {"path": rel(path), "exists": path.exists()}
    for key, path in artifacts.items()
}

visual_status = [
    {"title": title, "path": rel(path), "exists": path.exists()}
    for title, path in visuals
]

# Search for synthetic pipeline reports and documentation without assuming
# a particular internal results-folder layout.
synthetic_candidates = []
for p in RESEARCH.rglob("*.json"):
    name = p.name.lower()
    if any(token in name for token in (
        "calibration_report", "robustness_report", "detection_report",
        "demo_report", "integrity_report"
    )):
        if "phase" not in name and "ask033" not in str(p).lower():
            synthetic_candidates.append(rel(p))

synthetic_docs = [
    rel(p) for p in [
        RESEARCH / "README_RESEARCH.md",
        RESEARCH / "docs" / "README_STARLOC_FINAL.md",
        RESEARCH / "docs" / "final_report.md",
        RESEARCH / "docs" / "test_plan_and_results.md",
    ] if p.exists()
]

summary = {
    "project": "StarLoc 2.0",
    "phase": 62,
    "title": "Integrated Star Tracker Demonstration",
    "generated_utc": datetime.utcnow().isoformat(timespec="seconds") + "Z",
    "mode": "integration_only_no_previous_experiments_rerun",
    "synthetic_pipeline": {
        "status": "previously completed; source reports and documentation indexed",
        "known_results": {
            "synthetic_detected_stars": 99,
            "synthetic_input_stars": 100,
            "mean_centroid_error_px": 0.1745,
            "synthetic_catalogue_matches": 1136,
            "synthetic_catalogue_stars": 1284,
            "recovered_fov_deg": 179.9982,
            "recovered_roll_deg": 36.99925,
            "blind_calibration_rmse_px": 0.285,
        },
        "candidate_reports_found": sorted(synthetic_candidates),
        "documentation_found": synthetic_docs,
    },
    "real_camera": {
        "camera": "AllSkyKamera Network ASK033 — Miesenbach, Austria",
        "image_dimensions_px": [1920, 1440],
        "section_grid": "3 x 3",
        "solved_sections": ["R1C2", "R2C1", "R2C2", "R3C1", "R3C2"],
        "global_model_status": "exploratory; not independently validated",
        "calibration_models": calibration,
        "association_classification": classification,
        "leave_one_section_out": leave_one_out,
        "source_reports": reports,
    },
    "artifacts": artifact_status,
    "visuals": visual_status,
    "limitations": [
        "The real-camera section WCS solutions are not independent ground truth.",
        "The 74 strict points indicate internal consistency with local WCS solutions, not confirmed catalogue identities.",
        "The 155 uncertain correspondences remain unresolved.",
        "Four catalogue associations remain separately flagged as suspect.",
        "Leave-one-section-out performance varies by section; R3C1 is notably weaker.",
        "The global fisheye estimates are exploratory and require independent astrometric validation.",
        "Image timestamp and camera pointing metadata require confirmation.",
        "The synthetic demonstration assumes a controlled zenith-pointed fisheye geometry and does not prove general real-camera performance.",
    ],
    "integrity": {
        "missing_required_artifacts": [
            key for key, value in artifact_status.items() if not value["exists"]
        ],
        "missing_visuals": [
            item["path"] for item in visual_status if not item["exists"]
        ],
        "phase61_classification_total": sum([
            classification["strict_internal_consistency"],
            classification["uncertain"],
            classification["suspect_associations"],
        ]),
    },
}

json_path = OUT / "phase62_integrated_demo_report.json"
json_path.write_text(json.dumps(summary, indent=2))

# Presentation-friendly Markdown report.
md = f"""# StarLoc 2.0 — Phase 62
## Integrated Star Tracker Demonstration

Generated: {summary['generated_utc']}

### 1. Project objective
Demonstrate a software-defined workflow for detecting stars, associating detections
with a stellar catalogue, estimating image-to-sky geometry and evaluating calibration.

### 2. Synthetic pipeline
- Star detection: 99 / 100 simulated stars.
- Mean centroid error: 0.1745 px.
- Blind catalogue matching: 1,136 / 1,284 catalogue-rendered stars.
- Recovered FOV: 179.9982°.
- Recovered roll: 36.99925°.
- Blind calibration RMSE: 0.285 px.

These are controlled synthetic results, not real-camera accuracy claims.

### 3. Real-camera experiment — ASK033
- Input image: 1920 × 1440 px.
- Image subdivision: 3 × 3 sections.
- Sections with plate solutions: R1C2, R2C1, R2C2, R3C1 and R3C2.
- Cross-section correspondences: 233.

### 4. Association audit
| Classification | Count |
|---|---:|
| Strict internal consistency | 74 |
| Uncertain | 155 |
| Suspect associations | 4 |
| **Total** | **233** |

The strict category indicates agreement with the corresponding local WCS solution.
It does not independently prove the Hipparcos identity of a detected source.

### 5. Global fisheye calibration experiments
**Phase 38 exploratory model**
- Optical centre: (940.8793, 755.5388) px
- Focal scale: 822.9709 px/rad
- Radial coefficients: k1 = -0.03333727, k2 = 0.00089815
- Held-out RMSE: 0.9863 px

**Phase 56 strict-subset model**
- Optical centre: (941.0884, 755.9871) px
- Focal scale: 823.0072 px/rad
- Radial coefficients: k1 = -0.03258449, k2 = -0.00120724
- Training / held-out points: 59 / 15
- Held-out RMSE: 0.9381 px

These models are exploratory because the correspondences originate from section WCS
solutions and are not independently certified astrometric ground truth.

### 6. Cross-section generalisation
Leave-one-section-out validation on 74 strict-subset correspondences:
- Median error: 1.0468 px
- Mean error: 1.5935 px
- RMSE: 2.3247 px
- 90th percentile: 3.2666 px
- Maximum: 8.2780 px

R3C1 was the weakest held-out section (RMSE 3.460 px), indicating section-dependent
systematic errors or association problems that need further investigation.

### 7. Scientific limitations
{chr(10).join('- ' + x for x in summary['limitations'])}

### 8. Demonstration assets
{chr(10).join('- ' + item['title'] + ': `' + item['path'] + '`' + ('' if item['exists'] else ' (missing)') for item in visual_status)}

### 9. Reproducibility and integrity
This phase indexes existing reports and evidence. It does not rerun earlier phases,
refit calibration parameters, or alter prior experimental outputs.

Machine-readable report: `{rel(json_path)}`
"""
md_path = OUT / "phase62_integrated_demo.md"
md_path.write_text(md)

# Standalone HTML presentation page, using relative image paths.
cards = []
for title, path in visuals:
    if path.exists():
        cards.append(
            f'<section class="visual"><h3>{html.escape(title)}</h3>'
            f'<img src="{html.escape(os.path.relpath(path, OUT))}" alt="{html.escape(title)}">'
            f'<p>{html.escape(rel(path))}</p></section>'
        )
    else:
        cards.append(
            f'<section class="visual"><h3>{html.escape(title)}</h3>'
            f'<p>Asset not found: {html.escape(rel(path))}</p></section>'
        )

html_doc = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>StarLoc 2.0 — Phase 62 Demo</title>
<style>
body{{font-family:Arial,sans-serif;max-width:1100px;margin:36px auto;padding:0 20px;
line-height:1.55;color:#20242a;background:#f7f8fa}}
h1,h2{{line-height:1.2}} .sub{{color:#586273}}
.metrics{{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:12px}}
.metric,.visual{{background:white;border:1px solid #dfe3e8;border-radius:12px;padding:16px}}
.metric strong{{font-size:28px;display:block}} .gallery{{display:grid;
grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:16px}}
img{{width:100%;height:auto;border-radius:8px}} .warning{{border-left:4px solid #d69a20;
padding:12px;background:#fff8e8}} code{{overflow-wrap:anywhere}}
</style></head><body>
<h1>StarLoc 2.0</h1><p class="sub">Phase 62 — Integrated Star Tracker Demonstration</p>
<p>A combined view of the controlled synthetic pipeline and the ASK033 real-camera
research experiment.</p>
<div class="metrics">
<div class="metric"><strong>99/100</strong>Synthetic star detections</div>
<div class="metric"><strong>0.285 px</strong>Synthetic blind-calibration RMSE</div>
<div class="metric"><strong>5</strong>Real-camera sections solved</div>
<div class="metric"><strong>233</strong>WCS-derived correspondences</div>
<div class="metric"><strong>74</strong>Strict internal consistency</div>
<div class="metric"><strong>155</strong>Uncertain</div>
<div class="metric"><strong>4</strong>Suspect associations</div>
</div>
<h2>Real-camera evidence</h2><div class="gallery">{''.join(cards)}</div>
<h2>Calibration and validation</h2>
<p>Phase 38 and Phase 56 produced exploratory global fisheye estimates.
The Phase 56 held-out RMSE was 0.9381 px on 15 points. Leave-one-section-out
validation across 74 points produced a 2.3247 px RMSE, with R3C1 the weakest
section at 3.460 px.</p>
<div class="warning"><strong>Interpretation:</strong> Low local-WCS residuals indicate
internal consistency, not independent confirmation of stellar identities.
The real-camera global calibration remains exploratory and requires independent
astrometric validation.</div>
<h2>Reproducibility</h2>
<p>This demonstration reads existing reports and assets only. No earlier phase
was rerun and no calibration parameters were modified.</p>
<p>See <code>phase62_integrated_demo.md</code> and
<code>phase62_integrated_demo_report.json</code> in this folder.</p>
</body></html>"""
html_path = OUT / "phase62_integrated_demo.html"
html_path.write_text(html_doc)

print("=" * 72)
print("STARLOC 2.0 — PHASE 62 INTEGRATION COMPLETED")
print("=" * 72)
print("Synthetic results indexed.")
print("Real-camera sections:", 5)
print("Correspondences:", classification["total_correspondences"])
print("Classification:", classification)
print("\nOutputs:")
print(rel(json_path))
print(rel(md_path))
print(rel(html_path))
print("\nMissing required artifacts:", summary["integrity"]["missing_required_artifacts"])
print("Missing visuals:", summary["integrity"]["missing_visuals"])
print("\nNo previous phases rerun. No calibration parameters modified.")
