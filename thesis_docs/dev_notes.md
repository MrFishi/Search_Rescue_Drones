# SAR Drone — Development Notes

> Running notes on system architecture, setup decisions, and key concepts learned during thesis development. Append new sections as you go.

---

## Table of Contents

- [PX4, Gazebo & ROS2 — How They Connect](#px4-gazebo--ros2--how-they-connect)
- [Vision Pipeline — How It All Connects](#vision-pipeline--how-it-all-connects)
- [Jetson Orin Nano Super — Deployment Target](#jetson-orin-nano-super--deployment-target)
- [Pinned Versions](#pinned-versions)


## PX4, Gazebo & ROS2 — How They Connect

### What PX4 Actually Is

PX4 is an open-source **flight controller firmware** — the operating system running on the Pixhawk. It handles everything that needs to happen fast and reliably at the hardware level:

- Reading IMU, barometer, GPS, and magnetometer sensors
- Running the **attitude estimator (EKF2)** to know where the drone is and how it's oriented in 3D space
- Running **control loops** — rate controller, attitude controller, position controller — dozens of times per second
- Outputting PWM/DSHOT signals to ESCs to spin the motors
- **Motor mixing** — translating a desired pitch/roll/yaw/thrust into individual motor commands for a specific airframe geometry

> **Key thesis principle:** PX4 owns all of this completely. Our job is only to tell PX4 *where we want the drone to go*. PX4 figures out how to get there.

---

### The uORB Message Bus — PX4's Internal Nervous System

Inside PX4, everything communicates via a publish/subscribe system called **uORB** (micro Object Request Broker). Every sensor reading, every state estimate, every command is a uORB message. Key topics:

| Topic | Direction | Description |

| `vehicle_odometry` | PX4 → us | Position, velocity, orientation from EKF2 |
| `vehicle_status` | PX4 → us | Arming state, flight mode, health flags |
| `offboard_control_mode` | us → PX4 | Tells PX4 what kind of setpoints we're sending |
| `trajectory_setpoint` | us → PX4 | Target position/velocity we want the drone to reach |
| `vehicle_command` | us → PX4 | Commands: ARM, DISARM, SET_MODE |

uORB is internal to PX4. To talk to the outside world, PX4 needs a bridge.

---

### How PX4 SITL Works

When running in **SITL (Software In The Loop)** mode, the exact same PX4 firmware runs as a process on the development machine instead of on a Pixhawk:

- Instead of reading a real IMU → receives simulated sensor data from Gazebo
- Instead of outputting PWM to real ESCs → sends motor commands to Gazebo's physics engine
- Gazebo simulates the physics (gravity, aerodynamics, motor thrust) and feeds the result back into PX4's estimator

The connection between PX4 SITL and Gazebo Harmonic happens via **Gazebo Transport** — a pub/sub system native to Gazebo. PX4 ships a plugin that handles this link automatically.

```
PX4 SITL ──[motor commands]──► Gazebo physics
Gazebo    ──[IMU, GPS, camera data]──► PX4 SITL
```

> **Why Gazebo Harmonic specifically:** Modern Gazebo (gz-sim) uses Gazebo Transport natively and has proper PX4 plugins. Gazebo Classic used a completely different plugin API and is end-of-life — do not use it.

---

### The uXRCE-DDS Bridge — How PX4 Talks to ROS2

uORB is internal to PX4. ROS2 is external. The translator between them is **Micro XRCE-DDS** (uXRCE-DDS).

```
┌─────────────────────────────────────┐
│           Your ROS2 Nodes           │
│  (offboard_hello_world.py, etc.)    │
└──────────────┬──────────────────────┘
               │  ROS2 Topics (DDS)
               │  /fmu/in/...   (commands to PX4)
               │  /fmu/out/...  (state from PX4)
┌──────────────▼──────────────────────┐
│       Micro XRCE-DDS Agent          │
│  (runs as a separate process)       │
└──────────────┬──────────────────────┘
               │  UDP (port 8888)
               │  XRCE-DDS protocol
┌──────────────▼──────────────────────┐
│          PX4 SITL Process           │
│  (runs Micro XRCE-DDS Client        │
│   built into PX4 firmware)          │
└─────────────────────────────────────┘
```

- PX4 runs a **built-in DDS Client** that serialises selected uORB topics and streams them out over UDP
- The **XRCE-DDS Agent** (a separate process) receives that UDP stream and re-publishes everything as proper ROS2 topics
- ROS2 nodes then subscribe/publish to those topics like any other ROS2 topic

**ROS2 topic naming convention:**

| ROS2 Topic | Direction | Maps to uORB |
|---|---|---|
| `/fmu/out/vehicle_odometry` | PX4 → node | `vehicle_odometry` |
| `/fmu/out/vehicle_status` | PX4 → node | `vehicle_status` |
| `/fmu/in/offboard_control_mode` | node → PX4 | `offboard_control_mode` |
| `/fmu/in/trajectory_setpoint` | node → PX4 | `trajectory_setpoint` |
| `/fmu/in/vehicle_command` | node → PX4 | `vehicle_command` |

---

### Full System Architecture

```

                   Development Machine                  
                                                        
  ┌─────────────┐    Gazebo     ┌──────────────────┐    
  │  Gazebo Sim │◄─ Transport ─►│   PX4 SITL       │    
  │  (physics,  │               │  (EKF2, attitude │    
  │   visuals)  │               │   control, etc.) │    
  └─────────────┘               └────────┬─────────┘     
                                         │ UDP :8888    
                                ┌────────▼─────────┐    
                                │  uXRCE-DDS Agent │    
                                └────────┬─────────┘    
                                         │ DDS/ROS2     
                          ┌──────────────▼───────────┐  
                          │    ROS2 Nodes            │  
                          │  offboard_hello_world.py │  
                          │  vision_node.py (later)  │  
                          │  swarm_coordinator(later)│  
                          └──────────────────────────┘  
```

**For swarm simulation:** Each drone is a separate PX4 SITL instance on a different UDP port, with its own ROS2 namespace (`drone_1`, `drone_2`, etc.). This is already scaffolded in `sim_swarm.launch.py`. ---> to be made later

---

## Vision Pipeline — How It All Connects

The vision/AI side is deliberately **decoupled from ROS2** until Phase 6. Training must run on any GPU box or on Kaya with no ROS2 installed, so `vision/` is a plain Python package that knows nothing about the flight stack. It only gets wrapped in a ROS2 node at the very end.

> **Key thesis principle:** the detector is a pure function — image in, boxes out. Everything about flight, telemetry, and coordination lives on the other side of a ROS2 topic boundary. Keeping that boundary clean is what lets the whole vision pipeline be developed, trained, and benchmarked before the airframe exists.

---

### Stage 1 — Raw datasets to trainable data

Three sources feed the pipeline, and each has a different structural hazard that its converter exists to handle.

| Source | Raw form | Hazard | Handled by |
|---|---|---|---|
| HERIDAL | 4000×3000, VOC XML, person only | People shrink to ~5 px if fed whole to the network | `heridal_to_yolo.py` — tiles to 1024 px, splits by **source photo** |
| Weitefeld | 8416×6032, `data.txt`, 4 classes | One physical finding appears in up to 85 frames | `weitefeld_to_yolo.py` — tiles, splits by **physical finding** |
| Own bush data | DJI stills + video, CVAT export | Bursts of stills around one placement are near-copies | Split by **placement**, ideally by **site** |

```
raw photos ──► TILE (1024px, 20% overlap) ──► SPLIT (by unit of independence)
                                                        │
                                                        ▼
                                          train / val / test  +  manifest.csv
```

**The one principle behind all three split rules:** split on the *unit of independence*, never on the individual image. Near-duplicates crossing a split don't crash anything — they silently inflate val/test scores by a large and entirely fake margin, and every architecture decision made downstream is then built on a lie.

Both converters have a `--verify` mode that renders sample tiles with boxes drawn. **Always run it before training.** Coordinate-convention bugs are visible there and invisible in every metric afterwards.

---

### Stage 2 — The occlusion instrument

`occlude.py` covers a controlled percentage of each target's **bounding-box pixels** and writes a frozen dataset to disk.

| Mode | What it does | Use |
|---|---|---|
| `cutout` | Solid rectangle | Crude lower bound, fast |
| `blobs` | Organic irregular mask, exact coverage | Right silhouette, wrong texture |
| `texture` | Vegetation patches sampled from **elsewhere in the same image** | Default — correct texture, lighting, colour for free |
| `foliage` | Alpha-matted leaf/branch PNGs | Most realistic, needs an asset library |

Two design rules that matter:

- **Frozen sets, never on-the-fly.** Every model in the Phase 3 sweep must see byte-identical images, or the degradation curve is comparing RNG rather than models. Same seed in → same bytes out, verified.
- **`--distractor-rate` for training data.** Pasting occluders only over targets teaches the model "that texture means something is hidden underneath." It then aces the synthetic test set and fails on real foliage. Distractors paste identical occluders over background too.

Label policy: an 80%-occluded target **keeps its full original box**. Ground truth is "a target is present here," not "visible pixels are here." Shrinking the box would quietly turn an occlusion experiment into a small-object-detection experiment.

---

### Stage 3 — Training, and what's actually inside the model

```
COCO-pretrained weights
        │
        ▼
  ┌───────────┐    ┌──────┐    ┌──────┐
  │ BACKBONE  │───►│ NECK │───►│ HEAD │───► boxes + classes + confidence
  │ (features)│    │(multi│    │(your │
  │           │    │ scale│    │ class│
  └───────────┘    │fusion)    │ slots)
   expensive,      └──────┘    └──────┘
   transferable                  cheap, task-specific
```

- **Backbone** — extracts visual features at increasing abstraction. Most of the compute, and the most transferable part. This is what COCO pretraining gives you for free.
- **Neck** — fuses features across scales (FPN/PANet) so objects of different sizes are all detectable from one representation.
- **Head** — produces the actual output. One output slot per class you train on.

**Why this matters for the A0/A2/A2b comparison:**

| Arm | Structure | Cost |
|---|---|---|
| A0 | One backbone, one multi-class head | Baseline |
| A2 | Shared backbone, **two heads** (person / HPI) | Small — the second head is a parallel branch, not a second forward pass |
| A2b | Two **fully separate models** | ~2× compute and memory — likely fatal on 8 GB shared with a VLM |

A2 exists because `person` examples will outnumber any single HPI class, so HPI classes risk being drowned out. Separate heads let each be weighted and sampled independently.

Full conceptual detail — batches, epochs, loss, backprop, optimiser, mAP — is in `HOW_TRAINING_WORKS.md`.

---

### Stage 4 — Export and on-device inference

```
best.pt ──► TensorRT engine (FP16) ──► Orin Nano Super
   │                                        │
   └── verify mAP after export ─────────────┘
       (quantisation cost is usually small
        but "usually" isn't a thesis claim)
```

Benchmark with `jetson_clocks` locked and 200+ warm iterations. Report **mean and p95** latency, plus power from `jtop`. Report model inference time and end-to-end pipeline latency **separately** — at 1024 px with tiling, tiling and NMS overhead is not negligible.

---

### Stage 5 — The detection pipeline configurations

Not one architecture — four configurations being compared end to end.

```
                     ┌─────────────────────────────────┐
   every frame ─────►│  DETECTOR  (winning arch + head)│
                     └───────────┬─────────────────────┘
                                 │
                    high conf ───┴─── low conf
                        │              │
                        ▼              ▼
                     OUTPUT      ┌──────────────┐
                                 │  A1: crop +  │  ~10–15 ms
                                 │  re-detect   │  same model, higher res
                                 └──────┬───────┘
                                        │ still unresolved
                                        │ + held-out classes
                                        ▼
                                 ┌──────────────┐
                                 │  VLM worker  │  async, off a queue
                                 │  (≤2B params)│  NOT inline
                                 └──────────────┘

   D-arm: open-vocab detector (YOLO-World / YOLOE / Grounding DINO)
          runs as a PARALLEL alternative, not another tier
```

| Config | Pipeline | Establishes |
|---|---|---|
| **P-1** | Detector only | The floor everything must beat |
| **P-2** | Detector + A1 | The **double-detector** config, and the bar the VLM must clear |
| **P-3** | Detector + A1 + VLM | Does generative reasoning add anything A1 didn't recover? |
| **P-4** | Open-vocab D-arm | Open-vocab flexibility at closed-set speed |

> **Hard ordering constraint:** A1 must be benchmarked *before* any VLM work starts. Building P-3 first and retrofitting A1 as its comparison invites the objection that the baseline was tuned to lose.

**The VLM is measured on throughput, not per-frame latency**, because it isn't inline. The meaningful numbers are candidate clearance rate, queue backlog at a given flight speed, and time-to-verification.

Full dependency structure and gating in `COMPARISON_DEPENDENCY_FLOWCHART.md`.

---

### Stage 6 — Where vision meets ROS2 (Phase 6)

Only at this point does the vision stack acquire a ROS2 dependency.

```
  ┌──────────────────┐   camera frames   ┌─────────────────────┐
  │  Arducam AR0822  │──────────────────►│   vision_node.py    │
  │  (MIPI, 145° FOV)│                   │  detector + A1      │
  └──────────────────┘                   │  + VLM queue worker │
                                         └──────────┬──────────┘
                                                    │ /detections
                                                    │ (custom msg:
                                                    │  class, bbox,
                                                    │  confidence,
                                                    │  geolocation)
                                         ┌──────────▼──────────┐
                                         │ search_coordinator  │
                                         │  (Phase 5/6)        │
                                         └──────────┬──────────┘
                                                    │ /fmu/in/trajectory_setpoint
                                                    ▼
                                              PX4 (via uXRCE-DDS)
```

The detection message is what closes the loop back to the flight stack described above: detections inform search-area optimisation, which becomes trajectory setpoints, which PX4 executes.

---

## Jetson Orin Nano Super — Deployment Target

The companion computer. **Inference and benchmarking only — never train on it.**

### Setup essentials

| Step | Command / note |
|---|---|
| JetPack version | **6.2.x**, not 7.2.1 — Super mode is available from 6.2, Ubuntu 22.04 gives ROS2 Humble on the Jetson (decoupled from the ROS2 Jazzy / Ubuntu 24.04 sim stack on the dev machine — the split is required by the AR0822 driver's L4T dependency, not a version mismatch to fix), and the Phase 4 edge-AI ecosystem is validated against JP6 |
| **Check first** | Confirm the Arducam AR0822 driver supports your chosen JetPack. These drivers are locked to specific L4T releases and lag new JetPack by months. This may decide the version for you. |
| Module selection | **P3767-0005** ("8GB developer kit version"). Selecting P3767-0003 gives a mismatched BSP that underperforms silently. |
| Boot | NVMe SSD, not SD card. SD is too slow for model loading and VLM swap. |
| Power mode | `sudo nvpmodel -q` to list, then select MAXN SUPER |
| Benchmarking | `sudo jetson_clocks` — **required**, or DVFS swings latency 20%+ run to run |
| Monitoring | `sudo pip3 install jetson-stats` → `jtop`. Source of all power/memory figures for O2 and O5. |
| Swap | 16 GB swapfile on NVMe. Default zram is inadequate for Phase 4 VLM weights. |

### The 8 GB constraint

Unified memory shared between the detector, the VLM, and the ROS2 stack. This is the single hardest constraint in the build, and it drives several decisions:

- VLM capped at ~2B parameters
- A2b (two separate models) likely infeasible
- Detector scale selection is a real trade-off, not a default — hence the n/s/m scale sweep on the winning architecture

> **Admission rule for architectures:** nothing requiring custom CUDA kernels. SSM/Mamba detectors were scrapped under this rule — `selective_scan` kernels must compile on x86, compile again on ARM64, *and* survive TensorRT export, any of which can fail outright rather than merely slowly.

### Bring-up status (P0.8 complete, 2026-09-15)

Flashed and running. JetPack 6.2.2 with the `-super` device tree; `MAXN_SUPER`
persists across reboots. AR0822 verified at 4K on the CAM1 connector. CUDA
PyTorch with YOLO11n confirmed working end to end on a captured camera frame.
Working commands and gotchas are in the repo `README.md`; the capture command
there runs at 1920x1080 UYVY, so 4K is confirmed available rather than in use.

Still open (deferred until after the sem 1 proposal submission):

- **Module part number unverified.** Confirm the board is P3767-0005 and not
  P3767-0003. A -0003 gives a mismatched BSP that underperforms silently, so
  every latency number measured before this check is provisional.
- **No TensorRT numbers yet.** Inference so far is PyTorch. P0.8 step 5 also
  calls for `yolo export format=engine half=True` and a re-run on the engine,
  with FP32 against FP16 logged to `results/runs.csv`. Phase 0's exit criterion
  asks for TensorRT inference with numbers logged, so this is the one part of
  the Jetson block still outstanding. The ratio predicts the speedup for every
  Phase 3 model, so it is worth having early.
- **Thermal soak not run.** See below.
- **CAM0 connector came loose during setup.** Unused, but worth a visual check
  before it becomes an intermittent fault chased in software.

### Thermals

Loop inference for 10 minutes under MAXN SUPER with `jtop` open. If it throttles on a desk with the stock fan, it will throttle worse inside an airframe fairing at low airspeed. That's a Phase 7 airframe constraint worth discovering in month 1.

---

## Pinned Versions

Record after the P0.7 sim smoke test and the P0.8 Jetson bring-up. Reproducibility depends on these.

| Component | Version / SHA | Recorded |
|---|---|---|
| PX4-Autopilot | `171f0f38cf` (2026-06-25, "fix(fw_mode_manager): Fix regression with offboard gliding setpoints (#26538)") | 2026-09-30 |
| Gazebo | Harmonic, Gazebo Sim 8.10.0 | 2026-09-30 |
| ROS2 distro (sim stack, dev machine) | Jazzy, Ubuntu 24.04 | 2026-09-30 |
| ROS2 distro (Jetson) | Humble, Ubuntu 22.04 (forced by AR0822 driver/L4T support) | |
| uXRCE-DDS Agent | v3.0.1 (`155cfaa`, 2025-03-18) | 2026-09-30 |
| JetPack / L4T | JetPack 6.2.2, `-super` device tree | 2026-09-15 |
| Arducam driver | `<version>` — read off the running Jetson, not yet recorded | |
| CUDA / TensorRT | `<version>` — read off the running Jetson, not yet recorded | |
| Ultralytics | 8.4.138, pinned in `uv.lock`. `freeze=N` semantics and the "all frozen" `RuntimeError` were checked against this version (2026-09-24) | 2026-09-24 |
| Dataset versions | `heridal_yolo_v1`, `weitefeld_yolo_v1`, `bush_v1` | |

---




## 2026-09-02/03 — P0.4 training environment (WSL2, RTX 4070)

Done: `vision/` moved out of `sar_drone_ws/src/sar_drone/sar_drone/vision/` to
top-level `~/Search_Rescue_Drones/vision/` (sibling of sar_drone_ws), matching
`simulation/`/`scripts/`. Clean git renames, both machines synced.

P0.4 environment built in WSL2 (Ubuntu 24.04, RTX 4070, driver 591.86, CUDA
capability 13.1). Two corrections to the guide's P0.4 commands, worth noting
for reproducing on a fresh box later:

- **`cu121` is gone from PyTorch's index** (checked live, Sept 2026 — current
  options are cu118/cu126/cu128). Used `cu128` instead:
  `uv add torch torchvision --default-index https://download.pytorch.org/whl/cu128`
- `pyproject.toml` needs manual fixup after `uv init` + `uv add torch`:
  - `--default-index` sets that index as the project-wide default (breaks
    every non-torch package resolution). Fix: use a named `[[tool.uv.index]]`
    with `explicit = true` + `[tool.uv.sources]` routing only
    torch/torchvision to it.
  - `requires-python` needs an upper bound (`>=3.11,<3.12`) or uv tries to
    resolve deps for hypothetical future Python versions and fails on
    anything not yet published for 3.12+.
  - `vision` doesn't need to be an installable package (nothing does
    `import vision.x` yet — every script runs by file path). Set
    `[tool.uv] package = false` rather than fight uv_build's src-layout
    convention. Revisit when Phase 6 wraps this as a ROS2 node — restructure
    to `vision/vision/{...}` to match the `sar_drone` package pattern then.

All deps installed: torch 2.11.0+cu128, torchvision 0.26.0+cu128, ultralytics
8.4.138, opencv-python-headless, sahi, lxml, pandas, matplotlib, seaborn, etc.
`torch.cuda.is_available()` verified True. `uv.lock` + `pyproject.toml`
committed and synced across both machines.

**Next: P0.5 — acquire HERIDAL + 2-3 Weitefeld strips.**


I am using a DJI Lito X1 to make my HPI dataset


Size	Accuracy	Latency
nano	75%	        8ms
small	82%	        20ms
medium	88%     	45ms

note to self: example values which we would plot to get a pareto front for different model sizes to determine which is best size of the model to use, not just a single operating point 


## 2026-09-24 — P3.3 fine-tuning ladder, Ultralytics `freeze` semantics

Decision: the P3.3 training-methodology arm is widened from full vs frozen backbone to
a seven-arm ladder (R0 full, R1/R2 freeze-depth sweep, R3 backbone frozen, R4 head-only,
R5 linear probe, R6 staged unfreezing). Spec, pinned config and selection rule live in
`phase_execution_guide.md` P3.3.

What was checked against Ultralytics 8.4.138 (and is worth remembering):

- `freeze=N` freezes layers `model.0`…`model.N-1`, the first N *layers*, not "the
  backbone". YOLO11s/YOLO26s backbone is layers 0–10, Detect is layer 23, so the whole
  backbone is `freeze=11`; `freeze=10` leaves `C2PSA` trainable (52.9% / 55.5% of
  parameters). YOLOv12s backbone is layers 0–8, Detect is layer 21, whole backbone
  `freeze=9`. The old plan's `freeze=10` and its "~30–40% trainable" were wrong.
- Frozen layers also have their BatchNorm held in `eval()` (`_model_train`), driven by
  `trainer.freeze_layer_names`. Any unfreezing callback must update that list.
- 8.4.138 raises `RuntimeError` if `freeze` leaves nothing trainable, so a linear probe
  cannot be `freeze=<all layers>`; it is `freeze=<Detect index>` plus an `on_train_start`
  callback that freezes all of `Detect` except the final 1×1 convs.
- `patience=0` is treated as infinite (early stopping off).
- The optimiser is built over all parameters before training, so `requires_grad`
  flipped on later (staged unfreezing) is picked up with no rebuild.
- Gotcha when smoke-testing on a tiny set: the optimiser steps only every
  `nbs / batch` batches (`nbs=64`), so a 12-batch test with `batch=4` never steps and
  every parameter looks "frozen". Set `nbs` equal to `batch` for such tests.

Smoke test (yolo11n, CPU, synthetic data) confirmed: R3 leaves backbone weights and
BatchNorm statistics bit-identical; R5 changes only the 12 final-conv tensors; R6 steps
trainable parameters 431k → 1.22M → 2.59M at the scheduled epochs. Still to do before
the ladder: write `vision/training/train_recipe.py`, and rerun the pre-flight on the
real #1 and #2 architectures.

---

## 2026-09-30 — P0.7 sim stack smoke test

Run on the laptop (Vivobook, no GPU), following `simulation/sim_setup.README.md`
(the up-to-date version — the abbreviated snippet in `phase_execution_guide.md`
P0.7 is stale: it says `ros2_ws`/`sim_launch.py`, actual paths are
`sar_drone_ws`/`sim_single_drone.launch.py`).

Confirmed working end to end: `make px4_sitl gz_x500` (headless, `-s`, no GUI
needed) → `MicroXRCEAgent udp4 -p 8888` bridges `/fmu/in/*` and `/fmu/out/*` into
ROS2 → `ros2 topic echo /fmu/out/vehicle_odometry --once` returns live pose/velocity
→ `ros2 run sar_drone hover` (node name: `offboard_hello_world`) sends offboard mode
+ ARM and the vehicle climbs toward the -5.0 m NED target. Versions recorded in the
Pinned Versions table above. Sim stack was stopped after confirming — nothing left
running per the guide's "then leave it" instruction.

Cosmetic-only noise, not a bug: `rmw_cyclonedds_cpp` logs a "Failed to parse type
hash" WARN per `px4_msgs` topic on every `ros2 topic list`/`echo`/node start. Topics
still list and data still flows; this is a known cyclonedds/px4_msgs type-hash
metadata quirk, not a bridge failure.

---

## 2026-10-07 — P2.1 Lito X1 test flight: what the files contain

First test flight with the Lito X1 (30 m survey altitude, gimbal at 45° and 90°, plus
stills at 20/40/60 m at both angles). Files stay on the SD card for now, in
`DCIM/DJI_001/thesis/`; `RENAME_MAP.csv` in the card root maps the short names back to the
DJI originals and timestamps. Nothing from the flight is in the repo yet.

Gimbal convention: **pitch is measured down from the horizon**, so 90° is nadir (straight
down) and 45° is the oblique setting for the main drone. Stills store it as XMP
`GimbalPitchDegree` with the opposite sign (−90 is nadir); the decoded video value is
positive-down. The gimbal does not snap exactly: the "45°" stills read −44° to −46°.

**Formats**

- Video: 3840×2160, 59.94 fps, HEVC, about 82 Mbps, 16:9. Stills: 4032×3024 (4:3), 6.7 mm
  (24 mm equivalent). Photo and video aspect ratios differ, so the video is probably a
  sensor crop. EXIF reports a 73.7° FOV (an exiftool composite, not checked); the 82.1°
  vendor figure is a diagonal. True HFOV/VFOV still to be derived.
- Stills carry full metadata inside the JPG (EXIF + XMP): GPS, relative and absolute
  altitude, gimbal pitch/yaw/roll, flight attitude, speed. Read with `exiftool`. It is lost
  if the JPG is re-saved by an editor.
- Video has two metadata sources: the `.SRT` sidecar (only if captions are on; the first two
  test clips were recorded without it) and a `djmd` data track inside the MP4. A third
  track, `dbgi`, was not decoded. The default Ubuntu player warns about both tracks
  ("decoder required"); playback is fine, and VLC/mpv do not complain.

**SRT fields** (one row per frame, 60 per second): timestamp to the millisecond, ISO,
shutter, f-number, EV, colour mode, focal length, latitude, longitude, relative and absolute
altitude, colour temperature, tint. **No gimbal pitch and no heading.**

**`djmd` track.** DJI protobuf (header names `dvtm_Lito_X1.proto`; the schema file is not
available, so field meanings were inferred by comparison with the SRT). One record per
frame, same count as the SRT. Extract with ffmpeg (`-map 0:1 -c copy -f data`, record
sizes from `-f framecrc`), then read as generic protobuf. Compared frame by frame against
the SRT over five clips (15,457 frames), with **zero mismatches** for:

| SRT field | `djmd` field | Note |
|---|---|---|
| latitude, longitude | `/3/3/4/1/2`, `/3/3/4/1/3` | |
| relative altitude | `/3/3/5/1` | millimetres |
| absolute altitude | `/3/3/4/2` | millimetres |
| ISO | `/3/2/9/1` | varies in 2 of 5 clips |
| colour temperature | `/3/2/32/1` | varies in every clip |
| EV | `/3/2/31/1` | constant 0.3 |

`djmd` also holds an orientation quaternion in `/3/4/4` (order x, y, z, w). The pitch from it
reads 45.4° throughout the oblique pass, 90° in the nadir hovers, and falls from 90° to 4.4°
on the descent, matching the footage, so **per-frame gimbal pitch for video comes from
`djmd`**. Yaw from this quaternion is unreliable near nadir (gimbal singularity).

Not in `djmd`: wall-clock time (only a monotonic 16.68 ms frame clock; the MP4 creation date
gives the start to the nearest second), shutter speed, tint. Aperture and focal length are
also absent but constant (f/1.7, 24 mm). `/3/3/3/1-3` and `/3/3/2` were not identified;
`/3/3/3` is not GPS speed.

**Decision (2026-10-08): read both.** Pitch from `djmd`, shutter / tint / millisecond time from
the SRT, everything else is identical in both. Keep the `.SRT` next to every clip; they are
about 1 MB against 600 MB for the video, and the `djmd` layout is undocumented, so it could
change with firmware or on a different drone (the main drone may differ), and data tracks
are often stripped when a clip is trimmed or re-exported (not tested here). Check the decoder against the SRT again on any new
firmware or drone.

Telemetry goes into the P2.4 manifest and is used to stratify results (altitude, pitch,
lighting, shutter) and to compute ground sample distance. It is **not** a model input: the
detectors take the image only, so the six-architecture comparison stays like for like.

**Still open from this flight:** whether the DJI app exports a flight log and in what
format; battery endurance (not measured; the expected range is 15–25 min, to be logged
from real sessions); true HFOV/VFOV and ground size per pixel at 45° versus 90°;
the `djmd` parser itself (not written; the exploratory decoder is not in the repo).

**Parser (2026-10-08).** `vision/telemetry/{dji,extract,plot}.py` now reads all three sources
(stills EXIF/XMP, SRT, `djmd`) in pure Python and writes per-frame CSVs, a per-clip summary
and a stills table, plus PNG plots. Re-run on the five thesis clips, `--check` still gives
zero SRT-vs-`djmd` mismatches. Usage is in `vision/README.md`.

---

## 2026-10-08 — Wave 0 pilot: pixel sizes and the 45° decision

Stills (82, 3-15 m, 45° and 90°) are on the card under `thesis/wave0_pilot/2026-10-08/`; tables,
plots and the pixel-size predictions are in `flights/2026-10-08_wave0_pilot/`. The orbit
video (15 s, 3.9-8.4 m, pitch 14-35°, 4.9 m/s mean) was copied alongside; its SRT and
`djmd` still agree on every frame.

**Camera angle decided: 45° only** for the drone being built; a servo to switch 45°/90° is a
possible later retrofit. **Slope check dropped:** the drone always flies 5-10 m above ground.

**Geometry check.** Stills are 4032x3024. From the 82.1° diagonal: HFOV about 69.5°, VFOV
about 55.5°, f about 2906 px, so nadir ground size is about 0.035 cm per pixel per metre of
height. COCO-pretrained yolo11s (weights in `vision/training/`) was used only to get first-pass
boxes for people and backpacks, checked by eye: it duplicates boxes, calls a jacket a
backpack, misses a bottle from above, and has no sunglasses class, so it was not used for the
table. Backpack size, measured over predicted, was 1.07-1.09 at every nadir height (3, 5,
10, 15 m) and 1.06 overall at 45° (IQR 0.98-1.17). Anchors from the 3 m nadir stills: teal
bottle about 21 cm long, sunglasses about 14.5 cm across, backpack box about 64 x 50 cm with
straps splayed.

**Result.** At 45° and 5-10 m every class is above 8 px at the centre of the frame, but at
the far edge a sunglasses along the view direction is 4-8 px and a water bottle 6-12 px
(table in `collection_plan.md` 3.2). That comes from the 45° mount, not the height. A
standing person looks larger than predicted at low heights because the head is nearer
the camera than the ground.

Limits: sizes are inferred from one set of props; boxes were not hand-annotated; the
`djmd` fields `/3/3/2` and `/3/3/3` remain unidentified.

---

## 2026-10-08 (evening) — Phase 0/1 status, SD card layout, occlusion rules

**SD card layout (Lito X1 card, `DCIM/DJI_001/`).** Thesis footage lives under
`thesis/wave0_pilot/<date>/`; for 2026-10-08 that is `nadir/` (37 stills), `obl45/` (45 stills)
and `video/` (the orbit clip, copied; the original is still in place). Stills are named
`<angle>_h<rounded height m>m_<nn>`. The empty `thesis/wave1_object_only`,
`wave2_person_present` and `wave3_topups` folders are ready. Files outside `thesis/` are
deliberately untouched: the 12:45-12:52 home shots (not thesis), the circle video `0095`, the
water and skyline stills `0101-0108`, and the ground-level stills `0097-0100`. Thesis `.LRF`
proxy files were deleted (author does not need them). The footage exists only on the card; git
holds the derived tables in `flights/` and the rename maps. `pixel_size.py` regenerates the
pixel-size table and plot.

**Occlusion strategy decided in principle** (recorded in `collection_plan.md` 3.5): natural
staged tiers are the evidence, synthetic occlusion is the instrument and an optional training
arm. If used in training: `--distractor-rate`, fixed seed, frozen on disk, full box, tagged
`synthetic_occlusion`, never in the test split. A model trained with it gets its own
degradation curve; the baseline sweep uses one trained without it. Natural staging methods
to be planned prop by prop before Wave 1.

**Phase 0 and 1 status, from the repo on 2026-10-08.**

- Phase 0 done: P0.3 repo layout, P0.4 environment, P0.5 datasets, P0.7 sim smoke test
  (2026-09-30), the P0.2 class list (locked 2026-10-06). Ethics is handled by the author.
- Phase 0 open: P0.6 CVAT (not running; `docker` on the laptop is a podman shim, the old
  plumbing was removed); P0.2 close-out (protocol `[confirm]` items, 7.1, 7.2, target sign-off);
  P0.8 Jetson (part number P3767-0005 vs -0003, TensorRT FP32/FP16 latency to `runs.csv`,
  10-minute thermal soak, loose CAM0 connector).
- Phase 1 done: P1.1, P1.2, P1.3 (baselines A and B trained; val rows in `results/runs.csv`).
- Phase 1 open: P1.4 eval harness (`vision/eval/` does not exist yet; needs per-class
  `runs.csv` rows, `provenance_filter` assert, SAHI full-frame eval, centre-distance metric);
  score Baseline A on the official HERIDAL test set (1957 tiles; the 0.954 mAP50 is val, so
  this checks for leakage); verify Weitefeld `--core-only` (the provenance shows
  `core_only=False`, target about 405 findings) and score Baseline B; P1.5 frozen occlusion
  sets (tool built in `vision/occlusion/occlude.py`, nothing generated; 0/10/20/40/60/80% in
  `cutout` and `texture`, with `--verify`); P1.6 the two degradation curves; P1.7 TensorRT
  on-device numbers (needs the Jetson).

**Plan for the weekend (author, RTX PC):** finish P0 and P1, do some CVAT labelling as a check,
then plan Wave 1, including a prop-by-prop plan for natural and synthetic occlusion.
