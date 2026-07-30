# Companion Computer & Camera Hardware Comparison
### Low-Altitude Bush/Forest Runner SAR Drone — Vision/AI Perception Stack

*Prepared for thesis design-justification / methodology section. Pricing and availability current as of end of July 2026 — re-verify before final submission if there is a long gap between drafting and submission, as SBC/edge-AI hardware pricing shifts often.*

---

## 1. Context & Requirements

The forest runner drone requires an onboard companion computer capable of **real-time human/human-presence-indicator detection** from a low-altitude UAV operating over dense, low-visibility bush terrain, where vegetative occlusion degrades both human search effectiveness and vision-based detection systems. Key constraints driving the hardware selection:

- **Total drone budget:** $1000–1500 AUD, covering the entire airframe (frame, Pixhawk, motors/ESCs, battery, telemetry, companion computer, camera(s)) — not just the perception stack.
- **Real-time onboard inference required** (no reliance on ground-station offload for core detection).
- **Payload/weight and power budget are tight** on a small forest-runner airframe; every gram and watt trades directly against flight time.
- **PX4 handles all motor control natively** — the companion computer's job is perception, mission logic, and communicating setpoints/detections over uXRCE-DDS/ROS2, not actuation.

---

## 2. Companion Computer Options Considered

| Board | Price (approx.) | CPU | AI Accelerator | Peak AI Performance | Power (idle → load) | Software Ecosystem |
|---|---|---|---|---|---|---|
| **Raspberry Pi 5 (8GB) + Hailo AI HAT** | ~$150–210 total | 4-core Cortex-A76 @ 2.4GHz | Hailo-8L or Hailo-8 (add-on) | 13 or 26 TOPS (INT8) | ~5–7W → ~13–18W | Mature Pi ecosystem, decent Hailo docs, huge community |
| **Radxa ROCK 5B / 5B+** | ~$110–220 | 8-core (4× A76 @2.4GHz + 4× A55 @1.8GHz) | Onboard 6 TOPS NPU (RKNN) | 6 TOPS onboard; up to ~32 TOPS with Hailo M.2 add-on | ~2–5W idle → ~10–22W (with M.2 accelerator + peripherals) | Weaker — RKNN toolchain has rougher docs, fewer prebuilt examples |
| **Orange Pi 5 Plus / 5B** | ~$130–250 | Same RK3588/RK3588S as above | Onboard 6 TOPS NPU | 6 TOPS onboard | Similar to ROCK 5B | Similar to ROCK 5B; availability inconsistent in some regions in 2026 |
| **Khadas VIM4** | ~$150–200 | Amlogic A311D2 | Onboard NPU | ~5 TOPS | Not benchmarked in this comparison | Smaller community than Pi/Jetson |
| **NVIDIA Jetson Orin Nano Super Dev Kit** ✅ *(chosen)* | ~$399 (list price rose from $249 in a July 2026 NVIDIA price adjustment) | 6-core Arm CPU | 1024-core Ampere GPU w/ Tensor Cores | 67 TOPS (INT8) | 7W / 15W / 25W configurable power modes (MAXN unlocked can exceed 25W) | **Mature** — CUDA, TensorRT, JetPack, large robotics/ROS2 community, strongest precedent in published SAR-UAV literature |

### Notes on TOPS as a metric
TOPS (Tera/Trillion Operations Per Second) measures peak theoretical throughput of the AI accelerator (typically quoted at INT8 precision) — it is a useful *ceiling* indicator but not a reliable predictor of real-world frames-per-second, since actual performance depends heavily on software toolchain maturity (TensorRT vs. RKNN), memory bandwidth, and how well a given model architecture (e.g. YOLOv8-nano) maps onto the specific accelerator. A lower-TOPS device with a mature, well-optimised toolchain (e.g. Hailo-8 with YOLO) can outperform a higher-TOPS device with a less mature one on real detection workloads. This is why raw TOPS alone was not used as the sole decision criterion below.

---

## 3. Decision: NVIDIA Jetson Orin Nano Super Developer Kit

### Rationale
1. **Software maturity reduces development risk.** CUDA/TensorRT/JetPack is the most mature, best-documented edge-AI toolchain of the options evaluated, with the deepest pool of existing ROS2 + robotics integration examples. Given a fixed thesis timeline, minimising toolchain friction was weighted heavily against the ~$150–250 cost premium over a Raspberry Pi + Hailo or Rockchip RK3588 alternative.
2. **Literature precedent.** The Jetson platform (Nano/Xavier/Orin family) is the most commonly used embedded platform in published UAV-based SAR person-detection research (see companion literature review), which supports methodological comparability with prior work.
3. **Configurable power envelope.** The 7W/15W/25W power modes allow direct empirical trade-off testing between detection throughput and power draw/flight-time within the thesis itself — this is usable as a designed experiment (e.g. reporting detection FPS and accuracy at each power mode) rather than only a fixed operating point.
4. **Model headroom for future work.** 67 TOPS and CUDA support leave room to extend beyond a single lightweight detector (e.g. RGB-thermal fusion networks, or heavier detection backbones) without a hardware change, should the vision pipeline be extended later in the project.

### Trade-offs accepted
- **Cost:** ~$399 vs. ~$150–250 for Pi+Hailo or RK3588+Hailo alternatives — a larger fraction of the total ~$1000–1500 drone budget than initially planned, requiring tighter allocation elsewhere in the BOM (airframe, motors, battery).
- **Weight/power:** Heavier and higher peak power draw than the Pi 5 + Hailo option, which has a direct (if modest) cost to flight endurance on a small airframe.
- **Price volatility:** NVIDIA revised Jetson pricing during the course of this project (Orin Nano Super rose from $249 to ~$399 in July 2026), which is worth noting as a real-world procurement/BOM-planning consideration for the thesis methodology section.


## 5. Power Consumption Summary (companion computer only)

| System | Idle / light | Typical inference load | Peak / max load |
|---|---|---|---|
| Raspberry Pi 5 alone | ~3–5W | ~5–8W | ~10–12W |
| Pi 5 + Hailo-8L AI HAT (13 TOPS) | ~5–7W | ~8–11W | ~13–15W |
| Pi 5 + Hailo-8 AI HAT (26 TOPS) | ~6–8W | ~9–13W | ~15–18W |
| Radxa ROCK 5B/5B+ alone | ~2–5W | ~8–10W | ~10–15W |
| ROCK 5B + Hailo-8 M.2 (32 TOPS combined) | ~5–8W | ~12–16W | ~18–22W |
| **Jetson Orin Nano Super (chosen)** | ~5–7W (7W mode floor) | ~10–15W (15W mode) | up to 25W (MAXN unlocked) |

*For context: this is a few-percent contribution to overall power draw relative to a typical small-UAV motor system (~150–500W), but is non-trivial on a payload/endurance-constrained forest-runner airframe and is worth quantifying empirically once the airframe is finalised.*

## 7. Key References for Design Justification

These support the "why thermal + RGB fusion" and "why this compute tier" arguments in the proposal/thesis:

- Božić-Štulić, D., Marušić, Ž., Gotovac, S. (2019). *Deep Learning Approach in Aerial Imagery for Supporting Land Search and Rescue Missions.* International Journal of Computer Vision. — foundational HERIDAL dataset/baseline paper.
- Marušić, Ž. et al. (2020). *Multimodel Deep Learning for Person Detection in Aerial Images.* Electronics (MDPI). — discusses thermal contrast failure modes outdoors.
- WiSARD: *A Labeled Visual and Thermal Image Dataset for Wilderness Search and Rescue* (arXiv 2309.04453).
- MISFIT-V: *Misaligned Image Synthesis and Fusion using Information from Thermal and Visual* (arXiv 2309.13216). — RGB/thermal sensor-rig alignment considerations relevant to physical mounting.
- *Seeing Through Sparse Foliage: Quality–Occlusion-Guided RGB–Thermal Fusion for Drone-Based Person Detection* (MDPI Remote Sensing, 2026). — closely mirrors this project's problem statement.
- *Human Detection in UAV Thermal Imagery: Dataset Extension and Comparative Evaluation on Embedded Platforms* (MDPI Drones / PMC, 2025). — embedded platform (Jetson AGX Orin) benchmarking precedent.
- *Aerial Person Detection for Search and Rescue: Survey and Benchmarks* (Journal of Remote Sensing / Science Partner Journal). — literature review anchor.

