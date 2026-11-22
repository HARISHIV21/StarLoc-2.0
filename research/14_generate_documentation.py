from pathlib import Path
import json
import csv

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "research" / "docs"
DOCS.mkdir(parents=True, exist_ok=True)

def write(name, content):
    path = DOCS / name
    path.write_text(content.strip() + "\n", encoding="utf-8")
    print("Created:", path)

write("state_of_art.md", r"""
# State of the Art — StarLoc 2.0

## 1. Project context

StarLoc 2.0 investigates automatic optical calibration of an all-sky camera using stellar observations. The intended application is the AllSkyKamera Network, where camera orientation and geometric properties should be estimated from night-sky images rather than relying exclusively on potentially inaccurate camera configuration.

The project focuses on detecting stars, identifying them in an astronomical catalogue, associating celestial coordinates with image pixels and estimating the camera's optical model.

## 2. Stellar catalogues and astrometry

An astronomical star catalogue provides reference positions for identifiable stars. The Hipparcos catalogue is used in this project as the reference source. Its right ascension, declination, visual magnitude and proper-motion information support the construction of a time-dependent reference sky.

The catalogue positions must be interpreted at the observation epoch. Proper motion is relevant because stellar coordinates change over time. The project propagates catalogue positions to the selected observation date before generating the local visible-sky catalogue.

## 3. Celestial coordinate systems

The project uses celestial coordinates and local horizontal coordinates.

- Right ascension and declination describe stellar positions in an equatorial reference frame.
- Altitude and azimuth describe the apparent direction of a star relative to an observer.
- Observation time and geographic location are required to relate these coordinate systems.

The current demonstration uses a temporary Rouen test location. This is not a confirmed AllSkyKamera installation location.

## 4. Star detection

Star detection identifies bright compact sources in an image. The project uses image thresholding and connected-component analysis, followed by intensity-weighted centroid estimation.

The centroid provides a subpixel estimate of the star's image position. Detection performance is affected by noise, source brightness, overlapping stars, image artefacts and background illumination.

## 5. Fisheye projection

An all-sky camera requires a wide-angle projection model. The current research implementation uses an equidistant fisheye model:

    r = f × θ

where r is the radial image distance from the optical centre, f is the focal scale in pixels and θ is the incident ray angle.

This model is a starting point. A real camera may exhibit additional radial and tangential distortions, lens asymmetry, sensor alignment errors and masking.

## 6. Astrometric identification and calibration

Once image stars are detected, their pixel coordinates can be associated with catalogue positions. Each identified star provides a correspondence between a known celestial direction and an observed image location.

The correspondences can be used to estimate optical parameters, including:
- Optical centre.
- Focal scale.
- Effective field of view.
- Camera rotation or roll under the current pointing assumptions.

Reprojection residuals quantify the difference between observed and model-predicted pixel coordinates.

## 7. Multi-section calibration

A full 180-degree fisheye image may be difficult to solve as one observation. Dividing the image into overlapping sections can provide local star correspondences. Section-level solutions can then be compared and combined.

The current synthetic experiments fit four overlapping image sections and compare their estimated parameters. A real camera implementation must additionally address lens distortion, section overlap, edge effects, star association errors and consistency of the global solution.

## 8. Existing tools and related approaches

Astrometry.net is a relevant reference approach for astronomical source identification and astrometric solving. The project investigates a complementary workflow tailored to the AllSkyKamera objective, especially the combination of solutions from multiple image sections.

Astropy is used for astronomical coordinate calculations and catalogue processing. NumPy and SciPy support numerical processing and parameter estimation. OpenCV supports image processing and star detection.

## 9. Current limitations

The current results are based on synthetic fisheye observations generated from real Hipparcos catalogue data. They do not yet establish performance on a real AllSkyKamera exposure.

The present calibration model assumes a zenith-pointed camera with an unknown roll. Arbitrary camera pointing, unknown geographic position, full distortion modelling and real-image validation remain future work.

## 10. Conclusion

The research establishes a reproducible simulation pipeline from catalogue preparation to star detection, blind matching, optical parameter estimation and multi-section validation. The next essential validation step is to apply the pipeline to an actual AllSkyKamera night-sky image with known observation time and approximate installation location.
""")

write("feasibility_study.md", r"""
# Feasibility Study — StarLoc 2.0

## 1. Objective

Assess the feasibility of automatically estimating the optical calibration of an all-sky camera from stars observed in night-sky images.

## 2. Technical feasibility

The project is technically feasible as a software-based research prototype.

The required operations can be implemented using:
- A reference stellar catalogue.
- Observation date and time.
- Approximate geographic location and camera pointing.
- Image processing for star detection.
- Catalogue matching and coordinate transformations.
- Numerical optimisation for optical calibration.

A synthetic dataset allows the pipeline to be developed and tested before real camera data is available.

## 3. Demonstrated feasibility

The current implementation demonstrates:

- Processing of 8,870 valid Hipparcos catalogue entries.
- Propagation of catalogue positions to a selected date.
- Generation of a visible-sky catalogue for a temporary Rouen test site.
- Rendering of catalogue stars into a synthetic 180-degree equidistant fisheye image.
- Blind catalogue calibration recovering approximately 180-degree field of view and 37-degree roll.
- Robustness tests under different noise, missing-star and false-detection conditions.
- Local calibration of four overlapping image sections in each of four synthetic test cases.

The Phase 12 blind calibration reported a 0.2850-pixel reprojection RMSE. Phase 13 reported a mean RMSE of 0.90025 pixels across four test scenes.

These figures apply to the synthetic experiments and their assumptions.

## 4. Resources and implementation

The prototype is implemented in Python and uses the existing macOS development environment.

Main libraries:
- NumPy
- SciPy
- OpenCV
- Astropy
- Matplotlib

No dedicated hardware or paid software is required for the current simulation work.

## 5. Main risks

- Real camera images may contain clouds, light pollution, reflections and optical artefacts.
- A camera may not point exactly at the zenith.
- The actual camera location or observation time may be uncertain.
- The equidistant model may not describe the real lens accurately.
- Catalogue matching may be ambiguous in sparse or noisy image sections.
- Calibration solutions from separate sections may not agree.

## 6. Feasibility conclusion

The software simulation demonstrates that the principal processing stages can work under controlled conditions. The feasibility of the complete AllSkyKamera application remains conditional on real-image validation and confirmation of camera metadata.

The next experimental requirement is an actual night-sky image, its timestamp, the approximate camera location and any available lens or camera information.
""")

write("functional_technical_specifications.md", r"""
# Functional and Technical Specifications — StarLoc 2.0

## 1. Functional objective

The system shall estimate the optical calibration of an all-sky camera by identifying stars in a night-sky image and associating their image coordinates with known celestial coordinates.

## 2. Inputs

Required or expected inputs:

| Input | Purpose |
|---|---|
| Night-sky image | Source for star detection |
| Observation date and time | Celestial coordinate calculation |
| Approximate geographic location | Local sky transformation |
| Approximate camera pointing | Initial identification constraint |
| Star catalogue | Reference celestial positions |
| Image dimensions | Pixel-coordinate reference |

The actual camera location, timestamp and image have not yet been supplied for real-camera validation.

## 3. Processing stages

### Stage 1 — Catalogue preparation
Load the reference catalogue, validate its fields and propagate stellar positions to the observation epoch.

### Stage 2 — Local visible-sky generation
Transform catalogue positions into local horizontal coordinates using observation time and approximate observer location.

### Stage 3 — Image preprocessing
Load the image, establish the valid image region and prepare it for star detection.

### Stage 4 — Star detection
Identify compact bright sources and estimate their intensity-weighted centroids.

### Stage 5 — Catalogue identification
Match detected stars with candidate catalogue stars using the available observation time and approximate pointing information.

### Stage 6 — Pixel-to-celestial correspondence
Associate each identified star's celestial direction with its measured image coordinates.

### Stage 7 — Optical calibration
Estimate optical centre, focal scale and other supported camera parameters by minimising reprojection residuals.

### Stage 8 — Multi-section analysis
Repeat the estimation on overlapping image regions and assess agreement between local solutions.

### Stage 9 — Calibration output
Save estimated parameters, matched-star information, residual statistics and diagnostic visualisations.

## 4. Technical model

The current baseline projection is equidistant:

    r = f × θ

The current calibration estimates:
- Optical centre (cx, cy).
- Focal scale f.
- Effective field of view.
- Roll angle under a zenith-pointed camera assumption.

## 5. Output requirements

The software should produce:
- Detected star coordinates.
- Catalogue identification table.
- Estimated camera parameters.
- Reprojection residuals.
- Calibration report in JSON or CSV.
- Diagnostic images.
- Section-level calibration results.

## 6. Constraints

The current prototype is a simulation-based research implementation. It does not yet support unrestricted arbitrary camera pointing or a complete real-lens distortion model.

Unknown observer position is outside the current priority scope. IMU integration is optional future work, not a prerequisite for the primary optical calibration objective.
""")

write("risk_analysis.md", r"""
# Risk Analysis — StarLoc 2.0

| ID | Risk | Probability | Impact | Mitigation |
|---|---|---|---|---|
| R1 | Insufficient stars detected | Medium | High | Adjust detection threshold, exposure assumptions and minimum source size |
| R2 | False detections from noise or artefacts | High | High | Robust matching, residual rejection and image-quality checks |
| R3 | Incorrect timestamp | Medium | High | Require timestamp and time zone; record UTC conversion |
| R4 | Incorrect geographic location | Medium | High | Obtain installation coordinates before real-image calibration |
| R5 | Unknown camera pointing | High | High | Begin with approximate pointing; defer unrestricted blind solving |
| R6 | Fisheye model mismatch | Medium | High | Compare residuals and extend the model using distortion parameters |
| R7 | Sparse stars in an image section | Medium | Medium | Use overlapping sections and minimum-match criteria |
| R8 | Inconsistent local section solutions | Medium | High | Compare section parameters and perform global optimisation |
| R9 | Cloud cover or light pollution | High | Medium | Select suitable images and implement image-quality screening |
| R10 | No real AllSkyKamera image available | Current blocker | High | Request a representative image and metadata from the project supervisor |

## Risk review

The synthetic tests reduce uncertainty around the algorithmic pipeline but do not eliminate the risks associated with real optical systems.

The highest-priority external dependency is access to a real AllSkyKamera image and its observation metadata.
""")

write("test_plan_and_results.md", r"""
# Test Plan and Results — StarLoc 2.0

## 1. Test objectives

Validate the principal stages of the star detection, catalogue identification and fisheye optical calibration pipeline.

## 2. Test environment

- Operating system: macOS
- Language: Python
- Image processing: OpenCV
- Numerical processing: NumPy and SciPy
- Astronomy: Astropy
- Reference catalogue: Hipparcos
- Synthetic image: 1024 × 1024 pixels
- Projection: Equidistant fisheye, nominal 180-degree field of view

## 3. Recorded results

### Star detection optimisation

- Best threshold: 3
- Minimum component area: 1 pixel
- Maximum component area: 80 pixels
- Detected regions: 101
- Catalogue matches: 99 / 100
- Mean matching error: 0.1745 pixels
- Maximum matching error: 1.2257 pixels

### Initial optical calibration

- Matched stars: 99
- Training stars: 79
- Independent test stars: 20
- Estimated optical centre: (511.9038, 512.0058) pixels
- Focal scale: 318.2911 pixels
- Estimated field of view: 180.0106 degrees
- Training RMSE: 0.2106 pixels
- Independent test RMSE: 0.6926 pixels

### Blind catalogue calibration

- Detected image regions: 1,136
- Catalogue candidates: 1,284
- Identified stars: 1,136
- Estimated optical centre: (511.501, 511.505) pixels
- Focal scale: 318.313 pixels
- Estimated field of view: 179.998 degrees
- Estimated roll: 36.999 degrees
- Mean reprojection residual: 0.1790 pixels
- Reprojection RMSE: 0.2850 pixels
- Maximum residual: 2.0206 pixels

### Robustness tests

| Scene | Roll error | Reprojection RMSE |
|---|---:|---:|
| Clean, 0° | 0.0017° | 0.5208 px |
| Noisy, 37° | 0.0037° | 0.5751 px |
| Degraded, 123° | 0.0088° | 0.7877 px |
| Stress, 271° | 0.0052° | 1.7174 px |

Mean roll error: 0.00485 degrees.

Mean reprojection RMSE: 0.90025 pixels.

Total catalogue matches across the four scenes: 4,184.

### Overlapping-section tests

Four overlapping sections were fitted in each of the four scenes, giving 16 local section fits.

Reported local parameter errors:
- Optical-centre coordinate errors below 0.1 pixels.
- Focal-scale errors below 0.11 pixels.
- Roll errors below 0.015 degrees.

The highest reported section RMSE was 1.9027 pixels in the stress scene.

## 4. Interpretation

The experiments demonstrate that the synthetic pipeline can identify catalogue stars and estimate optical parameters under the tested assumptions.

The stress scene produces higher residuals, showing that degraded image quality affects positional accuracy even when the estimated roll remains close to the simulated value.

The local section results demonstrate promising consistency in the synthetic model. They do not yet validate real-lens distortion or a combined global solution from a real 180-degree camera image.

## 5. Outstanding tests

- Real AllSkyKamera image validation.
- Arbitrary camera pointing.
- Camera-centre and focal-scale variation across independent generated scenes.
- Real optical distortion.
- Cloud, moonlight and light-pollution rejection.
- Global combination of section-level calibration solutions.
- Repeatability across multiple real observations.
""")

write("project_schedule_gantt.md", r"""
# Project Schedule and Tracking — StarLoc 2.0

## Work-package status

| Work package | Activity | Status |
|---|---|---|
| WP1 | State of the art and feasibility | Draft prepared |
| WP2 | Planning, risk analysis and test documentation | Draft prepared |
| WP3 | Synthetic image and star detection pipeline | Implemented |
| WP3 | Catalogue preparation and epoch propagation | Implemented |
| WP3 | Blind catalogue matching and optical calibration | Demonstrated in simulation |
| WP3 | Robustness and overlapping-section tests | Demonstrated in simulation |
| WP3 | Real AllSkyKamera validation | Pending image and metadata |
| WP4 | Final report and oral presentation | To finalise |

## Suggested remaining schedule

| Period | Activity | Deliverable |
|---|---|---|
| Day 1 | Review and validate documentation | Project tracking pack |
| Day 2 | Consolidate scripts and reproducibility | README and demo |
| Day 3 | Obtain and inspect real camera data | Real-image test record |
| Day 4 | Adapt model and validate real image | Calibration results |
| Day 5 | Final review | Final report and presentation |

These are proposed remaining activities, not a record of completed calendar dates.

## Dependencies

The real-camera validation depends on receiving:
- At least one representative night-sky image.
- Exact observation date and time, preferably with time zone.
- Approximate camera installation coordinates.
- Approximate camera pointing, if available.
- Camera and lens details, if available.

## Project tracking

The next review should explicitly record:
- Work completed.
- Evidence and output files.
- Open technical issues.
- External dependencies.
- Decisions and next actions.
""")

write("final_report.md", r"""
# StarLoc 2.0 — Final Research Report

## Software-Defined Optical Calibration of an All-Sky Camera Using Stellar Identification

## 1. Introduction

The objective of StarLoc 2.0 is to investigate automatic optical calibration of an all-sky camera using stars observed in night-sky images. The project is motivated by the AllSkyKamera Network requirement to determine camera orientation and geometric properties without depending entirely on potentially inaccurate camera configuration.

## 2. Methodology

The developed workflow consists of:
1. Preparation of a Hipparcos reference catalogue.
2. Propagation of stellar positions to the selected observation date.
3. Transformation into local horizontal coordinates.
4. Generation of synthetic equidistant fisheye observations.
5. Detection of stellar image regions and centroid estimation.
6. Blind catalogue identification.
7. Estimation of optical parameters.
8. Robustness testing under noise and missing or false detections.
9. Local calibration using overlapping image sections.

## 3. Implementation

The prototype uses Python, NumPy, SciPy, OpenCV, Astropy and Matplotlib.

The synthetic image is 1024 × 1024 pixels with a nominal 180-degree equidistant fisheye projection.

## 4. Results

The blind calibration experiment identified 1,136 image regions against 1,284 catalogue candidates. It estimated a 179.998-degree field of view and 36.999-degree roll, with a reprojection RMSE of 0.2850 pixels.

Four robustness scenes produced a mean roll error of 0.00485 degrees and a mean reprojection RMSE of 0.90025 pixels.

Four overlapping sections were fitted in each scene. Their local optical-centre, focal-scale and roll estimates were consistent with the simulated camera parameters.

## 5. Discussion

The results show that the main algorithmic stages are feasible under controlled synthetic conditions. The use of a real stellar catalogue makes the synthetic sky geometrically meaningful, while the rendering and noise model allow repeatable tests.

However, the synthetic images are generated from a known camera model. The current calibration also assumes zenith pointing with unknown roll. Therefore, the reported accuracy must not be interpreted as real-camera accuracy.

## 6. Limitations

- No actual AllSkyKamera exposure has yet been calibrated.
- The current camera model is equidistant and does not fully represent real-lens distortions.
- The present blind calibration assumes approximate pointing at the zenith.
- Unknown observer location is not solved.
- The global combination of section-level solutions requires further development.
- IMU coupling is outside the completed primary pipeline.

## 7. Future work

The next steps are:
1. Obtain a real AllSkyKamera image and its timestamp.
2. Confirm approximate geographic location and camera pointing.
3. Run star detection and catalogue matching on the real image.
4. Inspect residuals and identify optical-model mismatch.
5. Extend the model to include additional distortion parameters if required.
6. Combine overlapping section solutions into one global calibration.
7. Evaluate repeatability on multiple observations.

## 8. Conclusion

StarLoc 2.0 has established a software prototype for catalogue-based stellar identification and synthetic all-sky fisheye optical calibration. The blind calibration and robustness experiments provide encouraging results under controlled assumptions.

The project has not yet demonstrated calibration of a real AllSkyKamera exposure. That validation is the principal remaining experimental step.
""")

write("presentation_outline.md", r"""
# StarLoc 2.0 — Oral Presentation Outline

## Slide 1 — Title
StarLoc 2.0: Software-Defined Optical Calibration of an All-Sky Camera Using Stellar Identification.

## Slide 2 — Context and motivation
- All-sky camera network.
- Need for reliable optical calibration.
- Limitations of relying on camera configuration alone.

## Slide 3 — Project objectives
- Detect stars.
- Identify stars in a reference catalogue.
- Associate celestial and image coordinates.
- Estimate optical calibration.
- Investigate multi-section calibration.

## Slide 4 — Overall methodology
Show the pipeline:
Catalogue → visible sky → image detection → star identification → pixel/celestial correspondences → calibration.

## Slide 5 — Catalogue and coordinate processing
- Hipparcos catalogue.
- Epoch propagation.
- Observation time and temporary Rouen test location.
- Local altitude and azimuth.

## Slide 6 — Fisheye model
Explain the equidistant model and the optical centre, focal scale and field of view.

## Slide 7 — Star detection
Show the detection image and centroid method.
Include the 99/100 detection optimisation result.

## Slide 8 — Blind catalogue calibration
Show the synthetic observation and identified stars.
Present estimated field of view, roll and reprojection RMSE.

## Slide 9 — Robustness tests
Present the four test scenes and their reprojection RMSE values.

## Slide 10 — Multi-section calibration
Show the four overlapping image sections.
Present local parameter consistency and the stress-scene residuals.

## Slide 11 — Limitations and lessons learned
- Synthetic rather than real camera observations.
- Zenith-pointing assumption.
- Real-lens distortion.
- Need for camera metadata.
- Importance of robust star identification.

## Slide 12 — Conclusion and future work
- Demonstrated synthetic calibration pipeline.
- Next: real AllSkyKamera image validation.
- Future: global section combination, arbitrary pointing and optional IMU integration.
""")

write("README_RESEARCH.md", r"""
# StarLoc 2.0 — Research Workspace

## Overview

This workspace contains the research implementation for catalogue-based all-sky camera calibration.

## Environment

Activate the existing virtual environment:

    source .venv/bin/activate

The current implementation uses Python with NumPy, SciPy, OpenCV, Astropy and Matplotlib.

## Research scripts

The principal research scripts are:

- `research/01_generate_fisheye_dataset.py`
- `research/02_detect_fisheye_stars.py`
- `research/03_optimize_star_detection.py`
- `research/04_fisheye_optical_calibration.py`
- `research/07_download_hipparcos_catalogue.py`
- `research/08_clean_hipparcos_catalogue.py`
- `research/09_propagate_hipparcos_positions.py`
- `research/10_generate_visible_sky_catalogue.py`
- `research/11_render_catalogue_fisheye.py`
- `research/12_blind_catalogue_calibration.py`
- `research/13_robustness_validation.py`

Some intermediate scripts and data files are also retained in the workspace.

## Reproduce the latest synthetic experiment

From the project root:

    python research/12_blind_catalogue_calibration.py
    python research/13_robustness_validation.py

The catalogue and generated synthetic observation files must already exist under `research/data`.

## Results

Important result files are stored in `research/results`:

- `blind_fisheye_calibration.json`
- `blind_catalogue_matches.csv`
- `blind_calibration_residuals.csv`
- `phase13_robustness_report.json`
- `phase13_summary.csv`
- `phase13_robustness_example.png`

## Documentation

The `research/docs` folder contains the state of the art, feasibility study, functional and technical specifications, risk analysis, test plan, project schedule, final report and presentation outline.

## Important validation note

The current results are based on synthetic images generated from real catalogue data. They do not constitute real AllSkyKamera validation.

Real-image validation requires a representative camera image, its observation timestamp, approximate geographic location and camera pointing information.
""")

# Verify documentation files.
print("\nDOCUMENTATION PACK")
print("=" * 55)
for path in sorted(DOCS.glob("*.md")):
    print(f"{path.name:40s} {path.stat().st_size:>7,d} bytes")

print("\nPHASE 14 COMPLETE")
