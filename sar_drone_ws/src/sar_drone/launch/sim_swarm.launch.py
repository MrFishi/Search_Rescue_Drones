"""
sim_swarm.launch.py

Launches multiple drone instances for swarm simulation.
Each drone gets a unique namespace matching its PX4 SITL instance.

Usage:
  ros2 launch sar_drone sim_swarm.launch.py num_drones:=3
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, GroupAction, OpaqueFunction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def spawn_drones(context, *args, **kwargs):
    num_drones = int(LaunchConfiguration('num_drones').perform(context))
    use_sim_time = LaunchConfiguration('use_sim_time')
    actions = []

    for i in range(num_drones):
        drone_id = f'drone_{i + 1}'
        actions.append(
            GroupAction([
                Node(
                    package='sar_drone',
                    executable='offboard_hello_world',
                    name='offboard_hello_world',
                    namespace=drone_id,
                    parameters=[{
                        'use_sim_time': use_sim_time,
                        'drone_id': drone_id,
                        'px4_instance': i,
                    }],
                    output='screen'
                ),
            ])
        )
    return actions


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument('num_drones', default_value='2'),
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        OpaqueFunction(function=spawn_drones),
    ])
