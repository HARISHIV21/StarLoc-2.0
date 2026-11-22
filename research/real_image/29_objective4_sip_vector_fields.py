from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
from astropy.wcs import WCS

R = Path("research/real_image/results/ASK033")
OUT = R / "objective4_calibration_audit/sip_vector_fields"
OUT.mkdir(parents=True, exist_ok=True)

SECTIONS = {
    "R1C2": R / "phase36_section_solutions/R1C2_custom.wcs",
    "R2C1": R / "phase36_section_solutions/R2C1_custom.wcs",
    "R3C1": R / "phase36_section_solutions/R3C1_custom.wcs",
    "R3C2": R / "phase36_section_solutions/R3C2_custom.wcs",
    "R2C2": R / "custom_plate_solutions/R2C2_custom.wcs",
}

def polynomial(coeff, u, v):
    result = np.zeros_like(u, dtype=float)
    for i in range(coeff.shape[0]):
        for j in range(coeff.shape[1]):
            result += coeff[i, j] * u**i * v**j
    return result

print("=" * 65)
print("STARLOC — SIP DISTORTION VECTOR FIELDS")
print("=" * 65)

for name, path in SECTIONS.items():
    if not path.exists():
        print(name, "WCS missing")
        continue

    wcs = WCS(fits.getheader(path), naxis=2)
    sip = wcs.sip

    if sip is None:
        print(name, "No SIP model")
        continue

    # Sample the section at regular intervals.
    x, y = np.meshgrid(
        np.linspace(1, 640, 13),
        np.linspace(1, 480, 10)
    )

    u = x - sip.crpix[0]
    v = y - sip.crpix[1]

    dx = polynomial(sip.a, u, v)
    dy = polynomial(sip.b, u, v)
    magnitude = np.hypot(dx, dy)

    fig, ax = plt.subplots(figsize=(10, 7))

    # Draw correction vectors from each sampled pixel.
    ax.quiver(
        x, y, dx, dy,
        magnitude,
        angles="xy",
        scale_units="xy",
        scale=1,
        cmap="viridis",
        width=0.003
    )

    ax.scatter(
        [sip.crpix[0]], [sip.crpix[1]],
        marker="x", s=90,
        label="SIP reference pixel"
    )

    ax.set_xlim(0, 640)
    ax.set_ylim(480, 0)
    ax.set_aspect("equal")
    ax.set_xlabel("Local pixel X")
    ax.set_ylabel("Local pixel Y")
    ax.set_title(f"{name} — SIP correction vector field")
    ax.legend()
    fig.colorbar(
        ax.collections[0],
        ax=ax,
        label="Correction magnitude (pixels)"
    )
    fig.tight_layout()

    output = OUT / f"{name}_sip_vector_field.png"
    fig.savefig(output, dpi=160)
    plt.close(fig)

    print(
        f"{name}: median={np.median(magnitude):.2f}px, "
        f"maximum={np.max(magnitude):.2f}px"
    )
    print("  Saved:", output)

print("\nVector-field plots:", OUT)
print("SIP VECTOR FIELD ANALYSIS COMPLETE")
