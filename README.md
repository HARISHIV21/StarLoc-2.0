# StarLoc 2.0 — Star Identification and Optical Calibration for All-Sky Cameras

**Primary R&D objective:** detect stars in a real all-sky image, identify them in a celestial catalogue using observation date/time and approximate observer location, convert their accurate RA/Dec coordinates to image pixels, and determine the camera's optical calibration.

The project follows the priorities provided by the professor. It is not currently presented as a complete star tracker, observer-position solver, mobile-robotics estimator or IMU-fusion system.

## Professor's four core objectives

1. **Find stars in the image.** Detect point sources and estimate reliable sub-pixel centroids.
2. **Identify the stars in a catalogue.** Use observation date/time and approximate observer position to predict visible catalogue stars and associate detections with catalogue identities. If observer position is unknown, defer that harder problem.
3. **Convert RA/Dec to pixel coordinates.** Use identified stars' celestial coordinates and the image astrometric transform to obtain corresponding image coordinates, with explicit coordinate conventions and round-trip checks.
4. **Determine optical calibration.** Estimate and validate optical centre, focal scale/FOV and distortion model from identified star correspondences.

See [Professor Objectives & Traceability](PROFESSOR_OBJECTIVES.md) for the mapping from each objective to existing scripts, data and evidence.

## Current status — evidence-based

| Objective | Current status | Evidence / remaining gap |
|---|---|---|
| 1. Star detection | Implemented and tested synthetically and on ASK033 | Detection, quality filtering and centroid-refinement scripts/results exist; independent real-image detection labels are still needed |
| 2. Catalogue identification | Synthetic blind identification demonstrated; real ASK033 associations exploratory | Hipparcos processing, epoch handling and local WCS matching exist; timestamp/site provenance and independent star-identity verification remain open |
| 3. RA/Dec → pixel | Conversion workflow implemented for local WCS sections | Script 25_objective3_radec_to_pixel.py; verify inputs, coordinate origin, section offsets and independent accuracy |
| 4. Optical calibration | Synthetic constrained calibration demonstrated; real global model exploratory | Local section WCS and global fisheye/SIP audits exist; one independently validated global real-camera calibration is not yet established |

## Processing architecture

    REAL IMAGE + OBSERVATION METADATA
    (date/time, approximate site, image dimensions)
                     |
                     v
             STAR DETECTION
                     |
                     v
        SUB-PIXEL CENTROID ESTIMATION
                     |
                     v
         CATALOGUE / EPOCH PREPARATION
                     |
                     v
           STAR IDENTIFICATION
                     |
                     v
          RA/DEC <-> PIXEL MAPPING
                     |
                     v
           OPTICAL CALIBRATION
                     |
                     v
      RESIDUALS / DISTORTION / VALIDATION
                     |
                     v
        CALIBRATION RESULT + DEMO

## Real observation retained as the main application dataset

The active real-camera dataset is the public **ASK033 AllSkyKamera** still image:

- Image size: 1920 × 1440 pixels.
- Recorded site metadata: Miesenbach, Austria (47.834° N, 16.005° E); recorded metadata, not an independently surveyed site reference.
- Five image sections have local astrometric solutions: R1C2, R2C1, R2C2, R3C1 and R3C2.
- The historical association audit classified 233 candidates as 74 strict internal-consistency, 155 uncertain and 4 suspect. These labels do not independently certify catalogue identity.
- Phase 37B recorded 237 accepted geometric matches using its stated 5-pixel gate; this is a separate result and must not be conflated with the 233-point classified audit.

**Metadata blocker:** the endpoint query timestamp and separate image-overlay timestamp do not agree. The exposure-time meaning (start, midpoint or end) also requires confirmation before epoch-dependent coordinates can be treated as final.

Open [REAL_OBSERVATIONS.md](REAL_OBSERVATIONS.md) for the source image, metadata, detection outputs, local solutions and retained real-image reports.

## Necessary synthetic observations — retained

Synthetic observations remain in the project because they provide controlled ground truth for testing detection, catalogue association, coordinate mapping and optical calibration before claiming real-camera accuracy.

The retained synthetic pipeline includes:
- A 1024 × 1024, nominal 180° equidistant-fisheye synthetic observation with known camera parameters.
- A separate catalogue-rendered synthetic observation built from Hipparcos-derived stars and a documented temporary Rouen test location.
- Ground-truth catalogues, metadata, detection/matching outputs, calibration reports and robustness results.
- A reproducible blind synthetic demo and robustness test.

See [Synthetic Observation & Validation](research/docs/synthetic_observation_validation.md). Synthetic performance numbers must never be reported as real ASK033 accuracy.

## Run the synthetic demonstration

From the repository root:

    python3 -m venv .venv
    source .venv/bin/activate
    python -m pip install numpy scipy opencv-python astropy matplotlib
    python research/16_run_final_demo.py

This is the documented research dependency set, not yet a pinned lock file. The demo runs the catalogue-based synthetic calibration and robustness workflow. It does not rerun ASK033 real-image calibration.

## Main source-code entry points

| Purpose | Script |
|---|---|
| Generate controlled synthetic fisheye data | research/01_generate_fisheye_dataset.py |
| Detect synthetic stars | research/02_detect_fisheye_stars.py |
| Optimise detection | research/03_optimize_star_detection.py |
| Initial synthetic optical calibration | research/04_fisheye_optical_calibration.py |
| Download / clean / propagate Hipparcos data | research/07–10 |
| Render catalogue-based synthetic observation | research/11_render_catalogue_fisheye.py |
| Blind catalogue matching and calibration | research/12_blind_catalogue_calibration.py |
| Synthetic robustness validation | research/13_robustness_validation.py |
| Run synthetic demonstration | research/16_run_final_demo.py |
| Detect/refine real ASK033 candidates | research/real_image/04–06 |
| Build real-image visible catalogue | research/real_image/07_build_ask033_catalogue.py |
| Local astrometric solve and validation | research/real_image/12–24 |
| RA/Dec to pixel conversion | research/real_image/25_objective3_radec_to_pixel.py |
| Optical calibration / distortion audits | research/real_image/26–44 |
| Final real-image association evidence | research/real_image/46–47 |
| Integrated evidence demonstration | research/48_phase62_integrated_demo.py |

Historical scripts are retained where they support the four core objectives. They are staged research experiments, not one automatic production pipeline.

## Required project deliverables

- Project tracking documents and planning.
- Functional and technical specifications.
- Research source code and preserved input datasets.
- Synthetic test observations with known ground truth.
- Real ASK033 observation and traceable detection/catalogue/calibration evidence.
- Test plan, results and limitations.
- A repeatable synthetic demonstration and, where possible, a real-image evidence demo.
- Final report and oral presentation.

## Later objectives — explicitly outside the current core scope

Only after the four core objectives are sufficiently validated should the project consider:
1. Image orientation relative to the celestial dome, Sun or Moon.
2. Estimating observer position from stellar observations.
3. Coupling one or two IMUs to account for motion in mobile robotics.

These are future extensions, not completed capabilities.

## Scientific limitations

- ASK033 uses one real still image in the active scope.
- Recorded site and timestamp metadata require confirmation.
- Local WCS consistency is not independent proof of catalogue identity.
- The global real-camera optical model remains exploratory.
- A deployable server-side calibration service, embedded implementation and IMU fusion are not current deliverables.

**StarLoc 2.0 — detect stars, identify them, map celestial coordinates to pixels, and calibrate the camera.**
