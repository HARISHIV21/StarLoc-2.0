# StarLoc 2.0 — System Architecture & Interface Definition

## 1. System purpose

StarLoc 2.0 investigates a server-side calibration pipeline for the AllSkyKamera Network. Given a night-sky image and observation metadata, the intended system estimates camera geometry and orientation from stellar observations, reconciles solutions across overlapping image regions and produces a traceable pixel-to-celestial calibration.

The architecture also defines how the research core could later be separated into portable algorithm modules for embedded optical sensing and aerospace/autonomous applications.

## 2. System boundary

### Current research implementation
- Python research scripts for catalogue preparation, synthetic image generation, stellar detection, centroiding, matching and optical calibration.
- Synthetic datasets with known camera parameters.
- Public ASK033 real-image investigation using local astrometric solutions.
- Cross-section correspondence classification, residual analysis and integrated evidence outputs.

### Target system capabilities still to be completed
- Robust global multi-section calibration on independently validated real observations.
- Temporal camera-orientation estimation from image sequences.
- A deployable server-side service and stable calibration-result interface.
- C++/embedded implementation and target performance evidence.
- Camera/IMU fusion for a downstream attitude-estimation application.

## 3. Logical architecture

```text
[Image + Observation Metadata]
             |
             v
[Input Validation / Provenance]
             |
             v
[Image Pre-processing]
             |
             v
[Star Detection] -> [Centroid + Quality]
             |                 |
             +--------+--------+
                      v
             [Catalogue Preparation]
             [Epoch / Sky Coordinates]
                      |
                      v
             [Star Correspondence]
                      |
                      v
          [Per-Section Astrometric Solve]
                      |
                      v
        [Association and Residual Quality Audit]
                      |
                      v
         [Global Multi-Section Calibration]
                      |
                      v
          [Temporal / Repeatability Analysis]
                      |
                      v
           [Calibration Result + Diagnostics]
                      |
                      v
             [Server-side Consumer]
                      |
              future adapter boundary
                      v
          [Embedded / Autonomy Consumer]
```

The diagram describes the target architecture. The current implementation covers selected components and experimental flows; it is not yet a single operational service implementing every block.

## 4. Functional modules

| Module | Responsibility | Current status |
|---|---|---|
| Observation metadata | Timestamp, site, image dimensions and camera context | Inputs documented; real-image metadata needs independent confirmation |
| Catalogue service | Load catalogue, validate fields and propagate epoch-dependent positions | Research scripts implemented |
| Image processing | Preprocess, detect stellar candidates and estimate centroids | Implemented experimentally |
| Association engine | Link detected stars to catalogue objects | Synthetic matching implemented; real-image associations require independent validation |
| Local astrometric solver | Obtain local image-to-sky solutions | Investigated using cropped ASK033 sections / WCS |
| Correspondence auditor | Classify strict, uncertain and suspect associations | Implemented in research evidence workflow |
| Global calibration solver | Reconcile local solutions into a full-image camera model | Exploratory; not yet independently validated |
| Temporal estimator | Track orientation/calibration behaviour across observations | Future development |
| Result publisher | Produce versioned calibration, quality metrics and diagnostics | Evidence outputs exist; deployable service/API remains future work |
| Embedded adapter | Consume bounded calibration/measurement outputs | Future development |

## 5. Input contract — target

A production calibration run should identify its input explicitly:

| Field | Meaning |
|---|---|
| image_id | Stable identifier for the image |
| image | Image bytes or immutable object reference |
| observation_time | Timestamp with explicit time scale and timezone/UTC convention |
| observer_location | Latitude, longitude and altitude, with source/uncertainty |
| image_geometry | Width, height, orientation and pixel convention |
| camera_metadata | Camera/lens identifier and any known optical information |
| initial_pointing | Optional prior orientation and uncertainty |
| catalogue_version | Reference catalogue and version |
| processing_config | Algorithm/model version and calibration settings |

The exact production schema is not yet implemented. Missing or uncertain metadata must be represented explicitly rather than silently replaced with assumed values.

## 6. Calibration result contract — target

A calibration result should include:
- Calibration identifier and source image identifiers.
- Observation time and site metadata used.
- Camera model name and parameter vector.
- Pixel-to-celestial and celestial-to-pixel transform conventions.
- Local section solutions and their quality classifications.
- Number of accepted, uncertain and rejected correspondences.
- Residual distribution and validation method.
- Uncertainty or confidence information.
- Software version, catalogue version and processing configuration.
- Warnings and known limitations.

A result must distinguish fitting residuals, random held-out residuals, leave-one-section-out residuals and independent external validation. These metrics are not interchangeable.

## 7. Coordinate and timing conventions to formalise

Before integration, the implementation must explicitly define:
- Pixel origin, axis directions and pixel-centre convention.
- Celestial reference frame and equinox/epoch.
- Horizontal frame conventions where altitude/azimuth are used.
- Camera frame and optical-axis direction.
- Camera-to-world and world-to-camera rotation direction.
- Angle units and handedness.
- Timestamp source, time scale and conversion rules.
- Camera-to-body extrinsic transform for any future aerospace integration.

## 8. Non-functional requirements for the target system

- Reproducible results from immutable inputs and versioned configuration.
- Traceable catalogue and observation metadata.
- Robust handling of sparse, cloudy, noisy and contaminated images.
- Explicit quality gates for uncertain or inconsistent local solutions.
- Bounded resource use for any embedded implementation.
- Measured execution time and memory on the selected target.
- Regression tests for algorithm changes.
- Clear failure states; no silent fallback to unverified calibration.

## 9. Aerospace and autonomous integration boundary

The calibration engine should publish a geometrically defined, timestamped optical measurement with quality information. A downstream attitude estimator may consume this measurement alongside inertial propagation, but the estimator is a separate subsystem with its own state definition, noise model, observability analysis and verification plan.

This separation avoids treating camera calibration as equivalent to a complete star tracker or autonomous navigation system.
