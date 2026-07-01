#!/bin/bash
# deploy_blue_mountains.sh
#
# ONE-TIME setup (per machine) for live-editing the blue_mountains world.
#
# What it does:
#   1. Rewrites the heightmap texture <uri> tags in the repo's source
#      blue_mountains.world to absolute paths pointing at THIS repo's
#      mesh/ folder (relative URIs are unreliable in this PX4/Gazebo
#      pipeline — see project notes).
#   2. Symlinks that rewritten file into PX4-Autopilot's Gazebo worlds
#      directory as blue_mountains.sdf.
#
# After running this ONCE, you can edit
#   simulation/worlds/blue_mountains/blue_mountains.world
# directly, save, and relaunch the sim — no redeploy, no colcon build,
# no re-running this script. The symlink means Gazebo always reads your
# live repo file.
#
# You only need to re-run this script if:
#   - You're setting up on a new machine
#   - You move/rename the repo or PX4-Autopilot directories
#   - The symlink gets broken somehow (e.g. PX4-Autopilot was reinstalled)
#
# Usage:
#   ./deploy_blue_mountains.sh [path-to-PX4-Autopilot]
#   (defaults to ~/Documents/PX4-Autopilot if not given)

set -e

PX4_DIR="${1:-$HOME/Documents/PX4-Autopilot}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORLD_SRC_DIR="$(cd "$SCRIPT_DIR/../worlds/blue_mountains" && pwd)"
WORLD_FILE="$WORLD_SRC_DIR/blue_mountains.world"
MESH_DIR="$WORLD_SRC_DIR/mesh"
WORLDS_DIR="$PX4_DIR/Tools/simulation/gz/worlds"

if [ ! -f "$WORLD_FILE" ]; then
    echo "ERROR: world file not found at $WORLD_FILE"
    exit 1
fi

if [ ! -d "$PX4_DIR" ]; then
    echo "ERROR: PX4-Autopilot not found at $PX4_DIR"
    echo "Usage: ./deploy_blue_mountains.sh [path-to-PX4-Autopilot]"
    exit 1
fi

echo "Repo world source : $WORLD_FILE"
echo "PX4 worlds dir     : $WORLDS_DIR"

# Rewrite relative mesh/ URIs to absolute paths pointing at THIS repo's
# mesh folder — done in-place on the repo file itself, so edits you make
# afterwards (e.g. adding trees) stay live without needing this rewrite
# to run again, as long as you don't touch the <uri> lines.
sed -i \
    -e "s|>mesh/height_map.png<|>$MESH_DIR/height_map.png<|g" \
    -e "s|>mesh/aerial.png<|>$MESH_DIR/aerial.png<|g" \
    -e "s|>mesh/normal_map.png<|>$MESH_DIR/normal_map.png<|g" \
    "$WORLD_FILE"

mkdir -p "$WORLDS_DIR"
ln -sf "$WORLD_FILE" "$WORLDS_DIR/blue_mountains.sdf"

echo ""
echo "Done."
echo "  - $WORLD_FILE now uses absolute mesh URIs (pointing at this repo)"
echo "  - $WORLDS_DIR/blue_mountains.sdf -> symlinked to that file"
echo ""
echo "From now on: edit $WORLD_FILE directly, save, and relaunch:"
echo "  ros2 launch sar_drone sim.launch.py world:=blue_mountains model_pose:=\"0,0,15\""
echo "No redeploy needed unless you move repos or set up a new machine."
