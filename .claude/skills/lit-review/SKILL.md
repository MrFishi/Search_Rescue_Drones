---
name: lit-review
description: "Triage, summarise, and synthesise research papers into a structured literature review, and position this thesis's contribution against related work. Use when processing a new paper, comparing several papers, building or updating the related-work section, or checking that a claimed novelty actually holds against the literature. Reads PDFs from `papers/` and `thesis/references.bib`."
---

# Literature Review & Positioning

## Purpose

Two jobs generic coding agents can't do well: (1) turn a pile of papers into a
coherent, comparable synthesis, and (2) honestly position this thesis against the
closest prior work, including novelty checks that could otherwise be missed until an
examiner raises them.

## When to use

- A new paper has been added and needs triaging into the review.
- Building or revising the related-work / background section.
- Deciding whether a claimed contribution is actually novel against a specific paper
  (e.g. the Weitefeld dataset paper, which is a novelty check as much as a resource).
- Producing a comparison across several methods on a shared set of axes.

## Inputs

- The paper PDF(s) — in `papers/` (repo root, gitignored — not committed) or attached.
- `thesis/references.bib` for the cite key (or route new papers to `find-refs` /
  Zotero — this is the Better BibTeX auto-export, don't hand-edit it if Zotero is
  managing it).
- **Every `.md` file in the repo** describing the project — this includes all of
  `thesis_docs/` (objectives, timeline, phase execution detail, dev notes,
  comparison/dependency structure), `training_nomenclature.md` (repo root — correct
  model/method naming), `vision/README.md`, `vision/training/overfit_gates.md`, and
  every per-dataset `PROVENANCE.md` under `data/raw/*/` and `data/processed/*/`
  (dataset quality/label-noise caveats — genuinely useful for honestly citing a
  dataset's limitations against what the literature claims). Search broadly
  (`find . -name "*.md"` or equivalent) rather than assuming a fixed list, so new
  docs get picked up automatically. `phase_execution_guide.md` in particular lays out
  the full plan in more raw detail than any summary document, so don't treat a
  higher-level planning doc (e.g. the active write-up's outline) as a substitute for
  reading it directly.
- `results/runs.csv` — the actual logged numeric results (per-class metrics, git SHA,
  device, occlusion mode/fraction). This is real evidence, not narrated in prose
  elsewhere, and belongs in Progress-to-Date-facing positioning and any claim about
  what's been measured so far.
  **Exclude:** `CLAUDE.md` files and anything under `.claude/` — those are agent
  instructions, not project facts — and `thesis/writeups/*/exemplars/`, which are
  structure references only, not project content.

## Procedure

### Gap-coverage check (run this first, every time)
Before triaging, synthesising, or drafting anything, build the full list of
technologies, methods, datasets, and claims named anywhere across every `.md` file
read above — not just the active write-up's outline, which is a summary and can omit
things a source doc like `phase_execution_guide.md` names explicitly (e.g. a specific
candidate VLM, OVD, or architecture). Cross-reference that list against `papers/` and
`thesis/references.bib`, and report it in three tiers, not two:

- **Solidly backed** — a citation exists and genuinely supports the specific claim
  being made (not just adjacent to the topic).
- **Thin** — a citation exists but the claim leans on it more than it can bear: a
  single incidental data point standing in for a general claim, a source that's
  tangential to what's actually being asserted, or one source doing double duty for
  several distinct claims. Name what a stronger source would need to establish, but
  don't treat this as blocking — per `find-refs`'s own rule, one strong source beats
  three weak ones, so only flag a real thinness, not every single-citation claim on
  principle.
- **Missing** — named in the project docs with no matching paper or bib entry at all.

Report all three, not just "missing" — do not silently skip a thin claim because it
technically has *a* citation, and do not flag something solid as needing more just to
pad the list. Do not skip this check because it wasn't the specific theme asked
about, and do not write around a gap by describing the technology from general
knowledge instead of a cited source. This check runs unprompted every time, since a
missed gap in this section costs marks in the highest-weighted rubric criterion.

### Triaging a single paper
Produce a structured card:
- **Full reference + cite key** (from `thesis/references.bib`; "needs adding" if
  absent — add the PDF to `papers/` and the source to Zotero, don't hand-write a bib
  entry).
- **Problem** it addresses, in one sentence.
- **Method** — the core mechanism, concisely and in plain terms.
- **Results** — the headline numbers, with the benchmark and conditions.
- **Relevance to this thesis** — which objective (O1–O6) or arm it touches.
- **How this thesis differs** — the specific differentiators (for this project,
  typically: low altitude 5–10 m vs high altitude, onboard real-time constraint on
  8 GB, finer HPI class granularity, open-vocabulary / VLM arms, multi-drone
  coordination). State plainly what the paper does *not* address.
- **Limitations / caveats** worth citing (e.g. crewed-aircraft altitude, coarse
  classes, crowd-sourced label noise).
- **Quote sparingly** — paraphrase; keep any direct quote short and attributed.

### Synthesising several papers
Build a comparison table on shared axes (task, altitude/platform, classes, occlusion
handling, on-device?, open-vocab?, headline metric) so the review compares rather than
lists. Then write the synthesis as themes (what the field agrees on, where it splits,
what's unsolved), not paper-by-paper summary.

### Novelty / positioning check
For the closest prior work, state explicitly: what it establishes, what it leaves
open, and the precise gap this thesis fills. If a paper substantially overlaps a
claimed contribution, say so directly — a surfaced overlap handled honestly is far
stronger than one an examiner finds. Treat published failure baselines (e.g. SOTA
detectors failing on real occluded forest HPI at survey altitude) as motivation to
cite, not to hide.

## Output format

Start with the gap-coverage list (even if empty — say so explicitly) before any
per-paper cards, comparison table, or positioning statement. Always attach cite keys
and flag "needs adding" for anything not yet in the bib.

## Hard rules

- **Paraphrase; never reproduce long passages** from a paper. Short attributed quotes
  only where exact wording matters.
- **Position against the current thesis**, not the old progress report.
- Do not overstate novelty. If the differentiator is thin, say so and suggest how to
  sharpen the actual contribution rather than inflating the claim.
- Never fabricate a paper's results or a citation — route unknowns to `find-refs`.
- **Never skip the gap-coverage check because the invocation only asked about one
  theme.** A narrow request ("triage this PDF") still runs it — cheaply, since it's
  just a cross-reference — so a gap elsewhere in the project docs never goes
  unnoticed simply because nobody happened to ask about that theme this time.
