# Embedded, Aerospace & Autonomous Systems Roadmap

## Purpose

This roadmap defines how the existing StarLoc 2.0 optical-calibration research can evolve toward an embedded aerospace sensing component. It distinguishes current evidence from proposed work.

## Baseline: what exists today

- Python research scripts for synthetic fisheye image generation, stellar candidate detection, centroiding, catalogue preparation, matching and optical calibration.
- Synthetic robustness experiments and multi-section analysis.
- An exploratory investigation of a public ASK033 all-sky image.
- Research reports, test evidence and diagnostic outputs.

The current repository does not yet contain a production C++ implementation, an RTOS target, a camera hardware driver, a flight computer integration, a completed IMU-fusion estimator or flight qualification evidence.

## Work package 1 — Real-camera scientific validation

**Objective:** establish whether the optical model generalises beyond generated images.

Tasks:
1. Secure a set of real camera images with verified timestamps and acquisition metadata.
2. Obtain independent astrometric reference solutions or independently verified star identities.
3. Evaluate multiple nights, sky regions and image-quality conditions.
4. Separate calibration-fit observations from independent validation observations.
5. Report pixel residuals, angular residuals, uncertainty, outliers and failure cases.
6. Compare global and local-section models without treating local-WCS consistency as independent ground truth.

Exit evidence:
- Reproducible dataset manifest.
- Independent reference and validation protocol.
- Multi-image validation report.
- Explicit acceptance thresholds agreed before final evaluation.

## Work package 2 — Software architecture and numerical contracts

**Objective:** convert research scripts into maintainable components.

Proposed modules:
- Image input and metadata validation.
- Preprocessing and candidate detection.
- Centroid estimation.
- Catalogue and coordinate transformation.
- Star correspondence and outlier rejection.
- Camera projection and distortion model.
- Calibration solver.
- Diagnostics and result serialization.

Define:
- Coordinate frames and transformation direction.
- Angle and distance units.
- Pixel origin and axis conventions.
- Timestamp scale and epoch conventions.
- Input validity, confidence and error codes.
- Numerical tolerances and deterministic test fixtures.

Exit evidence:
- Module-level interfaces and design note.
- Unit tests for each module.
- Regression fixtures from known synthetic and real observations.

## Work package 3 — Embedded C++ feasibility and port

**Objective:** determine which algorithms can execute within a defined target's compute and memory limits.

Tasks:
1. Select a target only after estimating image size, frame rate, compute load, memory and interface requirements.
2. Port one module at a time, beginning with numerically self-contained operations.
3. Use fixed-size or bounded buffers where appropriate.
4. Avoid unbounded dynamic allocation in time-critical paths.
5. Cross-check C++ outputs against the Python reference implementation.
6. Measure worst-case execution time, memory use and numerical deviation on target hardware.

Potential implementation choices (to be assessed, not assumed):
- Modern C++ for deterministic algorithm modules.
- OpenCV or a reduced/custom image-processing implementation depending on target resources.
- Embedded Linux for camera/compute-heavy platforms, or an RTOS/MCU for bounded control and sensor-interface tasks.

Exit evidence:
- Target rationale and resource budget.
- Python-versus-C++ equivalence report.
- Timing and memory measurements on the selected hardware.
- Automated host and target regression tests.

## Work package 4 — Attitude and autonomous-system interface

**Objective:** define how optical measurements could contribute to an autonomous platform's attitude estimate.

Tasks:
1. Define camera-to-body extrinsic calibration and body/navigation frame conventions.
2. Specify observation timestamps and measurement latency.
3. Convert accepted star observations into a documented attitude-measurement interface.
4. Define quality metrics and rejection criteria.
5. Design gyro propagation and camera/IMU fusion as a separately testable estimator.
6. Evaluate loss of stars, false matches, timing faults and reacquisition.

Possible future estimator:
- Gyroscope propagation between optical updates.
- Camera-derived attitude observations when valid.
- An EKF or other estimator selected after defining state, noise models and observability.

Exit evidence:
- Coordinate-frame and timing specification.
- Estimator design and observability analysis.
- Simulation tests for nominal and degraded conditions.
- Quantified attitude error and recovery performance.

## Work package 5 — Aerospace verification discipline

Tasks:
- Requirements and interface traceability.
- Verification plan and acceptance criteria.
- Unit, integration, regression and hardware-in-the-loop tests.
- Fault injection and robustness tests.
- Data provenance and configuration control.
- Resource, latency and failure-mode analysis.

No compliance or certification claim should be made without a defined system boundary, applicable standards, safety case and evidence from the relevant engineering process.

## Suggested milestone sequence

| Milestone | Deliverable | Dependency |
|---|---|---|
| M1 | Independent multi-image validation | Real images and reference data |
| M2 | Modular software architecture | Stable numerical contracts |
| M3 | C++ reference port | M2 and regression fixtures |
| M4 | Target-hardware benchmark | Selected compute platform |
| M5 | Attitude measurement interface | Frame and timing definitions |
| M6 | Camera/IMU estimator prototype | Validated optical measurement model |
| M7 | Integrated autonomy demonstration | Target platform and system tests |

## Priority recommendation

Do not start by adding an RTOS or claiming real-time operation. First establish independent real-camera accuracy and stable module interfaces. Then port and benchmark the computational core. This reduces the risk of embedding an algorithm whose real-world measurement quality is not yet established.
