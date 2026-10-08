#!/usr/bin/env python3
"""Plot telemetry tables written by extract.py.

Usage:
    uv run python vision/telemetry/plot.py <dir written by extract.py>

Writes PNGs to <dir>/plots/:
    <clip>.png     altitude + gimbal pitch, ISO + shutter, colour temperature, GPS track
    overview.png   gimbal pitch against time for every clip, and stills altitude vs pitch
"""
import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

EARTH_R = 6371000.0
ALT, PITCH, ISO, SHUT = "#1b6ca8", "#d1495b", "#2a9d8f", "#e9a23b"


def local_xy(df):
    """GPS to metres east/north of the first fix."""
    x = np.radians(df["lon"] - df["lon"].iloc[0]) * EARTH_R * np.cos(np.radians(df["lat"].iloc[0]))
    y = np.radians(df["lat"] - df["lat"].iloc[0]) * EARTH_R
    return x, y


def plot_clip(csv, out):
    df = pd.read_csv(csv)
    fig = plt.figure(figsize=(12, 7.5), constrained_layout=True)
    gs = fig.add_gridspec(3, 2, width_ratios=[2.2, 1])
    ax1, ax2, ax3 = (fig.add_subplot(gs[i, 0]) for i in range(3))
    axm = fig.add_subplot(gs[:, 1])
    t = df["t_s"]

    ax1.plot(t, df["rel_alt_m"], color=ALT)
    ax1.set_ylabel("height above take-off (m)", color=ALT)
    twin = ax1.twinx()
    twin.plot(t, df["pitch_deg"], color=PITCH)
    twin.set_ylabel("gimbal pitch (deg down)", color=PITCH)
    twin.set_ylim(-45, 95)

    ax2.plot(t, df["iso"], color=ISO)
    ax2.set_ylabel("ISO", color=ISO)
    twin2 = ax2.twinx()
    twin2.plot(t, 1 / df["shutter_s"], color=SHUT)
    twin2.set_ylabel("shutter (1/s)", color=SHUT)

    ax3.plot(t, df["ct_k"], color="#6b6b6b")
    ax3.set_ylabel("colour temp (K)")
    ax3.set_xlabel("time (s)")

    x, y = local_xy(df)
    sc = axm.scatter(x, y, c=t, s=3, cmap="viridis")
    axm.set_aspect("equal")
    axm.set_xlabel("east of start (m)")
    axm.set_ylabel("north of start (m)")
    fig.colorbar(sc, ax=axm, label="time (s)", shrink=0.7)
    fig.suptitle(Path(csv).stem)
    fig.savefig(out, dpi=130)
    plt.close(fig)


def plot_overview(tel, out):
    fig, (a, b) = plt.subplots(1, 2, figsize=(12, 4.8), constrained_layout=True)
    clips = sorted((tel / "clips").glob("*.csv"))
    stills = tel / "stills.csv"
    for csv in clips:
        df = pd.read_csv(csv)
        a.plot(df["t_s"], df["pitch_deg"], label=csv.stem, lw=1.4)
    if clips:
        a.set_xlabel("time (s)")
        a.set_ylabel("gimbal pitch (deg down)")
        a.legend(fontsize=8)
    elif stills.exists():
        # stills-only session: height over the session, coloured by angle
        s = pd.read_csv(stills)
        s["t"] = pd.to_datetime(s["time_local"], format="%Y:%m:%d %H:%M:%S")
        for ang, col in (("nadir", ALT), ("oblique45", PITCH)):
            sel = s[s["pitch_deg"] > 85] if ang == "nadir" else s[s["pitch_deg"] <= 85]
            a.scatter(sel["t"], sel["rel_alt_m"], s=14, color=col, label=ang)
        a.set_xlabel("time")
        a.set_ylabel("height above take-off (m)")
        a.legend(fontsize=8)
        a.tick_params(axis="x", rotation=30)
    if stills.exists():
        s = pd.read_csv(stills).dropna(subset=["rel_alt_m", "pitch_deg"])
        b.scatter(s["pitch_deg"], s["rel_alt_m"], color=ALT)
        b.set_xlabel("gimbal pitch (deg down)")
        b.set_ylabel("height above take-off (m)")
        b.set_title("stills")
    fig.savefig(out, dpi=130)
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("tel", type=Path, help="directory written by extract.py")
    args = ap.parse_args()
    plots = args.tel / "plots"
    plots.mkdir(exist_ok=True)
    for csv in sorted((args.tel / "clips").glob("*.csv")):
        plot_clip(csv, plots / f"{csv.stem}.png")
        print(f"  {csv.stem}.png")
    plot_overview(args.tel, plots / "overview.png")
    print(f"-> {plots}")


if __name__ == "__main__":
    main()
