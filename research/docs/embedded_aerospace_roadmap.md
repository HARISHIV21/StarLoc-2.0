# Embedded Aerospace & Autonomous Sensing — Engineering Roadmap

## Strategic intent

StarLoc's core research is the recovery of camera geometry and orientation from stellar observations. The first obligation is to solve and validate the AllSkyKamera multi-section calibration problem. Embedded aerospace development should build on a numerically trusted, modular optical measurement pipeline.

This is a staged engineering programme, not a claim that the current Python prototype is already an embedded star tracker.

## WP1 — Close the real-camera calibration problem

- Build a multi-image ASK dataset with verified timestamps and installation metadata.
- Independently validate catalogue identities.
- Quantify local WCS quality and section-dependent residuals.
- Develop a robust method to reconcile overlapping section solutions.
- Estimate one consistent global camera model and its uncertainty.
- Evaluate repeatability across time and camera-orientation changes.

**Gate:** independently validated global calibration on multiple real images, with spatial and temporal generalisation results.

## WP2 — Define a stable numerical architecture

Separate the research pipeline into modules:
1. Image input and metadata validation.
2. Preprocessing and star detection.
3. Centroid and measurement-quality estimation.
4. Catalogue and epoch/coordinate transformation.
5. Star correspondence and outlier rejection.
6. Local astrometric solution.
7. Global camera calibration.
8. Temporal consistency and result publication.

Specify coordinate frames, transform directions, pixel conventions, units, time scales, uncertainty representation and failure codes.

**Gate:** module contracts, regression fixtures and reproducible end-to-end research run.

## WP3 — C++ algorithm port

- Identify computationally intensive and numerically self-contained components.
- Port one module at a time to modern C++.
- Preserve a Python reference implementation.
- Cross-check outputs using fixed datasets and tolerances.
- Add unit and integration tests.
- Avoid unbounded allocation in any future time-critical path.

**Gate:** Python/C++ numerical equivalence report and repeatable host-side test suite.

## WP4 — Target selection and embedded performance

Select hardware only after establishing image dimensions, throughput, frame rate, latency, memory and interface requirements.

Evaluate whether the intended deployment is:
- Embedded Linux / SoC for camera and compute-heavy image processing.
- MCU / RTOS for deterministic control, sensor interfaces or reduced processing.
- A partitioned architecture with optical processing on a compute module and time-critical control on an MCU.

Measure execution time, peak memory, CPU load, data movement and failure behaviour on the actual target. Do not claim real-time performance without measured worst-case evidence.

**Gate:** documented target rationale, resource budget and hardware benchmark report.

## WP5 — Aerospace optical attitude interface

Define:
- Camera-to-body extrinsic calibration.
- Body and navigation coordinate frames.
- Timestamp and latency semantics.
- Attitude measurement representation.
- Measurement covariance / quality indicators.
- Rejection and reacquisition behaviour.

The optical calibration output should be a timestamped measurement with explicit quality metadata. It is not itself a complete attitude estimator.

**Gate:** interface specification and simulation-based integration tests.

## WP6 — Camera/IMU fusion and autonomous sensing

As a separate subsystem:
- Propagate attitude using gyro measurements.
- Apply accepted optical attitude observations.
- Select an estimator (e.g. EKF) based on the defined state and sensor models.
- Evaluate observability, noise assumptions, timestamp alignment and latency.
- Test loss of stars, false associations, dynamic camera motion and reacquisition.
- Measure attitude error against independent truth.

**Gate:** estimator design, fault/degraded-mode tests and quantified performance.

## WP7 — Verification and aerospace engineering discipline

- Requirements-to-test traceability.
- Unit, integration, regression and hardware-in-the-loop testing.
- Fault injection and robustness analysis.
- Data/configuration provenance.
- Memory, timing and failure-mode budgets.
- System safety and applicable standards assessment when a target application is defined.

No certification or compliance claim should be made without a defined system boundary and appropriate evidence.

## Milestone sequence

| Milestone | Deliverable |
|---|---|
| M1 | Independently validated real-camera dataset |
| M2 | Global multi-section camera calibration |
| M3 | Temporal orientation / repeatability analysis |
| M4 | Modular software architecture and regression suite |
| M5 | C++ reference implementation |
| M6 | Target-hardware resource and timing benchmark |
| M7 | Camera attitude measurement interface |
| M8 | Camera/IMU fusion prototype |
| M9 | Integrated autonomous sensing demonstration |

## Engineering priority

Do not begin with an RTOS port or an arbitrary microcontroller. First establish that the real-image calibration and global geometric model are correct. Then modularise, port, benchmark and integrate. This creates a credible bridge from the professor's AllSkyKamera R&D problem to embedded aerospace and autonomous sensing.
