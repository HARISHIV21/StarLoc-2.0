# StarLoc 2.0 — Research Workspace Guide

## Purpose

This directory contains the experiment scripts, input data, generated results and technical evidence for StarLoc 2.0. The research target is stellar identification and multi-section astrometric calibration for the AllSkyKamera Network.

## Repository areas

- `research/`: numbered research and integration scripts.
- `research/real_image/`: ASK033 real-image acquisition, detection, matching and calibration investigations.
- `research/data/catalogue/`: Hipparcos-derived catalogue files and metadata.
- `research/data/synthetic/`: generated fisheye observations and synthetic ground truth.
- `research/final_professor_evidence/`: classified real-image correspondence evidence.
- `research/docs/`: specifications, reports, validation matrix and roadmap.
- `research/results/`: generated calibration and robustness outputs.
- `simulation/`: staged algorithm-development exercises.
- `results/`: selected simulation plots and numeric outputs.

## Main experimental stages

1. Generate a controlled fisheye observation with known parameters.
2. Detect stellar candidates and estimate centroids.
3. Prepare the catalogue and propagate positions to the observation epoch.
4. Generate visible-sky candidates.
5. Associate image observations with catalogue stars.
6. Estimate the constrained camera model.
7. Test robustness and local-section behaviour.
8. Investigate real ASK033 image sections and local astrometric solutions.
9. Audit correspondences and section-dependent residuals.
10. Integrate the available evidence for review.

The numbered scripts preserve the development history. They are not all a single linear production pipeline; inspect each script's inputs and outputs before execution.

## Documented entry points

From the repository root:

```bash
python research/16_run_final_demo.py
python research/48_phase62_integrated_demo.py
```

The Phase 62 script integrates existing evidence; it does not rerun every historical experiment or independently refit the camera model.

## Environment

The research environment uses Python and scientific/image-processing libraries including NumPy, SciPy, OpenCV, Astropy and Matplotlib. A pinned, complete dependency lock and one-command environment setup remain reproducibility improvements to implement. Historical experiments may have different prerequisites.

## Evidence and validation

Use these documents before interpreting outputs:
- `docs/final_report.md`
- `docs/test_plan_and_results.md`
- `docs/real_camera_validation_matrix.md`
- `docs/system_architecture.md`

Synthetic fit metrics, random point holdout metrics, leave-one-section-out metrics and independent external validation are different evidence classes. Do not combine them into a single accuracy claim.

## Real-image status

The ASK033 investigation used one public 1920 × 1440 image and local astrometric solutions over five sections. The association audit recorded 233 candidate correspondences: 74 strict internal-consistency, 155 uncertain and four suspect. Strict local-WCS consistency is not independent proof of catalogue identity.

The global calibration remains exploratory. Independent reference verification, additional images, multi-section global estimation and temporal repeatability are required before claiming a validated operational calibration.

## Engineering direction

The next stages are global real-camera validation, temporal orientation analysis, modular interfaces, C++ numerical equivalence, target-hardware benchmarking and a separately validated optical/IMU estimator interface. See `docs/embedded_aerospace_roadmap.md`.


## Latest real-observation status — through Phase 147

The real-image work did not stop at the earlier Phase 60–62 evidence integration. Additional ASK033 archive-sequence experiments are recorded through Phase 147, including candidate reconstruction, tracking, catalogue consistency, frame registration, spatial holdouts and coordinate-integrity audits. The original source video is referenced by the reports but is not present in the Git tree; extracted frames and derived reports are present.

Use the [authoritative real-observation index](../../REAL_OBSERVATIONS.md) and [real-image workspace entry point](../real_image/README.md). The earlier real-image status paragraph in this guide is historical; the qualification remains that independent star identity and globally validated real-camera calibration are open.
