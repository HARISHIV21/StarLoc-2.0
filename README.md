# StarLoc 2.0
## Stellar Vision, Optical Calibration & an Embedded-Aerospace Development Path

[![Python](https://img.shields.io/badge/Python-research%20prototype-blue)](https://www.python.org/)
[![Domain](https://img.shields.io/badge/Domain-Aerospace%20%7C%20Embedded%20%7C%20Autonomy-16324F)](#)
[![Status](https://img.shields.io/badge/Status-R%26D%20prototype-orange)](#project-status)

**StarLoc 2.0** is a research and development project exploring catalogue-based stellar detection, identification and optical calibration for wide-field / all-sky imaging systems. It investigates the computer-vision and geometric-estimation stages that are relevant to star sensors, celestial navigation and autonomous aerospace systems.

The repository contains a Python research prototype, synthetic experiments, a real-camera investigation using a public ASK033 AllSkyKamera image, validation artefacts and technical documentation.

> **Engineering scope:** StarLoc is currently an optical-calibration and stellar-identification research prototype. It is not yet a flight-qualified star tracker, a real-time embedded implementation, or a completed star-camera/IMU fusion system. Those are explicit development directions, not claimed capabilities.

---

## 1. Why this project matters to aerospace and autonomous systems

Reliable orientation and environmental awareness are important in spacecraft, UAVs, autonomous platforms and other systems that cannot depend exclusively on external positioning infrastructure.

StarLoc investigates a relevant sensing chain:

1. Extract stellar observations from an image.
2. Estimate sub-pixel image coordinates for detected stars.
3. associate observations with a reference star catalogue.
4. Convert image measurements into geometric constraints.
5. Estimate camera parameters and quantify residual error.
6. Assess robustness, consistency and confidence before downstream use.

These capabilities form a foundation for further work on optical attitude sensors and autonomous navigation. The current implementation focuses on the vision and calibration problem; integration into an embedded flight-control or navigation architecture remains future work.

## 2. Project objectives

- Develop and evaluate star-detection and centroid-estimation methods.
- Prepare and use astronomical reference data, including Hipparcos-derived catalogues.
- Investigate blind catalogue-to-image correspondence.
- Estimate fisheye optical parameters using geometric optimisation.
- Evaluate sensitivity to noise, missing detections, false detections and image degradation.
- Investigate local astrometric solutions and cross-section consistency on a real all-sky camera image.
- Preserve experiment outputs, assumptions, limitations and validation evidence.
- Define a technically credible route toward deterministic C++ modules and embedded aerospace integration.

## 3. Processing architecture

```text
                  IMAGE / OBSERVATION METADATA
                              |
                              v
                    Image preparation
                              |
                              v
                 Stellar candidate detection
                              |
                              v
                Sub-pixel centroid estimation
                              |
                              v
       Reference catalogue + epoch / sky-coordinate processing
                              |
                              v
                  Catalogue correspondence
                              |
                              v
             Pixel-to-celestial correspondence
                              |
                              v
                Fisheye optical calibration
                              |
                              v
             Residuals, diagnostics, validation
                              |
                              v
            Calibration parameters + evidence
                              |
                 Future integration boundary
                              v
        Embedded C++ / real-time sensor architecture
                              |
                              v
          Future attitude estimator / IMU fusion
```

The final two blocks are proposed development stages. They are not represented as completed software in this repository.

## 4. Current technical scope

| Area | Current status |
|---|---|
| Synthetic fisheye image generation | Implemented in research experiments |
| Star candidate detection and centroiding | Implemented and experimentally evaluated |
| Hipparcos catalogue preparation | Implemented |
| Proper-motion / epoch processing | Implemented in catalogue workflow |
| Blind catalogue matching | Implemented in synthetic experiments |
| Fisheye optical parameter estimation | Implemented in synthetic experiments |
| Noise and degraded-image robustness | Experimentally evaluated |
| Multi-section synthetic analysis | Experimentally evaluated |
| Public ASK033 real-image investigation | Conducted; exploratory |
| Independent real-camera ground-truth validation | Not yet established |
| Embedded C/C++ implementation | Not yet implemented |
| RTOS / hardware sensor integration | Not yet implemented |
| Star-camera + IMU fusion | Not yet implemented |
| Flight qualification / safety certification | Out of current scope |

## 5. Selected experimental evidence

### Synthetic experiments

The documented blind synthetic calibration experiment reports:

- 1,136 detected image regions.
- 1,136 identified stars in that experiment.
- Estimated field of view: 179.998°.
- Estimated roll: 36.999°.
- Reprojection RMSE: 0.285 pixels.

These figures are specific to the documented synthetic experiment and its assumptions. They are not real-camera accuracy claims.

### Real-camera investigation

A public ASK033 image (1920 × 1440) was investigated using local astrometric solutions across image sections. The research audit records 233 candidate correspondences: 74 strict internal-consistency cases, 155 uncertain cases and four suspect associations.

The exploratory global calibration and cross-section tests show why independent validation matters: the documented leave-one-section-out aggregate RMSE is 2.3247 pixels, with section-dependent errors. Local-WCS consistency is not independent proof of catalogue identity.

**Interpretation:** synthetic feasibility is demonstrated; real-camera calibration remains exploratory and requires independent astrometric validation, more observations and confirmed acquisition metadata.

See [Research Workspace](research/docs/README_RESEARCH.md), [Final Report](research/docs/final_report.md) and [Test Plan & Results](research/docs/test_plan_and_results.md).

## 6. Repository guide

```text
.
├── README.md
├── README_STARLOC_FINAL.md
├── .gitignore
├── research/
│   ├── *.py                    # numbered research experiments
│   ├── real_image/             # ASK033 real-image investigation
│   ├── data/
│   │   ├── catalogue/          # astronomical reference data
│   │   └── synthetic/          # generated observations and ground truth
│   ├── docs/                   # specifications, reports and validation
│   ├── final_professor_evidence/
│   └── results/                # experiment outputs and diagnostics
├── simulation/
│   └── lesson_*/               # staged algorithm-development exercises
└── results/                    # selected simulation figures and outputs
```

The numbered research scripts preserve the experiment history. The lesson-based simulation scripts provide a staged learning and algorithm-development trail. Use the research documentation to identify the intended entry points and the assumptions behind each experiment.

## 7. Environment and reproducibility

The repository is a Python research workspace. The documented environment uses Python with NumPy, SciPy, OpenCV, Astropy and Matplotlib.

From the repository root, create and activate an isolated environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

Install the dependencies required by the experiment you intend to run. A pinned, repository-wide dependency file and a single supported end-to-end setup command should be added as part of the reproducibility hardening work; do not assume every historical script has identical dependencies.

The repository documentation identifies these useful experiment entry points:

```bash
# Main synthetic demonstration
python research/16_run_final_demo.py

# Integrated Phase 62 evidence demonstration
python research/48_phase62_integrated_demo.py
```

Run commands from the repository root. Some experiments depend on previously generated catalogue, image or intermediate result files. Read the relevant script and its documentation before running it. The Phase 62 integration script indexes prior evidence; it does not rerun all earlier experiments or refit the calibration.

## 8. Aerospace and embedded development roadmap

The roadmap deliberately separates completed research from future engineering work.

### Work package A — Research baseline and validation
- Consolidate the accepted optical model and document coordinate-frame conventions.
- Make experiment inputs, random seeds, parameter settings and outputs reproducible.
- Add independent real-image reference measurements and multi-frame evaluation.
- Quantify uncertainty, outliers, failure cases and calibration confidence.
- Define measurable acceptance criteria for each experiment.

### Work package B — Algorithm modularisation
- Separate image acquisition, preprocessing, detection, centroiding, matching and calibration into testable interfaces.
- Define explicit data structures, units, coordinate frames and error codes.
- Profile runtime and memory use on representative image sizes.
- Identify algorithms that can be ported without changing their mathematical behaviour.

### Work package C — Embedded implementation
- Port selected deterministic compute-intensive modules to modern C++.
- Define bounded memory use, allocation policy and execution-time budgets.
- Build host-based unit tests and Python/C++ numerical cross-checks.
- Evaluate target hardware constraints before selecting an MCU, SoC or embedded Linux platform.
- Add hardware-in-the-loop tests only when a target platform is selected.

### Work package D — Autonomous aerospace integration
- Define camera-to-body and body-to-navigation frame transformations.
- Specify timestamping, sensor interfaces and measurement-quality metadata.
- Design an estimator interface for camera-derived attitude observations.
- Investigate gyro propagation and camera/IMU fusion (for example, an EKF) as a separate validated work package.
- Evaluate degraded sensing, rejected observations, recovery behaviour and fault handling.

### Work package E — Verification and assurance
- Establish requirements-to-test traceability.
- Add repeatable regression datasets and automated test reports.
- Measure latency, throughput, memory footprint and failure rates on target hardware.
- Document limitations and verification evidence.
- Treat aerospace standards and certification as system-level activities requiring a defined target, safety assessment and qualified process.

## 9. Engineering quality principles

The project is being organised around practices expected in embedded and aerospace software:

- **Traceability:** every reported result should point to its experiment, input and configuration.
- **Reproducibility:** record dependencies, seeds, parameters and execution instructions.
- **Numerical integrity:** document coordinate frames, units, conventions and tolerances.
- **Verification:** distinguish training / fitting data from held-out and independent validation data.
- **Robustness:** retain failure cases and uncertainty rather than hiding them.
- **Honest claims:** label synthetic, exploratory real-image and independently validated results separately.
- **Portability:** design future modules with clear interfaces and measurable resource budgets.

## 10. Documentation index

- [Research workspace guide](research/docs/README_RESEARCH.md)
- [Final research report](research/docs/final_report.md)
- [Functional and technical specifications](research/docs/functional_technical_specifications.md)
- [Test plan and results](research/docs/test_plan_and_results.md)
- [State of the art](research/docs/state_of_art.md)
- [Feasibility study](research/docs/feasibility_study.md)
- [Risk analysis](research/docs/risk_analysis.md)
- [Project schedule](research/docs/project_schedule_gantt.md)
- [Presentation outline](research/docs/presentation_outline.md)
- [Submission checklist](research/docs/submission_checklist.md)

## 11. Potential applications

The underlying engineering themes are relevant to:

- Spacecraft star-sensor and optical attitude-determination research.
- Autonomous aerial and robotic platforms requiring robust orientation sensing.
- Wide-field optical instrumentation and sky-monitoring networks.
- Embedded computer vision and sensor-processing pipelines.
- Research into camera/IMU complementary sensing.

These are potential application areas, not claims that the current prototype has been deployed or qualified in those systems.

## 12. Project status

**Current stage:** research prototype with synthetic algorithmic validation and an exploratory real-camera investigation.

**Primary next milestone:** establish independently validated real-camera calibration, then modularise and benchmark the algorithm before beginning an embedded C++ port.

---

*Developed as an engineering R&D project focused on stellar vision, optical calibration and the pathway toward embedded aerospace and autonomous sensing systems.*
