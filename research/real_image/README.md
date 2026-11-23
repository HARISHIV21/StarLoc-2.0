# ASK033 Real-Image Research — Core Objectives

This directory contains source scripts and evidence for applying the professor's four core StarLoc objectives to the real ASK033 AllSkyKamera still image.

Start with:
- [Real observation evidence index](../../REAL_OBSERVATIONS.md)
- [Professor objectives and traceability](../../PROFESSOR_OBJECTIVES.md)
- [Final R&D report](../docs/final_report.md)
- [Real-camera validation matrix](../docs/real_camera_validation_matrix.md)

## Active real-image workflow

1. Acquire and inspect the original ASK033 image and camera metadata.
2. Detect point-source candidates and refine sub-pixel centroids.
3. Build a visible Hipparcos catalogue using the recorded observation epoch and approximate site.
4. Match image candidates with catalogue stars and assess identity quality.
5. Obtain local WCS solutions for selected image sections.
6. Convert catalogue RA/Dec to image pixels with explicit FITS/pixel-origin and section-offset handling.
7. Fit and audit the optical camera model, including distortion and spatial validation.

## Main source scripts

- 01_inspect_ask033.py–03_download_ask033.py: image acquisition and provenance inspection.
- 04_detect_real_stars.py–06_refine_real_candidates.py: detection and centroid refinement.
- 07_build_ask033_catalogue.py–08_fix_ask033_catalogue_ids.py: catalogue preparation and ID handling.
- 09_phase21_initial_real_matching.py onward: matching, local astrometry and correspondence validation.
- 25_objective3_radec_to_pixel.py: RA/Dec to pixel-coordinate conversion.
- 26_objective4_*.py onward: optical calibration, distortion and validation.
- 46_phase60_real_star_association_audit.py–47_phase61_final_association_visualisation.py: final classified correspondence evidence.

The phase-numbered scripts are research steps and have historical input/output dependencies. They are not all a single one-command production pipeline.

## Key retained data

- data/network/ASK033/: original image and camera/endpoint metadata.
- data/astrometry_indexes/ and astrometry/: local Astrometry.net index/configuration files.
- results/ASK033/: detection outputs, candidate tables, local WCS solutions, section correspondences, residual diagnostics and calibration reports.
- research/final_professor_evidence/: curated classified correspondence tables and summary.

## Scientific qualification

The ASK033 still-image investigation is exploratory. Recorded site/time metadata need confirmation. Local-WCS agreement does not independently prove catalogue identity, and the current global optical calibration has not passed independent multi-image validation.
