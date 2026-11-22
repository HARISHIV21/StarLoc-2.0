# State of the Art — StarLoc 2.0

## 1. Project context

StarLoc 2.0 investigates automatic optical calibration of an all-sky camera using stellar observations. The intended application is the AllSkyKamera Network, where camera orientation and geometric properties should be estimated from night-sky images rather than relying exclusively on potentially inaccurate camera configuration.

The project focuses on detecting stars, identifying them in an astronomical catalogue, associating celestial coordinates with image pixels and estimating the camera's optical model.

## 2. Stellar catalogues and astrometry

An astronomical star catalogue provides reference positions for identifiable stars. The Hipparcos catalogue is used in this project as the reference source. Its right ascension, declination, visual magnitude and proper-motion information support the construction of a time-dependent reference sky.

The catalogue positions must be interpreted at the observation epoch. Proper motion is relevant because stellar coordinates change over time. The project propagates catalogue positions to the selected observation date before generating the local visible-sky catalogue.

## 3. Celestial coordinate systems

The project uses celestial coordinates and local horizontal coordinates.

- Right ascension and declination describe stellar positions in an equatorial reference frame.
- Altitude and azimuth describe the apparent direction of a star relative to an observer.
- Observation time and geographic location are required to relate these coordinate systems.

The current demonstration uses a temporary Rouen test location. This is not a confirmed AllSkyKamera installation location.

## 4. Star detection

Star detection identifies bright compact sources in an image. The project uses image thresholding and connected-component analysis, followed by intensity-weighted centroid estimation.

The centroid provides a subpixel estimate of the star's image position. Detection performance is affected by noise, source brightness, overlapping stars, image artefacts and background illumination.

## 5. Fisheye projection

An all-sky camera requires a wide-angle projection model. The current research implementation uses an equidistant fisheye model:

    r = f × θ

where r is the radial image distance from the optical centre, f is the focal scale in pixels and θ is the incident ray angle.

This model is a starting point. A real camera may exhibit additional radial and tangential distortions, lens asymmetry, sensor alignment errors and masking.

## 6. Astrometric identification and calibration

Once image stars are detected, their pixel coordinates can be associated with catalogue positions. Each identified star provides a correspondence between a known celestial direction and an observed image location.

The correspondences can be used to estimate optical parameters, including:
- Optical centre.
- Focal scale.
- Effective field of view.
- Camera rotation or roll under the current pointing assumptions.

Reprojection residuals quantify the difference between observed and model-predicted pixel coordinates.

## 7. Multi-section calibration

A full 180-degree fisheye image may be difficult to solve as one observation. Dividing the image into overlapping sections can provide local star correspondences. Section-level solutions can then be compared and combined.

The current synthetic experiments fit four overlapping image sections and compare their estimated parameters. A real camera implementation must additionally address lens distortion, section overlap, edge effects, star association errors and consistency of the global solution.

## 8. Existing tools and related approaches

Astrometry.net is a relevant reference approach for astronomical source identification and astrometric solving. The project investigates a complementary workflow tailored to the AllSkyKamera objective, especially the combination of solutions from multiple image sections.

Astropy is used for astronomical coordinate calculations and catalogue processing. NumPy and SciPy support numerical processing and parameter estimation. OpenCV supports image processing and star detection.

## 9. Current limitations

The current results are based on synthetic fisheye observations generated from real Hipparcos catalogue data. They do not yet establish performance on a real AllSkyKamera exposure.

The present calibration model assumes a zenith-pointed camera with an unknown roll. Arbitrary camera pointing, unknown geographic position, full distortion modelling and real-image validation remain future work.

## 10. Conclusion

The research establishes a reproducible simulation pipeline from catalogue preparation to star detection, blind matching, optical parameter estimation and multi-section validation. The next essential validation step is to apply the pipeline to an actual AllSkyKamera night-sky image with known observation time and approximate installation location.
