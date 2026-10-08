# flights

One folder per flight session, named `YYYY-MM-DD_<wave>_<label>` (waves are defined in
`thesis_docs/collection_plan.md` §5). Raw footage stays on the SD card, filed under
`DCIM/DJI_001/thesis/<wave>/<session>/` (collection plan 3.1); only small derived files are tracked here.

Per session:

- `clips_summary.csv`: one row per clip (P2.4 manifest granularity)
- `stills.csv`: one row per still
- `plots/`: per-clip and overview PNGs
- `rename_map.csv`: original DJI filename, current path on the card (2026-10-07 also has the
  previous name). Stills are named `<angle>_h<height m>m_<nn>` from the pitch and height in
  their metadata.
- `pixel_size_predictions.csv` and `plots/pixel_size_vs_height.png`: from
  `vision/telemetry/pixel_size.py --out ../flights/<session>` (2026-10-08)
- `clips/`: per-frame CSVs. **Gitignored**; regenerate from the footage:

```
cd vision
uv run python telemetry/extract.py <session footage folder> --out ../flights/<session> --check
uv run python telemetry/plot.py ../flights/<session>
```
