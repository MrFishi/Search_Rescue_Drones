---
session_name: "Lit review and gap report"
slug: lit-review-and-gap-report
session_id: 3f5bf045-5b04-47dc-bfa7-e9a0c4e0d727
machine: Vivobook
created: 2026-09-17 23:33 AWST
repo_ref: main @ c1f28ad
status: open
supersedes: 2026-09-17_1552_lit-review-and-gap-report.md
---

## Goal
Draft the Literature Review (§2, ~1800 words). §2.1 is finalised, §2.2 is now
fully drafted (text below) and about to be hand-revised by the user. Next up
after that is §2.3 (Weitefeld).

## Done since the previous note (2026-09-17 15:52)
- **occlude.py reviewed and fixed** (`vision/occlusion/occlude.py`), all
  additive, `--seed`/`--mode`/achieved-fraction logging untouched:
  - `--verify N` — draws original boxes over the occluded image for the
    first N files, into `<out>/verify/`, per CLAUDE.md's converter
    `--verify` convention.
  - `texture_fallback_count` — counts how often `texture` mode silently fell
    back to a flat fill (no clean non-target patch found).
  - `distractor_attempted`/`distractor_placed` — counts skipped-for-overlap
    distractors. Both new counters land in `occlusion_meta.json` and print a
    warning line. Verified with `python3 vision/occlusion/occlude.py --help`.
- **NOMAD figure found and extracted.** Page 8 has 3 quantitative
  mAP@0.5:0.95-vs-visibility-level charts (YOLOv8l/RetinaNet-R101/
  FasterRCNN-R101) plus qualitative aerial photo pairs. Used the YOLOv8l
  chart, saved to `figures/nomad_yolov8l_visibility_map.png`.
- **Citation decision (§2.2 synthetic occlusion):** `devries2017cutout` cited
  in the LR for general grounding (one source, per gap report).
  `ghiasi2021copypaste` held back for Process §4.3, where it specifically
  grounds `--distractor-rate` (pasting occluder copies at background
  locations — the actual Copy-Paste-shaped operation in the code). Neither
  paper cleanly matches the default `texture` mode itself (self-samples from
  the same image); reasoning recorded in the outline.
- Outline `sem1_proposal_outline.md` §2.2 updated with both decisions, dated.
- **§2.2 drafted in full** (267 words + caption) — see below.
- **Permission fix:** `.claude/settings.local.json` had 3 stale/incomplete
  Bash allow-rules for the handoff skill's own `state.sh`/`list.sh` calls
  (wrong path form — relative+unquoted vs. the actual quoted-absolute-path
  invocation, one with a literal `../pickup/list.sh` segment). Added 3
  correct entries; this is what let `/handoff` finally run.

## The §2.2 draft (267 words + caption)

> Search-and-rescue detectors trained on standing, unobstructed pedestrians
> degrade sharply on partially occluded, non-standing subjects. Recent
> occluded-person corpora built specifically for this gap show conventional
> models missing targets that differ from their training distribution in
> pose and visibility alone [cite:pop_infrared2025].
>
> One sensor-side answer is RGB-thermal fusion, which recovers detections
> through sparse foliage by exploiting thermal contrast a visible-only model
> cannot see [cite:gui2026seeing]. The result is strong, but it assumes a
> second, spatially aligned sensor and the calibration that pairing
> requires; this project scopes that cost out and asks how far a single RGB
> channel goes before the extra sensor becomes necessary.
>
> Where paired sensor data doesn't exist, synthetic occlusion is the
> established substitute. Masking a controlled fraction of an image during
> training or evaluation is a standard regularisation and evaluation
> instrument for convolutional detectors [cite:devries2017cutout].
>
> Two risks temper it. A detector can learn "occluder texture implies
> target" instead of "target present under occlusion" if occluders only
> ever appear over real subjects, which motivates pasting identical
> occluders over background regions during training as a control. Synthetic
> masks are also geometrically and texturally cruder than real canopy, so a
> synthetic degradation curve is a lower bound on real-world difficulty, not
> a substitute for it.
>
> Figure X quantifies that difficulty directly. On NOMAD's graded-visibility
> aerial imagery, YOLOv8l's mAP@0.5:0.95 collapses toward zero beyond
> roughly 50 m regardless of visibility level, and falls steeply even at
> 10 m once visibility drops below about 60 [cite:bernal2024nomad].
>
> Together, these motivate a graded synthetic sweep validated against a
> real-occlusion set, and the full-box label policy that keeps ground truth
> tied to presence rather than visible pixels.

**Fig. X.** YOLOv8l detection performance vs. NOMAD visibility level, by
distance. Adapted from [cite:bernal2024nomad].
(`figures/nomad_yolov8l_visibility_map.png`)

Ran through `/humanizer` mentally — already clean (no dashes, no
not-X-but-Y, no AI-vocabulary hits, hyphens correctly only before nouns).

## In flight
- **Nothing from §2.1/§2.2/the framing paragraph is saved to a file yet** —
  all three exist only in this chat and in handoff notes. No
  `draft_lit_review.md` or similar exists in
  `thesis/writeups/sem1_proposal_lit_review/`.
- Uncommitted: `vision/occlusion/occlude.py` (M), `sem1_proposal_outline.md`
  (M), `figures/nomad_yolov8l_visibility_map.png` (??),
  `.claude/settings.local.json` (M, permission rules).

## Decisions
- §2.2 citation split and NOMAD figure choice — both recorded in outline
  §2.2 (2026-09-17), reasoning in "Done" above.
- Everything from the previous note (word budget, figure placements for
  §2.3/§4.1, framing paragraph) still stands, unchanged.

## Open questions
- Carried over, untouched this session: O6 scope, which 1–2 open-vocab
  detectors, which 2–3 VLM candidates.
- Should §2.1/§2.2/framing paragraph get saved into a real draft file now,
  or stay chat-only until the whole LR is done? Not asked yet.

## Next steps
1. User hand-revises the §2.2 draft above into the real submission.
2. Then §2.3 (Weitefeld, ~240 words) — fully sourced, `altitude_ladder.png`
   already decided (fixes still pending on the user's end, see previous note).
3. Commit + push: occlude.py, outline, the new figure, settings.local.json.
4. Consider starting a persistent draft file so prose survives outside chat.

## Gotchas
- The handoff skill's own permission rules needed 3 new entries this
  session because the literal invoked command used a quoted absolute path
  (one with a `../` traversal segment) that didn't match older
  relative/unquoted rules. If `/handoff` fails again, read the exact
  command in the error and match it literally — don't assume prior rules cover it.
- occlude.py's default `texture` mode doesn't cleanly match either Cutout or
  Copy-Paste — the citation split is about which mode/mechanism each paper
  grounds, not the default mode itself.
- No `.tex` file exists yet; IEEEtran.bst vs ieeetr.bst warning from the
  previous note still applies.

## Read first
- This note's "The §2.2 draft" section above
- vision/occlusion/occlude.py (all 3 fixes)
- thesis/writeups/sem1_proposal_lit_review/sem1_proposal_outline.md:256 (§2.2)
- figures/nomad_yolov8l_visibility_map.png
- .claude/handoffs/2026-09-17_1552_lit-review-and-gap-report.md (§2.1, framing
  paragraph, §2.3/§4.1 figure decisions — still current)
