#!/usr/bin/env python3
"""Predict the box size in pixels of each prop class, by height, angle and image position.

Usage:
    uv run python telemetry/pixel_size.py --out ../flights/<session>

Writes <out>/pixel_size_predictions.csv and <out>/plots/pixel_size_vs_height.png.

Geometry: Lito X1 stills, 4032 x 3024. From the 82.1 deg diagonal, HFOV is about 69.5 deg and
f is about 2906 px. For a camera pitched down by `pitch` and an object at ray angle `theta` below
the horizon, an object of ground size L x W (cm) at height h covers
    across the view direction: f * L * sin(theta) / h
    along the view direction:  f * L * sin(theta)^2 / h
(foreshortened). At nadir both are f * L / h. Checked against detected backpacks in the
2026-10-08 stills: measured / predicted was 1.07-1.09 at nadir (3-15 m) and 1.06 at 45 deg.

Object sizes are bounding boxes in cm, taken from the 3 m nadir stills (bottle, sunglasses,
backpack) and from 5-10 m nadir person boxes. `person_lying` is a typical-size guess, not
measured. Replace them when real prop measurements exist.
"""
import argparse
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

F = 2906.0                                   # focal length, px (stills, 4032 wide)
HALF = math.atan(1512 / F)                   # half the vertical field of view
PITCH = math.radians(45)
SIZES_CM = {                                 # (long, short) box size
    "backpack": (64, 50),
    "water_bottle": (23, 6.5),
    "sunglasses": (14.5, 8.5),
    "person_sit_stand": (95, 85),
    "person_lying": (165, 95),
}
HEIGHTS = [3, 5, 7.5, 10, 15]
COLOURS = {"backpack": "#1b6ca8", "water_bottle": "#2a9d8f", "sunglasses": "#d1495b",
           "person_sit_stand": "#e9a23b", "person_lying": "#6b6b6b"}


def predictions():
    rows = []
    for cls, (long_cm, short_cm) in SIZES_CM.items():
        for h in HEIGHTS:
            rows.append(dict(cls=cls, angle="nadir", pos="all", h_m=h, orient="any",
                             long_px=F * long_cm / 100 / h, short_px=F * short_cm / 100 / h))
            for pos, theta in (("far_edge", PITCH - HALF), ("centre", PITCH), ("near_edge", PITCH + HALF)):
                s = math.sin(theta)
                for orient, scale in (("long axis across", s), ("long axis along", s * s)):
                    rows.append(dict(cls=cls, angle="obl45", pos=pos, h_m=h, orient=orient,
                                     long_px=F * long_cm / 100 * scale / h,
                                     short_px=F * short_cm / 100 * (s * s if orient == "long axis across" else s) / h))
    return pd.DataFrame(rows).round(1)


def plot(out):
    fig, ax = plt.subplots(1, 2, figsize=(12, 4.8), constrained_layout=True, sharey=True)
    hh = np.linspace(3, 15, 50)
    for a, (theta, title) in zip(ax, ((PITCH, "45° camera, image centre"),
                                      (PITCH - HALF, "45° camera, far (top) edge"))):
        s = math.sin(theta)
        for cls, (long_cm, _) in SIZES_CM.items():
            a.fill_between(hh, F * long_cm / 100 * s * s / hh, F * long_cm / 100 * s / hh,
                           color=COLOURS[cls], alpha=0.25)
            a.plot(hh, F * long_cm / 100 * s / hh, color=COLOURS[cls], label=cls)
        a.axhline(8, color="k", ls="--", lw=1)
        a.text(14.9, 9, "8 px", ha="right", fontsize=8)
        a.axvspan(5, 10, color="grey", alpha=0.12)
        a.set_yscale("log")
        a.set_xlabel("height above ground (m)")
        a.set_title(title)
    ax[0].set_ylabel("long side of box (px)")
    ax[0].legend(fontsize=8, loc="upper right")
    fig.savefig(out, dpi=130)
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    (args.out / "plots").mkdir(parents=True, exist_ok=True)
    predictions().to_csv(args.out / "pixel_size_predictions.csv", index=False)
    plot(args.out / "plots" / "pixel_size_vs_height.png")
    print(f"-> {args.out}")


if __name__ == "__main__":
    main()
