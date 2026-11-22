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
