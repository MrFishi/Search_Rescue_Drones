# Phase 2 Collection Plan (own bush/HPI dataset)

**Status: revised 2026-10-08, still a draft.** Targets, waves and rules below are
proposed. Items marked **[decide]** need the author's call before they bind. Class
list is locked in `hpi_taxonomy.md`. Guide references: `phase_execution_guide.md`
P2.3 (session design), P2.4 (metadata), P2.6 (targets, tracker), P2.7 (Arducam batch),
P2.8 (assembly), and the temporal-video section near line 1195.

Revision 2026-10-08 (what changed and why):

- Altitude bands and camera angles are now explicit. The old plan left them open and
  the 2026-10-07 test flight used 20/40/60 m, which is far above the 5-10 m the thesis
  is about (Section 3).
- Person and HPI footage are separated by session type, scene and folder (Section 3).
- The site-level test split and the held-out seal are designed in from the start, not
  added at assembly (Section 4).
- Wave 0 now has exit criteria; Wave 1 has a session matrix and checkpoints; the
  Arducam validation batch is its own wave (Section 5).
- Consent and ethics are out of scope for this plan (Section 7).

## 1. Constraints (confirmed 2026-10-06)

| Item | Value |
|---|---|
| Drone | DJI Lito X1, 3 batteries (Fly More Combo) |
| Cadence | 3-5 sessions/week |
| Sites | 3-5 bush sites (plan for 4) |
| Person subjects | The author and thesis peers (volunteers) |
| Session length | ~2 h planned in advance (P2.3) |
| Main-drone camera | Fixed at 45° down (decided 2026-10-08); a servo to switch 45°/90° is a possible later retrofit |
| Main-drone altitude | Held constant above the ground by a ToF sensor, 5-10 m (author, 2026-10-08) |

Not yet verified (see Section 8): per-battery flight time, flight-log export, exact
HFOV/VFOV.

## 2. Targets

The guide floor is the minimum; the proposed target adds margin so a bad session
or a failed annotation check does not drop a class below the floor.

| Class tier | Unit | Guide floor | Proposed target |
|---|---|---|---|
| Trained HPI (6 classes) | unique placements | 40 | 60 |
| | annotated boxes (stills) | 400 | 600 |
| | sessions / sites | 5 / 3 | 6 / 4 |
| Held-out HPI (4 classes) | unique placements | 25 | 40 |
| | annotated boxes (stills) | 250 | 400 |
| | sessions / sites | 4 / 3 | 5 / 4 |
| `person` | distinct poses/positions | 30 | 45 |
| | annotated boxes (stills) | 400 | 600 |
| | sessions / sites | 4 / 3 | 5 / 4 |
| Slow-pass video clips | clips | 15 | 20+, >=3 sites |

Boxes per placement: 600 boxes from 60 placements means about 10 stills per
placement; the shot list in Section 3 gives about 8 per scene plus overlap between
scenes. All stills of one placement stay in one split (HARD RULE 1).

Terms: a **placement** is one object at one spot in one session (the unit of
independence). A **scene** is one staged arrangement of 3-5 placements shot together
(the smallest leak-free split unit, see Section 4). A **session** is one outing.

## 3. How a session is shot

### 3.1 Session and scene types (keeps person and HPI footage separate)

Every scene gets exactly one type, recorded in the log and the manifest.

| Type | Contains | Used for |
|---|---|---|
| `T` trained objects | 3-5 trained-class objects, no people, no held-out objects | detector training / val / test |
| `H` held-out objects | 3-5 held-out-class objects, no people, no trained-class objects | held-out eval only (D arm, VLM). Never trained |
| `P` person | one volunteer in a pose, no staged objects | `person` class |
| `C` co-occurrence | one volunteer plus trained-class objects 1-3 m away | `person` + HPI together |
| `N` negative | empty bush, logs, rocks, shadow patches, vaguely person-shaped things | negatives |
| `V` video pass | a slow pass over `T` or `P`/`C` scenes | temporal arm only (`dji_video`) |

Waves 0 and 1 are object-only (`T`, `H`, `N`, `V` over objects). `P` and `C` start in
Wave 2. Held-out scenes contain no trained-class objects and no people, so no held-out
object ever appears unlabelled in a training frame (resolves
`annotation_protocol.md` 7.2, HARD RULE 3) **[decide]**. The cost: the held-out pool
has no person-plus-held-out scenes; state this as a limitation.

Storage on the SD card: `DCIM/DJI_001/thesis/<wave>/<session>/` with subfolders
`trained/`, `heldout/`, `person/`, `negatives/`, `video/`. HPI and person footage are
then physically separate from the moment they are offloaded.

### 3.2 Altitude bands and camera angle

**Camera angle: 45° only** (decided 2026-10-08). It covers a wide range of heights and
distances in one frame. No 90° stills are collected for training; keep a small nadir
reference set only if a use for it appears. If a 45°/90° servo is retrofitted later, that
is new data at the new angle, not a reason to collect it now. Pitch is logged per frame
from `djmd` and per still from XMP, so use the logged value, not the nominal one (the
2026-10-08 "45°" stills read 44.9-45.7°).

**Heights are above ground (AGL).** The main drone holds a constant 5-10 m above the
ground with a ToF sensor, and collection is flown in the same bands from a take-off point
at the scene's own ground level. On level ground `rel_alt` is then AGL (`agl_method =
level_ground`). The slope check is dropped (author, 2026-10-08): the deployed drone always
flies 5-10 m from the ground, so there is no uneven-ground case to calibrate. Open
question for the deployed system, not for collection: a downward ToF over bush reads the
vegetation top, not the forest floor; state which one "5-10 m" refers to.

**Bands (provisional [decide]): 5, 7.5 and 10 m AGL.** The 2026-10-08 sweep covered 3-15
m; `flights/2026-10-08_wave0_pilot/pixel_size_predictions.csv` has the predicted box size per
class. Geometry (82.1° diagonal, 4:3 stills, f = 2906 px) was checked against detected
backpacks: measured over predicted size was 1.07-1.09 at every nadir height from 3 to 15 m
and 1.06 overall at 45° (IQR 0.98-1.17), so the scaling holds. Long side of the box in
pixels at 45°, 5-10 m:

| Class (real size, cm) | Centre of frame | Far (top) edge | Far edge, long axis along view |
|---|---|---|---|
| backpack (64 x 50) | 130-260 | 55-110 | 17-34 |
| person sitting or standing (95 x 85) | 195-390 | 85-170 | 25-50 |
| person lying (165 x 95) | 340-680 | 145-290 | 43-87 |
| water_bottle (23 x 6.5) | 47-94 | 20-40 | 6-12 |
| sunglasses (14.5 x 8.5) | 30-60 | 13-25 | 4-8 |

Takeaways: every class stays above the 8 px `difficult` line at the centre of a 45° frame
at 10 m. At the far edge a sunglasses lying along the view direction drops to 4-8 px, and a
bottle to 6-12 px, so those two will often be `difficult` there. That is a property of the
45° mount, not of the drone height. Tall objects (a standing person) sit closer to the
camera than the ground, so they look bigger than this table at low heights.

### 3.3 Shot list per scene (about 9 stills)

- 45°: 5, 7.5 and 10 m, each from 3 headings (two opposite sides and one side-on)
  (9 stills) **[decide]**.
- Keep every still of one scene in one folder; log scene ID and placement IDs.

Stage each object three ways across scenes: exposed, partial, deep under canopy, and
log the staged tier (`exposed`/`partial`/`deep`) per placement. Aim for about a third
each, per class, per site. A moved object is a new placement; another pass over the
same layout is not.

### 3.4 Session template (~2 h)

1. **Before leaving:** read the class-count tracker (P2.6), pick the 2-3 classes
   furthest behind, write the scene list with types and tiers.
2. **Site setup:** site ID, weather, canopy notes, time of day, captions ON. Check card
   space, charge all batteries.
3. **Negatives (`N`, first or last 10 min):** about one still in ten **[decide]**.
4. **Staged scenes:** about 14 (see 5.2 for the mix), shot per 3.3.
5. **Video (`V`):** 2 slow passes, at or under about 2 m/s and at 5-10 m
   **[decide after Wave 0]**, over scenes at varied occlusion. Check speed afterwards
   from the `speed_mps` column; the test flight passes ran at about 3.1 m/s.
6. **Same-day offload and backup** to the card folders in 3.1, rename, then run
   `vision/telemetry/extract.py --check` and `plot.py`; commit the session folder in
   `flights/`.
7. **Annotate the session's footage before planning the next one** (P2.5).

Battery plan: about one battery per 15-25 min of flying (expected, unmeasured). Log
real flight time per battery from Wave 0 and rebalance.

### 3.5 Occlusion: natural and synthetic

The two kinds have different jobs, and synthetic occlusion does not have to be matched
by natural occlusion image for image.

- **Natural (staged) occlusion is the evidence.** Every placement is logged as `exposed`,
  `partial` or `deep` (3.3). The test split must hold enough of each tier for the P3.6
  cross-check, where the synthetic degradation curve is compared with real occluded
  imagery; agreement is a strong claim and disagreement is a finding to report. Ways to
  stage it, to be planned per prop with the author before Wave 1: partly under a bush or
  branch, behind a log or rock, under leaf litter, deep under canopy, or with fallen
  branches and leaves from the ground laid over the object (do not cut live vegetation).
- **Synthetic occlusion is the instrument, and optionally a training aid.** The test
  sweep (0, 10, 20, 40, 60, 80%) comes from `occlusion/occlude.py` on the bush test split.
  If synthetic occlusion is also used to make training images, then: use
  `--distractor-rate` (the guide uses 1.0) and `--frac-jitter`, or the model learns "pasted
  foliage means a target underneath"; generate once with a fixed seed and keep the files
  on disk, so every model sees byte-identical images (HARD RULE 2); keep the full box on
  an occluded target (HARD RULE 6); tag it `synthetic_occlusion`; keep it out of the test
  split; and treat it as its own arm **[decide]**, because a model trained with it has a
  different degradation curve from one without. The baseline sweep uses a model trained
  without synthetic occlusion.

Reference: `phase_execution_guide.md` P1.5, P3.6.

## 4. Splits and the held-out seal, designed up front

**[decide] before Wave 1.**

- **Name the test site now,** before any data exists (say Site D of four). Do not pick
  it after seeing results.
- **Every class at every site,** trained and held-out, so the test site holds enough:
  about 15 trained and 10 held-out placements per class per site at the target counts,
  which gives the 8-12 per class the guide expects in the test set. Per-site minima go
  in the tracker, not just class totals.
- **Train and val:** sites A-C, with val taken by scene within those sites (about
  15%). Never split a scene or a clip.
- **Held-out pool:** every `H` scene is sealed in its own folder from the day it is
  shot. Sites A-C are dev (prompt and threshold tuning for the D arm and VLM); the
  test site is test. No `H` scene ever enters a training manifest, and the seal assert
  (P1.4-P1.6) checks it.
- **Video clips** stay in one split and are tagged `dji_video`, kept out of detector
  training.
- **Arducam batch** is test-only, tagged `arducam_handheld`.

## 5. Waves

### 5.1 Overview

| Wave | Content | Sessions | Gate to start |
|---|---|---|---|
| 0 | Pilot: finish equipment checks, one full-process session at one site | 1-2 (plus the 2026-10-07 test flight, done) | CVAT label set (P0.6) |
| 1 | Object-only core: trained and held-out scenes, 4 sites, 3 rounds | ~12 | Wave 0 exit criteria met |
| 2 | Person and co-occurrence | ~5 | volunteer availability |
| 3 | Top-ups and video completion, driven by the tracker | 2-4 | checkpoint after Wave 1 round 2 |
| 4 | Arducam validation batch, test-only | 1-2, or folded into Wave 1 rounds 2-3 | Arducam calibrated (P0.8 step 7) |

About 21-25 sessions, so 5-8 weeks at 3-5 per week. Annotation, not flying, sets the
pace: at 2-4 h per session that is roughly 50-90 h, plus the IAA pass and video
interpolation. Keep at most two un-annotated sessions in flight.

### 5.2 Wave 0: pilot (done in part)

- **0a Equipment test flight, 2026-10-07 (done):** SRT, `djmd` pitch, formats, and
  45°/90° comparison clips. Footage is an equipment pilot with volunteers in frame, so
  it is not dataset footage.
- **0b Pilot session, Site A (or the reserve site), 6-8 scenes:** types `T` and `H` only,
  every class at least twice, shot per 3.3 at 5, 7.5 and 10 m and 45°, one `V`
  pass, some `N`. Then run the whole process on it: offload, rename, `extract.py
  --check`, CVAT annotation, YOLO export, split by scene, seal assert. No training
  claims; this tests plumbing.
- **2026-10-08 field session (see `flights/2026-10-08_wave0_pilot/field_plan.md`):** a
  hand-flown height sweep at 45° and 90° (3-15 m, 82 stills; no 20 or 30 m), mixed
  scenes with the props at hand (bottles, sunglasses, backpacks, 2 to 4 volunteers), and
  one 15 s orbit video. Outcomes: the pixel-size table in 3.2; no slow pass was recorded
  (the orbit averages 4.9 m/s), so the pass-speed check is still open; the slope check
  was dropped. No held-out props yet, so `H` scenes and the held-out pixel sizes wait for
  a second pilot session.
- **Measure:** pixels per class per band; annotation minutes per still; flight time per
  battery; frame overlap at pass speed; flight-log export; HFOV/VFOV and GSD.

**Exit criteria for Wave 1:** per-class protocol `[confirm]` items decided; bands (5, 7.5,
10 m) confirmed, angle already fixed at 45°; held-out scene rule and test site decided; IAA
on 50 pilot frames at or above 0.75 mIoU and 90% class agreement; end-to-end process runs
clean; viability call made on `sunglasses` and `water_bottle`, which fall to about 4-12 px
at the far edge of a 45° frame (3.2); battery plan updated.

**Status after 2026-10-08.** Judged done for the trained classes: pixel sizes and geometry
(they stay above 8 px at the frame centre), 45° angle, no slope check, level-ground AGL.
Still open before Wave 1:

- A pilot at a real bush site: the exposed/partial/deep tiers and canopy have not been
  tried (everything so far was an open oval). Shoot the 3.3 list at 5, 7.5, 10 m.
- A slow pass at 5-10 m and at or under about 2 m/s (the orbit video was 4.9 m/s).
- The held-out props (trail marker tape, discarded gear, campfire remains, emergency
  blanket) and their pixel sizes.
- Annotate the pilot stills in CVAT, run the export, split by scene and the seal assert,
  and the 50-frame agreement check. This needs P0.6 (CVAT) first.
- The author's [decide] items (Section 8) and `annotation_protocol.md` 7.1, 7.2 and the
  `[confirm]` items.
- Smaller: flight-log export check, battery endurance (log it), name the 4 sites and the
  test site, HFOV/VFOV for the 16:9 video crop.

### 5.3 Wave 1: object-only core

12 sessions in 3 rounds of 4, one visit per site per round, so every site has data
early and a lost day does not empty a site.

| Round | Sessions | Lighting | Checkpoint |
|---|---|---|---|
| 1 | A, B, C, D | lighting 1 (morning) | annotate all four; cut or keep classes that are not on pace for the floor |
| 2 | A, B, C, D | lighting 2 (midday or overcast) | size Wave 3; start Arducam scenes if available |
| 3 | A, B, C, D | lighting 3 (late afternoon), plus gaps | final per-site-per-class check |

Each session: about 14 scenes = 9 `T` scenes (about 36 placements) + 5 `H` scenes (about
18 placements), plus negatives and 2 `V` passes. Over 12 sessions that is about 430
trained placements (72 per class against a target of 60) and 215 held-out (54 per class
against 40), each with about 8 stills, so about 580 trained and 430 held-out boxes per
class. Held-out margin is thinner than trained; watch it at the round 1 checkpoint.

### 5.4 Wave 2: person and co-occurrence

About 5 sessions over at least 3 sites, including the test site; can interleave with
Wave 1 if weather or availability forces it.

- **`P` scenes (about 10 poses per session):** lying, sitting, crouched, curled,
  standing, at a bush edge, in shade, partly under a branch. Target 45 distinct
  poses/positions.
- **`C` scenes (about 6 per session):** trained-class objects 1-3 m from the volunteer
  (backpack off to the side, clothing on a branch, a bottle).
- **`V` passes:** 2 per session over a volunteer at varied occlusion.
- Use at least 2-3 different volunteers or clothing sets across sessions, so `person`
  does not become one appearance **[decide]**.
- No held-out objects in Wave 2.

### 5.5 Wave 3: top-ups and video completion

Triggered by the tracker, not by plan: any class under its floor, the test site under
its per-class minimum, a lighting or occlusion-tier gap, fewer than 15 clips or fewer
than 3 sites for video, a class that failed IAA, or scenes rejected in annotation.
Applies the "cut classes rather than accept thin ones" rule (P2.6) if a class cannot
reach its floor.

### 5.6 Wave 4: Arducam validation batch (test-only)

100-200 frames of the same staged scenes shot with the Arducam (handheld or boom, at
deployment height and a downward angle), taken straight after the DJI shots so lighting
matches. Trained classes and `person`. It is the only measurement of the DJI-to-Arducam
gap (D5), so it does not get cut. Needs the Arducam calibrated first.
**[decide]** whether to fold it into Wave 1 rounds 2-3 (same scenes, no extra trips) or
run it standalone on re-staged scenes.

## 6. Ethics and consent

Handled separately by the author and not tracked in this plan. No wave is gated on it
here.

## 7. Metadata to capture (P2.4)

Per clip and per still: altitude AGL, GPS, timestamp, gimbal pitch, shutter, camera
FOV/resolution (one-off), site ID, canopy notes, weather, pass speed, session ID,
`provenance` (`dji_still`, `dji_video`, `arducam_handheld`). New in this revision:
scene ID, placement IDs, scene type (`T/H/P/C/N/V`), `person_present`, `cooccurrence`,
`heldout_pool`, staged occlusion tier, altitude band, split (`train/val/test/heldout-dev/
heldout-test`), volunteer code if any, and `agl_m` with `agl_method`. `rel_alt` from the
drone is height above take-off, so AGL is logged separately: nominal band flown from a
take-off point at scene level, checked against pixels on target. The pixel-size
distribution of the annotated boxes (known object sizes) is the measurement that
matters for D5, so compute it per still and use it as the AGL cross-check. On level
ground with take-off at the same level (the Wave 0 sweep), `rel_alt` is AGL, logged as
`agl_method = level_ground`, which is how every session is flown (see 3.2).

Where each value comes from (Lito X1, checked in the 2026-10-07 test flight; see
`dev_notes.md`):

| Source | Gives |
|---|---|
| Still JPG (EXIF/XMP) | GPS, relative altitude, gimbal pitch/yaw/roll, flight attitude |
| Video `.SRT` | millisecond timestamp, shutter, tint, ISO, colour temperature, GPS, altitude |
| Video `djmd` track | per-frame gimbal pitch (the SRT has none), GPS, altitude |

Read both video sources; keep the `.SRT` next to every clip. Tables and plots come from
`vision/telemetry/` (`vision/README.md`) and per-session outputs live in `flights/`. Gimbal
pitch for video no longer needs logging by hand, but note the intended angle per clip
in the session log as a cross-check. Telemetry is manifest metadata for splits,
stratified results and ground size per pixel; it is not a model input.

## 8. Open items before Wave 0 and Wave 1

- [x] **Test flight and SRT check** (2026-10-07). The `.SRT` is written with captions on;
  it has no gimbal pitch or heading, but the MP4's `djmd` track has per-frame pitch.
  Findings in `dev_notes.md`.
- [ ] **Flight-log format.** Check whether the DJI app exports a flight log from the
  Lito X1, and in what format.
- [ ] **Battery endurance.** Not measured separately; expected 15-25 min. Log flight time
  per battery on the session sheet from Wave 0 and adjust the battery plan.
- [x] **FOV and GSD** (2026-10-08). The reported 82.1° is a diagonal: stills (4:3, 4032 px)
  have HFOV about 69.5° and f about 2906 px, about 0.035 cm/px per metre of height at
  nadir. Validated against backpack detections (3.2). Still to do: the same for the 16:9
  video crop, and the DJI to Arducam comparison.
- [ ] **Bands** (3.2, angle is decided), **pass speed** (3.4), **negative ratio** (3.4),
  **held-out scene rule** (3.1), **test site and split design** (4), **volunteer
  diversity** (5.4), **Arducam batch timing** (5.6): author decisions.
- [ ] **Site list.** Name 4 sites (3-5 available) with permission, canopy type and
  access, and mark which is the test site.
- [ ] **Prop kit.** Mylar blankets (multi-pack), charcoal/ash for `campfire_remains`
  (staged cold, no live fire), wardrobe/footwear/sunglasses/backpacks/headlamps from
  home.
- [ ] **Targets sign-off** (Section 2) and a decision on where the tracker lives.

## 9. Dependencies

- P0.6 (CVAT label set from `hpi_taxonomy.md`) before Wave 0b annotation.
- Per-class annotation protocol (`annotation_protocol.md`) with `[confirm]` items settled
  before Wave 1 annotation, so box tightness and ambiguity rules are fixed before the
  first instances are drawn.
- P1.4-P1.6 held-out seal assert must exist before any training uses this data.
- Arducam calibration (P0.8 step 7) before Wave 4.
