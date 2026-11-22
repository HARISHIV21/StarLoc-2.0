# Functional and Technical Specifications — StarLoc 2.0

## 1. Functional objective

The system shall estimate the optical calibration of an all-sky camera by identifying stars in a night-sky image and associating their image coordinates with known celestial coordinates.

## 2. Inputs

Required or expected inputs:

| Input | Purpose |
|---|---|
| Night-sky image | Source for star detection |
| Observation date and time | Celestial coordinate calculation |
| Approximate geographic location | Local sky transformation |
| Approximate camera pointing | Initial identification constraint |
| Star catalogue | Reference celestial positions |
| Image dimensions | Pixel-coordinate reference |

The actual camera location, timestamp and image have not yet been supplied for real-camera validation.

## 3. Processing stages

### Stage 1 — Catalogue preparation
Load the reference catalogue, validate its fields and propagate stellar positions to the observation epoch.

### Stage 2 — Local visible-sky generation
Transform catalogue positions into local horizontal coordinates using observation time and approximate observer location.

### Stage 3 — Image preprocessing
Load the image, establish the valid image region and prepare it for star detection.

### Stage 4 — Star detection
Identify compact bright sources and estimate their intensity-weighted centroids.

### Stage 5 — Catalogue identification
Match detected stars with candidate catalogue stars using the available observation time and approximate pointing information.

### Stage 6 — Pixel-to-celestial correspondence
Associate each identified star's celestial direction with its measured image coordinates.

### Stage 7 — Optical calibration
Estimate optical centre, focal scale and other supported camera parameters by minimising reprojection residuals.

### Stage 8 — Multi-section analysis
Repeat the estimation on overlapping image regions and assess agreement between local solutions.

### Stage 9 — Calibration output
Save estimated parameters, matched-star information, residual statistics and diagnostic visualisations.

## 4. Technical model

The current baseline projection is equidistant:

    r = f × θ

The current calibration estimates:
- Optical centre (cx, cy).
- Focal scale f.
- Effective field of view.
- Roll angle under a zenith-pointed camera assumption.

## 5. Output requirements

The software should produce:
- Detected star coordinates.
- Catalogue identification table.
- Estimated camera parameters.
- Reprojection residuals.
- Calibration report in JSON or CSV.
- Diagnostic images.
- Section-level calibration results.

## 6. Constraints

The current prototype is a simulation-based research implementation. It does not yet support unrestricted arbitrary camera pointing or a complete real-lens distortion model.

Unknown observer position is outside the current priority scope. IMU integration is optional future work, not a prerequisite for the primary optical calibration objective.
