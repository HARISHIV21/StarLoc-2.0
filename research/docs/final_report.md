# StarLoc 2.0 — Research & Development Report
## Star identification and optical calibration for the AllSkyKamera Network

## 1. Project objective

The project follows the professor's priority sequence:

1. Find stars in the image.
2. Identify them in a catalogue using observation date/time and approximate observer position. If the position is unknown, defer that harder problem.
3. Once identified, use the accurate RA/Dec positions and a celestial-to-image transform to obtain pixel coordinates.
4. Determine optical calibration from these correspondences.

Image orientation relative to the celestial dome/Sun/Moon, observer-position estimation and coupling one or two IMUs for mobile robotics are later-stage options, not current core acceptance criteria.

## 2. Implemented research workflow

The Python research prototype contains:
- Synthetic fisheye observation generation with known geometry.
- Star candidate detection, centroid estimation and detection-parameter optimisation.
- Hipparcos catalogue acquisition/cleaning and epoch-dependent position propagation.
- Visible-sky catalogue generation for a temporary Rouen test location.
- Catalogue rendering, blind matching and constrained optical calibration.
- Synthetic robustness experiments.
- Real ASK033 image acquisition, detection/refinement, visible-catalogue construction and local astrometric solving over five sections.
- RA/Dec-to-pixel conversion using Astropy WCS, including pixel-origin conversion, section offsets and inverse round-trip checks.
- Real-image optical model, distortion, residual and leave-one-section-out audits.

## 3. Synthetic validation

The catalogue-rendered synthetic observation has 1024 × 1024 pixels, nominal 180° equidistant fisheye projection, optical centre (511.5, 511.5) px, focal scale 318.309886 px and hidden roll 37°. It uses 1,284 Hipparcos-derived catalogue stars, magnitude limit 5.5, noise sigma 3.0 and PSF sigma 1.15 px. Its site is a temporary Rouen test location, not the ASK033 camera site.

The recorded blind synthetic calibration reports:
- 1,136 detected regions and 1,136 identified stars.
- Estimated FOV 179.9982° and roll 36.9993°.
- Reprojection RMSE 0.2850 px; maximum residual 2.0206 px.

Four synthetic robustness scenes report mean roll error 0.00485° and mean reprojection RMSE 0.90025 px. The stress scene RMSE is 1.7174 px.

These are synthetic truth-recovery results under the stated model. They are not real-camera accuracy measurements.

## 4. Real ASK033 observation

The retained real observation is the public ASK033 still image, 1920 × 1440 pixels, with recorded site metadata Miesenbach, Austria (47.834° N, 16.005° E). The site is not independently surveyed in this evidence set. The endpoint query timestamp and camera-overlay timestamp differ, and the overlay's exposure-time semantics are not known.

Five sections have local astrometric solutions: R1C2, R2C1, R2C2, R3C1 and R3C2.

The historical cross-section audit recorded 233 candidate correspondences: 74 strict internal-consistency, 155 uncertain and 4 suspect. Strict means consistency with the selected local-WCS residual check, not independent proof of catalogue identity. A separate Phase 37B report records 237 accepted geometric matches under a 5-pixel gate; it is a different output and must not be merged with the 233 classification count.

## 5. Real optical calibration evidence and limitations

Phase 38 reports an exploratory equidistant fisheye model with radial k1/k2 terms. It used 233 WCS-derived correspondences, with 186 training and 47 held-out points. Held-out RMSE was 0.9863 px; training RMSE was 3.9903 px with a 30.02 px maximum outlier. The fit is exploratory because its associations inherit local-WCS uncertainty.

Phase 56 uses a strict subset selected by local-WCS residual. Its 15-point random holdout RMSE was 0.9381 px. Phase 57 leave-one-section-out validation on the 74 strict points is more demanding and shows non-uniform spatial generalisation; the R3C1 held-out fold has 3.4604 px RMSE and 8.278 px maximum error. These metrics are not independent external accuracy.

The global real-camera model is therefore not yet independently validated.

## 6. Current limitations

- One real ASK033 still image is the active real dataset.
- Timestamp/exposure semantics and site-coordinate provenance require confirmation.
- Catalogue identities require independent verification beyond local-WCS agreement.
- Global calibration generalisation is not uniform across sections.
- The synthetic equidistant model does not establish real lens behaviour.
- A deployable server-side service, embedded implementation and IMU fusion are not current deliverables.

## 7. Next steps in professor's priority order

1. Resolve ASK033 observation-time and site metadata.
2. Establish an independently verified real-star correspondence subset.
3. Validate detection and centroid accuracy on labelled real image regions.
4. Verify RA/Dec-to-pixel coordinate conventions and section transforms.
5. Refit and validate a global optical model using independent references and complete held-out sections.
6. Package a reproducible demo and final report for the oral presentation.

Only after these four core objectives are sufficiently demonstrated should later orientation, unknown-position or IMU options be considered.

## 8. Conclusion

StarLoc 2.0 has a documented synthetic workflow and a substantial exploratory real ASK033 investigation covering detection, catalogue association, local astrometry, coordinate conversion and optical calibration. The strongest next contribution is not expanding into a full navigation/IMU system; it is closing the independent real-star identity and global optical-calibration validation gaps within the professor's stated scope.
