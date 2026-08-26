# Technical Work Timeline — Forest Runner SAR Drone (Vision/AI Track)

## Overview

This is ordered by dependency, not by calendar week. Several phases can run side by side, but a few of them gate everything downstream, so the ordering below matters more than exact dates.

**Critical path revised.** Dataset collection (Phase 2) was previously the single biggest risk, since it depends on ethics approval, weather and logistics. That is no longer the case, for three reasons: the Weitefeld dataset provides real multi-class HPI data as a fallback, the Phase 1 occlusion sweeps produce publishable results with no collected data at all, and only the `person` class actually requires ethics approval, so object-only HPI collection can proceed immediately. Collection is still the longest lead item and still deserves front-loading, but a delay there is no longer fatal to the project.

When a phase is marked "in parallel," it means it doesn't block, or get blocked by, whatever it's listed next to, so it's fair game to pick up whenever there's spare time, or while waiting on something external like ethics approval or a part delivery.

---

## Phase 0 — Groundwork

Start immediately, alongside everything else. None of this is research work in itself, but all of it gates research work if I leave it too late.

**Ethics approval.** If real people, including volunteers, end up in imagery collected for the HPI/occlusion dataset, that likely needs UWA human ethics sign-off before any of that data can legally be collected. Approval can take several weeks once submitted and is mostly out of my hands after that. Email Kieran this week to confirm whether it applies, and if so, get the application in immediately. If this slips, it becomes the actual critical path of the whole project, not model training.

**Hardware.** Order or confirm the Jetson Orin Nano Super dev kit if it isn't already sitting on the desk (~$560 AUD, part of the $1500 budget). Flash JetPack 6.2.x rather than 7.2.1: Super mode is available from 6.2 onward so no compute is lost, Ubuntu 22.04 keeps the companion computer on the same ROS2 distro as the sim stack, and the edge-AI ecosystem needed for Phase 4 is validated against JP6. Confirm which JetPack versions have a released Arducam AR0822 driver before flashing, since those drivers are locked to specific L4T releases and routinely lag new JetPack releases; if AR0822 support tops out at 6.2 that settles the choice. Enable MAXN SUPER power mode, lock clocks with `jetson_clocks` for repeatable benchmarking, and set up NVMe swap on a dedicated SSD (~$60 AUD), since that's needed later for running a VLM alongside the detector and the ROS2 stack on only 8GB of unified memory. Run a stock YOLO checkpoint through it, export it to TensorRT, and record both latencies before relying on it for real benchmarking.

**Repo and environment.** Get the detector training environment sorted (Ultralytics for the three native arms, plus the YOLOv13, RF-DETR and D-FINE repos), and have the annotation tool (CVAT or Label Studio) configured and reachable. Check the existing sim stack (`sim_launch.py`, the Gazebo world) still runs. It doesn't need touching yet, but I don't want to come back to it in Phase 6 and find it's rotted.

By the end of this phase I want the ethics application submitted (or confirmed unnecessary), the Jetson working, and everything ready to receive data and start training.

---

## Phase 1 — Baseline first

The point here is to validate the training and eval pipeline on a known dataset before sinking time into new data collection, so pipeline bugs get caught early and cheaply rather than buried under my own data later.

**HERIDAL baseline.** Train one detector, whichever YOLO variant I'm currently favouring, on HERIDAL as-is, no modifications. This gets me a working, validated train/eval loop, a baseline mAP number to measure everything else against, and confidence that annotation format, augmentation code, and training config are all correct before anything else gets layered on top.

**Weitefeld baseline (new).** HERIDAL is single-class and therefore cannot validate the multi-class machinery the thesis now depends on: per-class HPI metrics, class-imbalance handling, the A0-vs-A2 head split, held-out-class evaluation. Train a second baseline on Weitefeld (multi-class, real occluded aerial HPI) to validate all of that before the collected dataset exists. Report per-class, not aggregate — `person` is far rarer than `object` in that dataset, so the aggregate figure misleads. Expect a low number: the original authors' YOLOv12 attempt effectively scored zero, so anything meaningfully above that is a result, and landing near zero is itself the finding that motivates flying low.

Both baselines require tiling. HERIDAL is 4000x3000 and Weitefeld is 8416x6032; feeding either to a detector at 640px shrinks targets to a handful of pixels and produces a meaningless baseline. Split HERIDAL by source image and Weitefeld by physical finding, since Weitefeld back-projects each finding into up to 85 frames and splitting by image would put the same object in train and test.

**Occlusion augmentation tool.** Build the thing that synthetically occludes a target by a controlled percentage of its bounding-box pixels. Cutout first to get something working fast, then a texture mode that pastes vegetation patches sampled from elsewhere in the same image, which gives correct local texture, lighting and colour balance with no external asset library. Alpha-matted foliage overlays last, only if warranted. Generate frozen test sets on disk rather than occluding on the fly, so every model in the Phase 3 sweep sees byte-identical images. When used as training augmentation, paste identical occluders at background locations too, or the model learns that occluder texture implies a target underneath and will fail on real occlusion.

**Occlusion sweeps moved into Phase 1 (was Phase 3).** Running the sweep against both baselines needs no ethics approval, no flights and no Orin, so it produces the project's first defensible results within roughly four weeks. It also resolves a confound in O1: the drop measured on bush imagery conflates occlusion, the altitude/scale gap and the camera domain gap, whereas a sweep on HERIDAL itself holds scale and camera constant and isolates occlusion cleanly. The bush-imagery drop remains the operationally honest number; the controlled sweep is what makes it interpretable.

---

## Phase 2 — Dataset collection

This is the real critical path. Start it as early as ethics clearance allows, ideally overlapping Phase 0 and 1 rather than waiting for them to finish.

**Lock the HPI class list and annotation protocol first.** Decide the fixed list of HPI classes (backpack, clothing item, footprint, shelter/tent, discarded gear, etc.) and write down what counts as a positive example for each. Decide now which classes get deliberately held out of training entirely, since those are reserved for the open-vocabulary evaluation later in Phase 3/4. This has to be locked before annotation starts, not adjusted halfway through.

**Only the `person` class needs ethics.** Backpacks, tents, clothing, water bottles, footwear, trail tape, campfire remains and discarded gear are objects in bushland with no human subject involved. Split the session plan into an object-only track that starts immediately and a person-present track gated on approval. That covers roughly 80% of collection volume with no external dependency. Decide the policy for incidental people in frame up front — cleanest is to cut those clips from object-only sessions.

**Collect via DJI, no airframe needed.** The build doesn't need to be flight-ready. A DJI Mini or Air with a controllable gimbal works now.

**Stills primary, video collected alongside (revised).** Stills are the detector training set — confirmed with the lecturer that this doesn't affect the classification model, which is correct, since a detector trains on independent frames regardless of source. Video is captured in parallel at the same sessions anyway, on the reasoning that training can always be repeated without it but a field session can't be repeated to add it. Video is kept **out of** the Phase 3 detector training set (tagged `dji_video` and filtered explicitly), because sampling frames into it would let one placement contribute dozens of near-identical boxes and skew class balance. Instance targets stay placement-based and unchanged.

This keeps the Phase 5 temporal accumulation arm alive with two independent evidence lines: own drone video for true temporal accumulation over consecutive frames, and Weitefeld's multi-view back-projections for viewpoint-diversity accumulation on real forest occlusion at scale. These are reported as **different claims** — one is about the deployed flight pattern, the other about angle diversity in principle — since conflating them would overstate what either shows.

New work this adds: **tracking** (ByteTrack or BoT-SORT, both shipped in Ultralytics) to associate detections across frames, treated as its own small sub-experiment since identity switches and track fragmentation under occlusion are exactly the failure mode the study is about. Temporal passes must be flown **slow and steady** so consecutive frames actually overlap, with pass speed noted in the session log. Target ≥15 slow-pass clips across ≥3 sites.

Split rules: split by placement at minimum, by site preferably, and never split a video clip across train/val/test.

**No FOV compensation (changed).** Rather than adjusting altitude to correct for the lens difference between the DJI's ~88.9 degree and the Arducam's 145 degree field of view, capture the same subject at varied angles and positions directly. This gives viewpoint diversity, but viewpoint diversity and scale matching are orthogonal — the DJI still puts more pixels on a target at a given height than the Arducam will. The scale gap is therefore uncontrolled at capture and handled at training and reporting time instead: keep scale augmentation aggressive, measure and report the pixels-per-target distributions for the DJI training set against the Arducam validation batch, and record the limitation explicitly. This makes the Arducam validation batch the sole measurement of the DJI-to-Arducam domain gap rather than a supporting check, so it must not be skipped or shrunk.

**Sites, not a site.** Three or more distinct locations with a range of canopy densities within each. A single site's vegetation type and lighting otherwise become a hidden confound, and a result can't be separated from the particular patch of bush it was collected in.

**Count placements, not boxes.** One object filmed or photographed repeatedly in one spot is one independent observation, not fifty. Targets are roughly 40 unique placements and 400 boxes per trained HPI class, 25 placements and 250 boxes per held-out class, across at least five sessions and three sites. Placements are the number that matters, because they're what bootstrap confidence intervals resample over. If the targets look unreachable, cut classes rather than accept thin ones.

**Calibrate the actual Arducam early, in parallel, at small scale.** Even without the full airframe, calibrate the Arducam's real distortion profile (a twenty-minute checkerboard job) and grab a small validation-only batch handheld or on a boom pole at roughly the right height and angle. This becomes the ground-truth domain check against DJI-derived training data in Phase 3 and doesn't need to wait on the build at all.

**Annotate as I go, not all at the end.** Annotate each session's footage while planning the next one. Leaving it all to the end risks discovering protocol problems, ambiguous classes, inconsistent box tightness, too late to fix cheaply.

**Dataset hygiene, ongoing:**
- Split by placement or session, never by individual still. Stills captured in a burst around one placement are near-duplicates and must stay together in one split; splitting by site is stricter still and preferable where there are enough sites.
- Keep the held-out classes physically separated, not just excluded by a config flag, and assert programmatically that no held-out class ID appears in any training manifest. A leak invalidates the strongest result in the thesis.
- Tag provenance per image (DJI-video, DJI-still, Arducam-handheld, HERIDAL, synthetic-occlusion). Needed later for domain-gap analysis and per-source comparisons.
- Check class balance per source periodically. Video tends to over-represent "person" frames relative to single-instance HPI objects, and it's much easier to catch that early than after the dataset is finished.

**Run an inter-annotator agreement check.** The methodology criticises Weitefeld's crowd-sourced labels for subjectivity, so demonstrate that this dataset's aren't: have a second person annotate 50 frames independently, or re-annotate blind after three weeks, and report agreement. An afternoon's work that converts a potential weakness into a stated strength.

End state: an annotated, provenance-tagged, placement-split bush dataset with the held-out HPI subset sealed. Note that this is kept **separate** from HERIDAL and Weitefeld rather than combined with them — see the dataset decisions in `objective_changes_since_progress_report.md`.

---

## Phase 3 — Detector architecture sweep

Depends on the Phase 2 dataset (at least a usable first batch) and the Phase 1 pipeline.

Phase 3 is an elimination tournament, not a flat grid: each stage's winner is the only thing carried into the next. Running every architecture through every head configuration through every pipeline configuration would be 48 pipeline builds before the occlusion sweep multiplies it by six again. The elimination structure keeps the whole phase to roughly 25-35 runs. The dependency structure and what gates what is recorded in `COMPARISON_DEPENDENCY_FLOWCHART.md`.

All Phase 3 arms train and evaluate on the collected bush dataset only — HERIDAL and Weitefeld stay confined to their Phase 1 validation role, so every Phase 3 result carries `provenance_filter = bush_own`.

**Detector comparison, answers O2.** Train each candidate on the same dataset, eval on the same held-out test set, and benchmark accuracy, latency and resource usage together on the actual Orin Nano Super. A model that wins on mAP but can't hit real-time frame rate on-device isn't a real answer to O2, so all three numbers get reported side by side. Whichever wins becomes the main detector carried into everything below.

The candidate list has been expanded from the two families originally scoped to six, capped at six so the downstream tournament stays bounded. One hard admission rule applies: **no architecture requiring custom CUDA kernel compilation.**

| # | Model | Structural axis | Tier |
|---|---|---|---|
| 1 | **YOLO11s** | Pure CNN, local convolution; Phase 1 continuity | Free — Ultralytics-native |
| 2 | **YOLO26s** | Edge-optimised CNN, NMS-free, DFL-free | Free — Ultralytics-native |
| 3 | **YOLOv12s** | Area-based self-attention inside a CNN | Free — Ultralytics-native |
| 4 | **YOLOv13s** | Hypergraph, global high-order correlation | Moderate — separate repo |
| 5 | **RF-DETR** | Full transformer, Apache-2.0, domain-transfer leader | Moderate — separate repo |
| 6 | **D-FINE-S** | DETR with distribution-refinement regression, better localisation | Moderate — separate repo |

- **YOLO26** (Ultralytics, January 2026) — DFL-free regression, native end-to-end NMS-free inference, ProgLoss, Small-Target-Aware Label Assignment, MuSGD optimizer. Benchmarked by Ultralytics on Orin Jetson specifically. Its `yolo26-p2.yaml` variant adds a P2 small-object detection head, directly on point for small occluded targets; note P2 and P6 ship as YAML architectures only with no pretrained weights. Run `yolo26` vs `yolo26-p2` as an ablation if YOLO26 wins — it isolates the small-object head as a single clean variable, which comparing two different architectures never can.
- **YOLOv13** (Lei et al., arXiv 2506.17733) — CNN plus hypergraph, using HyperACE adaptive correlation enhancement and FullPAD distribution.
- **RF-DETR** (Roboflow) — first real-time model past 60 mAP on COCO and leader on the RF100-VL domain-transfer benchmark. Selected for domain transfer specifically, since that benchmark measures the same property as HERIDAL→bush and DJI→Arducam. **Apache-2.0**, making it the one non-AGPL option in an otherwise entirely AGPL sweep.
- **D-FINE** — reframes DETR box regression as fine-grained distribution refinement, so its contribution is better **localisation**, the axis small targets get punished hardest on under tight IoU.
- **Zero-friction swap for #6:** RT-DETR is Ultralytics-native and costs nothing, at the price of being a dated reference point.

**SSM / Mamba arms scrapped.** Mamba-YOLO and MambaNeXt-YOLO were scoped as the state-space arm and removed after consideration on time-constraint grounds. Both depend on hand-written `selective_scan` CUDA kernels rather than standard PyTorch operations, creating three independent failure points: compiling against the exact CUDA/PyTorch/GPU combination on the training machine, compiling again on the ARM64 Jetson (a target these projects rarely test against), and surviving TensorRT export, which needs a hand-written plugin for unrecognised custom ops. Any of the three can fail outright rather than merely slowly, which is categorically different from ordinary training where more time reliably buys a better result. With Phase 4 already the riskiest part of the build, that was a bad trade. The general rule this yields: admit no architecture requiring custom CUDA kernels. Vision Mamba, VMamba and MambaNeXt-YOLO remain in the literature review as the state-space lineage, with the exclusion recorded as a scope decision rather than a judgement on their merits.

**Correction to how this comparison gets framed.** YOLO26 is not transformer-based — it is deliberately de-complexified for edge deployment, and the literature explicitly frames it as breaking the recent pattern of adding transformer blocks. The attention-centric YOLO is YOLOv12, which is why it now has its own arm. YOLOv13 is likewise not plain CNN, it is CNN plus hypergraph correlation modelling. So the research question is not "which YOLO is newest" but **what architectural mechanism best recovers targets whose visible evidence is fragmented by occlusion, under a hard real-time and memory budget** — with the six arms giving distinct answers: local convolution (YOLO11), edge-optimised NMS-free convolution (YOLO26), attention inside a CNN (YOLOv12), global high-order correlation (YOLOv13), domain-transfer-selected transformer (RF-DETR), and transformer with refined localisation (D-FINE). That maps directly onto the occlusion sweep and holds up whichever way it resolves.

**Scale sweep on the winner.** After the tournament resolves, run n/s/m scales of the winning architecture. O2 asks about accuracy versus latency versus resources on-device: six architectures at one scale gives six scattered points, whereas a scale sweep gives the actual Pareto curve on the Orin. For an edge-deployment thesis the curve is the answer, and it is the figure that shows the trade-off was understood rather than a winner merely picked.

Licensing: YOLO11, YOLO26, YOLOv12 and YOLOv13 all inherit AGPL-3.0 from the Ultralytics codebase. RF-DETR is Apache-2.0 and is the deliberate non-AGPL fallback if licensing becomes a constraint on releasing code.

**Training methodology comparison (new), on the winning architecture only.** Standard full fine-tuning against backbone-frozen fine-tuning (`freeze=10`). With roughly 40 placements per class the dataset is small, so how much of the model needs to move is a genuine question, and it costs two runs and one flag.

LoRA was considered as this arm and rejected, recorded here because a documented rejection is worth more than silence. LoRA trains injected low-rank matrices alongside frozen weights, which suits dense linear layers such as transformer attention projections. YOLO detectors are overwhelmingly convolutional, so it would need a non-standard LoRA-for-convolution variant that Ultralytics doesn't ship, with no strong published baseline for conv detectors to compare against. The decisive point is that the thesis would end up defending its LoRA implementation rather than its research question. LoRA stays in scope for Phase 4 VLM fine-tuning, where it's the native and well-supported method.

**A0 vs A2 vs A2b, the imbalance test.** Runs on the winning architecture only — running it across all four would triple the sweep for no extra insight and would confound "does head separation help" with "which backbone is better."

A0 is one model, one multi-class head, person and every HPI class together. A2 shares the same backbone but splits into two heads, one for person and one for HPI, so each can be weighted and sampled independently instead of HPI classes being drowned out by the much larger volume of person examples. A2b is two fully separate models, which is the time-permitting stretch only: roughly double the inference cost and double the memory, likely fatal on 8GB shared with a VLM.

Compare per-class performance, especially on HPI, since aggregate mAP hides exactly the effect being tested. Measure the second head's latency overhead explicitly rather than assuming it's negligible — if A2 wins on HPI mAP but costs 15ms, that changes the deployment argument and O2 needs the number. Decision rule for A2b, set now: only run it if A2 beats A0 on HPI by a meaningful margin and schedule remains after Phase 4. If A2 doesn't beat A0, the honest finding is that architectural separation wasn't necessary at this data scale.

**A1, the bar the VLM has to clear.** On any detection below a lowered confidence threshold, crop the region and re-run the same detector on the crop at higher resolution rather than whatever it saw downsampled inside the full frame. Cheap, maybe 10-15ms, and recovers a lot of small-object recall with no VLM involved. This needs to exist and be benchmarked before any Phase 4 VLM work starts, since it's the fair comparison point the VLM verification arm needs to beat to justify its cost. Building the VLM arm first and retrofitting A1 afterwards invites the objection that the baseline was tuned to lose, so the ordering is a hard constraint rather than a preference.

**D arm, open-vocabulary detector.** Train or fine-tune YOLO-World, YOLOE or OWLv2 on the same data. Grounding DINO is the accuracy leader among zero-shot detectors if a stronger but heavier comparison point is wanted. Unlike A0/A2 it can be prompted with class names at inference time instead of being locked to a fixed trained list, so evaluate it specifically against the held-out HPI classes, where it should clearly beat the closed-set detectors by construction. This sits in a different tier from a VLM entirely: open-vocabulary flexibility at closed-set-detector speed, since it's still one fast forward pass with no language generation involved.

**Occlusion-fraction sweep, answers O1.** The controlled sweeps on HERIDAL and Weitefeld have already run in Phase 1. This is the same procedure applied to the bush test set across whichever pipeline configurations survive: graded buckets at 0/10/20/40/60/80% of bounding-box pixels, frozen on disk so every model sees byte-identical images, everything else held constant. Precision, recall and mAP@50 per bucket per class gives a degradation curve rather than one number, and it's probably the strongest single figure in the thesis — it shows exactly how much occlusion costs and whether the drop-off is graceful or a cliff. If there's a cliff, its location is the empirical justification for the VLM verification arm, since it marks where a single-pass detector stops being sufficient.

Cross-check the synthetic curve against the real-occluded subset staged during collection. Two independent lines of evidence agreeing is much stronger than either alone, and if they disagree that's an important and reportable finding about synthetic occlusion's validity.

**Pipeline configuration comparison (new), answers O4.** Distinct from the architecture and head comparisons above, and fed by them: the winning architecture feeds the head comparison, whose winner feeds this. Four configurations:

- **P-1, detector only** — single forward pass. The floor everything else must beat.
- **P-2, detector plus A1 re-detection** — the double-detector configuration. Low-confidence detections cropped and re-run through the same detector at higher effective resolution, roughly 10-15ms per escalated crop.
- **P-3, detector plus A1 plus VLM** — async queue worker consuming what A1 couldn't resolve, plus held-out classes.
- **P-4, open-vocabulary D arm** — a parallel alternative rather than another tier.

Decision criteria are pre-registered so whether the VLM survives is settled by criteria rather than after the fact. A1 is adopted if it recovers meaningfully more recall than P-1 within the latency budget. The VLM is adopted only if it beats **P-2**, not merely P-1, on both held-out classes and low-confidence verification, with queue backlog bounded at realistic flight speed. The D arm displaces the VLM if it matches VLM performance on held-out classes at one-forward-pass cost, which is the most likely outcome. A negative result is treated as a genuine contribution: that an onboard VLM doesn't justify its cost on an 8GB Orin relative to cheap re-detection and an open-vocabulary detector is useful to anyone building edge SAR systems, with quantified reasons.

---

## Phase 4 — VLM integration and evaluation

Depends on Phase 3's A1 baseline and best detector already existing. There's nothing to compare a VLM against otherwise.

**Setup.** Pick 2-3 VLMs under 2B parameters (SmolVLM2, Qwen2-VL-2B, Moondream2) and get them running on-device via llama.cpp or Ollama.

**Async pipeline.** Detector runs synchronously at frame rate as normal. A separate VLM worker consumes low-confidence crops off a queue at whatever throughput the hardware can sustain, which will likely be well under frame rate. This reframes the relevant VLM metric from "added latency per frame" to candidate-clearance throughput and queue backlog at a given flight speed, which is a fairer and more operationally honest way to report the cost than a raw per-frame tax.

**Held-out class evaluation, the strongest VLM result.** Evaluate each VLM on the same held-out HPI classes reserved earlier. Since the closed detectors score near zero here by construction, and even the D-arm open-vocab detector may struggle on some, this isolates exactly where a full VLM's reasoning actually earns its keep versus where a lighter open-vocab detector already covers the same ground.

Two things this result depends on. First, **verify the seal programmatically before running** — assert that no held-out class ID appears in any training manifest, and fail loudly. A leak invalidates the single strongest result in the thesis and is exactly what a config flag gets silently wrong. Second, **report bootstrap confidence intervals resampled over placements, not boxes.** With roughly 25 placements per held-out class and a site-level test split, the test set holds maybe 8-12 placements per class. That's a thin evidence base, the intervals will be wide, and resampling boxes instead would give falsely tight intervals because boxes from one placement aren't independent. Wide but honest beats narrow and wrong, and stating the limitation before an examiner raises it is much stronger than defending it afterwards.

**LoRA is in scope here**, unlike in Phase 3. If a VLM is fine-tuned, LoRA is the native and well-supported adaptation method for a transformer, so it needs no defending.

**Verification vs A1.** Test VLM-based verification of low-confidence detections against the A1 re-detection baseline. If VLM verification doesn't meaningfully beat A1 relative to its added latency, that's still a legitimate finding, not a failed experiment.

**On-device benchmarking.** Latency per query, throughput under the async queue, memory footprint, power draw, for each VLM, on the actual Orin Nano Super. Needed for O5 and for the feasibility discussion.

---

## Phase 5 — Temporal accumulation

Time-permitting. Depends on the Phase 3 best detector and the Phase 2 video data, since HERIDAL is stills-only and can't be used for this arm.

Add a lightweight tracker (ByteTrack or OC-SORT) on top of the best detector and accumulate detection evidence across a short sliding window of frames instead of scoring each frame in isolation. A weak single-frame detection that persists and strengthens across several frames from a slightly shifting viewpoint is more likely a true positive than a one-frame blip, and at low altitude small viewpoint shifts can reveal targets through gaps that a single static frame just misses. Evaluate the recall improvement on real collected footage, since this is the one arm that structurally can't run on stills.

---

## Phase 6 — Multi-drone simulation and fleet coordination (O6)

Can realistically start earlier than its position here suggests, since the sim stack (`sim_launch.py`, the Gazebo world) already runs and doesn't strictly need the finished vision pipeline. Coordination logic can be built and tested against mocked detection messages first, with the real detector swapped in once Phase 3 produces one.

Design the detection message schema carefully here: since person detections and HPI detections should trigger different fleet behaviours (converge vs reprioritise search area), the message needs an explicit `detection_type` field the coordinator can branch on cleanly, rather than reinterpreting a raw class index downstream.

From there: implement collaborative search-area reprioritisation across the simulated fleet, then compare time-to-full-coverage and redundant re-search area between independent and collaborative planning.

This is the first phase I'd scope down or cut if the timeline gets tight, which lines up with what the progress report already flags about it depending on later integration work.

---

## Phase 7 — Physical flight testing

Fallback: simulation and bench testing only. Gated on the airframe actually being built, and parts, integration, and flight tuning all carry their own risk independent of anything above. If the build isn't flight-ready in time, running the trained pipeline against pre-recorded or live-streamed footage on the ground stays the fallback path, consistent with the risk mitigation already in the progress report.

If this phase is reached: full on-hardware, in-flight validation of the whole pipeline, detector through VLM or open-vocab arm through fleet coordination, under real conditions.

---

## Critical path

```
Ethics approval (Phase 0)
        │
        ▼
Dataset collection + annotation (Phase 2) ◄──── DJI flights don't need the airframe
        │
        ▼
Baseline detector training (Phase 1, can start earlier on HERIDAL alone)
        │
        ▼
Detector architecture sweep: A0 / A2 / A1 / D-arm / occlusion curve (Phase 3)
        │
        ├──► VLM integration (Phase 4)
        ├──► Temporal accumulation (Phase 5, time-permitting)
        └──► Fleet coordination sim (Phase 6, can partly run earlier with mocked detections)
                        │
                        ▼
                Physical flight testing (Phase 7, fallback: sim/bench only)
```

The one thing that delays everything else if it's late is ethics approval and the start of dataset collection. Everything after that has some slack in how it's ordered. That doesn't.

---

## Changelog

**Rev. 3 — architecture sweep, pipeline comparison, dataset decisions**
- Critical path revised: Weitefeld, the Phase 1 sweeps and ethics-free object-only collection mean Phase 2 delay is no longer project-fatal.
- Phase 0: JetPack 6.2.x recommended over 7.2.1, gated on the Arducam AR0822 driver check; NVMe swap and `jetson_clocks` added.
- Phase 1: Weitefeld multi-class baseline added; tiling and split-hygiene requirements recorded; occlusion sweeps moved in from Phase 3.
- Phase 2: object-only vs person-present collection split; **stills primary with video collected alongside** for the temporal arm; **no FOV compensation**, varied angles and positions instead; placement-based instance counting; inter-annotator agreement check.
- Phase 3: detector candidates expanded with corrected architectural characterisations; training-methodology arm added and LoRA documented as rejected; A2b added as a stretch; pipeline configuration comparison (P-1 to P-4) made explicit with pre-registered decision criteria.
- Phase 4: seal verification and bootstrap CIs over placements added to the held-out evaluation.
- Datasets kept separate (D6); initialisation handled as a labelled side experiment (D7).

Full execution detail is in `PHASE_0_1_EXECUTION_GUIDE.md`. The dependency structure of every Phase 3/4 comparison, including what gates what and the run budget, is in `COMPARISON_DEPENDENCY_FLOWCHART.md`.

**Rev. 3a — video reinstated**
- Stills-only reversed: video is collected alongside stills, kept out of detector training, and used for the Phase 5 temporal arm. Rationale: training is repeatable, field sessions are not.
- Temporal accumulation arm restored, now with two independent evidence lines (own video for temporal, Weitefeld multi-view for viewpoint diversity), reported as distinct claims.
- Tracking (ByteTrack/BoT-SORT) added as new technical work.
- Split principle stated once explicitly in the execution guide (P1.0) rather than restated per dataset.

**Rev. 3b — SSM arms scrapped, sweep rebalanced to six**
- Mamba-YOLO and MambaNeXt-YOLO removed on time-constraint and deployment-risk grounds. New admission rule: no architecture requiring custom CUDA kernel compilation.
- Sweep rebalanced to six deployment-safe arms: YOLO11s, YOLO26s, YOLOv12s, YOLOv13s, RF-DETR, D-FINE-S. Three Ultralytics-native (free), three separate-repo standard-PyTorch (moderate).
- RF-DETR added specifically for Apache-2.0 licensing and RF100-VL domain-transfer leadership; D-FINE for localisation refinement on small targets; YOLOv12 for attention-inside-CNN as an axis distinct from full transformers.
- `yolo26` vs `yolo26-p2` added as a conditional ablation isolating the small-object head.
- Scale sweep (n/s/m) on the winner added as the direct answer to O2.
- Vision Mamba, VMamba and MambaNeXt-YOLO retained in the literature review as the state-space lineage.