# Simulation Environment Setup

Complete guide to setting up and running the SAR drone simulation stack from scratch.

**Stack:** Ubuntu 24.04 · ROS2 Jazzy · Gazebo Harmonic · PX4 SITL · Micro XRCE-DDS

---

## Prerequisites

Before starting, confirm your environment matches:

```bash
lsb_release -a          # Ubuntu 24.04
printenv ROS_DISTRO     # jazzy
gz sim --version        # Gazebo Sim 8.x (Harmonic)
python3 --version       # 3.12.x
```

If ROS2 Jazzy or Gazebo Harmonic are not installed, set those up first before continuing.

---

## One-Time Setup

These steps only need to be done once on a new machine.

### 1. System Dependencies

```bash
sudo apt update && sudo apt install -y \
  ninja-build \
  python3-pip \
  python3-venv \
  gstreamer1.0-plugins-bad \
  gstreamer1.0-libav \
  gstreamer1.0-gl \
  libfuse2 \
  libgstreamer-plugins-base1.0-dev \
  libgstreamer1.0-dev \
  python3-gi \
  python3-gst-1.0 \
  libxcb-xinerama0 \
  libxkbcommon-x11-0 \
  libxcb-cursor-dev
```

### 2. Clone PX4-Autopilot

Clone into `~/Documents` (or wherever you keep projects — keep it outside the thesis repo):

```bash
cd ~/Documents
git clone https://github.com/PX4/PX4-Autopilot.git --recursive
```

> This is a large clone (~1GB+) and will take several minutes depending on your connection.

### 3. Run PX4's Dependency Installer

PX4 ships its own script that installs all remaining build dependencies:

```bash
cd ~/Documents/PX4-Autopilot
bash ./Tools/setup/ubuntu.sh
```

### 4. Build PX4 SITL

This compiles the firmware for Software In The Loop simulation. **First build takes 10–15 minutes.**

```bash
cd ~/Documents/PX4-Autopilot
make px4_sitl gz_x500
```

When it finishes it will automatically launch Gazebo with an x500 drone. Close it with `Ctrl+C` once you've confirmed it works — you don't need it running for the next steps.

> Subsequent builds are fast (incremental). Only recompile if you update PX4.

### 5. Build the Micro XRCE-DDS Agent

This is the bridge between PX4 and ROS2. Build from source:

```bash
cd ~/Documents
git clone https://github.com/eProsima/Micro-XRCE-DDS-Agent.git
cd Micro-XRCE-DDS-Agent
mkdir build && cd build
cmake ..
make -j4
sudo make install
sudo ldconfig /usr/local/lib/
```

Verify it installed:

```bash
which MicroXRCEAgent
# Expected: /usr/local/bin/MicroXRCEAgent
```

### 6. Clone px4_msgs into the ROS2 Workspace

```bash
cd ~/Documents/Search_Rescue_Drones/sar_drone_ws/src
git clone https://github.com/PX4/px4_msgs.git
```

### 7. Build the ROS2 Workspace

```bash
cd ~/Documents/Search_Rescue_Drones/sar_drone_ws
colcon build --packages-select px4_msgs sar_drone
```

> `px4_msgs` takes ~10 minutes first time — it generates hundreds of message type bindings.

### 8. Add Source Commands to .bashrc

So you don't have to source manually every session:

```bash
echo "source /opt/ros/jazzy/setup.bash" >> ~/.bashrc
echo "source ~/Documents/Search_Rescue_Drones/sar_drone_ws/install/setup.bash" >> ~/.bashrc
source ~/.bashrc
```

### 9. Install QGroundControl (Optional but Recommended)

QGroundControl gives you a live telemetry dashboard alongside the simulation:

```bash
cd ~/Documents
wget https://d176tv9ibo4jno.cloudfront.net/builds/master/QGroundControl-x86_64.AppImage
chmod +x QGroundControl-x86_64.AppImage
```

Add yourself to the dialout group for serial port access:

```bash
sudo usermod -aG dialout "$(id -un)"
```

Log out and back in for the group change to take effect.

---

## Running the Simulation

Every simulation session requires **3 terminals** running simultaneously.

### Terminal 1 — PX4 SITL + Gazebo

```bash
cd ~/Documents/PX4-Autopilot
make px4_sitl gz_x500
```

Wait until you see:
```
INFO  [uxrce_dds_client] init UDP agent IP:127.0.0.1, port:8888
INFO  [commander] Ready for takeoff!
```

Leave this terminal running. The `pxh>` prompt is PX4's shell — do not close it.

### Terminal 2 — Micro XRCE-DDS Agent

```bash
MicroXRCEAgent udp4 -p 8888
```

You should see a flood of `topic created` and `datawriter created` messages — this means PX4 topics are now bridged into ROS2.

### Terminal 3 — Your ROS2 Nodes

```bash
source ~/Documents/Search_Rescue_Drones/sar_drone_ws/install/setup.bash
ros2 run sar_drone hover
```

Or to launch the full single-drone stack:

```bash
ros2 launch sar_drone sim_single_drone.launch.py
```

Or for swarm simulation:

```bash
ros2 launch sar_drone sim_swarm.launch.py num_drones:=3
```

### Terminal 4 — QGroundControl (Optional)

```bash
~/Documents/QGroundControl-x86_64.AppImage
```

QGroundControl will auto-detect the running PX4 SITL on UDP port 14550.

---

## Verifying the Bridge

With Terminals 1 and 2 running, check ROS2 topics are flowing:

```bash
ros2 topic list | grep fmu
```

You should see both `/fmu/in/...` and `/fmu/out/...` topics.

Check live position data from PX4:

```bash
ros2 topic echo /fmu/out/vehicle_odometry --once
```

You should see a message with `position`, `velocity`, and `q` (quaternion orientation) fields.

---

## Available Gazebo Models

The following drone models can be swapped into the `make` command:

| Model | Command suffix | Sensors |
|---|---|---|
| Standard quadcopter | `gz_x500` | IMU, GPS, baro, mag |
| Forward camera | `gz_x500_mono_cam` | + monocular camera |
| Downward camera | `gz_x500_mono_cam_down` | + downward camera |
| Depth camera | `gz_x500_depth` | + depth camera |
| Front lidar | `gz_x500_lidar_front` | + forward lidar |
| Downward lidar | `gz_x500_lidar_down` | + downward lidar |
| Visual odometry | `gz_x500_vision` | + optical flow |

Example — launch with depth camera:
```bash
make px4_sitl gz_x500_depth
```

---

## Directory Structure

```
~/Documents/
├── PX4-Autopilot/                  ← PX4 firmware (external, not in git)
├── Micro-XRCE-DDS-Agent/           ← DDS bridge (external, not in git)
├── QGroundControl-x86_64.AppImage  ← GCS app
└── Search_Rescue_Drones/           ← Thesis repo (this repo)
    └── sar_drone_ws/
        └── src/
            ├── px4_msgs/           ← PX4 message definitions
            └── sar_drone/          ← Your ROS2 nodes
```

---

## Known Issues

**Type hash warnings on `ros2 topic list`**
```
Failed to parse type hash for topic ...
```
This occurs when `px4_msgs` and `PX4-Autopilot` are on slightly different commits. Data still flows correctly — this is cosmetic. Fix by checking out matching versions (see dev_notes.md).

**Gazebo viewport mouse input not working (AMD GPU)**
Known issue with radeonsi drivers on Ubuntu 24.04. Camera navigation may be unresponsive in the default empty world. Workaround: use a world with visible terrain features (Task 3).

**PX4 build freezes midway**
Usually caused by thermal throttling or RAM pressure. Kill with `Ctrl+C` and rerun with limited parallelism:
```bash
make px4_sitl gz_x500 -j4
```

**`ros2 run sar_drone hover` — No executable found**
Rebuild the workspace cleanly:
```bash
cd ~/Documents/Search_Rescue_Drones/sar_drone_ws
rm -rf build/ install/ log/
colcon build --packages-select px4_msgs sar_drone
source install/setup.bash
```

---

## What Each Process Does

| Process | What it does |
|---|---|
| PX4 SITL | Runs flight controller firmware on your PC instead of a Pixhawk |
| Gazebo Harmonic | Simulates drone physics, sensors, and environment |
| Micro XRCE-DDS Agent | Bridges PX4 uORB topics into ROS2 topics over UDP port 8888 |
| px4_msgs | ROS2 message definitions for all PX4 topics |
| sar_drone | Your thesis ROS2 package — navigation, vision, VOC/audio nodes |
| QGroundControl | Ground control station — live telemetry dashboard |