---
name: outline
description: "Produce a detailed dot-point writing plan for a thesis, proposal, or report section, grounded in the marking rubric, the current project docs, and a high-scoring exemplar. Use when starting a new section, restructuring an existing one, or deciding what a section should contain. Produces a plan only — never finished prose."
---

# Section Outline (planner role — run on Opus)

## Purpose

Turn "I need to write section X" into a concrete, rubric-anchored plan the author
can write from. The value is in deciding *what to say and why it earns marks*
before a single sentence of prose is written. This skill never writes the section.

## When to use

- Starting any new section of the proposal, thesis, or a report.
- A section already exists but feels unstructured or is losing marks — re-outline it.
- Deciding whether a planned argument is even supportable by the project's evidence.

## Inputs to gather first

1. **Which section**, and the target length/word budget if known. If not specified,
   ask before proceeding — do not guess.
2. **The rubric** — read the actual file in `thesis/writeups/<active-writeup>/rubric_and_template/` (see `thesis/writeups/ACTIVE.md`). Never grade or plan
   against a remembered rubric; criteria wording matters.
3. **One exemplar** in `thesis/writeups/<active-writeup>/exemplars/` (see `thesis/writeups/ACTIVE.md`) — for structure, depth, and what a
   high-scoring version of this section looks like. Structure only, never wording.
4. **Current project state** — read whichever of these bear on the section:
   `training_nomenclature.md` (repo root — model/run naming: tiny gates vs Phase 1
   baselines vs the Phase 3 six-model sweep, and what structurally distinguishes each
   of the six models),
   `thesis_docs/objective_changes_since_progress_report.md` (authoritative current state),
   `thesis_docs/technical_work_timeline.md`, `thesis_docs/phase_execution_guide.md`,
   `thesis_docs/dev_notes.md`, `thesis_docs/comparison_dependency_flowchart.md`.

## Procedure

1. Extract from the rubric every criterion that applies to this section. Write each
   one down verbatim; the plan will map back to these.
2. Read the exemplar and note the *moves* it makes (e.g. "motivates with a published
   failure, then states the gap, then the research question"), not its content.
3. Read the project docs and collect the specific evidence available to support each
   point — real numbers, real design decisions, named datasets, named results.
4. Draft the plan. For every planned point, give:
   - **Point** — the claim/argument, as one dot point.
   - **Evidence** — the specific result, figure, decision, or source that backs it,
     naming the project file or dataset it comes from.
   - **Rubric hook** — which rubric criterion this point earns, quoted.
   - **Citation slots** — mark places needing literature support as `[cite: topic]`
     for the `find-refs` skill to fill later.
   - **Budget** — rough sentences/paragraphs.
5. Order the points into a logical argument arc for the section.

## Output format

A nested dot-point plan, subsection by subsection, each point carrying its evidence,
rubric hook, citation slots, and budget. No paragraphs of prose. End with:
- a short list of **evidence gaps** — planned points with no supporting evidence yet
  in the project docs (these are things to resolve before writing, not to bluff), and
- the question "which point do you want to draft first?"

## Hard rules

- **Never write the section.** If the author asks you to "just write it," produce the
  plan and offer to review their draft instead (see `thesis/CLAUDE.md`).
- **Plan the current project, not the old progress report.** Flag any point that would
  contradict `thesis_docs/objective_changes_since_progress_report.md` (e.g. treating VOC as in
  scope, or datasets as combined — they are not; see D6).
- **Use correct naming.** Per `training_nomenclature.md`: never cite a `tiny/` sanity
  gate as a baseline or reportable result; Baseline A is HERIDAL/yolo11s, Baseline B
  is Weitefeld/yolo11s; the Phase 3 sweep is the six named architectures (YOLO11s,
  YOLO26s, YOLOv12s, YOLOv13s, RF-DETR, D-FINE-S), each structurally distinct — don't
  blur what makes each one different (e.g. YOLOv13's hypergraph correlation across
  non-adjacent regions is not the same mechanism as YOLOv12's local self-attention).
- Do not invent evidence or results to make a point look supportable. A named gap is
  more useful than a confident fiction.
