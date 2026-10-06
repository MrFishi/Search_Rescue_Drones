# Phase 2 Collection Plan (own bush/HPI dataset)

**Status: draft 2026-10-06.** Targets and waves below are proposed and not yet
signed off. Class list is locked in `hpi_taxonomy.md`. Guide references:
`phase_execution_guide.md` P2.3 (session design), P2.4 (metadata), P2.6 (targets,
tracker), and the temporal-video section near line 1195.

## 1. Constraints (confirmed 2026-10-06)

| Item | Value |
|---|---|
| Drone | DJI Lito X1, 3 batteries (Fly More Combo) |
| Cadence | 3-5 sessions/week |
| Sites | 3-5 bush sites (plan for 4) |
| Person subjects | The author and thesis peers (volunteers) |
| Session length | ~2 h planned in advance (P2.3) |

Not yet verified (see Section 7): per-battery flight time, SRT contents, real FOV.

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
placement. That comes from 2-3 altitude bands x 2-3 headings/angles per scene.
All stills of one placement stay in one split (HARD RULE 1).

Rough capacity check: 12-15 scenes x 3-5 objects is about 40-70 object
placements per session. Required object placements are 6x60 + 4x40 = 520, so
roughly 8-12 object sessions. Wave 1 below sits inside that range, and Wave 3
absorbs the shortfall.

## 3. Session template (~2 h)

1. **Before leaving:** read the class-count tracker (P2.6), pick the 2-3 classes
   furthest behind target, and write the scene list for the session.
2. **Site setup:** record site ID, weather, canopy notes and time of day on the
   log sheet. Check SD card space and charge all three batteries.
3. **Negatives (first or last 10 min):** empty bush, fallen logs, rocks, dark
   shadow patches, anything vaguely person-shaped.
4. **Staged scenes (~12-15):** 3-5 objects per scene. Place the same object
   three ways: fully exposed, partially under a bush, deep under canopy (real
   occlusion data for P1.6 cross-check). Each placement is a new unique
   placement; do not re-shoot the same layout and count it twice.
5. **Stills per scene:** 2-3 altitude bands, 2-3 headings. Log altitude and
   gimbal pitch.
6. **Video:** 2 slow, steady passes per site over staged scenes at varied
   occlusion levels. Log pass speed.
7. **Same-day offload and backup.** Then tick the tracker.

Battery plan: three batteries per session, split roughly one for stills/scene
shooting, one for stills/second altitude band, one for video passes and spare.
Adjust once real flight time is measured.

## 4. Waves

| Wave | Content | Sessions | Gate to start |
|---|---|---|---|
| 0 | Pilot: test-flight, SRT/log check, FOV measure, one site, a few scenes of each tier, full annotate-and-split dry run | 1-2 | CVAT label set ready (P0.6) |
| 1 | Object-only (trained + held-out), 4 sites, >=2 lighting conditions per site | ~10 | Wave 0 findings folded in |
| 2 | Person-present and co-occurrence (objects near a volunteer), including slow video passes at varied occlusion | ~4-5 | Volunteer consent recorded (Section 6) |
| 3 | Top-ups driven by the class-count tracker; fill the weakest classes, sites or lighting | 2-4 | Waves 1-2 annotated |

At 3-5 sessions per week this is roughly 4-6 weeks of field time, but the real
constraint is annotation: annotate each session before planning the next (P2.5).
Waves 1 and 2 can interleave if weather or volunteer availability forces it, as
long as the held-out classes are only ever staged, annotated and stored under
their held-out label (HARD RULE 3).

Lighting coverage target per site: at least two of morning, midday, overcast,
late afternoon.

## 5. Metadata to capture (P2.4)

Per clip or still-set manifest row: altitude AGL, GPS, timestamp, gimbal pitch
(manual if absent from SRT), camera FOV/resolution (one-off), site ID, canopy
notes, weather, pass speed, session ID, `provenance = dji_video` for video.
Parse SRT to one row per clip, not per frame.

## 6. Ethics and person subjects

Volunteers are the author and thesis peers. Keep a brief written consent line per
volunteer and per session (name, date, permission to be imaged and retained for
the thesis) even though the approval path is simple. Person-present sessions
should not start until that record exists. Confirm with the supervisor whether
this matches what the P0.1 ethics email says before Wave 2.

## 7. Open items before Wave 0

- [ ] **Test flight and log check.** Fly a short test, enable video captions, and
  see whether an `.SRT` is written and what fields it has (altitude, gimbal pitch,
  heading). Also check which flight-log format the Lito X1 produces and whether
  the DJI app exports it. Record findings in `dev_notes.md`.
- [ ] **Battery endurance.** Measure real flight time per battery at survey
  altitude with wind.
- [ ] **FOV.** Verify the actual Lito X1 FOV (reported 82.1°, likely diagonal)
  before the DJI to Arducam domain-gap discussion.
- [ ] **Site list.** Name 4 sites (3-5 available) with permission, and note
  canopy type and access for each.
- [ ] **Prop kit.** Mylar blankets (multi-pack), charcoal/ash for
  `campfire_remains` (staged cold, no live fire), wardrobe/footwear/sunglasses/
  backpacks/headlamps from home.
- [ ] **Targets sign-off** (Section 2) and a decision on where the tracker lives.

## 8. Dependencies

- P0.6 (CVAT label set from `hpi_taxonomy.md`) before Wave 0 annotation.
- Per-class annotation protocol (`hpi_taxonomy.md` Section 4) before Wave 1
  annotation, so box tightness and ambiguity rules are fixed before the first
  instances are drawn.
- P1.4-P1.6 held-out seal assert must exist before any training uses this data.
