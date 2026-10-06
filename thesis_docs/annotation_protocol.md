# Annotation protocol: own bush/HPI dataset (P0.2 / P2.5)

Status: draft 2026-10-07, not yet signed off. This doc fills Section 4 of
`hpi_taxonomy.md`. Rules marked [confirm] are proposed defaults the author still
needs to accept. Once annotation starts the protocol is frozen like the class
list, and any later change means re-checking every annotated session.

Citations use `[cite:key]` for keys already in `thesis_writeups/references.bib`
and `[new:N]` for the sources in Section 9 that still need adding through Zotero.

## 1. General rules (all 11 classes)

### 1.1 Exhaustive labelling

Every instance of every class in a frame gets a box. A missed instance teaches
the model that the object is background. COCO gives this its own pipeline stage,
where annotators mark every instance of each category present
[cite:lin2014coco].

### 1.2 Box extent: full (amodal) box

An occluded object keeps the box of its full physical extent, with the hidden
part inferred (HARD RULE 6). CrowdHuman does the same for its full-body boxes:
the annotator completes the invisible part and draws the full box [new:2].
PASCAL VOC and COCO box only the visible extent [new:1] [cite:lin2014coco], so
our boxes are not directly comparable to theirs, and the methods section should
say so. We use the full box because a visible-only box shrinks as occlusion
grows, which would turn the occlusion experiment into a small-object experiment.

To infer the hidden extent, use the visible part plus the object's known size
from the placement log (Section 6). If the extent can't be estimated to within
about a quarter of the box size, set `difficult` (1.6).

### 1.3 Tightness

Box edges sit on the outermost pixel of the object or of its inferred extent.
Shadows are excluded, as in NOMAD's person boxes [cite:bernal2024nomad]. Draw
at full image resolution, zoomed in, and never on a downscaled view.

### 1.4 Box what the image shows

The annotator knows where every object was placed, which biases them toward
boxing things they can't actually see. Follow POP's two-pass rule
[cite:pop_infrared2025]:
1. Annotate the frame from the image alone.
2. Check the placement log for anything missed. Re-inspect those spots and add a
   box only if the object can be identified by eye in the image.

A placed object that can't be identified gets no box. Record it as
`present_not_visible` in the placement log. Those records show how often deep
canopy hides an object completely, which is useful for the occlusion analysis,
but they must stay out of the labels.

### 1.5 Minimum size

Box any identifiable object (1.4), whatever its pixel size. Below about 8 px on
the short side, also set `difficult` [confirm; tune the threshold on Wave 0
footage]. TinyPerson labels aerial persons as small as 2 to 20 px [new:3], so
pixel size alone is no reason to skip a box.

### 1.6 Attributes (CVAT, per box)

| Attribute | Values | Rule |
|---|---|---|
| `visibility` | `none_occl` / `partial` / `heavy` | 0%, 1-50% or over 50% of the object hidden. These are VisDrone's bins [new:4]; NOMAD uses ten finer ones [cite:bernal2024nomad] |
| `difficult` | bool | Identifiable but ambiguous: unclear class, unclear extent (1.2), or under the 1.5 size. PASCAL VOC excludes such objects from scoring [new:1] |
| `truncated` | bool | Object cut by the frame edge. Clip the box to the image |

An object more than 50% outside the frame gets no box, matching VisDrone's
evaluation cut-off [new:4]. POP skips every edge object
[cite:pop_infrared2025], which throws away more data than we need to.

The YOLO export drops attributes. Keep the CVAT/COCO export as the master copy
and have the eval harness read `difficult` and `visibility` from it [confirm:
train on `difficult` boxes, and report eval both with and without them].

### 1.7 Worn items

Anything a person wears or holds is part of their `person` box and gets no box
of its own. `emergency_blanket` is the exception [confirm], see Section 3. In
SAR an HPI is a trace found apart from the person, and boxing every worn shirt
would swamp the HPI classes with `person` co-occurrence.

### 1.8 Class precedence

A specific class beats a general one. Anything that fits a trained class is
never `discarded_gear`.

### 1.9 Negatives

Frames with no objects keep an empty label file. Don't drop them (P2.3).

## 2. Primary and trained classes

| Class | Positive | Not this class | Box notes |
|---|---|---|---|
| `person` | Any human in any pose: standing, sitting, lying, crouched, face-down, partly under vegetation. SARD stages a similar pose range for SAR [new:5] | Mannequins, clothing laid out in a body shape (box as `clothing_item`) | Full amodal body box (1.2). Two overlapping people get two boxes |
| `backpack` | Backpack, daypack, duffel, stuff sack or dry bag that isn't being worn | Plastic shopping bag (`discarded_gear`), worn pack (1.7) | Include straps lying flat next to the bag |
| `water_bottle` | Rigid or soft bottle, canteen, hydration bladder | Cans, cups, food packaging (`discarded_gear`) | Include the cap |
| `footwear` | Boot, shoe or sandal that isn't being worn | Socks (`clothing_item`) | One box per shoe. A touching pair that can't be separated gets one box plus `difficult` |
| `clothing_item` | Jacket, shirt, pants, hat, cap, gloves, socks or scarf that isn't being worn | Blankets (`emergency_blanket`), tarps (`discarded_gear`) | Box the whole garment, including sleeves draped over a branch |
| `sunglasses` | Any eyewear that isn't being worn | n/a | Most instances will probably be `difficult` at altitude. Check the Wave 0 counts before relying on this class [confirm] |
| `flashlight_headlamp` | Handheld torch or headlamp, on or off | Lanterns, phones (`discarded_gear`) | Include the headlamp strap |

## 3. Held-out classes (never trained, HARD RULE 3)

These are annotated in CVAT under their own names so the D-arm and VLM
evaluation has ground truth. The export script drops them from every training
manifest, and the seal assert (P1.4-P1.6) checks that it did.

| Class | Positive | Not this class | Box notes |
|---|---|---|---|
| `trail_marker_tape` | Flagging tape tied to vegetation or lying loose | Clothing, rope (`discarded_gear`) | One box per tie point, covering knot and tails |
| `discarded_gear` | Man-made outdoor equipment not covered by another class: tent, tarp, sleeping bag or mat, rope, pot, stove, packaging | Anything in a trained class (1.8) | One box per item. A pitched tent counts here [confirm, or rename the class `gear_shelter`] |
| `campfire_remains` | Ash and charcoal patch, with or without a stone ring (staged cold) | Burnt ground with no ring and no charcoal pile | Box ash, charcoal and ring together as one instance |
| `emergency_blanket` | Mylar blanket in any colour, spread, crumpled or draped | Tarp (`discarded_gear`) | Boxed even when wrapped around a person [confirm]. A mylar blanket is a strong SAR cue, which is why it is the exception to 1.7 |

## 4. Video (temporal arm only)

- Annotate each object as a track. Draw keyframes, let CVAT interpolate between
  them, and correct drift at each keyframe. VATIC showed that sparse keyframes
  with interpolation are an efficient way to label video [new:6].
- Put a keyframe at least every 10-15 frames and at every occlusion change, when
  an object enters or leaves cover. Mark the object "outside" in CVAT while it
  can't be identified (1.4), so no interpolated box sits over empty ground.
- Keep one track ID per physical object across the clip.
- Tag `provenance = dji_video`. Video never enters detector training (P2.5).

## 5. Quality checks

A second annotator labels 50 frames independently, stratified by class and
visibility (P2.5). If nobody else is available, the author re-labels the same
frames blind at least 3 weeks later. Report:
- matched-box mean IoU, matching at IoU >= 0.5
- class agreement rate on matched boxes
- missed-instance rate in each direction

PASCAL's expert annotators agree at 88% mIoU [new:7], and small, occluded aerial
objects will likely score lower. [confirm: pass mark of 0.75 matched mIoU and at
least 90% class agreement. Below that, revise the protocol and re-label.]
Weitefeld's crowd-sourced findings were checked in a review pass after
collection [cite:nathan2026weitefeld]. A measured agreement figure lets our
methods section answer the label-quality question that pass leaves open.

Before any session's labels are used, run the converter's `--verify` render
(CLAUDE.md conventions).

## 6. Placement log fields annotation depends on

Each placement records `scene_id`, `placement_id`, class, physical size (cm),
staged occlusion (`exposed` / `partial` / `deep`) and `present_not_visible` per
frame-set. Staged occlusion is the experimental condition and `visibility` is
what the annotator saw. Keep both.

## 7. Open decisions

1. Split unit. Each frame shows a whole scene of 3-5 placements, so the
   smallest leak-free split unit is the scene. Scenes or sites go to one split
   (HARD RULE 1). Confirm this, then update `collection_plan.md`.
2. Held-out objects in training images. A held-out object sitting unlabelled in
   a training frame gets learned as background. The manifest stays sealed, but
   the held-out result is biased. One option is to stage held-out classes only
   in scenes with no trained classes. The other is to send every frame
   containing a held-out object to the held-out eval pool. This needs a decision
   before Wave 1.
3. All [confirm] items above.

## 8. Precedent summary

| Choice | Ours | Precedent |
|---|---|---|
| Box extent | Full / amodal | CrowdHuman full box [new:2]; VOC and COCO use visible extent [new:1] [cite:lin2014coco] |
| Occlusion attribute | 3 bins | VisDrone [new:4]; NOMAD uses 10 bins [cite:bernal2024nomad] |
| Hard cases | `difficult` flag, kept | VOC `difficult` [new:1]; TinyPerson `uncertain` / `ignore` [new:3] |
| Known-location bias | Two passes, identifiable only | POP [cite:pop_infrared2025] |
| Video | Keyframes + interpolation | VATIC [new:6] |
| Agreement | 50-frame IoU + class check | PASCAL 88% mIoU [new:7] |

## 9. New sources (to add to Zotero; PDFs in `papers/`)

1. M. Everingham, L. Van Gool, C. K. I. Williams, J. Winn, A. Zisserman, "The
   PASCAL Visual Object Classes (VOC) Challenge," *IJCV*, 88(2):303-338, 2010.
   doi:10.1007/s11263-009-0275-4. `papers/pascal_voc_everingham2010.pdf`
2. S. Shao, Z. Zhao, B. Li, T. Xiao, G. Yu, X. Zhang, J. Sun, "CrowdHuman: A
   Benchmark for Detecting Human in a Crowd," arXiv:1805.00123, 2018.
   `papers/crowdhuman_shao2018_1805.00123.pdf`
3. X. Yu, Y. Gong, N. Jiang, Q. Ye, Z. Han, "Scale Match for Tiny Person
   Detection," *WACV*, pp. 1246-1254, 2020. doi:10.1109/WACV45572.2020.9093394.
   `papers/tinyperson_scalematch_yu2020_1912.10664.pdf`
4. P. Zhu, L. Wen, D. Du, X. Bian, H. Fan, Q. Hu, H. Ling, "Detection and
   Tracking Meet Drones Challenge," *IEEE TPAMI*, 44(11):7380-7399, 2022.
   doi:10.1109/TPAMI.2021.3119563. `papers/visdrone_zhu2021_2001.06303.pdf`
5. S. Sambolek, M. Ivasic-Kos, "Automatic Person Detection in Search and Rescue
   Operations Using Deep CNN Detectors," *IEEE Access*, 9:37905-37922, 2021.
   doi:10.1109/ACCESS.2021.3063681. Open access; PDF not downloaded.
6. C. Vondrick, D. Patterson, D. Ramanan, "Efficiently Scaling up Crowdsourced
   Video Annotation," *IJCV*, 101(1):184-204, 2013.
   doi:10.1007/s11263-012-0564-1. `papers/vatic_vondrick2013_ijcv.pdf`
7. D. P. Papadopoulos, J. R. R. Uijlings, F. Keller, V. Ferrari, "Extreme
   Clicking for Efficient Object Annotation," *ICCV*, pp. 4940-4949, 2017.
   doi:10.1109/ICCV.2017.528.
   `papers/extreme_clicking_papadopoulos2017_1708.02750.pdf`
