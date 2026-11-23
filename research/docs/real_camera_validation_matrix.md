# StarLoc 2.0 — Real-Camera Validation Matrix

## 1. Purpose

This document separates the evidence currently available from the evidence required to claim a reliable global AllSkyKamera calibration. It is intended to prevent synthetic fit accuracy, internal WCS consistency and independent real-world accuracy from being conflated.

## 2. Evidence currently recorded

| Evidence item | Recorded result | Interpretation |
|---|---|---|
| Synthetic blind calibration | 1,136 detections / identifications; FOV 179.998°; roll 36.999°; RMSE 0.2850 px | Controlled synthetic feasibility |
| Synthetic robustness | Four scenes; mean roll error 0.00485°; mean RMSE 0.90025 px | Behaviour under tested simulated degradations |
| ASK033 image | 1920 × 1440 px; five sections with local astrometric solutions | Real-image investigation |
| Cross-section candidate associations | 233 total: 74 strict internal-consistency, 155 uncertain, 4 suspect | Association-quality audit; not independent catalogue truth |
| Phase 56 random holdout | 15 held-out points; RMSE 0.9381 px | Random point holdout within the selected strict subset |
| Phase 57 leave-one-section-out | Aggregate RMSE 2.3247 px; R3C1 RMSE 3.460 px | More demanding spatial generalisation test |

## 3. Critical interpretation

- Synthetic data are generated from a known model; their fit metrics do not establish real-lens accuracy.
- A local WCS solution can be used as a comparison reference, but agreement with it is not independent confirmation that the star has been correctly identified.
- Randomly withholding points from a selected correspondence set is less demanding than withholding a complete image section.
- The leave-one-section-out result exposes spatially dependent errors and must be reported alongside the random holdout result.
- The 74 strict cases describe internal consistency, not 74 independently certified catalogue matches.

## 4. Validation matrix

| ID | Test | Required method | Current status | Exit evidence |
|---|---|---|---|---|
| V-01 | Image provenance | Record source, licence/access, timestamp, dimensions and camera identity | Partial | Immutable dataset manifest |
| V-02 | Observation metadata | Verify time scale, location and camera pointing | Incomplete | Metadata source and uncertainty record |
| V-03 | Star detection | Evaluate precision/recall against manually or independently labelled sources | Partial | Detection metrics over multiple images |
| V-04 | Centroid accuracy | Compare centroid locations with reference measurements | Synthetic evidence exists | Real-image centroid error distribution |
| V-05 | Catalogue identity | Independently verify matched stars | Incomplete | Verified correspondence set with provenance |
| V-06 | Local astrometric solve | Solve overlapping image regions and report WCS quality | Demonstrated exploratorily | Repeatable local-solution report |
| V-07 | Global camera model | Fit one consistent model from section observations | Exploratory | Global parameter estimate and covariance/uncertainty |
| V-08 | Spatial generalisation | Leave out complete sections during fitting | Tested; errors remain | Predefined acceptance thresholds met across sections |
| V-09 | Temporal repeatability | Repeat on multiple timestamps / nights | Not established | Drift and repeatability report |
| V-10 | Dynamic orientation | Estimate changes between observations and distinguish camera motion from solver noise | Not established | Time-series validation against independent reference |
| V-11 | Environmental robustness | Clouds, moonlight, light pollution, saturation and sparse fields | Synthetic/partial | Real-image stratified performance report |
| V-12 | Operational reproducibility | Re-run from pinned environment and immutable inputs | Partial | One-command reproducibility and run manifest |

## 5. Required next experiment campaign

1. Assemble a multi-image dataset with verified observation timestamps and camera/site metadata.
2. Obtain independent astrometric reference information for a subset of stars or images.
3. Freeze a training/fit set and separate independent validation images.
4. Re-run detection, matching and local WCS experiments using recorded configuration.
5. Compare candidate correspondences against independent reference data.
6. Fit a global camera model using overlapping sections.
7. Hold out entire sections and entire images—not only random points.
8. Report pixel and angular residuals, uncertainty, outliers and failure cases.
9. Repeat across time to investigate orientation stability and dynamic changes.
10. Define and approve quantitative acceptance criteria before claiming validated calibration.

## 6. Reporting rules

Every result must state:
- Dataset and image identifiers.
- Synthetic or real observation.
- Number of input detections, candidate matches and accepted matches.
- How correspondence identity was established.
- Fit, random-holdout, section-holdout or independent-test status.
- Camera model and assumptions.
- Pixel/angular units and coordinate conventions.
- Residual distribution, not only a single RMSE.
- Known weaknesses and excluded cases.

Do not describe the real-image pipeline as fully validated until independent identity/reference checks and multi-image global calibration tests pass.


## 7. Evidence update through Phase 147

The repository also contains the following temporal and real-image results, which should be considered alongside the earlier still-image evidence:

| Phase | Recorded result | Evidence class | Qualification |
|---|---|---|---|
| 117 | 13 frames; 18,213 candidate detections; 11,449 mutual matches; zero flux-integrity failures | Reconstruction/data integrity | Candidate detections are not confirmed stars |
| 120 | 290 projected catalogue sources; 104 distinct Hipparcos IDs matched; 70 repeated in ≥2 frames | Existing-WCS correspondence | Not independent astrometric truth |
| 138 | Theil–Sen image-plane rotation slope −0.0000524° per pair; total trend −0.0005764° | Temporal image-plane diagnostic | Does not prove physical camera motion |
| 145 | 4 × 4 grid; all 16 cells represented across 12 pairs; coordinate arithmetic consistent | Coordinate integrity | Does not establish absolute accuracy |
| 146–147 | Phase 117/95 one-to-one source correspondence about 97.8–98.8% | Cross-dataset lineage audit | The datasets are related, not independent replication |
| T1 V2 | 649 candidates: 0 high, 16 medium, 633 low | Candidate ranking | Not star classifications |

The original archive MP4 referenced by the temporal reports is not in the Git tree; extracted frames and derived reports are present. ASK033 metadata contains conflicting time references and unresolved exposure timestamp semantics. These provenance issues remain validation blockers.

The current real-data status should therefore be described as **substantial exploratory real-observation R&D through Phase 147**. It is not yet independently validated global camera calibration or validated physical orientation estimation.
