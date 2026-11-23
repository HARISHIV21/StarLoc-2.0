# StarLoc 2.0 — Research Workspace Guide

## Start here

- [Main project README](../../README.md)
- [Professor objectives and traceability](../../PROFESSOR_OBJECTIVES.md)
- [Real observation evidence index](../../REAL_OBSERVATIONS.md)
- [Synthetic observation validation](synthetic_observation_validation.md)
- [Final R&D report](final_report.md)
- [Real-camera validation matrix](real_camera_validation_matrix.md)

## Repository areas

- research/: core synthetic and real-image source scripts.
- research/data/catalogue/: Hipparcos-derived catalogue and epoch data.
- research/data/synthetic/: synthetic observations, metadata and ground truth.
- research/real_image/: ASK033 acquisition, detection, catalogue association, WCS and calibration experiments.
- research/final_professor_evidence/: curated ASK033 correspondence evidence.
- research/results/: synthetic detection, calibration and robustness outputs.
- research/docs/: project tracking, specifications, validation and reporting.

## Core workflow

1. Detect stars and estimate image centroids.
2. Identify detected stars in a catalogue using observation time and approximate site.
3. Convert catalogue RA/Dec to image pixel coordinates.
4. Estimate and validate the optical camera model.

The numbered scripts are staged research experiments with historical input/output dependencies. They are not all a single automatic production pipeline.

## Synthetic demonstration

From repository root:

    python research/16_run_final_demo.py

This runs the catalogue-based synthetic calibration and robustness workflow. It does not rerun ASK033 local astrometric solving.

## Real-image evidence

The active real observation is ASK033. See REAL_OBSERVATIONS.md for the original image, metadata, detection overlays, catalogue tables, local WCS solutions and calibration reports. The real-camera model remains exploratory; independent star identity and metadata verification are open.

## Reproducibility

The documented Python stack includes NumPy, SciPy, OpenCV, Astropy and Matplotlib. A pinned dependency lock and one-command setup remain improvements. Each experiment's input and output paths should be checked before running it.
