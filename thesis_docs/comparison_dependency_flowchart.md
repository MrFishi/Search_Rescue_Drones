# Comparison Dependency Flowchart

Forest Runner SAR Drone, vision/AI track. Companion to
`PHASE_0_1_EXECUTION_GUIDE.md` (Phase 3 section) and `technical_work_timeline.md`.

Purpose: make explicit which comparisons gate which, so it's unambiguous what has to
finish before the next stage can start, and so the run count stays bounded.

**The core structural rule: this is an elimination tournament, not a grid.** Each
stage's winner is the only thing carried into the next stage. Running every
architecture through every head configuration through every pipeline configuration
would be 6 × 3 × 4 = 72 pipeline builds before the occlusion sweep multiplies it by
six again. The elimination structure keeps the whole of Phase 3 to roughly 30–40 runs.

---

## The graph

```mermaid
flowchart TD
    %% ---------- Prerequisites ----------
    P1[["PHASE 1 COMPLETE<br/>validated pipeline · eval harness<br/>occlusion tool · HERIDAL + Weitefeld baselines"]]
    P2[["PHASE 2 COMPLETE<br/>bush dataset · stills only · annotated<br/>held-out classes sealed · Arducam batch"]]

    P1 --> GATE0
    P2 --> GATE0
    GATE0{{"GATE 0<br/>bush dataset usable<br/>+ pipeline trusted"}}

    %% ---------- Stage 1: architecture ----------
    GATE0 --> S1
    S1["<b>STAGE 1 — Architecture sweep</b><br/>P3.1 / P3.2 · 6 runs<br/>train + eval on bush_own only<br/>NO custom-CUDA architectures"]

    S1 --> A1a["YOLO11s<br/>pure CNN · Phase 1 continuity<br/>FREE · Ultralytics-native"]
    S1 --> A1b["YOLO26s<br/>edge-optimised CNN · NMS-free<br/>DFL-free · P2 head available<br/>FREE · Ultralytics-native"]
    S1 --> A1c["YOLOv12s<br/>area-based self-attention in CNN<br/>FREE · Ultralytics-native"]
    S1 --> A1d["YOLOv13s<br/>CNN + hypergraph HyperACE<br/>MODERATE · separate repo"]
    S1 --> A1e["RF-DETR<br/>full transformer · Apache-2.0<br/>domain-transfer leader<br/>MODERATE · separate repo"]
    S1 --> A1f["D-FINE-S<br/>DETR + distribution refinement<br/>better localisation<br/>MODERATE · separate repo"]

    A1a --> G1
    A1b --> G1
    A1c --> G1
    A1d --> G1
    A1e --> G1
    A1f --> G1
    G1{{"GATE 1<br/>winning architecture<br/>accuracy + latency + memory + power<br/>on Orin Nano Super"}}

    %% ---------- Stage 2: training methodology ----------
    G1 --> S2
    G1 -.if YOLO26 wins.-> ABL["<b>P3.3b — p2 ablation</b><br/>yolo26 vs yolo26-p2<br/>1 run · isolates small-object head"]
    G1 -.after tournament.-> SCALE["<b>P3.8 — Scale sweep</b><br/>n / s / m on winner<br/>3 runs · Pareto curve on Orin<br/>DIRECT ANSWER TO O2"]
    S2["<b>STAGE 2 — Training methodology</b><br/>P3.3 · 2 runs · winner only"]
    S2 --> A2a["Full fine-tune<br/>100% trainable"]
    S2 --> A2b["Backbone frozen<br/>freeze=10"]
    A2a --> G2
    A2b --> G2
    G2{{"GATE 2<br/>winning training recipe"}}

    %% ---------- Side experiment: init ----------
    G1 -.side experiment.-> SX["<b>D7 — Initialisation</b><br/>2 runs · reported separately<br/>COCO-init vs Weitefeld-init"]
    SX -.does not gate.-> RPT[["Reported separately<br/>does NOT feed the tournament"]]

    %% ---------- Stage 3: backbone / head ----------
    G2 --> S3
    S3["<b>STAGE 3 — Backbone / head</b><br/>P3.4 · 2–3 runs · winner only"]
    S3 --> A3a["A0<br/>one backbone, one multi-class head"]
    S3 --> A3b["A2<br/>shared backbone, two heads<br/>person | HPI"]
    S3 -.if A2 wins + time.-> A3c["A2b<br/>two fully separate models<br/>STRETCH ONLY"]
    A3a --> G3
    A3b --> G3
    A3c -.-> G3
    G3{{"GATE 3<br/>winning head configuration<br/>per-class HPI mAP + 2nd-head latency cost"}}

    %% ---------- Stage 4: pipeline configurations ----------
    G3 --> S4
    S4["<b>STAGE 4 — Pipeline configurations</b><br/>P3.5 · answers O4"]

    S4 --> C1["<b>P-1</b> Detector only<br/>single forward pass<br/>THE FLOOR"]
    C1 --> C2["<b>P-2</b> Detector + A1<br/>double detector: crop + re-detect<br/>low-confidence, ~10–15 ms"]
    C2 --> C3["<b>P-3</b> Detector + A1 + VLM<br/>async queue worker<br/>≤2B params on-device"]
    S4 --> C4["<b>P-4</b> D-arm open-vocabulary<br/>YOLO-World / YOLOE / Grounding DINO<br/>PARALLEL ALTERNATIVE"]

    C1 --> G4
    C2 --> G4
    C3 --> G4
    C4 --> G4
    G4{{"GATE 4<br/>surviving pipeline configurations"}}

    %% ---------- Stage 5: cross-cutting evaluations ----------
    G4 --> E1["<b>P3.6 — Occlusion sweep</b><br/>survivors × 6 frozen buckets<br/>0/10/20/40/60/80%<br/>cross-check vs real occlusion"]
    G4 --> E2["<b>P3.7 — Held-out class eval</b><br/>survivors × sealed classes<br/>bootstrap CIs over PLACEMENTS"]

    E1 --> FIN
    E2 --> FIN
    FIN[["<b>PHASE 3/4 RESULT</b><br/>O1 · O2 · O4 answered<br/>degradation curves + held-out performance<br/>all with on-device latency and power"]]

    %% ---------- Styling ----------
    classDef gate fill:#2d3748,stroke:#1a202c,color:#fff,stroke-width:2px
    classDef stage fill:#2b6cb0,stroke:#1a4971,color:#fff,stroke-width:2px
    classDef arm fill:#ebf8ff,stroke:#2b6cb0,color:#1a365d
    classDef pipe fill:#f0fff4,stroke:#276749,color:#1c4532
    classDef term fill:#553c9a,stroke:#44337a,color:#fff,stroke-width:2px
    classDef side fill:#fffaf0,stroke:#c05621,color:#7b341e,stroke-dasharray: 5 3

    class GATE0,G1,G2,G3,G4 gate
    class S1,S2,S3,S4 stage
    class A1a,A1b,A1c,A1d,A1e,A1f,A2a,A2b,A3a,A3b,A3c arm
    class C1,C2,C3,C4 pipe
    class P1,P2,FIN,RPT term
    class SX,E1,E2,ABL,SCALE side
```

---

## Prerequisite table — what must finish before what

| Stage | Cannot start until | Produces | Blocks |
|---|---|---|---|
| **Gate 0** | Phase 1 pipeline validated; Phase 2 bush dataset annotated with held-out classes sealed | Trusted data + trusted plumbing | Everything |
| **Stage 1** — architecture sweep | Gate 0 | Winning architecture | Stages 2, 3, 4 |
| **P3.3b** — `yolo26-p2` ablation | Gate 1, and only if YOLO26 won | Small-object head verdict | **Nothing.** Reported alongside. |
| **P3.8** — scale sweep | Gate 1 | Accuracy/latency Pareto curve on the Orin | **Nothing.** Runs any time after the winner is known. |
| **Stage 2** — training methodology | Gate 1 | Winning training recipe | Stage 3 |
| **D7 side experiment** — initialisation | Gate 1 | COCO vs Weitefeld init comparison | **Nothing.** Reported separately, deliberately outside the tournament so it can't entangle the datasets. |
| **Stage 3** — backbone/head | Gate 2 | Winning head config (A0/A2/A2b) | Stage 4 |
| **Stage 4** — pipeline configs | Gate 3 | P-1…P-4 benchmarked | Stages 5a, 5b |
| **— P-2 (A1) specifically** | P-1 benchmarked | The bar the VLM must clear | **P-3.** Never start VLM work before A1 is benchmarked, or there's nothing fair to compare against. |
| **— P-3 (VLM)** | P-2 benchmarked; Jetson with NVMe swap configured | VLM throughput + backlog figures | Stage 5b |
| **— P-4 (D-arm)** | Gate 3 | Open-vocab performance | Stage 5b |
| **Stage 5a** — occlusion sweep | Gate 4; frozen buckets generated | Degradation curves | Final writeup |
| **Stage 5b** — held-out eval | Gate 4; seal verified programmatically | Headline result | Final writeup |

---

## Hard ordering constraints

Three orderings are non-negotiable. Everything else has slack.

**1. A1 before the VLM.** P-2 is the cheap alternative the VLM has to beat. Building
P-3 first and then retrofitting A1 as a comparison invites the accusation that the
baseline was tuned to lose. Benchmark A1, write the number down, then start VLM work.

**2. Architecture before head configuration.** A0 vs A2 is a question about class
imbalance, not about architecture. Running it across all four architectures would
triple the sweep for no extra insight, and would confound "does head separation help"
with "which backbone is better."

**3. Seal verification before held-out evaluation.** Assert programmatically that no
held-out class ID appears in any training manifest, and fail loudly. A leak
invalidates the single strongest result in the thesis, and it's precisely the failure
a config flag gets silently wrong.

---

## Decision points embedded in the graph

| Point | Rule | Consequence if it fails |
|---|---|---|
| **Custom-CUDA admission rule** | No architecture requiring hand-written CUDA kernels enters the sweep, for training or export | Applied pre-emptively: the SSM/Mamba arms were scrapped under this rule. All six current arms run on standard PyTorch ops and export to TensorRT through the ordinary path. |
| **A2b stretch** | Run only if A2 beats A0 on HPI classes by a meaningful margin **and** schedule remains after Phase 4 | Skip. If A2 didn't beat A0, doubling inference cost and memory almost certainly won't help, and "architectural separation wasn't necessary at this data scale" is the honest finding. |
| **A1 adoption** | Recovers meaningfully more recall than P-1 at acceptable precision cost, within latency budget | At ~10–15 ms the bar is low; if it fails, that itself is informative about crop resolution assumptions. |
| **VLM adoption** | Must beat **P-2** (not P-1) on held-out classes *and* low-confidence verification, with bounded queue backlog at realistic flight speed | Phase out the VLM. A documented negative result is a genuine contribution to edge-SAR system design. |
| **D-arm displaces VLM** | Matches VLM performance on held-out classes at one-forward-pass cost | Most likely outcome. Clean finding: open-vocab flexibility without generative cost. |

---

## What stays outside the tournament

Deliberately excluded from the elimination structure so they can't contaminate it:

- **HERIDAL and Weitefeld baselines** (Phase 1) — pipeline validation and their own
  occlusion sweeps. Never mixed into Phase 3 training. Every Phase 3 row carries
  `provenance_filter = bush_own`.
- **The D7 initialisation experiment** — sequencing Weitefeld pretraining into a bush
  fine-tune is legitimate and interesting, but it's reported as a standalone finding
  rather than becoming the silent default for every arm. That's what keeps D6's
  dataset separation legible.
- **The Arducam validation batch** — test-only, never trained on. It is the sole
  measurement of the DJI→Arducam domain gap now that FOV compensation has been dropped
  from collection.
- **LoRA** — considered and rejected for the closed-set detector (see P3.3). Remains in
  scope for Phase 4 VLM fine-tuning only, where it's the native and well-supported
  method.
- **SSM / Mamba detectors** — scrapped on time-constraint and deployment-risk grounds
  (see P3.1). They depend on hand-written `selective_scan` CUDA kernels that must
  compile on x86, compile again on ARM64, and then survive TensorRT export, any of
  which can fail outright rather than merely slowly. Vision Mamba, VMamba and
  MambaNeXt-YOLO remain in the literature review as the state-space lineage, with the
  exclusion stated as a scope decision rather than a judgement on their merits.

---

## Run budget

| Stage | Runs |
|---|---|
| Stage 1 — architecture sweep | 6 |
| Stage 2 — training methodology | 2 |
| D7 — initialisation side experiment | 2 |
| Stage 3 — backbone/head | 2 (3 with A2b) |
| Stage 4 — pipeline configurations | 4 |
| Stage 5a — occlusion sweep | survivors × 6 buckets |
| Stage 5b — held-out evaluation | survivors × 1 |
| P3.3b — `yolo26-p2` ablation | 1 (conditional) |
| P3.8 — scale sweep on winner | 3 |
| **Total** | **~30–40** |

Every row lands in `results/runs.csv`, one row **per class per run**, with git SHA,
dataset version, and device recorded. At this volume the schema being fixed before
run #1 is what makes the results section writable rather than an archaeology project.