"""
sim_bringup.launch.py

Single-command bringup of the simulation infrastructure:
  - PX4 SITL + Gazebo (via PX4's make target)
  - Micro XRCE-DDS Agent (bridges PX4 uORB topics into ROS2)
  - QGroundControl (optional, auto-connects to PX4 on UDP 14550)

This launch file does NOT start any sar_drone nodes — run those separately
with `ros2 run sar_drone <node>` or a follow-up launch file while developing.

Usage:
  ros2 launch sar_drone sim.launch.py
  ros2 launch sar_drone sim.launch.py world:=default model_pose:="0,0,0"
  ros2 launch sar_drone sim.launch.py gz_model:=gz_x500_depth
  ros2 launch sar_drone sim.launch.py px4_dir:=/home/me/PX4-Autopilot
  ros2 launch sar_drone sim.launch.py launch_qgc:=false

World files:
  'world' must match the filename (without .sdf) of a world already copied into
  <px4_dir>/Tools/simulation/gz/worlds/. Default is 'blue_mountains' (the custom
  terrain, live-symlinked from this repo via simulation/scripts/deploy_blue_mountains.sh).
  Pass world:=default to fall back to PX4's built-in grey plane instead.

Requires:
  - PX4-Autopilot already built at least once (so 'make' is a fast incremental build)
  - MicroXRCEAgent installed and on PATH (check with: which MicroXRCEAgent)
  - QGroundControl AppImage present at qgc_path (skip with launch_qgc:=false)
  - blue_mountains.sdf already deployed via deploy_blue_mountains.sh (only needed once)
"""

import os

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, TimerAction
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node


def generate_launch_description():

    # Default PX4-Autopilot location — override with px4_dir:=/your/path if different
    default_px4_dir = os.path.join(os.path.expanduser('~'), 'Documents', 'PX4-Autopilot')

    px4_dir_arg = DeclareLaunchArgument(
        'px4_dir',
        default_value=default_px4_dir,
        description='Absolute path to the PX4-Autopilot repo'
    )

    gz_model_arg = DeclareLaunchArgument(
        'gz_model',
        default_value='gz_x500',
        description=(
            'PX4 make target for the Gazebo model, e.g. gz_x500, gz_x500_depth, '
            'gz_x500_mono_cam, gz_x500_mono_cam_down, gz_x500_lidar_front'
        )
    )

    world_arg = DeclareLaunchArgument(
        'world',
        default_value='blue_mountains',
        description=(
            'Gazebo world name (filename without .sdf) to load. Defaults to the '
            'custom blue_mountains terrain. Pass world:=default for PX4\'s built-in '
            'grey plane. Must already exist in <px4_dir>/Tools/simulation/gz/worlds/ '
            '(blue_mountains is deployed there via simulation/scripts/deploy_blue_mountains.sh). '
            'Sets PX4_GZ_WORLD for the px4_sitl make process.'
        )
    )

    model_pose_arg = DeclareLaunchArgument(
        'model_pose',
        default_value='0,0,15',
        description=(
            'Spawn pose "x,y,z[,roll,pitch,yaw]" for the vehicle. Defaults to '
            '"0,0,15" (15m up) to clear blue_mountains terrain on spawn. Pass '
            'model_pose:="0,0,0" when using world:=default. Sets PX4_GZ_MODEL_POSE '
            'for the px4_sitl make process.'
        )
    )

    dds_port_arg = DeclareLaunchArgument(
        'dds_port',
        default_value='8888',
        description='UDP port the Micro XRCE-DDS Agent listens on (must match PX4)'
    )

    agent_delay_arg = DeclareLaunchArgument(
        'agent_delay',
        default_value='8.0',
        description='Seconds to wait after PX4/Gazebo starts before launching the DDS Agent'
    )

    qgc_path_arg = DeclareLaunchArgument(
        'qgc_path',
        default_value=os.path.join(
            os.path.expanduser('~'), 'Documents', 'QGroundControl-x86_64.AppImage'
        ),
        description='Absolute path to the QGroundControl AppImage'
    )

    launch_qgc_arg = DeclareLaunchArgument(
        'launch_qgc',
        default_value='true',
        description='Whether to launch QGroundControl alongside the sim (true/false)'
    )

    px4_dir = LaunchConfiguration('px4_dir')
    gz_model = LaunchConfiguration('gz_model')
    world = LaunchConfiguration('world')
    model_pose = LaunchConfiguration('model_pose')
    dds_port = LaunchConfiguration('dds_port')
    agent_delay = LaunchConfiguration('agent_delay')
    qgc_path = LaunchConfiguration('qgc_path')
    launch_qgc = LaunchConfiguration('launch_qgc')

    # PX4 SITL + Gazebo — runs PX4's own make target, which both compiles
    # (fast/incremental after the first build) and launches Gazebo + PX4.
    # QT_QPA_PLATFORM=xcb avoids known Gazebo viewport input issues under
    # native Wayland sessions. Gazebo binary resolution (standalone vs
    # ROS-vendored) is handled globally via PATH in ~/.bashrc.
    px4_env = dict(os.environ)
    px4_env['QT_QPA_PLATFORM'] = 'xcb'

    px4_sitl = ExecuteProcess(
        cmd=['make', 'px4_sitl', gz_model],
        cwd=px4_dir,
        env=px4_env,
        additional_env={'PX4_GZ_WORLD': world, 'PX4_GZ_MODEL_POSE': model_pose},
        output='screen',
        name='px4_sitl_gazebo',
        shell=False,
    )

    # Micro XRCE-DDS Agent — bridges PX4 uORB topics into ROS2 topics.
    # Delayed so PX4 has time to boot and open its UDP port before the
    # Agent tries to connect.
    dds_agent = TimerAction(
        period=agent_delay,
        actions=[
            ExecuteProcess(
                cmd=['MicroXRCEAgent', 'udp4', '-p', dds_port],
                output='screen',
                name='micro_xrce_dds_agent',
            )
        ]
    )

    # QGroundControl — auto-connects to PX4 SITL on UDP 14550, no config needed.
    # Started after the DDS Agent delay too, since it doesn't need to be early.
    qgc = TimerAction(
        period=agent_delay,
        actions=[
            ExecuteProcess(
                cmd=[qgc_path],
                output='screen',
                name='qgroundcontrol',
                condition=IfCondition(launch_qgc),
            )
        ]
    )

    return LaunchDescription([
        px4_dir_arg,
        gz_model_arg,
        world_arg,
        model_pose_arg,
        dds_port_arg,
        agent_delay_arg,
        qgc_path_arg,
        launch_qgc_arg,
        px4_sitl,
        dds_agent,
        qgc,
    ])