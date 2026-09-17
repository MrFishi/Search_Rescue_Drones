---
session_name: "Lit review and gap report"
slug: lit-review-and-gap-report
session_id: 3f5bf045-5b04-47dc-bfa7-e9a0c4e0d727
machine: Vivobook
created: 2026-09-16 18:38 AWST
repo_ref: main @ ee5b5ae
status: superseded
---

## Goal
Source and draft the Literature Review (§2) for the GENG4411/5511 Sem 1 proposal
(due Mon 21 Sep), per `temp/six_day_plan.md`. No name was passed to `/handoff`,
so this uses the auto-generated title — run `/rename` if you want it different.

## Done
- Gap report (`thesis/writeups/sem1_proposal_lit_review/lit_review_gap_report.md`)
  covers 10 LR themes with sourcing status.
- Weitefeld publisher PDF verified against `papers/weitefeld dataset.pdf` — every
  quoted number (10,659 images, 34,424 labels, 405 findings, ~300m, 3-5cm/px GSD,
  YOLOv12 0.016%/2.6% confidence, 160 volunteers) matches. Theme 3 now fully ready.
- Word budget rebalanced and written into `sem1_proposal_outline.md` §0 + every
  section header: LR 900→**1800**, Process 1050→1000, Progress 800→500,
  Timeline 500→230, Intro 300→200, Objectives 350→270, slack removed.
- 20 candidate papers sourced (web search, not Scholar/IEEE directly) and
  downloaded into `temp_papers/` — Mamba root paper, six-arm sweep sources
  (YOLO26/v12/v13, D-FINE, RF-DETR, RF100-VL), open-vocab (YOLO-World,
  Grounding DINO, OWLv2, YOLOE), VLM candidates (Qwen2-VL, SmolVLM, Florence-2,
  InternVL2.5-1B/2B — the last two newly added), occlusion (NOMAD, Psych-Occlusion,
  Cutout, Simple Copy-Paste), multi-UAV (Hickling et al.). All verified as
  genuine full-text PDFs via `pdftotext` word counts.
- Venue-checked every paper: 5 are preprint-only with no peer review (YOLO
  Evolution/YOLO26, YOLOv13, Qwen2-VL, Cutout, Hickling multi-UAV).
- `dad_papers/` reviewed — confirmed irrelevant (business/IS "agentic AI"
  scholarship, wrong field entirely).

## In flight
- `temp_papers/` (20 PDFs, untracked) — nothing promoted to `papers/` or
  `references.bib` yet. User is vetting manually.
- Uncommitted: `lit_review_gap_report.md`, `sem1_proposal_outline.md`,
  `thesis_docs/technical_work_timeline.md` (Florence-2/InternVL2.5 added to the
  Phase 4 VLM candidate line).

## Decisions
- LR locked at ~1800 words, recorded in outline §0 (2026-09-16 revision note).
- Working method: draft every section fully first, cull at the end guided by
  `/evaluate` — recorded in outline §0.
- O6 multi-UAV scope **not yet decided** (LR paragraph vs. Process-only).

## Open questions
- Which `temp_papers/` survive vetting?
- O6 in LR or Process-only?
- Which 1-2 open-vocab detectors to name (of YOLO-World/GDINO/OWLv2/YOLOE)?
- Which 2-3 VLM candidates to finalize (of 5: SmolVLM2, Qwen2-VL-2B, Moondream2,
  Florence-2, InternVL2.5)? Moondream2 has no paper at all — cite model card or drop.

## Next steps
1. Read/vet each PDF in `temp_papers/`.
2. Move survivors into `papers/`, get proper bib keys via Zotero/`/find-refs`.
3. Update `lit_review_gap_report.md` to match vetted state.
4. Draft §2.1-2.3 (already "ready" per gap report) — six-day plan Day 3 target.
5. Also still open from Day 2: draft §4 Process, run `/lit-review` in background
   on the new architecture papers.

## Gotchas
- `temp_papers/` is untracked — must `git add` it or it won't reach the other
  machine on `git pull`.
- Weitefeld paper has **two flight passes**: broad scan (25km², ~4cm/px, not
  cited) vs. priority zone (10,659 images, 3-5cm/px, the one all figures come
  from). Don't conflate them when writing §2.3.
- 5 papers are preprint-only — cite as `arXiv:XXXX.XXXXX`, not as conference papers.

## Read first
- thesis/writeups/sem1_proposal_lit_review/lit_review_gap_report.md
- thesis/writeups/sem1_proposal_lit_review/sem1_proposal_outline.md:15 (§0 budget table)
- thesis/writeups/sem1_proposal_lit_review/sem1_proposal_outline.md:220 (§2 LR plan)
- temp_papers/ (20 unvetted PDFs)
- thesis_docs/technical_work_timeline.md:76
- temp/six_day_plan.md
