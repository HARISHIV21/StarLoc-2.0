# StarLoc 2.0 — concise project entry point

StarLoc 2.0 is a Python research prototype for stellar-image processing and multi-section astrometric calibration of wide-field all-sky cameras.

**For the authoritative project scope, implemented status, synthetic results, real-observation evidence and remaining validation work, see the [main README](README.md).**

## Start with the evidence

- [Real Observations & Experimental Evidence — ASK033 and T1](REAL_OBSERVATIONS.md)
- [Real-image research workspace](research/real_image/README.md)
- [Final R&D report](research/docs/final_report.md)
- [Real-camera validation matrix](research/docs/real_camera_validation_matrix.md)
- [Research workspace guide](research/docs/README_RESEARCH.md)

## Current scope

The repository contains:
- Synthetic fisheye image generation, candidate detection, catalogue processing, blind matching and constrained optical calibration experiments.
- ASK033 real still-image detection and local astrometric investigation across five sections.
- ASK033 archive-derived temporal experiments, including feature tracking, photometry/morphology, candidate ranking, catalogue consistency, registration and coordinate-integrity audits through Phase 147.
- A separate T1 real-image detection and candidate-ranking experiment.

## Scientific qualification

The real-image work is substantial but exploratory. Candidate features and tracks are not automatically confirmed stars. Existing-WCS correspondence, repeated IDs and cross-phase agreement are not independent astrometric truth. The original archive MP4 is referenced by reports but is not in the Git tree; ASK033 timestamp/exposure semantics also need resolution.

Independent real-star identity validation, globally validated multi-image calibration, physical camera-motion validation, a production server-side service, embedded C++ deployment and camera/IMU fusion remain open.

This file is intentionally a short navigation page. The main README and linked evidence documents are authoritative.
