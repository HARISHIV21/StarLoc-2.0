# ASK033 and Real-Image Research

This folder contains the real-observation acquisition scripts and the associated ASK033/T1 experimental data. It is the historical research workspace, not a single linear production package.

**Start with the repository-level [Real Observations & Experimental Evidence index](../../REAL_OBSERVATIONS.md).**

## Main contents

- `01_...py` onward: acquisition, preprocessing, candidate detection, local astrometry and historical phase scripts.
- `data/network/ASK033/`: public-camera image and acquisition metadata.
- `data/astrometry_indexes/`: local astrometry.net index files/configuration.
- `results/ASK033/`: ASK033 still-image and archive-sequence outputs, phase reports, overlays, CSV measurements and diagnostic images.
- `user_test/`: separate user-provided T1 image and its detection/ranking outputs.
- `phase117_dataset_selection/`: later temporal dataset-selection utility.

## Real-observation evidence

The experiments include:
- ASK033 still-image candidate detection and five-section local astrometric investigation.
- Cross-section correspondence, WCS, distortion and residual audits.
- Archive-derived temporal feature persistence, optical flow, centroid/patch tracking, photometry and morphology.
- Candidate ranking, targeted blind-solve attempts and WCS/catalogue consistency checks.
- 13-frame reconstruction, repeated catalogue-ID consistency checks, frame registration, spatial holdouts and coordinate-integrity audits through Phase 147.
- T1 real-image detection and candidate ranking.

## Interpretation guardrails

- Detected points and tracks are image-feature candidates until independently identified.
- Local WCS consistency is not independent catalogue truth.
- Phase 117 and Phase 95 share closely related data lineage; their agreement is not independent replication.
- Image-plane motion/rotation estimates do not establish physical camera motion.
- The archive MP4 referenced by reports is not in the current Git tree; extracted frames and derived reports are retained.
- ASK033 timestamps and exposure-time semantics require reconciliation before absolute epoch-dependent astrometric claims.

Do not remove historical phase scripts or result artefacts until their input/output lineage and role in the evidence record have been reviewed.
