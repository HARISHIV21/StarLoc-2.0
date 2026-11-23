# StarLoc 2.0 — Functional & Technical Specification
## Four core objectives defined by the professor

## 1. System mission

Detect stars in an all-sky image, identify them in a celestial catalogue using the observation date/time and approximate observer location, convert their accurate RA/Dec coordinates to image pixels, and determine the camera's optical calibration.

Unknown observer position is explicitly deferred as a more complex later problem.

## 2. Inputs

| Input | Purpose | Current status |
|---|---|---|
| All-sky image | Star detection and pixel measurements | ASK033 public still image retained; synthetic observations retained |
| Observation date/time | Epoch-dependent catalogue positions and local-sky transformation | ASK033 timestamp discrepancy requires resolution |
| Approximate observer location | Transform celestial coordinates to local sky | ASK033 recorded site metadata available, not independently surveyed |
| Approximate camera pointing | Constrain initial catalogue identification | Not yet independently verified |
| Star catalogue | Reference RA/Dec, IDs, magnitude and proper motion | Hipparcos-derived data retained |
| Image geometry | Width, height, pixel origin and orientation | Recorded for retained images |
| Camera/lens information | Optical model and calibration context | Partial/unknown for ASK033 |

## 3. Functional requirements

| ID | Requirement | Evidence/status |
|---|---|---|
| FR-01 | Load and validate catalogue records | Hipparcos research workflow |
| FR-02 | Handle catalogue epoch and proper motion | Epoch propagation script and metadata |
| FR-03 | Detect point-source candidates | Synthetic and ASK033 detection scripts |
| FR-04 | Estimate image centroids | Detection/refinement workflow |
| FR-05 | Predict visible catalogue stars from time/site | Visible-sky catalogue scripts; real metadata needs confirmation |
| FR-06 | Identify image candidates in catalogue | Synthetic blind matching demonstrated; ASK033 associations exploratory |
| FR-07 | Convert RA/Dec to pixel coordinates | Objective 3 WCS conversion script; local sections |
| FR-08 | Estimate optical parameters | Synthetic calibration demonstrated; real global fit exploratory |
| FR-09 | Validate model residuals and spatial generalisation | Synthetic holdout and ASK033 section audits |
| FR-10 | Preserve source provenance and reproducibility | Documentation exists; pinned environment and metadata checks remain |

## 4. Processing stages

### 4.1 Star detection
Preprocess the image, estimate background, detect compact candidates, reject obvious artefacts and calculate sub-pixel centroids. Retain rejected candidates and quality measures for audit.

### 4.2 Catalogue identification
Load the selected catalogue version, propagate positions to the observation epoch when required, transform to the local sky using observation time and approximate site, and associate candidates with predicted catalogue stars. Record ID, RA/Dec, matching method, residual and quality class. Unknown observer position is not solved in this project stage.

### 4.3 RA/Dec-to-pixel mapping
Use the selected astrometric WCS/transform to map catalogue RA/Dec to pixel coordinates. Explicitly record FITS one-based versus image zero-based origin, axis orientation, local section coordinates and global section offsets. Perform inverse round-trip checks.

### 4.4 Optical calibration
Estimate optical centre, focal scale/FOV and appropriate distortion terms from accepted correspondences. Report fit residuals, outliers, section-dependent residuals and holdout results. A low residual against a local WCS is not independent proof of catalogue identity.

## 5. Geometric baseline

The synthetic baseline uses an equidistant fisheye relation:

    r = f × θ

where r is radial pixel distance from the optical centre, f is focal scale in pixels and θ is incident ray angle in radians.

The real-camera model must be selected from evidence and may require distortion terms. The synthetic model is not assumed to describe the ASK033 lens exactly.

## 6. Output requirements

Each calibration result should record:
- Source image ID and immutable input provenance.
- Observation timestamp, time scale and exposure-time convention.
- Observer location and provenance.
- Catalogue name/version and epoch handling.
- Detected candidate coordinates and quality.
- Accepted, uncertain and rejected catalogue correspondences.
- RA/Dec and corresponding pixel coordinates.
- Projection/distortion model and estimated parameters.
- Residual distributions, holdout method and uncertainty where estimated.
- Software version and processing configuration.

## 7. Later-stage options

Image orientation relative to the celestial dome/Sun/Moon, observer-position estimation and one/two-IMU coupling for mobile robotics are future extensions. They are not required to declare the four core objectives complete.
