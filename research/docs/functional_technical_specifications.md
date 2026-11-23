# StarLoc 2.0 — Functional & Technical Specification
## Stellar Identification and Multi-Section Astrometric Calibration

## 1. System mission

StarLoc 2.0 is an R&D software system intended to recover optical geometry and orientation of wide-field all-sky cameras from stellar observations. The primary application context is server-side calibration for the AllSkyKamera Network.

The system is expected to transform image observations and acquisition metadata into a traceable pixel-to-celestial calibration, including local image-region solutions, cross-section quality assessment and a consistent global camera model.

This document distinguishes the target system requirements from the capabilities currently demonstrated by the Python research prototype.

## 2. Operational context

A calibration run is expected to use:
- An all-sky or wide-field night-sky image.
- Observation timestamp with explicit time-scale convention.
- Observer location and metadata provenance.
- Image dimensions and pixel-coordinate convention.
- Camera/lens context where available.
- A versioned stellar reference catalogue.
- Optional initial pointing or previous calibration as a prior, with uncertainty.

Missing or uncertain metadata must be flagged. The implementation must not silently substitute a guessed location, timestamp or pointing.

## 3. Functional requirements

| ID | Requirement | Current evidence / status |
|---|---|---|
| FR-01 | Load and validate astronomical catalogue records | Research workflow implemented for Hipparcos-derived data |
| FR-02 | Handle catalogue epoch and proper-motion information | Implemented in catalogue preparation workflow |
| FR-03 | Generate or obtain image observations | Synthetic renderer implemented; public ASK033 image investigated |
| FR-04 | Detect stellar candidates in image data | Implemented and experimentally evaluated |
| FR-05 | Estimate sub-pixel image centroids | Implemented in research experiments |
| FR-06 | Associate detected candidates with catalogue stars | Synthetic blind matching demonstrated; real-image identity validation incomplete |
| FR-07 | Generate local astrometric solutions for image regions | Explored on five ASK033 image sections |
| FR-08 | Classify correspondence and local-solution quality | Strict / uncertain / suspect audit implemented |
| FR-09 | Estimate camera optical parameters | Constrained synthetic calibration demonstrated; real-image fit remains exploratory |
| FR-10 | Reconcile overlapping sections into one global calibration | Target requirement; independent validation remains open |
| FR-11 | Quantify residuals and uncertainty | Residual and cross-section analyses available; uncertainty model requires further work |
| FR-12 | Compare calibration over multiple observations | Future temporal validation |
| FR-13 | Publish versioned machine-readable calibration results | Research evidence outputs exist; deployable service/API not yet implemented |

## 4. Processing requirements

### 4.1 Catalogue processing
The system shall load a named catalogue version, validate required fields and record epoch handling. Any proper-motion propagation shall retain the reference epoch and target observation epoch.

### 4.2 Image processing
The system shall detect candidate stellar sources and estimate image coordinates. Detection quality, saturation, clipping, border effects and rejected candidates should be retained for diagnostics.

### 4.3 Association
The system shall associate image detections with predicted catalogue directions. Each correspondence shall retain the association method, residual and quality classification. A correspondence that agrees with a local WCS solution shall not automatically be treated as independently verified catalogue truth.

### 4.4 Local astrometry
The system shall support solving selected image regions and preserve each region's transform, fit statistics, input correspondences and solution quality.

### 4.5 Global calibration
The target system shall estimate a camera model consistent across overlapping image regions. The solver must expose rejected observations, section-dependent residuals and model limitations. Random point holdout and leave-one-section-out validation shall be reported separately.

### 4.6 Temporal analysis
The target system shall compare calibration results from multiple observations, distinguishing true camera-orientation changes from measurement noise and model instability.

## 5. Geometric model and conventions

The current synthetic baseline uses an equidistant fisheye relation:

    r = f × θ

where:
- r is radial pixel distance from the optical centre.
- f is focal scale in pixels.
- θ is incident ray angle in radians.

The constrained synthetic calibration estimates optical centre, focal scale, effective field of view and roll under a zenith-pointing assumption.

A production model must explicitly specify:
- Pixel origin and axis direction.
- Camera optical-axis convention.
- Celestial reference frame and epoch.
- Horizontal-coordinate conventions where applicable.
- Rotation order, handedness and transform direction.
- Angular units and time scale.
- Distortion model and valid field of view.

The current model is not a complete real-lens model and does not support unrestricted arbitrary camera pointing.

## 6. Target input and output contracts

### Input record — target

| Field | Description |
|---|---|
| image_id | Stable observation identifier |
| image_ref | Image bytes or immutable storage reference |
| observation_time | Timestamp and time-scale convention |
| site | Latitude, longitude, altitude and provenance |
| image_geometry | Width, height, pixel convention and orientation |
| camera_context | Camera/lens identifier and known parameters |
| pointing_prior | Optional orientation prior and uncertainty |
| catalogue_version | Reference catalogue identity/version |
| processing_config | Algorithm, model and configuration version |

### Calibration result — target

| Field | Description |
|---|---|
| calibration_id | Stable calibration identifier |
| source_observations | Image IDs and observation metadata |
| model | Projection and distortion model |
| parameters | Optical centre, scale, orientation and model coefficients |
| transforms | Explicit pixel-to-sky / sky-to-pixel conventions |
| correspondences | Accepted, uncertain and rejected associations |
| section_solutions | Local transforms and quality metrics |
| validation | Fit, random holdout, section holdout and independent-test metrics |
| uncertainty | Parameter and measurement uncertainty where estimated |
| provenance | Software, catalogue and configuration versions |
| warnings | Missing metadata, model limitations and quality flags |

These are target interface definitions, not a claim that a production API currently exists.

## 7. Non-functional requirements

- Reproducibility from immutable image inputs and versioned configuration.
- Traceability from each result to source observations and catalogue version.
- Explicit coordinate, unit and timestamp conventions.
- Robustness to sparse detections, false stars, clouds and image artefacts.
- Quality gates that prevent uncertain local solutions being silently accepted.
- Measured execution time and memory before any real-time claim.
- Automated regression tests and preserved failure cases.
- Bounded memory and deterministic behaviour for any future embedded port.

## 8. Embedded aerospace interface direction

The calibration engine may eventually publish a timestamped optical attitude observation with frame definition and quality/covariance metadata to a downstream estimator.

Camera-to-body extrinsic calibration, gyro propagation, IMU fusion and autonomous navigation are separate system functions. They require their own state definitions, sensor models, timing analysis and verification. StarLoc's current calibration prototype is not itself a complete star tracker or flight navigation system.

## 9. Verification strategy

Verification shall include:
1. Synthetic truth recovery.
2. Detection and centroid accuracy.
3. Catalogue association quality against independent references.
4. Local-section solution quality.
5. Global model consistency.
6. Leave-one-section-out and leave-one-image-out validation.
7. Temporal repeatability.
8. Environmental robustness.
9. Reproducibility and software regression.
10. Target performance and resource measurement when hardware is selected.
