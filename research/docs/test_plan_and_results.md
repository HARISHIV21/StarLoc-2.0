# StarLoc 2.0 — Verification Plan & Experimental Evidence
## Stellar Identification and Multi-Section Astrometric Calibration

## 1. Verification philosophy

StarLoc results are reported in distinct evidence classes:
- **Synthetic truth recovery:** observations are generated from known parameters.
- **Fit residual:** residuals on data used to estimate model parameters.
- **Random point holdout:** selected points from the same image/section population are withheld.
- **Leave-one-section-out:** an entire image region is withheld to assess spatial generalisation.
- **Independent real-image validation:** reference identities or calibration truth are established independently of the evaluated solution.
- **Temporal validation:** repeatability is evaluated across independent observations.

These classes are not interchangeable. A low synthetic or fit residual is not proof of real-camera accuracy.

## 2. Test environment

Documented research environment:
- macOS development platform.
- Python.
- NumPy and SciPy for numerical processing.
- OpenCV for image processing.
- Astropy for astronomical coordinate and catalogue operations.
- Matplotlib for diagnostic plots.
- Hipparcos-derived reference catalogue.
- Synthetic baseline image: 1024 × 1024 pixels.
- Synthetic projection: nominal 180-degree equidistant fisheye.

A pinned complete dependency lock and unified one-command setup remain reproducibility tasks.

## 3. Synthetic experimental evidence

### 3.1 Detection optimisation

Recorded experiment:
- Best threshold: 3.
- Connected-component area: 1–80 pixels.
- Detected regions: 101.
- Catalogue matches: 99 / 100.
- Mean matching error: 0.1745 px.
- Maximum matching error: 1.2257 px.

### 3.2 Initial optical calibration

- Matched stars: 99.
- Training stars: 79.
- Randomly held-out test stars: 20.
- Estimated optical centre: (511.9038, 512.0058) px.
- Focal scale: 318.2911 px.
- Estimated FOV: 180.0106°.
- Training RMSE: 0.2106 px.
- Held-out RMSE: 0.6926 px.

### 3.3 Blind synthetic catalogue calibration

- Detected image regions: 1,136.
- Catalogue candidates: 1,284.
- Identified stars: 1,136.
- Estimated optical centre: (511.501, 511.505) px.
- Focal scale: 318.313 px.
- Estimated FOV: 179.998°.
- Estimated roll: 36.999°.
- Mean reprojection residual: 0.1790 px.
- Reprojection RMSE: 0.2850 px.
- Maximum residual: 2.0206 px.

### 3.4 Synthetic robustness

| Scene | Roll error | Reprojection RMSE |
|---|---:|---:|
| Clean, 0° | 0.0017° | 0.5208 px |
| Noisy, 37° | 0.0037° | 0.5751 px |
| Degraded, 123° | 0.0088° | 0.7877 px |
| Stress, 271° | 0.0052° | 1.7174 px |

Mean roll error: 0.00485°. Mean reprojection RMSE: 0.90025 px. Total catalogue matches across the four scenes: 4,184.

### 3.5 Synthetic overlapping-section experiments

Four overlapping sections were fitted in each of four synthetic scenes, yielding 16 local fits. Reported parameter errors were below 0.1 px for optical-centre coordinates, below 0.11 px for focal scale and below 0.015° for roll. The highest reported section RMSE was 1.9027 px in the stress scene.

**Interpretation:** these experiments validate behaviour under the generated model and tested conditions. They do not establish performance on a physical lens.

## 4. Real ASK033 image investigation

Image dimensions: 1920 × 1440 pixels.

Five sections obtained local astrometric solutions: R1C2, R2C1, R2C2, R3C1 and R3C2.

The correspondence audit recorded:
- Total candidate correspondences: 233.
- Strict internal-consistency cases: 74.
- Uncertain cases: 155.
- Suspect associations: 4.

The term *strict* describes consistency with the corresponding local WCS solution. It is not independent confirmation of catalogue identity.

### 4.1 Random point holdout

Phase 56 used 74 strict correspondences, with 59 fitting points and 15 random held-out points. The held-out RMSE was 0.9381 px.

### 4.2 Leave-one-section-out validation

Phase 57 withheld complete image sections. Across 74 predictions:
- Aggregate median error: 1.047 px.
- Aggregate RMSE: 2.3247 px.
- Section RMSE range: 0.718–3.460 px.
- Weakest section: R3C1 at 3.460 px RMSE.
- R2C1 contained only four held-out points.

Phase 58 residual analysis identified section-dependent directional bias and outlier sensitivity, particularly in R2C2.

**Interpretation:** spatial generalisation is weaker than the random point holdout suggests. The real-image calibration remains exploratory and must not be described as independently validated.

## 5. Verification matrix

| ID | Verification objective | Current status | Required evidence |
|---|---|---|---|
| T-01 | Synthetic parameter recovery | Demonstrated | Regression on fixed synthetic truth datasets |
| T-02 | Star detection quality | Partial | Precision/recall against labelled real images |
| T-03 | Centroid accuracy | Synthetic experiments | Independent real-image centroid reference |
| T-04 | Catalogue identity | Incomplete | Independently verified correspondences |
| T-05 | Local astrometric solutions | Exploratory real-image study | Repeated solves across multiple images |
| T-06 | Global multi-section calibration | Not closed | One global model with independent validation |
| T-07 | Spatial generalisation | Tested; errors remain | Predefined acceptance criteria across held-out sections |
| T-08 | Temporal repeatability | Not established | Multi-time / multi-night validation |
| T-09 | Environmental robustness | Synthetic/partial | Real clouds, moonlight, light pollution and artefact tests |
| T-10 | Reproducible environment | Partial | Pinned dependencies and clean-environment run |
| T-11 | Server-side operational behaviour | Not implemented as deployable service | Service/API integration and operational tests |
| T-12 | Embedded execution | Not implemented | Target hardware, timing and memory evidence |

## 6. Required next verification campaign

1. Acquire multiple real images with traceable source, time and camera/site metadata.
2. Establish independent reference identities or astrometric solutions.
3. Freeze fitting and independent validation datasets before calibration.
4. Evaluate detection precision, recall and centroid error.
5. Reassess catalogue matching against independent truth.
6. Estimate a global model from overlapping sections.
7. Hold out complete sections and complete images.
8. Report residual distributions, angular error, uncertainty and failure cases.
9. Repeat across time and environmental conditions.
10. Define acceptance thresholds before evaluating final performance.

## 7. Reproducibility and result reporting checklist

Every reported experiment should record:
- Script and source revision.
- Input image/catalogue identifiers.
- Observation time, location and metadata provenance.
- Processing configuration and random seed.
- Camera model and coordinate conventions.
- Number of detections, candidates, accepted and rejected associations.
- Fitting and validation split method.
- Residual distribution and units.
- Output file paths and integrity hashes where available.
- Limitations and failure cases.

## 8. Final verification statement

The current evidence supports synthetic feasibility and an exploratory real-camera investigation. It does not yet support a claim of independently validated global AllSkyKamera calibration, deployable server-side operation, real-time embedded execution, flight qualification or completed camera/IMU fusion.
