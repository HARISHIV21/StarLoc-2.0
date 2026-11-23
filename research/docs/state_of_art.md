# StarLoc 2.0 — Technical Background & Research Context

## 1. Problem context

StarLoc investigates optical calibration of wide-field all-sky cameras from stellar observations. Its immediate objective is to detect stars, identify them in a catalogue using observation date/time and approximate observer location, convert celestial coordinates to pixels, and estimate optical calibration.

## 2. Catalogue and epoch

A stellar catalogue provides reference IDs, right ascension, declination and associated astrometric information. StarLoc uses Hipparcos-derived data. Catalogue epoch and proper motion matter when comparing catalogue positions with later observations.

## 3. Time and observer position

Observation time and observer location are required to relate equatorial coordinates to the local sky. The current synthetic workflow uses a temporary Rouen test site. The ASK033 real image has recorded Miesenbach site metadata, but the timestamp discrepancy and independent site provenance require confirmation.

The professor explicitly defers unknown observer-position estimation as a more complex later problem.

## 4. Image detection and centroiding

The current prototype uses image preprocessing, background estimation, thresholding and connected-component candidate extraction, followed by centroid refinement. Candidate quality is affected by noise, background gradients, saturation, overlapping sources, clouds, reflections and other artefacts.

## 5. Celestial-to-pixel geometry

The project connects:
- Equatorial RA/Dec catalogue coordinates.
- Local horizontal altitude/azimuth coordinates.
- Camera/image pixel coordinates.

The coordinate transformation must specify reference frame, epoch, time scale, observer site, pixel origin, axis direction and transform convention.

## 6. Fisheye optical model

The synthetic baseline uses the equidistant projection:

    r = f × θ

where r is radial pixel distance, f is focal scale and θ is incident ray angle in radians.

A physical camera may require additional radial/tangential distortion terms and validation over the full field. The synthetic model is not assumed to represent the real ASK033 lens exactly.

## 7. Identification and optical calibration

After detections are associated with catalogue stars, each accepted correspondence links a celestial coordinate with an image coordinate. These pairs support optical parameter estimation. Residual analysis, outlier handling and held-out sections are needed to evaluate calibration quality.

Local WCS solutions are useful astrometric evidence but are not independent proof that the matched catalogue identities are correct.

## 8. Research gap

The main gap is independent validation on real observations: verify metadata and star identities, assess detection/centroid quality, establish RA/Dec-to-pixel accuracy and validate one global optical model across image regions.

Unknown observer-position estimation, celestial-dome/Sun/Moon orientation and IMU coupling are later options, not the present core scope.
