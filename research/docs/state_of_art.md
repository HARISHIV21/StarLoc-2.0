# Technical Background & Research Context — StarLoc 2.0

## 1. Application context

StarLoc 2.0 addresses optical calibration of wide-field all-sky cameras using stellar observations. Its primary R&D context is the AllSkyKamera Network: recover camera orientation and pixel-to-sky geometry from observations rather than relying exclusively on nominal installation parameters.

The project also studies engineering concepts that transfer to optical attitude sensing: stellar feature extraction, catalogue association, geometric calibration, multi-region consistency and measurement-quality assessment.

## 2. Astronomical reference data

A star catalogue provides reference celestial positions and associated metadata. StarLoc uses Hipparcos-derived data in its research workflow. Catalogue epoch and proper-motion information matter when comparing catalogue coordinates with observations taken at a later epoch.

The observation time, observer location and coordinate-frame conventions are required to transform celestial positions into the local sky geometry relevant to a camera.

## 3. Coordinate transformations

The research involves relationships between:
- Equatorial coordinates (right ascension and declination).
- Local horizontal coordinates (altitude and azimuth).
- Camera/image coordinates (pixel positions).
- Future aerospace body and navigation frames.

The transformation chain must record epoch, time scale, observer location, axis direction, handedness and rotation convention. A temporary Rouen test location used in synthetic experiments is not a confirmed camera installation location.

## 4. Stellar image processing

The current research prototype uses thresholding and connected-component analysis to detect compact bright candidates, followed by intensity-weighted centroid estimation. The resulting sub-pixel image locations are used as measurements for catalogue association and geometric calibration.

Detection quality is affected by background gradients, noise, saturation, overlapping sources, clouds, reflections, moonlight and other image artefacts. Real-image performance must therefore be assessed separately from synthetic tests.

## 5. Fisheye camera geometry

A wide-field all-sky camera requires a projection model that maps angular directions to image radii. The current baseline is equidistant:

    r = f × θ

where r is radial image distance from the optical centre, f is focal scale and θ is the incident ray angle.

A physical lens may require additional radial and tangential distortion terms, non-central effects, masking and asymmetric calibration. The equidistant model is a starting point rather than a universal lens model.

## 6. Catalogue identification and astrometric solving

Image detections must be associated with reference stars before camera parameters can be estimated. Local astrometric solutions provide a way to investigate image regions independently, while overlapping regions offer constraints for checking consistency and estimating a global transform.

The StarLoc real-image investigation uses local WCS solutions on ASK033 image sections. A local WCS residual is useful evidence, but agreement with that WCS does not independently certify the identity of a matched catalogue star.

## 7. Multi-section calibration as the central research challenge

A full all-sky image may have non-uniform source density, optical distortion and varying local image quality. Dividing an image into overlapping sections can help obtain local solutions. However, the resulting estimates may differ because of sparse matches, false associations, local distortion and model mismatch.

The core global-calibration challenge is to:
- Assess the reliability of each local solution.
- Preserve association provenance and uncertainty.
- Reject or down-weight inconsistent correspondences.
- Reconcile overlapping section transforms.
- Validate the global model on sections and images not used for fitting.

The current ASK033 investigation exposed section-dependent residuals and therefore motivates further independent validation.

## 8. Related tools used in the research

- **Astropy:** astronomical coordinate and time-related processing.
- **NumPy / SciPy:** numerical computation and optimisation.
- **OpenCV:** image processing and candidate detection.
- **Astrometry.net:** relevant external reference approach for source identification and astrometric solving.

This project does not claim to replace these tools. It investigates a workflow tailored to all-sky multi-section calibration and the integration of local evidence into a camera-level model.

## 9. Transfer to embedded aerospace and autonomous sensing

The transferable engineering elements are:
- Camera calibration and coordinate transforms.
- Stellar feature and catalogue association.
- Geometric estimation and outlier rejection.
- Timestamped measurement generation.
- Residual and quality monitoring.
- A future C++ implementation with bounded resource use.

An aerospace optical attitude sensor requires additional camera-to-body calibration, attitude solution, timing, fault handling and verification. Camera/IMU fusion is a separate estimator. Those capabilities are future work, not current claims.

## 10. Research gap and conclusion

The key gap is not basic star detection alone. It is independent real-camera validation and robust reconciliation of local astrometric solutions into a globally consistent calibration over multiple image regions and observations.

The next research phase should prioritise independent reference data, complete-section and complete-image holdouts, temporal repeatability, uncertainty estimation and a reproducible global calibration pipeline. Only after the optical measurement is validated should the project progress to embedded C++ deployment and aerospace estimator integration.
