import cv2, csv, json, hashlib
import numpy as np
from pathlib import Path
from scipy.spatial import cKDTree

VIDEO = Path("research/real_image/data/network/ASK033/archive_video_20261119/allsky-20261119.mp4")
MASK = Path("research/real_image/results/ASK033/phase68_real_frame_preparation/primary_valid_pixel_mask.png")
OUT = Path("research/real_image/results/ASK033/phase117_clean_reconstruction")
OUT.mkdir(parents=True, exist_ok=True)

FRAMES = range(518, 531)
MAX_SOURCES = 3000
RADIUS = 8.0

def detect(gray, valid):
    image = gray.astype(np.float32)
    response = cv2.GaussianBlur(image, (0, 0), 1.0) - cv2.GaussianBlur(image, (0, 0), 3.0)
    usable = response[valid > 0]
    med = float(np.median(usable))
    sigma = max(1.4826 * float(np.median(np.abs(usable-med))), 1e-6)
    threshold = med + 5.0*sigma
    work = response.copy()
    work[valid == 0] = -1e9
    peaks = (work >= cv2.dilate(work, np.ones((5,5), np.uint8))-1e-6) & (work > threshold) & (valid > 0)
    ys, xs = np.where(peaks)
    values = response[ys, xs]
    if len(values) > MAX_SOURCES:
        keep = np.argpartition(values, -MAX_SOURCES)[-MAX_SOURCES:]
        xs, ys, values = xs[keep], ys[keep], values[keep]
    out = []
    for x,y,peak in zip(xs,ys,values):
        if x < 3 or y < 3 or x >= gray.shape[1]-3 or y >= gray.shape[0]-3:
            continue
        patch = response[y-2:y+3,x-2:x+3].copy()
        patch -= patch.min()
        flux = float(patch.sum())
        if flux <= 0 or not np.isfinite(flux):
            continue
        yy,xx = np.mgrid[y-2:y+3,x-2:x+3]
        cx = float((xx*patch).sum()/flux)
        cy = float((yy*patch).sum()/flux)
        # Independent integrity check at the exact integer peak.
        check = response[y-2:y+3,x-2:x+3].copy()
        check -= check.min()
        check_flux = float(check.sum())
        out.append(dict(peak_x=int(x),peak_y=int(y),x=cx,y=cy,
                        peak=float(peak),flux=flux,
                        check_flux=check_flux,
                        flux_error=abs(flux-check_flux)))
    out.sort(key=lambda p:p["peak"], reverse=True)
    return out, dict(background=med,noise_sigma=sigma,threshold=threshold)

cap = cv2.VideoCapture(str(VIDEO))
if not cap.isOpened():
    raise RuntimeError(f"Cannot open {VIDEO}")

ok, first = cap.read()
if not ok:
    raise RuntimeError("Cannot read video")
height,width = first.shape[:2]

mask = cv2.imread(str(MASK), cv2.IMREAD_GRAYSCALE)
if mask is None or mask.shape != (height,width):
    raise RuntimeError("Phase 68 mask missing or dimensions incorrect")
valid = np.where(mask > 0,255,0).astype(np.uint8)
valid = cv2.erode(valid,np.ones((7,7),np.uint8),iterations=1)

detections, stats = {}, {}
for n in FRAMES:
    cap.set(cv2.CAP_PROP_POS_FRAMES,n)
    ok, frame = cap.read()
    if not ok:
        raise RuntimeError(f"Cannot decode frame {n}")
    gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
    detections[n],stats[n] = detect(gray,valid)
    print(f"Frame {n}: {len(detections[n])} detections")

cap.release()

det_path = OUT/"phase117_detections.csv"
with det_path.open("w",newline="") as f:
    fields=["frame","peak_x","peak_y","x","y","peak","flux","check_flux","flux_error"]
    w=csv.DictWriter(f,fieldnames=fields); w.writeheader()
    for n,points in detections.items():
        for p in points:
            w.writerow({"frame":n,**p})

matches_path = OUT/"phase117_tracks.csv"
match_count=0
with matches_path.open("w",newline="") as f:
    fields=["frame_a","frame_b","source_x","source_y","destination_x","destination_y",
            "dx_px","dy_px","displacement_px","match_distance_px",
            "source_flux","destination_flux","source_peak","destination_peak"]
    w=csv.DictWriter(f,fieldnames=fields); w.writeheader()
    for a,b in zip(FRAMES,list(FRAMES)[1:]):
        pa,pb=detections[a],detections[b]
        if not pa or not pb: continue
        A=np.array([[p["x"],p["y"]] for p in pa])
        B=np.array([[p["x"],p["y"]] for p in pb])
        da,ia=cKDTree(B).query(A)
        db,ib=cKDTree(A).query(B)
        for i,(j,d) in enumerate(zip(ia,da)):
            if d>RADIUS or ib[j]!=i or db[j]>RADIUS: continue
            x1,y1=A[i]; x2,y2=B[j]
            w.writerow(dict(frame_a=a,frame_b=b,source_x=x1,source_y=y1,
                destination_x=x2,destination_y=y2,dx_px=x2-x1,dy_px=y2-y1,
                displacement_px=float(np.hypot(x2-x1,y2-y1)),
                match_distance_px=float(d),source_flux=pa[i]["flux"],
                destination_flux=pb[j]["flux"],source_peak=pa[i]["peak"],
                destination_peak=pb[j]["peak"]))
            match_count+=1

allp=[p for ps in detections.values() for p in ps]
errors=[p["flux_error"] for p in allp]
report={
 "phase":"117_clean_reconstruction",
 "video":str(VIDEO),
 "frame_numbers":list(FRAMES),
 "image_dimensions":[width,height],
 "detection_counts":{str(n):len(v) for n,v in detections.items()},
 "total_detections":len(allp),
 "mutual_matches":match_count,
 "flux_integrity_max_abs_error":max(errors,default=None),
 "flux_integrity_failures":sum(e>1e-5 for e in errors),
 "all_flux_finite":all(np.isfinite(p["flux"]) for p in allp),
 "frame_detection_statistics":stats,
 "interpretation":"Detections are point-source candidates, not confirmed stars. Tracking is not astrometric identification."
}
(OUT/"phase117_report.json").write_text(json.dumps(report,indent=2))
(OUT/"phase117_reconstruction.py").write_text(Path("/tmp/starloc_phase117.py").read_text())
sha=hashlib.sha256(VIDEO.read_bytes()).hexdigest()
(OUT/"video_sha256.txt").write_text(sha+"\n")
print("\nPHASE 117 COMPLETE")
print(json.dumps(report,indent=2))
print("\nOUTPUT:",OUT)
