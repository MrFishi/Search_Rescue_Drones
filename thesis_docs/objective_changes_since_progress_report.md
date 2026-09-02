# Objective Changes Since Progress Report

This note exists so a fresh chat in this project has the current state of the thesis without having to infer it by comparing the progress report against later files. The progress report (`GENG4411ProgressReport_Roy_23921699.pdf`) is still valid as a formative document; nothing below invalidates it, it just records what's changed since it was submitted.

## Team scope change

VOC (voice/operator control interface) is no longer part of this thesis track. A different student on the team has picked that up. This thesis is now vision/AI only: detection, classification of human-presence indicators, and the multi-drone search coordination that consumes those detections.

## Core problem statement and objectives (O1-O6): unchanged

The research problem statement and O1 through O6 as written in the progress report still hold, word for word. What's changed is emphasis and the experimental design underneath them, not the wording of the objectives.

## One exception: O4's routing rule no longer matches the method

O4 as submitted reads:

> Does routing low confidence detections to an onboard VLM for verification, and high confidence detections for indicator classification, recover recall and mAP@50 without a net precision loss or without breaching the real-time latency budget on the Orin Nano Super?

Section 3.3 of the methodology describes the same rule: high-confidence detections go to the VLM for indicator classification, low-confidence detections go to the VLM for verification.

The "high confidence → VLM for indicator classification" half of that rule is no longer what's being built. If the detector is trained multi-class on HPI categories, it has already classified the box by the time it's high-confidence; sending that box to a VLM to relabel something already labelled adds latency for no new information. This was flagged as a weak point in the original design and the method has moved on from it.

What replaces it: the VLM's role is now confined to (a) verifying low-confidence detections, benchmarked specifically against a cheap re-detection baseline rather than against nothing, and (b) handling HPI classes the detector was never trained on, evaluated via a held-out-class split. High-confidence detections are not routed to the VLM at all under the current plan; classification of known classes is left to the detector itself.

O4's underlying question, whether VLM involvement recovers recall/mAP without a net precision loss or breaching the latency budget, is still exactly what's being tested. Only the routing mechanism described in the objective's wording and in section 3.3 is out of date. This is worth flagging explicitly rather than leaving implicit, since the objective's phrasing and the actual method now disagree on one detail.

## What's actually shifted

**HPI detection promoted to the primary contribution.** Originally the VLM verification layer and the person-detection pipeline were roughly co-equal focuses. Human-presence indicators (backpacks, clothing, footprints, shelters, discarded gear) are now the centre of the thesis, on the reasoning that HPIs are the harder, less-studied problem and the more novel contribution, especially compared to well-covered person detection on datasets like HERIDAL.

**VLMs are no longer the main pipeline differentiator, but they're still being tested.** The original framing was "does adding a VLM on top of a detector improve accuracy enough to justify the latency." That's a weak experiment on its own, since a well-tuned closed-set detector or a cheap high-resolution re-detection pass on low-confidence crops can likely match a VLM's classification of things it was already trained to recognise. The VLM's role has moved to where it has a structural advantage a closed-set detector doesn't have: open-vocabulary handling of HPI classes the detector was never trained on. VLMs are evaluated in an async, queue-based role (verifying low-confidence detections, handling held-out classes) rather than sitting inline on every frame.

**A middle tier was added: open-vocabulary detectors.** YOLO-World and OWLv2-style models sit between closed-set detectors and VLMs. They accept text-prompted classes at inference time without the latency cost of a generative language model, since they're still a single fast forward pass. This is a new experimental arm (the "D arm") not in the original progress report.

**Two-pipeline comparison reframed as an architecture question, not two products.** The original idea was a detector-only pipeline vs a detector-plus-VLM pipeline, with the detector-only version potentially using two separate models (one for people, one for HPIs). That's been refined: rather than two fully independent models, the main comparison is a single multi-class detector (one backbone, one head) against a shared-backbone, two-head variant, to test whether HPI classes need architectural separation to avoid being drowned out by the much larger volume of person training examples. Two fully independent models remains a possible extension if time allows, but isn't the default plan.

**Explicit baseline added ahead of VLM work.** Before any VLM comparison happens, a cheap baseline is built and benchmarked: re-running the same detector on low-confidence crops at higher resolution. This exists so the VLM arm is compared against a real, cheap alternative rather than against nothing.

**Occlusion evaluation reframed as a continuous sweep, not a single before/after number.** Performance is now measured across graded synthetic occlusion levels (0 to 80 percent of target pixels covered), producing a degradation curve per model rather than one accuracy figure on "occluded data."

**Dataset plan finalised, then revised — see "Dataset decisions" below.** The original plan was to combine HERIDAL, augmented/occluded versions of it, and a newly collected HPI-focused dataset into one training set. That combination has since been dropped: the datasets are now kept separate (see D6 below). Data collection still uses a DJI drone rather than the project's own airframe, which isn't flight-ready, with a small validation set captured on the actual Arducam once calibrated. A subset of HPI classes remains deliberately held out of training to test open-vocabulary detection and VLM performance on genuinely novel classes.

## Second dataset added: Weitefeld

A second public dataset has been brought in alongside HERIDAL: Nathan et al., "An aerial color image anomaly dataset for search missions in complex forested terrain," *Scientific Data* 13:747 (2026), doi:10.1038/s41597-026-07101-w, Zenodo record 15848419.

It is aerial imagery from a real search operation in a German forest: 10,659 labelled images at 8416x6032, 34,424 bounding boxes across 405 physical findings, with four classes (unknown, shelter, object, person) covering tarps, tents, barrels, fire pits, hunting stands and similar. Real vegetative occlusion rather than staged or synthetic.

Three reasons it's in scope:

1. **It closes a validation gap.** HERIDAL is single-class, person-only, so it structurally cannot validate the multi-class machinery the thesis now depends on: per-class HPI metrics, class-imbalance handling, the A0-vs-A2 head comparison, held-out-class evaluation. Weitefeld can.
2. **It de-risks the critical path.** Ethics approval and dataset collection were previously the single point of failure for the whole project. With Weitefeld available, a delay there is no longer fatal, since there is real multi-class HPI data to develop and test against in the meantime.
3. **It supplies a published failure baseline.** The original authors trained YOLOv12 on it and it effectively failed, reporting 0.016% average confidence and 2.6% maximum. Their diagnosis is that at roughly 300 m altitude and 3-5 cm per pixel, occluded clues occupy too few pixels to carry learnable appearance. That is an independent, peer-reviewed argument for exactly what this thesis is testing: whether flying at 5-10 m instead recovers enough pixels-on-target to make the problem tractable.

It is also a novelty consideration, not just a resource, and is treated as one in the literature review. The differentiators for this thesis against that work are low altitude, the onboard real-time constraint, finer HPI class granularity, the open-vocabulary and VLM arms, and multi-drone coordination — none of which it addresses.

Caveats recorded in the methodology: 300 m from a crewed aircraft rather than 5-10 m from a UAV; four coarse classes rather than the finer HPI taxonomy; crowd-sourced labels from 160 volunteers with the subjectivity that implies; and the "unknown" class being semantically messy, so primary runs exclude it with a with-and-without sensitivity check reported.

## Objective scope clarification: O1 applies to person detection only

O1 asks about the performance drop when a detector trained on open-terrain SAR data is applied to occluded bush imagery. The only open-terrain SAR dataset available is HERIDAL, which is person-only. There is therefore no HPI baseline in it to measure a drop from, and O1 is in practice a person-detection objective.

The HPI occlusion story comes from two other places instead: the synthetic occlusion sweep applied to Weitefeld's real HPI classes, and the sweep applied to the project's own collected bush data. These are internally controlled but come from different source datasets, so the person degradation curve and the HPI degradation curve are reported as separate results rather than compared directly against each other.

## Dataset decisions

**D6 — HERIDAL, Weitefeld and the collected bush dataset are kept separate.** They are not combined into a single training set, which supersedes the original plan recorded above. HERIDAL and Weitefeld are confined to pipeline validation and their own occlusion sweeps; every Phase 3 experiment trains and evaluates on the collected bush dataset only. The reason is interpretability: with the datasets combined, a result cannot be attributed to real bush conditions rather than to HERIDAL's easier open terrain, which matters directly for interpreting the occlusion sweep.

**D7 — initialisation is a separate question from mixing.** All Phase 3 arms start from COCO-pretrained weights by default. One clearly labelled side experiment compares COCO initialisation against Weitefeld-pretrained initialisation on the sweep's top-ranked architecture only. This does not violate D6, since the datasets are sequenced rather than mixed, and "does domain-relevant pretraining beat generic pretraining for SAR detection" is a worthwhile minor finding. It is reported separately from the main results and does not feed the architecture tournament.

**Stills primary, video collected alongside.** This was briefly scoped as stills-only and has been revised. Stills are the detector training set — confirmed with the lecturer that this does not affect the classification model, which is correct, since a detector trains on independent frames regardless of source. Video is captured in parallel at the same sessions regardless, on the reasoning that a training run can always be repeated without the video but a field session cannot be repeated to add it. The asymmetry between cheap-to-have and expensive-to-lack makes collecting it the right call even if the temporal arm ultimately doesn't work out.

Consequences handled explicitly:

- Video is kept **out of** the Phase 3 detector training set, tagged `dji_video` and filtered explicitly rather than by intention. Sampling frames into it would let a single placement contribute dozens of near-identical boxes and skew class balance toward whatever happened to be filmed longest. Instance targets remain placement-based and unchanged.
- Phase 5's temporal accumulation arm is retained, now with two independent evidence lines rather than one: own drone video for true temporal accumulation across consecutive frames of a continuous pass, and Weitefeld's multi-view back-projections (each finding captured from up to 85 angles) for viewpoint-diversity accumulation on real forest occlusion at scale. These are reported as **different claims** — the first concerns whether the deployed flight pattern naturally accumulates evidence over time, the second whether angle diversity helps in principle — since conflating them would overstate what either establishes.
- Tracking becomes new technical work: associating detections of the same object across frames so evidence can be aggregated. ByteTrack and BoT-SORT ship with Ultralytics so this is not from-scratch, but identity switches and track fragmentation under occlusion are precisely the condition being studied, so tracker choice and tuning is treated as its own sub-experiment rather than assumed to work on defaults.
- Temporal passes must be flown slow and steady for consecutive frames to overlap meaningfully; pass speed is recorded in the session log. Target is at least 15 slow-pass clips across at least three sites.
- Annotation is per-still for the detector set, with CVAT frame interpolation used only for the temporal video subset.
- Split hygiene: split by placement at minimum and by site preferably, and never split a video clip across train, validation and test.

**No FOV compensation between the DJI and the Arducam.** Images of the same subject are captured at varied angles and positions directly, rather than correcting for the lens difference by adjusting altitude. This gives viewpoint diversity, which helps generalisation, but viewpoint diversity and scale matching are orthogonal: the DJI's narrower field of view still puts more pixels on a target at a given height than the 145-degree Arducam will. That scale component is therefore uncontrolled at capture time and is handled at training and reporting time instead — aggressive scale augmentation, an explicit comparison of the pixels-per-target distributions between the DJI training set and the Arducam validation batch, and a stated limitation in the thesis. The Arducam validation batch consequently becomes the sole measurement of the DJI-to-Arducam domain gap rather than a supporting check.

## Detector candidate scope expanded

The architecture sweep now spans six candidates rather than the two families originally scoped, with one hard admission rule: **no architecture requiring custom CUDA kernel compilation.**

| # | Model | Structural axis | Cost |
|---|---|---|---|
| 1 | YOLO11s | Pure CNN, local convolution; Phase 1 continuity | Free, Ultralytics-native |
| 2 | YOLO26s | Edge-optimised CNN, NMS-free, DFL-free | Free, Ultralytics-native |
| 3 | YOLOv12s | Area-based self-attention inside a CNN | Free, Ultralytics-native |
| 4 | YOLOv13s | Hypergraph, global high-order correlation | Moderate, separate repo |
| 5 | RF-DETR | Full transformer, Apache-2.0, domain-transfer leader | Moderate, separate repo |
| 6 | D-FINE-S | DETR with distribution-refinement regression | Moderate, separate repo |

YOLO26 (Ultralytics, January 2026) brings DFL-free regression, native end-to-end NMS-free inference, ProgLoss, Small-Target-Aware Label Assignment and the MuSGD optimizer, and was benchmarked by Ultralytics on Orin Jetson platforms specifically. Its `yolo26-p2.yaml` variant adds a P2 small-object detection head, which is directly relevant to small occluded targets; P2 and P6 ship as YAML architectures only with no pretrained weights. If YOLO26 wins the sweep, `yolo26` versus `yolo26-p2` runs as an ablation, isolating the small-object head as a single clean variable in a way that comparing two different architectures never can.

RF-DETR is included for two project-specific reasons rather than for headline accuracy: it is **Apache-2.0**, giving one non-AGPL option in a sweep that is otherwise entirely AGPL through the Ultralytics codebase, and it leads the RF100-VL **domain-transfer** benchmark, which measures transfer to new domains from limited data — the same property as HERIDAL-to-bush and DJI-to-Arducam. D-FINE reframes DETR box regression as fine-grained distribution refinement, so its contribution is better localisation, which is the axis small targets are punished hardest on under tight IoU.

**SSM / Mamba arms scrapped after consideration.** Mamba-YOLO and MambaNeXt-YOLO were scoped as the state-space arm and have been removed on time-constraint grounds. The reasoning is recorded because it generalises into a selection rule. Both depend on hand-written `selective_scan` CUDA kernels rather than standard PyTorch operations, which creates three independent failure points: compiling against the exact CUDA, PyTorch and GPU-architecture combination on the training machine; compiling again on the ARM64 Jetson, a target these projects rarely test against since their authors build on x86; and surviving TensorRT export, which requires a hand-written plugin for any operation TensorRT does not recognise. Any of the three can fail outright rather than merely slowly, which is categorically different from ordinary training where additional time reliably buys a better result. With Phase 4 already the riskiest part of the build, spending schedule on an architecture that may simply not deploy was a poor trade. The rule this yields, applied to every future candidate: admit no architecture requiring custom CUDA kernels for training or export.

Vision Mamba, VMamba and MambaNeXt-YOLO remain in the literature review as the state-space lineage — Mamba for sequence modelling, then Vim and VMamba as vision backbones with linear complexity, then MambaNeXt-YOLO as a detection-adapted hybrid — with the exclusion stated explicitly as a scope decision on deployment risk rather than a judgement on their merits. This pre-empts the question of why an obviously relevant architecture family is absent from the sweep.

**Scale sweep added.** After the tournament resolves, n/s/m scales of the winning architecture are run. O2 asks about accuracy versus latency versus resources on-device, and six architectures at one scale each gives six scattered points rather than a curve. The scale sweep produces the actual Pareto front on the Orin, which is the direct answer to that objective.

**Elimination structure relaxed at one stage: top-two carry-forward.** The architecture sweep does not pass only its single winner downstream. The two highest-mAP architectures that meet the on-device latency and memory budget are both carried into the A0/A2 head comparison; a single architecture-plus-head winner is chosen there, and strict elimination resumes for the pipeline, occlusion, held-out and scale stages. This is a deliberate, bounded relaxation of strict elimination, not a move toward a full grid. Strict elimination assumes the architecture ranking is stable across the head split; the one plausible way that fails is a runner-up architecture that only becomes best once paired with A2's separate HPI head, which a pure funnel would have discarded prematurely at the sweep. Carrying two finalists into the head stage catches exactly that case for roughly two extra training runs, against the roughly 120 extra runs a full architecture × recipe × head × init × scale grid would cost. The training recipe (full vs freeze) is still decided on the #1 architecture only and applied to both finalists — a far weaker assumption than assuming the architecture ranking survives the head split. The residual limitation — an interaction between architecture and a stage other than the head split — is stated in the thesis rather than searched over. The reason the relaxation is applied here and nowhere else is that the architecture sweep is the one elimination whose loser cannot be recovered later, since every downstream comparison is conditioned on it.

A correction worth recording, since it affects how the comparison is framed: YOLO26 is not transformer-based. It is deliberately de-complexified for edge deployment, and the literature explicitly frames it as breaking the recent pattern of adding transformer blocks. The attention-centric YOLO is YOLOv12, which is why it now holds its own arm. YOLOv13 is likewise not plain CNN — it is CNN plus hypergraph correlation modelling.

The research question the sub-comparison actually tests is therefore not "which YOLO is newest" but what architectural mechanism best recovers targets whose visible evidence is fragmented by occlusion, under a hard real-time and memory budget. The six arms give distinct answers: local convolution, edge-optimised NMS-free convolution, attention inside a CNN, global high-order correlation, a domain-transfer-selected transformer, and a transformer with refined localisation. That maps directly onto the occlusion sweep and is defensible whichever way it resolves.

## Training methodology arm added, LoRA considered and rejected

A training-methodology comparison has been added: standard full fine-tuning against backbone-frozen fine-tuning, run on the sweep's top-ranked architecture only. With roughly 40 placements per class the dataset is small, so how much of the model needs to move is a real question, and Ultralytics answers it with a single `freeze` flag at zero implementation cost.

LoRA was considered as the comparison arm and rejected. The reasoning is recorded here because a documented rejection is worth more than silence. LoRA freezes pretrained weights and trains injected low-rank matrices, which is well suited to dense linear layers such as transformer attention projections. YOLO detectors are overwhelmingly convolutional, so applying LoRA requires a non-standard LoRA-for-convolution variant that Ultralytics does not ship, and there is no strong published baseline for conv detectors to compare against. The decisive consideration is that the thesis would end up defending its LoRA implementation rather than its research question. LoRA remains in scope for Phase 4 VLM fine-tuning, where it is the native and well-supported method.

## Pipeline comparison made explicit

The end-to-end comparison is between four pipeline configurations, distinct from the architecture and head comparisons that precede it and feed into it:

- **P-1, detector only** — single forward pass. The floor everything else must beat.
- **P-2, detector plus A1 re-detection** — low-confidence detections cropped and re-run through the same detector at higher effective resolution, roughly 10-15 ms per escalated crop. This is the double-detector configuration, and it is the bar the VLM has to clear.
- **P-3, detector plus A1 plus VLM** — an async queue worker consuming what A1 could not resolve, plus held-out classes.
- **P-4, open-vocabulary D arm** — a parallel alternative rather than another tier.

How these compose is now stated explicitly: the top two architectures from the model sweep feed the backbone/head comparison, whose single architecture-plus-head winner feeds the pipeline comparison, and the occlusion sweep and held-out evaluation are applied across whichever pipeline configurations survive. The full dependency structure is recorded in `COMPARISON_DEPENDENCY_FLOWCHART.md`.

Decision criteria are pre-registered so the question of whether the VLM survives is settled by criteria rather than after the fact. A1 is adopted if it recovers meaningfully more recall than P-1 within the latency budget. The VLM is adopted only if it beats P-2, not merely P-1, on both held-out classes and low-confidence verification, with queue backlog remaining bounded at realistic flight speed. The D arm displaces the VLM if it matches VLM performance on held-out classes at one-forward-pass cost, which is the most likely outcome. A negative result — that an onboard VLM does not justify its cost on an 8 GB Orin Nano Super relative to cheap re-detection and an open-vocabulary detector — is treated as a genuine contribution rather than a failed experiment.

## Reference document

See `technical_work_timeline.md` for the full phase-by-phase technical work plan reflecting this updated approach, including dependency ordering and the critical path. Note that the critical path has changed: ethics approval and dataset collection no longer gate everything downstream, since Weitefeld provides a real multi-class HPI fallback and the Phase 1 occlusion sweeps produce results with no collected data at all.

See `PHASE_0_1_EXECUTION_GUIDE.md` for the step-by-step execution detail across Phases 0 to 3, and `COMPARISON_DEPENDENCY_FLOWCHART.md` for the dependency structure of every Phase 3/4 comparison and what gates what.