# StarLoc 2.0 Submission Checklist

## Documentation
- [x] State-of-the-art study
- [x] Feasibility study
- [x] Functional and technical specifications
- [x] Risk analysis
- [x] Test plan and results
- [x] Project schedule
- [x] Final report
- [x] Presentation outline

## Software
- [x] Star detection pipeline
- [x] Hipparcos catalogue processing
- [x] Epoch propagation
- [x] Visible-sky catalogue generation
- [x] Blind catalogue matching
- [x] Optical calibration
- [x] Robustness validation
- [x] Consolidated demonstration
- [x] Project integrity check

## Remaining
- [ ] Real AllSkyKamera image validation
- [ ] Final oral presentation

Important: numerical results currently represent synthetic validation, not real-camera calibration.


## Current status correction — real observations through Phase 147

The earlier “Remaining” section above predates the extended real-image work and should not be read as saying no real-image validation was attempted.

**Completed at exploratory R&D level:**
- [x] ASK033 still-image acquisition, detection/refinement and five-section local astrometric investigation
- [x] Cross-section correspondence and residual audits
- [x] ASK033 archive-derived temporal image-feature analysis through Phase 147
- [x] Optical flow, centroid/patch tracking, photometry/morphology and candidate ranking
- [x] Multiframe reconstruction, existing-WCS catalogue correspondence and residual-stability checks
- [x] Image registration, spatial holdout/model comparison and coordinate-integrity audits
- [x] T1 real-image detection and candidate-ranking experiment

**Still open — independent scientific validation:**
- [ ] Recover original archive MP4 and preserve source provenance
- [ ] Reconcile ASK033 timestamp references and exposure-time semantics
- [ ] Independently verify site coordinates and real star identities
- [ ] Validate a global camera model on independently verified stars, held-out sections and multiple images
- [ ] Validate physical temporal camera orientation against an independent reference

**Still open — product/embedded engineering:**
- [ ] Pinned reproducible environment and one-command experiment runner
- [ ] Deployable server-side calibration service/API
- [ ] Embedded C++ implementation and target-hardware measurements
- [ ] Separately validated camera/IMU estimator

**Status statement:** real-image experiments have been conducted extensively, but independent real-camera astrometric validation and global calibration acceptance are not complete. Synthetic metrics are not real-camera accuracy figures.
