import json
import shutil
import subprocess
from pathlib import Path

import cv2

ROOT = Path("research/real_image")
IMAGE = ROOT / "data/network/ASK033/ASK033_live_original.jpg"
OUT = ROOT / "results/ASK033"
OUT.mkdir(parents=True, exist_ok=True)

print("\nSTARLOC 2.0 — PHASE 23")
print("=" * 58)

print("\n1. ASTROMETRY.NET AVAILABILITY")
for command in ("solve-field", "astrometry-engine", "build-astrometry-index"):
    path = shutil.which(command)
    print(command + ":", path if path else "NOT INSTALLED")

print("\n2. IMAGE VALIDATION")
image = cv2.imread(str(IMAGE))
if image is None:
    raise SystemExit("ERROR: original ASK033 image not found")

height, width = image.shape[:2]
print("Dimensions:", width, "x", height)
print("Channels:", image.shape[2])

print("\n3. IMAGE METADATA")
try:
    from PIL import Image
    with Image.open(IMAGE) as im:
        print("Format:", im.format)
        print("EXIF fields:", len(im.getexif()))
        exif = {
            str(k): str(v) for k, v in im.getexif().items()
        }
        (OUT / "image_exif_metadata.json").write_text(
            json.dumps(exif, indent=2)
        )
except Exception as exc:
    print("Pillow EXIF inspection unavailable:", repr(exc))

print("\n4. NINE IMAGE SECTIONS")
for row in range(3):
    for col in range(3):
        x1 = col * width // 3
        x2 = (col + 1) * width // 3
        y1 = row * height // 3
        y2 = (row + 1) * height // 3
        section = image[y1:y2, x1:x2]
        name = f"ASK033_section_R{row+1}C{col+1}.jpg"
        cv2.imwrite(str(OUT / name), section)
        print(name, section.shape[1], "x", section.shape[0])

print("\n5. PREVIOUS MATCHING RESULTS")
for filename in (
    "phase21_matching_report.json",
    "phase22_full_orientation_report.json"
):
    path = OUT / filename
    if path.exists():
        print("\n" + filename)
        data = json.loads(path.read_text())
        for key, value in data.items():
            print(f"{key}: {value}")

print("\nPHASE 23 AUDIT COMPLETE")
print("Section images saved in:", OUT.resolve())
