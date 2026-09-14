---
name: evaluate
description: "Grade a thesis, proposal, or report draft strictly against the marking rubric and return a prioritised, mark-raising fix list. Use to critique a draft the author has written and wants improved. Checks factual consistency against the project docs, flags unsupported claims and missing citations. Never rewrites the author's prose."
---

# Draft Evaluation (critic role — run on Opus)

## Purpose

Act as a demanding but fair examiner. Find exactly what is costing marks and say how
to recover them, so the author can revise it themselves. The deliverable is a
critique and a fix list — never replacement prose.

## When to use

- The author has drafted a section (or the whole document) and wants it assessed.
- Before submission, as a final adversarial pass.
- After a revision, to confirm the previous round's fixes actually landed.

## Inputs to gather first

1. **The draft** — a section or the full document. If it lives on Overleaf, work from
   the git-synced clone; if local, read the `.tex` directly.
2. **The rubric** in `thesis/writeups/<active-writeup>/rubric_and_template/` (see `thesis/writeups/ACTIVE.md`) — grade against the actual file.
3. **The current project docs** for factual checks:
   `training_nomenclature.md` (repo root — model/run naming and what structurally
   distinguishes the six Phase 3 architectures),
   `thesis_docs/objective_changes_since_progress_report.md`, `thesis_docs/technical_work_timeline.md`,
   `thesis_docs/comparison_dependency_flowchart.md`, and any relevant method docs.

## Procedure

1. **Per-criterion grading.** For each rubric criterion, give:
   - an indicative band (weak / adequate / strong / excellent) with a one-line reason
     tied to specific text in the draft, and
   - the single highest-value change that would move it up one band.
2. **Consolidated flags**, quoting the offending text in each case:
   - **Unsupported claims** — assertions with no evidence, citation, or derivation.
   - **Missing citations** — spots that need literature support; route these to
     `find-refs`.
   - **Consistency errors** — anything contradicting the project docs. Common traps:
     implying VOC is in scope; implying HERIDAL/Weitefeld/bush data are combined
     (they are kept separate, D6); describing O4's old routing rule (high-confidence
     detections are no longer routed to the VLM); citing a `tiny/` sanity-gate run as
     a baseline or reportable result (see `training_nomenclature.md`); mixing up what
     structurally distinguishes the six Phase 3 architectures (e.g. YOLOv13's
     hypergraph correlation across non-adjacent regions is not YOLOv12's local
     self-attention); overstating the temporal or fleet
     arms, which are time-permitting.
   - **Scope & precision** — vague or overclaimed statements. The rubric rewards
     precise, hedged, evidence-backed claims; penalise "our system is robust" with no
     quantification.
   - **Structure & signposting** — does each paragraph earn its place and connect?
3. **Prioritised fix list.** Order by mark impact, highest first. Each fix must be
   concrete and actionable enough for the author to execute without further guidance,
   and must say *what the fix needs to achieve*, not supply the sentence itself.

## Output format

Three blocks: (1) per-criterion table with band + top change; (2) flagged issues
grouped by the categories above, each quoting the draft; (3) the prioritised fix
list. Keep it specific; a vague critique is useless.

## Hard rules

- **Never rewrite the author's prose.** Identify problems and what a fix must do.
  If asked to "just fix it," decline and hand back the actionable version (see
  `thesis/CLAUDE.md`).
- **Do not soften real problems.** A generous grade that misses a weakness the
  examiner will catch costs marks later. Be honest and specific.
- **Grade against the real rubric**, not a plausible-sounding one. If no rubric file
  is present, say so and stop rather than inventing criteria.
- Distinguish "needs a citation" from "fine as the author's own reasoning" — not
  every sentence needs a reference.
