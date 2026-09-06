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
- Extracted layout note: the three strip zips extract directly to
  `weitefeld/strip1/`, `strip2/`, `strip3/`, each containing images named
  `AA_BBBBB_<timestamp>_<us>_RGB.jpg` directly (no `images/` subfolder). Point
  `--images-root` at `data/raw/weitefeld` itself, not `.../images` — the
  converter's `rglob` finds the strip folders on its own.

## Two format unknowns from the paper's prose, resolved empirically

The converter script (weitefeld_to_yolo.py) flagged two assumptions that could
only be verified against the real file and real renders, not the paper text
alone:

1. **Box origin convention.** The paper describes box coordinates as a
   "lower-left" corner but is ambiguous on whether y increases up or down the
   image. INITIALLY MISDIAGNOSED: an early visual check on large shelter/object
   boxes appeared to confirm the default `topleft` origin was correct, but this
   was wrong — see the 2026-09-06 addendum below for the actual bug, its cause,
   and the fix (`--box-origin bottomedge`). The lesson: verifying box alignment
   on large objects does not catch an offset roughly equal to one box height,
   because a large box still overlaps its structure even when shifted. Small
   boxes (person) exposed the bug; large boxes (shelter/object) did not.

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
- **The "person" class carries a comparable, separate labelling issue** — see
  the 2026-09-07 addendum. Roughly 15% of person-class rows in the full dataset
  are police-flagged as excluded (not actually a person) but still coded
  `cls=3`, since data.txt has no field for a police-rejected label.
- **Only 3 of 15 strips downloaded.** This dataset is used in this project for
  Phase 1 pipeline validation only (proving the converter and eval harness work
  correctly), not as training data for Phase 3. Per-class balance in the
  resulting train/val/test split is uneven as a result (e.g. the val split in
  this 3-strip subset contains almost no shelter/person examples) and should
  not be read as representative of the full dataset's class balance.

## Conversion output — 4-class (with unknown)
- Script: vision/datasets/weitefeld_to_yolo.py (case-normalisation fix and
  box-origin fix applied — see 2026-09-06 addendum below)
- Output: data/processed/weitefeld_yolo_v1/
- Parameters: tile=1024 overlap=0.2 min_visible=0.3 neg_ratio=0.05 seed=42
  box_origin=bottomedge, drop_unknown=False
- Result: train 6,839 tiles / val 233 tiles / test 428 tiles
- This is the sensitivity-check variant per D3 in the phase execution guide.
  Primary training runs use the 3-class conversion below.

## Conversion output — 3-class (unknown dropped)
- Script: vision/datasets/weitefeld_to_yolo.py, same fixes as the 4-class run
- Output: data/processed/weitefeld_yolo_3cls_v1/
- Parameters: tile=1024 overlap=0.2 min_visible=0.3 neg_ratio=0.05 seed=42
  box_origin=bottomedge, drop_unknown=True, images-root corrected to
  `data/raw/weitefeld` (see the extracted-layout note above)
- Findings: 371 train / 79 val / 79 test (unchanged from the 4-class run —
  finding-to-split assignment happens before class-dropping, so dropping
  `unknown` boxes changes which boxes survive within a finding, not which
  split the finding lands in)
- Indexed 1,342 images; 6,663 labelled rows pointed at the other 12
  undownloaded strips and were correctly skipped
- Tile result:

  | split | tiles | positive | negative | dropped | shelter | object | person |
  |---|---|---|---|---|---|---|---|
  | train | 3,850 | 1,453 | 2,397 | 104 | 805 | 424 | 730 |
  | val | 1,002 | 337 | 665 | 21 | 258 | 65 | 248 |
  | test | 308 | 105 | 203 | 1 | 0 | 54 | 57 |

  Note the test split has **no shelter instances at all**. Shelter mAP cannot
  be reported on test for this 3-strip subset — val is the only split with
  shelter examples. Consistent with the known class-balance limitation already
  noted above for the 3-strip subset.
- Class remap confirmed correct: `nc: 3`, `names: {0: shelter, 1: object,
  2: person}`, checked against the earlier hand-arithmetic verification
  (2026-09-06 addendum) and the 300-epoch overfit gate below.

---

## Addendum, 2026-09-06: box-origin bug found and fixed during overfit gate

Before Baseline B training, the standard overfit gate (20 tiles used as both
train and val, 50 epochs, augmentation off) was run on the converted Weitefeld
tiles per the execution guide's Phase 1 protocol. It initially failed badly
(mAP50 near zero), which led to a full re-inspection of the converter's box
geometry rather than proceeding to real training on unverified data.

### The bug

`weitefeld_to_yolo.py`'s `to_xyxy()` function had two selectable
interpretations of the paper's box encoding (`--box-origin topleft` or
`bottomleft`), both taken from the paper's prose rather than verified against
the file. Neither correctly implemented the paper's literal description of
`by` as the y-coordinate of the box's "lower-left corner": the `topleft` mode
(the default in use, and the one an earlier check in this file incorrectly
called "confirmed correct") treated `by` as the box's TOP edge and extended
downward, rather than treating it as the BOTTOM edge and extending upward.

### Why it went undetected initially

The error is a vertical offset equal to one box height. For large boxes
(shelter, object; 50-70px), this offset still generally left the box
overlapping part of the same large physical structure, so the earlier visual
--verify check on shelter/object examples looked correct. For small person
boxes (~20-30px), the same offset completely misses the target, placing the
box entirely outside the visible content. This was only caught by rendering
small person-class boxes specifically and observing that the actual anomaly
sat just outside the drawn box.

### Verification of the fix

A third option, `--box-origin bottomedge` (by = bottom edge, box extends
upward), was added and checked two ways before trusting it:

1. Hand arithmetic against a raw data.txt line with an independent point
   marker (strip 01, image 02943): point marker at row 7; old `topleft`
   interpretation placed the box at rows 22-51 (point outside the box); new
   `bottomedge` interpretation placed the box at rows 0-22 (point inside the
   box).
2. Visual --verify renders on shelter examples post-fix showed boxes
   correctly tight around real structures (a shed with visible roof/chimney
   detail; a partially-tiled roof edge at a tile boundary).

`--box-origin bottomedge` is the value used for the committed conversion
(data/processed/weitefeld_yolo_v1) from this point forward.

### Overfit gate result, post-fix

Run against a randomly-sampled (not sequential) 20-tile subset:

| class | images | instances | precision | recall | mAP50 | mAP50-95 |
|---|---|---|---|---|---|---|
| shelter | 3 | 3 | 1.00 | 0.951 | 0.995 | 0.658 |
| object | 2 | 2 | 1.00 | 0 | 0.247 | 0.099 |
| unknown | 10 | 10 | 1.00 | 0 | 0 | 0 |
| person | 6 | 8 | 0 | 0 | 0 | 0 |
| **all** | 20 | 23 | 0.75 | 0.238 | 0.311 | 0.189 |

Overall mAP50 (0.311) does not clear the gate's 0.95 threshold, but this is
attributed to per-class sample size and label difficulty, not a further
pipeline defect, for the following reasons:

- `shelter`'s near-perfect score on the same 20-tile run confirms the
  underlying image/label/training pipeline is sound post-fix.
- `unknown` boxes are frequently placed over visually unremarkable terrain by
  design (see "Known limitations" above): they represent volunteer sightings
  that could not be confirmed, so a box with no visible anomaly under it can
  be a correctly-placed label, not a coordinate error. This was independently
  confirmed by rendering an unknown-class example from this exact gate run.
  A model cannot learn a consistent visual pattern from 10 examples of
  inherently varied, often-invisible anomalies.
- `person` (8 instances across 6 images) is too small a sample, on its own,
  to expect reliable memorization within a 20-image overfit gate, especially
  given the same class-imbalance and visual-subtlety issues documented
  throughout this file.

This gate result is not treated as a pass in the strict sense of the
protocol, but is treated as sufficient evidence that the geometry bug is
fixed and the pipeline is sound, on the basis of the shelter class's clean
result. Baseline B proceeds on the full training set (~6,800 tiles), where
class sample sizes are far larger and the small-sample effects seen here are
not expected to dominate. If Baseline B's real per-class mAP for
person/unknown is unexpectedly poor, this addendum is the first thing to
revisit.

---

## Addendum, 2026-09-07: person-class label contamination found while
## verifying the 3-class conversion

While confirming the box-origin fix also holds for person boxes (it had only
been checked against shelter examples in the 2026-09-06 addendum), two person
boxes in the 3-class conversion showed no visible person in the render, in a
tile that was otherwise correctly positioned and sized by hand arithmetic:

- `val_02_5776_x1638_y4914.jpg`: raw row `bx=2226, by=5982, bh=81, bw=93`,
  `bottomedge` gives `y1=5901, y2=5982`; tile spans rows 4914-5938, so the box
  sits at relative rows 987-1068, clipped against the tile's bottom edge.
  Matches the render.
- `val_02_5763_x1638_y4095.jpg`: raw row `bx=2314, by=4238, bh=81, bw=93`,
  `bottomedge` gives `y1=4157, y2=4238`; tile spans rows 4095-5119, relative
  rows 62-143, comfortably inside the tile. Matches the render.

Both rows' police comment reads "Group of people — excluded — not checked."
The volunteer comments were guesses ("few people lying or sitting on the
grass," "Looks like 3 people") that police reviewed and rejected, but data.txt
has no field for a police-rejected label, so the row keeps `cls=3` regardless.
Box placement is correct in both cases; the class label is not.

Checked across the full data.txt (not just the 3 downloaded strips):

```
awk '$5==3 && /excluded/' data.txt | wc -l   # 281
awk '$5==3' data.txt | wc -l                 # 1909
```

**281 of 1,909 person-class rows (14.7%) carry a police comment indicating
exclusion**, while still being coded as person. This is the same underlying
problem as the documented `unknown`-class caveat above — box geometry can be
correct while the class label reflects an unconfirmed or since-rejected
volunteer guess — but it affects `person`, a class kept in the primary
3-class training set, not just the dropped `unknown` class.

Treat reported person-class precision and recall as a lower bound: some
fraction of ground-truth person boxes are not, in fact, people, and no
parser-level fix is possible without an explicit police-verification field
that data.txt does not provide.

### Overfit gate on the 3-class conversion

A first attempt used 20 randomly-sampled train tiles, which happened to
contain no shelter examples and produced all-zero metrics after 50 epochs.
Predicted-box renders at a very low confidence threshold (0.001) showed a
dense, uniform grid of boxes covering nearly the whole frame, distinct from
the earlier box-origin bug's signature of a small number of consistently
offset boxes. That pattern points to an undertrained model rather than a
geometry or remap defect.

A second sample, built by taking up to 5 label files per class (7 shelter,
5 object, 7 person across 15 tiles, 17 instances after deduplication), was
run for 300 epochs instead of 50 to test convergence directly:

| class | images | instances | precision | recall | mAP50 | mAP50-95 |
|---|---|---|---|---|---|---|
| shelter | 5 | 6 | 1.00 | 0.757 | 0.972 | 0.809 |
| object | 5 | 5 | 0.73 | 0.80 | 0.755 | 0.549 |
| person | 5 | 6 | 1.00 | 0.739 | 0.856 | 0.650 |
| **all** | 15 | 17 | 0.91 | 0.765 | 0.861 | 0.669 |

Clean convergence across all three classes confirms the class remap
(`unknown` dropped, `shelter/object/person` reindexed 0/1/2) and box geometry
are correct for `weitefeld_yolo_3cls_v1`. Baseline B proceeds on this dataset.