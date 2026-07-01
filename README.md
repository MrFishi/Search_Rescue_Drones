SAR Collaborative Multi-Drone System

Thesis project: heterogeneous UAV fleet collaboratively searching for missing persons using distributed information sharing and dynamic re-tasking.

Primary Focus: Low-Altitude Bush/Forest Runner


Vision/AI — camera + person detection in dense bush
VOC & audio sensing — non-visual human presence detection


Stack


Flight Controller: Pixhawk / PX4
Companion Computer: TBD
Middleware: ROS2 Humble
Simulator: Gazebo Harmonic
PX4–ROS2 Bridge: uXRCE-DDS Agent


Quick Start

bash# Terminal 1 — PX4 SITL + Gazebo
./simulation/scripts/start_sim.sh

# Terminal 2 — ROS2 stack
cd ~/Search_Rescue_Drones/sar_drone_ws
colcon build --symlink-install
source install/setup.bash
ros2 launch sar_drone sim_single_drone.launch.py

# kill everything
pkill -9 -f 'px4|gz sim|gz-sim|MicroXRCEAgent|QGroundControl'

# check everything is killed (should return empty)
ps aux | grep -E 'px4|gz|MicroXRCE|QGround' | grep -v grep