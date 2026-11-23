# StarLoc 2.0

**Stellar Identification & Multi-Section Astrometric Calibration for All-Sky Camera Networks**

This repository contains the research implementation, experiments and validation evidence for StarLoc 2.0. The primary R&D problem is recovering camera geometry and orientation from stellar observations for the AllSkyKamera Network, including local astrometric analysis across overlapping image regions and the development of a globally consistent calibration.

For the full project scope, architecture, experimental evidence and engineering roadmap, see the [main project README](README.md).

## Current evidence

- Synthetic stellar detection, catalogue matching and constrained fisheye calibration.
- Hipparcos-derived catalogue preparation and epoch processing.
- Synthetic robustness and multi-section experiments.
- Exploratory investigation of a public ASK033 real-camera image.
- Correspondence-quality audit and leave-one-section-out analysis.

## Important scope distinction

The current implementation is a Python research prototype. Independent real-camera global calibration, a deployable server-side service, embedded C++/RTOS implementation and camera/IMU fusion remain future engineering work.

## Technical documentation

- [System architecture](research/docs/system_architecture.md)
- [Research workspace](research/docs/README_RESEARCH.md)
- [Final R&D report](research/docs/final_report.md)
- [Functional and technical specification](research/docs/functional_technical_specifications.md)
- [Verification plan and evidence](research/docs/test_plan_and_results.md)
- [Real-camera validation matrix](research/docs/real_camera_validation_matrix.md)
- [Embedded aerospace roadmap](research/docs/embedded_aerospace_roadmap.md)
