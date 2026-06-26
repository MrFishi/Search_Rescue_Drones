# SAR Drone — Development Notes

> Running notes on system architecture, setup decisions, and key concepts learned during thesis development. Append new sections as you go.

---

## Table of Contents

- [PX4, Gazebo & ROS2 — How They Connect](#px4-gazebo--ros2--how-they-connect)


## PX4, Gazebo & ROS2 — How They Connect

### What PX4 Actually Is

PX4 is an open-source **flight controller firmware** — the operating system running on the Pixhawk. It handles everything that needs to happen fast and reliably at the hardware level:

- Reading IMU, barometer, GPS, and magnetometer sensors
- Running the **attitude estimator (EKF2)** to know where the drone is and how it's oriented in 3D space
- Running **control loops** — rate controller, attitude controller, position controller — dozens of times per second
- Outputting PWM/DSHOT signals to ESCs to spin the motors
- **Motor mixing** — translating a desired pitch/roll/yaw/thrust into individual motor commands for a specific airframe geometry

> **Key thesis principle:** PX4 owns all of this completely. Our job is only to tell PX4 *where we want the drone to go*. PX4 figures out how to get there.

---

### The uORB Message Bus — PX4's Internal Nervous System

Inside PX4, everything communicates via a publish/subscribe system called **uORB** (micro Object Request Broker). Every sensor reading, every state estimate, every command is a uORB message. Key topics:

| Topic | Direction | Description |

| `vehicle_odometry` | PX4 → us | Position, velocity, orientation from EKF2 |
| `vehicle_status` | PX4 → us | Arming state, flight mode, health flags |
| `offboard_control_mode` | us → PX4 | Tells PX4 what kind of setpoints we're sending |
| `trajectory_setpoint` | us → PX4 | Target position/velocity we want the drone to reach |
| `vehicle_command` | us → PX4 | Commands: ARM, DISARM, SET_MODE |

uORB is internal to PX4. To talk to the outside world, PX4 needs a bridge.

---

### How PX4 SITL Works

When running in **SITL (Software In The Loop)** mode, the exact same PX4 firmware runs as a process on the development machine instead of on a Pixhawk:

- Instead of reading a real IMU → receives simulated sensor data from Gazebo
- Instead of outputting PWM to real ESCs → sends motor commands to Gazebo's physics engine
- Gazebo simulates the physics (gravity, aerodynamics, motor thrust) and feeds the result back into PX4's estimator

The connection between PX4 SITL and Gazebo Harmonic happens via **Gazebo Transport** — a pub/sub system native to Gazebo. PX4 ships a plugin that handles this link automatically.

```
PX4 SITL ──[motor commands]──► Gazebo physics
Gazebo    ──[IMU, GPS, camera data]──► PX4 SITL
```

> **Why Gazebo Harmonic specifically:** Modern Gazebo (gz-sim) uses Gazebo Transport natively and has proper PX4 plugins. Gazebo Classic used a completely different plugin API and is end-of-life — do not use it.

---

### The uXRCE-DDS Bridge — How PX4 Talks to ROS2

uORB is internal to PX4. ROS2 is external. The translator between them is **Micro XRCE-DDS** (uXRCE-DDS).

```
┌─────────────────────────────────────┐
│           Your ROS2 Nodes           │
│  (offboard_hello_world.py, etc.)    │
└──────────────┬──────────────────────┘
               │  ROS2 Topics (DDS)
               │  /fmu/in/...   (commands to PX4)
               │  /fmu/out/...  (state from PX4)
┌──────────────▼──────────────────────┐
│       Micro XRCE-DDS Agent          │
│  (runs as a separate process)       │
└──────────────┬──────────────────────┘
               │  UDP (port 8888)
               │  XRCE-DDS protocol
┌──────────────▼──────────────────────┐
│          PX4 SITL Process           │
│  (runs Micro XRCE-DDS Client        │
│   built into PX4 firmware)          │
└─────────────────────────────────────┘
```

- PX4 runs a **built-in DDS Client** that serialises selected uORB topics and streams them out over UDP
- The **XRCE-DDS Agent** (a separate process) receives that UDP stream and re-publishes everything as proper ROS2 topics
- ROS2 nodes then subscribe/publish to those topics like any other ROS2 topic

**ROS2 topic naming convention:**

| ROS2 Topic | Direction | Maps to uORB |
|---|---|---|
| `/fmu/out/vehicle_odometry` | PX4 → node | `vehicle_odometry` |
| `/fmu/out/vehicle_status` | PX4 → node | `vehicle_status` |
| `/fmu/in/offboard_control_mode` | node → PX4 | `offboard_control_mode` |
| `/fmu/in/trajectory_setpoint` | node → PX4 | `trajectory_setpoint` |
| `/fmu/in/vehicle_command` | node → PX4 | `vehicle_command` |

---

### Full System Architecture

```

                   Development Machine                  
                                                        
  ┌─────────────┐    Gazebo     ┌──────────────────┐    
  │  Gazebo Sim │◄─ Transport ─►│   PX4 SITL       │    
  │  (physics,  │               │  (EKF2, attitude │    
  │   visuals)  │               │   control, etc.) │    
  └─────────────┘               └────────┬─────────┘     
                                         │ UDP :8888    
                                ┌────────▼─────────┐    
                                │  uXRCE-DDS Agent │    
                                └────────┬─────────┘    
                                         │ DDS/ROS2     
                          ┌──────────────▼───────────┐  
                          │    ROS2 Nodes            │  
                          │  offboard_hello_world.py │  
                          │  vision_node.py (later)  │  
                          │  swarm_coordinator(later)│  
                          └──────────────────────────┘  
```

**For swarm simulation:** Each drone is a separate PX4 SITL instance on a different UDP port, with its own ROS2 namespace (`drone_1`, `drone_2`, etc.). This is already scaffolded in `sim_swarm.launch.py`.

---

