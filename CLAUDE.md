# Agent Instructions — Forest Runner SAR Drone (Vision/AI Track)

> This file is read automatically by Claude Code (`CLAUDE.md`) and Codex
> (`AGENTS.md`). Keep them identical — symlink one to the other. Read the
> canonical docs below before making non-trivial changes; they are the source
> of truth, this file is only the short version plus the hard rules.

## Read first (canonical project docs)

- `training_nomenclature.md` (repo root) — naming conventions: `tiny/` sanity gates
  vs Phase 1 baselines (yolo11s) vs the Phase 3 six-model sweep. Read this before
  writing or checking anything that names a model or a run.
- `thesis_docs/objective_changes_since_progress_report.md` — current thesis state, supersedes the progress report
- `thesis_docs/technical_work_timeline.md` — phases, dependency ordering, critical path
- `thesis_docs/phase_execution_guide.md` — step-by-step execution detail, Phases 0–3
- `thesis_docs/dev_notes.md` — system architecture, environment decisions, pinned versions
- `thesis_docs/comparison_dependency_flowchart.md` — Phase 3/4 comparison dependency structure
- `vision/training/overfit_gates.md` — dataset trust gate results and known label issues
- `data/processed/<dataset>/PROVENANCE.md` and `data/raw/<dataset>/PROVENANCE.md`
  — per-dataset provenance (one file per dataset, not a single global file)
- `simulation/sim_setup.README.md` — ROS2/PX4/Gazebo sim stack

## What this project is

Vision/AI track only: aerial detection, human-presence-indicator (HPI)
classification, and multi-drone search coordination that consumes detections.
**VOC (voice/operator control) is NOT part of this track** — another student
owns it. Do not add VOC work. HPI detection is the primary contribution; the
VLM arm is evaluated, not assumed to win (a negative VLM result is a valid result).

## Environment

- The `vision/` package is a plain, `uv`-managed Python package, deliberately
  **decoupled from ROS2** until Phase 6. It must run on a GPU box with no ROS2.
  Run everything with `uv run python ...`. Do not add a ROS2 import to `vision/`.
- Training runs on WSL2 / RTX 4070 (or Kaya HPC for the Phase 3 sweeps).
  **Never train on the Jetson** — it is an inference/benchmarking device only.
- Torch/torchvision are pinned to the `pytorch-cu128` index in `pyproject.toml`.
  Do not change the index or add a project-wide `--default-index`.
- The PX4-Autopilot clone is an external dependency with its own git history.
  Do not edit files inside it from this repo; the sim uses symlink/deploy scripts.

## HARD RULES — do not do any of these without explicit confirmation

1. **Split by the unit of independence, never by frame/image.** HERIDAL splits
   by source photo, Weitefeld by physical finding, bush data by placement (site
   preferred). A single video clip never spans train/val/test. Near-duplicates
   leaking across splits silently inflate scores — do not "simplify" split logic.
2. **Occlusion sets are frozen on disk with fixed seeds.** Every model in a sweep
   must see byte-identical images. Never regenerate, re-seed, or switch to
   on-the-fly occlusion. Preserve `--seed`, `--mode`, and achieved-fraction logging.
3. **The held-out HPI class seal is sacred.** Held-out classes must never appear
   in any training manifest. Keep/strengthen the programmatic assert that verifies
   this before training. A leak invalidates the headline Phase 4 result.
4. **No architectures requiring custom CUDA kernels** (training OR export).
   This is why the SSM/Mamba arms were dropped. Do not reintroduce them as code.
5. **Datasets stay separate (D6).** Do not combine HERIDAL + Weitefeld + bush
   into one training set. Phase 3 trains/evals on bush data only. Init-source
   comparison (D7) is sequenced, not mixed.
6. **Occlusion label policy:** an occluded target keeps its FULL original box.
   Never shrink boxes to visible pixels — that turns occlusion into a
   small-object experiment.
7. **Log every training/eval run to `results/runs.csv`** with git SHA, per-class metrics,
   `provenance_filter`, occlusion mode/frac, device, and latency/power where
   applicable. Do not run experiments that don't get logged.

## Conventions

- Always run a converter's `--verify` mode (renders tiles with boxes) before
  trusting its output. Coordinate-convention bugs are invisible in metrics.
- Report Weitefeld `person`-class metrics as a lower bound — ~14.7% of person
  rows are "excluded, not checked" label noise (see `vision/training/overfit_gates.md`).
- A failed overfit gate has more than one cause; render predictions at near-zero
  confidence to tell a coordinate bug from an undertrained model.
- When adding deps, use `uv add` and keep `uv.lock` committed and synced.
- Pin versions in the `thesis_docs/dev_notes.md` "Pinned Versions" table when they're established.
- **Naming discipline:** never call a `tiny/` gate run a "baseline" or a "result" —
  see `training_nomenclature.md`. Baseline A = HERIDAL/yolo11s, Baseline B =
  Weitefeld/yolo11s. The Phase 3 sweep is the six named architectures, not variants
  of yolo11.

## Ask before

- Changing anything in the HARD RULES list.
- Restructuring `vision/` into an installable package (deferred to Phase 6).
- Large downloads (Weitefeld full is 404 GB; start with 2–3 strips).

## graphify

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

Rules:
- For codebase questions, first run `graphify query "<question>"` when graphify-out/graph.json exists. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- If graphify-out/wiki/index.md exists, use it for broad navigation instead of raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).
