# StarLoc 2.0 — System Architecture
## Architecture aligned with the professor's four core objectives

## 1. System boundary

The current system is a Python R&D prototype for optical calibration of an all-sky camera. The active real dataset is one public ASK033 still image. Controlled synthetic observations are retained for ground-truth validation.

Unknown observer-position estimation, full star-tracker attitude solution, IMU fusion, mobile robotics integration and production server deployment are outside the current scope.

## 2. Logical architecture

    [Real or Synthetic Image + Metadata]
                    |
                    v
             [Input Validation]
                    |
                    v
            [Image Pre-processing]
                    |
                    v
              [Star Detection]
                    |
                    v
          [Sub-pixel Centroiding]
                    |
                    +-----------------------+
                    |                       |
                    v                       v
          [Catalogue Preparation]   [Candidate Quality]
          [Epoch / Site / RA/Dec]            |
                    |                       |
                    +-----------+-----------+
                                |
                                v
                     [Star Identification]
                                |
                                v
                      [RA/Dec to Pixel]
                                |
                                v
                      [Optical Calibration]
                                |
                                v
                  [Residuals and Validation]
                                |
                                v
                  [Calibration Result / Demo]

## 3. Functional modules

| Module | Responsibility | Current implementation |
|---|---|---|
| Observation input | Load image and metadata | ASK033 acquisition and synthetic generation scripts |
| Catalogue preparation | Load Hipparcos data and handle epoch | Catalogue download, cleaning and propagation scripts |
| Sky prediction | Transform catalogue coordinates using time/site | Visible-sky catalogue generation |
| Image processing | Detect candidates and estimate centroids | Synthetic and real-image detection/refinement scripts |
| Identification | Match image candidates to catalogue stars | Blind synthetic matching; exploratory ASK033 WCS/catalogue workflow |
| Coordinate mapping | Convert celestial coordinates to image pixels | Astropy WCS conversion script and section solutions |
| Optical calibration | Estimate optical centre, scale/FOV and distortion | Synthetic fit and exploratory real-camera model audits |
| Validation | Report residuals and spatial holdout | Synthetic robustness and ASK033 section validation |

## 4. Coordinate and timing contracts

Before accepting real calibration, record:
- Celestial reference frame and catalogue epoch.
- Observation timestamp, time scale and exposure start/midpoint/end convention.
- Observer latitude, longitude, altitude and provenance.
- Camera/image coordinate origin and axis directions.
- FITS one-based versus image zero-based pixel coordinates.
- Local section coordinates and offsets into the full image.
- Camera projection model, angular units and transform direction.

Do not silently substitute a guessed timestamp, location or camera pointing.

## 5. Current limitations

- ASK033 metadata needs timestamp and site verification.
- Catalogue correspondences from local WCS solutions are not independent identity truth.
- Global real-camera optical calibration is exploratory and spatial generalisation is non-uniform.
- Synthetic accuracy does not establish physical-lens accuracy.
- The current project does not implement unknown-position solving, IMU fusion or a production service.
