# StarLoc 2.0 — Research Workspace

## Overview

This workspace contains the research implementation for catalogue-based all-sky camera calibration.

## Environment

Activate the existing virtual environment:

    source .venv/bin/activate

The current implementation uses Python with NumPy, SciPy, OpenCV, Astropy and Matplotlib.

## Research scripts

The principal research scripts are:

- `research/01_generate_fisheye_dataset.py`
- `research/02_detect_fisheye_stars.py`
- `research/03_optimize_star_detection.py`
- `research/04_fisheye_optical_calibration.py`
- `research/07_download_hipparcos_catalogue.py`
- `research/08_clean_hipparcos_catalogue.py`
- `research/09_propagate_hipparcos_positions.py`
- `research/10_generate_visible_sky_catalogue.py`
- `research/11_render_catalogue_fisheye.py`
- `research/12_blind_catalogue_calibration.py`
- `research/13_robustness_validation.py`

Some intermediate scripts and data files are also retained in the workspace.

## Reproduce the latest synthetic experiment

From the project root:

    python research/12_blind_catalogue_calibration.py
    python research/13_robustness_validation.py

The catalogue and generated synthetic observation files must already exist under `research/data`.

## Results

Important result files are stored in `research/results`:

- `blind_fisheye_calibration.json`
- `blind_catalogue_matches.csv`
- `blind_calibration_residuals.csv`
- `phase13_robustness_report.json`
- `phase13_summary.csv`
- `phase13_robustness_example.png`

## Documentation

The `research/docs` folder contains the state of the art, feasibility study, functional and technical specifications, risk analysis, test plan, project schedule, final report and presentation outline.

## Important validation note

The current results are based on synthetic images generated from real catalogue data. They do not constitute real AllSkyKamera validation.

Real-image validation requires a representative camera image, its observation timestamp, approximate geographic location and camera pointing information.


<!-- STARLOC_PHASE59_FINAL_VALIDATION -->
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

<!-- STARLOC_PHASE60_62_FINAL_UPDATE -->

## Latest research status — Phases 60–62

The latest real-camera association audit covers 233 correspondences:
74 strict internal-consistency cases, 155 uncertain cases and four suspect
associations. The strict category is based on local-WCS agreement and does
not independently confirm catalogue identities.

Phase 56 reports a 0.9381 px held-out RMSE on 15 points. Phase 57 reports
2.3247 px aggregate leave-one-section-out RMSE, with R3C1 at 3.460 px.
These real-camera calibration experiments remain exploratory.

Phase 61 provides the final association overlay and classified CSV.
Phase 62 provides an integrated JSON, Markdown and HTML demonstration.
Run `python research/48_phase62_integrated_demo.py` from the project root
to regenerate the Phase 62 integration outputs. This does not rerun the
earlier experiments or refit calibration parameters.
