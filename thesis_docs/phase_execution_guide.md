# Phase 0 + Phase 1 — Execution Guide (rev. 2)

Forest Runner SAR Drone, vision/AI track. Companion to `technical_work_timeline.md`
and `objective_changes_since_progress_report.md`.

Scope: from "nothing trained, Jetson in the post" to a validated multi-class
training/eval pipeline, baseline numbers for both person and HPI detection, the
occlusion tool built, and controlled degradation curves in hand.

Sequenced so **nothing on the critical path waits on hardware**. All Jetson work is
quarantined into one block (P0.8) you execute the day the box arrives.

---

## What changed in rev. 2, and why it matters

HPI detection is now the primary contribution rather than a co-equal focus. That
isn't a change you can absorb by reordering a to-do list — it changes what Phase 1
has to prove:

- **HERIDAL cannot validate the pipeline you now need.** It is single-class,
  person-only. The Phase 3 experiments that carry the thesis — A0 vs A2 head
  splitting, per-class HPI metrics, class-imbalance handling, held-out-class
  evaluation — are all multi-class. A pipeline validated only on HERIDAL leaves
  every one of those unvalidated until your own data arrives, which is the worst
  possible moment to discover a bug.
- **O1 is now, strictly, a person-detection objective.** It asks about a detector
  "trained on open terrain SAR data," and the only such dataset is person-only.
  There is no HPI drop to measure from HERIDAL because there is no HPI baseline in
  it. Your HPI occlusion story has to come from elsewhere. State this in the thesis
  rather than letting a reviewer find it.
- **The held-out class split is now the highest-leverage design decision in the
  project**, because it produces the headline Phase 4 result. It needs deciding in
  Phase 0 with instance-count targets, not sketched in Phase 2.

There's also a dataset published four months ago that resolves most of the first
two points. See D3 — read that before the rest.

---

## 0. Decisions to lock before writing code

### D1 — Where does training run?

Tiled HERIDAL is ~30k images at 1024 px; add Weitefeld and it's larger. Not a
laptop job.

| Option | Reality check |
|---|---|
| UWA Kaya HPC (GPU partition) | Free, A100/H100-class, SLURM batch, no interactive debugging. Right tool for the Phase 3 sweeps. **Apply now** — account requests take days to weeks. |
| Own/lab RTX GPU (≥12 GB) | Best iteration speed, fine for Phase 1. Check what your supervisor's group already has before buying. |
| Colab Pro / Kaggle | Fine for a first baseline, painful across ~15 Phase 3 runs. Session limits bite. |

Never train on the Orin. It is an inference and benchmarking device only.

If Kaya is in the mix, submit the account request this week, alongside the ethics
email. Same class of external latency you don't control.

### D2 — JetPack 6.2.x or 7.2.1?

**Recommendation: JetPack 6.2.2 (Ubuntu 22.04 / ROS2 Humble), unless the Arducam
driver decides otherwise.**

- Super mode (67 INT8 TOPS, 102 GB/s) is available from JetPack 6.2 onward, so
  staying on 6.x costs you no compute.
- Ubuntu 22.04 → ROS2 Humble, matching what your `sim_launch.py` / PX4 stack is
  almost certainly built against. JetPack 7.2 is Ubuntu 24.04 → Jazzy, giving you a
  distro mismatch between sim machine and drone.
- Phase 4 (on-device VLM via llama.cpp/Ollama) is your riskiest software
  integration. Every working recipe, `jetson-containers` image, and Ultralytics
  TensorRT guide is validated against JP6. JP7.2 is CUDA 13.2 and already
  generating "my OpenCV CUDA build broke" reports.
- You're optimising for thesis submission, not for running the newest stack.

**Blocking check before you flash:** confirm on Arducam's AR0822 page which JetPack
versions have a released driver `.deb` / device-tree overlay. Arducam MIPI drivers
are locked to specific L4T releases and routinely lag a new JetPack by months. If
AR0822 support tops out at JP6.2, that settles D2 — and you'll be glad you checked
before flashing rather than after.

### D3 — Use the Weitefeld dataset? (Recommendation: yes, and early)

**Nathan et al., "An aerial color image anomaly dataset for search missions in
complex forested terrain," Scientific Data 13:747 (2026).**
doi:10.1038/s41597-026-07101-w · Zenodo 15848419 · https://weitefeld.cg.jku.at/

Published March 2026, from a real manhunt in a German forest. What it contains:

- 10,659 labelled aerial images at 8416 × 6032, 3–5 cm/px ground sampling
- 34,424 bounding-box labels across 405 physical findings, each back-projected
  photogrammetrically into up to 85 frames at different viewing angles and
  occlusion levels
- Four classes: `unknown`, `shelter`, `object`, `person`
- The objects are tarps, trash bags, barrels, tents, huts, hunting stands, sheds,
  fire pits, metal barriers — **that is an HPI class list in all but name**
- Real vegetative occlusion, not synthetic
- Plus 19,795 unlabelled frames over adjacent zones
- Openly licensed, ethics-approved at source (JKU EC-55-2025)

Three separate reasons this matters to you:

**1. It fixes your Phase 1 validation gap.** Real, multi-class, occluded aerial HPI
data available *today* — no ethics, no flying, no waiting. You can stand up and
validate the whole multi-class pipeline (A0 vs A2, per-class metrics, imbalance
handling) before your own data exists.

**2. It de-risks your critical path.** Your timeline names ethics approval and
dataset collection as the thing that sinks the project if late. With Weitefeld in
hand, a delay there stops being fatal: you'd still have a real HPI dataset to run
Phase 3 against, and your own collection becomes the low-altitude contribution
layered on top rather than the sole foundation. That's the largest risk reduction
available to you right now, and it costs a download.

**3. It hands you your motivation section.** The authors trained YOLOv12 on it and
report it **failed outright** — average confidence 0.016%, maximum 2.6%. The
anomaly detectors they benchmarked managed under 3.5% precision, or near-100%
detection rate at under 0.75% precision. Their diagnosis: at 300 m altitude and
3–5 cm/px, occluded clues occupy a handful of pixels and carry no learnable
appearance.

That's an argument *for* your platform, made independently in a Nature journal. The
strongest available framing of your thesis becomes: state-of-the-art detection
fails on real occluded forest HPI at aerial-survey altitude; this project tests
whether flying at 5–10 m instead of 300 m recovers enough pixels-on-target to make
the problem tractable, and which onboard architecture does it best. Far more
compelling than "occlusion is hard," and it gives you a published failure baseline
to beat.

Handle it honestly, though — it's a **novelty check as well as a gift**. You now
have to position your contribution against it in the lit review, not merely cite
it. Your differentiators are low altitude, the onboard real-time constraint, finer
HPI class granularity, the open-vocabulary and VLM arms, and multi-drone
coordination. None of those are addressed by that paper. Say so directly.

Caveats for the methods section:
- 300 m from a crewed aircraft, not 5–10 m from a UAV. The scale gap runs opposite
  to HERIDAL's but is just as real.
- Four coarse classes, not your finer taxonomy. `object` lumps a barrel with a tarp.
- Crowd-sourced labels from 160 volunteers, so labelling is subjective — the authors
  say so themselves.
- `unknown` is semantically messy. Use `--drop-unknown` for primary runs and report
  with-and-without as a sensitivity check.
- 144 GB (core) or 404 GB (full). Start with 2–3 strips (~20–30 GB) to prototype
  before committing the disk and the download time.

### D4 — Detector family and license

Start with **Ultralytics YOLO11** (`yolo11n` to iterate, `yolo11s` for reported
baselines). It gives training, validation, TensorRT export, and COCO metrics in one
toolchain — exactly what Phase 1 must validate.

For the methods section: Ultralytics is AGPL-3.0. Fine for academic work, but if
you release the repo publicly the whole repo inherits AGPL. Decide now whether that
matters to you or your supervisor.

The full architecture sweep belongs to Phase 3. Don't touch it yet — it blocks
nothing in Phase 1, and the Phase 1 baselines exist to validate the pipeline the
sweep will run through.

### D5 — The O1 confound

O1 measures a drop that is the sum of three things:

1. Occlusion — what you actually want
2. Altitude/scale gap — HERIDAL is 45–60 m, you fly 5–10 m
3. Camera/domain gap — Canon PowerShot S110 vs Arducam AR0822 at 145°, different
   geography, different light

If you can't separate them, your headline number is uninterpretable. Structural fix,
landing in Phase 1:

- **Controlled O1** — synthetic occlusion sweep on HERIDAL itself. Same images,
  same scale, same camera, only occlusion varies. Isolates (1) cleanly. Needs no
  new data.
- **In-the-wild O1** — the drop on real bush imagery in Phase 3. Reports (1)+(2)+(3)
  together, which is the operationally honest number.
- **Scale control** — downscale a subset of your low-altitude imagery to match
  HERIDAL's pixels-per-person and report that too. Isolates (2).

Consequence: the occlusion tool isn't a parallel nice-to-have. It's the instrument
that produces your first defensible result, and it needs nothing external.

---

## Phase 0 — Groundwork

### P0.1 — Ethics (today, ~1 hour)

Still the hardest external dependency, though D3 softens the consequence of delay.
Email Kieran with enough specificity that he can answer yes/no in one reply:

- Imagery captured by a DJI consumer UAV at 5–10 m AGL over bushland
- Human subjects are volunteers (you plus 1–3 known participants) acting as
  simulated lost persons
- Imagery trains and evaluates object detectors; faces are incidental, not the
  target
- Data held on university storage; published results contain no identifiable
  imagery — or state which example frames you'd want to publish, since that's
  usually the part needing explicit consent
- Ask directly: full HREC, low-risk review, or exempt?

Draft the participant information sheet and consent form **while waiting for the
reply**. If approval is needed, the application becomes a same-day submission
instead of a two-week one.

Parallel: ask about CASA / UWA requirements for the flights themselves (sub-2 kg
excluded RPA rules, landholder permission for the site). Not ethics, same class of
latency.

### P0.2 — HPI taxonomy and held-out split (~4 hours) ← now a top-tier Phase 0 item

This defines your primary contribution and your headline Phase 4 result. No longer
something to sketch in Phase 2.

**The class list.** Three tiers, locked before annotation starts:

| Tier | Classes | Role |
|---|---|---|
| Primary | `person` | Baseline, comparability to literature |
| HPI-trained | `backpack`, `clothing_item`, `shelter_tent`, `water_bottle`, `footwear` | Trained in A0/A2, the main HPI result |
| HPI-heldout | `trail_marker_tape`, `campfire_remains`, `discarded_gear` | **Never trained.** Reserved for the D-arm and VLM evaluation |

Write a one-page protocol per class: what counts as positive, box tightness
convention, minimum visible size, handling of ambiguous cases, with a photo example
of each. This becomes a thesis appendix, and it's what makes your dataset citable
rather than merely used.

**Held-out selection criteria**, because a reviewer will ask why these three:
(a) collectable in reasonable quantity during Phase 2, (b) visually distinct enough
that an open-vocab model or VLM has a fair shot, (c) genuinely meaningful to a SAR
crew. Note `footprint` fails (a) and (b) at 5–10 m over bush — hard to annotate
consistently, hard to see. Treat it as a stretch class and don't build an argument
on it.

**Now plan instance counts backwards.** Easy to skip, expensive to skip. Your
strongest Phase 4 claim rests entirely on performance over the held-out classes. If
you hold out three classes with 40 instances each, that claim rests on ~120
instances and any difference you report sits inside the noise. Set targets now,
because they drive Phase 2 collection volume:

- ≥300 instances per trained HPI class
- ≥150 instances per held-out class, spread over ≥5 sessions and ≥3 sites so you're
  not reporting one afternoon's lighting
- Per-class counts tracked in the manifest, checked weekly

If those look unreachable given your flying time, cut the number of classes rather
than accept thin ones. Three well-populated HPI classes beat seven starved ones,
and it's much easier to defend.

### P0.3 — Repo layout (~1 hour)

ML work stays **out of** the colcon workspace. Training must run on Kaya or a bare
GPU box with no ROS2 present. It only becomes a ROS2 node in Phase 6.

```
sar-thesis/
├── ros2_ws/src/sar_drone/          # existing, untouched
├── sim/                            # worlds, models, deploy script
├── vision/                         # plain python pkg, no ROS2 dependency
│   ├── datasets/
│   │   ├── heridal_to_yolo.py
│   │   ├── weitefeld_to_yolo.py
│   │   └── manifests/              # COMMITTED
│   ├── occlusion/occlude.py
│   ├── training/configs/*.yaml
│   ├── eval/{evaluate.py,results_schema.md}
│   ├── deploy/{export_trt.py,bench_jetson.py}
│   └── pyproject.toml
├── data/                           # GITIGNORED
│   ├── raw/{heridal,weitefeld}/
│   ├── processed/{heridal_yolo_v1,weitefeld_yolo_v1}/
│   └── occluded/
├── results/
│   ├── runs.csv                    # COMMITTED, one row per class per run
│   └── runs/<run_id>/
└── thesis/{references.bib,figures/}
```

Two things that look like bureaucracy and aren't:

**Commit manifests, gitignore data.** A manifest is a CSV: `image_id, source_path,
provenance, clip_id, split, n_person, n_hpi`. It makes clip-level and
finding-level splits reproducible and auditable, for kilobytes. "Which images were
in the test set for run 47" is a question you *will* be asked in your viva, and
without this it's unanswerable.

**Commit `results/runs.csv` from run #1.** Fixed schema:

```
run_id, git_sha, date, model, weights, dataset_version, split, occlusion_mode,
occlusion_frac, provenance_filter, class_name, precision, recall, map50,
map50_95, latency_ms_mean, latency_ms_p95, device, power_w_mean, notes
```

Note `class_name`: with HPI primary, per-class rows are the whole point. Aggregate
mAP hides exactly the effect you're studying — a model can post a respectable
overall number while scoring near zero on your three rarest HPI classes. One row
per class per run.

Phase 3 is roughly 5 architectures × 6 occlusion buckets × several arms × per-class
rows. Thousands of rows. Fix the schema before row 1 or lose a weekend reconciling
spreadsheets.

Branching: `main` (always builds), `dev` (daily), `exp/<name>` for throwaway work.
Tag `phase-1-baseline` when the baselines lock.

### P0.4 — Training environment (~2 hours)

```bash
cd vision
uv init --python 3.11
uv add "torch>=2.4" torchvision --index-url https://download.pytorch.org/whl/cu121
uv add ultralytics opencv-python-headless pillow numpy pandas pyyaml tqdm
uv add sahi lxml matplotlib seaborn
```

Commit `uv.lock`. Your Phase 1 baselines get compared against months later.

Verify: `uv run python -c "import torch; print(torch.__version__, torch.cuda.is_available())"`

### P0.5 — Acquire both datasets (~2 hours plus download)

**HERIDAL** — FESB Split IPSAR page (`ipsar.fesb.unist.hr`). Historically flaky;
the **Accenture/AIR** GitHub repo mirrors it in keras-retinanet format, and the
authors answer email. You want the 1546 train + 101 test full-size 4000×3000 images
with VOC XML, single class `person`, 3229 annotations. Ignore the ~68k pre-cropped
patches — those serve the original paper's patch-classifier method, not detection
training.

**Weitefeld** — Zenodo 15848419, 15 zips (one per flight strip) plus `data.txt`.
Pull 2–3 strips first (~20–30 GB) and get the pipeline working before committing
144 GB.

Sanity-check both on arrival: open three images, confirm dimensions, parse one
annotation, plot a box, confirm it lands on the target. Ten minutes that saves a
week.

Record SHA256, download date, and full citation in `data/raw/<name>/PROVENANCE.md`.

### P0.6 — Annotation tool (~2 hours)

**CVAT, self-hosted via Docker**, over Label Studio: CVAT handles video natively
with frame interpolation, and your Phase 2 collection is video-first. Interpolating
a backpack box across 300 frames beats drawing 300 boxes.

```bash
git clone https://github.com/cvat-ai/cvat && cd cvat
docker compose up -d
# create superuser per their README, then browse to localhost:8080
```

Load 20 images as a test project — you're verifying the import/export round-trip,
not annotating. Configure the P0.2 label set now so the taxonomy is baked into the
tool before real annotation starts.

### P0.7 — Sim stack smoke test (~1 hour, then leave it)

Defensive only. You don't need the sim until Phase 6, but you don't want to find in
month 7 that a PX4 or Gazebo update broke it.

```bash
cd ros2_ws && colcon build --symlink-install && source install/setup.bash
ros2 launch sar_drone sim_launch.py launch_qgc:=false
# second terminal:
ros2 topic list | grep fmu
ros2 topic echo /fmu/out/vehicle_odometry --once
ros2 run sar_drone hover
```

Works: record the exact PX4 git SHA, Gazebo version, and ROS2 distro in
`dev_notes.md`, then don't touch it. Broken: fix it now while the break is small.

### P0.8 — Jetson bring-up (day of arrival, ~4 hours)

Don't start until D2 is resolved by the Arducam driver check.

**Buy an NVMe SSD first** if you don't have one — 500 GB, ~$50–70 AUD.
Non-negotiable: SD boot is too slow for model loading, and Phase 4 needs real swap
on fast storage for VLM weights. Budget: $560 Jetson + ~$60 NVMe against $1500.

1. **Flash.** SDK Manager on an Ubuntu 22.04 x86 host, Direct Flash to NVMe. Select
   module **P3767-0005, "Jetson Orin Nano [8GB developer kit version]"**. Picking
   P3767-0003 gives a mismatched BSP that underperforms silently — the worst
   failure mode available.
2. **Confirm Super mode.**
   ```bash
   sudo nvpmodel -q            # list modes, find MAXN SUPER, note its index
   sudo nvpmodel -m <index>
   sudo jetson_clocks          # lock clocks — REQUIRED for repeatable benchmarks
   ```
   Never benchmark without `jetson_clocks`. DVFS otherwise swings latency 20%+ run
   to run and your Phase 3 comparison becomes noise.
3. **Monitoring.** `sudo pip3 install jetson-stats`, then `jtop`. This is where O2
   and O5 power and memory numbers come from — confirm it reports power before you
   need it.
4. **Swap on NVMe.** Default zram is inadequate for Phase 4.
   ```bash
   sudo fallocate -l 16G /swapfile && sudo chmod 600 /swapfile
   sudo mkswap /swapfile && sudo swapon /swapfile
   echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
   ```
5. **Stock inference sanity run.**
   ```bash
   pip install ultralytics
   yolo predict model=yolo11n.pt source=https://ultralytics.com/images/bus.jpg
   yolo export model=yolo11n.pt format=engine half=True
   yolo predict model=yolo11n.engine source=bus.jpg
   ```
   Log FP32 vs TensorRT-FP16 latency to `runs.csv`. Even on a stock COCO model that
   ratio predicts the speedup for every Phase 3 model, and it's your first evidence
   the device works.
6. **Thermals.** Loop inference for 10 minutes under MAXN SUPER with `jtop` open.
   If it throttles on a desk with the stock fan, it will throttle worse inside an
   airframe fairing at low airspeed. A Phase 7 constraint worth knowing in month 1.
7. **Arducam.** Install the driver for your exact L4T version, confirm enumeration
   (`v4l2-ctl --list-devices`), grab a frame. Then do the checkerboard calibration —
   nominally Phase 2, but the camera is in your hand and it's twenty minutes.

**Phase 0 exit criteria:** ethics submitted or confirmed unnecessary; HPI taxonomy
and held-out split locked with instance targets written down; environment
reproducible from `uv.lock`; both datasets downloaded and verified; CVAT running
with the label set configured; sim confirmed and version-pinned; Jetson flashed, in
Super mode, running TensorRT inference with numbers logged.

---

## Phase 1 — Baselines and instruments

### P1.0 — Why the splits are constructed the way they are (~read once)

Three different split rules appear below — by source image for HERIDAL, by physical
finding for Weitefeld, by placement or site for the bush data. They look like three
ad-hoc decisions. They're one principle applied three times, and it's worth being
able to state it cleanly rather than defending three separate rules.

For the conceptual grounding — what each split is for, what overfitting is, why
validation and test can't be the same set — see `HOW_TRAINING_WORKS.md` sections 2
and 3. The short version and the project-specific reasoning follow.

**The three splits do different jobs.**

| Split | Weights updated on it? | Looked at during development? | Job |
|---|---|---|---|
| **Train** | Yes | Constantly | The only data the model actually learns from |
| **Validation** | No | Every epoch | Overfitting early-warning; the set you make decisions against (learning rate, augmentation, when to stop, which checkpoint) |
| **Test** | No | **Once, at the end** | The honest number you report |

Validation and test have to be separate sets, even though neither trains the model.
The moment you tune anything against a set — pick a learning rate because it scored
better, stop training at the epoch where it peaked — you have started fitting to it,
just slowly and indirectly. A number from a set you've tuned against overstates real
performance. Test is the one set that has influenced nothing, which is what makes it
worth reporting.

**The principle: split on the unit of independence, not on the image.**

Random per-image splitting assumes every image is an independent sample. In all
three of your datasets, that assumption is false, in a different way each time:

| Dataset | Unit of independence | What breaks if you split by image |
|---|---|---|
| HERIDAL | The **source photo** | 20 overlapping tiles from one photo are near-duplicates. Tiles in train and test from the same photo means the model is tested on a near-copy of what it trained on. |
| Weitefeld | The **physical finding** | One tarp appears in up to 85 frames from different angles. Splitting by image puts *literally the same object* in train and test — worse than near-duplication. |
| Your bush data | The **placement** (ideally the **site**) | A burst of stills around one staged backpack, or a video clip of it, are all near-copies of each other. |

The failure mode is the same in every case and it's nasty because it's silent:
nothing crashes, no error appears, your validation and test mAP just come out
inflated by a large and entirely fake margin. You then make architecture decisions
on those numbers, report them in the thesis, and discover the problem when the model
performs far worse in the field than your results promised.

**Choosing the strictest split you can afford for test.** For the bush data, split
train/val by placement but hold out an entire **site** for test where you have
enough sites. Placement-level splitting answers "does this generalise to a backpack
I didn't photograph." Site-level answers "does this generalise to bush I've never
flown" — which is much closer to the real deployment question, and much harder to
pass. If you can pass the harder test, report that one.

**Ratios, and why.** Roughly 70–80% train, 10–15% val, 10–15% test is the standard
starting point and the scripts default near it (`--val-frac 0.10`, `--test-frac
0.15`). The logic behind the numbers: train gets the majority because data quantity
drives model quality most directly; val only needs to be large enough for a stable
signal to make decisions from; test only needs to be large enough for the reported
number to be meaningful. For HERIDAL, the official 101-image test set is used
directly, which keeps your numbers comparable to published results — that's a better
reason than any ratio.

**Where this bites hardest in your project.** Your held-out HPI classes will have
roughly 25 placements each, so a site-level test split leaves 8–12 placements per
class in test. That's a thin evidence base for your single strongest claim, which is
why P3.7 specifies bootstrap confidence intervals resampled **over placements, not
boxes**. Resampling boxes would treat 10 stills of one backpack as 10 independent
observations and give you falsely narrow intervals — the same independence-unit
mistake as a bad split, just showing up in the statistics instead of the data.

### P1.1 — HERIDAL → tiled YOLO (~4 hours) ← the step that silently ruins baselines

**The trap:** pointing Ultralytics at 4000×3000 images with `imgsz=640` downsamples
~6×. A 30 px person becomes 5 px. You get a terrible mAP, conclude YOLO is bad at
SAR, and build on a broken baseline. Every published HERIDAL result above 0.80
mAP@50 uses tiling or high-resolution inference.

```bash
uv run python datasets/heridal_to_yolo.py \
    --heridal-root ../data/raw/heridal \
    --out ../data/processed/heridal_yolo_v1 \
    --tile 1024 --overlap 0.2 --min-visible 0.3 --neg-ratio 0.10 --seed 42
```

Why each parameter:

- `--tile 1024 --overlap 0.2` → 5×4 = 20 tiles per image, ~31k tiles. Overlap stops
  a person landing on a seam and being halved in every tile.
- `--min-visible 0.3` → a box clipped below 30% of original area causes the **tile
  to be dropped entirely**, rather than emitting a sliver box or leaving a person
  unlabelled. Both alternatives teach the model something false.
- `--neg-ratio 0.10` → keeps 10% of person-free tiles. Without it, ~90% empties: the
  model learns to predict nothing and training takes 5× longer for a worse result.
  With too few, you get false positives on rocks and shrubs.
- **Splits by source image, never by tile** (enforced). Adjacent overlapping tiles
  are near-duplicates; leaking them across train/val inflates val mAP by a large and
  entirely fake margin. Same principle as your "split by clip, never by frame"
  hygiene rule, one level down.

**Verify before training. Non-negotiable, 15 minutes:**
```bash
uv run python datasets/heridal_to_yolo.py --verify ../data/processed/heridal_yolo_v1 --n 12
```
Renders 12 tiles with boxes drawn. Look at them yourself. Every YOLO coordinate bug
in existence is visible here and invisible everywhere else.

### P1.2 — Weitefeld → tiled multi-class YOLO (~4 hours) ← new, and load-bearing

```bash
uv run python datasets/weitefeld_to_yolo.py \
    --images-root ../data/raw/weitefeld/images \
    --data-txt    ../data/raw/weitefeld/data.txt \
    --out         ../data/processed/weitefeld_yolo_v1 \
    --tile 1024 --overlap 0.2 --core-only --drop-unknown --seed 42
```

Three things the script handles that would otherwise bite:

**Splits assigned per FINDING, not per image.** Each physical finding was
back-projected into up to 85 frames. Splitting by image puts the same tarp in train
and test — a worse leak than the tile case, because it's literally the same object
from a slightly different angle. The script groups first, splits second, and routes
each image wholly to one split.

**`--core-only`** restricts to the first 34,424 entries, the peer-reviewed core.
Later rows are community additions that can change over time. Use it, or your
dataset isn't reproducible.

**`--drop-unknown`** excludes class 0, which is semantically messy by the authors'
own account. Run primary experiments without it, report with-and-without as a
sensitivity check.

**Two format assumptions you must verify.** I built the parser from the paper's
prose, not from the file. The box encoding is documented as `x y height width` with
x,y at the "lower-left" corner, which is ambiguous about y direction; and there's no
explicit finding-ID column, so the script groups on comment strings. It prints the
number of unique findings detected and warns if that isn't near 405. Run `--verify`
and **look at the renders** — if boxes sit vertically mirrored relative to the
objects, re-run with `--box-origin bottomleft`.

```bash
uv run python datasets/weitefeld_to_yolo.py --verify ../data/processed/weitefeld_yolo_v1 --n 16
```

### P1.3 — Train the baselines (~2 days, mostly unattended)

**Overfit gate first**, on both datasets. Point a config at 20 tiles used as both
train and val:
```bash
yolo detect train model=yolo11n.pt data=configs/heridal_tiny.yaml \
    epochs=50 imgsz=1024 batch=4 augment=False
```
You should exceed mAP@50 0.95. If not, the data format is broken and nothing
downstream will work. Ten minutes, saves days. Run the equivalent for Weitefeld —
that one also confirms multi-class label indices are correct, which the
single-class HERIDAL gate cannot.

**Baseline A — HERIDAL, person only.** Validates the pipeline, gives a
literature-comparable number, and provides the substrate for the controlled
occlusion sweep.
```bash
yolo detect train model=yolo11s.pt data=configs/heridal_v1.yaml \
    epochs=150 imgsz=1024 batch=8 optimizer=AdamW lr0=0.001 \
    scale=0.5 mosaic=1.0 close_mosaic=15 \
    hsv_v=0.5 fliplr=0.5 flipud=0.3 degrees=180 \
    single_cls=True seed=42 \
    project=../results/runs name=p1_heridal_yolo11s
```

**Baseline B — Weitefeld, multi-class.** Validates everything HERIDAL can't, and
gives you a real HPI number to carry into Phase 3.
```bash
yolo detect train model=yolo11s.pt data=configs/weitefeld_v1.yaml \
    epochs=150 imgsz=1024 batch=8 optimizer=AdamW lr0=0.001 \
    scale=0.5 mosaic=1.0 close_mosaic=15 \
    hsv_v=0.5 fliplr=0.5 flipud=0.3 degrees=180 \
    seed=42 \
    project=../results/runs name=p1_weitefeld_yolo11s
```
Note the absence of `single_cls`. **Report per-class metrics, not just aggregate** —
with `person` far rarer than `object` here, the aggregate will mislead you in
whichever direction the imbalance runs.

Augmentation choices you can defend in the methods section:
- `degrees=180`, `flipud=0.3` — aerial imagery has no canonical up. Standard photo
  augmentation assumes it does. Rotation is nearly free accuracy here.
- `scale=0.5` — deliberately generous, because your later bush data sits at a
  radically different apparent scale from both datasets. Cheapest partial hedge
  against the D5 confound.
- `hsv_v=0.5` — bush and forest lighting varies enormously between canopy shadow
  and open sun. Worth more than hue jitter.
- `close_mosaic=15` — mosaic helps small objects but distorts scale statistics;
  disabling it for the last 15 epochs lets the model settle on the real
  distribution.

**Expected results.** HERIDAL: mAP@50 roughly 0.70–0.85 on tiled val — Božić-Štulić
et al. report an 88.9% detection rate and a YOLOv5s variant reached 0.802 mAP@50.
Below ~0.60 something is wrong; above ~0.92 suspect leakage. Weitefeld: expect much
lower, and don't panic — the published YOLOv12 attempt effectively scored zero.
Anything meaningfully above that is a result. If you land near zero too, that's also
a finding, and it's precisely the finding that motivates flying low.

### P1.4 — Eval harness (~1–2 days) ← build once, use for the whole thesis

Ultralytics `val` gives tile-level metrics. Not sufficient. Three additions:

**(a) Per-class everything.** With HPI primary, aggregate mAP is close to useless on
its own — it hides the rare classes that are the point. One `runs.csv` row per class
per run, always.

**(b) Full-frame sliced evaluation.** Tile mAP isn't the operational question;
"given one full frame, did we find it" is. Use SAHI to run sliced inference over the
full test image, merge with NMS, score against untiled ground truth. Report both:
the tile number is comparable across your experiments, the full-frame number is
comparable to published work and to reality.

**(c) A localisation-tolerant SAR metric.** IoU@0.5 on a 20 px target is a brutal
and arguably meaningless bar — 8 px off fails IoU while being operationally a
perfect detection. The Accenture/AIR work introduced an SAR-APD evaluation for this
reason. Report "detection centre within N px of GT centre" recall alongside mAP@50.
Two lines of code, and it protects you from the reviewer who says your metric
doesn't reflect the use case. Cite AIR when you do.

Make `evaluate.py` append to `runs.csv` automatically. A manual step gets skipped
under deadline pressure and the audit trail dies with it.

### P1.5 — Occlusion tool (~2 days) ← your primary instrument

Design points that matter more than they look:

**Fraction is measured against bbox pixels**, not image pixels. "40% occluded" means
40% of the target's box area is covered. Achieved fraction is measured after
rendering and logged per instance.

**Generate frozen test sets; never occlude on the fly.**
```bash
for f in 0 10 20 40 60 80; do
  uv run python occlusion/occlude.py \
      --in ../data/processed/heridal_yolo_v1/test \
      --out ../data/occluded/heridal_occ_v1/frac_$f \
      --frac 0.$f --mode texture --seed 42
done
```
Every model in Phase 3 must see byte-identical images. On-the-fly occlusion with a
per-run RNG means model A and model B see different images and your degradation
curve compares noise. The tool is deterministic — same seed, same bytes, verified.

**Four modes, escalating realism:**
1. `cutout` — solid rectangle. Crude lower bound, fast.
2. `blobs` — organic irregular mask at exact coverage. Right silhouette, wrong
   texture.
3. `texture` — **vegetation patches sampled from elsewhere in the same image.** The
   sweet spot: correct local texture statistics, lighting, and colour balance, with
   no external asset library. Default, and the one to report.
4. `foliage` — alpha-matted leaf/branch PNGs. Most realistic, needs an asset
   library. Last, and only if reviewer pressure justifies it.

**Label policy, decided once and stated in the thesis:** an 80%-occluded target
keeps its full original box. Ground truth is "a target is present here," not
"visible pixels are here." Shrinking boxes would quietly convert an occlusion
experiment into a small-object-detection experiment.

**The leakage trap, and it's serious:** if you use occlusion as *training*
augmentation and only ever paste occluders over targets, the model learns "pasted
foliage texture ⇒ target underneath." It'll score beautifully on your synthetic test
set and fail completely on real occlusion. `--distractor-rate` pastes identical
occluders at random background locations. **Always use it for training data:**
```bash
uv run python occlusion/occlude.py --in .../train --out .../train_occ \
    --frac 0.35 --frac-jitter 0.2 --mode texture --distractor-rate 1.0 --seed 42
```

The tool preserves the source class map, so it works unchanged on the multi-class
Weitefeld output and on your own HPI data later.

### P1.6 — The controlled sweeps (~1 day) ← first real thesis results

**Sweep 1, person / O1.** Baseline A against every frozen HERIDAL bucket:
```bash
for f in 0 10 20 40 60 80; do
  uv run python eval/evaluate.py \
      --weights ../results/runs/p1_heridal_yolo11s/weights/best.pt \
      --data ../data/occluded/heridal_occ_v1/frac_$f \
      --run-id p1_occ_heridal_frac$f --occlusion-frac 0.$f --occlusion-mode texture
done
```

**Sweep 2, HPI.** Same procedure on Weitefeld, per class. This is the one that
speaks to your primary contribution, and it has no equivalent in HERIDAL because
HERIDAL has no HPI classes. Worth stating plainly in the thesis: the person curve
and the HPI curve come from different source datasets and are not directly
comparable to each other — each is internally controlled, which is what makes each
one valid.

Plot precision, recall, and mAP@50 against occlusion fraction, per class. What to
look for: graceful degradation or a cliff? If mAP holds to 40% and collapses at 60%,
that cliff location is a real finding and it's the empirical justification for the
entire VLM verification arm — it says exactly where a single-pass detector stops
being sufficient, which is the premise of your hypothesis. A smooth gentle curve is
also a finding, and a more awkward one for the hypothesis. Better to know in month 2
than month 8.

Both sweeps run before ethics clearance, before a flight, before the Orin arrives.

### P1.7 — TensorRT export and on-device baseline (~half day, needs the Jetson)

```bash
# on the Jetson
yolo export model=best.pt format=engine half=True imgsz=1024 device=0
```

Benchmark with `jetson_clocks` locked, 200+ warm iterations, mean and p95 latency
plus `jtop` power. Log to `runs.csv`.

Two things that get missed:
- **Verify mAP after export.** FP16 quantisation usually costs almost nothing, but
  "usually" isn't a thesis claim. Re-run eval with the engine and report the delta
  per class. If HPI classes degrade more than `person` under quantisation — plausible,
  since they're rarer and lower-confidence — that's a genuine O2 finding.
- **Separate model inference time from end-to-end pipeline latency**, as your
  progress report methodology already promises. At `imgsz=1024` with tiling, tiling
  and NMS overhead is not negligible and reporting only the forward pass would
  overstate your frame rate.

**Phase 1 exit criteria:** validated single- and multi-class pipelines; locked
HERIDAL person baseline and Weitefeld HPI baseline with committed configs and
manifests; occlusion tool working in `cutout` and `texture` with frozen sets on
disk; two controlled degradation curves; TensorRT model with per-class on-device
latency and power logged.

---

## Sequencing

Week 1 ordering is rigid only because it's all external-latency items.

| When | What | Blocked by |
|---|---|---|
| Day 1 | Ethics email · Kaya account request · Arducam driver check · start Weitefeld download | nothing |
| Days 1–2 | HPI taxonomy + held-out split + instance targets | nothing |
| Days 2–4 | Repo layout, uv env, HERIDAL download | nothing |
| Days 4–6 | Both converters + verify renders | downloads |
| Week 2 | Overfit gates, both baseline runs | converters |
| Week 2 (parallel) | CVAT, annotation protocol writeup | taxonomy |
| Week 3 | Eval harness (per-class, sliced, SAR metric), occlusion tool | baselines |
| Week 4 | Both occlusion sweeps, first figures | occlusion tool |
| On arrival | P0.8 Jetson block, then P1.7 | hardware |
| Throughout | Site recon, flight planning, DJI test flights | ethics |

The Jetson block is genuinely detached — arriving in week 2 or week 6 changes
nothing above.

---

## Documents to update

**`technical_work_timeline.md`**
- Phase 0 says JetPack 6.2; revise once D2 resolves.
- Phase 1 should list the Weitefeld baseline and the controlled occlusion sweeps as
  Phase 1 deliverables, not Phase 3 ones. They need no external dependency and they
  produce your first results.
- Phase 2's risk framing softens: with Weitefeld in hand, ethics delay is no longer
  project-fatal, and the critical-path diagram should reflect that.

**`objective_changes_since_progress_report.md`**
- Add Weitefeld: what it is, why it's used, and how your contribution is positioned
  against it. It's a novelty consideration, not just a resource.
- The O4 wording mismatch you flagged should be resolved in the proposal and lit
  review, not just noted here. Suggested rewording that keeps the underlying
  question intact while matching the method: *"Does routing low-confidence
  detections to an onboard VLM for verification, and handling untrained HPI classes
  via open-vocabulary inference, recover recall and mAP@50 without a net precision
  loss or breaching the real-time latency budget on the Orin Nano Super?"* Flag the
  change explicitly in the proposal rather than silently substituting it —
  supervisors notice, and a documented, justified change reads far better than an
  undocumented one.

**`dev_notes.md`**
- Add a "Vision pipeline" section mirroring the PX4/ROS2 one.
- Record the pinned PX4 / Gazebo / ROS2 versions from P0.7.

**Minor:** the removed setup prompt described VOC as volatile organic compound /
scent sensing; `objective_changes_since_progress_report.md` describes it as
voice/operator control interface. Either way it's out of scope, but the team-split
description should be consistent wherever it appears in the thesis.

---

# Phase 2 — Dataset collection

The real critical path, and the phase where mistakes are unrecoverable: a training
run can be repeated in a day, a badly-collected field season cannot.

Two things from rev. 2 change how this phase runs. First, HPI is the primary
contribution, so collection is now driven by per-class instance targets rather than
"get some bush footage." Second, Weitefeld means a delay here is no longer
project-fatal — you have a real HPI fallback — which buys you the freedom to collect
properly rather than desperately.

## P2.0 — Split the collection by ethics dependency (do this first, ~30 min)

The single most useful realisation available in this phase: **only the `person`
class needs human ethics approval.** Backpacks, tents, clothing, water bottles,
footwear, trail tape, campfire remains and discarded gear are objects in bushland.
No human subject, no ethics gate.

So split your session plan in two:

| Track | Classes | Gate |
|---|---|---|
| **Object-only** | every HPI class, trained and held-out | None. Start now. |
| **Person-present** | `person`, plus person+HPI co-occurrence frames | Ethics approval |

That covers roughly 80% of your collection volume with no external dependency. Do
the object-only sessions while ethics is pending, and you arrive at approval already
holding most of your dataset instead of starting from zero.

Two caveats worth handling explicitly rather than assuming:
- **Incidental people.** You, a spotter, or a passing bushwalker may enter frame.
  Decide the policy now — cleanest is to cut those clips entirely from object-only
  sessions rather than argue about them later. Note it in the session log.
- **Confirm with Kieran** that object-only collection in public bushland carries no
  requirement you've missed. It's a one-line addition to the email you're already
  sending, and it converts an assumption into a documented answer.

## P2.1 — Site selection and recon (~1 day, before any collection flying)

**Three or more distinct sites, not one site visited repeatedly.** A single
location's canopy type, density, ground litter and typical lighting otherwise get
baked into your dataset as a hidden confound, and you can't separate "my model
learned to detect backpacks" from "my model learned to detect backpacks in one
particular patch of jarrah."

Per site, check and record:
- Landholder or park permission — separate from CASA flight rules, and the thing
  most likely to be forgotten
- CASA sub-2 kg excluded-RPA conditions for the location (airspace, proximity to
  people, VLOS)
- **A range of canopy densities within the site** — open, moderate, dense. If every
  site is uniformly open, your real-occlusion range is artificially narrow and the
  synthetic sweep is doing all the work
- Safe launch/land points, and whether VLOS is maintainable across the area you
  want to cover
- Mobile coverage (for emergencies, and for checking anything mid-session)

Write a one-paragraph site description per location — vegetation type, canopy
density estimate, terrain, typical lighting. These become a thesis table and they
support the per-site domain analysis later.

## P2.2 — Altitude bands and the FOV correction (~1 hour of arithmetic, high stakes)

Your timeline says to fly the DJI "adjusted upward to roughly account for the FOV
gap." That's the right instinct, but the magnitude is much larger than "roughly"
suggests, and getting it wrong quietly invalidates the DJI-to-Arducam transfer.

**Match ground sample distance (pixels-on-target), not ground coverage.** What
determines whether a detector can see a backpack is how many pixels the backpack
occupies, and that is GSD.

```
ground_width = 2 · h · tan(FOV / 2)
GSD          = ground_width / image_width_px

For matched GSD between two cameras:
h_dji = h_arducam · [ tan(FOV_ard/2) / tan(FOV_dji/2) ] · [ res_dji / res_ard ]
```

With DJI ≈ 88.9° and Arducam ≈ 145°, both capturing at 3840 px wide:

**h_dji ≈ 3.2 × h_arducam**

| Arducam operational altitude | Equivalent DJI altitude |
|---|---|
| 5 m | ~16 m |
| 7.5 m | ~24 m |
| 10 m | ~32 m |

If your DJI's FOV is actually ~82° (common on Mini-series), the factor rises to
~3.6 and the band becomes ~18–36 m. **Recompute with your drone's real spec sheet
and your real capture resolution before the first session** — don't inherit my
numbers.

Why this matters: flying the DJI at a literal 5–10 m gives you *far* more pixels per
target than the Arducam will ever deliver at the same height. Train on that and your
Phase 3 numbers are optimistic in a way that only surfaces when you finally fly the
real camera, which is exactly when you have no time left to fix it.

Fly **2–3 bands** within the corrected range per staged scene where time allows. The
scale variation is free and it hedges the residual domain gap.

Record the correction and its derivation in the methods section. A reviewer asking
"how do you justify training on data from a different camera" gets answered with
arithmetic rather than hand-waving.

## P2.3 — Session design and staging (~2 hours per session, planned in advance)

Unstructured bushwalk footage is not a dataset. Every session is a plan for
populating specific classes at specific difficulty levels.

**Plan each session against the class-count gap.** Before you drive out: look at the
tracker (P2.6), identify the two or three classes furthest behind target, and design
the session around them.

**Stage deliberately across occlusion levels.** Place the same object three ways —
fully exposed, partially under a bush, deep under canopy. This is your *real*
occlusion data, and it's what proves the synthetic sweep in P1.6 isn't a synthetic-
only artifact. Two independent lines of evidence pointing the same way is a much
stronger thesis argument than either alone.

**Stage co-occurrence, once ethics allows.** Put HPI objects near but not on the
volunteer — a backpack a few metres off, clothing on a branch, a tent under partial
canopy. Real SAR scenes contain a person *and* their traces; a dataset where the two
never co-occur can't represent that.

**Collect negatives on purpose.** Empty bush, fallen logs, rocks, dark shadow
patches, anything shaped vaguely person-like. A dataset of only positive-containing
frames trains a model that has never seen "nothing here." Your negative-tile ratios
in P1.1/P1.2 only work because those datasets contain real empty terrain — yours
needs the same.

**Multiple passes and headings per staged scene.** Two or three passes at different
angles over the same arrangement gives you the viewpoint-shift-reveals-occluded-
target effect. That's directly the Phase 5 temporal accumulation argument, and
Weitefeld's back-projection design shows why it matters — an object invisible from
one angle is often visible from the next.

**Vary lighting across sessions.** Morning, midday, overcast, late afternoon. You're
already augmenting `hsv_v=0.5` for this; real variation validates that the
augmentation is doing something honest.

**Stills for training, video for the temporal arm.** Shoot stills as the primary
asset at every staged scene. Additionally, run at least one **slow, steady pass** per
site capturing video over staged scenes at varied real occlusion levels — that's the
temporal accumulation arm's data. Fast or erratic passes produce frames with too
little frame-to-frame correspondence to accumulate anything, so pass speed matters
and belongs in the session log.

## P2.4 — What to capture besides pixels (~15 min per session)

Pure RGB isn't enough, mostly because of the D5 confound: without altitude you can't
scale-match your imagery to HERIDAL, and the occlusion-vs-scale separation collapses.

DJI writes an `.SRT` sidecar alongside every video containing per-frame GPS,
altitude and speed — free, provided video captions are enabled in camera settings.
Check yours: on some consumer models the SRT carries position but **not** gimbal
pitch or heading, in which case log gimbal angle manually per session.

| Field | Source | Why |
|---|---|---|
| Altitude AGL | SRT | GSD calculation, HERIDAL scale-matching, altitude stratification |
| GPS | SRT | Site tagging, avoiding accidental duplicate coverage |
| Timestamp | SRT | Lighting-condition tagging |
| Gimbal pitch | SRT if present, else manual | Nadir vs oblique difficulty; Weitefeld reports this |
| Camera FOV / resolution | One-off per device | The P2.2 correction |
| Site ID, canopy notes, weather | Manual log sheet | Domain-gap and per-site analysis |

Parse the SRT to **one manifest row per clip**, not per frame — clip-level
resolution is plenty for thesis-level analysis and keeps the manifest readable.
`dji-drone-metadata-embedder` or `dji-telemetry` will do it, or parse it directly:
it's plain text.

**Offload and back up the same day.** A corrupt SD card erases a staged field
session that cannot be recreated.

## P2.5 — Annotation loop (~2–4 hours per session's footage)

**Annotate each session before planning the next.** Your timeline already says this
and it's right — the reason is that protocol ambiguities ("is a half-buried tarp a
`shelter_tent` or `discarded_gear`?") surface during annotation, and catching one
after two sessions costs an hour while catching it after ten costs the dataset.

Working in CVAT (configured in P0.6 with the locked label set):
- **Stills** are annotated individually — no interpolation available, and none needed.
  These are the detector training set.
- **Video** (temporal arm only) uses frame interpolation: track a box across the clip
  rather than drawing every frame, and sample every 10th–15th frame. Consecutive
  frames at 30 fps are near-identical, so annotating all of them inflates box counts
  without adding information.
- Tag video-derived annotations `provenance = dji_video` and keep them out of the
  Phase 3 detector training set. Mixing them in would let one placement contribute
  dozens of near-identical boxes and quietly wreck your class balance.
- Export to YOLO format; `occlude.py` and the eval harness consume it unchanged
  since they preserve arbitrary class maps.

**Run an inter-annotator agreement check.** You criticise Weitefeld's crowd-sourced
labels for subjectivity in your methods section — so demonstrate that yours aren't.
Have a second person annotate 50 frames independently, or re-annotate them yourself
blind three weeks later, and report agreement (IoU overlap and class agreement
rate). An afternoon's work that converts a potential weakness into a stated strength.

## P2.6 — Instance counting, and a correction to the P0.2 targets

The P0.2 targets (≥300 trained, ≥150 held-out) were underspecified, and the
ambiguity matters enough to fix here.

**Count unique physical placements, not annotated boxes.** One tent, filmed for 30
seconds, sampled every 10th frame, yields ~90 boxes — but it is *one* tent, in one
spot, in one light. Those 90 boxes are not 90 independent observations, and treating
them as such inflates your apparent sample size by an order of magnitude while
teaching the model one tent.

Revised targets, tracked separately:

| Class tier | Unique placements | Annotated boxes | Sessions / sites |
|---|---|---|---|
| Trained HPI | ≥40 per class | ≥800 per class | ≥5 sessions, ≥3 sites |
| Held-out HPI | ≥25 per class | ≥400 per class | ≥4 sessions, ≥3 sites |
| `person` | ≥30 distinct poses/positions | ≥800 | ≥4 sessions, ≥3 sites |

A "placement" = a specific object at a specific location in a specific session.
Moving the same backpack ten metres and re-shooting counts as a new placement;
circling it for another pass does not.

**Be honest about what this means for your held-out result.** With ≥25 placements
per held-out class and a site-level test split, your test set holds maybe 8–12
placements per class. That is thin, and it's the evidence base for your headline
Phase 4 claim. Two mitigations, both cheap:
- Report **bootstrap confidence intervals resampled over placements**, not over
  boxes. Resampling boxes would give you falsely tight intervals for exactly the
  reason above.
- State the limitation explicitly in the discussion rather than waiting to be asked.

If the targets look unreachable given available flying time, **cut classes rather
than accept thin ones**. Three well-populated HPI classes beat seven starved ones,
and it is far easier to defend.

Track counts in the manifest and check after every session. A spreadsheet column per
class, updated the same day you annotate.

## P2.7 — Arducam calibration and validation batch (~half day, parallel, no airframe needed)

Doesn't wait on the build, and shouldn't.

1. **Checkerboard calibration** — twenty minutes with OpenCV, gives you the real
   distortion profile of the 145° lens. Do it the day the camera arrives (it's
   already listed in P0.8 step 7).
2. **Small validation-only batch** — handheld or on a boom pole at roughly the right
   height and downward angle, over a few staged scenes you've already shot with the
   DJI. Target maybe 100–200 frames.
3. **This batch is test-only. Never train on it.** Its entire job is to answer "does
   a model trained on GSD-matched DJI imagery transfer to the actual sensor," which
   is the (3) component of the D5 confound. Training on it destroys that.

Shooting the *same staged scenes* with both cameras is what makes this a controlled
comparison rather than two unrelated datasets. Worth the extra trip.

## P2.8 — Dataset assembly and hygiene (ongoing)

- **Split by placement at minimum, and never split a video clip across splits.**
  Same principle as the tile-level rule in P1.1 and the finding-level rule in P1.2 —
  see P1.0 for why it's one principle rather than three rules. Stills from one
  placement and frames from one clip are both near-duplicates; leaking either across
  splits inflates val/test scores by a large, entirely fake margin. Prefer splitting
  by *site* for the test set where you have enough sites — it's the strictest and
  most honest split, and it answers "does this generalise to bush I haven't flown."
- **Tag provenance per image**: `dji_still` (detector training), `dji_video`
  (temporal arm only, excluded from Phase 3 training), `arducam_handheld` (test only),
  `heridal`, `weitefeld`, `synthetic_occlusion`. The `provenance_filter` column in
  `runs.csv` exists to slice on this.
- **Check class balance per source periodically.** Video over-represents `person`
  relative to single-instance HPI objects. Catch it early; it's much cheaper to fix
  with a targeted session than with loss weighting after the fact.
- **Keep the held-out classes genuinely sealed.** Physically separate directory, not
  just a config flag. The failure mode — accidentally including a held-out class in
  a training run and not noticing — invalidates your strongest result, and it is
  exactly the kind of thing a `--drop-classes` flag silently gets wrong.
- **Version the dataset.** `bush_v1`, `bush_v2` as collection proceeds. The
  `dataset_version` column in `runs.csv` is meaningless if the underlying data
  mutates in place.

## Phase 2 exit criteria

- ≥3 sites, ≥5 sessions collected, per-class placement and box targets met or
  consciously rescoped
- Every clip in the manifest with provenance, site, session, altitude, GSD, gimbal
  angle, lighting
- All stills annotated to the locked protocol, IAA check done and reported
- ≥15 slow-pass video clips across ≥3 sites for the temporal arm, annotated and
  tagged `dji_video`, verified absent from the detector training set
- Arducam calibrated, validation batch captured, sealed as test-only
- Held-out classes physically separated and verified absent from training splits
- Combined dataset assembled: HERIDAL + Weitefeld + bush + synthetic-occlusion, all
  provenance-tagged, split by site/session
- Dataset tagged and versioned; a training run can be reproduced from the manifest
  alone

## Standing risks in this phase

**Weather.** Perth winter and consistent bush lighting don't cooperate on demand.
Front-load object-only sessions during any good-weather window rather than waiting
for a tidy schedule.

**Ethics slip.** Mitigated three ways now: object-only collection proceeds
regardless, Weitefeld provides a real HPI fallback, and the Phase 1 sweeps produce
results without any collected data at all. Worth stating this mitigation explicitly
to your supervisor — it's a meaningful de-risking of what your own timeline calls
the project's biggest threat.

**Scope creep in the class list.** The temptation to add "just one more class" mid-
collection is strong and it will wreck your balance targets and your annotation
consistency. The taxonomy locked in P0.2 is locked. Write new ideas down for future
work instead.

---

# Phase 3 — Architecture sweep and pipeline comparison

Where the thesis contribution actually gets made. Phases 0–2 built and validated the
instruments; this is the measurement.

Two structural points before the detail. First, Phase 3 is a **tournament with
elimination rounds**, not a flat grid — the winner of each stage is the only thing
carried into the next, otherwise the run count explodes combinatorially. Second,
every arm is evaluated on **accuracy, latency, and resource use together on the
actual Orin Nano Super**. A model that wins on mAP but can't hit frame rate on-device
is not an answer to O2.

See `COMPARISON_DEPENDENCY_FLOWCHART.md` for the dependency graph and what gates what.

---

## P3.0 — Dataset decisions since rev. 2, and what they change

Two collection decisions have been made that alter Phase 3's evaluation assumptions.
Both are recorded here because they invalidate specific assumptions written into
Phase 2 and into the original timeline.

### Decision (revised): stills primary, video collected alongside

Originally scoped as stills-only. Revised: **collect both.** Stills remain the
primary training source; video is captured in parallel at the same sessions to keep
the temporal accumulation arm alive.

The reasoning is sound and worth stating explicitly, because it's a general principle
worth applying elsewhere: **you can always train without the video, but you cannot
retroactively collect it.** Training runs are repeatable in a day. A field session is
not. When the cost of capturing something is low and the cost of not having it is
"drive back out to three sites," capture it. Video costs an SD card and some offload
time.

**What this does and doesn't change.**

| | Status |
|---|---|
| Primary detector training | **Stills only.** Unchanged. Video frames do not enter the Phase 3 training set. |
| Instance-count targets | **Unchanged** — still placement-based (see the revised table below). Video does not count toward them. |
| Temporal accumulation arm (Phase 5) | **Alive again**, with its own data source |
| Annotation burden | Increases, but only for the temporal arm's subset — not the whole dataset |
| Split hygiene | Gains a clip-level rule layered on top of the placement rule |

**Keep the video out of the detector training set.** This matters. If you sample
frames from video into the main training set, a single placement contributes dozens
of near-identical boxes, your class balance silently skews toward whatever you happened
to film longest, and the placement-based targets stop meaning anything. Video is a
separate asset for a separate experiment. Tag it `provenance = dji_video` and filter
it out of Phase 3 training explicitly rather than by intention.

**Now you get two independent lines of evidence for the temporal claim**, which is
strictly better than either alone:

| Source | What it tests | Strength |
|---|---|---|
| **Your own drone video** | True temporal accumulation — does a single continuous low-altitude pass naturally accumulate enough evidence across consecutive frames to recover an occluded target? | Directly matches the deployed system's actual behaviour |
| **Weitefeld multi-view** | Viewpoint-diversity accumulation — does aggregating across angles recover occluded targets? | Real occlusion, real forest, 405 findings, up to 85 views each, zero collection cost |

Keep reporting them as **different claims**. Your video answers "does my drone's
flight pattern accumulate evidence over time." Weitefeld answers "does angle
diversity help in principle, on real forest occlusion at scale." Conflating them
would overstate what either shows; presenting both, clearly distinguished, is a
stronger result than one alone.

**New technical work this adds — budget for it.** Temporal accumulation needs
**tracking**: associating detections of the same object across consecutive frames so
evidence can be aggregated rather than treated as unrelated detections. Ultralytics
ships ByteTrack and BoT-SORT and they run on top of any detect model, so this isn't
from-scratch work, but it is a real component with its own failure modes (identity
switches, track fragmentation under occlusion — which is, awkwardly, exactly the
condition you're studying). Treat tracker choice and tuning as its own small
sub-experiment rather than assuming defaults will hold up.

**Flight discipline for usable temporal data.** Consecutive frames need meaningful
overlap for accumulation to have anything to accumulate. Fly the temporal passes
**slow and steady** over staged scenes, not fast or erratically. A fast pass gives
you frames with little frame-to-frame correspondence, which is video that looks fine
and is useless for the experiment. Note the pass speed in the session log.

**Annotation approach for video.** Use CVAT's frame interpolation here — track a box
across the clip rather than drawing each frame — and sample every 10th–15th frame.
This is the workflow the earlier stills-only revision removed; it's back, but scoped
to the temporal subset only.

**Split hygiene.** Two layers now, and both apply: split by **placement or site**
(the stills rule), and additionally never split a **video clip** across train/val/test.
Every frame of one clip stays in one split. In practice the clip sits inside a
placement anyway, so honouring the placement rule usually satisfies the clip rule —
but assert it rather than assuming.

**Instance targets (revises P2.6).** Unchanged from the stills-only revision, because
placements remain the unit that matters and video contributes to the temporal arm
rather than to detector training:

| Class tier | Unique placements | Annotated boxes (stills) | Sessions / sites |
|---|---|---|---|
| Trained HPI | ≥40 per class | ≥400 per class | ≥5 sessions, ≥3 sites |
| Held-out HPI | ≥25 per class | ≥250 per class | ≥4 sessions, ≥3 sites |
| `person` | ≥30 distinct poses/positions | ≥400 | ≥4 sessions, ≥3 sites |

Separately, for the temporal arm: aim for **≥15 slow-pass clips** spanning a range of
real occlusion levels, across ≥3 sites. Fewer than that and the temporal result rests
on too little to say much.

**If the temporal arm doesn't work out, that's fine.** You'll have spent SD card space
and some annotation time, and the main detector results are untouched because video
never entered that training set. That asymmetry — cheap to have, expensive to lack —
is exactly why collecting it is the right call.

### Decision: no FOV compensation, varied angles and positions instead

The P2.2 altitude correction is dropped. Same subject captured at varied angles and
positions directly, no lens-difference correction.

**What this buys you:** viewpoint diversity, which genuinely helps generalisation and
partially addresses the occlusion-gaps-revealed-by-angle question.

**What it does not buy you, and this must be stated as a limitation:** viewpoint
diversity and scale matching are orthogonal. Varying the angle doesn't change the
fact that a DJI frame at a given height puts more pixels on a backpack than the
145° Arducam will at the same height. The scale component of the D5 confound is now
uncontrolled at capture time, so it has to be handled at training and reporting time
instead:

1. **Keep scale augmentation aggressive.** `scale=0.5` in the training configs was
   already a hedge; it's now load-bearing rather than precautionary. Consider
   multi-scale training as well.
2. **Measure and report the pixels-per-target distribution** for the DJI training set
   versus the Arducam validation batch. If the two distributions barely overlap, that
   is a quantified, honest limitation. If they overlap substantially, the concern was
   overstated and you can say so with evidence. Either result is publishable; the
   unacceptable outcome is not knowing.
3. **The Arducam validation batch (P2.7) is now your only measurement of the
   DJI→Arducam gap.** It was a nice-to-have under the altitude-corrected plan. It is
   now the single piece of evidence that your trained model transfers to the
   deployment sensor. Do not skip it, and do not let it shrink.

Add to the thesis limitations section explicitly: training imagery was captured on a
different sensor with a narrower field of view, without geometric scale
normalisation; transfer was assessed on a held-out validation batch from the
deployment camera rather than controlled at capture time.

---

## D6 — Datasets stay separate (decided)

The primary bush dataset is **not** combined with HERIDAL or Weitefeld for training or
reporting. Consequences to enforce mechanically rather than by intention:

- All Phase 3 arms train and evaluate on the bush dataset only.
- HERIDAL and Weitefeld stay confined to their Phase 1 role: pipeline validation and
  the two occlusion sweeps.
- Every Phase 3 row in `runs.csv` carries `provenance_filter = bush_own`. Anything
  else in that column during Phase 3 is a bug, and it's worth a one-line assertion in
  `evaluate.py` that fails loudly rather than a convention you have to remember.

## D7 — Initialisation: what do the Phase 3 models start from?

D6 settles *mixing*, but not *initialisation*, and these are genuinely different
questions. Three options:

| Init | Argument |
|---|---|
| **COCO-pretrained** (default) | Standard, uncontroversial, what every YOLO baseline does. |
| **Weitefeld-pretrained → bush fine-tune** | Domain-relevant pretraining on real occluded aerial HPI. Plausibly better than generic COCO for this task. |
| **From scratch** | Not defensible for any arm in the current shortlist — your dataset is far too small. All six candidates assume a pretrained checkpoint. |

**Recommendation: COCO-pretrained as the default for all arms, plus one clearly
labelled side experiment** comparing COCO-init against Weitefeld-init on the winning
architecture only. That side experiment is cheap (two runs), it doesn't violate D6
because the datasets are never mixed — only sequenced — and "does domain-relevant
pretraining beat generic pretraining for SAR detection" is a genuinely publishable
minor finding. Report it separately from the main results so the separation stays
legible.

Do not let Weitefeld-init become the silent default for every arm. That would
entangle the two datasets in exactly the way D6 exists to prevent.

---

## P3.1 — Candidate architecture search (~2 days reading, ~1 day shortlisting)

Broaden past what's currently scoped. Five families are worth considering, and the
shortlist should name one or two per family rather than sampling one family densely.
One hard admission rule applies throughout: **no architecture requiring custom CUDA
kernels.**

### The families

**1. CNN-based YOLO (the production baseline).** YOLO11 (your Phase 1 baseline),
YOLOv8. Mature, exhaustively benchmarked, TensorRT export is a solved problem.

**2. Edge-optimised YOLO.** **YOLO26** (Ultralytics, January 2026) — DFL-free
regression, native end-to-end NMS-free inference, ProgLoss, Small-Target-Aware Label
Assignment (STAL), MuSGD optimizer. 40.9–57.5 mAP on COCO at 1.7–11.8 ms T4 TensorRT,
and up to 43% faster CPU ONNX inference for the nano variant versus YOLO11n.

Two things make this the most relevant single release to your project:
- **It's engineered for exactly your deployment target.** Ultralytics benchmarked it
  on NVIDIA Orin Jetson platforms specifically, and NMS-free inference removes a
  post-processing step whose cost you'd otherwise be measuring and defending.
- **`yolo26-p2.yaml` adds a P2 small-object detection head.** Your entire problem is
  small occluded targets. This is directly on point. Note the constraint: P2 and P6
  variants ship as **YAML architectures only, with no pretrained `yolo26*-p2.pt`
  weights** — you instantiate from YAML (`YOLO("yolo26n-p2.yaml")`) and train or
  fine-tune yourself. Budget for that; it's not a drop-in checkpoint.

**3. Attention / transformer detectors.** **YOLOv12** introduced area-based
self-attention into the YOLO line. **RT-DETR** is the true transformer detector, and
it's supported natively in Ultralytics, which matters for keeping one toolchain.

**4. Attention-augmented CNN.** **YOLOv12** introduced area-based self-attention into
the YOLO line — attention inside an otherwise convolutional detector, which is a
distinct point from a full encoder-decoder transformer. Ultralytics-native, so it
costs one line.

**5. Modern DETR-line real-time detectors.** **RF-DETR** (Roboflow, Apache-2.0) and
**D-FINE**. These have overtaken RT-DETR v1, which is now dated — at small scale
YOLOv13-S reaches 48.0 AP while D-FINE-S hits 48.5 and DEIM-S 49.0 at fewer
parameters.

### Also worth a look, outside the four families

- **YOLOE** and **YOLO-World** — open-vocabulary, both Ultralytics-supported. These
  are your D-arm candidates, not general detector candidates.
- **RTMDet** — MIT licensed, 300+ FPS for pure-throughput scenarios, but MMDetection
  packaging means a second framework. Cite published numbers rather than running it
  unless throughput specifically becomes the question.
- **Faster R-CNN** — the classical two-stage anchor. You already hold the paper. Also
  a second framework, so prefer citing published numbers for the "what did we gain
  over the standard approach" comparison rather than running it yourself.

### Shortlisting rule

Cap the sweep at **six architectures**, and — the constraint that actually matters —
**admit nothing that requires custom CUDA kernel compilation.** See "Scope decision:
SSM arms scrapped" below for why that rule exists. Every architecture you add
multiplies through the downstream tournament, and every exotic build multiplies your
schedule risk rather than your insight.

The six, with cost tiering:

| # | Model | Structural axis | Tier |
|---|---|---|---|
| 1 | **YOLO11s** | Pure CNN, local convolution. Phase 1 continuity. | Free — Ultralytics-native |
| 2 | **YOLO26s** | Edge-optimised CNN, NMS-free, DFL-free, P2 head available | Free — Ultralytics-native |
| 3 | **YOLOv12s** | Area-based self-attention *inside* a CNN detector | Free — Ultralytics-native |
| 4 | **YOLOv13s** | Hypergraph, global high-order correlation | Moderate — separate repo, standard PyTorch |
| 5 | **RF-DETR** | Full transformer, Apache-2.0, domain-transfer leader | Moderate — separate repo |
| 6 | **D-FINE-S** | DETR with distribution-refinement regression — better *localisation*, which is exactly where small targets are punished | Moderate — separate repo |

**Zero-friction swap for #6:** **RT-DETR** is Ultralytics-native and costs nothing, at
the price of being a dated reference point. Take it if you want four free arms and
only two moderate ones.

**License note:** YOLO11, YOLO26, YOLOv12 and YOLOv13 all inherit AGPL-3.0 from the
Ultralytics codebase. **RF-DETR is Apache-2.0**, which makes it your one non-AGPL
option — worth having deliberately, since it's the fallback if the licence becomes a
constraint on releasing code.

### Scope decision: SSM / Mamba arms scrapped

Mamba-YOLO and MambaNeXt-YOLO were scoped as the state-space arm and have been
**removed after consideration, on time-constraint grounds.** Recording the reasoning
here because a documented rejection is worth more than silence, and because it
generalises into a selection rule.

Both depend on hand-written `selective_scan` CUDA kernels rather than standard
PyTorch operations. That creates three independent failure points, none of which is
"slow but certain":

1. Compiling against the exact CUDA, PyTorch and GPU-architecture combination on the
   training machine.
2. Compiling **again** on the Jetson, which is ARM64 — a target almost none of these
   projects test against, since their authors build on x86 desktops.
3. Surviving TensorRT export. TensorRT must recognise every operation in the graph;
   custom ops routinely need a hand-written plugin, and writing one is its own
   software project.

Any of the three can consume days with no guarantee at the end. That is categorically
different from ordinary training, where more time reliably buys a better result. With
Phase 4 already the riskiest part of the build, spending schedule on an architecture
that may simply not deploy is a bad trade.

**The general rule this yields, which applies to every future candidate:** admit no
architecture that requires custom CUDA kernels for either training or export. Novel
operations are a research risk; the thesis's contribution is elsewhere.

**The papers stay in the literature review.** You hold Vision Mamba, VMamba and
MambaNeXt-YOLO. They belong in related work as the state-space lineage — Mamba
(sequence modelling) → Vim / VMamba (vision backbones, linear complexity) →
MambaNeXt-YOLO (detection-adapted hybrid) — with a stated note that SSM detectors
were evaluated for inclusion and excluded on deployment-risk grounds rather than on
their merits. That is an honest and defensible scope decision, and it pre-empts the
question of why an obviously relevant architecture family is absent.

---

## P3.2 — YOLO sub-comparison: correcting the premise first

The sub-comparison was originally framed as **YOLOv13 (CNN) vs YOLOv26 (transformer)
vs a YOLO-SSM variant**. Two of those three characterisations are wrong, and building
a comparison on them would produce a claim a reviewer can dismantle in one sentence.
The SSM arm has since been scrapped separately (P3.1), but the characterisations
still need correcting because YOLOv13 and YOLO26 both remain in the sweep.

### What these models actually are

| Model | Actually is | Source |
|---|---|---|
| **YOLOv13** | CNN + **hypergraph** correlation modelling. HyperACE (Hypergraph-based Adaptive Correlation Enhancement) treats pixels in multi-scale feature maps as hypergraph vertices with learnable hyperedge construction, plus FullPAD distribution and depthwise separable convs. Explicitly positioned as going *beyond* both YOLO11's convolutions and YOLOv12's area-based self-attention. | Lei et al., arXiv 2506.17733, June 2025 |
| **YOLOv26 / YOLO26** | **Not transformer-based — the opposite.** Ultralytics, January 2026. Deliberately de-complexified for edge: DFL removed, NMS-free end-to-end inference, ProgLoss, STAL, MuSGD. The literature explicitly frames it as breaking the recent pattern of adding transformer blocks and expensive post-processing. | Ultralytics, docs.ultralytics.com/models/yolo26; arXiv 2510.09653 |
| **The attention/transformer YOLO** | That's **YOLOv12** (area-based self-attention), or **RT-DETR** for a genuine transformer detector. | — |

So a three-way "CNN vs transformer vs SSM" framing was never the right description of
these models, independently of the SSM arm being dropped.

### The corrected sub-comparison

Run this as an explicitly named sub-experiment inside P3.1, on the same axes as
everything else (mAP@50, mAP@50-95 per class, latency mean/p95 on Orin, peak memory,
power):

| Arm | Architecture class | Why it's in |
|---|---|---|
| **YOLO11s** | Pure CNN, local convolution | Mature reference point and Phase 1 continuity — the thing everything else has to beat |
| **YOLO26s** | Edge-optimised CNN, NMS-free, DFL-free | Deployment-target-native; P2 small-object head available |
| **YOLOv12s** | Area-based self-attention inside a CNN | Attention *within* a convolutional detector, distinct from a full encoder-decoder |
| **YOLOv13s** | CNN + hypergraph high-order correlation | Global multi-to-multi correlation should, in principle, help with partially occluded targets whose visible fragments are spatially scattered — a directly testable hypothesis for your problem |
| **RF-DETR** | Full transformer, Apache-2.0 | Leads the RF100-VL **domain-transfer** benchmark, which is your HERIDAL→bush and DJI→Arducam problem restated. Selected for a property you actually need, not for COCO mAP. |
| **D-FINE-S** | DETR + distribution-refinement regression | Its contribution is specifically better **box localisation** — the axis where small targets get punished hardest under tight IoU |

**Frame the claim carefully.** The interesting question isn't "which YOLO is newest."
It's: *what architectural mechanism best recovers targets whose visible evidence is
fragmented by occlusion, under a hard real-time and memory budget?* Six arms, five
distinct answers:

- **Local convolution, mature** (YOLO11)
- **Local convolution, edge-optimised and NMS-free** (YOLO26)
- **Attention inside a CNN** (YOLOv12)
- **Global high-order correlation** (YOLOv13)
- **Full transformer, domain-transfer-selected** (RF-DETR)
- **Transformer with refined localisation** (D-FINE)

That's a defensible research design regardless of which wins, and it's a much better
answer under questioning than "I tested the six newest models."

**No exotic build risk in this lineup.** All six run on standard PyTorch operations,
so all six export to TensorRT through the ordinary path. That's deliberate — see the
scrapped-SSM scope decision in P3.1. Three of the six are Ultralytics-native and cost
one line each; the other three are separate repos but standard PyTorch, roughly a day
of tooling apiece.

---

## P3.3 — Training methodology: full fine-tune vs LoRA vs layer freezing

You asked whether to run standard Ultralytics full-model training against LoRA-style
fine-tuning as a comparison arm. Short answer: **the underlying question is worth
answering, but LoRA is the wrong instrument for it. Use layer freezing instead, and
save LoRA for Phase 4.**

### What LoRA actually adapts, for detection specifically

LoRA freezes the pretrained weights and injects a pair of trainable low-rank matrices
(rank *r*, typically 4–32) alongside each adapted weight matrix, so only the low-rank
update is learned. In the LLM setting it's applied to attention projections
(Q, K, V, O), which is where nearly all the parameters live and which are all dense
linear layers.

Detection is a different shape of problem:

- **YOLO detectors are overwhelmingly convolutional.** LoRA's low-rank decomposition
  is defined for linear layers. Applying it to `Conv2d` requires a LoRA-for-conv
  variant that decomposes the kernel, which is less standard, less well-supported, and
  not something Ultralytics ships.
- **The parameter distribution is different.** In an LLM, adapting attention
  projections covers most of the model. In a YOLO, the backbone convs, the neck, and
  the detection head are all substantial, and there is no single dense-layer family
  that dominates the parameter count.
- **Where LoRA genuinely fits in your project:** the **VLM** in Phase 4 (native
  transformer, LoRA is the standard adaptation method, well-supported tooling), and
  the **text encoder** of an open-vocabulary D-arm model like YOLO-World if you
  fine-tune it. Both are transformer components. Neither is the closed-set detector.

### What to run instead

The real question behind "LoRA vs full training" is **how much of the model needs to
move given a small dataset** — you have ≥40 placements per class, which is small.
Ultralytics answers that with one flag:

```bash
# Full fine-tune (default) — everything trainable
yolo detect train model=yolo26s.pt data=configs/bush_v1.yaml \
    epochs=150 imgsz=1024 seed=42 \
    project=../results/runs name=p3_train_full

# Backbone-frozen — train neck + head only
yolo detect train model=yolo26s.pt data=configs/bush_v1.yaml \
    epochs=150 imgsz=1024 seed=42 freeze=10 \
    project=../results/runs name=p3_train_freeze10
```

| | Full fine-tune | Freeze backbone (`freeze=10`) | LoRA |
|---|---|---|---|
| **Trainable params** | 100% | ~30–40% | ~1–5% |
| **Training time** | Baseline | ~30–50% faster | Faster, but needs custom code for convs |
| **Data efficiency on small sets** | Can overfit | Better — pretrained features preserved | Best in principle, unproven for conv detectors |
| **Final accuracy** | Usually highest given enough data | Slightly lower, sometimes higher on small data | Unclear for CNN detectors; no strong published baseline to cite |
| **Implementation cost** | Zero | Zero (one flag) | Days, plus a novel-implementation risk you'd have to defend |
| **Defensibility in a thesis** | Standard | Standard | You'd be defending your LoRA-for-conv implementation, not your research question |

### Recommendation

**Run full vs `freeze=10` as a genuine comparison arm — it's two runs and one flag,
and given your small dataset the answer is not obvious.** Report it as a training-
methodology result on the winning architecture only, not across all four.

**Drop LoRA from Phase 3 entirely.** The payoff is unclear, the implementation is
non-trivial for conv detectors, and — the decisive point — you would end up defending
your adaptation implementation rather than your actual research question. That's a
bad trade for a thesis with a fixed deadline and a Phase 4 that's already the riskiest
part of the build.

**Keep LoRA in scope for Phase 4** if you fine-tune a VLM. There it's native,
well-supported, and the standard method, so it needs no defending.

---

## P3.4 — Backbone and head comparison: A0 vs A2 vs A2b

Runs on the **winning architecture from P3.1/P3.2 only.** Running it across all six
architectures would multiply the sweep for no additional insight.

The problem this tests: `person` examples will substantially outnumber any individual
HPI class, so HPI classes risk being drowned out during training. Does architectural
separation fix that, and what does it cost?

| Arm | Structure | What it tests |
|---|---|---|
| **A0** | One backbone, one multi-class head. `person` and all HPI classes in a single output layer. | Baseline. Does the imbalance actually hurt? |
| **A2** | One shared backbone, **two heads** — one for `person`, one for HPI classes. Each head weighted and sampled independently. | Does separating the heads let HPI classes be up-weighted without starving `person`, and is the second head's latency overhead genuinely small (it should be — shared backbone, parallel heads, not a second forward pass)? |
| **A2b** | Two **fully separate models**, one for `person`, one for HPI. | Time-permitting stretch only. Maximum separation, but roughly double the inference cost and double the memory — likely fatal on 8 GB shared with a VLM. |

**Report per-class, always.** The entire point is what happens to the rare HPI
classes; aggregate mAP will hide it.

**Measure the second head's latency overhead explicitly** rather than assuming it's
negligible. If A2 wins on HPI mAP but costs 15 ms, that changes the deployment
argument and it's a number O2 needs.

**A2b decision rule, set now:** only run it if A2 beats A0 on HPI classes by a
meaningful margin *and* you have schedule left after Phase 4's VLM work. If A2 doesn't
beat A0, A2b almost certainly won't justify double the compute, and the honest finding
is that architectural separation wasn't necessary at this data scale.

---

## P3.5 — Pipeline configurations: the end-to-end comparison

This is the comparison that answers O4, and it's distinct from the architecture
comparisons above. Here you're comparing **whole pipelines**, with the model
architecture and head configuration already fixed by P3.1–P3.4.

### The configurations

| Config | Pipeline | Cost | What it establishes |
|---|---|---|---|
| **P-1: Detector only** | Winning detector, single forward pass per frame | Baseline latency | The floor. Everything else must beat this to justify itself. |
| **P-2: Detector + A1 (double detector)** | Detector → any detection below a lowered confidence threshold gets cropped and re-run through **the same detector** at higher effective resolution | ~10–15 ms per escalated crop | The cheap escalation tier. **This is the bar the VLM has to clear**, and it must be benchmarked before any VLM work starts. |
| **P-3: Detector + A1 + VLM (async)** | As P-2, plus a separate VLM worker consuming what A1 couldn't resolve, off a queue | Throughput-bounded, not latency-bounded | The full pipeline. Does generative reasoning add anything A1 didn't already recover? |
| **P-4: D-arm (open-vocabulary)** | YOLO-World / YOLOE / Grounding DINO, text-prompted at inference | One forward pass, no generation | The parallel alternative. Open-vocab flexibility at closed-set speed. |

Note P-4 runs **parallel to** the P-1/P-2/P-3 stack, not stacked with it. It's a
different answer to the same problem, not another tier.

### How these compose

The A1 tier exists specifically so the VLM is compared against a real cheap
alternative rather than against nothing. State the composition explicitly in the
thesis: detector → cheap re-detection on low-confidence crops → VLM only for what
survives that filter, plus held-out classes the detector was never trained on.
"Double detector pipeline" undersells it — there's a principled reason for the middle
tier.

### VLM measurement, and why it isn't a per-frame latency number

The detector runs synchronously at frame rate. The VLM worker consumes crops off a
queue at whatever throughput the hardware sustains, which will be well under frame
rate. So the meaningful metrics are:

- **Candidate clearance throughput** — crops verified per second
- **Queue backlog at a given flight speed** — does the queue grow unboundedly at
  5 m/s, and at what speed does it stabilise?
- **Time-to-verification** — how long between detection and VLM verdict

Reporting the VLM as "adds X ms per frame" would be both wrong and unflattering, since
it isn't inline. This reframing is already in your timeline and it's the right call.

### Pre-registered decision criteria (set these before seeing results)

Write these down now, so the VLM phase-out question is answered by criteria rather
than by post-hoc rationalisation:

- **A1 is adopted if** it recovers meaningfully more recall than P-1 at acceptable
  precision cost and stays within the latency budget. Given ~10–15 ms, the bar is low.
- **The VLM is adopted only if** it beats P-2 on held-out classes *and* on
  low-confidence verification, at a queue backlog that remains bounded at realistic
  flight speed. Beating P-1 is not sufficient — P-2 is the bar.
- **The D-arm displaces the VLM if** it matches VLM performance on held-out classes at
  one-forward-pass cost. This is the most likely outcome, and it would be a clean
  finding.
- **A negative result is a result.** "An onboard VLM does not justify its cost on an
  8 GB Orin Nano Super relative to a cheap re-detection pass and an open-vocabulary
  detector, under these conditions" is a genuinely useful contribution — arguably more
  useful than a positive one, because it tells other people building edge SAR systems
  not to bother, with quantified reasons.

---

## P3.6 — Occlusion sweep across survivors

Apply the frozen occlusion buckets (P1.5, `occlude.py`) to the **bush test set**, and
run every surviving candidate through them.

```bash
for f in 0 10 20 40 60 80; do
  uv run python occlusion/occlude.py \
      --in ../data/processed/bush_v1/test \
      --out ../data/occluded/bush_occ_v1/frac_$f \
      --frac 0.$f --mode texture --seed 42
done
```

Same rules as Phase 1: frozen sets on disk, byte-identical across models, achieved
fraction logged, per-class metrics.

**Cross-check against the real-occlusion subset.** Your Phase 2 collection staged
objects at varied real occlusion levels. Compare the synthetic degradation curve
against real-occluded imagery. Two independent lines of evidence agreeing is a much
stronger claim than either alone — and if they *disagree*, that's an important finding
about synthetic occlusion's validity that's worth reporting honestly.

---

## P3.7 — Held-out class evaluation

The headline Phase 4 result. Runs across P-1 through P-4.

Expected shape: P-1 and P-2 score at or near zero **by construction** — a closed-set
detector cannot detect a class it was never trained on. That's not a failure, it's the
control condition, and it's what makes any non-zero score from P-3 or P-4 cleanly
attributable to the thing you added.

**Report bootstrap confidence intervals resampled over placements, not boxes.** With
~8–12 held-out placements per class in the test split, this is a thin evidence base
and the CIs will be wide. Wide-but-honest beats narrow-and-wrong, and stating the
limitation before an examiner raises it is much stronger than defending it after.

**Verify the seal before running.** Assert programmatically that no held-out class ID
appears in any training manifest. A held-out class leaking into training invalidates
your strongest result, and it's exactly the kind of thing a config flag gets silently
wrong.

---

## Phase 3 sequencing

Elimination structure — each stage's winner is the only thing carried forward.

| Stage | Runs | Depends on | Output |
|---|---|---|---|
| P3.1/P3.2 architecture sweep | 6 architectures × 1 config | Phase 2 dataset, Phase 1 pipeline | Winning architecture |
| P3.3 training methodology | 2 runs (full vs freeze) | Winning architecture | Winning training recipe |
| D7 init side experiment | 2 runs (COCO vs Weitefeld init) | Winning architecture | Reported separately |
| P3.3b `yolo26-p2` ablation | 1 run | Only if YOLO26 wins | Small-object head verdict |
| P3.4 backbone/head | 2 runs (A0, A2), +1 if A2b | Winning architecture + recipe | Winning head config |
| P3.5 pipeline configs | 4 configs (P-1…P-4) | Winning head config; A1 before any VLM work | Pipeline comparison |
| P3.6 occlusion sweep | Survivors × 6 buckets | All above | Degradation curves |
| P3.7 held-out eval | Survivors × held-out set | All above; seal verified | Headline result |
| P3.8 scale sweep | 3 runs (n/s/m) on winner | Gate 1 | Accuracy/latency Pareto curve on the Orin — the direct answer to O2 |

Roughly 30–40 training/eval runs total. The elimination structure is what keeps that
from becoming 200+.

**On the scale sweep (P3.8), which is new and worth the three runs.** O2 asks about
accuracy versus latency versus resources on-device. Six architectures at one scale
each gives you six scattered points; running n/s/m on the winner gives you the actual
**Pareto curve** on your Orin. For an edge-deployment thesis the curve is the answer,
and it's the figure that demonstrates you understood the trade-off rather than just
picked a winner.

## Phase 3 exit criteria

- Six architectures benchmarked on accuracy, latency, memory, and power on the Orin
- Sub-comparison completed with correct architectural characterisations
- `yolo26-p2` ablation run if YOLO26 won, isolating the small-object head as a single
  variable
- Scale sweep (n/s/m) on the winner, giving the on-device Pareto curve
- Training methodology comparison (full vs freeze) reported on the winner
- A0 vs A2 reported per-class, with the second head's latency overhead measured
- All four pipeline configurations benchmarked, A1 established before VLM work began
- Occlusion degradation curves for survivors, cross-checked against real occlusion
- Held-out evaluation with bootstrap CIs over placements, seal verified
- Every run in `runs.csv` with `provenance_filter = bush_own`, per class, git SHA
  logged

## Documents to update after Phase 3 decisions land

**`technical_work_timeline.md`**
- Phase 3's detector list becomes the six-arm shortlist; add the sub-comparison and
  the corrected architectural characterisations.
- Record that the SSM/Mamba arms were considered and scrapped on time-constraint and
  deployment-risk grounds, and that the papers remain in related work.
- Add the training-methodology arm; record that LoRA was considered and dropped, with
  the reason. A documented rejection is worth more than silence.
- Add the scale sweep as the direct answer to O2.
- Phase 5's temporal accumulation arm: record the stills-only decision and the
  Weitefeld multi-view substitution.
- Phase 2: remove the FOV-compensation instruction, add varied-angle collection and
  the resulting limitation.

**`objective_changes_since_progress_report.md`**
- Log the stills-only and no-FOV-compensation decisions and their consequences.
- Log D6 (datasets separate) and D7 (initialisation), since the "Dataset plan
  finalised" section currently says training data will *combine* HERIDAL with the new
  dataset — that's now contradicted and needs correcting.
- Log the pre-registered pipeline decision criteria from P3.5.