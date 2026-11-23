# Synthetic Observation & Validation — StarLoc 2.0

## Why synthetic observations are retained

Synthetic observations provide controlled inputs with known camera geometry and known catalogue/image correspondences. They are necessary for debugging and measuring the first four project objectives before using real AllSkyKamera data. They must remain clearly separated from real-camera evidence.

## Dataset A — controlled 1024 × 1024 fisheye image

Source files:
- research/data/synthetic/synthetic_fisheye.npy
- research/data/synthetic/synthetic_fisheye.png
- research/data/synthetic/synthetic_star_catalogue.csv
- research/data/synthetic/synthetic_metadata.json

Recorded metadata:
- Image: 1024 × 1024 pixels.
- Projection: equidistant fisheye.
- Nominal field of view: 180°.
- Image radius: 500 pixels.
- Stars generated: 100.
- Known camera Euler angles: X = 8°, Y = −12°, Z = 25°.
- Random seed: 2026.

This dataset supports controlled star detection, centroid comparison and initial calibration experiments. It is synthetic, not a physical camera exposure.

## Dataset B — catalogue-rendered synthetic observation

Source files:
- research/data/synthetic/catalogue_fisheye_observation.npy
- research/data/synthetic/catalogue_fisheye_ground_truth.csv
- research/data/synthetic/catalogue_fisheye_metadata.json
- Rendered preview and catalogue products are in research/results/ and research/data/catalogue/.

Recorded metadata:
- Image: 1024 × 1024 pixels.
- Projection: equidistant fisheye, r = f × theta.
- Nominal FOV: 180°.
- Optical centre: (511.5, 511.5) px.
- Focal scale: 318.309886 px.
- Hidden test roll: 37°.
- Stars rendered from Hipparcos-derived catalogue: 1,284.
- Magnitude limit: 5.5.
- Noise sigma: 3.0; PSF sigma: 1.15 px.
- Temporary test site: Rouen, France; this is not the ASK033 site.
- Synthetic ground truth is stored separately and is not supplied to the blind-identification stage.

## Blind calibration evidence

The recorded Phase 12 / final demo reports:
- Detected image regions: 1,136.
- Catalogue candidates: 1,284.
- Identified stars: 1,136.
- Estimated optical centre: (511.5005, 511.5046) px.
- Estimated focal scale: 318.3131 px.
- Estimated FOV: 179.9982°.
- Estimated roll: 36.9993°.
- Reprojection RMSE: 0.2850 px.
- Maximum residual: 2.0206 px.
- Ground truth was not used for the matching stage; known parameters are available for post-fit evaluation.

## Synthetic robustness evidence

Four controlled scenes were tested: clean, noisy, degraded and stress. The report records:
- Mean roll error: 0.00485°.
- Mean reprojection RMSE: 0.90025 px.
- Stress-scene RMSE: 1.7174 px.
- Total catalogue matches across the four scenes: 4,184.

These results demonstrate behaviour only under the generated scene assumptions and tested degradation settings. They do not establish real-lens accuracy or independent real-camera calibration.

## Reproduction

From the repository root:

    python research/16_run_final_demo.py

The demo calls catalogue rendering, blind calibration and robustness stages and writes the consolidated report to research/results/final_demo_report.json. Install the research dependencies listed in the main README first.

## Reporting rule

Every presentation and report must label these numbers **synthetic**. Do not combine synthetic RMSE with ASK033 real-image residuals or call the synthetic observation a real AllSkyKamera image.
