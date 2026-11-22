# StarLoc 2.0 — Oral Presentation Outline

## Slide 1 — Title
StarLoc 2.0: Software-Defined Optical Calibration of an All-Sky Camera Using Stellar Identification.

## Slide 2 — Context and motivation
- All-sky camera network.
- Need for reliable optical calibration.
- Limitations of relying on camera configuration alone.

## Slide 3 — Project objectives
- Detect stars.
- Identify stars in a reference catalogue.
- Associate celestial and image coordinates.
- Estimate optical calibration.
- Investigate multi-section calibration.

## Slide 4 — Overall methodology
Show the pipeline:
Catalogue → visible sky → image detection → star identification → pixel/celestial correspondences → calibration.

## Slide 5 — Catalogue and coordinate processing
- Hipparcos catalogue.
- Epoch propagation.
- Observation time and temporary Rouen test location.
- Local altitude and azimuth.

## Slide 6 — Fisheye model
Explain the equidistant model and the optical centre, focal scale and field of view.

## Slide 7 — Star detection
Show the detection image and centroid method.
Include the 99/100 detection optimisation result.

## Slide 8 — Blind catalogue calibration
Show the synthetic observation and identified stars.
Present estimated field of view, roll and reprojection RMSE.

## Slide 9 — Robustness tests
Present the four test scenes and their reprojection RMSE values.

## Slide 10 — Multi-section calibration
Show the four overlapping image sections.
Present local parameter consistency and the stress-scene residuals.

## Slide 11 — Limitations and lessons learned
- Synthetic rather than real camera observations.
- Zenith-pointing assumption.
- Real-lens distortion.
- Need for camera metadata.
- Importance of robust star identification.

## Slide 12 — Conclusion and future work
- Demonstrated synthetic calibration pipeline.
- Next: real AllSkyKamera image validation.
- Future: global section combination, arbitrary pointing and optional IMU integration.
