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



## Custom Terrain — Generating Real-World Gazebo Worlds

> Adds real-world-accurate terrain (elevation, satellite imagery, buildings) to the
> simulation instead of PX4's default flat/generic world. Useful for realistic SAR
> bush/forest testing on actual geography rather than synthetic terrain.

### Tool

[`gazebo_terrain_generator`](https://github.com/saiaravind19/gazebo_terrain_generator)
— a local web tool that generates a Gazebo Harmonic-compatible `.world` file from
real elevation data, satellite imagery, and OSM building footprints for any
location on Earth.

### Setup

```bash
cd ~/Documents
git clone https://github.com/saiaravind19/gazebo_terrain_generator.git
cd gazebo_terrain_generator

curl -LsSf https://astral.sh/uv/install.sh | sh   # if uv not already installed
source ~/.bashrc

export GAZEBO_TERRAIN_OUTPUT_PATH=~/Documents/gazebo_terrain_output
echo "export GAZEBO_TERRAIN_OUTPUT_PATH=~/Documents/gazebo_terrain_output" >> ~/.bashrc
mkdir -p ~/Documents/gazebo_terrain_output

uv sync
uv run scripts/server.py
```

Open `http://localhost:8080`. Requires a free [Mapbox](https://www.mapbox.com/) API
token, pasted into **Settings → Mapbox API Key** (stored browser-side only, never
touches the server or this repo).

### Map Tile Source — Why Mapbox, Not Google

The tool defaults to "Google Maps Satellite" as a tile source. **Changed to
Mapbox Satellite for this project.**

**Reasoning:** Google Maps/Earth imagery is licensed for viewing within Google's
own products — there is no official API or license path for extracting raw
satellite tiles for reuse in a third-party simulation engine. Scraping Google's
tiles through a generator tool like this sits in a legal gray area against
Google's Terms of Service. Mapbox, by contrast, provides a Satellite imagery
product specifically licensed for API access via developer tokens — which is
exactly the access method this project already uses.

**Data provenance for generated worlds:**
- Satellite imagery — Mapbox Satellite API
- Elevation / heightmap data — Mapbox Terrain-DEM (via same API; note: source data
  caps at zoom 14-15 — horizontal resolution is roughly 4-8m/pixel at this
  project's latitude, regardless of the imagery zoom level setting used)
- Building footprints — OpenStreetMap (via the tool's OSM integration)

**Setting used:** Settings → Map Tile Source → `Mapbox Satellite`

### Generation Workflow

1. Search for or navigate to the target location
2. Draw a **convex** polygon around the area of interest (concave/notched shapes
   are rejected — "Polygon must be convex" error — keep boundaries simple, a
   basic 4-6 point shape rather than hugging every contour)
3. Set spawn marker position
4. Settings to check:
   - Zoom Level: 17 (default) — controls imagery sharpness only, not elevation detail
   - Include Buildings: on/off depending on need (extrudes OSM footprints as flat
     untextured 3D boxes — functional but not visually polished; see Known Issues)
   - Map Tile Source: **Mapbox Satellite** (not the default)
   - Target Gazebo Version: Harmonic (and above) — 16-bit heightmap precision
   - Target Heightmap Size: Auto (nearest to DEM resolution)
5. Generate, then use the **real output directory**, not the Download button (see
   Known Issues) — `~/Documents/gazebo_terrain_output/<world_name>/`

### Checking World Dimensions

Real-world size and elevation range are encoded in the `.world` file's heightmap
`<size>` element:

```bash
grep -A 2 "<size>" <world_file>.world
```

Returns `<size>width_m length_m elevation_range_m</size>` — e.g. a 1706m × 1321m
area with 575.6m of elevation relief for the Blue Mountains test world.

### Known Issues

**Zip download from the tool is consistently incomplete.** "Download World"
produces a `.zip` containing only `.world` and `model.config` — missing
`model.sdf` and the entire `mesh/` folder (heightmap, texture, normal map,
buildings). This happened on every generation, not a one-off. **Fix:** skip the
zip entirely — the complete output already exists at
`$GAZEBO_TERRAIN_OUTPUT_PATH/<world_name>/`, use that directly.

**No `model.sdf` is generated at all, even in the complete output.** The tool
bakes the model definition directly into the `.world` file rather than using a
separate `model://`-referenced model — confirmed by loading the `.world` file
standalone (`gz sim <file>.world`), which renders correctly with no missing
references. Not a bug, just a different-than-expected output structure — moving
a generated world means copying the `.world` file and its `mesh/` folder together
as a pair.

**Auto-extruded buildings are flat, untextured gray boxes with no roof detail,**
and some buildings visible in the satellite imagery are missing entirely (OSM
footprint data isn't complete everywhere). Acceptable for geographic layout
accuracy; not visually polished. Improving this would require manual
materials/lighting work or swapping in modeled buildings from Fuel — deferred as
low-priority relative to core thesis goals (vision/VOC sensing, not environment art).

**No tree/vegetation geometry is generated** — satellite imagery gives ground
color only, not 3D plant geometry. Vegetation placement is a separate manual step
(not yet done — planned next).

**Heightmap can show artifacts at polygon edges** on large/loosely-bounded
polygons — observed as an unnatural flat shelf/vertical drop at the boundary on
an early (Shenton Bushland) test. Not fully root-caused; suspected DEM edge
coverage or resampling artifact. Not reproduced on a tighter, more deliberately
bounded polygon (Blue Mountains test) — keep polygons reasonably tight and
convex as a precaution.

---

## Integrating Generated Worlds into PX4 SITL

Getting a custom-generated world to actually spawn PX4's drone into it (rather
than PX4's own bundled default) required working around several layers of
PX4's world-resolution logic. Documented here in case a future custom world hits
the same issues.

### World File Discovery Is Hardcoded, Not Path-Searched

`PX4_GZ_WORLD` (env var) is **not** a resource-path lookup — PX4's
`px4-rc.gzsim` init script builds the world file path as a literal string
concatenation: