#!/usr/bin/env python3
"""
offboard_hello_world.py

Minimal PX4 offboard control node via uXRCE-DDS bridge.

What it does:
  1. Reads current position from PX4 via VehicleOdometry
  2. Arms the vehicle
  3. Switches to Offboard flight mode
  4. Commands a hover at 5m altitude via TrajectorySetpoint

PX4 handles ALL motor control — this node only sends high-level position setpoints.

To run:
  ros2 run sar_drone offboard_hello_world
"""

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy, DurabilityPolicy

from px4_msgs.msg import (
    OffboardControlMode,
    TrajectorySetpoint,
    VehicleCommand,
    VehicleOdometry,
    VehicleStatus,
)


class OffboardHelloWorld(Node):

    def __init__(self):
        super().__init__('offboard_hello_world')

        # QoS must match PX4 uXRCE-DDS settings
        px4_qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
            history=HistoryPolicy.KEEP_LAST,
            depth=1
        )

        # Publishers — send commands TO PX4
        self.offboard_mode_pub = self.create_publisher(
            OffboardControlMode, '/fmu/in/offboard_control_mode', px4_qos)
        self.trajectory_pub = self.create_publisher(
            TrajectorySetpoint, '/fmu/in/trajectory_setpoint', px4_qos)
        self.vehicle_command_pub = self.create_publisher(
            VehicleCommand, '/fmu/in/vehicle_command', px4_qos)

        # Subscribers — read state FROM PX4
        self.create_subscription(
            VehicleOdometry, '/fmu/out/vehicle_odometry',
            self.odometry_callback, px4_qos)
        self.create_subscription(
            VehicleStatus, '/fmu/out/vehicle_status',
            self.status_callback, px4_qos)

        self.counter = 0
        self.position = [0.0, 0.0, 0.0]  # NED frame
        self.target_z_ned = -5.0          # 5m up (NED: negative = up)

        # Must publish at >2 Hz before PX4 accepts offboard mode switch
        self.timer = self.create_timer(0.1, self.control_loop)  # 10 Hz
        self.get_logger().info('OffboardHelloWorld started — will arm and hover at 5m')

    def odometry_callback(self, msg: VehicleOdometry):
        self.position = list(msg.position)

    def status_callback(self, msg: VehicleStatus):
        pass

    def publish_offboard_mode(self):
        msg = OffboardControlMode()
        msg.position = True
        msg.velocity = False
        msg.acceleration = False
        msg.timestamp = int(self.get_clock().now().nanoseconds / 1000)
        self.offboard_mode_pub.publish(msg)

    def publish_setpoint(self, x, y, z, yaw=0.0):
        msg = TrajectorySetpoint()
        msg.position = [x, y, z]
        msg.yaw = yaw
        msg.timestamp = int(self.get_clock().now().nanoseconds / 1000)
        self.trajectory_pub.publish(msg)

    def send_command(self, command, param1=0.0, param2=0.0):
        msg = VehicleCommand()
        msg.command = command
        msg.param1 = param1
        msg.param2 = param2
        msg.target_system = 1
        msg.target_component = 1
        msg.source_system = 1
        msg.source_component = 1
        msg.from_external = True
        msg.timestamp = int(self.get_clock().now().nanoseconds / 1000)
        self.vehicle_command_pub.publish(msg)

    def control_loop(self):
        # Always publish — PX4 drops offboard mode if setpoints stop arriving
        self.publish_offboard_mode()
        self.publish_setpoint(0.0, 0.0, self.target_z_ned)

        # After 1 second of setpoints, arm and switch to offboard
        if self.counter == 10:
            self.send_command(VehicleCommand.VEHICLE_CMD_DO_SET_MODE, 1.0, 6.0)
            self.send_command(VehicleCommand.VEHICLE_CMD_COMPONENT_ARM_DISARM, 1.0)
            self.get_logger().info('Offboard mode + ARM sent')

        p = self.position
        self.get_logger().info(
            f'Pos NED: [{p[0]:.2f}, {p[1]:.2f}, {p[2]:.2f}] | Target Z: {self.target_z_ned}m'
        )

        if self.counter < 11:
            self.counter += 1


def main(args=None):
    rclpy.init(args=args)
    node = OffboardHelloWorld()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
