# StarLoc 2.0 — Real Observation & Experimental Dataset Index

This page is the entry point for the **actual camera observations and user-supplied real image tests** in the repository. These must be distinguished from synthetic fisheye images generated with known ground truth.

## 1. ASK033 AllSkyKamera — real network camera observation

**Camera:** ASK033  
**Recorded site:** Miesenbach, Austria (47.834° N, 16.005° E)  
**Image dimensions:** 1920 × 1440  
**Source:** AllSkyKamera public image endpoint  
**Stored source image:** `research/real_image/data/network/ASK033/ASK033_live_original.jpg`

### Open the actual observation and its processing outputs

- [Original ASK033 colour image](research/real_image/data/network/ASK033/ASK033_live_original.jpg)
- [Grayscale image](research/real_image/data/network/ASK033/ASK033_live_grayscale.png)
- [Original preview](research/real_image/results/ASK033/ASK033_original_preview.jpg)
- [Star-candidate detection overlay](research/real_image/results/ASK033/ASK033_detection_overlay.jpg)
- [Background-subtracted image](research/real_image/results/ASK033/ASK033_background_subtracted.png)
- [Refined candidate overlay](research/real_image/results/ASK033/ASK033_refined_candidates.jpg)
- [Detection report](research/real_image/results/ASK033/detection_report.json)
- [Observation metadata](research/real_image/results/ASK033/ASK033_observation_metadata.json)
- [Camera/source metadata](research/real_image/data/network/ASK033/image_metadata.json)

### Local astrometric sections

The real image was divided into a 3 × 3 grid. Local plate-solving and validation artefacts are available for the sections. Five sections were used in the later cross-section calibration investigation:

- R1C2
- R2C1
- R2C2
- R3C1
- R3C2

Open the [section previews](research/real_image/results/ASK033/) and the [real-image processing directory](research/real_image/results/ASK033/).

The local solutions and cross-section correspondences are exploratory. A local WCS agreement is not independent proof that a catalogue identity is correct.

## 2. ASK033 archive video — real multi-frame observation sequence

The repository contains frame exports and analysis results from an ASK033 archive clip identified in the reports as:

`allsky-20261119.mp4`

**Important repository limitation:** the original MP4 itself is referenced by the experiment reports but is not present in the current GitHub tree. The repository contains extracted frame images, timestamp-contact sheets, tracking measurements and analysis reports. Keep the original video in controlled external storage or add it with an appropriate large-file strategy if redistribution is permitted.

### Frame evidence

- [Frame contact sheet](research/real_image/results/ASK033/archive_video_20261119_frame_inspection/contact_sheet.jpg)
- [Timestamp contact sheet](research/real_image/results/ASK033/archive_video_20261119_frame_inspection/timestamp_sequence/timestamp_contact_sheet.jpg)
- [Timestamp audit JSON](research/real_image/results/ASK033/archive_video_20261119_frame_inspection/timestamp_sequence/archive_frame_timestamp_audit.json)
- [Extracted frame sequence](research/real_image/results/ASK033/archive_video_20261119_frame_inspection/timestamp_sequence/)

The timestamp audit records 13 sampled frames from 0 to 36 seconds at 3-second intervals. The visible camera overlay timestamps run from 19 November 2026 17:16:50 to 20 November 2026 05:33:19 (Europe/Vienna). These are manually transcribed overlay values; whether they represent exposure start, midpoint or end is not established.

### Real multi-frame experiments already present

| Phase | Real-data experiment | Recorded evidence | Interpretation / limitation |
|---|---|---|---|
| 87 | Temporal source persistence | Frame-sequence persistence analysis | Persistence alone does not prove a source is a star |
| 90 | Fixed-pixel versus temporal motion | Frames 518–530; 1,390 reference detections; 997 tracks with at least five frames | Moving/stationary classes are exploratory; no track confirmed as a star by this phase |
| 91 | Video integrity and spatial motion consistency | Frame hashes, pixel differences and phase-correlation diagnostics | Checks sequence integrity and image motion |
| 93 | Forward/backward optical flow | 12 frame pairs; median forward/backward-valid count 129; median inlier residual 0.106 px | Optical-flow consistency is not stellar identity validation |
| 95 | Point-source centroid motion | 13 frames, 12 adjacent pairs; median 991 mutual matches per pair | Real image-feature centroid motion analysis |
| 96B | Bidirectional patch-correlation validation | 12 pairs; median 829.5 verified patch tracks per pair | Patch verification does not prove astronomical identity |
| 97 | Continuous multi-frame patch tracking | 13 frames (518–530); 565 tracks persisted in at least 10 frames; 441 in all 13 | Tracks describe local image texture and may include fixed structures |
| 98 | Stationary-structure motion audit | 1,349 tracks analysed; 567 exact integer-pixel stationary tracks | Explicitly separates stationary image structure from moving features |
| 99 | Motion-class photometry and PSF-morphology audit | 13 decoded frames; 1,076 tracks with photometry; 9,429 measurements | Photometric/morphology descriptors are not a full PSF fit or proof of star identity |

Open the detailed reports under:
`real_image/results/ASK033/phase87_...` through `phase99_...`.

## 3. User-provided real image — T1

A separate real image is stored at:

`research/real_image/user_test/T1.jpeg`

- Dimensions: 6000 × 1918 pixels.
- [Open T1 original image](research/real_image/user_test/T1.jpeg)
- [Initial detection overlay](research/real_image/user_test/T1_detection_results/T1_detection_overlay.jpg)
- [Initial detection report](research/real_image/user_test/T1_detection_results/T1_detection_report.json)
- [Refined detection overlay](research/real_image/user_test/T1_refined_detection_results/T1_refined_overlay.jpg)
- [V2 candidate overlay](research/real_image/user_test/T1_refined_v2_results/T1_v2_all_overlay.jpg)
- [V2 high-confidence overlay](research/real_image/user_test/T1_refined_v2_results/T1_v2_high_overlay.jpg)
- [V2 candidate report](research/real_image/user_test/T1_refined_v2_results/T1_v2_report.json)

The initial detector reported 2,104 image-feature candidates. The V2 ranking reported 649 candidates: 0 high-confidence, 16 medium-confidence and 633 low-confidence. These are algorithmic candidate rankings, **not confirmed star detections**. The image's source, capture timestamp, location and independent astronomical ground truth are not established in the report.

## 4. Real observations versus synthetic experiments

| Dataset | Real or synthetic? | What was tested |
|---|---|---|
| ASK033 live original image | Real camera image | Candidate detection, local astrometry, catalogue association audits and calibration investigation |
| ASK033 archive frame sequence | Real camera video frames | Temporal tracking, optical flow, centroid motion, photometry and image-structure audits |
| T1.jpeg | Real user-provided image | Detection and candidate ranking; astronomical identity not confirmed |
| `research/data/synthetic/` | Synthetic | Controlled fisheye rendering, blind catalogue matching and parameter recovery |
| `results/lesson_*/` | Primarily simulation outputs | Algorithm development and controlled tests |

## 5. Metadata issues that must remain visible

The stored ASK033 metadata contains more than one time reference:
- The image endpoint metadata records a query timestamp of 20 November 2026 19:20:23 UTC.
- The observation metadata records a camera-overlay timestamp of 19 November 2026 19:55:13 UTC and links it to an archive-video frame match.
- The archive-frame audit contains manually transcribed overlay timestamps across the clip.
- Exposure timestamp semantics (start, midpoint or end) are not independently established.
- The recorded camera-site coordinates have not been independently surveyed in the evidence.

Do not silently choose one of these timestamps as the definitive exposure epoch. Resolve the discrepancy and document the chosen time semantics before regenerating epoch-dependent catalogue coordinates or claiming astrometric accuracy.

## 6. How to navigate the real-data work

Start with:
1. The ASK033 original image and detection overlay.
2. The observation metadata and timestamp audit.
3. The section previews and local plate-solve outputs.
4. The Phase 90–99 temporal analysis reports.
5. The T1 image and candidate-ranking overlays.

The real-data experiments are substantial, but they must be described precisely: image-feature tracking and photometric stability are not equivalent to independently confirmed star tracking.


## 7. Additional real-data work after Phase 99 — Phases 100–147

The following experiments are also present in the repository and must be included when describing the real-observation work:

| Phase range | Actual work | Key recorded outcome | Limitation |
|---|---|---|---|
| 100–106 | PSF-coverage audit, candidate ranking, visual/patch inspection, shortlist and WCS coverage | Phase 101B: 1,073 rankable but not astrometrically verified; 3 invalid/degenerate; 273 with insufficient temporal evidence. Phase 105 shortlisted 11; Phase 106 found 0/11 covered by primary WCS files | Rankings are not probabilities or star IDs; shortlist did not prove catalogue identities |
| 107–116 | Targeted blind solve, WCS/catalogue validation, correspondence/residual audits and independent-region solve attempts | Solver outputs and follow-up reports retained | Solver marker/WCS output is not independent proof of a valid star-field solution |
| 117 | Clean multiframe reconstruction | 13 frames; 18,213 point-source candidate detections; 11,449 mutual matches; flux-integrity maximum absolute error 0 and zero failures | Point-source candidates, not confirmed stars |
| 120–121 | One-to-one catalogue correspondence and residual stability | 290 projected catalogue sources; 104 distinct Hipparcos IDs matched; 70 repeated in ≥2 frames, 40 in ≥3, 8 in ≥5 | Correspondences use the existing WCS; not independent astrometric truth |
| 122–129 | Frame-shift decomposition and global/tiled/overlapping registration | Multiple image-only and catalogue-derived displacement comparisons | Image-plane displacement does not identify its physical cause |
| 130–138 | Spatial support, translation/similarity/affine comparisons, quadrant holdouts and rotation-trend robustness | Phase 138 Theil–Sen slope −0.0000524° per frame pair; estimated total trend −0.0005764°; leave-one-out slopes −0.000451° to +0.001556° per pair | Descriptive image-plane estimates, not proof of physical camera rotation |
| 145 | Coordinate-integrity and full-frame spatial-support audit | 4 × 4 grid; all 16 cells represented over 12 frame pairs; coordinate arithmetic internally consistent | Data integrity is not astrometric accuracy |
| 146–147 | Cross-dataset and one-to-one vector correspondence audits | Phase 117/95 match fractions about 97.8–98.8%; Phase 117/96B about 75.0–84.0% | Phase 117/95 data lineage is related, not independent replication; Phase 96B is integer-pixel limited |

Important source-lineage finding: Phase 146/147 explicitly compares Phase 117 with Phase 95. Their strong agreement must be reported as cross-pipeline consistency on related data, not as two independent observations.

The original archive MP4 named `allsky-20261119.mp4` is referenced by reports but is not present in the current Git tree. Extracted frames and derived reports are committed. A full video rerun requires the original clip and provenance record.

The ASK033 still-image metadata also contains different time references: the image endpoint query metadata records 20 November 2026 19:20:23 UTC, while the observation metadata records an overlay time of 19 November 2026 19:55:13 UTC. Exposure start/midpoint/end semantics and independent site-coordinate confirmation are unresolved. Do not silently choose one timestamp for epoch-dependent astrometry.
