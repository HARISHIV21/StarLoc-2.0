# StarLoc 2.0 — Submission Checklist

## Project tracking and documentation
- [x] State-of-the-art study
- [x] Feasibility study
- [x] Functional and technical specifications
- [x] System architecture
- [x] Risk analysis
- [x] Test plan and results
- [x] Project schedule and tracking
- [x] Final R&D report
- [x] Presentation outline
- [x] Professor objectives and traceability
- [x] Real observation evidence index
- [x] Synthetic observation validation note

## Source code and evidence
- [x] Synthetic image generation with known ground truth
- [x] Star detection and centroiding
- [x] Hipparcos catalogue processing and epoch propagation
- [x] Visible-sky catalogue generation
- [x] Synthetic blind catalogue matching
- [x] Synthetic optical calibration
- [x] Synthetic robustness validation
- [x] ASK033 real-image acquisition and detection evidence
- [x] ASK033 catalogue and local astrometric investigation
- [x] RA/Dec-to-pixel conversion workflow
- [x] Real-image optical calibration and residual audits (exploratory)
- [x] Synthetic demonstration script
- [ ] Independently validated real star identities
- [ ] Independently validated global real-camera optical calibration
- [ ] Pinned dependency environment and complete one-command reproducibility

## Demonstration and presentation
- [x] Synthetic demo entry point: research/16_run_final_demo.py
- [x] Real-image overlays and calibration evidence indexed
- [ ] Prepare concise end-to-end demo for professor
- [ ] Final oral presentation

## Explicitly later-stage options
- [ ] Image orientation relative to celestial dome/Sun/Moon
- [ ] Observer-position estimation when position is unknown
- [ ] One/two-IMU coupling for mobile robotics

These later items are not required to close the professor's four core objectives.

**Current status:** synthetic pipeline demonstrated; real ASK033 work is exploratory. The principal scientific closure tasks are metadata confirmation, independent catalogue identity verification and global optical-calibration validation.
