# StarLoc 2.0 — Test Plan & Experimental Results

## 1. Verification approach

Keep the evidence classes separate:
- Synthetic truth recovery.
- Fit residuals.
- Random point holdout.
- Leave-one-section-out spatial validation.
- Independent real-image validation.

Synthetic results and WCS-derived real-image residuals are not independent real-camera accuracy.

## 2. Synthetic observations and results

### Catalogue-rendered blind calibration
- Image: 1024 × 1024; nominal 180° equidistant fisheye.
- 1,284 Hipparcos-derived stars rendered.
- 1,136 detected image regions and 1,136 identified stars.
- Estimated optical centre: (511.5005, 511.5046) px.
- Estimated focal scale: 318.3131 px.
- Estimated FOV: 179.9982°.
- Estimated roll: 36.9993°.
- Reprojection RMSE: 0.2850 px; maximum residual 2.0206 px.

### Robustness
Four generated scenes (clean, noisy, degraded and stress) reported mean roll error 0.00485° and mean reprojection RMSE 0.90025 px. The stress-scene RMSE was 1.7174 px.

These metrics are for synthetic observations only. Full dataset details are in synthetic_observation_validation.md.

## 3. ASK033 real-image evidence

- Original image: 1920 × 1440.
- Five sections with local astrometric solutions: R1C2, R2C1, R2C2, R3C1 and R3C2.
- Historical correspondence audit: 233 candidates; 74 strict internal-consistency, 155 uncertain and 4 suspect.
- Phase 38 global fit: 233 WCS-derived correspondences, 186 training and 47 held out; held-out RMSE 0.9863 px; training RMSE 3.9903 px and maximum training residual 30.02 px.
- Phase 56 strict-subset random holdout: 15 points, RMSE 0.9381 px.
- Phase 57 leave-one-section-out: 74 strict points across five folds; R3C1 held-out RMSE 3.4604 px, maximum 8.278 px.

The strict set is selected using local-WCS residuals. The WCS-derived correspondences are not independent proof of star identity. The real global fit is exploratory, and the spatial validation is not uniform.

## 4. Required validation still open

1. Resolve the ASK033 timestamp discrepancy and exposure-time convention.
2. Confirm the camera-site coordinates and approximate pointing.
3. Independently verify a subset of catalogue star identities.
4. Establish real-image detection and centroid metrics against labelled references.
5. Validate the RA/Dec-to-pixel coordinate convention and section offsets.
6. Validate one global optical model on independent correspondences and held-out image regions.

## 5. Reproducible entry point

Run the synthetic demonstration with:

    python research/16_run_final_demo.py

It does not reproduce the real-image Astrometry.net local solving. Those steps depend on the retained input image, local index/configuration files and external Astrometry.net tooling.
