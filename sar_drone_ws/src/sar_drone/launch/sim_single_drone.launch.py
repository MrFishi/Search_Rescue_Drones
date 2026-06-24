"""
sim_single_drone.launch.py

Starts the ROS2 stack for a single Forest Runner drone in simulation.
Run simulation/scripts/start_sim.sh first to start PX4 SITL + Gazebo.

Usage:
  ros2 launch sar_drone sim_single_drone.launch.py
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():

    drone_id_arg = DeclareLaunchArgument('drone_id', default_value='drone_1')
    use_sim_time_arg = DeclareLaunchArgument('use_sim_time', default_value='true')

    drone_id = LaunchConfiguration('drone_id')
    use_sim_time = LaunchConfiguration('use_sim_time')

    # Micro XRCE-DDS Agent — bridges PX4 SITL uORB topics into ROS2
    xrce_agent = Node(
        package='micro_ros_agent',
        executable='micro_ros_agent',
        name='xrce_dds_agent',
        arguments=['udp4', '-p', '8888'],
        output='screen'
    )

    nav_node = Node(
        package='sar_drone',
        executable='offboard_hello_world',
        name='offboard_hello_world',
        namespace=drone_id,
        parameters=[{'use_sim_time': use_sim_time, 'drone_id': drone_id}],
        output='screen'
    )

    return LaunchDescription([
        drone_id_arg,
        use_sim_time_arg,
        xrce_agent,
        nav_node,
    ])
