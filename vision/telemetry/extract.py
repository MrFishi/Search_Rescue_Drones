#!/usr/bin/env python3
"""Extract DJI telemetry from stills and videos into CSV tables.

Usage:
    uv run python vision/telemetry/extract.py <file-or-folder> [...] --out <dir> [--check]

Writes to <dir>:
    clips/<video>.csv   one row per frame (SRT + djmd merged)
    clips_summary.csv   one row per clip (manifest granularity, P2.4)
    stills.csv          one row per still
With --check, also compares the djmd track against the SRT for every clip that has both
and prints the number of mismatching frames per field (all zeros means djmd is trusted).
"""
import argparse
from pathlib import Path

import pandas as pd

from dji import check_srt_vs_djmd, clip_summary, read_clip, read_still


def collect(inputs):
    files = []
    for p in inputs:
        files += sorted(f for f in p.rglob("*") if f.is_file()) if p.is_dir() else [p]
    return files


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("inputs", nargs="+", type=Path)
    ap.add_argument("--out", type=Path, default=Path("data/processed/telemetry"))
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    files = collect(args.inputs)
    (args.out / "clips").mkdir(parents=True, exist_ok=True)

    summaries, stills = [], []
    for f in files:
        ext = f.suffix.lower()
        if ext == ".mp4":
            df = read_clip(f)
            if df is None:
                print(f"  - {f.name}: no SRT and no djmd track, skipped")
                continue
            df.to_csv(args.out / "clips" / f"{f.stem}.csv", index=False)
            summaries.append(clip_summary(df, f))
            print(f"  clip  {f.name}: {len(df)} frames")
            if args.check:
                res = check_srt_vs_djmd(f)
                print(f"        check: {res if res else 'needs both SRT and djmd'}")
        elif ext in (".jpg", ".jpeg"):
            stills.append(read_still(f))

    if summaries:
        pd.DataFrame(summaries).to_csv(args.out / "clips_summary.csv", index=False)
    if stills:
        pd.DataFrame(stills).to_csv(args.out / "stills.csv", index=False)
    print(f"{len(summaries)} clips, {len(stills)} stills -> {args.out}")


if __name__ == "__main__":
    main()
