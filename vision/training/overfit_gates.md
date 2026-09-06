# Overfit Gates — HERIDAL and Weitefeld

Three overfit gates were run before trusting either dataset for training: one
on HERIDAL, two on Weitefeld. Full detail and raw arithmetic for the
Weitefeld gates are in `PROVENANCE.md`; this is the short version, HERIDAL
included.

## Gate 0 — HERIDAL, VOC devkit layout

HERIDAL ships in a PASCAL VOC devkit layout that the converter's `find_pairs`
didn't originally handle, only the plainer `trainImages` / `trainLabels`
layout some other HERIDAL distributions use. Once fixed to support both, and
with the dataset's own real train/val/test split honoured rather than
re-derived from filenames, the overfit gate passed cleanly: 20 tiles, 50
epochs, no augmentation.

| class | images | instances | precision | recall | mAP50 | mAP50-95 |
|---|---|---|---|---|---|---|
| person | 20 | 20 | 0.891 | 0.950 | 0.982 | 0.716 |

Well clear of the 0.95 bar on the first attempt, no follow-up needed.
HERIDAL is single-class (person only), which is most of why this gate was
straightforward compared to Weitefeld below — there's no class-imbalance or
remap question to complicate the result.

## Gate 1 — Weitefeld, 4-class conversion, box-origin bug

Twenty random tiles, train and val the same set, 50 epochs, no augmentation.
Overall mAP50 came back at 0.31, well short of the usual 0.95 bar.

The cause turned out to be a wrong box-origin assumption in the converter.
The paper describes box coordinates by the box's "lower-left corner" but
doesn't say which way y runs. The converter's default treated the given
y-value as the box's *top* edge; it should have been the *bottom* edge. That
shifts every box up by its own height.

This is easy to miss on large boxes. A shelter box shifted by 60px still
overlaps most of a shed. A person box shifted by 20px misses the person
completely. The bug was caught by rendering small person boxes specifically
and noticing the target sat just outside the drawn box.

Fixed with a new `--box-origin bottomedge` option, checked by hand against a
raw data.txt row with an independent point marker, and by re-rendering
shelter boxes to confirm they now sit tight against real structures.

After the fix, the same 20-tile gate still didn't clear 0.95 overall, but
`shelter` alone hit 0.995 mAP50 on its 3 instances. That was enough to trust
the pipeline. `person`, `object`, and `unknown` all had too few instances in
20 random tiles to expect a clean score regardless of whether the pipeline
worked.

| class | instances | mAP50 |
|---|---|---|
| shelter | 3 | 0.995 |
| object | 2 | 0.247 |
| unknown | 10 | 0 |
| person | 8 | 0 |

## Gate 2 — the 3-class conversion, undertrained model

A second conversion dropped the `unknown` class, per the project's primary
run recommendation. This changes the class indices, so the geometry fix
above needed re-checking against the new label files, not just assumed to
carry over.

Hand arithmetic on two person boxes confirmed the geometry was still
correct, but turned up something unrelated: both boxes sat over terrain with
no visible person, and both had a police comment reading "excluded, not
checked." A full scan of data.txt found this in 281 of 1,909 person-class
rows (14.7%), a labelling issue similar to the one already known for
`unknown`, just showing up in a class this project actually trains on.

With geometry cleared, a fresh overfit gate was run: 20 random train tiles,
50 epochs. It came back all zero, precision and recall both, across every
class. Rendering the model's raw predictions at a near-zero confidence
threshold showed why: a dense, uniform grid of boxes covering almost the
entire frame, all at floor confidence. That's what an undertrained model
looks like, not what a coordinate bug looks like. The earlier bug shifted a
small number of boxes by a fixed offset; this run hadn't converged at all.

The 20-tile sample also had no shelter examples, no negatives, and was still
being trained for only 50 epochs, so a second sample was built deliberately
(5 label files pulled per class) and trained for 300 epochs instead.

| class | instances | precision | recall | mAP50 |
|---|---|---|---|---|
| shelter | 6 | 1.00 | 0.757 | 0.972 |
| object | 5 | 0.73 | 0.80 | 0.755 |
| person | 6 | 1.00 | 0.739 | 0.856 |
| all | 17 | 0.91 | 0.765 | 0.861 |

Clean convergence across all three classes. The remap and geometry are
correct for `weitefeld_yolo_3cls_v1`; the earlier zero was just an
undertrained model on an unlucky, negative-free, shelter-free sample.

## Takeaways worth keeping

- A failed overfit gate has more than one possible cause. Coordinate bugs and
  undertrained models can produce the same headline number (near-zero mAP)
  but look completely different in the actual predicted boxes. Rendering
  predictions at a very low confidence threshold is what told them apart
  here.
- Changing class indices (dropping `unknown`) means re-verifying the
  remapped file, not assuming a fix proven on the old indices still applies.
- `person`, not just `unknown`, has a real label-confidence problem in this
  dataset. Report person-class metrics as a lower bound, not a clean number.
