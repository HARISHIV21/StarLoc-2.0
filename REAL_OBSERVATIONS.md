# StarLoc 2.0 — Real Observation Evidence Index

This index contains the real AllSkyKamera observation retained as the active dataset for the professor's four core objectives. Synthetic datasets are documented separately in research/docs/synthetic_observation_validation.md.

## 1. ASK033 public AllSkyKamera still image

**Camera:** ASK033  
**Recorded site:** Miesenbach, Austria  
**Recorded coordinates:** 47.834° N, 16.005° E  
**Image dimensions:** 1920 × 1440 pixels  
**Source:** AllSkyKamera public image endpoint  
**Original observation:** [ASK033_live_original.jpg](research/real_image/data/network/ASK033/ASK033_live_original.jpg)

### Original image and metadata

- [Original colour image](research/real_image/data/network/ASK033/ASK033_live_original.jpg)
- [Grayscale image](research/real_image/data/network/ASK033/ASK033_live_grayscale.png)
- [Original preview](research/real_image/results/ASK033/ASK033_original_preview.jpg)
- [Camera metadata](research/real_image/data/network/ASK033/camera_metadata.json)
- [Endpoint/image metadata](research/real_image/data/network/ASK033/image_metadata.json)
- [Observation metadata](research/real_image/results/ASK033/ASK033_observation_metadata.json)
- [EXIF metadata audit](research/real_image/results/ASK033/image_exif_metadata.json)

**Metadata warning:** the endpoint query timestamp and timestamp transcribed from the camera overlay differ. The overlay timestamp's exposure semantics (start, midpoint or end) are not established. Site coordinates are recorded camera metadata and have not been independently surveyed in this evidence set. Resolve these before final epoch-dependent catalogue matching.

## 2. Objective 1 — star detection

- [Detection overlay](research/real_image/results/ASK033/ASK033_detection_overlay.jpg)
- [Background-subtracted image](research/real_image/results/ASK033/ASK033_background_subtracted.png)
- [Detection mask](research/real_image/results/ASK033/ASK033_detection_mask.png)
- [Quality-detection overlay](research/real_image/results/ASK033/ASK033_quality_detections.jpg)
- [Refined candidate overlay](research/real_image/results/ASK033/ASK033_refined_candidates.jpg)
- [Initial detection report](research/real_image/results/ASK033/detection_report.json)
- [Quality report](research/real_image/results/ASK033/quality_detection_report.json)
- [Candidate coordinates](research/real_image/results/ASK033/real_star_candidates.csv)
- [Refined candidate coordinates](research/real_image/results/ASK033/refined_candidates.csv)

The detector outputs are point-source candidates. Candidate detection alone does not prove every detected source is a star.

## 3. Objective 2 — catalogue identification

- [ASK033 visible Hipparcos catalogue](research/real_image/results/ASK033/ASK033_visible_hipparcos_catalogue.csv)
- [Catalogue metadata](research/real_image/results/ASK033/ASK033_catalogue_metadata.json)
- [Catalogue-ID validation](research/real_image/results/ASK033/ASK033_catalogue_id_validation.json)
- [Phase 21 matching report](research/real_image/results/ASK033/phase21_matching_report.json)
- [Phase 33 Hipparcos validation](research/real_image/phase33_hipparcos_validation.json)
- [Phase 37B final multi-section report](research/real_image/results/ASK033/phase37B_final_validation/phase37B_final_report.json)
- [Final classified correspondence evidence](research/final_professor_evidence/STARLOC_FINAL_REAL_IMAGE_SUMMARY.txt)
- [Machine-readable correspondence report](research/final_professor_evidence/STARLOC_FINAL_REAL_IMAGE_REPORT.json)
- [All classified correspondences](research/final_professor_evidence/all_classified_correspondences.csv)
- [Strict internal-consistency subset](research/final_professor_evidence/strict_internal_correspondences.csv)

The historical association audit recorded 233 candidates: 74 strict internal-consistency, 155 uncertain and 4 suspect. “Strict” means internally consistent with the selected local-WCS residual check; it is not independent proof of catalogue identity. Phase 37B separately records 237 accepted geometric matches using its own 5-pixel association gate. These counts refer to different processing/audit outputs.

## 4. Objective 3 — RA/Dec to pixel coordinates

- [RA/Dec-to-pixel implementation](research/real_image/25_objective3_radec_to_pixel.py)
- [Five-section local WCS solutions](research/real_image/results/ASK033/phase36_section_solutions/)
- [Custom R2C2 WCS solution](research/real_image/results/ASK033/custom_plate_solutions/)
- [Coordinate conversion outputs](research/real_image/results/ASK033/objective3_radec_to_pixel/)

The script applies Astropy WCS world-to-pixel conversion, handles FITS one-based versus zero-based image coordinates, adds section offsets and performs an inverse round-trip check. This verifies numerical transform consistency, not independent correctness of the WCS or star identities.

## 5. Objective 4 — optical calibration

- [Global calibration report](research/real_image/phase38_global_calibration_report.json)
- [Calibration sensitivity report](research/real_image/phase41_calibration_sensitivity_report.json)
- [Spatial residual validation](research/real_image/phase42_spatial_validation_report.json)
- [Cross-section consistency report](research/real_image/phase49_cross_section_consistency_report.json)
- [Strict correspondence audit](research/real_image/phase55_strict_correspondence_audit_report.json)
- [Strict global calibration report](research/real_image/phase56_strict_global_calibration_report.json)
- [Leave-one-section-out report](research/real_image/phase57_leave_one_section_out_report.json)
- [Section error diagnostics](research/real_image/phase58_section_error_diagnostics_report.json)
- [Final real-camera summary](research/real_image/phase59_final_real_camera_validation_summary.json)
- [Final association audit](research/real_image/phase60_real_star_association_audit_report.json)
- [Final association visualisation report](research/real_image/phase61_final_association_visualisation_report.json)
- [Final association overlay](research/real_image/results/ASK033/phase61_final_association_visualisation/phase61_real_star_association_overlay.jpg)

The real global optical model is exploratory. Fitting correspondences are derived from local WCS solutions, so they are not independent ground truth. Leave-one-section-out validation shows non-uniform spatial generalisation, especially in R3C1. Do not present the current global model as a validated operational camera calibration.

## 6. Scope boundary

The active scope is the ASK033 still image. Separate T1 image tests and archive-video temporal/motion experiments were removed from the active repository to keep the project aligned with the professor's four primary objectives. Their former files remain recoverable from Git history before the cleanup commit. They are not part of the current evidence baseline.
