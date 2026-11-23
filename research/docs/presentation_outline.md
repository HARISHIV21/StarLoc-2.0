# StarLoc 2.0 — Technical Review Presentation
## Stellar Identification and Multi-Section Astrometric Calibration for All-Sky Camera Networks

### Slide 1 — Research title and engineering objective
- StarLoc 2.0.
- Server-side optical calibration from stellar observations.
- AllSkyKamera Network as the primary R&D application.
- Relevance to optical attitude sensing and embedded aerospace.

### Slide 2 — The calibration problem
- Wide-field camera geometry and orientation may be inaccurate or drift.
- Pixel-to-celestial transformations depend on camera model and pointing.
- Need to estimate geometry from stars rather than trust installation parameters.
- Local image-region solutions must be reconciled into one global model.

### Slide 3 — System requirements and outputs
- Inputs: image, observation time, observer location, camera context and reference catalogue.
- Outputs: star detections, catalogue associations, local solutions, global camera parameters, residuals and quality metadata.
- Downstream relevance: sky-coordinate measurement and trajectory analysis.

### Slide 4 — End-to-end processing architecture
Show:
Image/metadata → detection → centroiding → catalogue preparation → association → local astrometry → cross-section audit → global calibration → quality-controlled output.

### Slide 5 — Catalogue and coordinate processing
- Hipparcos-derived reference data.
- Epoch propagation.
- Equatorial and local horizontal coordinate transformations.
- Time and observer-location dependence.
- State assumptions and metadata provenance.

### Slide 6 — Stellar detection and centroid estimation
- Detection pipeline and connected-component processing.
- Intensity-weighted centroid.
- Detection parameter optimisation.
- Demonstrate representative detections and failure modes.

### Slide 7 — Synthetic camera model and blind calibration
- Equidistant fisheye projection.
- Optical centre, focal scale, field of view and roll.
- 1,136 identified stars.
- 179.998° estimated FOV, 36.999° roll and 0.2850 px RMSE.
- Explicitly label results synthetic and constrained.

### Slide 8 — Robustness and performance experiments
- Clean, noisy, degraded and stress scenes.
- Mean roll error 0.00485°.
- Mean reprojection RMSE 0.90025 px.
- Stress scene RMSE 1.7174 px.
- Discuss sensitivity to observation quality.

### Slide 9 — Transition to real ASK033 imagery
- Public 1920 × 1440 image.
- Five image sections with local astrometric solutions.
- Explain section overlap and the reason for local solves.
- Distinguish synthetic and real-image evidence.

### Slide 10 — Correspondence audit
- 233 candidate correspondences.
- 74 strict internal-consistency, 155 uncertain, 4 suspect.
- Strict means local-WCS consistency, not independent identity proof.
- Show classified overlay and representative residuals.

### Slide 11 — Global calibration and generalisation challenge
- Phase 56 random holdout: 15 points, 0.9381 px RMSE.
- Phase 57 leave-one-section-out: 2.3247 px aggregate RMSE.
- R3C1: 3.460 px RMSE.
- Explain why complete-section validation is more demanding.
- State that global real-camera calibration remains exploratory.

### Slide 12 — Engineering architecture and quality strategy
- Provenance, coordinate frames, timestamp conventions.
- Separation of local and global solutions.
- Uncertainty, outlier handling and failure states.
- Reproducible datasets, configuration and regression tests.

### Slide 13 — Embedded aerospace development pathway
- Stabilise and independently validate the global calibration.
- Modularise the Python reference pipeline.
- Port selected modules to C++.
- Benchmark target latency and memory.
- Define camera-to-body and timestamped measurement interface.
- Investigate camera/IMU fusion as a separate estimator.

### Slide 14 — Conclusions and next milestones
- Synthetic algorithmic feasibility demonstrated.
- Real-image investigation and correspondence audit completed at exploratory level.
- Main open research problem: independently validated global multi-section and temporal calibration.
- Roadmap from AllSkyKamera R&D to embedded optical sensing and autonomous aerospace applications.
