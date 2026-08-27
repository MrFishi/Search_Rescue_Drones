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
| JetPack version | **6.2.x**, not 7.2.1 — Super mode is available from 6.2, Ubuntu 22.04 keeps ROS2 Humble aligned with the sim stack, and the Phase 4 edge-AI ecosystem is validated against JP6 |
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

### Thermals

Loop inference for 10 minutes under MAXN SUPER with `jtop` open. If it throttles on a desk with the stock fan, it will throttle worse inside an airframe fairing at low airspeed. That's a Phase 7 airframe constraint worth discovering in month 1.

---

## Pinned Versions

Record after the P0.7 sim smoke test and the P0.8 Jetson bring-up. Reproducibility depends on these.

| Component | Version / SHA | Recorded |
|---|---|---|
| PX4-Autopilot | `<git SHA>` | |
| Gazebo | Harmonic `<version>` | |
| ROS2 distro | Humble | |
| uXRCE-DDS Agent | `<version>` | |
| JetPack / L4T | `<version>` | |
| Arducam driver | `<version>` | |
| CUDA / TensorRT | `<version>` | |
| Ultralytics | pinned in `uv.lock` | |
| Dataset versions | `heridal_yolo_v1`, `weitefeld_yolo_v1`, `bush_v1` | |

---