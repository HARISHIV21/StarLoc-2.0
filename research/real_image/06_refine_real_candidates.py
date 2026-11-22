import cv2
import csv
import json
import numpy as np
from pathlib import Path

BASE = Path("research/real_image")
DATA = BASE / "data/network/ASK033"
OUT = BASE / "results/ASK033"
OUT.mkdir(parents=True, exist_ok=True)

image = cv2.imread(str(DATA / "ASK033_live_original.jpg"))
if image is None:
    raise SystemExit("Original ASK033 image not found")

gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY).astype(np.float32)
h, w = gray.shape

# Valid-sky mask.
mask = np.ones((h, w), np.uint8) * 255

# Remove camera text and graphical overlays.
mask[:145, :340] = 0
mask[:115, 1180:] = 0
mask[h-220:, :350] = 0
mask[h-220:, w-370:] = 0
mask[:35, 600:1320] = 0

# Remove compass labels.
for x, y, r in [(285,600,35), (1640,600,40), (840,1390,40)]:
    cv2.circle(mask, (x,y), r, 0, -1)

# Moon and glare exclusion.
cv2.circle(mask, (1860,130), 90, 0, -1)
cv2.circle(mask, (1540,700), 300, 0, -1)

# Exclude obstructed upper-right tree area.
tree = np.array([
    [1700,0], [1919,0], [1919,520],
    [1870,430], [1820,330], [1760,210]
], np.int32)
cv2.fillPoly(mask, [tree], 0)

# Suppress the extreme fisheye boundary, where reflections are common.
yy, xx = np.mgrid[0:h, 0:w]
radius = np.sqrt(((xx-960)/930)**2 + ((yy-720)/690)**2)
mask[radius > 0.94] = 0

# Smooth background and residual.
background = cv2.GaussianBlur(gray, (0,0), 12)
residual = gray - background

# Estimate local noise from residual variance.
mean = cv2.blur(residual, (31,31))
mean_sq = cv2.blur(residual**2, (31,31))
local_sigma = np.sqrt(np.maximum(mean_sq - mean**2, 1.0))
snr_map = (residual - mean) / local_sigma

# Local maxima.
res8 = np.clip(residual, 0, 255).astype(np.uint8)
local_max = cv2.dilate(
    res8, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5,5))
)

candidate_mask = (
    (residual > 0) &
    (res8 == local_max) &
    (snr_map >= 4.5) &
    (mask > 0)
)

ys, xs = np.where(candidate_mask)
raw = sorted(
    [(float(snr_map[y,x]), int(x), int(y)) for y,x in zip(ys,xs)],
    reverse=True
)

# Non-maximum suppression: keep one detection per nearby source.
selected = []
for snr, x, y in raw:
    if any((x-s["x"])**2 + (y-s["y"])**2 < 36 for s in selected):
        continue

    patch = residual[y-4:y+5, x-4:x+5]
    weights = np.maximum(patch, 0)
    total = float(weights.sum())
    if total <= 0:
        continue

    py, px = np.mgrid[-4:5, -4:5]
    cx = float((weights*px).sum()/total)
    cy = float((weights*py).sum()/total)

    vx = float((weights*(px-cx)**2).sum()/total)
    vy = float((weights*(py-cy)**2).sum()/total)
    cov = np.array([[vx, 0], [0, vy]])
    eig = np.maximum(np.linalg.eigvalsh(cov), 0)
    major, minor = np.sqrt(eig[1]), np.sqrt(eig[0])
    elongation = major / max(minor, 0.15)

    # Reject extended, elongated and excessively broad sources.
    if major > 2.8 or elongation > 2.2:
        continue

    # Reject detections on saturated pixels.
    if gray[y,x] >= 250:
        continue

    selected.append({
        "x": round(x+cx, 3),
        "y": round(y+cy, 3),
        "snr": round(snr, 3),
        "peak_residual": round(float(residual[y,x]), 3),
        "major_sigma": round(float(major), 3),
        "minor_sigma": round(float(minor), 3),
        "elongation": round(float(elongation), 3)
    })

# Assign nine sections.
for d in selected:
    col = min(3, int(d["x"]/(w/3))+1)
    row = min(3, int(d["y"]/(h/3))+1)
    d["section"] = f"R{row}C{col}"

counts = {
    f"R{r}C{c}": sum(
        d["section"] == f"R{r}C{c}" for d in selected
    )
    for r in range(1,4) for c in range(1,4)
}

overlay = image.copy()
for d in selected:
    cv2.circle(
        overlay,
        (int(d["x"]), int(d["y"])),
        5, (0,255,0), 1
    )

for x in (w//3, 2*w//3):
    cv2.line(overlay, (x,0), (x,h), (255,180,0), 1)
for y in (h//3, 2*h//3):
    cv2.line(overlay, (0,y), (w,y), (255,180,0), 1)

cv2.imwrite(str(OUT/"ASK033_refined_candidates.jpg"), overlay)
cv2.imwrite(str(OUT/"ASK033_refined_mask.png"), mask)

fields = [
    "x","y","snr","peak_residual",
    "major_sigma","minor_sigma","elongation","section"
]
with open(OUT/"refined_candidates.csv","w",newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerows(selected)

report = {
    "image_dimensions": [w,h],
    "raw_local_maxima": len(raw),
    "refined_candidates": len(selected),
    "section_counts": counts,
    "filters": [
        "camera overlay exclusion",
        "Moon and glare mask",
        "fisheye edge exclusion",
        "local SNR threshold",
        "non-maximum suppression",
        "compactness and elongation filtering",
        "saturation rejection"
    ],
    "warning": "Remaining candidates still require astronomical catalogue validation."
}
(OUT/"phase19_report.json").write_text(json.dumps(report,indent=2))

print("\nSTARLOC 2.0 — PHASE 19")
print("="*55)
print("Raw local maxima:", len(raw))
print("Refined candidates:", len(selected))
print("\nNine-section counts:")
for name,count in counts.items():
    print(name, ":", count)
print("\nSaved:")
print((OUT/"ASK033_refined_candidates.jpg").resolve())
print((OUT/"refined_candidates.csv").resolve())
print((OUT/"phase19_report.json").resolve())
print("\nPHASE 19 COMPLETE")
