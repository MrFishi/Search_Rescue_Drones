# Technical Work Timeline — Forest Runner SAR Drone (Vision/AI Track)

## Overview

This is ordered by dependency, not by calendar week. Several phases can run side by side, but a few of them gate everything downstream, so the ordering below matters more than exact dates. The biggest risk to the whole schedule is dataset collection (Phase 2), since it depends on ethics approval and on weather and logistics, none of which I control directly. Anything that de-risks or front-loads that phase should take priority over polishing model code.

When a phase is marked "in parallel," it means it doesn't block, or get blocked by, whatever it's listed next to, so it's fair game to pick up whenever there's spare time, or while waiting on something external like ethics approval or a part delivery.

---

## Phase 0 — Groundwork

Start immediately, alongside everything else. None of this is research work in itself, but all of it gates research work if I leave it too late.

**Ethics approval.** If real people, including volunteers, end up in imagery collected for the HPI/occlusion dataset, that likely needs UWA human ethics sign-off before any of that data can legally be collected. Approval can take several weeks once submitted and is mostly out of my hands after that. Email Kieran this week to confirm whether it applies, and if so, get the application in immediately. If this slips, it becomes the actual critical path of the whole project, not model training.

**Hardware.** Order or confirm the Jetson Orin Nano Super dev kit if it isn't already sitting on the desk (~$560 AUD, part of the $1500 budget). Flash JetPack 6.2, enable MAXN SUPER power mode, and set up NVMe swap, since that's needed later for running a VLM alongside the detector and the ROS2 stack on only 8GB of unified memory. Run a stock YOLO checkpoint through it just to confirm basic inference works before relying on it for real benchmarking.

**Repo and environment.** Get the detector training environment sorted (Ultralytics/YOLO plus whichever Mamba-hybrid repo I end up using), and have the annotation tool (CVAT or Label Studio) configured and reachable. Check the existing sim stack (`sim_launch.py`, the Gazebo world) still runs. It doesn't need touching yet, but I don't want to come back to it in Phase 6 and find it's rotted.

By the end of this phase I want the ethics application submitted (or confirmed unnecessary), the Jetson working, and everything ready to receive data and start training.

---

## Phase 1 — Baseline first

The point here is to validate the training and eval pipeline on a known dataset before sinking time into new data collection, so pipeline bugs get caught early and cheaply rather than buried under my own data later.

**HERIDAL baseline.** Train one detector, whichever YOLO variant I'm currently favouring, on HERIDAL as-is, no modifications. This gets me a working, validated train/eval loop, a baseline mAP number to measure everything else against, and confidence that annotation format, augmentation code, and training config are all correct before anything else gets layered on top.

**Occlusion augmentation tool (in parallel).** Build the thing that synthetically occludes a target by a controlled percentage of its pixels. Start with plain programmatic cutout to get something working fast, then move to alpha-matted branch and leaf overlays once there are reference foliage images to pull from, since that's a much more realistic proxy for actual bush occlusion than a solid box. This gets reused constantly from Phase 3 onward, so building it now means it's ready the moment real data shows up.

---

## Phase 2 — Dataset collection

This is the real critical path. Start it as early as ethics clearance allows, ideally overlapping Phase 0 and 1 rather than waiting for them to finish.

**Lock the HPI class list and annotation protocol first.** Decide the fixed list of HPI classes (backpack, clothing item, footprint, shelter/tent, discarded gear, etc.) and write down what counts as a positive example for each. Decide now which classes get deliberately held out of training entirely, since those are reserved for the open-vocabulary evaluation later in Phase 3/4. This has to be locked before annotation starts, not adjusted halfway through.

**Collect via DJI, no airframe needed.** The build doesn't need to be flight-ready for this. A DJI Mini or Air with a controllable gimbal gets consistent, repeatable altitude bands right now. Fly multiple bands within the 5–10m operational target, adjusted upward to roughly account for the FOV gap between the DJI's ~88.9° lens and the Arducam's 145°, so ground coverage is at least comparable. Collect as video, not just stills, since that costs nothing extra now and is needed later for the temporal accumulation work in Phase 5; stills for annotation can just be pulled from it.

**Calibrate the actual Arducam early, in parallel, at small scale.** Even without the full airframe, calibrate the Arducam's real distortion profile (a twenty-minute checkerboard job) and grab a small validation-only batch handheld or on a boom pole at roughly the right height and angle. This becomes the ground-truth domain check against DJI-derived training data in Phase 3 and doesn't need to wait on the build at all.

**Annotate as I go, not all at the end.** Annotate each session's footage while planning the next one. Leaving it all to the end risks discovering protocol problems, ambiguous classes, inconsistent box tightness, too late to fix cheaply.

**Dataset hygiene, ongoing:**
- Split by clip or session, never by frame. Every frame from one video clip stays entirely in one split (train, val, or test) so near-duplicates don't leak across splits.
- Tag provenance per image (DJI-video, DJI-still, Arducam-handheld, HERIDAL, synthetic-occlusion). Needed later for domain-gap analysis and per-source comparisons.
- Check class balance per source periodically. Video tends to over-represent "person" frames relative to single-instance HPI objects, and it's much easier to catch that early than after the dataset is finished.

End state: an annotated, provenance-tagged, clip-split combined dataset (HERIDAL plus DJI plus Arducam-validation plus synthetic occlusion), with the held-out HPI subset locked away for later.

---

## Phase 3 — Detector architecture sweep

Depends on the Phase 2 dataset (at least a usable first batch) and the Phase 1 pipeline.

**Detector comparison, answers O2.** Train each detector candidate (YOLO variants, Mamba-hybrid) on the same combined dataset, eval on the same held-out test set, and benchmark accuracy, latency, and resource usage together on the actual Orin Nano Super. A model that wins on mAP but can't hit real-time frame rate on-device isn't a real answer to O2, so all three numbers need to be reported side by side. Whichever wins becomes the main detector carried into everything below, so I'm not multiplying every later experiment across every architecture.

**A0 vs A2, the imbalance test.** A0 is one model, one multi-class head, person and every HPI class together. A2 shares the same backbone but splits into two heads, one for person and one for HPI, so each can be weighted and sampled independently instead of HPI classes getting drowned out by the much larger volume of person examples. Train both on the combined dataset, compare per-class performance (especially on HPI), and check the latency overhead of the second head, which should be minimal. This tells me whether the architectural split is actually worth the added complexity.

**A1, the bar the VLM has to clear.** On any detection below a lowered confidence threshold, crop the region and re-run the same detector on the crop at higher resolution rather than whatever it saw downsampled inside the full frame. Cheap, maybe 10-15ms, and recovers a lot of small-object recall with no VLM involved. This needs to exist and be benchmarked before any Phase 4 VLM work starts, since it's the fair comparison point the VLM verification arm needs to beat to justify its cost.

**D arm, open-vocabulary detector.** Train or fine-tune YOLO-World or OWLv2 on the same data. Unlike A0/A2 it can be prompted with class names at inference time instead of being locked to a fixed trained list, so evaluate it specifically against the held-out HPI classes, where it should clearly beat the closed-set detectors by construction. This sits in a different tier from a VLM entirely: open-vocabulary flexibility at closed-set-detector speed, since it's still one fast forward pass with no language generation involved.

**Occlusion-fraction sweep, answers O1.** Run every model above through the occlusion tool from Phase 1 at graded percentages, say 0/10/20/40/60/80%, everything else about each source image held constant. Compute precision, recall, and mAP@50 per bucket per model to get a degradation curve rather than one number. This is probably the strongest single figure in the whole thesis, since it shows exactly how much occlusion costs and whether the drop-off is graceful or a cliff. Cross-check against the smaller real-occluded Arducam/DJI validation set as a sanity check.

---

## Phase 4 — VLM integration and evaluation

Depends on Phase 3's A1 baseline and best detector already existing. There's nothing to compare a VLM against otherwise.

**Setup.** Pick 2-3 VLMs under 2B parameters (SmolVLM2, Qwen2-VL-2B, Moondream2) and get them running on-device via llama.cpp or Ollama.

**Async pipeline.** Detector runs synchronously at frame rate as normal. A separate VLM worker consumes low-confidence crops off a queue at whatever throughput the hardware can sustain, which will likely be well under frame rate. This reframes the relevant VLM metric from "added latency per frame" to candidate-clearance throughput and queue backlog at a given flight speed, which is a fairer and more operationally honest way to report the cost than a raw per-frame tax.

**Held-out class evaluation, the strongest VLM result.** Evaluate each VLM on the same held-out HPI classes reserved earlier. Since the closed detectors score near zero here by construction, and even the D-arm open-vocab detector may struggle on some, this isolates exactly where a full VLM's reasoning actually earns its keep versus where a lighter open-vocab detector already covers the same ground.

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
