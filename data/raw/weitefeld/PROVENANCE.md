# Weitefeld Dataset — Provenance

## Source
- Paper: Nathan, R.J.A.A., Gessner, M., Ozkan, N., Bock, M., Youssef, M., Mews, M.,
  Piltz, B., Berger, R., Bimber, O. "An aerial color image anomaly dataset for
  search missions in complex forested terrain." Scientific Data 13:747 (2026).
  DOI: 10.1038/s41597-026-07101-w
- Preprint: arXiv:2507.15492
- Data host: Zenodo record 15848419
- URL: https://zenodo.org/records/15848419
- Project page: https://weitefeld.cg.jku.at/
- Institutions: Johannes Kepler University Linz (Institute of Computer Graphics),
  German Aerospace Center (DLR)

## Background
Collected during the real search operation for a fugitive suspect following a
2025 triple homicide near Weitefeld, Germany. DLR flew a research aircraft over a
25 km^2 forested area on 27 April 2025. Findings were crowd-sourced from 160
volunteers reviewing the imagery, then reviewed by police for the ground-truth
comment field. Labelling is subjective by design; see "Known limitations" below.

## Files downloaded (3 of 15 strips, chosen as the smallest for Phase 1 pipeline
validation — full coverage is not required for this stage)

| File | Size | MD5 | Verified |
|---|---|---|---|
| data.txt | 4,414,586 bytes | af4fee2a2cf10014a6ab64fcf0300b21 | match |
| strip1.zip | 4,420,878,778 bytes | 859a78628c2a08e04aad2704aff90fce | match |
| strip2.zip | 4,604,335,196 bytes | f433caffbb9cd73390be72bb946eb86d | match |
| strip3.zip | 5,962,523,435 bytes | 585006cae744f9e0afeab9305a0a7e63 | match |
| README.md (Zenodo) | 2,823 bytes | not checked | — |

All four checksums verified against Zenodo's published record metadata on
download, no corruption.

## Download
- Date: 2026-09-05
- Downloaded via: aria2c / wget, WSL2 Ubuntu 24.04

## Content
- data.txt: 34,424 peer-reviewed core entries (the "core" dataset; later rows in
  the full file are community additions and are excluded via --core-only in the
  full-download case, though this run used the 34,424-row core file directly)
- Classes: 0 unknown, 1 shelter, 2 object, 3 person
- Strips 1-3 only: 1,342 images indexed on disk; 8,060 labelled entries in
  data.txt point at images from the other 12 strips, not downloaded, and were
  correctly skipped by the converter (expected, not an error)

## Two format unknowns from the paper's prose, resolved empirically

The converter script (weitefeld_to_yolo.py) flagged two assumptions that could
only be verified against the real file and real renders, not the paper text
alone:

1. **Box origin convention.** The paper describes box coordinates as a
   "lower-left" corner but is ambiguous on whether y increases up or down the
   image. Resolved: default topleft origin confirmed correct by visual
   inspection (--verify renders) — boxes sit directly on visible structures
   (e.g. a shelter box anchored at the base of a visible shed roof), with no
   sign of the vertical mirroring a wrong convention would produce.

2. **Finding-grouping heuristic.** data.txt has no explicit finding-ID column.
   The script groups back-projections into findings by hashing the volunteer +
   police comment text. Initial run detected 606 unique findings against the
   paper's reported ~405. Comment-text inspection showed case-variant
   duplicates ("Shelter" vs "shelter", "Possible shelter" vs "possible
   shelter") artificially fragmenting single findings into two. Fixed by
   normalising comment text (lowercase, whitespace-collapsed) before hashing.
   Re-run after the fix: 593 unique findings, an improvement but still above
   405.

## Known limitations (for thesis writeup, not bugs in this pipeline)

- **Comment-based finding grouping is a proxy, not ground truth.** Generic,
  frequently reused phrasing (e.g. "human" appears 1,976 times, "Shelter"/
  "shelter" combined ~2,600 times in the 3-strip subset) means distinct
  physical objects described with identical generic text will hash to the same
  finding key and be merged, while genuinely different wording for the same
  object can still fragment it into two. The case-normalisation fix in this
  converter mitigates the second failure mode only. Neither failure mode can be
  fully resolved without an explicit finding-ID column, which data.txt does not
  provide. Train/val/test independence for Weitefeld should be described as
  best-effort, not guaranteed, on this basis.
- **The "unknown" class (0) encodes labeller uncertainty by design.** Many
  unknown-class boxes sit over visually unremarkable terrain with no obvious
  object present. This is expected: unknown is the bucket for volunteer
  sightings that could not be confirmed, so the box's location can be correct
  even where nothing is visibly identifiable in the crop. This is a property of
  the crowd-sourced label, not a coordinate error.
- **Only 3 of 15 strips downloaded.** This dataset is used in this project for
  Phase 1 pipeline validation only (proving the converter and eval harness work
  correctly), not as training data for Phase 3. Per-class balance in the
  resulting train/val/test split is uneven as a result (e.g. the val split in
  this 3-strip subset contains almost no shelter/person examples) and should
  not be read as representative of the full dataset's class balance.

## Conversion output
- Script: vision/datasets/weitefeld_to_yolo.py (case-normalisation fix applied,
  see above)
- Output: data/processed/weitefeld_yolo_v1/
- Parameters: tile=1024 overlap=0.2 min_visible=0.3 neg_ratio=0.05 seed=42
  box_origin=topleft
- Result: train 6,825 tiles / val 233 tiles / test 422 tiles
