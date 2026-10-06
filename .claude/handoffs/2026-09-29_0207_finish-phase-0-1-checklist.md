---
session_name: "Finish Phase 0 and Phase 1 checklist"
slug: finish-phase-0-1-checklist
session_id: f4832a6f-ec78-4c45-b80a-0de3e7feb29a
machine: Crystallina
created: 2026-09-29 02:07 AWST
repo_ref: main @ cdd3bce
status: superseded
---

## Goal
Finish everything remaining in Phase 0 and Phase 1 (per `phase_execution_guide.md`),
working from the laptop, to unblock the start of Phase 2 (own dataset collection on
the DJI Lito X1) as soon as possible.

## Done
- Reviewed current Phase 0/1 status against the guide (see Next steps for the full
  checklist) — no repo code changed this session.
- Deleted the 4 prior handoff notes (3 lit-review ones, 1 prior P1.4/collection one)
  at the user's request. Deletion is staged in the working tree, not yet committed.

## In flight
- `.claude/handoffs/` deletions above are uncommitted (working tree only).
- This new note itself is uncommitted until pushed (see Next steps in the skill's
  own instructions: `git add .claude/handoffs && git commit -m "handoff: ..." && git push`).

## Decisions
- Work order for tomorrow: taxonomy + CVAT first (unblock Phase 2 directly), then
  the rest of Phase 0, then Phase 1. Not yet written into any thesis_docs file —
  only exists in this chat and this note.

## Open questions
- Does the laptop have the repo cloned with a working `uv` env, and Docker (for CVAT)?
- Ethics email (P0.1) status — still unconfirmed whether it's been sent.
- Laptop will be off the home wifi (at uni) — Jetson is only reachable there
  (`rishi@192.168.68.113`), so confirm no VPN/Tailscale exists before assuming
  P0.8 remainder / P1.7 are reachable.

## Next steps
Phase 0 remaining (taxonomy + CVAT first, unblocks Phase 2):
1. P0.2 — lock HPI taxonomy: final class list, held-out tier + criteria, per-class
   protocol doc w/ photo example, instance-count targets.
2. P0.6 — stand up CVAT via Docker, configure the P0.2 label set, test round-trip
   on ~20 images.
3. P0.1 — send ethics email if not sent; draft participant sheet/consent form.
4. P0.7 — sim smoke test; record PX4 SHA/Gazebo/ROS2 distro in dev_notes.md.
5. P0.8 — confirm module part number, TensorRT export + FP32/FP16 latency to
   runs.csv, 10-min thermal soak, check loose CAM0 connector. (Needs Jetson access.)

Phase 1 remaining:
6. P1.4 — build vision/eval/evaluate.py: per-class runs.csv rows, provenance_filter
   assert, SAHI full-frame eval, centre-distance SAR metric.
7. P1.4 — score Baseline A on official HERIDAL test set (1957 tiles) — checks
   whether val mAP50 0.954 was leakage.
8. P1.4 — verify Weitefeld used --core-only and ~405 unique findings, then score
   Baseline B on its test set.
9. P1.5 — generate frozen occlusion buckets (0/10/20/40/60/80%) with --verify on
   both HERIDAL and Weitefeld test sets; eyeball the verify renders.
10. P1.6 — run both controlled sweeps through the harness, plot degradation curves.
11. P1.7 — re-eval with the TensorRT engine, log latency/power/mAP delta. (Needs Jetson.)

## Gotchas
- Laptop likely has no GPU — P1.4 code can be written/tested on the `tiny/` subset
  (CPU-fine), but P1.6's full sweeps want the RTX 4070.
- `/handoff` needs the state.sh permission approved first, or it silently fails.

## Read first
- thesis_docs/phase_execution_guide.md:210 (P0.2 taxonomy)
- thesis_docs/phase_execution_guide.md:628 (P1.4 eval harness)
- thesis_docs/phase_execution_guide.md:652 (P1.5 occlusion tool)
- thesis_docs/dev_notes.md:328 (P0.8 status, still-open items)
- results/runs.csv:1
- vision/occlusion/occlude.py:357 (CLI args, already built)
- data/processed/weitefeld_yolo_3cls_v1/PROVENANCE.md:1 (core_only=False flag)
