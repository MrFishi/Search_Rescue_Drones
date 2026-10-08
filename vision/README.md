# vision

Plain `uv` Python package, decoupled from ROS2. Run from this folder with `uv run python ...`.

## telemetry/ — DJI Lito X1 metadata to tables and plots

Pure Python, no ffmpeg or exiftool needed.

```
uv run python telemetry/extract.py <files or folders> --out ../data/processed/telemetry --check
uv run python telemetry/plot.py ../data/processed/telemetry
```

`extract.py` writes `clips/<video>.csv` (one row per frame, SRT + `djmd` merged),
`clips_summary.csv` (one row per clip, the P2.4 manifest granularity) and `stills.csv`.
`--check` compares the `djmd` track against the SRT; run it on any new drone or firmware
before trusting `djmd`. `plot.py` writes per-clip and overview PNGs to `<dir>/plots/`.
`pixel_size.py --out <dir>` predicts the box size in pixels of each prop class by height, angle
and image position (geometry in its docstring).
Field meanings and the SRT-vs-`djmd` comparison are in `thesis_docs/dev_notes.md`
(2026-10-07). Pitch is in degrees down from the horizon (90 = nadir) for stills and video.
