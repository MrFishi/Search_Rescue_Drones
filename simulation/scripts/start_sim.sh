#!/bin/bash
# start_sim.sh — Launch PX4 SITL + Gazebo Harmonic for a single drone
# Run this BEFORE: ros2 launch sar_drone sim_single_drone.launch.py

PX4_DIR="${PX4_DIR:-$HOME/PX4-Autopilot}"

if [ ! -d "$PX4_DIR" ]; then
  echo "ERROR: PX4-Autopilot not found at $PX4_DIR"
  echo "Clone PX4-Autopilot to $HOME/PX4-Autopilot or set PX4_DIR"
  exit 1
fi

echo "Starting PX4 SITL + Gazebo Harmonic..."
cd "$PX4_DIR"
PX4_SYS_AUTOSTART=4001 PX4_GZ_WORLD=default \
  ./build/px4_sitl_default/bin/px4 -s etc/init.d-posix/rcS
