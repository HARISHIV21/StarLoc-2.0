# StarLoc 2.0
## Software-Defined All-Sky Camera Calibration Using Stellar Identification

### Objective
Detect stars in all-sky fisheye images, identify them using an astronomical catalogue, associate celestial coordinates with image pixels, and estimate optical calibration parameters.

### Implemented workflow
- Synthetic 180-degree equidistant fisheye image generation.
- Star detection and centroid extraction.
- Hipparcos catalogue processing.
- Proper-motion propagation to the observation epoch.
- Visible-sky catalogue generation.
- Blind catalogue matching and optical calibration.
- Robustness testing under simulated image degradation.
- Four-section synthetic image analysis.

### Main demonstration
Run: python research/16_run_final_demo.py

### Main synthetic results
- Detected regions: 1,136
- Identified stars: 1,136
- Estimated FOV: 179.998 degrees
- Estimated roll: 36.999 degrees
- Reprojection RMSE: 0.285 pixels

### Validation limitation
These results are from synthetic observations generated using real astronomical catalogue data. They are not real AllSkyKamera measurements. The current model assumes a zenith-pointed equidistant fisheye camera with unknown roll. Validation using a real camera exposure remains pending.

<!-- STARLOC_PHASE60_62_FINAL_UPDATE -->

## Latest validation status — Phases 60–62

The ASK033 real-camera investigation produced 233 cross-section
correspondences: 74 strict internal-consistency cases, 155 uncertain cases
and four suspect associations. Strict consistency with a local WCS solution
does not independently prove a stellar catalogue identity.

The Phase 56 strict-subset model reported a held-out RMSE of 0.9381 px.
However, Phase 57 leave-one-section-out validation reported 2.3247 px
aggregate RMSE, with R3C1 at 3.460 px. Real-camera calibration is therefore
exploratory, not independently certified.

Phase 61 provides the classified association visualisation. Phase 62
integrates the existing synthetic and real-camera evidence into JSON,
Markdown and HTML demonstration files. No previous calibration results
were modified during integration.
