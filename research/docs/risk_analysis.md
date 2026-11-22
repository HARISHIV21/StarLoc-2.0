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
