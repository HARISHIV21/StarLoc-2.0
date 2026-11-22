# Test Plan and Results — StarLoc 2.0

## 1. Test objectives

Validate the principal stages of the star detection, catalogue identification and fisheye optical calibration pipeline.

## 2. Test environment

- Operating system: macOS
- Language: Python
- Image processing: OpenCV
- Numerical processing: NumPy and SciPy
- Astronomy: Astropy
- Reference catalogue: Hipparcos
- Synthetic image: 1024 × 1024 pixels
- Projection: Equidistant fisheye, nominal 180-degree field of view

## 3. Recorded results

### Star detection optimisation

- Best threshold: 3
- Minimum component area: 1 pixel
- Maximum component area: 80 pixels
- Detected regions: 101
- Catalogue matches: 99 / 100
- Mean matching error: 0.1745 pixels
- Maximum matching error: 1.2257 pixels

### Initial optical calibration

- Matched stars: 99
- Training stars: 79
- Independent test stars: 20
- Estimated optical centre: (511.9038, 512.0058) pixels
- Focal scale: 318.2911 pixels
- Estimated field of view: 180.0106 degrees
- Training RMSE: 0.2106 pixels
- Independent test RMSE: 0.6926 pixels

### Blind catalogue calibration

- Detected image regions: 1,136
- Catalogue candidates: 1,284
- Identified stars: 1,136
- Estimated optical centre: (511.501, 511.505) pixels
- Focal scale: 318.313 pixels
- Estimated field of view: 179.998 degrees
- Estimated roll: 36.999 degrees
- Mean reprojection residual: 0.1790 pixels
- Reprojection RMSE: 0.2850 pixels
- Maximum residual: 2.0206 pixels

### Robustness tests

| Scene | Roll error | Reprojection RMSE |
|---|---:|---:|
| Clean, 0° | 0.0017° | 0.5208 px |
| Noisy, 37° | 0.0037° | 0.5751 px |
| Degraded, 123° | 0.0088° | 0.7877 px |
| Stress, 271° | 0.0052° | 1.7174 px |

Mean roll error: 0.00485 degrees.

Mean reprojection RMSE: 0.90025 pixels.

Total catalogue matches across the four scenes: 4,184.

### Overlapping-section tests

Four overlapping sections were fitted in each of the four scenes, giving 16 local section fits.

Reported local parameter errors:
- Optical-centre coordinate errors below 0.1 pixels.
- Focal-scale errors below 0.11 pixels.
- Roll errors below 0.015 degrees.

The highest reported section RMSE was 1.9027 pixels in the stress scene.

## 4. Interpretation

The experiments demonstrate that the synthetic pipeline can identify catalogue stars and estimate optical parameters under the tested assumptions.

The stress scene produces higher residuals, showing that degraded image quality affects positional accuracy even when the estimated roll remains close to the simulated value.

The local section results demonstrate promising consistency in the synthetic model. They do not yet validate real-lens distortion or a combined global solution from a real 180-degree camera image.

## 5. Outstanding tests

- Real AllSkyKamera image validation.
- Arbitrary camera pointing.
- Camera-centre and focal-scale variation across independent generated scenes.
- Real optical distortion.
- Cloud, moonlight and light-pollution rejection.
- Global combination of section-level calibration solutions.
- Repeatability across multiple real observations.


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

## Additional real-camera audit and integration tests — Phases 60–62

### Phase 60 — Association audit
- Total correspondences: 233.
- Strict internal consistency: 74.
- Uncertain: 155.
- Suspect associations: 4.
- Acceptance interpretation: local-WCS consistency is not independent proof
  of catalogue identity.

### Phase 61 — Classification visualisation
Generated a full-image association overlay and classified correspondence CSV.
The classification preserves the distinction between strict, uncertain and
suspect associations.

### Phase 62 — Integrated demonstration
Generated machine-readable JSON, Markdown and HTML outputs. The demonstration
indexes prior results without rerunning experiments or changing calibration.

### Generalisation qualification
Phase 57 leave-one-section-out RMSE was 2.3247 px overall. R3C1 reached
3.460 px RMSE. The real-camera calibration must therefore remain labelled
exploratory pending independent astrometric validation.
