# StarLoc 2.0 — Feasibility Study

## 1. Objective

Assess the feasibility of the professor's four-step task: detect stars, identify them in a catalogue using date/time and approximate location, convert catalogue RA/Dec to pixels, and determine optical calibration.

## 2. Technical approach

1. Load an all-sky image and observation metadata.
2. Prepare the Hipparcos-derived catalogue for the observation epoch.
3. Use approximate observer location to predict visible catalogue stars.
4. Detect image candidates and estimate centroids.
5. Associate candidates with catalogue stars.
6. Convert RA/Dec to pixel coordinates through the astrometric image transform.
7. Estimate and validate optical parameters and distortion.

If observer position is unknown, the professor says that problem is more complex and should be addressed later.

## 3. Demonstrated synthetic feasibility

- 8,870 valid Hipparcos catalogue entries are recorded in the catalogue workflow.
- Catalogue positions are propagated to a selected epoch.
- A visible-sky catalogue is generated for a temporary Rouen test location.
- Catalogue stars are rendered into a synthetic 180° equidistant-fisheye observation.
- Blind synthetic calibration reports 1,136 detections/identifications, FOV 179.9982°, roll 36.9993° and RMSE 0.2850 px.
- Four synthetic robustness scenes report mean roll error 0.00485° and mean RMSE 0.90025 px.

These results demonstrate the constrained synthetic pipeline, not real-lens accuracy.

## 4. Real ASK033 feasibility evidence

A public 1920 × 1440 ASK033 image has been processed. Five sections have local astrometric solutions. The historical correspondence audit records 233 candidates: 74 strict internal-consistency, 155 uncertain and 4 suspect.

The global real-camera model remains exploratory. The strict subset and local WCS residuals are not independent proof of star identities. Leave-one-section-out validation shows non-uniform spatial generalisation.

## 5. Feasibility by objective

| Objective | Assessment | Main remaining dependency |
|---|---|---|
| Star detection | Demonstrated as a research prototype | Independent labels for real-image performance |
| Catalogue identification | Synthetic demonstration; real-image exploratory | Verified time/site metadata and independent star IDs |
| RA/Dec-to-pixel conversion | Implemented for local WCS sections | Independent coordinate accuracy and convention checks |
| Optical calibration | Synthetic demonstrated; real fit exploratory | Independently verified correspondences and spatial validation |

## 6. Main risks

- Incorrect timestamp or exposure convention.
- Incorrect or uncertain observer location.
- Unknown camera pointing.
- False candidate detections or catalogue associations.
- Lens distortion beyond the baseline model.
- Sparse stars in some image sections.
- Inconsistent local section solutions.
- No independent astrometric truth set.

## 7. Conclusion

The four objectives are technically feasible. The synthetic pipeline provides controlled evidence, and the ASK033 image provides a real-data research baseline. The next critical step is to resolve metadata and independently verify catalogue identities before claiming a validated global optical calibration.
