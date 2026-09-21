---
session_name: "P1.4 eval, HPI collection, drone parts"
slug: p1-4-eval-hpi-collection-drone-parts
session_id: f4832a6f-ec78-4c45-b80a-0de3e7feb29a
machine: Crystallina
created: 2026-09-22 01:11 AWST
repo_ref: main @ 79526c8
status: open
---

## Goal
Resume thesis work after the Sem 1 proposal: start P1.4 (eval harness), lock the HPI
classes and start DJI Lito X1 collection, and start buying parts for the user's own airframe.

## Done
- Read phase_execution_guide.md (all), objective_changes, technical_work_timeline, dev_notes,
  overfit_gates.md, training_nomenclature.md, occlude.py, converter headers, configs, runs.csv.
- Web-checked Lito X1: 249 g, 1/1.3" 48 MP, 24 mm-equiv, 82.1° FOV (likely diagonal); SRT support NOT confirmed.
- Updated memory: collection-drone-dji-lito-x1.md. No repo files changed.

## In flight
- Nothing uncommitted from this session. Git was clean at start (main @ 79526c8, ahead 0/behind 0).
- The 2026-09-17 note listed occlude.py, the outline and the NOMAD figure as uncommitted; not re-checked here.

## Decisions
- None made by the user yet. Recommendations only (not recorded in any repo doc):
  - Cut HPI list to 4 trained + 2-3 held out; drop `trail_marker_tape` (~2 px wide on Arducam at 10 m).
  - Define `discarded_gear` as "not any trained class" to avoid overlap.
  - Airframe: X500 v2-class kit (PX4-native, matches Gazebo x500); the Holybro Jetson baseboard is not needed.

## Open questions
- Has the ethics email (person-present sessions) been sent? Repo doesn't say.
- Is the flight controller already bought or part of the buy list? Budget left for everything but the Jetson is ~$700-900 AUD.
- Does the Lito X1 write an SRT sidecar with altitude and gimbal? Needs a test clip.
- Is the AR0822's 145° horizontal or diagonal? Needs checking against Arducam's spec.

## Next steps
1. Build vision/eval/evaluate.py: per-class rows appended to results/runs.csv, provenance_filter assert, sealed-class assert, occlusion mode/frac, git SHA, device.
2. Score Baseline A on the official HERIDAL test split (1,957 tiles). Val mAP50 0.954 is above the guide's ~0.92 leakage line.
3. Check Weitefeld: PROVENANCE says core_only=False (guide says use --core-only); confirm unique finding count is near 405; test split is only 308 tiles.
4. Add SAHI full-frame eval and centre-distance recall (cite Accenture/AIR).
5. Generate frozen occlusion buckets 0/10/20/40/60/80 with `occlude.py --verify`, then the P1.6 sweeps.
6. Write per-class protocols, set up CVAT with the locked labels, recon 3+ sites, make a session log and manifest schema.
7. Test-fly the Lito X1 for SRT/altitude, then make a BOM sheet: frame, FC, GPS, motors/ESCs, battery x2, 12 V buck for the Jetson, downward rangefinder, camera mount, spares.
8. Bench-test Pixhawk-Jetson uXRCE-DDS over UART before any expensive parts.

## Gotchas
- `/handoff` needs approval for state.sh; the first run failed on the permission check.
- The name arg was parsed as "this", so the slug was set manually.
- Docs are stale: guide P2.2 FOV compensation (dropped in P3.0), Kaya mentions (not used), Mamba in timeline, `HOW_TRAINING_WORKS.md` name in dev_notes.
- ~77 MB of .pt files are tracked in git under results/baselines and vision/training (relevant to the public-release plan).
- dev_notes Pinned Versions still has blanks: PX4 SHA, Gazebo, uXRCE agent, Arducam driver, CUDA/TensorRT.

## Read first
- thesis_docs/phase_execution_guide.md:628 (P1.4)
- thesis_docs/phase_execution_guide.md:210 (P0.2 taxonomy)
- results/runs.csv:1
- vision/training/overfit_gates.md:1
- data/processed/weitefeld_yolo_3cls_v1/PROVENANCE.md:1
- vision/occlusion/occlude.py:206
- thesis_docs/companion_computer_choices.md:1 (budget, Jetson choice)
