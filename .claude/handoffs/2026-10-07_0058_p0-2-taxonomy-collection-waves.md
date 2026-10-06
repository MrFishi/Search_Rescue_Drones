---
session_name: "P0.2 taxonomy and collection waves"
slug: p0-2-taxonomy-collection-waves
session_id: fedb8fbd-30d5-4867-826a-861738481218
machine: Crystallina
created: 2026-10-07 00:58 AWST
repo_ref: main @ ee0899c
status: open
supersedes: 2026-10-06_2324_p0-2-taxonomy-collection-waves.md
---

## Goal
Finish P0.2 (HPI taxonomy + annotation protocol) and the Phase 2 collection plan, working
WITH the user, then move on to P0.6 (CVAT), P0.1, P0.8 and Phase 1.

## Done
- `thesis_docs/collection_plan.md` (new): constraints, targets (proposed 60/600 trained,
  40/400 held-out, 45/600 person, 20+ clips, 4 sites), session template, Waves 0-3,
  metadata, consent line, open items, dependencies.
- `thesis_docs/annotation_protocol.md` (new, via /find-refs + /humanizer): general rules
  1.1-1.9, per-class tables for all 11 classes, video, IAA check, placement log fields,
  open decisions, precedent table, 7 new sources with Crossref-checked DOIs.
- `thesis_docs/hpi_taxonomy.md` Section 4: pointer to the two new docs.
- 6 PDFs added to `papers/`: pascal_voc_everingham2010, crowdhuman_shao2018,
  tinyperson_scalematch_yu2020, visdrone_zhu2021, vatic_vondrick2013_ijcv,
  extreme_clicking_papadopoulos2017. SARD (IEEE Access 2021) is open access, not downloaded.

## In flight
- Everything above is UNCOMMITTED on Crystallina. It reaches the laptop only once
  committed and pushed together with this note.
- New sources are NOT in `thesis_writeups/references.bib` (Zotero/Better BibTeX export, do
  not hand-edit). User must add the 7 items in annotation_protocol.md Section 9 to Zotero.

## Decisions
- Constraints confirmed by user: Lito X1 + 3 batteries (Fly More), 3-5 sessions/week,
  3-5 sites, volunteers = user + thesis peers. Recorded in collection_plan.md Section 1.
- Targets: user said "if ur happy with that", so the proposed numbers went in, marked draft.
- Amodal full box (HARD RULE 6) justified against CrowdHuman; VOC/COCO use visible extent.

## Open questions (all in annotation_protocol.md)
- Section 7.1: split unit = scene (3-5 placements per frame), not placement. HARD RULE 1.
- Section 7.2: held-out objects unlabelled in training frames get learned as background.
  Option A: stage held-out classes only in scenes without trained classes. Option B: send
  frames containing them to the held-out eval pool. Needs a decision before Wave 1. HARD RULE 3.
- [confirm] items: 8 px `difficult` threshold; train on difficult and report both; worn
  items unboxed except emergency_blanket; pitched tent in discarded_gear; sunglasses
  viability; IAA pass mark 0.75 mIoU / 90% class agreement.
- Lito X1 test flight: SRT fields, flight-log format, battery endurance, real FOV.

## Next steps
1. On Crystallina: commit and push (see the command at the end of this note).
2. On the laptop: `git pull`, then `/pickup P0.2 taxonomy and collection waves`.
3. Walk through annotation_protocol.md Section 7 and the [confirm] items one at a time;
   the user decides each, then update the doc (and collection_plan.md for the split unit).
4. User adds the 7 new sources to Zotero.
5. Test flight per collection_plan.md Section 7; record findings in dev_notes.md.
6. Then P0.6 (CVAT label set from hpi_taxonomy.md), P0.1, P0.8, Phase 1.

## Gotchas
- The user wants to decide rules themselves: present defaults, don't finalise unasked.
- pdftotext is not installed; use `uvx --from pypdf python` to read PDFs.
- The handoff skill is disable-model-invocation; it was run manually from SKILL.md.
- Vivobook (laptop): `docker` is a podman shim; CVAT needs XDG_DATA_HOME fix and newer
  compose (see previous note). No GPU on the laptop.

## Read first
- thesis_docs/annotation_protocol.md:1
- thesis_docs/annotation_protocol.md:155
- thesis_docs/collection_plan.md:1
- thesis_docs/hpi_taxonomy.md:71
- thesis_docs/phase_execution_guide.md:1000
- CLAUDE.md:1

Commit: `git add .claude/handoffs thesis_docs papers && git commit -m "handoff: p0-2-taxonomy-collection-waves" && git push`
