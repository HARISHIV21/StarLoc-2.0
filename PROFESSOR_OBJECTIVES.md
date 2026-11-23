# StarLoc 2.0 — Professor Objectives & Implementation Traceability

This document preserves the professor's stated task order and maps it to the work currently present in the repository. The first four items define the active project scope. The remaining items are explicitly later-stage options.

## A. Core objectives — priority order

### Objective 1 — Find the stars in the image

**Professor's intent:** detect stars in the supplied all-sky image.

**Existing implementation**
- Synthetic detection and centroiding: research/02_detect_fisheye_stars.py, research/03_optimize_star_detection.py.
- Real ASK033 acquisition: research/real_image/01_inspect_ask033.py through 03_download_ask033.py.
- Real ASK033 detection and refinement: research/real_image/04_detect_real_stars.py, 05_real_source_quality.py, 06_refine_real_candidates.py.

**Retained evidence**
- Original ASK033 image and metadata in research/real_image/data/network/ASK033/.
- Detection overlays, masks, candidate CSVs and reports in research/real_image/results/ASK033/.
- Synthetic observation, ground-truth catalogue and detection reports in research/data/synthetic/ and research/results/.

**Status:** implemented as a research detector and exercised on the ASK033 image. A labelled real-image reference set and quantified real detection precision/recall remain to be established.

### Objective 2 — Identify the stars in a catalogue using date/time and approximate position

**Professor's intent:** use observation date/time and approximate observer location to predict the visible sky and identify detected stars. If location is unknown, defer that harder problem.

**Existing implementation**
- Hipparcos acquisition/cleaning/epoch propagation: research/07_download_hipparcos_catalogue.py, 08_clean_hipparcos_catalogue.py, 09_propagate_hipparcos_positions.py.
- Visible-sky catalogue: research/10_generate_visible_sky_catalogue.py.
- Catalogue-based synthetic observation and blind matching: research/11_render_catalogue_fisheye.py, 12_blind_catalogue_calibration.py.
- ASK033 catalogue construction and matching: research/real_image/07_build_ask033_catalogue.py, 08_fix_ask033_catalogue_ids.py, 09_phase21_initial_real_matching.py, and subsequent WCS/catalogue validation scripts.

**Known position:** ASK033 metadata records Miesenbach, Austria (47.834° N, 16.005° E). Treat this as provisional metadata until independently confirmed. The synthetic catalogue uses a separate temporary Rouen test location; it is not the ASK033 site.

**Metadata issue:** the endpoint query timestamp and image-overlay timestamp recorded in the repository differ. Exposure start/midpoint/end semantics are not confirmed. Resolve this before regenerating the epoch-dependent visible catalogue.

**Status:** catalogue preparation and synthetic blind identification are demonstrated. Real ASK033 catalogue correspondences remain provisional/exploratory; independent identity confirmation is not complete.

**Out of scope for now:** solving an unknown observer position. The professor explicitly places this later.

### Objective 3 — Convert accurate catalogue RA/Dec to pixel coordinates

**Professor's intent:** after stars are identified, their RA/Dec are known accurately; use the image transform to obtain their pixel coordinates.

**Existing implementation**
- Local astrometric solutions and WCS outputs are retained under research/real_image/results/ASK033/phase36_section_solutions/ and custom_plate_solutions/.
- RA/Dec-to-pixel conversion: research/real_image/25_objective3_radec_to_pixel.py.
- The script uses Astropy WCS all_world2pix, converts FITS one-based coordinates to zero-based local pixels, applies section offsets and checks the inverse transform.

**Status:** the conversion implementation exists for available local WCS solutions. Its numerical round-trip check verifies transform consistency; it does not independently prove input star identity or WCS correctness.

### Objective 4 — Determine optical calibration from the identified stars

**Professor's intent:** estimate camera optical calibration from star/celestial-coordinate and pixel-coordinate correspondences.

**Existing implementation**
- Synthetic constrained fisheye calibration: research/04_fisheye_optical_calibration.py, 12_blind_catalogue_calibration.py.
- Real local astrometry and global fisheye fitting: research/real_image/13–24, 26–44.
- Distortion and model diagnostics include WCS parameter audits, SIP analysis/effectiveness, vector fields, section-boundary continuity, sensitivity and leave-one-section-out checks.

**Recorded real-image evidence**
- Five ASK033 sections have local astrometric solutions.
- The historical cross-section audit retained 233 candidate correspondences: 74 strict internal-consistency, 155 uncertain and 4 suspect.
- The strict class is based on local-WCS consistency, not independent star identity.
- Phase 57 leave-one-section-out validation exposes non-uniform generalisation; the R3C1 fold is notably weak.

**Status:** optical calibration has been investigated and a global model fitted experimentally. A single globally consistent, independently validated real-camera optical calibration has not yet been established.

## B. Later-stage options — not current acceptance criteria

These are the professor's possible next steps depending on progress:

1. Determine image orientation relative to the celestial dome, Sun or Moon.
2. Determine observer position from star data, similar to a traditional star tracker.
3. Couple one or two IMUs to account for motion for mobile robotics.

Do not present these as implemented deliverables. The unknown-position problem is explicitly deferred.

## C. Deliverables expected for review

- Project tracking documents and planning.
- Source code for the work.
- Documented synthetic observations and test evidence.
- Real-image demonstration/evidence where possible.
- Test plan, results, limitations and final report.
- Demo before the oral presentation, if feasible.
- Prototype only if overall progress justifies it; discuss this with the professor later.

## D. Completion gate

The active project is ready for a strong review when the four core objectives can be demonstrated in order on the real ASK033 observation, with:
- traceable observation time and approximate site;
- a documented star-detection result;
- catalogue associations whose identity quality is assessed independently;
- RA/Dec-to-pixel conversion with explicit coordinate conventions;
- an optical model with residuals and spatial validation;
- reproducible scripts, inputs, outputs and a concise demo.

The current repository is a research prototype and evidence record. The real-camera validation gates above remain open.
