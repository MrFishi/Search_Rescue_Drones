---
session_name: "P0.2 taxonomy and collection waves"
slug: p0-2-taxonomy-collection-waves
session_id: c069e1a0-34cd-49f1-bd31-912e1dc3a9fd
machine: Vivobook
created: 2026-10-06 23:24 AWST
repo_ref: main @ 85b2844
status: open
supersedes: 2026-09-29_0207_finish-phase-0-1-checklist.md
---

## Goal
Finish Phase 0 (and then Phase 1) per the checklist, working WITH the user, not for them.
Current thread: finish P0.2 (HPI taxonomy) and sketch the Phase 2 collection plan (waves).

## Done
- P0.7 sim smoke test passed on the laptop: PX4 SITL + Gazebo, XRCE-DDS bridge, live
  `/fmu/out/vehicle_odometry`, `ros2 run sar_drone hover` armed and climbed. Versions are in
  `thesis_docs/dev_notes.md` Pinned Versions table and a 2026-09-30 entry (committed, 85b2844).
- P0.2 class list locked 2026-10-06 in `thesis_docs/hpi_taxonomy.md` (UNCOMMITTED, see below).
- P0.6 and an earlier autonomous P0.2 draft were reverted at the user's request (see Gotchas).

## In flight
- `thesis_docs/hpi_taxonomy.md` is untracked on the Vivobook: class list, exclusion reasoning,
  stretch-ablation note, TODO section. Not committed or pushed, so it is NOT on the PC yet.
- No other uncommitted files.

## Decisions
- 1 primary + 6 trained + 4 held-out. Recorded in `hpi_taxonomy.md` only.
  - Primary: `person`
  - Trained: `backpack`, `water_bottle`, `footwear`, `clothing_item` (absorbs gloves/hats),
    `sunglasses`, `flashlight_headlamp`
  - Held-out: `trail_marker_tape`, `discarded_gear`, `campfire_remains` (staged cold with
    charcoal/ash props, no live fire), `emergency_blanket`
- Excluded: `footprint` (already rejected at phase_execution_guide.md:231) and `pocket_knife`
  (too small at search altitude). Candidates for a later stretch ablation only.
- Later tier-swap ablation is allowed only as a secondary study after the real held-out result
  exists (HARD RULE 3). Not yet in any other doc.
- Not yet decided: extensive-dataset targets (proposed below, not agreed).

## Open questions
- Targets (guide floor -> my proposal): trained 40/400 -> 60/600 placements/stills-boxes;
  held-out 25/250 -> 40/400; person 30/400 -> 45/600; video clips 15 -> 20+; sites 3 -> 4.
- Need from user: number of bush sites with permission, drone model + battery count,
  how often they can go out, ethics status (gates person-present sessions).
- Where the session plan lives: new `thesis_docs/collection_plan.md` or stay in chat.

## Next steps
1. `git pull` on the PC after the Vivobook commits and pushes this note and `hpi_taxonomy.md`.
2. Settle the targets and answer the open questions, then fill Section 4 of `hpi_taxonomy.md`.
3. Per-class annotation protocol for all 11 classes, one at a time with the user.
4. Collection waves (proposed): Wave 0 pilot session; Wave 1 object-only, ~10 sessions across
   4 sites, 2+ lighting conditions per site; Wave 2 person-present, ~4 sessions after ethics;
   Wave 3 top-ups driven by the class-count tracker. Per session: setup, negatives, ~12-15
   staged scenes (3-5 objects each), 2 slow video passes, same-day backup.
5. Then P0.6 (CVAT), P0.1 (ethics email), P0.8 (Jetson), then Phase 1 (P1.4-P1.7).

## Gotchas
- The user wants to do P0.2 and P0.6 themselves with guidance; don't write finished artifacts
  unprompted. Discuss, agree, then record.
- The guide has two target tables; the later one (phase_execution_guide.md:1238) counts stills
  only (400/250/400). Earlier 800/400 figures are stale.
- On the Vivobook, `docker` is a podman shim and fails with a storage-path mismatch under the
  VSCode snap (XDG_DATA_HOME). Workaround: set XDG_DATA_HOME=$HOME/.local/share. Also
  docker-compose 1.29.2 is too old for CVAT's compose file. All CVAT plumbing was removed.
- Guide snippet for P0.7 is stale; sim_setup.README.md is correct (`sar_drone_ws`).
- The PC (WSL2) has the uv env and GPU; the Vivobook has no GPU.

## Read first
- thesis_docs/hpi_taxonomy.md:1
- thesis_docs/phase_execution_guide.md:1238
- thesis_docs/phase_execution_guide.md:928
- thesis_docs/phase_execution_guide.md:859
- thesis_docs/dev_notes.md:360
- CLAUDE.md:1
