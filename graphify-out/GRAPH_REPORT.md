# Graph Report - Search_Rescue_Drones  (2026-09-14)

## Corpus Check
- 74 files · ~411,725 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 289 file(s) not represented in the graph (top: .msg 257, (none) 12, .pt 7)

## Summary
- 447 nodes · 580 edges · 41 communities (22 shown, 14 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 57 edges (avg confidence: 0.88)
- Token cost: 24,000 input · 9,500 output

## Community Hubs (Navigation)
- PX4 Msgs Release Governance
- Project Hard Rules & Conventions
- Dataset Splits & Evaluation Conventions
- Phase 3 Elimination Tournament
- Jetson & Sim Ops
- SAR Detection Literature & Hardware Choice
- Phase 3 Architecture Sweep Rationale
- Baseline A/B Naming & Conventions
- HERIDAL YOLO Converter
- Training Methodology Gates
- Occlusion Tool Implementation
- Claude Code Skills Catalog
- PX4 Offboard Hover Demo
- Weitefeld YOLO Converter
- PX4/Gazebo/ROS2 Sim Stack
- Changelog Generator Script
- Detection Pipeline Comparison (P-1..P-4)
- Occlusion Label Policy & Rationale
- Weitefeld Dataset Adoption (D3)
- Blue Mountains Terrain Assets
- Altitude/FOV Dataset Decisions
- Model Architecture (Backbone/Neck/Head)
- Sim Launch Bringup
- Label Verification Tool
- Deb Container Build Script
- Blue Mountains Deploy Script
- Sim Startup Script
- Dev Notes & Sim Smoke Test
- CVAT Annotation Loop
- Terrain Generation Tools
- Vision Package
- Companion Computer Comparison Doc
- Training Loop Concept
- A0 vs A2 Reframing Rationale
- Occlusion Sweep Reframing Rationale
- Detector License Decision (D4)

## God Nodes (most connected - your core abstractions)
1. `Agent Instructions (CLAUDE.md, canonical)` - 31 edges
2. `px4_msgs Contributing Guide` - 19 edges
3. `px4_msgs README` - 17 edges
4. `Outline Skill (section writing plan)` - 16 edges
5. `Decision: Jetson Orin Nano Super (chosen companion computer)` - 15 edges
6. `Skills Index` - 14 edges
7. `Evaluate Skill (draft grading)` - 12 edges
8. `Thesis AI Setup bundle` - 11 edges
9. `Build Package Workflow (build.yml)` - 11 edges
10. `OffboardHelloWorld` - 10 edges

## Surprising Connections (you probably didn't know these)
- `gazebo_terrain_generator tool (real-world terrain worlds)` --semantically_similar_to--> `Graphify codebase knowledge graph tool`  [INFERRED] [semantically similar]
  simulation/sim_setup.README.md → README-SETUP.md
- `Phase 3 architecture sweep - six named architectures` --semantically_similar_to--> `STAGE 1 - Architecture sweep (P3.1/P3.2, 6 runs)`  [INFERRED] [semantically similar]
  training_nomenclature.md → thesis_docs/comparison_dependency_flowchart.md
- `Baseline A - HERIDAL yolo11s (person-only)` --semantically_similar_to--> `HERIDAL and Weitefeld baselines - Phase 1 only, never mixed into Phase 3`  [INFERRED] [semantically similar]
  training_nomenclature.md → thesis_docs/comparison_dependency_flowchart.md
- `Baseline B - Weitefeld yolo11s (multi-class)` --semantically_similar_to--> `HERIDAL and Weitefeld baselines - Phase 1 only, never mixed into Phase 3`  [INFERRED] [semantically similar]
  training_nomenclature.md → thesis_docs/comparison_dependency_flowchart.md
- `YOLO26s - edge-optimized CNN, no DFL/NMS, optional P2 head` --semantically_similar_to--> `YOLO26 architecture (edge-optimised CNN, P2 small-object head)`  [INFERRED] [semantically similar]
  training_nomenclature.md → thesis_docs/phase_execution_guide.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Thesis writing loop: outline -> evaluate -> find-refs, governed by thesis/CLAUDE.md** — claude_skills_outline_skill_outlineskill, claude_skills_evaluate_skill_evaluateskill, claude_skills_find_refs_skill_findrefsskill, thesis_claude_writingconventions [EXTRACTED 0.95]
- **Weitefeld conversion, box-origin bug fix, and resulting dataset variants** — data_raw_weitefeld_provenance_weitefeldtoyoloscript, data_raw_weitefeld_provenance_boxoriginbug, data_processed_weitefeld_yolo_v1_provenance_weitefeldyolov1dataset, data_processed_weitefeld_yolo_3cls_v1_provenance_weitefeldyolo3clsv1dataset [EXTRACTED 0.90]
- **Phase 1 Baseline A/B training runs and their naming convention** — results_baselines_p1_heridal_yolo11s_2_args_baselineatrainingrun, results_baselines_p1_weitefeld_yolo11s_args_baselinebtrainingrun, claude_naming_baselinea, claude_naming_baselineb [INFERRED 0.90]
- **Dependabot-maintained GitHub Actions workflows** — sar_drone_ws_src_px4_msgs_github_dependabot_dependabot_config, sar_drone_ws_src_px4_msgs_github_workflows_build_build_workflow, sar_drone_ws_src_px4_msgs_github_workflows_create_release_create_release_workflow, sar_drone_ws_src_px4_msgs_github_workflows_package_package_workflow, sar_drone_ws_src_px4_msgs_github_workflows_release_bloom_release_workflow [INFERRED 0.75]
- **px4_msgs release automation pipeline (GitHub release -> .deb packaging -> rosdistro PR)** — sar_drone_ws_src_px4_msgs_github_workflows_create_release_create_release_workflow, sar_drone_ws_src_px4_msgs_github_workflows_package_package_workflow, sar_drone_ws_src_px4_msgs_github_workflows_release_bloom_release_workflow, concept_px4_msgs_release_repo [EXTRACTED 1.00]
- **REP-2004 Quality Level 3 compliance evidence bundle** — sar_drone_ws_src_px4_msgs_quality_declaration_quality_declaration, concept_rep_2004_quality_level, sar_drone_ws_src_px4_msgs_github_workflows_build_build_workflow, sar_drone_ws_src_px4_msgs_cmakelists_cmakelists, sar_drone_ws_src_px4_msgs_pre_commit_config_pre_commit_config, sar_drone_ws_src_px4_msgs_security_security_policy [EXTRACTED 1.00]
- **Phase 3 elimination-tournament structure (architecture -> training -> head -> pipeline)** — thesis_docs_comparison_dependency_flowchart_stage1architecturesweep, thesis_docs_comparison_dependency_flowchart_stage2trainingmethodology, thesis_docs_comparison_dependency_flowchart_stage3backboneheadcomparison, thesis_docs_comparison_dependency_flowchart_stage4pipelineconfigurations [EXTRACTED 1.00]
- **Four pipeline configurations (P-1..P-4) compared end-to-end for O4** — thesis_docs_comparison_dependency_flowchart_p1detectoronly, thesis_docs_comparison_dependency_flowchart_p2detectora1, thesis_docs_comparison_dependency_flowchart_p3detectora1vlm, thesis_docs_comparison_dependency_flowchart_p4darm [EXTRACTED 1.00]
- **Companion computer options evaluated against each other before Jetson decision** — thesis_docs_companion_computer_choices_jetsonorinnanosuper, thesis_docs_companion_computer_choices_raspberrypi5hailo, thesis_docs_companion_computer_choices_orangepi5, thesis_docs_companion_computer_choices_radxarock5b [INFERRED 0.80]

## Communities (41 total, 14 thin omitted)

### Community 0 - "PX4 Msgs Release Governance"
Cohesion: 0.07
Nodes (48): apt/dpkg lock wait-and-retry to avoid unattended-upgrade flakiness, BLOOM_GITHUB_TOKEN Secret, bloom Release Tool / bloom-release, ccache compiler-masquerade over CMAKE_<LANG>_COMPILER_LAUNCHER, Contributor Covenant v2.1, Conventional Commits, Developer Certificate of Origin (DCO), Explicit apt-package dependency install instead of full ROS desktop / rosdep resolution (+40 more)

### Community 1 - "Project Hard Rules & Conventions"
Cohesion: 0.07
Nodes (49): Agent Instructions (AGENTS.md, Codex copy), Agent Instructions (CLAUDE.md, canonical), Torch/torchvision pinned to pytorch-cu128 index, vision/ package decoupled from ROS2 until Phase 6, Hard Rule 1: split by unit of independence, never by frame/image, Hard Rule 2: occlusion sets frozen on disk with fixed seeds, Hard Rule 3: held-out HPI class seal is sacred, Hard Rule 4: no architectures requiring custom CUDA kernels (+41 more)

### Community 2 - "Dataset Splits & Evaluation Conventions"
Cohesion: 0.08
Nodes (34): Arducam validation batch - test-only, sole DJI->Arducam domain gap measurement, HERIDAL and Weitefeld baselines - Phase 1 only, never mixed into Phase 3, heridal_to_yolo.py converter (tiles, splits by source photo), Rationale: split on unit of independence, never individual image, Rationale: vision/ package deliberately decoupled from ROS2 until Phase 6, weitefeld_to_yolo.py converter (tiles, splits by physical finding), Train/validation/test data splits, Evaluation metrics: IoU, precision, recall, mAP, per-class reporting (+26 more)

### Community 3 - "Phase 3 Elimination Tournament"
Cohesion: 0.08
Nodes (29): P3.6 - Occlusion sweep (survivors x 6 frozen buckets), P3.7 - Held-out class eval (bootstrap CIs over placements), GATE 3 - winning head configuration, GATE 4 - surviving pipeline configurations, P-1 Detector only (the floor), P-2 Detector + A1 (double detector, crop + re-detect), P-3 Detector + A1 + VLM (async queue worker), P-4 D-arm open-vocabulary detector (parallel alternative) (+21 more)

### Community 4 - "Jetson & Sim Ops"
Cohesion: 0.08
Nodes (27): Jetson is inference/benchmarking device only, never train on it, PX4-Autopilot clone treated as external dependency, Camera frame capture via v4l2-ctl + ffmpeg conversion, Jetson/Sim Ops Cheat Sheet (README.md), Jetson power-mode/clocks session checks (nvpmodel, jtop, jetson_clocks), Force-kill px4/gz/MicroXRCEAgent/QGroundControl processes, sar_drone_ws colcon build + sim launch, scp transfer of annotated frame off Jetson to WSL2/Windows (+19 more)

### Community 5 - "SAR Detection Literature & Hardware Choice"
Cohesion: 0.08
Nodes (27): Aerial Person Detection for SAR: Survey and Benchmarks, Bozic-Stulic et al. 2019 - Deep Learning Approach in Aerial Imagery for SAR (HERIDAL paper), Human Detection in UAV Thermal Imagery: Dataset Extension and Embedded Platform Evaluation (2025), Decision: Jetson Orin Nano Super (chosen companion computer), Khadas VIM4 option, Marusic et al. 2020 - Multimodel Deep Learning for Person Detection in Aerial Images, MISFIT-V - Misaligned Image Synthesis and Fusion (Thermal/Visual), Orange Pi 5 Plus/5B option (+19 more)

### Community 6 - "Phase 3 Architecture Sweep Rationale"
Cohesion: 0.10
Nodes (23): Rationale: no architecture requiring custom CUDA kernels admitted to sweep, GATE 0 - bush dataset usable + pipeline trusted, Run budget table (~30-40 total runs), Rationale: SSM/Mamba detector arms scrapped (selective_scan kernel risk), STAGE 1 - Architecture sweep (P3.1/P3.2, 6 runs), Detector candidate scope expanded to six architectures, RF-DETR - full transformer, Apache-2.0, domain-transfer leader, Rationale: SSM/Mamba arms scrapped (selective_scan CUDA kernel risk) (+15 more)

### Community 7 - "Baseline A/B Naming & Conventions"
Cohesion: 0.11
Nodes (22): Convention: render near-zero-confidence predictions to distinguish coordinate bug from undertrained model, Convention: report Weitefeld person-class metrics as a lower bound (~14.7% label noise), Baseline A = HERIDAL/yolo11s, Baseline B = Weitefeld/yolo11s, heridal_to_yolo.py converter script, heridal_yolo_v1 processed dataset, weitefeld_yolo_3cls_v1 processed dataset (unknown dropped), weitefeld_yolo_v1 processed dataset (4-class, unknown kept) (+14 more)

### Community 8 - "HERIDAL YOLO Converter"
Cohesion: 0.18
Nodes (19): clip_boxes(), convert(), find_pairs(), _find_voc_devkit(), main(), _pair_ids(), parse_voc(), Path (+11 more)

### Community 9 - "Training Methodology Gates"
Cohesion: 0.11
Nodes (19): A2b stretch - two fully separate models (conditional), D7 - Initialisation side experiment (COCO-init vs Weitefeld-init), GATE 1 - winning architecture (accuracy + latency + memory + power), GATE 2 - winning training recipe, Rationale: LoRA considered and rejected for closed-set detector, P3.3b - yolo26-p2 ablation (conditional), P3.8 - Scale sweep (n/s/m on winner, Pareto curve, answers O2), STAGE 2 - Training methodology (P3.3, 2 runs) (+11 more)

### Community 10 - "Occlusion Tool Implementation"
Cohesion: 0.21
Nodes (15): ndarray, apply_occlusion(), feather(), main(), mask_blobs(), mask_cutout(), Grab a patch from the image that does not overlap any annotated box, so we…, Soften edges. Hard edges are a texture the network can memorise. (+7 more)

### Community 11 - "Claude Code Skills Catalog"
Cohesion: 0.14
Nodes (15): Humanizer Skill, Wikipedia: Signs of AI writing, doc-sync skill (drafted, not active), jetson-bench skill (drafted, not active), lit-review skill (drafted, not active), log-run skill (drafted, not active), Rationale: verify-seal/log-run better as assert+script than skills, occlusion-sweep skill (drafted, not active) (+7 more)

### Community 12 - "PX4 Offboard Hover Demo"
Cohesion: 0.20
Nodes (6): Node, main(), OffboardHelloWorld, hover.py Minimal PX4 offboard control node via uXRCE-DDS bridge. What it does:…, VehicleOdometry, VehicleStatus

### Community 13 - "Weitefeld YOLO Converter"
Cohesion: 0.25
Nodes (12): convert(), index_images(), main(), parse_data_txt(), Path, Map (strip, image_number) -> file. Names are AA_BBBBB_<ts>_<us>_RGB.jpg., data.txt box -> absolute (x1, y1, x2, y2). See format caveat in docstring.…, weitefeld_to_yolo.py — convert the Weitefeld aerial forest anomaly dataset into… (+4 more)

### Community 14 - "PX4/Gazebo/ROS2 Sim Stack"
Cohesion: 0.18
Nodes (11): Gazebo Harmonic simulator, PX4 flight controller firmware, PX4 SITL (Software In The Loop) mode, uORB internal PX4 message bus, uXRCE-DDS bridge (PX4 <-> ROS2 translator), Stage 6: where vision meets ROS2 (Phase 6, vision_node.py), Phase 6 - Multi-drone simulation and fleet coordination (O6), Phase 7 - Physical flight testing (+3 more)

### Community 15 - "Changelog Generator Script"
Cohesion: 0.42
Nodes (8): contributors(), emit(), forthcoming_block(), generate(), join_csv(), names(), generate_changelog.sh script, underline()

### Community 16 - "Detection Pipeline Comparison (P-1..P-4)"
Cohesion: 0.28
Nodes (9): Comparison Dependency Flowchart, A1: crop + re-detect escalation tier, D-arm open-vocabulary detector (YOLO-World/YOLOE/Grounding DINO), Detection pipeline configurations (P-1..P-4), VLM worker (async, off-queue, <=2B params), Objective Changes Since Progress Report, Pipeline comparison made explicit (P-1..P-4), Phase 0 + Phase 1 (+2+3) Execution Guide (+1 more)

### Community 17 - "Occlusion Label Policy & Rationale"
Cohesion: 0.22
Nodes (9): Rationale: --distractor-rate prevents occluder-texture shortcut learning, Rationale: frozen occlusion sets, never on-the-fly, occlude.py occlusion instrument, Rationale: occluded target keeps full original box (label policy), Occlusion modes: cutout, blobs, texture, foliage, Data augmentation for aerial imagery, D5 - The O1 confound (occlusion vs altitude vs camera domain gap), P1.5 - Occlusion tool (fraction, frozen sets, modes, label policy) (+1 more)

### Community 18 - "Weitefeld Dataset Adoption (D3)"
Cohesion: 0.33
Nodes (7): Rationale: HPI detection promoted to primary contribution, Nathan et al. 2026, Scientific Data 13:747 - aerial anomaly dataset for SAR (Weitefeld), Rationale: O1 applies to person detection only (HERIDAL person-only), Rationale: VOC dropped from track, vision/AI-only scope, Weitefeld dataset (Nathan et al. 2026), D3 - Use the Weitefeld dataset (recommendation: yes, early), P0.5 - Acquire HERIDAL and Weitefeld datasets

### Community 19 - "Blue Mountains Terrain Assets"
Cohesion: 0.60
Nodes (5): Blue Mountains Gazebo World, Aerial Diffuse Texture (Blue Mountains), Blue Mountains Aerial Texture (aerial.png, inferred), Blue Mountains Terrain Height Map, Blue Mountains Normal Map (normal_map.png, inferred)

### Community 20 - "Altitude/FOV Dataset Decisions"
Cohesion: 0.40
Nodes (5): Rationale: no FOV compensation between DJI and Arducam, Rationale: stills primary, video collected alongside for temporal arm, P2.2 - Altitude bands and FOV correction (later dropped), P2.4 - What to capture besides pixels (SRT telemetry), P3.0 - Dataset decisions since rev.2 (stills+video, no FOV compensation)

### Community 21 - "Model Architecture (Backbone/Neck/Head)"
Cohesion: 0.50
Nodes (4): A0 / A2 / A2b head-configuration comparison, Backbone / Neck / Head model structure, Backbone / neck / head explanation, How model training works

## Ambiguous Edges - Review These
- `Rationale: no FOV compensation between DJI and Arducam` → `P2.2 - Altitude bands and FOV correction (later dropped)`  [AMBIGUOUS]
  thesis_docs/phase_execution_guide.md · relation: conceptually_related_to

## Knowledge Gaps
- **123 isolated node(s):** `build_deb_container.sh script`, `build_deb_host.sh script`, `deploy_blue_mountains.sh script`, `start_sim.sh script`, `vision` (+118 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 191 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **14 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `Rationale: no FOV compensation between DJI and Arducam` and `P2.2 - Altitude bands and FOV correction (later dropped)`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **Why does `Agent Instructions (CLAUDE.md, canonical)` connect `Project Hard Rules & Conventions` to `Jetson & Sim Ops`, `Baseline A/B Naming & Conventions`?**
  _High betweenness centrality (0.040) - this node is a cross-community bridge._
- **Why does `GATE 1 - winning architecture (accuracy + latency + memory + power)` connect `Training Methodology Gates` to `Phase 3 Architecture Sweep Rationale`?**
  _High betweenness centrality (0.037) - this node is a cross-community bridge._
- **Why does `STAGE 1 - Architecture sweep (P3.1/P3.2, 6 runs)` connect `Phase 3 Architecture Sweep Rationale` to `Training Methodology Gates`, `Phase 3 Elimination Tournament`?**
  _High betweenness centrality (0.036) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `Decision: Jetson Orin Nano Super (chosen companion computer)` (e.g. with `Jetson Orin Nano Super deployment target setup` and `Jetson Orin Nano Developer Kit User Guide`) actually correct?**
  _`Decision: Jetson Orin Nano Super (chosen companion computer)` has 2 INFERRED edges - model-reasoned connections that need verification._
- **What connects `build_deb_container.sh script`, `build_deb_host.sh script`, `deploy_blue_mountains.sh script` to the rest of the system?**
  _123 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `PX4 Msgs Release Governance` be split into smaller, more focused modules?**
  _Cohesion score 0.07020408163265306 - nodes in this community are weakly interconnected._