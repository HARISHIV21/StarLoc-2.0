# StarLoc 2.0 — Real Observation & Experimental Dataset Index

This page is the entry point for the **actual camera observations and user-supplied real image tests** in the repository. These must be distinguished from synthetic fisheye images generated with known ground truth.

## 1. ASK033 AllSkyKamera — real network camera observation

**Camera:** ASK033  
**Recorded site:** Miesenbach, Austria (47.834° N, 16.005° E)  
**Image dimensions:** 1920 × 1440  
**Source:** AllSkyKamera public image endpoint  
**Stored source image:** `research/real_image/data/network/ASK033/ASK033_live_original.jpg`

### Open the actual observation and its processing outputs

- [Original ASK033 colour image](real_image/data/network/ASK033/ASK033_live_original.jpg)
- [Grayscale image](real_image/data/network/ASK033/ASK033_live_grayscale.png)
- [Original preview](real_image/results/ASK033/ASK033_original_preview.jpg)
- [Star-candidate detection overlay](real_image/results/ASK033/ASK033_detection_overlay.jpg)
- [Background-subtracted image](real_image/results/ASK033/ASK033_background_subtracted.png)
- [Refined candidate overlay](real_image/results/ASK033/ASK033_refined_candidates.jpg)
- [Detection report](real_image/results/ASK033/detection_report.json)
- [Observation metadata](real_image/results/ASK033/ASK033_observation_metadata.json)
- [Camera/source metadata](real_image/data/network/ASK033/image_metadata.json)

### Local astrometric sections

The real image was divided into a 3 × 3 grid. Local plate-solving and validation artefacts are available for the sections. Five sections were used in the later cross-section calibration investigation:

- R1C2
- R2C1
- R2C2
- R3C1
- R3C2

Open the [section previews](real_image/results/ASK033/) and the [real-image processing directory](real_image/results/ASK033/).

The local solutions and cross-section correspondences are exploratory. A local WCS agreement is not independent proof that a catalogue identity is correct.

## 2. ASK033 archive video — real multi-frame observation sequence

The repository contains frame exports and analysis results from an ASK033 archive clip identified in the reports as:

`allsky-20261119.mp4`

**Important repository limitation:** the original MP4 itself is referenced by the experiment reports but is not present in the current GitHub tree. The repository contains extracted frame images, timestamp-contact sheets, tracking measurements and analysis reports. Keep the original video in controlled external storage or add it with an appropriate large-file strategy if redistribution is permitted.

### Frame evidence

- [Frame contact sheet](real_image/results/ASK033/archive_video_20261119_frame_inspection/contact_sheet.jpg)
- [Timestamp contact sheet](real_image/results/ASK033/archive_video_20261119_frame_inspection/timestamp_sequence/timestamp_contact_sheet.jpg)
- [Timestamp audit JSON](real_image/results/ASK033/archive_video_20261119_frame_inspection/timestamp_sequence/archive_frame_timestamp_audit.json)
- [Extracted frame sequence](real_image/results/ASK033/archive_video_20261119_frame_inspection/timestamp_sequence/)

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
- [Open T1 original image](real_image/user_test/T1.jpeg)
- [Initial detection overlay](real_image/user_test/T1_detection_results/T1_detection_overlay.jpg)
- [Initial detection report](real_image/user_test/T1_detection_results/T1_detection_report.json)
- [Refined detection overlay](real_image/user_test/T1_refined_detection_results/T1_refined_overlay.jpg)
- [V2 candidate overlay](real_image/user_test/T1_refined_v2_results/T1_v2_all_overlay.jpg)
- [V2 high-confidence overlay](real_image/user_test/T1_refined_v2_results/T1_v2_high_overlay.jpg)
- [V2 candidate report](real_image/user_test/T1_refined_v2_results/T1_v2_report.json)

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
