# Feasibility & Engineering Assessment — StarLoc 2.0

## 1. Objective

Assess the feasibility of recovering optical geometry and orientation of wide-field all-sky cameras from stellar observations, with the AllSkyKamera Network as the primary R&D application.

## 2. Technical approach

The intended processing chain is:
1. Load a night-sky image and acquisition metadata.
2. Prepare a reference stellar catalogue at the observation epoch.
3. Detect stellar candidates and estimate sub-pixel centroids.
4. Associate image detections with catalogue objects.
5. Obtain local astrometric solutions over image regions.
6. Audit correspondence and section quality.
7. Estimate a globally consistent camera model.
8. Publish calibration parameters with residuals, uncertainty and provenance.
9. Compare calibration across observations to evaluate repeatability and orientation changes.

The current research prototype implements selected stages and has investigated the real-image problem. A complete deployable server-side service is not yet implemented.

## 3. Demonstrated feasibility

### Synthetic research
- Processing of 8,870 valid Hipparcos catalogue entries is recorded in the feasibility evidence.
- Catalogue positions are propagated to a selected epoch.
- A visible-sky catalogue is generated for a temporary Rouen test location.
- Catalogue stars are rendered into a synthetic 180-degree equidistant fisheye image.
- Blind synthetic calibration recovered approximately 180-degree field of view and 37-degree roll.
- The documented blind experiment reported 0.2850 px reprojection RMSE.
- Four robustness scenes reported a mean RMSE of 0.90025 px.
- Four overlapping sections were fitted in each of four synthetic cases.

### Real-image investigation
A public 1920 × 1440 ASK033 image was analysed using local astrometric solutions across five sections. The correspondence audit recorded 233 candidates, of which 74 were strict internal-consistency cases, 155 uncertain and four suspect.

The Phase 57 leave-one-section-out result reported 2.3247 px aggregate RMSE, with R3C1 at 3.460 px. This exposes spatial generalisation limitations and prevents the real-image experiment from being described as a completed independent validation.

## 4. Feasibility by engineering stage

| Stage | Feasibility assessment | Main dependency |
|---|---|---|
| Synthetic stellar detection and calibration | Demonstrated under stated assumptions | Existing research pipeline |
| Real-image local astrometry | Explored | Real image and metadata |
| Independent catalogue identity verification | Not yet established | Independent reference observations |
| Global multi-section calibration | Technically plausible; not yet validated | Reliable correspondences and robust solver |
| Temporal orientation analysis | Feasible as next research stage | Multi-time image dataset |
| Server-side operational service | Feasible after architecture definition | Stable inputs, outputs and deployment environment |
| C++/embedded implementation | Feasible after algorithm stabilisation | Numerical contracts and target resource budget |
| Camera/IMU fusion | Separate feasible research workstream | Validated optical attitude measurement and inertial model |

## 5. Main technical risks

- Incorrect or uncertain observation time and site metadata.
- False catalogue associations and ambiguous star patterns.
- Clouds, light pollution, moonlight, saturation and reflections.
- Lens distortion and departure from the equidistant model.
- Section-dependent bias and insufficient overlap.
- Overfitting to one image or one camera configuration.
- Lack of independent reference truth.
- Non-reproducible historical script dependencies.
- Embedded resource and timing constraints not yet measured.

## 6. Resource requirements

Current simulation and research work can be performed with a standard development computer and Python scientific libraries. A physical camera is not required for synthetic development, but real-image validation requires representative observations and trustworthy acquisition metadata.

Embedded feasibility cannot be concluded until the target image dimensions, update rate, latency budget, memory limit and compute platform are specified.

## 7. Feasibility conclusion

The synthetic processing chain is demonstrated under controlled conditions. A real ASK033 image investigation has been carried out, including local astrometric analysis and correspondence-quality auditing. However, independent real-camera global calibration remains an open research milestone.

The technically strongest next step is to establish a multi-image dataset with independent reference information and complete-section validation. Once the optical model is stable, modularisation, server-side operationalisation and an embedded C++ port become well-founded engineering stages.
