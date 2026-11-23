# StarLoc 2.0 — Project Schedule & Tracking

## Work packages aligned with professor's objectives

| WP | Work package | Current status | Next action | Deliverable |
|---|---|---|---|---|
| WP0 | Project tracking and documentation | Prepared | Keep decisions, risks and evidence current | Project tracking pack |
| WP1 | Find stars in the image | Synthetic and ASK033 candidate detection implemented | Label real image regions and quantify detection/centroid quality | Detection report and overlays |
| WP2 | Identify stars in catalogue using date/time and approximate position | Synthetic blind matching demonstrated; ASK033 associations exploratory | Confirm timestamp/site and independently verify catalogue IDs | Correspondence table with provenance |
| WP3 | Convert RA/Dec to pixel coordinates | Local WCS conversion workflow implemented | Audit coordinate origin, section offsets and independent accuracy | Pixel-coordinate table and round-trip report |
| WP4 | Determine optical calibration | Synthetic fit demonstrated; ASK033 global fit exploratory | Fit global model using verified correspondences and validate held-out sections | Optical parameter report and residual plots |
| WP5 | Demo and oral presentation | Synthetic demo script exists | Prepare an end-to-end demo showing the four objectives | Demo and presentation |

## Critical dependencies

- Confirmed ASK033 observation timestamp and exposure-time convention.
- Approximate camera location and pointing.
- Reference catalogue epoch and proper-motion treatment.
- Independent real-star identities for calibration validation.
- Access to retained local WCS/index artefacts and compatible Astrometry.net tooling.

## Project tracking record

At each review record:
- Work package and objective.
- Completed activity and source script.
- Input dataset and provenance.
- Output artefacts and measured results.
- Failed/uncertain cases.
- Open risks and dependencies.
- Next action and decision owner.

## Later-stage roadmap — not current core schedule

Only after WP1–WP4 are sufficiently validated:
- Determine image orientation relative to celestial dome/Sun/Moon.
- Investigate observer-position estimation if the position is unknown.
- Consider one/two-IMU coupling for mobile robotics.

A prototype is conditional on overall progress and should be discussed with the professor.
