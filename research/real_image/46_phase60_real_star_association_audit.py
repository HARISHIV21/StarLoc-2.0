from pathlib import Path
import csv
import json
import statistics
from collections import defaultdict

ROOT = Path.cwd()
BASE = ROOT / "research/real_image"
ASK = BASE / "results/ASK033"

phase49_csv = (
    ASK / "phase49_cross_section_consistency"
    / "phase49_cross_section_point_comparison.csv"
)
phase53_csv = (
    ASK / "phase53_catalogue_revalidation"
    / "phase53_catalogue_identity_audit.csv"
)

required = [
    phase49_csv,
    phase53_csv,
    BASE / "phase37_multi_section_validation.json",
    BASE / "phase55_strict_correspondence_audit_report.json",
    BASE / "phase59_final_real_camera_validation_summary.json",
]

missing = [p for p in required if not p.exists()]
if missing:
    print("MISSING INPUTS:")
    for p in missing:
        print(" ", p.relative_to(ROOT))
    raise SystemExit("Audit stopped: required existing results are missing.")

with phase49_csv.open(newline="") as f:
    phase49 = list(csv.DictReader(f))

with phase53_csv.open(newline="") as f:
    phase53 = list(csv.DictReader(f))

def number(row, key):
    return float(row[key])

sections = defaultdict(list)
for row in phase49:
    sections[row["section"]].append(row)

print("=" * 76)
print("STARLOC 2.0 — PHASE 60")
print("REAL-STAR ASSOCIATION VALIDATION AUDIT")
print("=" * 76)

print("\n1. EXISTING CORRESPONDENCE COUNTS")
print("Total Phase 49 correspondences:", len(phase49))

thresholds = [0.5, 1.0, 1.5, 2.0, 3.0, 5.0]

for section in sorted(sections):
    rows = sections[section]
    errors = [
        number(r, "local_wcs_candidate_error_px") for r in rows
    ]
    print(f"\n{section}: {len(rows)} correspondences")
    print(f"  Median local-WCS residual: {statistics.median(errors):.3f}px")
    print(f"  RMSE: {(sum(e*e for e in errors)/len(errors))**0.5:.3f}px")
    for threshold in thresholds:
        count = sum(e <= threshold for e in errors)
        print(f"  Within {threshold:.1f}px: {count}/{len(errors)}")

print("\n2. STRICT MATCH SET")
strict = [
    r for r in phase49
    if number(r, "local_wcs_candidate_error_px") <= 1.0
]
print("Correspondences with local-WCS residual <= 1px:", len(strict))

for section in sorted(sections):
    count = sum(
        number(r, "local_wcs_candidate_error_px") <= 1.0
        for r in sections[section]
    )
    print(f"  {section}: {count}")

print("\n3. FOUR PREVIOUSLY SUSPECTED ASSOCIATIONS")
for row in phase53:
    print(
        f"\n{row['point']}: "
        f"assigned HIP={row['original_assigned_hip_id']}"
    )
    print(
        "  Candidate nearest HIP:",
        row["candidate_nearest_hip_id"],
        "| separation:",
        f"{number(row, 'candidate_nearest_hip_separation_arcsec'):.2f} arcsec"
    )
    print(
        "  Prediction nearest HIP:",
        row["prediction_nearest_hip_id"],
        "| separation:",
        f"{number(row, 'prediction_nearest_hip_separation_arcsec'):.2f} arcsec"
    )
    print(
        "  Same nearest catalogue ID:",
        row["same_nearest_catalogue_id"]
    )

print("\n4. ASSOCIATION QUALITY INTERPRETATION")
print(
    "A low local-WCS pixel residual demonstrates internal consistency "
    "between a candidate and its section WCS. It does NOT independently "
    "prove the Hipparcos identity."
)
print(
    "The four Phase 53 cases remain suspect because the catalogue "
    "angular separations are large and the global-prediction nearest "
    "catalogue identities differ."
)

# Export transparent quality-labelled subsets.
out = ASK / "phase60_association_audit"
out.mkdir(parents=True, exist_ok=True)

accepted_path = out / "phase60_strict_internal_consistency.csv"
uncertain_path = out / "phase60_uncertain_correspondences.csv"

fields = list(phase49[0].keys())

with accepted_path.open("w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerows(strict)

uncertain = [
    r for r in phase49
    if number(r, "local_wcs_candidate_error_px") > 1.0
]

with uncertain_path.open("w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerows(uncertain)

report = {
    "phase": 60,
    "title": "Real-star association validation audit",
    "input_correspondences": len(phase49),
    "strict_internal_consistency_count": len(strict),
    "uncertain_correspondence_count": len(uncertain),
    "strict_threshold_px": 1.0,
    "per_section": {},
    "previously_suspected_associations": phase53,
    "conclusion": (
        "This audit classifies internal pixel-WCS consistency. "
        "It does not independently certify catalogue identities. "
        "Independent real-star confirmation remains necessary."
    ),
    "limitations": [
        "The local WCS solutions are not independent ground truth.",
        "The image uses one public AllSky camera observation.",
        "Catalogue identity requires stronger independent verification.",
        "The four Phase 53 suspect associations must not be presented "
        "as confirmed star identifications."
    ]
}

for section, rows in sorted(sections.items()):
    errors = [
        number(r, "local_wcs_candidate_error_px") for r in rows
    ]
    report["per_section"][section] = {
        "count": len(rows),
        "median_residual_px": statistics.median(errors),
        "rmse_px": (sum(e*e for e in errors)/len(errors))**0.5,
        "within_1px": sum(e <= 1.0 for e in errors),
        "within_2px": sum(e <= 2.0 for e in errors),
        "within_3px": sum(e <= 3.0 for e in errors),
        "within_5px": sum(e <= 5.0 for e in errors)
    }

report_path = BASE / "phase60_real_star_association_audit_report.json"
report_path.write_text(json.dumps(report, indent=2))

print("\n" + "=" * 76)
print("PHASE 60 COMPLETED")
print("=" * 76)
print("Report:", report_path.relative_to(ROOT))
print("Strict internal-consistency CSV:", accepted_path.relative_to(ROOT))
print("Uncertain correspondence CSV:", uncertain_path.relative_to(ROOT))
print("\nNo calibration parameters or previous results were modified.")
