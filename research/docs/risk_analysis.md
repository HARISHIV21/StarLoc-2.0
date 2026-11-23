# StarLoc 2.0 — Risk Analysis

| ID | Risk | Probability | Impact | Mitigation / next action |
|---|---|---|---|---|
| R1 | Insufficient real stars detected | Medium | High | Inspect source quality; tune detection and centroiding; label representative regions |
| R2 | False detections from noise/artefacts | High | High | Quality filtering, one-to-one matching, residual checks and independent visual audit |
| R3 | Incorrect observation timestamp | High until resolved | High | Reconcile endpoint and overlay timestamps; confirm exposure start/midpoint/end |
| R4 | Incorrect observer location | Medium | High | Confirm ASK033 installation coordinates and provenance |
| R5 | Unknown camera pointing | Medium | High | Obtain approximate pointing; defer unrestricted unknown-position solution |
| R6 | Catalogue epoch/proper-motion mismatch | Medium | High | Record catalogue epoch and propagate to verified observation epoch |
| R7 | Lens model mismatch | Medium | High | Compare residual patterns and validate distortion terms |
| R8 | Sparse section correspondences | Medium | Medium | Use overlapping sections and explicit minimum-match quality gates |
| R9 | Local WCS associations mistaken for truth | High | High | Independently verify a subset of catalogue identities |
| R10 | Global calibration overfits one image | High | High | Leave-one-section-out tests and later multiple independent images |
| R11 | Historical scripts have inconsistent prerequisites | Medium | Medium | Maintain source-to-input/output traceability and a pinned environment |

## Highest-priority risks

1. Timestamp and site metadata must be verified before final catalogue prediction.
2. Catalogue identity must be validated independently of the local WCS used for matching.
3. Global optical calibration must generalise across held-out sections.

The synthetic tests reduce algorithm-development uncertainty but do not remove physical-camera or metadata risks.
