---
session_name: "Lit review and gap report"
slug: lit-review-and-gap-report
session_id: 3f5bf045-5b04-47dc-bfa7-e9a0c4e0d727
machine: Vivobook
created: 2026-09-17 15:52 AWST
repo_ref: main @ cd94395
status: open
supersedes: 2026-09-16_1838_lit-review-and-gap-report.md
---

## Goal
Draft the Literature Review (§2, ~1800 words) for the GENG4411/5511 Sem 1
proposal (due Mon 21 Sep). All sourcing is done — this session is now purely
about writing prose. Start by finishing the framing paragraph (draft below),
then 2.1–2.3.

## Done since the previous note (2026-09-16 18:38)
- **All 20 sourced papers vetted and kept** — moved from `temp_papers/` into
  `papers/` (35 PDFs total now). `temp_papers/` no longer exists.
- **`references.bib` updated to 35 entries.** Added 20 new keys (see list
  below), each with author list transcribed directly from the PDF title page
  (not search snippets). Then a full-file pass added `url` fields (arXiv →
  `arxiv.org/abs/<id>`, DOI → `doi.org/<doi>`) and normalised 7 booktitle
  strings to match the exemplar's rendering style (dropped "Proceedings of
  the" for NeurIPS/ICLR/ICML/COLM/ECCV, abbreviated CVF venues to "Proc.
  IEEE/CVF Conf. …"). One entry (`ren2017fasterrcnn`, pre-existing, not mine)
  still has no `url` — no doi/eprint field to derive one from.
- **Backup of pre-url-pass bib** at `/tmp/references.bib.bak` if a diff is
  ever needed.
- **Two figures placed, both hand-drawn, both at repo root:**
  - `altitude_ladder.png` → **§2.3** (Weitefeld). Compares HERIDAL 45–60m,
    Weitefeld ~300m, this project 5–10m. Numbers verified against sources.
    **Fixes needed before use** (recorded in outline, not yet done): (1)
    remove the baked-in "Nathan et al., Scientific Data 13:747 (2026)"
    footnote from the PNG — it's author-year, clashes with IEEE numbered
    style, attribution belongs in the LaTeX caption instead; (2) add "not to
    scale" — axis spacing isn't proportional; (3) caption should cite
    HERIDAL's altitude too, not just Weitefeld's GSD. Caption text drafted,
    see outline §2.3.
  - `tournament_funnel.png` → **§4.1** (Process overview). **Fix needed:**
    funnel currently reads "accuracy, then latency, memory and power on the
    Orin" — this is backwards. Actual rule (`phase_execution_guide.md:1400`):
    latency+memory budget is a hard pass/fail gate FIRST, mAP ranks only the
    survivors, power isn't part of the gate. Reword before redrawing.
  - **Open question, unresolved:** funnel says "answers O1, O2 and O4" but
    the final stage evaluates held-out HPI classes, and O3 (HPI detection) is
    the stated primary contribution. Should O3 be on that line? Flowchart doc
    has the same omission, so this may be a pre-existing doc gap, not just
    the figure.
- **Framing paragraph drafted** (112 words, target 110) — full text below.
  User was rewording it in their own voice when this session ended.

## In flight
- Uncommitted in git right now: `thesis/references.bib` (M),
  `sem1_proposal_outline.md` (M, figure notes added), all 35 files in
  `papers/` (20 untracked, 15 pre-existing already committed), `temp_papers/`
  deletions (20 files, since moved not copied), `altitude_ladder.png` (??),
  `tournament_funnel.png` (??). None of this is pushed. A prior commit
  ("papers added to be vetted", made via VSCode Source Control) already
  landed `lit_review_gap_report.md` and `technical_work_timeline.md` changes
  — those two are NOT in the current diff, already on `main`.
- **If picking this up on a different machine: the working-directory changes
  above (bib, outline, papers/, the two PNGs) are NOT on origin yet.** Either
  commit+push them from Vivobook first, or redo the bib/outline edits — they
  are NOT recoverable from git alone on another machine right now.

## The framing paragraph (draft, ~112 words)

> Aerial imagery is now standard in land search and rescue, and detection
> over open terrain is largely solved: HERIDAL-lineage systems locate people
> in unobstructed scenes photographed from 45–60 m `[cite:bozicstulic2019heridal]`.
> Vegetated terrain is not. On real search imagery captured at approximately
> 300 m over dense forest canopy, a current-generation detector effectively
> failed `[cite:nathan2026weitefeld]`, and recent surveys name occlusion as a
> core unsolved challenge in aerial person detection `[cite:zhang2025aerialsurvey]`.
> The problem compounds onboard, where unoptimised inference on embedded
> hardware has been measured at roughly two frames per second
> `[cite:yolo_sar_drones2025]`: robustness must be bought within a fixed
> compute budget. This review traces that lineage from open terrain into
> canopy and identifies what remains untested.

**Must survive any reword:** "approximately 300 m" (plants the low-altitude
premise the thesis rests on) and "unoptimised" (that paper's abstract claims
real-time for its *final* model — dropping this word misrepresents the source).
Deliberately did NOT quote HERIDAL's 88.9% here (it's recall against 34.8%
precision — bare quoting overstates it; save the caveated number for 2.1).

## Decisions
- LR locked at ~1800 words (outline §0, 2026-09-16). Process 1000, Progress
  500, Timeline 230, Intro 200, Objectives 270, slack 0.
- Working method: draft fully first, cull at the end guided by `/evaluate`.
- Figure budget: 2 reproduced (NOMAD occlusion levels in 2.2, a Weitefeld
  canopy image in 2.3) + 2 own-drawn (a 2.4 mechanism-contrast schematic
  CNN→attention→hypergraph→transformer, and a 2.5/2.6 latency-vs-vocabulary
  positioning sketch) + the 2.4 arm/evidence table. altitude_ladder and
  tournament_funnel are separate from this budget (2.3 and Process, not
  competing for the same LR figure slots).
- O6 multi-UAV scope: still **not decided** (LR paragraph vs Process-only).

## Open questions
- O6 in LR or Process-only?
- Does the funnel's/flowchart's "answers O1, O2, O4" line need O3 added?
- Which 1–2 open-vocab detectors to name (of YOLO-World/GDINO/OWLv2/YOLOE)?
- Which 2–3 VLM candidates to finalize (of 5: SmolVLM2, Qwen2-VL-2B,
  Moondream2 [no paper], Florence-2, InternVL2.5)?
- Does the user want ME drafting LR prose for heavy revision, or do they
  write while I check against project docs? Unresolved as of this note —
  ask at the start of the new session rather than assuming either way.

## Next steps
1. Finish rewording the framing paragraph (in progress) — check the reworded
   version preserves "~300 m" and "unoptimised".
2. Fix `altitude_ladder.png` (remove baked-in citation) before it goes in §2.3.
3. Fix `tournament_funnel.png`'s selection-rule wording before it goes in §4.1.
4. Draft §2.1 (Aerial person detection for SAR, ~320 words) — keys ready:
   `ren2017fasterrcnn`, `bozicstulic2019heridal`, `yolo_sar_drones2025`,
   `botea2026lostperson`, `zhang2025aerialsurvey`. Traps: HERIDAL 88.9% is
   recall (pair with 34.8% precision or say "recall"); Ciccone's 0.802 mAP@50
   is one specific variant (PBfpn-Deconv), name it; the 450ms Jetson Nano
   figure is that paper's *unoptimised preliminary* number, not its
   conclusion.
5. Then 2.2 (occlusion) and 2.3 (Weitefeld, now fully sourced) — six-day plan
   Day 3/4 target, all three are "ready" per the gap report.
6. Still open from Day 2: draft §4 Process.
7. Commit + push the uncommitted state listed above — needed before any
   other machine can see the bib/papers/figures work.

## Gotchas
- Weitefeld has **two flight passes** in the source paper: broad scan (25km²,
  ~4cm/px, not cited) vs priority zone (10,659 images, 3–5cm/px, what every
  figure/number comes from). Don't conflate them in §2.3.
- 5 bib entries are preprint-only, marked with a `note` field so it's visible
  in the rendered bibliography: `sapkota2025yoloevolution`, `lei2025yolov13`,
  `wang2024qwen2vl`, `devries2017cutout`, `hickling2025multiuavsar`.
  `lei2025yolov13` is the sole citation for one of the six sweep arms — worth
  a hedge clause in 2.4 prose since the exemplar never rests an architectural
  claim on an unreviewed source alone.
- `marafioti2025smolvlm` is the *base* SmolVLM architecture paper — SmolVLM2
  itself has no separate paper, the note field says so.
- No `.tex` file exists in the repo yet. If drafting in LaTeX, use
  `IEEEtran.bst` not classic `ieeetr.bst` — the latter silently drops
  `eprint`/`archivePrefix`, so all 5 preprint-only entries would render with
  no identifier at all and no warning.
- Remote Control: CLI now installed (`~/.local/bin/claude`, v2.1.274) but
  `claude remote-control` almost certainly starts a **new** session, not this
  one — that's the whole reason this note exists. `/pickup "Lit review and
  gap report"` from the new session to get this state back.

## Read first
- This note's "The framing paragraph" section above (the actual draft text)
- thesis/writeups/sem1_proposal_lit_review/sem1_proposal_outline.md:15 (§0 budget)
- thesis/writeups/sem1_proposal_lit_review/sem1_proposal_outline.md:109 (§4.1 figure note)
- thesis/writeups/sem1_proposal_lit_review/sem1_proposal_outline.md:220 (§2 LR plan, figure notes)
- thesis/references.bib (35 entries, tail half is 2026-09-17 additions)
- thesis/writeups/sem1_proposal_lit_review/lit_review_gap_report.md
- altitude_ladder.png, tournament_funnel.png (repo root, both need the fixes above)
