# Sem 1 Proposal — Section Outlines (plan only, no prose)

> Produced by `/outline`, 2026-09-15. Planning document, not part of the submission.
> Sources: rubric + template (`rubric_and_template/`), exemplar (structure only),
> `thesis_docs/objective_changes_since_progress_report.md` (authoritative),
> `thesis_docs/comparison_dependency_flowchart.md`, `thesis_docs/phase_execution_guide.md`,
> `thesis_docs/dev_notes.md`, `training_nomenclature.md`, `vision/training/overfit_gates.md`,
> `results/runs.csv`, dataset `PROVENANCE.md` files.
>
> Cite slots: `[cite:key]` = key exists in `thesis/references.bib`.
> `[cite: topic]` = no key yet → `/find-refs`.

---

## 0. Word budget and global notes

| Section (template order) | Rubric weight | Budget | Write order |
|---|---|---|---|
| 1 Introduction | part of /30 | 200 | 6th |
| 2 Literature Review | part of /30 | **1800** | 4th |
| 3 Project Objectives | part of /30 | 270 | **1st** |
| 4 Project Process | /25 | 1000 | 2nd |
| 5 Timeline and Risk Management | /15 | 230 | 5th |
| 6 Progress to Date | /20 | 500 | 3rd |
| Slack | — | 0 | — |
| **Body total** | | **4000** | |

Project Summary (<300 words, not counted) is written last.

**Budget revision (2026-09-16):** rebalanced to push the Literature Review to
~1800 words (from 900) since it and Process are the two highest-value sections
to get right, at the cost of Intro/Objectives/Timeline/Progress. Progress's cut
is weighted toward §6.1/§6.4/§6.5 (narrative) rather than §6.3 (baseline results
+ critical analysis), which keeps most of its original budget since that's the
actual mark-driver in that section. Hard cap is 4,000 words (Intro → Progress to
Date only; confirmed in the proposal guide — excludes title page, contents,
Gantt, references, appendices).

**Working method:** draft every section as fully/well as possible first: do not
pre-cull while writing. Cut for word count at the end, guided by `/evaluate`
output, once the whole draft exists and it's clear which sentences are actually
carrying marks vs which are padding.

**Rubric's bar for the top band, per criterion (verbatim):**
- Intro/LR/Objectives HD: *"Comprehensive coverage of the historical background and state of the art with sound critical analysis and interpretation. Research hypothesis and project objectives clearly stated and discussed in detail."*
- Process HD: *"Excellent description of project process capable of yielding significant, high-quality, and repeatable results."*
- Timeline/Risk HD: *"Detailed timeline submitted with insightful discussion of planned tasks, critical path and milestones. Time assigned to each task is reasonable and justified. Risks are identified and a well-considered management plan is in place."*
- Progress HD: *"Excellent progress to date. Exceeds expectations. Preliminary results are high quality and discussed in detail with critical analysis. Risks are being proactively managed. Project on track to produce outcomes worthy of inclusion in a journal paper."*
- Overview questions that apply everywhere: research gap stated; testable hypothesis; **"clearly stated your intended individual contribution"**; **"all necessary and appropriate resources identified and justified"**.

**Global cautions:**
- Tables are counted by Turnitin and probably by the marker. The exemplar leans on tables. Use them where they replace prose, not on top of it.
- **Stale doc warning:** `thesis_docs/technical_work_timeline.md` still says "combined dataset" and "Mamba-hybrid" in Phases 2–3. Both are superseded (D6; Mamba scrapped). Don't write from that file on those points — use the flowchart and `objective_changes`.
- **Resolved:** sim stack (dev machine) runs ROS2 Jazzy / Ubuntu 24.04; the Jetson runs ROS2 Humble / Ubuntu 22.04, forced by the AR0822 camera driver's L4T support — two separate ROS2 environments by design, not a contradiction. `dev_notes.md` wording fixed accordingly.
- Scope guards: no VOC; datasets never combined (D6); no `tiny/` gate run described as a result; YOLOv12 = area attention, YOLOv13 = hypergraph correlation, YOLO26 is not transformer-based.
- 3rd person, impersonal (template §2.6.1).

---

## 3. Project Objectives — ~270 words (WRITE FIRST)

**Exemplar moves:** hypothesis in 2–3 sentences with a measurable success condition → objectives as labelled blocks, each with one rationale clause → one summary table (objective → mechanism → what's measured) → Significance ending with "the contribution is X, which prior work A and B have not done because…".

### 3.1 Research Hypothesis (~60 words)
- **Point:** Re-state the hypothesis for the current method, not the submitted one.
  - **Differs from progress report:** the submitted hypothesis routes *high-confidence* detections to a VLM for HPI classification. That is no longer the method (`objective_changes`, "O4's routing rule").
  - **Also consider splitting it.** The submitted version is double-barrelled (detection + fleet). Suggest a primary hypothesis (low-altitude onboard detection of persons *and* HPIs holds up under occlusion within the Orin's real-time budget) and a secondary one (a VLM / open-vocabulary stage adds value on low-confidence and never-seen HPI classes only if it beats cheap re-detection). Fleet coordination becomes a subordinate hypothesis or an objective only.
  - **Evidence:** flowchart pre-registered decision criteria (VLM must beat P-2, not P-1).
  - **Rubric hook:** "Research hypothesis … clearly stated and discussed in detail"; overview "Has a research hypothesis been stated that can be tested by the proposed work?"
  - **Make it falsifiable:** name the metric (mAP@50/recall per class, per occlusion bucket), the comparator (P-1 / P-2), and the budget (real-time on Orin Nano Super, 8 GB).

### 3.2 Research Objectives (~130 words + table)
- **Point:** Keep O1–O6 numbering for continuity with the submitted report; add one sentence saying the wording is retained except where noted.
- O1 — occlusion degradation. **Scope note:** person detection only (HERIDAL is person-only; no HPI baseline to drop from). HPI degradation comes from the Weitefeld and bush sweeps and is reported separately, not compared against the person curve.
  - Measured as: P/R/mAP@50 at frozen occlusion buckets 0/10/20/40/60/80 % → degradation curve, not a single before/after number.
- O2 — architecture trade-off. **Differs from progress report:** the candidates are the six named arms, not "YOLO-family and Mamba-hybrid". Answer = accuracy vs latency vs memory/power on Orin, with the n/s/m scale sweep giving the Pareto front.
- O3 — HPI detection reliability. **Now the primary contribution** (`objective_changes`). Measured per class; held-out classes reserved.
- O4 — **wording must change.** Replace the high-/low-confidence routing rule with: does escalation of low-confidence detections (A1 re-detection, then VLM) and open-vocabulary handling of held-out classes recover recall without net precision loss or queue backlog at flight speed.
- O5 — VLM selection (≤2B params, on-device throughput, memory, power).
- O6 — fleet coordination in simulation (time-to-full-coverage, redundant search area). State it is the first objective descoped if time is short.
- **Table (recommended):** Objective | Question | Primary metric | Comparator | Answered in phase/stage.
- **Rubric hook:** "objectives should be clear, specific, and measurable" (template §3.3).
- **Budget:** ~1 sentence each + table.

### 3.3 Significance (~80 words)
- **Point:** Who benefits and how.
  - SAR operators: more usable search in vegetated terrain where current aerial detection is weakest `[cite:bozicstulic2019heridal]`, `[cite:nathan2026weitefeld]`. **RESOLVED 2026-09-18:** time-criticality now cites `[cite:hashimoto2022lostperson]` (searcher-scarcity clause dropped — no confident source found, see gap report note).
  - Engineering community: an occlusion-graded benchmark and an edge-deployment comparison under a fixed 8 GB budget.
  - Template explicitly asks for benefits to affected parties (financial, KPI, health & safety) — one sentence on life-safety / reduced searcher exposure.
- **Point:** Contribution statement, exemplar-style: what prior work has not done.
  - Weitefeld: real forest occlusion, but ~300 m, crewed aircraft, 4 coarse classes, detector fails `[cite:nathan2026weitefeld]`.
  - HERIDAL lineage: open terrain, person only, 45–60 m `[cite:bozicstulic2019heridal]`, `[cite:yolo_sar_drones2025]`.
  - RGB-thermal fusion addresses foliage via a second sensor `[cite:gui2026seeing]`; this project tests how far RGB alone gets at low altitude.
  - None test low altitude + onboard real-time + fine HPI taxonomy + open-vocab/VLM arms + graded occlusion together.
- **Point:** Negative results are valid (VLM not beating A1 / D-arm is a design finding).
- **Individual contribution:** state explicitly what is this student's work vs the team (airframe build, VOC and triangulation are other students' projects). Rubric overview asks for this directly.
- **Rubric hook:** "how the project will contribute useful outcomes to the field".

---

## 4. Project Process (rename: "Methodology and Methods") — ~1000 words (WRITE SECOND)

**Project type:** Design and Build (as declared in progress report). Template §4.3 (design constraints, criteria, tools) and §4.1 (apparatus, procedures, how parameters are computed) both apply.

**Exemplar moves:** one-paragraph overview of the workstreams → sub-sections per workstream, each justifying a tool choice against an alternative → a process/gating flowchart figure.

**Template requirement to hit:** "identify equipment or approaches that are already in place, and those that will be developed". Mark each sub-section with built / to build.

### 4.1 Overview (~75 words + Figure)
- Point: three workstreams — detection/HPI pipeline (offline, then on-device), data (public datasets now, bush collection), fleet simulation.
- Point: the Phase 3 comparisons run as an elimination tournament (~30–40 runs), not a grid (6 × 3 × 4 = 72 pipeline builds before the occlusion sweep multiplies it again).
- **Figure:** simplified version of `COMPARISON_DEPENDENCY_FLOWCHART.drawio` (stages + gates). Own drawing — no citation issue.
  - **DECIDED 2026-09-17: use `tournament_funnel.png`** (repo root, hand-drawn). Content verified against `comparison_dependency_flowchart.md` and the exit rule at `phase_execution_guide.md:1400`.
  - ~~Fix before use — selection rule is inverted.~~ **Resolved 2026-09-19 (user):** the funnel's metric text is a side list, not an ordered rule, so it doesn't contradict §4.4's gate-then-rank rule. No redraw needed.
  - Open question: funnel and flowchart both say "answers O1, O2 and O4", but the final stage evaluates held-out HPI classes and O3 is the stated primary contribution. Confirm whether O3 belongs in that line.
- Rubric hook: "capable of yielding … repeatable results".

### 4.2 Datasets and split protocol (~190 words)
- HERIDAL: person-only, 45–60 m, open terrain; used for pipeline validation and the controlled O1 sweep `[cite:bozicstulic2019heridal]`. Status: built (tiled 1024 px, 0.2 overlap, split by source image).
- Weitefeld: real forest occlusion, multi-class (shelter/object/person; `unknown` dropped, sensitivity check with/without), split by physical finding `[cite:nathan2026weitefeld]`. Status: built on 3 of 15 strips.
  - Caveats to state: ~300 m crewed aircraft; crowd-sourced labels; 14.7 % of person rows "excluded, not checked" → person metrics are a lower bound.
- Own bush dataset: DJI for collection (airframe not flight-ready), stills primary, video captured alongside but tagged `dji_video` and excluded from Phase 3 training. Split by placement, preferably site; clips never span splits. Status: to build.
- Arducam AR0822 validation batch: test-only, never trained on; sole measure of the DJI→Arducam domain gap. No FOV compensation at capture → handled by scale augmentation + pixels-per-target comparison + stated limitation.
- **D6:** datasets kept separate; Phase 3 trains/evaluates on bush data only. One sentence on why (attribution of results to real bush conditions). **D7** init experiment sequenced, reported separately.
- Held-out HPI classes sealed out of every training manifest, verified programmatically before training.
- Ethics / regulatory: person-present sessions need ethics approval; object-only sessions do not. `[cite: CASA Part 101 / excluded-category RPA rules]` — template Process criterion names "relevant Australian and/or International Standards".
- Rubric hook: "databases … relevant Australian and/or International Standards".

### 4.3 Occlusion instrument (~125 words + example figure)
- Point: occlusion fraction measured against **target bbox pixels**, achieved fraction logged per instance.
- Point: four modes (cutout, blobs, texture, foliage); `texture` (vegetation sampled from the same image) is the reported mode — justify vs cutout (wrong texture) and foliage (needs asset library).
- Point: frozen, seeded buckets on disk (seed 42) so every model sees byte-identical images. Status: tool built (`vision/occlusion/occlude.py`).
- Point: label policy — occluded targets keep their full original box (otherwise it becomes a small-object experiment).
- Point: training-time use applies distractor occluders on background to prevent "occluder ⇒ target" shortcut learning.
- Point: O1 confound decomposition. Real bush imagery differs from HERIDAL in three ways at once (occlusion, altitude, camera), so one before/after number can't say which caused a drop. Three tests separate them:
  - **Controlled** — synthetic occlusion sweep (0–80%) on HERIDAL's own images. Same camera/altitude/dataset, only occlusion varies → isolates occlusion alone.
  - **In-the-wild** — the detector run on real bush imagery as collected. The honest deployment number, but occlusion + altitude + camera are confounded together.
  - **Scale-check** — bush imagery downscaled to match HERIDAL's pixels-per-person. Cancels out most of the altitude/camera gap → isolates how much of the in-the-wild drop is occlusion vs. scale/camera.
  - Controlled + scale-check together let the write-up say how much of the in-the-wild number (O1's headline result) is actually attributable to occlusion, rather than reporting one confounded drop and leaving the cause unstated. Evidence: `phase_execution_guide.md` D5.
  - Note: this detail lives in Process, not in O1 itself — O1 was deliberately kept short and plain ("How much do precision, recall, and mAP@50 drop when the baseline detector, trained on open-terrain SAR data, is tested on bush imagery under increasing occlusion?").
- `[cite: cutout / copy-paste / synthetic occlusion augmentation]`, `[cite:pop_infrared2025]` for occluded-person detection context.
- **Figure:** one image at 0 / 40 / 80 % texture occlusion rendered by the tool's verify output.

### 4.4 Detector architecture sweep (~210 words + table)
- Point: admission rule — no architecture requiring custom CUDA kernels for training or export (why: must compile on x86, again on ARM64, then survive TensorRT export; each can fail outright).
- **Table (arm → structural mechanism → why relevant to fragmented occluded evidence):**
  - YOLO11s — plain CNN, local convolution; Phase 1 continuity reference. `[cite: YOLO11 / Ultralytics]`
  - YOLO26s — edge-optimised CNN, NMS-free, DFL-free, optional P2 small-object head. `[cite: YOLO26]`
  - YOLOv12s — area-based self-attention inside a CNN. `[cite: YOLOv12]`
  - YOLOv13s — CNN + hypergraph correlation across non-adjacent regions (HyperACE). `[cite: YOLOv13]`
  - RF-DETR — full transformer, Apache-2.0, leads RF100-VL domain transfer. `[cite: RF-DETR]`, `[cite: RF100-VL]`
  - D-FINE-S — DETR with fine-grained distribution refinement for localisation. `[cite: D-FINE]`
- Point: selection criteria stated before results — highest mAP among arms meeting on-device latency + memory budget; **top two** carried into the A0/A2 head comparison (catches a runner-up that only wins with A2's separate HPI head; ~2 extra runs vs ~120 for a full grid).
- Point: training recipe — full fine-tune vs backbone-frozen on the #1 arm; LoRA considered and rejected for conv detectors (non-standard, no baseline to compare).
- Point: A0 (one multi-class head) vs A2 (shared backbone, person head + HPI head) tests class imbalance; A2b stretch only.
- Point: scale sweep n/s/m on winner → Pareto front (direct answer to O2); `yolo26` vs `yolo26-p2` ablation if YOLO26 wins.
- All from COCO-pretrained weights (D7 side experiment separate).
- Rubric hook: "theoretical frameworks, … models, … techniques".

### 4.5 Pipeline configurations and VLM evaluation (~160 words)
- P-1 detector only (floor) → P-2 + A1 crop re-detection (~10–15 ms, the bar the VLM must clear) → P-3 + async VLM queue (≤2B params) → P-4 open-vocabulary D-arm as a parallel alternative.
- Point: A1 benchmarked before any VLM work (fairness; avoids "baseline tuned to lose").
- Point: VLM metric is candidate-clearance throughput and queue backlog at realistic flight speed, not per-frame latency.
- Point: pre-registered criteria (quote the decision table): A1 adopted if it recovers recall within budget; VLM adopted only if it beats P-2 on held-out classes *and* verification with bounded backlog; D-arm displaces VLM if it matches it at one-forward-pass cost.
- Candidate VLMs (SmolVLM2, Qwen2-VL-2B, Florence-2, InternVL2.5-1B/2B; **Moondream2 dropped 2026-09-20**, no paper) and runtime (llama.cpp / Ollama). `[cite: each VLM]`; edge VLM benchmarking method `[cite:sarwar2026benchmarking]`; small-VLM design `[cite:chu2024mobilevlmv2]`.
- Open-vocab candidates (YOLO-World / YOLOE / OWLv2 / Grounding DINO). `[cite: each]`
- Held-out class evaluation with bootstrap CIs over placements.

### 4.6 On-device evaluation and metrics (~125 words)
- Hardware: Jetson Orin Nano Super 8 GB, JetPack 6.2.x, MAXN SUPER, `jetson_clocks` (DVFS otherwise swings latency 20 %+), NVMe boot + 16 GB swap, `jtop` for power/memory, TensorRT export.
- Metrics: per-class precision, recall, mAP@50, mAP@50-95; latency mean and p95 (model-only vs end-to-end, as in `[cite:sarwar2026benchmarking]`); power (W); memory; VLM throughput/backlog.
- Repeatability: every run logged to `results/runs.csv`, one row per class per run, with git SHA, dataset version, provenance filter, occlusion mode/fraction, device. Pinned environment (torch 2.11.0+cu128, Ultralytics 8.4.138, `uv.lock`).
- Rubric hook: "computational and statistical tools … metrics to be used for evaluating project outcomes"; "repeatable".

### 4.7 Fleet coordination in simulation (~55 words)
- PX4 SITL + Gazebo Harmonic + ROS2 via uXRCE-DDS; single-drone sim (PX4/Gazebo/DDS bridge, custom terrain) already running. Multi-drone/swarm coordination is not yet built (`swarm/` is an empty package stub) — Phase 6 work, not a current result. Sim runs ROS2 Jazzy on the dev machine; the Jetson runs ROS2 Humble (forced by the AR0822 camera driver) — deliberate split, not a bug to resolve.
- Coordination tested against mocked detection messages first; `detection_type` field distinguishes person (converge) from HPI (reprioritise area).
- Metrics: time-to-full-coverage, redundant re-searched area, collaborative vs independent. `[cite: multi-UAV coverage / cooperative search]`

### 4.8 Resources (~60 words, or fold into a table)
- Rubric overview explicitly asks resources be "identified and justified".
- RTX 4070 (WSL2) for all training (**Kaya NOT used — decided 2026-09-19**); Jetson Orin Nano Super (~US$399 after July 2026 price rise, within $1500 project budget); DJI drone; Arducam AR0822; CVAT; licences (Ultralytics AGPL vs RF-DETR Apache-2.0).
- Justify the Jetson choice briefly: TensorRT/CUDA maturity and the most common embedded platform in published UAV-SAR detection work (`companion_computer_choices.md`) `[cite: Jetson use in UAV SAR detection]`, `[cite:yolo_sar_drones2025]`.

---

## 6. Progress to Date — ~500 words (WRITE THIRD)

**Exemplar moves:** one line "on schedule against the Gantt" → completed tasks → a validated-parameters table → a figure of real output. Ours can go further: the rubric's top band wants *critical analysis* of results, and there are real results to analyse.

### 6.1 Status against timeline (~50 words)
- Point: Phase 0 and most of Phase 1 complete; name what's done vs outstanding with dates from git log:
  - 2026-09-03 training environment built (P0.4)
  - 2026-09-05/06 HERIDAL and Weitefeld acquired (checksums verified) and converted
  - 2026-09-06/07 overfit gates passed; Baselines A and B trained and logged (2026-09-07)
  - Occlusion tool built (`occlude.py`)
  - Sim stack operational — single-drone only (PX4 SITL + Gazebo Harmonic + ROS2 Jazzy bridge, custom real-world terrain). Multi-drone support was claimed in the progress report but does not exist yet (`swarm/` package is an empty stub) — do not repeat that claim.
- Outstanding in Phase 1: test-set evaluation (P1.4 eval harness), controlled occlusion sweeps (P1.6), TensorRT/on-device baseline (P1.7).
- Rubric hook: "Refer to your timeline to identify tasks completed and work remaining" (template §6).

### 6.2 Data pipeline validation (~70 words)
- Point: overfit gates as a trust gate before any reported training — a pipeline must memorise 20 tiles to mAP@50 > 0.95. Don't call these results.
- **Critical-insight point:** Weitefeld gate 1 exposed a box-origin convention bug (paper describes a "lower-left corner" without stating y direction). Invisible on large shelter boxes, obvious on small person boxes → caught only by rendering small targets. Fixed with `--box-origin bottomedge`, verified by hand against a raw row. Lesson: coordinate bugs don't show in aggregate metrics.
- **Critical-insight point:** gate 2 zero result diagnosed as an undertrained model (uniform floor-confidence grid when rendered at near-zero threshold), not a geometry bug → re-sampled per class, 300 epochs → all three classes converged (mAP@50 0.861 overall).
- Point: label-noise discovery — 281 of 1,909 person rows (14.7 %) marked "excluded, not checked".
- Point: split-by-unit protocol (source image / physical finding) prevents near-duplicate leakage.
- Rubric hook: "Risks are being proactively managed"; "discussed with critical analysis".

### 6.3 Baseline results (~220 words + table)
- **Table:** run | dataset | split | class | P | R | mAP@50 | mAP@50-95 (from `results/runs.csv`; yolo11s, 150 epochs, imgsz 1024, batch 8, RTX 4070).
  - Baseline A, HERIDAL, val: person P 0.922, R 0.900, mAP@50 0.954, mAP@50-95 0.641.
  - Baseline B, Weitefeld 3-class, val: person 0.705 / 0.226 / 0.331 / 0.114; object 0.090 / 0.123 / 0.019 / 0.005; shelter 0.000 / 0.000 / 0.0001 / 0.00001.
- **Baseline A analysis:**
  - Point: pipeline validated on a known dataset; score is high, as expected for open terrain.
  - **Hedge required:** val split, not test (test eval pending P1.4). Not directly comparable to the HERIDAL paper's 88.9 % detection rate `[cite:bozicstulic2019heridal]` (different metric) or Ciccone & Ceruti's 0.802 mAP@50 `[cite:yolo_sar_drones2025]` (different split/tiling). Say so explicitly — that *is* the critical analysis.
- **Baseline B analysis:**
  - Point: person class clears the published near-failure on the same dataset (`[cite:nathan2026weitefeld]` report YOLOv12 average confidence ~0.016 %). **Hedge:** different metric (confidence vs mAP), 3 of 15 strips, tiled at 1024 px with min-visible filtering, `unknown` dropped → not a like-for-like comparison. Person metrics are a lower bound (label noise).
  - Point: precision ≫ recall for person (0.705 vs 0.226): the model is conservative; many true targets sit below the default confidence threshold. Author's reasoning to check against `BoxPR_curve.png` / `BoxR_curve.png` before claiming: this is the population the low-confidence escalation arm (A1/VLM) targets.
  - Point: shelter ≈ 0 and object ≈ 0.02 despite shelter reaching 0.972 in the overfit gate → the classes are learnable in principle; the full-data failure needs explaining. Candidate explanations to *check, not assert*: instance count per class in 3 strips; tiling splitting large shelters across tiles (min_visible 0.3); class imbalance vs person; ~300 m pixels-on-target argument from the dataset authors.
  - Point: the result supports the low-altitude premise (pixels-on-target), not proves it — keep the claim to "consistent with".
- Rubric hook: "Preliminary results are high quality and discussed in detail with critical analysis".

### 6.4 Changes since the progress report and risks that eventuated (~100 words)
- Scope: VOC transferred to another student.
- Weitefeld added (why: multi-class validation, de-risks ethics/collection on the critical path, published failure baseline).
- Datasets kept separate (D6), reversing the combined-dataset plan.
- SSM/Mamba arms scrapped under the custom-CUDA admission rule; six-arm sweep instead.
- O4 routing rule revised; VLM role narrowed to low-confidence verification and held-out classes; A1 baseline and D-arm added; occlusion reframed as a graded sweep.
- Risks that eventuated and how handled: box-origin ambiguity (render-verify); label noise (lower-bound reporting); PyTorch `cu121` index removal (moved to `cu128`); Jetson price increase (within budget).
- Rubric hook: "Discuss any risks that have eventuated and your actions to manage them. Also describe any changes to the timeline." (template §6)

### 6.5 Next steps (~60 words)
- Test-set eval harness → controlled occlusion sweeps on HERIDAL and Weitefeld → TensorRT on Orin → HPI taxonomy lock + object-only bush collection.

---

## 2. Literature Review — ~1800 words (WRITE FOURTH)

**Exemplar moves:** opens with a short framing paragraph that states the problem the review converges on → thematic sub-sections, each ending with what it means for *this* project → a critical table mapping each design choice to supporting literature, opposing literature, and the rebuttal. That last table is the clearest "critical analysis" signal in the exemplar; reuse the *move*, not the content.

**Budget reality (revised 2026-09-16):** ~1800 words over seven themes, matching
the exemplar's own LR weight (it ran ~2000+ words, over half its 3978-word
total). Still prioritise critical comparison over description, but there's now
room for the per-arm evidence table and fuller treatment of 2.4 without
starving the other themes.

**Framing paragraph (~110 words):** detection in open terrain is largely solved at altitude; forest occlusion is not; onboard constraints narrow what can be deployed.

### 2.1 Aerial person detection for SAR (~320 words)
- History: two-stage detectors (Faster R-CNN) `[cite:ren2017fasterrcnn]` → HERIDAL-era SAR pipelines `[cite:bozicstulic2019heridal]` → single-stage YOLO dominance for real-time `[cite:yolo_sar_drones2025]`, `[cite:botea2026lostperson]`.
- State of the art / taxonomy: survey's four method groups (scale/perspective-aware, sample-oriented sparse, information fusion, lightweight on-device) `[cite:zhang2025aerialsurvey]`.
- **Critical point:** reported accuracies come from open terrain at 45–60 m or from visible subjects; they don't transfer to canopy. Speed figures are hardware-dependent (Faster R-CNN 5–17 fps on workstation `[cite:ren2017fasterrcnn]`; YOLO ~2 fps on Jetson Nano without TensorRT `[cite:yolo_sar_drones2025]`).
- **Critical point:** Botea et al. use YOLO11n/s but evaluate on a custom set and video; mAP@50-95 weak → localisation, not recognition, is the gap `[cite:botea2026lostperson]`.
- Relevance: justifies YOLO11s as continuity reference and the need for on-device numbers alongside mAP.

### 2.2 Occlusion and vegetation (~280 words)
- Occluded-person datasets and why standard pedestrian-trained detectors fail on partially occluded, non-standing subjects `[cite:pop_infrared2025]`.
- RGB-thermal fusion as the sensor-side answer to foliage `[cite:gui2026seeing]`. **Critical:** strong result but needs a second, costlier sensor and aligned data; scoped out on cost. This thesis asks how far RGB goes first.
- Synthetic occlusion as an evaluation instrument. **DECIDED 2026-09-17:** cite `[cite:devries2017cutout]` here (general grounding claim only — one source, per gap report). `[cite:ghiasi2021copypaste]` held back for Process §4.3, where it grounds the `--distractor-rate` mechanism specifically (pasting occluder copies at background locations to block "occluder texture ⇒ target" shortcut learning) — that's the actual Copy-Paste-shaped operation in `occlude.py`, not the default `texture` mode, which self-samples from the same image and isn't a clean match for either paper.
- **Critical:** synthetic occluders risk shortcut learning and don't reproduce real canopy — hence distractors and a real-occlusion cross-check.
- Relevance: motivates graded sweep + full-box label policy.
- **Figure — DECIDED 2026-09-17:** `figures/nomad_yolov8l_visibility_map.png` (extracted from NOMAD `[cite:bernal2024nomad]`, page 8). YOLOv8l mAP@0.5:0.95 vs. visibility level at 5 distances — performance collapses toward zero past ~50 m regardless of visibility, and drops steeply even at 10 m below visibility ~60. Chosen over a qualitative photo since 2.1 already carries one (HERIDAL); this pairs "why it's hard" (2.1) with "what it costs in mAP" (2.2). Reproduced figure, so caption uses "Adapted from".
  - Caption (~20 words): *"Fig. X. YOLOv8l detection performance vs. NOMAD visibility level, by distance. Adapted from `[cite:bernal2024nomad]`."*

### 2.3 Real forest SAR data: Weitefeld (~240 words)
- What it is: real search operation, 10,659 images, 34,424 boxes, 405 findings, 4 classes, real canopy `[cite:nathan2026weitefeld]`.
- **Critical point (published failure):** YOLOv12 effectively fails; authors attribute it to too few pixels on occluded clues at ~300 m / 3–5 cm per pixel.
- **Critical point (limitations):** crewed aircraft, not UAV; coarse classes; crowd-sourced subjective labels; `unknown` class semantically messy; person-label noise found in this project.
- **Novelty differentiator:** low altitude, onboard real-time, finer HPI taxonomy, open-vocab/VLM arms, multi-drone — none addressed there.
- Relevance: independent evidence for the low-altitude premise and the multi-class validation set.
- **Figure — DECIDED 2026-09-17: `altitude_ladder.png`** (repo root, hand-drawn). Place here: by 2.3 the reader has met HERIDAL's 45–60 m (2.1), and this is where Weitefeld's ~300 m is argued, so the comparison lands when it's being made. Can be pointed back to from the Introduction. Numbers verified against sources (300 m/1000 ft, 3–5 cm/px, 45–60 m, Sci. Data 13:747).
  - **Fixes before use:** (1) remove the baked-in "Nathan et al., Scientific Data 13:747 (2026)" footnote from the image — it's author-year and clashes with IEEE numbered; attribution goes in the caption. (2) Add "not to scale" — altitude axis spacing isn't proportional. (3) Cite HERIDAL's altitude as well as Weitefeld's.
  - Caption (~25 words, captions count toward limit): *"Fig. X. Operating altitude of HERIDAL `[cite:bozicstulic2019heridal]`, Weitefeld `[cite:nathan2026weitefeld]` and the proposed system. Not to scale; silhouette sizes illustrate relative target size in frame."* Own drawing, so no "Adapted from".

### 2.4 Detector architectures for occluded small targets (~380 words)
- Group, don't list: local convolution (YOLO11) → edge-simplified CNN (YOLO26) → attention within CNN (YOLOv12) → high-order/global correlation (YOLOv13) → full transformers (RF-DETR, D-FINE). `[cite: each arm's originating paper/report]` — **all currently missing**.
- **Critical point per group, one clause each:** what mechanism might help reconnect fragmented visible evidence; what it costs (latency, export risk, data hunger of transformers on small datasets).
- State-space lineage as its own paragraph: Mamba for sequences `[cite: Mamba, Gu & Dao]` → Vision Mamba, bidirectional scan `[cite:zhu2024visionmamba]` → VMamba SS2D four-way scan, linear complexity `[cite:liu2024vmamba]` → MambaNeXt-YOLO detection hybrid `[cite:mambanextyolo2025]`.
  - **Critical point:** exclusion is a deployment-risk scope decision (custom `selective_scan` kernels, ARM64 compile, TensorRT export), not a judgement on accuracy. State it here so the marker doesn't ask.
- **Recommended table (exemplar's critical move):** arm → supporting evidence → weakness/opposing evidence → why still included / excluded.
- Relevance: justifies the six arms spanning distinct mechanisms rather than YOLO versions.

### 2.5 Open-vocabulary detection (~170 words)
- Text-prompted detectors (YOLO-World, OWLv2, Grounding DINO, YOLOE) `[cite: each]`.
- **Critical point:** one forward pass, no generation → sits between closed-set detectors and VLMs on latency; unknown robustness on tiny aerial objects `[cite: open-vocab on aerial/small objects]`.
- Relevance: the D-arm and the most likely displacer of the VLM on held-out classes.

### 2.6 Onboard vision-language models (~190 words)
- Small VLM design for mobile hardware `[cite:chu2024mobilevlmv2]`; local VLM benchmarking on edge hardware, model vs end-to-end latency `[cite:sarwar2026benchmarking]`.
- Aerial VLA precedent: onboard VLA on drones `[cite:chen2025gradnavpp]`; dual-rate scheduling on Jetson AGX Orin, pre-fill dominates latency `[cite:williams2026litevlah]`.
- **Critical point:** these run on larger Orin modules (AGX) or target navigation/guidance, not detection verification; prefill-dominated latency supports the async-queue design and throughput metric instead of per-frame latency.
- **Critical point:** a VLM re-labelling what a trained detector already labelled adds latency for no information → VLM role confined to low-confidence verification and unseen classes.
- Relevance: justifies ≤2B cap, async design, and the "must beat A1" criterion.

### 2.7 Research gap (~110 words, or end of 2.6)
- One tight synthesis: no study combines low-altitude onboard detection, graded occlusion, a fine HPI taxonomy, and a fair cheap-baseline test of VLM/open-vocab arms under an 8 GB edge budget. Leads straight into §3.

**DECIDED 2026-09-18:** multi-drone coordination (O6) gets no LR paragraph. Reasoning: the core project is the single-drone pipeline; the fleet is a later, secondary objective the user's teammates own their own airframes for. O6 stays covered where it already is — Objectives §3.2 (O6, explicitly the first objective descoped if time is short) and Timeline/Risk §5 (descoping order) — not duplicated in the LR. No citation needed here as a result.

---

## 5. Timeline and Risk Management — ~230 words (WRITE FIFTH)

**Exemplar moves:** one paragraph pointing to the Gantt appendix and naming the critical path as a dependency chain → one sentence on schedule status → risk register table; explicitly states "no significant environmental risk".

**Budget reality (revised 2026-09-16):** cut hardest of any section (500→230)
to fund the LR/Process increase — defensible since it's the lowest-weighted
criterion (/15) and the Gantt chart itself (not word-counted) carries most of
the timeline content; the risk register table does most of §5.2's work too.

### 5.1 Timeline (~100 words + Gantt in appendix)
- Point: Gantt in Appendix, updated from the progress report version (phases 0–7 mapped to Sem 1 remainder + Sem 2 weeks, with milestones).
- Milestones: Proposal; Phase 1 complete (sweeps + on-device baseline); HPI taxonomy locked; ethics decision; Gate 0 (bush data usable); Gates 1–4; VLM decision; final thesis submission. `[gap: unit milestone dates for Sem 2]`
- **Critical path (changed since progress report — say so):**
  - Before: ethics → data collection → everything.
  - Now: bush dataset collection + annotation → Gate 0 → architecture sweep → training recipe → head comparison → pipeline configurations (A1 strictly before VLM) → occlusion sweep + held-out evaluation → write-up.
  - Why it changed: Weitefeld provides multi-class data and Phase 1 sweeps produce results with no collected data; object-only collection proceeds without ethics.
- Hard ordering constraints (three): A1 before VLM; architecture before head configuration; seal verification before held-out eval.
- **Time justification (rubric HD wants "reasonable and justified"):** run budget ~30–40 runs; baseline run cost from the Phase 1 logs (150 epochs, 1024 px on RTX 4070) × runs → hours on the RTX 4070 alone (no Kaya). `[gap: wall-clock hours per baseline run]`
- Slack / descoping order: Phase 7 → Phase 6 → Phase 5 → A2b stretch. Phase 6 can start early on mocked detections.

### 5.2 Risk management (~130 words incl. table)
Columns: risk | type | likelihood | consequence | mitigation. Only real risks — the template warns you can lose marks for padding.

- **Safety — UAV flight at 5–10 m near people/volunteers.** Medium consequence. Mitigation: CASA RPA operating rules `[cite: CASA]`, landholder permission, object-only sessions don't involve people, standard pre-flight procedure.
- **Environmental:** likely none significant beyond site access and minimal-disturbance flying → say so in one sentence (or name wildlife disturbance / fire-season restrictions only if they actually apply to chosen sites).
- **Financial — hardware price volatility.** Jetson rose from US$249 to ~US$399 (July 2026); within $1500 budget. Low likelihood of further impact.
- **Project outcome — ethics delay for person-present data.** Mitigation: object-only sessions first; Weitefeld as multi-class fallback.
- **Project outcome — weather/logistics delay bush collection (critical path).** Mitigation: staged sessions, annotate per session, Weitefeld fallback, DJI (not airframe) for collection.
- **Project outcome — separate-repo arms (YOLOv13, RF-DETR, D-FINE) fail TensorRT/ARM64 export.** Mitigation: admission rule, export test early, three Ultralytics-native arms guarantee a result.
- **Project outcome — 8 GB memory makes the VLM arm infeasible.** Mitigation: ≤2B cap, quantisation, NVMe swap, async queue; negative result pre-registered as valid.
- **Project outcome — held-out class leak invalidates headline result.** Mitigation: programmatic seal assert before every training run.
- **Project outcome — DJI→Arducam domain gap.** Mitigation: Arducam test-only batch, scale augmentation, pixels-per-target comparison, stated limitation.
- **Project outcome — airframe not flight-ready (other student's build).** Mitigation: simulation + bench/pre-recorded footage fallback.
- **Data loss.** Datasets gitignored and tracked via PROVENANCE with checksums; code/results in git. `[gap: backup location for raw data and checkpoints]`
- Rubric hook: "Risks are identified and a well-considered management plan is in place."

---

## 1. Introduction — ~200 words (WRITE SIXTH)

**Exemplar moves:** open with the operational problem → quantified prior result (with a number) → the failure/limitation → root cause → one paragraph on what this thesis does. No lit-review depth here.

**Budget reality (revised 2026-09-16):** cut from 300→200 to help fund the LR
increase. Tightest of the three P1/P2/P3 beats, not a dropped one — the rubric
still wants problem, evidence, and project framing all present.

- **P1 — the problem (~60 words):** lost-person SAR in vegetated terrain is time-critical; aerial imagery helps in open ground but canopy hides people and their traces. **RESOLVED 2026-09-18:** cite `[cite:hashimoto2022lostperson]` for time-criticality (survival rate decreases as search time passes, per its own abstract) `[cite:zhang2025aerialsurvey]`. Searcher-intensiveness clause dropped — no confident source found (see gap report note); don't reintroduce without one.
  - Stakeholders (template §3.1 asks for implications for interested parties): SAR agencies/police/SES, volunteer searchers, missing persons. `[cite: Australian SAR context, optional]`
- **P2 — what works and what doesn't (~80 words):** HERIDAL-lineage systems perform well on open terrain at 45–60 m (88.9 % detection rate) `[cite:bozicstulic2019heridal]`; on real forest imagery at ~300 m a modern YOLO effectively fails `[cite:nathan2026weitefeld]`; detectors trained on unoccluded data degrade on occluded subjects `[cite:pop_infrared2025]`. Root-cause framing: pixels-on-target and fragmented visible evidence, under an onboard compute limit.
- **P3 — this project (~60 words):** low-altitude (5–10 m) onboard pipeline on Jetson Orin Nano Super; persons plus human-presence indicators as the primary contribution; graded occlusion evaluation; fair test of VLM and open-vocabulary stages against cheap re-detection; multi-drone coordination in simulation. One sentence on individual contribution within the team.
- Optional closing sentence on report structure (template says not required).
- Rubric hook: "sufficient background for the reader to understand the context of the project, the problem statement/hypothesis".

---

## Evidence gaps (resolve before writing — don't bluff these)

**Missing literature (highest priority, blocks §2.4–2.6):**
1. ~~YOLO11 / Ultralytics, YOLO26, YOLOv12, YOLOv13, RF-DETR (+ RF100-VL), D-FINE — no keys.~~ **RESOLVED 2026-09-18/19:** all present — `sapkota2025yoloevolution` (YOLO11/YOLO26), `tian2025yolov12`, `lei2025yolov13`, `robinson2026rfdetr`, `robicheaux2025rf100vl`, `peng2025dfine`.
2. ~~Mamba (Gu & Dao) — the root of the state-space lineage paragraph.~~ **RESOLVED:** `gu2024mamba` present.
3. ~~Open-vocabulary detectors: YOLO-World, OWLv2, Grounding DINO, YOLOE.~~ **RESOLVED 2026-09-19:** `cheng2024yoloworld`, `minderer2023owlv2`, `liu2024groundingdino`, `wang2025yoloe` all present, checked against `papers/` PDFs.
4. ~~The actual candidate VLMs: SmolVLM2, Qwen2-VL, Moondream2, Florence-2, InternVL2.5-1B/2B.~~ **RESOLVED 2026-09-19:** `marafioti2025smolvlm`, `wang2024qwen2vl`, `xiao2024florence2`, `chen2024internvl25` all present (Florence-2/InternVL2.5 vetted and moved out of `temp_papers/`). Moondream2 still has no paper — stays design-context-only, not a citable candidate. `chu2024mobilevlmv2` remains design-context only, not a candidate.
5. Multi-UAV cooperative search / coverage (O6) — **DECIDED 2026-09-18: not needed.** O6 gets no LR paragraph (see §2.7 decision); stays covered in Objectives/Timeline only.
6. ~~Synthetic occlusion / cutout augmentation.~~ **RESOLVED:** `devries2017cutout`, `ghiasi2021copypaste` present, both used in §2.2.
7. ~~SAR operational context (time-criticality, lost-person behaviour / clue finding).~~ **RESOLVED 2026-09-18:** `[cite:hashimoto2022lostperson]` added (Hashimoto et al., *Scientific Reports* 12:5873, 2022; PDF in `papers/`). Covers time-criticality only — searcher-scarcity/resource-intensiveness has no confident source and was dropped from both P1 and §3.3, not added back without one.
8. CASA RPA regulations (standards criterion).
9. Jetson in published UAV-SAR detection (the companion-computer doc names an MDPI Drones 2025 thermal paper — verify before use).

**Missing project facts:**
- Ethics status (submitted? confirmed unnecessary for object-only?).
- Jetson Orin Nano Super: arrived and brought up? Any on-device number yet?
- ~~Kaya HPC account status.~~ Not used for this project (2026-09-19).
- HPI taxonomy and held-out classes: locked (P0.2)? Needed to state O3 concretely.
- Occlusion sweeps (P1.6): not in `runs.csv` → not run yet. **Biggest single lever on Progress to Date** — a first degradation curve would move that section up a band. Your call whether there's time before Day 4.
- Test-set evaluation for Baselines A/B (runs.csv says "test-set eval pending").
- Baseline B per-class instance counts (needed to interpret shelter ≈ 0).
- Wall-clock training time per baseline run (for timeline justification).
- ~~Sim stack: ROS2 Jazzy vs Humble contradiction~~ — resolved, deliberate split (see §4.7). Multi-drone support confirmed NOT built yet — swarm package is an empty stub.
- Semester 2 milestone dates for the Gantt.
- Bush collection: any sessions or site recon done yet?
- Raw data / checkpoint backup location.

---

**Which point do you want to draft first?** Suggested: §3.1 Research Hypothesis — every other section depends on its final wording.
