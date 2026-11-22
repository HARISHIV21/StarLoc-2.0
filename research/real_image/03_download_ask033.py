from pathlib import Path
from urllib.request import Request, urlopen
from datetime import datetime, timezone
import json
import cv2
import numpy as np

OUT = Path("research/real_image/data/network/ASK033")
OUT.mkdir(parents=True, exist_ok=True)

URL = (
    "https://allskykamera.space/imageProxy.php"
    "?cam=ASK033&type=image&variant=auto&t=1795202423"
)

print("\nSTARLOC 2.0 — REAL IMAGE DOWNLOAD")
print("=" * 55)

request = Request(
    URL,
    headers={"User-Agent": "StarLoc-2.0 academic research"}
)

with urlopen(request, timeout=60) as response:
    content = response.read()
    content_type = response.headers.get("Content-Type", "")
    status = response.status
    headers = dict(response.headers)

print("HTTP status:", status)
print("Content type:", content_type)
print("Downloaded bytes:", len(content))

if status != 200:
    raise SystemExit("Download failed: unexpected HTTP status")

if not content_type.lower().startswith("image/"):
    (OUT / "download_response.txt").write_bytes(content)
    raise SystemExit(
        "The server did not return an image. "
        "Response saved for inspection."
    )

image_path = OUT / "ASK033_live_original.jpg"
image_path.write_bytes(content)

image = cv2.imdecode(
    np.frombuffer(content, dtype=np.uint8),
    cv2.IMREAD_COLOR
)

if image is None:
    raise SystemExit("OpenCV could not decode the downloaded image.")

height, width = image.shape[:2]
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

timestamp = 1795202423
utc_time = datetime.fromtimestamp(timestamp, timezone.utc)

metadata = {
    "camera_id": "ASK033",
    "location": "Miesenbach, Austria",
    "latitude_deg": 47.834,
    "longitude_deg": 16.005,
    "timezone": "Europe/Vienna",
    "image_source_url": URL,
    "image_type": "individual live camera image",
    "timestamp_query_parameter_unix": timestamp,
    "timestamp_utc": utc_time.isoformat(),
    "http_status": status,
    "content_type": content_type,
    "file": image_path.name,
    "width_px": width,
    "height_px": height,
    "channels": int(image.shape[2]),
    "gray_min": int(gray.min()),
    "gray_max": int(gray.max()),
    "gray_mean": float(gray.mean()),
    "gray_std": float(gray.std()),
    "file_size_bytes": len(content)
}

(OUT / "image_metadata.json").write_text(
    json.dumps(metadata, indent=2),
    encoding="utf-8"
)

# Save a grayscale copy for image-processing experiments.
cv2.imwrite(str(OUT / "ASK033_live_grayscale.png"), gray)

print("\nIMAGE VALIDATION")
print("Dimensions:", width, "x", height)
print("Channels:", image.shape[2])
print("Pixel range:", int(gray.min()), "to", int(gray.max()))
print("Mean intensity:", round(float(gray.mean()), 3))
print("Intensity standard deviation:", round(float(gray.std()), 3))
print("File size:", round(len(content) / 1024, 2), "KB")
print("Timestamp parameter (UTC):", utc_time.isoformat())

print("\nSAVED FILES")
print(image_path.resolve())
print((OUT / "ASK033_live_grayscale.png").resolve())
print((OUT / "image_metadata.json").resolve())

print("\nDOWNLOAD AND IMAGE VALIDATION COMPLETE")
