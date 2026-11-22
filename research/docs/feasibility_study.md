# Feasibility Study — StarLoc 2.0

## 1. Objective

Assess the feasibility of automatically estimating the optical calibration of an all-sky camera from stars observed in night-sky images.

## 2. Technical feasibility

The project is technically feasible as a software-based research prototype.

The required operations can be implemented using:
- A reference stellar catalogue.
- Observation date and time.
- Approximate geographic location and camera pointing.
- Image processing for star detection.
- Catalogue matching and coordinate transformations.
- Numerical optimisation for optical calibration.

A synthetic dataset allows the pipeline to be developed and tested before real camera data is available.

## 3. Demonstrated feasibility

The current implementation demonstrates:

- Processing of 8,870 valid Hipparcos catalogue entries.
- Propagation of catalogue positions to a selected date.
- Generation of a visible-sky catalogue for a temporary Rouen test site.
- Rendering of catalogue stars into a synthetic 180-degree equidistant fisheye image.
- Blind catalogue calibration recovering approximately 180-degree field of view and 37-degree roll.
- Robustness tests under different noise, missing-star and false-detection conditions.
- Local calibration of four overlapping image sections in each of four synthetic test cases.

The Phase 12 blind calibration reported a 0.2850-pixel reprojection RMSE. Phase 13 reported a mean RMSE of 0.90025 pixels across four test scenes.

These figures apply to the synthetic experiments and their assumptions.

## 4. Resources and implementation

The prototype is implemented in Python and uses the existing macOS development environment.

Main libraries:
- NumPy
- SciPy
- OpenCV
- Astropy
- Matplotlib

No dedicated hardware or paid software is required for the current simulation work.

## 5. Main risks

- Real camera images may contain clouds, light pollution, reflections and optical artefacts.
- A camera may not point exactly at the zenith.
- The actual camera location or observation time may be uncertain.
- The equidistant model may not describe the real lens accurately.
- Catalogue matching may be ambiguous in sparse or noisy image sections.
- Calibration solutions from separate sections may not agree.

## 6. Feasibility conclusion

The software simulation demonstrates that the principal processing stages can work under controlled conditions. The feasibility of the complete AllSkyKamera application remains conditional on real-image validation and confirmation of camera metadata.

The next experimental requirement is an actual night-sky image, its timestamp, the approximate camera location and any available lens or camera information.
