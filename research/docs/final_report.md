# StarLoc 2.0 — Final Research Report

## Software-Defined Optical Calibration of an All-Sky Camera Using Stellar Identification

## 1. Introduction

The objective of StarLoc 2.0 is to investigate automatic optical calibration of an all-sky camera using stars observed in night-sky images. The project is motivated by the AllSkyKamera Network requirement to determine camera orientation and geometric properties without depending entirely on potentially inaccurate camera configuration.

## 2. Methodology

The developed workflow consists of:
1. Preparation of a Hipparcos reference catalogue.
2. Propagation of stellar positions to the selected observation date.
3. Transformation into local horizontal coordinates.
4. Generation of synthetic equidistant fisheye observations.
5. Detection of stellar image regions and centroid estimation.
6. Blind catalogue identification.
7. Estimation of optical parameters.
8. Robustness testing under noise and missing or false detections.
9. Local calibration using overlapping image sections.

## 3. Implementation

The prototype uses Python, NumPy, SciPy, OpenCV, Astropy and Matplotlib.

The synthetic image is 1024 × 1024 pixels with a nominal 180-degree equidistant fisheye projection.

## 4. Results

The blind calibration experiment identified 1,136 image regions against 1,284 catalogue candidates. It estimated a 179.998-degree field of view and 36.999-degree roll, with a reprojection RMSE of 0.2850 pixels.

Four robustness scenes produced a mean roll error of 0.00485 degrees and a mean reprojection RMSE of 0.90025 pixels.

Four overlapping sections were fitted in each scene. Their local optical-centre, focal-scale and roll estimates were consistent with the simulated camera parameters.

## 5. Discussion

The results show that the main algorithmic stages are feasible under controlled synthetic conditions. The use of a real stellar catalogue makes the synthetic sky geometrically meaningful, while the rendering and noise model allow repeatable tests.

However, the synthetic images are generated from a known camera model. The current calibration also assumes zenith pointing with unknown roll. Therefore, the reported accuracy must not be interpreted as real-camera accuracy.

## 6. Limitations

- No actual AllSkyKamera exposure has yet been calibrated.
- The current camera model is equidistant and does not fully represent real-lens distortions.
- The present blind calibration assumes approximate pointing at the zenith.
- Unknown observer location is not solved.
- The global combination of section-level solutions requires further development.
- IMU coupling is outside the completed primary pipeline.

## 7. Future work

The next steps are:
1. Obtain a real AllSkyKamera image and its timestamp.
2. Confirm approximate geographic location and camera pointing.
3. Run star detection and catalogue matching on the real image.
4. Inspect residuals and identify optical-model mismatch.
5. Extend the model to include additional distortion parameters if required.
6. Combine overlapping section solutions into one global calibration.
7. Evaluate repeatability on multiple observations.

## 8. Conclusion

StarLoc 2.0 has established a software prototype for catalogue-based stellar identification and synthetic all-sky fisheye optical calibration. The blind calibration and robustness experiments provide encouraging results under controlled assumptions.

The project has not yet demonstrated calibration of a real AllSkyKamera exposure. That validation is the principal remaining experimental step.


<!-- STARLOC_PHASE59_FINAL_VALIDATION -->
## Final real-camera validation update — Phases 38–59

### Real-image experiment

The project was extended to a public ASK033 AllSkyKamera image with dimensions
1920 × 1440 pixels. Five image sections obtained local astrometric solutions:
R1C2, R2C1, R2C2, R3C1 and R3C2.

The Phase 37 validation produced 233 provisional catalogue-to-image
correspondences. A stricter local-WCS residual filter selected 74 points
for the Phase 56 calibration experiment.

### Global fisheye calibration

The Phase 38 exploratory equidistant fisheye model used radial coefficients
k1 and k2. Its random held-out subset contained 47 points, with median
residual 0.608 px and RMSE 0.986 px.

Phase 56 fitted the same model using 74 strict correspondences. Its
15-point random held-out subset had median residual 0.797 px and RMSE
0.938 px. The optical centre and focal scale remained close to the
Phase 38 estimates. This does not establish a clear accuracy improvement.

### Cross-section validation

Phase 57 withheld each complete image section in turn. Across 74
predictions, the aggregate median error was 1.047 px and RMSE was
2.325 px. Section-level RMSE ranged from 0.718 px to 3.460 px.
R3C1 was the weakest section, with RMSE 3.460 px and maximum error
8.278 px. R2C1 had only four held-out points.

Phase 58 examined residual vectors and distributions. It identified
section-dependent directional biases and outlier sensitivity, especially
in R2C2. No further correction was accepted without independent evidence.

### Final interpretation and limitations

The synthetic calibration experiments demonstrate the feasibility of
the image-processing and geometric-calibration pipeline under controlled
conditions. The public real-camera experiment demonstrates that local
astrometric plate solving and an exploratory global fisheye fit can be
performed across multiple image sections.

However, the real-camera result is not a fully validated production
calibration. The correspondences inherit uncertainty from local WCS
solutions, only one public image was investigated, and the four suspect
R2C2 associations remain unresolved. Independent multi-frame or
independently verified astrometric validation is required.

The Phase 38 and Phase 56 models are retained as separate experimental
results. Neither is silently substituted for the other.

<!-- STARLOC_PHASE60_62_FINAL_UPDATE -->

## Final association audit and integrated demonstration — Phases 60–62

### Association quality audit
The ASK033 experiment contains 233 cross-section correspondences:
74 strict internal-consistency cases, 155 uncertain cases and four separately
flagged suspect associations. Strict internal consistency means agreement with
the corresponding local WCS solution; it does not independently certify a
Hipparcos catalogue identity.

### Calibration and generalisation
The Phase 56 strict-subset model used 59 training and 15 held-out points and
reported a held-out RMSE of 0.9381 px. Phase 57 leave-one-section-out validation
reported an aggregate RMSE of 2.3247 px. R3C1 was the weakest held-out section
at 3.460 px RMSE. These results indicate section-dependent errors and limit
claims of general real-camera calibration accuracy.

### Integrated demonstration
Phase 61 generated the classified association overlay and CSV. Phase 62
integrated the synthetic results, real-camera reports, calibration experiments,
validation evidence and scientific limitations into JSON, Markdown and HTML
demonstration outputs. These integration steps did not refit calibration
parameters or rerun previous experiments.

The real-camera global fisheye estimates remain exploratory because the
section WCS correspondences are not independent astrometric ground truth.
Image timestamp and camera pointing metadata also require confirmation.
