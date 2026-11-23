# STARLOC 2.0
### Stellar Vision & Multi-Section Astrometric Calibration for All-Sky Camera Networks
**Research direction:** Embedded Aerospace • Autonomous Optical Sensing • Geometric Calibration

[![Research](https://img.shields.io/badge/Project-R%26D%20Engineering-17324D)](#research-objective)
[![Processing](https://img.shields.io/badge/Pipeline-Stellar%20Vision%20%2B%20Astrometry-315B75)](#processing-architecture)
[![Implementation](https://img.shields.io/badge/Implementation-Python%20Prototype-3776AB)](#implementation)
[![Validation](https://img.shields.io/badge/Validation-Synthetic%20%2B%20Real--Image%20Study-C47A27)](#validation-evidence)

> **StarLoc 2.0 develops the software pipeline needed to recover camera geometry and orientation from observed stars, reconcile local astrometric solutions across overlapping image regions, and produce a consistent calibration model for wide-field optical systems.**

The project is motivated by the calibration requirements of the **AllSkyKamera Network**: determine the geometric properties and orientation of a camera from night-sky observations rather than relying blindly on potentially inaccurate installation parameters. The same core engineering problems—stellar feature extraction, celestial catalogue association, camera geometry, attitude references, uncertainty and robust estimation—are relevant to optical attitude sensing and autonomous aerospace systems.

---

## Research objective

Build and validate a software-defined calibration workflow that transforms a night-sky image into traceable pixel-to-sky geometry.

The central engineering challenge is not simply detecting bright points. It is establishing reliable correspondences between image observations and celestial reference directions, estimating the camera model, understanding where local solutions disagree, and combining evidence into a coherent global calibration.

### Target outputs

- Stellar detections with sub-pixel image coordinates.
- Catalogue associations linked to observation epoch and sky coordinates.
- Local astrometric solutions for image regions.
- Camera optical parameters and image-to-celestial transformations.
- Cross-section consistency and global-calibration diagnostics.
- Residual, uncertainty, quality and provenance information suitable for downstream processing.

## Why this is an embedded-aerospace project

StarLoc is centred on a real optical sensing and calibration problem. Its relevance extends beyond an all-sky monitoring network:

| Engineering capability | All-sky camera application | Aerospace / autonomy relevance |
|---|---|---|
| Stellar feature detection | Extract stars from night-sky images | Optical sensor front-end |
| Catalogue association | Identify observed stars | Celestial reference matching |
| Camera geometry estimation | Recover optical centre, scale and orientation | Sensor alignment and optical calibration |
| Multi-region solution reconciliation | Build a consistent full-image model | Multi-camera / multi-sensor geometric consistency |
| Temporal comparison | Investigate changes in orientation and calibration | Dynamic sensing and attitude-reference updates |
| Quality and residual analysis | Detect unreliable local solutions | Measurement validation and fault-aware estimation |

The current repository implements the research prototype and experiments in Python. A deterministic C++ core, target-hardware deployment and camera/IMU estimator are planned engineering stages—not capabilities claimed as already complete.

## Processing architecture

```text
       ALL-SKY IMAGE + OBSERVATION METADATA
       (timestamp, site, image geometry, camera context)
                         |
                         v
              IMAGE PRE-PROCESSING
                         |
                         v
          STELLAR CANDIDATE DETECTION
                         |
                         v
           SUB-PIXEL CENTROID ESTIMATION
                         |
                         +------------------------------+
                         |                              |
                         v                              v
              REFERENCE STAR CATALOGUE          IMAGE REGIONS / TILES
              epoch and sky coordinates          overlapping sections
                         |                              |
                         +---------------+--------------+
                                         |
                                         v
                          STAR / CATALOGUE ASSOCIATION
                                         |
                                         v
                            LOCAL ASTROMETRIC SOLUTIONS
                                         |
                                         v
                         CROSS-SECTION CONSISTENCY AUDIT
                                         |
                                         v
                         GLOBAL CAMERA MODEL ESTIMATION
                                         |
                                         v
                       PIXEL <-> CELESTIAL TRANSFORM
                                         |
                                         v
                     CALIBRATION QUALITY + UNCERTAINTY
                                         |
                                         v
                       VERSIONED CALIBRATION OUTPUT
                                         |
                          future integration interface
                                         v
                EMBEDDED OPTICAL / ATTITUDE SENSOR STACK
                                         |
                                         v
                AUTONOMOUS NAVIGATION / SENSOR FUSION
```

The real-image research has explored section-level astrometric solutions and their consistency. A fully validated global multi-section calibration product is the key research objective still to be closed.

## Research programme and implementation

The repository preserves a staged investigation rather than one monolithic script. The numbered experiments and phase artefacts provide a record of algorithm development, validation attempts and evidence.

| Workstream | Engineering content | Repository location |
|---|---|---|
| Synthetic sensor environment | Generate fisheye observations with known geometric truth | `research/`, `research/data/synthetic/` |
| Stellar image processing | Detection, centroid estimation and candidate refinement | `research/`, `research/real_image/`, `simulation/` |
| Catalogue and astrometry | Hipparcos data preparation, epoch propagation and visible-sky generation | `research/data/catalogue/`, `research/` |
| Blind identification | Catalogue-to-image matching and calibration experiments | `research/` |
| Robustness and performance | Noise, missing/false detections, residual and benchmark experiments | `research/`, `results/` |
| Real-camera investigation | ASK033 image analysis, local WCS, section correspondences and residual audits | `research/real_image/`, `research/final_professor_evidence/` |
| Research evidence | Reports, test plans, integrity records and presentation material | `research/docs/` |

## Selected experimental evidence

### 1. Controlled synthetic calibration

The documented blind synthetic experiment reports:

| Metric | Result |
|---|---:|
| Detected image regions | 1,136 |
| Catalogue candidates | 1,284 |
| Identified stars | 1,136 |
| Recovered field of view | 179.998° |
| Recovered roll | 36.999° |
| Reprojection RMSE | 0.2850 px |

This experiment demonstrates the end-to-end feasibility of the implemented detection, catalogue association and constrained fisheye calibration workflow under its synthetic assumptions. It is not a real-camera accuracy result.

### 2. Robustness under controlled degradation

Four documented synthetic scenes—clean, noisy, degraded and stress—reported a mean roll error of 0.00485° and mean reprojection RMSE of 0.90025 px. The stress scene reached 1.7174 px RMSE, showing the effect of degraded observations.

### 3. Real ASK033 image investigation

The project progressed from synthetic work to a public 1920 × 1440 ASK033 AllSkyKamera image. Five image sections obtained local astrometric solutions. The association audit recorded:

- 233 candidate correspondences in the cross-section audit.
- 74 strict internal-consistency cases.
- 155 uncertain cases.
- 4 separately flagged suspect associations.

The Phase 56 strict-subset experiment reported 0.9381 px RMSE on 15 randomly held-out points. The more demanding Phase 57 leave-one-section-out evaluation reported 2.3247 px aggregate RMSE, with R3C1 reaching 3.460 px.

**What these results mean:** the real-image work demonstrates a substantial investigation of local astrometry, correspondence quality and section-dependent calibration behaviour. It does not yet establish an independently validated global camera solution. Agreement with a local WCS is an internal consistency check, not independent proof of catalogue identity. The next validation campaign must use independently verified references and multiple real observations.

## Current engineering status

| Capability | Evidence status |
|---|---|
| Synthetic fisheye image generation | Implemented |
| Stellar detection and centroid estimation | Implemented and experimentally evaluated |
| Hipparcos catalogue preparation and epoch handling | Implemented in research workflow |
| Blind catalogue matching | Demonstrated on synthetic data |
| Constrained fisheye optical calibration | Demonstrated on synthetic data |
| Synthetic robustness and multi-section experiments | Documented |
| ASK033 real-image investigation | Conducted; exploratory |
| Real-image correspondence quality audit | Conducted; unresolved/uncertain cases retained |
| Independently validated global multi-section calibration | Remaining research milestone |
| Dynamic orientation across a time series | Further validation and integration required |
| Production server-side service/API | Not yet implemented as a deployable service |
| Embedded C++ / RTOS target implementation | Future engineering work |
| Camera/IMU fusion and autonomous attitude estimator | Future research and integration work |

## Repository structure

```text
.
├── README.md
├── README_STARLOC_FINAL.md
├── research/
│   ├── *.py
│   ├── real_image/                 # ASK033 image investigation
│   ├── data/
│   │   ├── catalogue/              # Hipparcos-derived reference data
│   │   └── synthetic/              # generated observations / ground truth
│   ├── final_professor_evidence/   # classified correspondence evidence
│   ├── docs/                       # reports, specifications and plans
│   └── results/                    # research outputs and diagnostics
├── simulation/
│   └── lesson_*/                   # staged algorithm development
└── results/                        # selected simulation figures
```

## Running the research

The repository is a Python research workspace developed on macOS. The documented stack includes Python, NumPy, SciPy, OpenCV, Astropy and Matplotlib.

Create an isolated environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

Install the dependencies required by the experiment being run. A single pinned, repository-wide environment is a reproducibility task still to be consolidated; historical scripts may have different dependencies and generated-file prerequisites.

Documented entry points:

```bash
# Main synthetic demonstration
python research/16_run_final_demo.py

# Integrated Phase 62 evidence demonstration
python research/48_phase62_integrated_demo.py
```

Run from the repository root. The Phase 62 script integrates previously generated evidence; it does not rerun every experiment or independently refit the calibration model. Consult [Research Workspace Guide](research/docs/README_RESEARCH.md) before running individual experiments.

## Engineering roadmap

The roadmap is ordered to protect scientific validity before moving toward embedded deployment.

1. **Close the real-camera validation loop** — independent star identities/reference solutions, verified timestamps and site metadata, multiple images, held-out-section testing and documented acceptance thresholds.
2. **Complete global multi-section calibration** — robustly reconcile overlapping local solutions, model distortion and quantify the global transform's uncertainty.
3. **Add temporal orientation analysis** — evaluate repeatability and camera-orientation changes over image sequences, separating real movement from calibration noise.
4. **Harden the software architecture** — modular interfaces, coordinate-frame contracts, units, error handling, deterministic regression data and reproducible configuration.
5. **Develop an embedded C++ implementation** — port selected algorithms, cross-check against Python and measure latency, memory and numerical deviation on a selected target.
6. **Integrate into autonomous sensing** — define camera-to-body alignment, timestamped attitude observations and quality gates; investigate gyro/IMU fusion as a separate estimator workstream.

See the [Embedded & Aerospace Engineering Roadmap](research/docs/embedded_aerospace_roadmap.md).

## Technical documentation

- [System architecture and interfaces](research/docs/system_architecture.md)
- [Research and experiment guide](research/docs/README_RESEARCH.md)
- [Final research report](research/docs/final_report.md)
- [Functional and technical specifications](research/docs/functional_technical_specifications.md)
- [Test plan and validation evidence](research/docs/test_plan_and_results.md)
- [Real-camera validation matrix](research/docs/real_camera_validation_matrix.md)
- [Embedded and aerospace roadmap](research/docs/embedded_aerospace_roadmap.md)
- [State of the art](research/docs/state_of_art.md)
- [Feasibility study](research/docs/feasibility_study.md)
- [Risk analysis](research/docs/risk_analysis.md)
- [Project schedule](research/docs/project_schedule_gantt.md)
- [Presentation outline](research/docs/presentation_outline.md)
- [Submission checklist](research/docs/submission_checklist.md)

## Application context

**Primary R&D application:** server-side optical calibration of the AllSkyKamera Network, where reliable camera orientation and pixel-to-celestial transformations support downstream sky observation and trajectory analysis.

**Related engineering domains:** star-sensor research, optical attitude determination, autonomous aerial/robotic sensing, embedded computer vision, camera geometry and multi-sensor estimation.

The current project is a research prototype. It is not presented as a flight-qualified star tracker, a certified aerospace component or a deployed calibration service.

---

**StarLoc 2.0 — from stellar observations to traceable camera geometry.**
