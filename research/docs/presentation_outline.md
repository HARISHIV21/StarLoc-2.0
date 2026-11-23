# StarLoc 2.0 — Oral Presentation Outline

## Slide 1 — Project title and objective
Star identification and optical calibration for the AllSkyKamera Network. State the four objectives supplied by the professor.

## Slide 2 — Professor's expected workflow
1. Find stars in the image.
2. Identify stars in a catalogue using date/time and approximate position.
3. Convert accurate catalogue RA/Dec to pixel coordinates.
4. Determine optical calibration.
Mention that unknown observer-position estimation is deferred.

## Slide 3 — System inputs and coordinate chain
Image + timestamp + approximate site + Hipparcos catalogue → local sky prediction → detected image centroids → catalogue associations → RA/Dec-to-pixel transform → optical calibration.

## Slide 4 — Necessary synthetic observations
Explain the 1024 × 1024 controlled fisheye observation and the catalogue-rendered synthetic observation. Show known optical centre, focal scale, field of view and hidden roll. Emphasise that these are synthetic tests.

## Slide 5 — Synthetic detection and calibration results
Present 1,136 detected/identified stars, estimated FOV 179.9982°, roll 36.9993° and RMSE 0.2850 px. Label every metric synthetic.

## Slide 6 — Synthetic robustness
Show clean/noisy/degraded/stress cases, mean roll error 0.00485° and mean RMSE 0.90025 px. Explain tested assumptions and limits.

## Slide 7 — Real ASK033 observation
Show the original 1920 × 1440 image, metadata and detection overlay. Explain the recorded site/time metadata and the unresolved timestamp discrepancy.

## Slide 8 — Real catalogue association
Show the visible catalogue and five local astrometric sections. Explain 233 candidate correspondences: 74 strict internal-consistency, 155 uncertain and 4 suspect. Clarify that strict does not mean independently confirmed star identity. Distinguish the separate Phase 37B 237-match output.

## Slide 9 — RA/Dec to pixel coordinates
Demonstrate the WCS world-to-pixel mapping, FITS one-based to image zero-based conversion, section offsets and inverse round-trip check. Explain that a round-trip test is not independent astrometric truth.

## Slide 10 — Optical calibration
Explain the equidistant fisheye baseline and the exploratory real global fit. Present Phase 38 random holdout and Phase 57 leave-one-section-out results separately. Highlight the R3C1 error and why global calibration is not yet validated.

## Slide 11 — Limitations and next steps
Resolve timestamp/site metadata; independently verify star identities; quantify real detection/centroid quality; validate coordinate mapping; fit and test a global optical model on independent references and held-out sections.

## Slide 12 — Conclusion and later options
Summarise progress against the four objectives. Mention celestial-dome/Sun/Moon orientation, unknown observer-position estimation and one/two-IMU mobile-robotics coupling only as future options depending on progress.
