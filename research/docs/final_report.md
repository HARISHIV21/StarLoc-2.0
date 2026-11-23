# StarLoc 2.0 — Research & Development Report
## Stellar Identification and Multi-Section Astrometric Calibration for All-Sky Camera Networks

## 1. Executive summary

StarLoc 2.0 investigates a software-defined approach to calibrating wide-field all-sky cameras from stellar observations. The motivating application is the AllSkyKamera Network, where camera orientation and geometric properties should be recovered from night-sky imagery rather than assumed from potentially inaccurate installation parameters.

The research pipeline combines astronomical catalogue preparation, image-based star detection, sub-pixel centroid estimation, catalogue association, local astrometric analysis and fisheye camera-model estimation. A major research direction is to reconcile solutions from overlapping image regions into a consistent full-image calibration.

The work has progressed through controlled synthetic experiments and an exploratory real-image investigation using a public ASK033 AllSkyKamera image. Synthetic experiments demonstrate the feasibility of the constrained processing chain. The real-image study exposes correspondence uncertainty and section-dependent residuals, identifying the remaining scientific work needed before a global calibration can be considered validated.

## 2. Problem statement and application context

An all-sky camera provides a wide angular field of view but its pixel-to-sky mapping depends on optical geometry and camera orientation. If these parameters are inaccurate, downstream measurements of sky position and observed trajectories may also be inaccurate.

The R&D problem is to estimate the camera's optical and orientation parameters from stars whose celestial positions can be predicted from a reference catalogue and observation metadata.

The system must address:
- Reliable extraction of star image coordinates.
- Catalogue identification using celestial reference data.
- Observation epoch and observer-location dependence.
- Optical projection and lens distortion.
- Local solutions in overlapping image sections.
- Consistency and fusion of local solutions into a global camera model.
- Residuals, uncertainty and quality control.
- Temporal changes in camera orientation.

## 3. Objectives

1. Build a reproducible synthetic environment with known camera geometry.
2. Develop stellar candidate detection and centroid estimation.
3. Prepare Hipparcos-derived reference data and epoch-dependent sky positions.
4. Investigate blind catalogue-to-image matching.
5. Estimate optical parameters using geometric optimisation.
6. Test robustness under noise, missing detections and false detections.
7. Investigate real ASK033 image sections using local astrometric solutions.
8. Audit correspondence quality and cross-section consistency.
9. Define the route to a robust global calibration and temporal orientation analysis.

## 4. Processing methodology

### 4.1 Catalogue preparation
The research workflow processes Hipparcos-derived stellar data, validates catalogue fields and propagates positions to the selected observation epoch.

### 4.2 Sky-coordinate transformation
Celestial coordinates are related to local horizontal directions using observation time and an observer location. The temporary Rouen test location used in synthetic work is not a confirmed AllSkyKamera installation location.

### 4.3 Synthetic camera observation
A nominal 180-degree equidistant fisheye model is used to render controlled observations with known parameters. This provides ground truth for initial algorithm development.

### 4.4 Stellar image processing
The prototype performs image thresholding, connected-component candidate extraction and intensity-weighted centroid estimation. Detection settings are investigated under varying image conditions.

### 4.5 Catalogue correspondence
Detected image locations are compared with predicted catalogue-star projections. The synthetic workflow supports blind identification under its stated pointing and projection assumptions.

### 4.6 Optical calibration
The baseline equidistant model uses r = f × θ. The constrained synthetic calibration estimates optical centre, focal scale, effective field of view and roll.

### 4.7 Multi-section real-image investigation
A public ASK033 image was divided into overlapping regions. Local astrometric solutions and their cross-section correspondences were examined. The research retained strict, uncertain and suspect association classes rather than treating all matches as equally reliable.

## 5. Experimental results

### 5.1 Synthetic blind calibration

The documented blind experiment reports:
- 1,136 detected image regions.
- 1,284 catalogue candidates.
- 1,136 identified stars.
- Estimated field of view: 179.998 degrees.
- Estimated roll: 36.999 degrees.
- Reprojection RMSE: 0.2850 pixels.

These results are specific to the generated image and constrained camera model.

### 5.2 Synthetic robustness

Four scenes—clean, noisy, degraded and stress—reported a mean roll error of 0.00485 degrees and a mean reprojection RMSE of 0.90025 pixels. The stress scene reached 1.7174 pixels RMSE.

### 5.3 ASK033 real-image study

The investigation used a 1920 × 1440 public ASK033 image. Five image sections obtained local astrometric solutions.

The association audit reported 233 candidate correspondences:
- 74 strict internal-consistency cases.
- 155 uncertain cases.
- 4 suspect associations.

Phase 56 fitted a model using the strict subset and reported 0.9381 pixels RMSE on 15 randomly held-out points. Phase 57 evaluated leave-one-section-out generalisation and reported 2.3247 pixels aggregate RMSE, with R3C1 reaching 3.460 pixels.

These metrics measure different validation conditions. The random holdout result must not be presented as equivalent to independent spatial generalisation. The strict class denotes local-WCS consistency, not independent proof of catalogue identity.

## 6. Discussion

The synthetic experiments show that the implemented stages can recover the parameters of a constrained fisheye camera model under controlled conditions. They provide useful algorithm-development evidence and a repeatable starting point.

The real-image investigation is an important step beyond simulation. It demonstrates the practical complexity of section-based astrometric calibration: local solutions do not automatically combine into a consistent global model, and association uncertainty can dominate downstream fitting.

The leave-one-section-out result indicates that spatial generalisation remains a key weakness. The current evidence therefore supports describing the real-image calibration as exploratory rather than validated.

## 7. Current limitations

- Real-image evidence is based on a limited public-image investigation.
- Independent catalogue identity validation is incomplete.
- Local WCS consistency is not independent ground truth.
- The equidistant fisheye model is a baseline and does not fully represent real lens behaviour.
- The synthetic blind solution assumes a constrained zenith-pointed camera with unknown roll.
- A robust global multi-section calibration has not yet been independently validated.
- Temporal orientation estimation over a sequence remains to be established.
- A deployable server-side service is not yet implemented.
- Embedded C++ implementation, hardware benchmarking and camera/IMU fusion are future work.

## 8. Next research and engineering work

### Priority 1 — Complete real-camera calibration
Obtain a multi-image dataset with verified timestamps and site metadata, independently verify star identities, and validate a global model using complete held-out sections and images.

### Priority 2 — Global and temporal estimation
Develop a robust method for reconciling overlapping local solutions and analyse orientation repeatability across observations.

### Priority 3 — Software architecture
Separate detection, centroiding, catalogue transformation, matching, local solving, global calibration and result publication into documented modules with explicit coordinate and timing conventions.

### Priority 4 — Embedded port
After numerical behaviour is stable, port selected components to C++, compare against the Python reference and benchmark on a selected target.

### Priority 5 — Aerospace/autonomous integration
Define a timestamped camera attitude-measurement interface and investigate camera/IMU fusion as a separate estimator with its own verification evidence.

## 9. Conclusion

StarLoc 2.0 has developed a substantial research workflow for stellar detection, catalogue association and constrained fisheye calibration, and has extended the investigation to real ASK033 imagery and cross-section astrometric consistency.

The next decisive milestone is not simply more star detection. It is an independently validated global calibration across multiple real images, followed by temporal analysis and a modular implementation suitable for future embedded deployment.

The project therefore provides a credible research foundation at the intersection of optical calibration, stellar vision, embedded sensing and aerospace/autonomous system development, while keeping current experimental evidence distinct from future system capabilities.
