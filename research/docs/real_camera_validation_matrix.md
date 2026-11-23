# StarLoc 2.0 — Real-Camera Validation Matrix

## Purpose

Track evidence for the professor's four core objectives on the ASK033 real still image. Do not treat synthetic performance or local-WCS agreement as independent real-world truth.

| Objective | Existing evidence | Status | Exit condition |
|---|---|---|---|
| 1. Find stars in image | ASK033 detection, quality filtering, refined candidates, masks and overlays | Implemented experimentally | Evaluate precision/recall and centroid error against independently labelled real sources |
| 2. Identify catalogue stars | Hipparcos-derived visible catalogue, epoch/site transform, WCS/catalogue associations | Exploratory | Resolve time/site metadata and independently verify catalogue identities |
| 3. Convert RA/Dec to pixels | Five local WCS solutions and Objective 3 conversion script | Implemented for local sections | Verify coordinate frame, origin, section offsets and accuracy against independent references |
| 4. Determine optical calibration | Phase 38 global fit, Phase 56 strict-subset fit, Phase 57 section holdout, SIP/WCS audits | Exploratory; not independently validated | One global model must pass independent correspondence and complete-section validation |

## ASK033 evidence currently recorded

- Image size 1920 × 1440.
- Five locally solved sections: R1C2, R2C1, R2C2, R3C1, R3C2.
- Cross-section audit: 233 candidates; 74 strict internal-consistency, 155 uncertain, 4 suspect.
- Phase 38 global fit: 233 WCS-derived correspondences; 47 random held-out points; held-out RMSE 0.9863 px; training RMSE 3.9903 px; maximum training residual 30.02 px.
- Phase 56 strict subset: 15 random held-out points; RMSE 0.9381 px.
- Phase 57 leave-one-section-out: 74 strict points; R3C1 held-out RMSE 3.4604 px and maximum 8.278 px.

Strict points are selected using local-WCS residuals. They are not independently verified star identities. Phase 38/56/57 metrics therefore describe internal model behaviour under the current WCS-derived correspondence set, not external astrometric accuracy.

## Metadata blockers

- Endpoint query timestamp and image-overlay timestamp differ.
- Exposure start/midpoint/end semantics are not established.
- Recorded site coordinates are not independently surveyed in this evidence set.
- Approximate camera pointing must be confirmed or explicitly treated as an initial assumption.

## Validation gates

| ID | Test | Current status | Required evidence |
|---|---|---|---|
| V-01 | Image provenance | Partial | Source, access/licence, immutable image hash and camera ID |
| V-02 | Time/site metadata | Incomplete | Confirmed time scale, exposure convention and site provenance |
| V-03 | Star detection | Implemented experimentally | Independent real-image labels and precision/recall |
| V-04 | Centroid quality | Implemented experimentally | Real-image centroid error distribution against reference points |
| V-05 | Catalogue identity | Exploratory | Independently confirmed star IDs with reference provenance |
| V-06 | RA/Dec-to-pixel | Implemented for local WCS | Round-trip, pixel-origin and section-offset tests plus independent reference |
| V-07 | Optical calibration | Exploratory | Global model with residual distribution, uncertainty and held-out section results |
| V-08 | Reproducibility | Partial | Pinned environment, immutable inputs, configuration and run manifest |

## Required next campaign

1. Reconcile timestamp metadata and confirm observer location.
2. Independently verify a subset of star IDs.
3. Evaluate detection and centroid accuracy on labelled image regions.
4. Revalidate the local WCS transforms and coordinate conventions.
5. Fit one optical model from the accepted correspondences.
6. Hold out complete sections and compare spatial generalisation.
7. Report all residuals, outliers, model assumptions and limitations.
8. Do not claim a validated camera calibration until the independent validation gate passes.

## Scope boundary

Unknown observer-position estimation, Sun/Moon orientation, temporal attitude tracking and IMU coupling are later-stage options from the professor, not current validation requirements.
