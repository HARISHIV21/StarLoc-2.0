# StarLoc 2.0 — Phase 62
## Integrated Star Tracker Demonstration

Generated: 2026-11-20T21:56:02Z

### 1. Project objective
Demonstrate a software-defined workflow for detecting stars, associating detections
with a stellar catalogue, estimating image-to-sky geometry and evaluating calibration.

### 2. Synthetic pipeline
- Star detection: 99 / 100 simulated stars.
- Mean centroid error: 0.1745 px.
- Blind catalogue matching: 1,136 / 1,284 catalogue-rendered stars.
- Recovered FOV: 179.9982°.
- Recovered roll: 36.99925°.
- Blind calibration RMSE: 0.285 px.

These are controlled synthetic results, not real-camera accuracy claims.

### 3. Real-camera experiment — ASK033
- Input image: 1920 × 1440 px.
- Image subdivision: 3 × 3 sections.
- Sections with plate solutions: R1C2, R2C1, R2C2, R3C1 and R3C2.
- Cross-section correspondences: 233.

### 4. Association audit
| Classification | Count |
|---|---:|
| Strict internal consistency | 74 |
| Uncertain | 155 |
| Suspect associations | 4 |
| **Total** | **233** |

The strict category indicates agreement with the corresponding local WCS solution.
It does not independently prove the Hipparcos identity of a detected source.

### 5. Global fisheye calibration experiments
**Phase 38 exploratory model**
- Optical centre: (940.8793, 755.5388) px
- Focal scale: 822.9709 px/rad
- Radial coefficients: k1 = -0.03333727, k2 = 0.00089815
- Held-out RMSE: 0.9863 px

**Phase 56 strict-subset model**
- Optical centre: (941.0884, 755.9871) px
- Focal scale: 823.0072 px/rad
- Radial coefficients: k1 = -0.03258449, k2 = -0.00120724
- Training / held-out points: 59 / 15
- Held-out RMSE: 0.9381 px

These models are exploratory because the correspondences originate from section WCS
solutions and are not independently certified astrometric ground truth.

### 6. Cross-section generalisation
Leave-one-section-out validation on 74 strict-subset correspondences:
- Median error: 1.0468 px
- Mean error: 1.5935 px
- RMSE: 2.3247 px
- 90th percentile: 3.2666 px
- Maximum: 8.2780 px

R3C1 was the weakest held-out section (RMSE 3.460 px), indicating section-dependent
systematic errors or association problems that need further investigation.

### 7. Scientific limitations
- The real-camera section WCS solutions are not independent ground truth.
- The 74 strict points indicate internal consistency with local WCS solutions, not confirmed catalogue identities.
- The 155 uncertain correspondences remain unresolved.
- Four catalogue associations remain separately flagged as suspect.
- Leave-one-section-out performance varies by section; R3C1 is notably weaker.
- The global fisheye estimates are exploratory and require independent astrometric validation.
- Image timestamp and camera pointing metadata require confirmation.
- The synthetic demonstration assumes a controlled zenith-pointed fisheye geometry and does not prove general real-camera performance.

### 8. Demonstration assets
- Real-camera association overlay — Phase 61: `research/real_image/results/ASK033/phase61_final_association_visualisation/phase61_real_star_association_overlay.jpg`
- Global calibration residual map — Phase 38: `research/real_image/results/ASK033/phase38_global_calibration/phase38_residual_map.png`
- Section residual vectors — Phase 58: `research/real_image/results/ASK033/phase58_section_error_diagnostics/phase58_spatial_residual_vectors.png`
- Section error distribution — Phase 58: `research/real_image/results/ASK033/phase58_section_error_diagnostics/phase58_section_error_distribution.png`
- Four-point investigation — Phase 52: `research/real_image/results/ASK033/phase52_global_prediction_test/phase52_four_point_montage.jpg`
- WCS validation overlay — Phase 35: `research/real_image/results/ASK033/phase35_wcs_match_overlay.jpg`

### 9. Reproducibility and integrity
This phase indexes existing reports and evidence. It does not rerun earlier phases,
refit calibration parameters, or alter prior experimental outputs.

Machine-readable report: `research/real_image/results/ASK033/phase62_integrated_demo/phase62_integrated_demo_report.json`
